"""The Enforcer protocol (Ahmad, AHM-08).

An Enforcer applies an *approved* block on a firewall the user owns, and undoes
it. It only ever talks to that firewall: nothing is sent toward the blocked
address (CLAUDE.md rule 4). maxguard.response.approvals decides when an enforcer
may run; an enforcer never decides anything by itself.

Any class with these three methods is an Enforcer (typing.Protocol checks the
shape, no base class needed), so a test can pass a small fake one.
"""

from __future__ import annotations

from typing import Protocol


class EnforcerError(RuntimeError):
    """The firewall refused or could not be reached; the block state did not change."""


class Enforcer(Protocol):
    def add(self, ip: str) -> None:
        """Put ip on the firewall's block list."""

    def remove(self, ip: str) -> None:
        """Take ip off the firewall's block list."""

    def apply(self) -> None:
        """Make the firewall use the changed list (some firewalls need this step)."""
