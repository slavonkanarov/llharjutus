"""Lesson delivery, authorization, and deterministic grading for the demo."""

from __future__ import annotations

import json
import secrets
from threading import RLock

from .contracts import AttemptRecord, StoredExercise
from .sample_data import ANSWER_KEYS, CONTENT_BLOCKS, EXERCISES, LESSON


DEMO_TOKENS = {
    "demo-learner-one": "learner-one",
    "demo-learner-two": "learner-two",
}


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def validate_seed() -> None:
    """Fail at startup if an exercise has an incomplete private answer key."""
    for exercise in EXERCISES:
        key = ANSWER_KEYS[exercise.answer_key_id]
        item_ids = {item["id"] for item in exercise.items}
        if key.exercise_id != exercise.id or key.exercise_version != exercise.version:
            raise ValueError(f"Answer key version mismatch: {exercise.id}")
        if item_ids != set(key.items):
            raise ValueError(f"Incomplete answer key: {exercise.id}")
        for item in exercise.items:
            answer = key.items[item["id"]]
            if not answer.accepted_variants:
                raise ValueError(f"No accepted variants: {item['id']}")
            if exercise.activity_type == "single_choice":
                option_ids = {option["id"] for option in item["options"]}
                if not set(answer.accepted_variants) <= option_ids:
                    raise ValueError(f"Answer is not a visible option: {item['id']}")


def public_exercise(exercise: StoredExercise) -> dict:
    """Build an explicit learner DTO; never copy a stored exercise wholesale."""
    items = []
    for item in exercise.items:
        if exercise.activity_type == "single_choice":
            items.append({
                "id": item["id"],
                "options": [{"id": option["id"], "label": option["label"]} for option in item["options"]],
            })
        else:
            items.append({"id": item["id"], "label": item["label"], "placeholder": item["placeholder"]})
    return {
        "id": exercise.id,
        "schemaVersion": 1,
        "blockType": "exercise",
        "activityType": exercise.activity_type,
        "exerciseVersion": exercise.version,
        "prompt": exercise.prompt,
        "items": items,
        "gradingDisclosure": {
            "equivalentAnswersMayBeAccepted": exercise.disclosure["equivalentAnswersMayBeAccepted"],
            "aiReviewPossible": exercise.disclosure["aiReviewPossible"],
        },
        "feedbackPolicy": {
            "maxAttempts": ANSWER_KEYS[exercise.answer_key_id].max_attempts,
            "revealAnswer": ANSWER_KEYS[exercise.answer_key_id].reveal_answer,
        },
    }


def public_lesson() -> dict:
    intro, vocabulary, summary = CONTENT_BLOCKS
    blocks = [
        {"id": intro["id"], "schemaVersion": 1, "blockType": "intro", "content": {
            "eyebrow": intro["content"]["eyebrow"],
            "title": intro["content"]["title"],
            "body": intro["content"]["body"],
        }},
        {"id": vocabulary["id"], "schemaVersion": 1, "blockType": "vocabulary", "content": {
            "items": [{"term": item["term"], "translation": item["translation"]} for item in vocabulary["content"]["items"]]
        }},
        *(public_exercise(exercise) for exercise in EXERCISES),
        {"id": summary["id"], "schemaVersion": 1, "blockType": "summary", "content": {
            "title": summary["content"]["title"],
            "body": summary["content"]["body"],
        }},
    ]
    return {
        "id": LESSON["id"],
        "schemaVersion": LESSON["schemaVersion"],
        "version": LESSON["version"],
        "languageTag": LESSON["languageTag"],
        "interfaceLanguageTag": LESSON["interfaceLanguageTag"],
        "level": LESSON["level"],
        "estimatedMinutes": LESSON["estimatedMinutes"],
        "title": LESSON["title"],
        "subtitle": LESSON["subtitle"],
        "blocks": blocks,
    }


class LessonService:
    def __init__(self) -> None:
        validate_seed()
        self._lock = RLock()
        self._attempts: dict[tuple[str, str], list[AttemptRecord]] = {}
        self._idempotency: dict[tuple[str, str], tuple[str, dict]] = {}

    @staticmethod
    def learner_for_token(header: str | None) -> str:
        if not header or not header.startswith("Bearer "):
            raise ApiError(401, "unauthorized", "A demo learner token is required.")
        learner = DEMO_TOKENS.get(header[7:])
        if not learner:
            raise ApiError(401, "unauthorized", "Invalid demo learner token.")
        return learner

    def lesson(self, learner: str, lesson_id: str) -> dict:
        if lesson_id != LESSON["id"]:
            raise ApiError(404, "not_found", "Lesson not found.")
        return public_lesson()

    def progress(self, learner: str) -> dict:
        with self._lock:
            exercises = {}
            for exercise in EXERCISES:
                attempts = self._attempts.get((learner, exercise.id), [])
                exercises[exercise.id] = {
                    "attemptsUsed": len(attempts),
                    "completed": bool(attempts and attempts[-1].result["status"] == "correct"),
                    "lastResult": attempts[-1].result if attempts else None,
                }
            return {"schemaVersion": 1, "exercises": exercises}

    def submit(self, learner: str, payload: object) -> dict:
        if not isinstance(payload, dict):
            raise ApiError(400, "invalid_request", "Expected a JSON object.")
        required = {"exerciseId", "exerciseVersion", "responses", "idempotencyKey"}
        if set(payload) != required:
            raise ApiError(400, "invalid_request", "Invalid attempt fields.")
        exercise_id = payload["exerciseId"]
        version = payload["exerciseVersion"]
        responses = payload["responses"]
        idempotency_key = payload["idempotencyKey"]
        if not isinstance(exercise_id, str) or not isinstance(version, int) or isinstance(version, bool):
            raise ApiError(400, "invalid_request", "Invalid exercise reference.")
        if not isinstance(idempotency_key, str) or not 8 <= len(idempotency_key) <= 100:
            raise ApiError(400, "invalid_request", "Invalid idempotency key.")
        exercise = next((item for item in EXERCISES if item.id == exercise_id), None)
        if not exercise:
            raise ApiError(404, "not_found", "Exercise not found.")
        if version != exercise.version:
            raise ApiError(409, "stale_version", "Reload this lesson before submitting.")
        item_ids = {item["id"] for item in exercise.items}
        if not isinstance(responses, dict) or set(responses) != item_ids:
            raise ApiError(400, "invalid_responses", "Submit one response for every item.")
        if any(not isinstance(value, str) or not value or len(value) > 200 for value in responses.values()):
            raise ApiError(400, "invalid_responses", "Each response must be a non-empty string of at most 200 characters.")
        if exercise.activity_type == "single_choice":
            for item in exercise.items:
                if responses[item["id"]] not in {option["id"] for option in item["options"]}:
                    raise ApiError(400, "invalid_responses", "Select a visible option.")

        fingerprint = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        key = ANSWER_KEYS[exercise.answer_key_id]
        with self._lock:
            prior = self._idempotency.get((learner, idempotency_key))
            if prior:
                if prior[0] != fingerprint:
                    raise ApiError(409, "idempotency_conflict", "This idempotency key was used for another attempt.")
                return prior[1]
            learner_attempts = self._attempts.setdefault((learner, exercise.id), [])
            if len(learner_attempts) >= key.max_attempts or (learner_attempts and learner_attempts[-1].result["status"] == "correct"):
                raise ApiError(409, "attempt_limit", "No attempts remain for this exercise.")
            item_results = []
            for item in exercise.items:
                item_id = item["id"]
                spec = key.items[item_id]
                answer = spec.normalization.apply(responses[item_id])
                accepted = {spec.normalization.apply(variant) for variant in spec.accepted_variants}
                correct = answer in accepted
                item_results.append({
                    "id": item_id,
                    "status": "correct" if correct else "incorrect",
                    "feedback": "Верно!" if correct else "Пока не так. Попробуй ещё раз.",
                })
            correct_count = sum(item["status"] == "correct" for item in item_results)
            status = "correct" if correct_count == len(item_results) else "partial" if correct_count else "incorrect"
            attempt_number = len(learner_attempts) + 1
            reveal = key.reveal_answer == "after_final_attempt" and attempt_number == key.max_attempts
            if reveal:
                for item_result in item_results:
                    spec = key.items[item_result["id"]]
                    if exercise.activity_type == "single_choice":
                        item = next(item for item in exercise.items if item["id"] == item_result["id"])
                        item_result["correctAnswer"] = next(option["label"] for option in item["options"] if option["id"] == spec.accepted_variants[0])
                    else:
                        item_result["correctAnswer"] = spec.accepted_variants[0]
            remaining = 0 if status == "correct" else key.max_attempts - attempt_number
            result = {
                "schemaVersion": 1,
                "attemptId": secrets.token_hex(8),
                "exerciseId": exercise.id,
                "exerciseVersion": exercise.version,
                "status": status,
                "items": item_results,
                "attemptsUsed": attempt_number,
                "attemptsRemaining": remaining,
                "nextAction": "retry" if remaining else "complete",
            }
            learner_attempts.append(AttemptRecord(learner, exercise.id, exercise.version, dict(responses), result, idempotency_key))
            self._idempotency[(learner, idempotency_key)] = (fingerprint, result)
            return result

    def reset_demo(self, learner: str) -> dict:
        with self._lock:
            for key in list(self._attempts):
                if key[0] == learner:
                    del self._attempts[key]
            for key in list(self._idempotency):
                if key[0] == learner:
                    del self._idempotency[key]
        return {"ok": True}
