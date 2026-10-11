"""Versioned contracts shared by the backend boundary and demo fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict


GradeStatus = Literal["correct", "incorrect", "partial", "needs_review"]
BlockType = Literal["intro", "vocabulary", "exercise", "summary"]
ActivityType = Literal["single_choice", "fill_blanks"]


class GradingDisclosure(TypedDict):
    equivalentAnswersMayBeAccepted: bool
    aiReviewPossible: bool


class PublicBlock(TypedDict):
    id: str
    schemaVersion: int
    blockType: BlockType
    content: dict


class AttemptRequest(TypedDict):
    exerciseId: str
    exerciseVersion: int
    responses: dict[str, str]
    idempotencyKey: str


class ItemGrade(TypedDict):
    id: str
    status: GradeStatus
    feedback: str


class AIJob(TypedDict):
    schemaVersion: int
    id: str
    status: Literal["queued", "running", "completed", "failed"]
    languageTag: str
    provenance: dict[str, str]


@dataclass(frozen=True)
class Normalization:
    trim: bool = False
    case_fold: bool = False
    punctuation: Literal["strict"] = "strict"

    def apply(self, value: str) -> str:
        if self.trim:
            value = value.strip()
        if self.case_fold:
            value = value.casefold()
        return value


@dataclass(frozen=True)
class ItemAnswer:
    accepted_variants: tuple[str, ...]
    normalization: Normalization


@dataclass(frozen=True)
class AnswerKey:
    exercise_id: str
    exercise_version: int
    items: dict[str, ItemAnswer]
    max_attempts: int
    reveal_answer: Literal["never", "after_final_attempt"]


@dataclass(frozen=True)
class StoredExercise:
    id: str
    version: int
    activity_type: ActivityType
    prompt: str
    items: tuple[dict, ...]
    disclosure: GradingDisclosure
    answer_key_id: str


@dataclass(frozen=True)
class AttemptRecord:
    learner_id: str
    exercise_id: str
    exercise_version: int
    responses: dict[str, str]
    result: dict
    idempotency_key: str
