#!/usr/bin/env python3
"""Explicit state machines for typed brain workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar, Mapping


Role = str
State = str


class StateMachineError(ValueError):
    """Raised when a transition is not allowed."""


@dataclass(frozen=True)
class TransitionRule:
    from_state: State
    to_state: State
    roles: frozenset[Role]
    required_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransitionEvent:
    from_state: State
    to_state: State
    role: Role
    actor: str
    at: str
    reason: str = ""


@dataclass
class StateMachine:
    state: State
    created_at: str = field(default_factory=lambda: utc_now())
    updated_at: str = field(default_factory=lambda: utc_now())
    history: list[TransitionEvent] = field(default_factory=list)

    initial_state: ClassVar[State] = ""
    terminal_states: ClassVar[frozenset[State]] = frozenset()
    transitions: ClassVar[tuple[TransitionRule, ...]] = ()

    def allowed_transitions(self, role: Role | None = None) -> list[TransitionRule]:
        rules = [rule for rule in self.transitions if rule.from_state == self.state]
        if role is not None:
            rules = [rule for rule in rules if role in rule.roles]
        return rules

    def can_transition(self, to_state: State, role: Role, context: Mapping[str, object] | None = None) -> bool:
        try:
            self._find_rule(to_state, role, context or {})
            return True
        except StateMachineError:
            return False

    def transition(
        self,
        to_state: State,
        *,
        role: Role,
        actor: str,
        context: Mapping[str, object] | None = None,
        reason: str = "",
        at: str | None = None,
    ) -> TransitionEvent:
        rule = self._find_rule(to_state, role, context or {})
        timestamp = at or utc_now()
        event = TransitionEvent(
            from_state=rule.from_state,
            to_state=rule.to_state,
            role=role,
            actor=actor,
            at=timestamp,
            reason=reason,
        )
        self.state = to_state
        self.updated_at = timestamp
        self.history.append(event)
        return event

    def _find_rule(self, to_state: State, role: Role, context: Mapping[str, object]) -> TransitionRule:
        if self.state in self.terminal_states:
            raise StateMachineError(f"{self.state} is terminal")
        matches = [
            rule
            for rule in self.transitions
            if rule.from_state == self.state and rule.to_state == to_state
        ]
        if not matches:
            raise StateMachineError(f"transition {self.state} -> {to_state} is not allowed")
        for rule in matches:
            if role not in rule.roles:
                continue
            missing = [field for field in rule.required_fields if not context.get(field)]
            if missing:
                raise StateMachineError(f"transition requires context fields: {', '.join(missing)}")
            return rule
        allowed_roles = sorted({role for rule in matches for role in rule.roles})
        raise StateMachineError(f"role {role} cannot transition {self.state} -> {to_state}; allowed: {allowed_roles}")


class ApprovalStateMachine(StateMachine):
    initial_state = "draft"
    terminal_states = frozenset({"published", "rejected"})
    transitions = (
        TransitionRule("draft", "review", frozenset({"author", "owner", "agent"}), ("artifact_ref",)),
        TransitionRule("review", "approved", frozenset({"reviewer", "owner"}), ("review_ref",)),
        TransitionRule("review", "rejected", frozenset({"reviewer", "owner"}), ("review_ref",)),
        TransitionRule("approved", "published", frozenset({"publisher", "owner"}), ("approval_ref", "publish_target")),
    )

    def __init__(self, state: State = "draft") -> None:
        super().__init__(state=state)


class TaskStateMachine(StateMachine):
    initial_state = "pending"
    terminal_states = frozenset({"complete"})
    transitions = (
        TransitionRule("pending", "in_progress", frozenset({"owner", "agent", "manager"})),
        TransitionRule("in_progress", "blocked", frozenset({"owner", "agent", "manager"}), ("blocker",)),
        TransitionRule("blocked", "in_progress", frozenset({"owner", "agent", "manager"}), ("resolution",)),
        TransitionRule("in_progress", "complete", frozenset({"owner", "agent", "manager"}), ("evidence_ref",)),
        TransitionRule("blocked", "complete", frozenset({"owner", "manager"}), ("evidence_ref", "resolution")),
    )

    def __init__(self, state: State = "pending") -> None:
        super().__init__(state=state)


class ResearchStateMachine(StateMachine):
    initial_state = "queued"
    terminal_states = frozenset({"delivered"})
    transitions = (
        TransitionRule("queued", "investigating", frozenset({"researcher", "agent", "owner"}), ("question",)),
        TransitionRule("investigating", "synthesizing", frozenset({"researcher", "agent", "owner"}), ("source_refs",)),
        TransitionRule("synthesizing", "delivered", frozenset({"researcher", "agent", "owner"}), ("deliverable_ref",)),
    )

    def __init__(self, state: State = "queued") -> None:
        super().__init__(state=state)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
