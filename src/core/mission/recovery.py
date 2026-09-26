"""Políticas de recuperação para experimentos de missão."""

from dataclasses import dataclass
from enum import StrEnum


class RecoveryStrategy(StrEnum):
    BASELINE = "baseline"
    DYNAMIC_REPLANNING = "dynamic_replanning"
    ASSUMPTION_BASED = "assumption_based"


@dataclass(frozen=True)
class FailureEvent:
    reason: str
    task_key: str | None
    action_name: str | None
    attempt: int


@dataclass(frozen=True)
class RecoveryDecision:
    strategy: RecoveryStrategy
    action: str


def decide_recovery(strategy: RecoveryStrategy, event: FailureEvent) -> RecoveryDecision:
    """Decisão sem efeitos; permite trocar a implementação posteriormente."""
    if strategy is RecoveryStrategy.BASELINE:
        return RecoveryDecision(strategy, "stop")
    if strategy is RecoveryStrategy.DYNAMIC_REPLANNING:
        return RecoveryDecision(strategy, "replan")
    return RecoveryDecision(strategy, "evaluate_assumptions")
