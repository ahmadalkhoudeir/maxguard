"""JSON API for block proposals under /api/response (Ahmad, AHM-08).

create_app() in maxguard/api/app.py includes this router when it imports. The
routes read the stores from request.app.state and read the clock (time.time())
like the rest of the API; approvals.py and preview.py never do.

    POST /api/response/proposals                  {actor, ip, direction, reason?, finding_id?}
    GET  /api/response/proposals
    GET  /api/response/proposals/{id}
    POST /api/response/proposals/{id}/preview     {actor}
    POST /api/response/proposals/{id}/approve     {actor, confirm_ip}
    POST /api/response/proposals/{id}/apply       {actor}
    POST /api/response/proposals/{id}/revert      {actor}
    POST /api/response/proposals/{id}/reject      {actor, reason?}

apply uses the OPNsense enforcer when MAXGUARD_OPNSENSE_URL is set; otherwise
it records that the person ran the generated commands by hand.
Errors: 400 bad input or wrong typed IP, 404 no such proposal, 409 step not
allowed now, 502 the firewall refused or could not be reached.
"""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from maxguard.response.approvals import ProposalStore, WrongState
from maxguard.response.enforcers import opnsense
from maxguard.response.enforcers.base import EnforcerError
from maxguard.response.generate import OPNSENSE_ALIASES, sides
from maxguard.response.preview import preview

router = APIRouter(prefix="/api/response")


class NewProposal(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    ip: str = Field(min_length=1, max_length=100)
    direction: str = "both"
    reason: str = Field(default="", max_length=1000)
    finding_id: str | None = Field(default=None, max_length=100)


class Step(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    reason: str = Field(default="", max_length=1000)


class Approval(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    confirm_ip: str = Field(default="", max_length=100)  # missing -> refused, and audited


def proposals(request: Request) -> ProposalStore:
    """One ProposalStore per app, made on first use (it creates its table once)."""
    state = request.app.state
    if getattr(state, "proposal_store", None) is None:
        state.proposal_store = ProposalStore(state.state_store)
    return state.proposal_store


def enforcers_for(request: Request, direction: str) -> list:
    """The configured OPNsense enforcers (one alias per side), or [] when none is set up."""
    enforcers = []
    for side in sides(direction):
        enforcer = opnsense.from_env(request.app.state.data_dir, OPNSENSE_ALIASES[side])
        if enforcer is not None:
            enforcers.append(enforcer)
    return enforcers


def run_step(step):
    """Call one workflow step and turn its errors into HTTP answers."""
    try:
        return step()
    except KeyError:
        raise HTTPException(404, "no such proposal") from None
    except WrongState as err:
        raise HTTPException(409, str(err)) from None
    except EnforcerError as err:
        raise HTTPException(502, str(err)) from None
    except ValueError as err:
        raise HTTPException(400, str(err)) from None


@router.post("/proposals")
def create_proposal(request: Request, body: NewProposal) -> dict:
    return run_step(lambda: proposals(request).propose(
        ip=body.ip, direction=body.direction, actor=body.actor, at=time.time(),
        reason=body.reason, finding_id=body.finding_id))


@router.get("/proposals")
def list_proposals(request: Request, limit: int = Query(200, ge=1, le=1000)) -> list[dict]:
    return proposals(request).list_proposals(limit=limit)


@router.get("/proposals/{proposal_id}")
def get_proposal(request: Request, proposal_id: int) -> dict:
    return run_step(lambda: proposals(request).get(proposal_id))


@router.post("/proposals/{proposal_id}/preview")
def preview_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    store = proposals(request)
    proposal = run_step(lambda: store.get(proposal_id))
    now = time.time()
    summary = preview(proposal["ip"], proposal["direction"], request.app.state.event_store,
                      window_end=now)
    return run_step(lambda: store.record_preview(proposal_id, actor=body.actor,
                                                 preview=summary, at=now))


@router.post("/proposals/{proposal_id}/approve")
def approve_proposal(request: Request, proposal_id: int, body: Approval) -> dict:
    return run_step(lambda: proposals(request).approve(
        proposal_id, actor=body.actor, confirm_ip=body.confirm_ip, at=time.time()))


@router.post("/proposals/{proposal_id}/apply")
def apply_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    store = proposals(request)

    def step():
        proposal = store.get(proposal_id)
        enforcers = enforcers_for(request, proposal["direction"])
        return store.mark_applied(proposal_id, actor=body.actor, at=time.time(),
                                  enforcers=enforcers)
    return run_step(step)


@router.post("/proposals/{proposal_id}/revert")
def revert_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    store = proposals(request)

    def step():
        proposal = store.get(proposal_id)
        # Undo the same way it was applied: a block applied by hand is undone by hand.
        enforcers = []
        if proposal["method"] == "enforcer":
            enforcers = enforcers_for(request, proposal["direction"])
        return store.revert(proposal_id, actor=body.actor, at=time.time(), enforcers=enforcers)
    return run_step(step)


@router.post("/proposals/{proposal_id}/reject")
def reject_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    return run_step(lambda: proposals(request).reject(
        proposal_id, actor=body.actor, at=time.time(), reason=body.reason))
