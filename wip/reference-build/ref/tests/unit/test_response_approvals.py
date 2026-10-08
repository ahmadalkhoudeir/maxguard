"""Tests for maxguard.response.approvals (Ahmad, AHM-08)."""

import sqlite3
import threading

import pytest

from maxguard.response import approvals
from maxguard.response.approvals import ProposalStore, WrongState
from maxguard.response.enforcers.base import EnforcerError
from maxguard.storage.state import StateStore

T0 = 1791331200.0  # times are passed in; the store never reads the clock
PREVIEW = {"connections": 3, "devices": ["192.168.1.20"], "window_end": T0}


class FakeEnforcer:
    """Keeps a block list in memory, like a firewall alias."""

    def __init__(self, fail: bool = False):
        self.blocked: set[str] = set()
        self.applied = 0
        self.removed = 0
        self.fail = fail

    def add(self, ip: str) -> None:
        if self.fail:
            raise EnforcerError("firewall said no")
        self.blocked.add(ip)

    def remove(self, ip: str) -> None:
        self.removed += 1
        self.blocked.discard(ip)

    def apply(self) -> None:
        self.applied += 1


@pytest.fixture
def state(tmp_path):
    return StateStore(tmp_path / "state.db")


@pytest.fixture
def store(state):
    return ProposalStore(state)


def approved(store: ProposalStore, ip: str = "203.0.113.7") -> int:
    proposal_id = store.propose(ip=ip, direction="both", actor="ahmad", at=T0)["proposal_id"]
    store.record_preview(proposal_id, actor="ahmad", preview=PREVIEW, at=T0 + 1)
    store.approve(proposal_id, actor="fiona", confirm_ip=ip, at=T0 + 2)
    return proposal_id


def actions(state: StateStore) -> list[str]:
    return [row["action"] for row in reversed(state.list_audit())]


def test_full_workflow_is_audited(store, state):
    proposal_id = approved(store)
    firewall = FakeEnforcer()
    applied = store.mark_applied(proposal_id, actor="fiona", at=T0 + 3, enforcers=[firewall])
    assert applied["state"] == "applied" and applied["method"] == "enforcer"
    assert firewall.blocked == {"203.0.113.7"} and firewall.applied == 1
    reverted = store.revert(proposal_id, actor="ahmad", at=T0 + 4, enforcers=[firewall])
    assert reverted["state"] == "reverted"
    assert firewall.blocked == set()  # revert removed the address
    assert actions(state) == ["response.proposed", "response.previewed", "response.approved",
                              "response.applied", "response.reverted"]
    rows = list(reversed(state.list_audit()))
    assert {row["target"] for row in rows} == {str(proposal_id)}
    assert [row["at"] for row in rows] == [T0, T0 + 1, T0 + 2, T0 + 3, T0 + 4]
    assert rows[2]["actor"] == "fiona"


def test_proposal_shows_the_commands_and_their_undo(store):
    proposal = store.propose(ip="2001:DB8::7", direction="inbound", actor="ahmad", at=T0)
    assert proposal["ip"] == "2001:db8::7"
    assert proposal["rules"]["nftables"]["undo"]
    assert proposal["state"] == "proposed" and proposal["preview"] is None


@pytest.mark.parametrize("text", ["1.2.3.4; rm -rf /", "127.0.0.1", "ff02::1", "0.0.0.0",
                                  "169.254.1.1", "2001:db8::1%$(id)"])
def test_bad_addresses_cannot_be_proposed(store, state, text):
    with pytest.raises(ValueError):
        store.propose(ip=text, direction="both", actor="ahmad", at=T0)
    assert store.list_proposals() == [] and state.list_audit() == []


@pytest.mark.parametrize("typed", [None, "", "203.0.113.8", "203.0.113.7; rm -rf /"])
def test_approval_needs_the_same_ip_typed_again(store, state, typed):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    store.record_preview(proposal_id, actor="a", preview=PREVIEW, at=T0)
    with pytest.raises(ValueError, match="does not match"):
        store.approve(proposal_id, actor="fiona", confirm_ip=typed, at=T0 + 1)
    assert store.get(proposal_id)["state"] == "previewed"
    assert actions(state)[-1] == "response.approve_refused"  # refusals are logged too


def test_ipv6_typed_in_another_spelling_matches(store):
    proposal_id = approved(store, ip="2001:db8::7")
    assert store.get(proposal_id)["approved_by"] == "fiona"
    other = store.propose(ip="2001:db8::8", direction="both", actor="a", at=T0)["proposal_id"]
    store.record_preview(other, actor="a", preview=PREVIEW, at=T0)
    assert store.approve(other, actor="b", confirm_ip="2001:DB8:0::8", at=T0)["state"] == \
        "approved"


def test_no_approval_without_a_preview(store):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    with pytest.raises(WrongState):
        store.approve(proposal_id, actor="a", confirm_ip="203.0.113.7", at=T0)


def test_steps_out_of_order_are_refused(store):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    with pytest.raises(WrongState):
        store.mark_applied(proposal_id, actor="a", at=T0)       # not approved yet
    with pytest.raises(WrongState):
        store.revert(proposal_id, actor="a", at=T0)             # not applied yet
    with pytest.raises(KeyError):
        store.approve(999, actor="a", confirm_ip="203.0.113.7", at=T0)


def test_approved_twice_is_refused(store):
    proposal_id = approved(store)
    with pytest.raises(WrongState):
        store.approve(proposal_id, actor="b", confirm_ip="203.0.113.7", at=T0 + 5)


def test_manual_apply_and_revert(store, state):
    proposal_id = approved(store)
    assert store.mark_applied(proposal_id, actor="a", at=T0 + 3)["method"] == "manual"
    assert store.revert(proposal_id, actor="a", at=T0 + 4)["state"] == "reverted"
    assert state.list_audit()[0]["details"] == {"ip": "203.0.113.7", "method": "manual"}


def test_enforcer_failure_keeps_it_approved_and_is_audited(store, state):
    proposal_id = approved(store)
    with pytest.raises(EnforcerError):
        store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[FakeEnforcer(True)])
    assert store.get(proposal_id)["state"] == "approved"
    assert actions(state)[-1] == "response.apply_failed"


def test_enforcer_block_needs_the_enforcer_to_revert(store):
    proposal_id = approved(store)
    store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[FakeEnforcer()])
    with pytest.raises(ValueError, match="connector"):
        store.revert(proposal_id, actor="a", at=T0 + 4)
    assert store.get(proposal_id)["state"] == "applied"


def test_reject(store, state):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    assert store.reject(proposal_id, actor="b", at=T0 + 1, reason="our VPN")["state"] == \
        "rejected"
    with pytest.raises(WrongState):
        store.reject(proposal_id, actor="b", at=T0 + 2)
    assert actions(state)[-1] == "response.rejected"


def test_preview_is_kept_with_the_proposal(store):
    proposal_id = approved(store)
    assert store.get(proposal_id)["preview"] == PREVIEW


def test_a_state_change_and_its_audit_row_are_one_transaction(store, state, monkeypatch):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="ahmad",
                                at=T0)["proposal_id"]

    def broken_audit(*args, **kwargs):  # as if the disk filled up at this moment
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(approvals, "insert_audit", broken_audit)
    with pytest.raises(sqlite3.OperationalError):
        store.reject(proposal_id, actor="ahmad", at=T0 + 1)
    # The UPDATE was rolled back with the failed audit row: no change without its record.
    assert store.get(proposal_id)["state"] == "proposed"
    assert actions(state) == ["response.proposed"]


def test_one_open_proposal_per_address(store, state):
    first = store.propose(ip="203.0.113.7", direction="inbound", actor="a", at=T0)
    # Two open proposals for one address: reverting one would silently remove the
    # block the other still shows as applied. So the second one is refused.
    with pytest.raises(WrongState, match="open proposal"):
        store.propose(ip="203.0.113.7", direction="both", actor="b", at=T0 + 1)
    store.reject(first["proposal_id"], actor="a", at=T0 + 2)
    again = store.propose(ip="203.0.113.7", direction="both", actor="b", at=T0 + 3)
    assert again["state"] == "proposed"
    assert actions(state) == ["response.proposed", "response.rejected", "response.proposed"]


def test_a_failed_apply_takes_the_address_off_the_other_firewall_lists(store, state):
    proposal_id = approved(store)
    inbound, outbound = FakeEnforcer(), FakeEnforcer(fail=True)
    with pytest.raises(EnforcerError):
        store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[inbound, outbound])
    # The first list had the address; it was removed again, so nothing stays half-blocked.
    assert inbound.blocked == set() and inbound.removed == 1
    assert store.get(proposal_id)["state"] == "approved"
    assert state.list_audit()[0]["details"] == {"error": "firewall said no", "undone": True}


class SlowEnforcer(FakeEnforcer):
    """add() waits until the test says go, like a slow firewall."""

    def __init__(self):
        super().__init__()
        self.adds = 0
        self.entered = threading.Event()
        self.go = threading.Event()

    def add(self, ip: str) -> None:
        self.adds += 1
        self.entered.set()
        self.go.wait(5)
        super().add(ip)


def test_a_double_click_on_apply_reaches_the_firewall_once(store):
    proposal_id = approved(store)
    firewall = SlowEnforcer()
    results = []

    def click():
        try:
            store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[firewall])
            results.append("applied")
        except WrongState:
            results.append("refused")

    first, second = threading.Thread(target=click), threading.Thread(target=click)
    first.start()
    assert firewall.entered.wait(5)  # the first click is talking to the firewall
    second.start()
    second.join(0.2)                 # the second click waits for the first one
    firewall.go.set()
    first.join(5)
    second.join(5)
    assert firewall.adds == 1
    assert sorted(results) == ["applied", "refused"]
