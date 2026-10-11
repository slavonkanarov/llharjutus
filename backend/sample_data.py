"""Published demo lesson and separately held private answer specifications."""

from .contracts import AnswerKey, ItemAnswer, Normalization, StoredExercise


LESSON = {
    "id": "estonian-first-words",
    "schemaVersion": 1,
    "version": 1,
    "status": "published",
    "languageTag": "et",
    "interfaceLanguageTag": "ru",
    "level": "A0",
    "estimatedMinutes": 4,
    "title": "Первые слова по-эстонски",
    "subtitle": "Приветствия и вежливые фразы, с которых начинается разговор.",
}

CONTENT_BLOCKS = (
    {
        "id": "intro-1",
        "schemaVersion": 1,
        "blockType": "intro",
        "content": {
            "eyebrow": "НАЧНЁМ С ПРОСТОГО",
            "title": "Четыре фразы на каждый день",
            "body": "Прочитай слова, затем проверь себя в двух коротких заданиях.",
        },
    },
    {
        "id": "vocabulary-1",
        "schemaVersion": 1,
        "blockType": "vocabulary",
        "content": {
            "items": [
                {"term": "Tere", "translation": "Привет / здравствуйте"},
                {"term": "Aitäh", "translation": "Спасибо"},
                {"term": "Palun", "translation": "Пожалуйста"},
                {"term": "Head aega", "translation": "До свидания"},
            ]
        },
    },
    {
        "id": "summary-1",
        "schemaVersion": 1,
        "blockType": "summary",
        "content": {
            "title": "Уже начало!",
            "body": "Эти фразы пригодятся в магазине, кафе и при знакомстве. Возвращайся к ним, пока они не станут привычными.",
        },
    },
)

EXERCISES = (
    StoredExercise(
        id="exercise-choice-1",
        version=1,
        activity_type="single_choice",
        prompt="Что означает «Palun»?",
        items=(
            {
                "id": "choice-meaning",
                "options": [
                    {"id": "option-c", "label": "До свидания"},
                    {"id": "option-a", "label": "Пожалуйста"},
                    {"id": "option-b", "label": "Спасибо"},
                ],
            },
        ),
        disclosure={"equivalentAnswersMayBeAccepted": False, "aiReviewPossible": False},
        answer_key_id="key-choice-1",
    ),
    StoredExercise(
        id="exercise-text-1",
        version=1,
        activity_type="fill_blanks",
        prompt="Переведи фразы на эстонский",
        items=(
            {"id": "blank-greeting", "label": "Привет", "placeholder": "Напиши перевод"},
            {"id": "blank-goodbye", "label": "До свидания", "placeholder": "Напиши перевод"},
        ),
        disclosure={"equivalentAnswersMayBeAccepted": True, "aiReviewPossible": False},
        answer_key_id="key-text-1",
    ),
)

ANSWER_KEYS = {
    "key-choice-1": AnswerKey(
        exercise_id="exercise-choice-1",
        exercise_version=1,
        items={"choice-meaning": ItemAnswer(("option-a",), Normalization())},
        max_attempts=2,
        reveal_answer="after_final_attempt",
    ),
    "key-text-1": AnswerKey(
        exercise_id="exercise-text-1",
        exercise_version=1,
        items={
            "blank-greeting": ItemAnswer(("Tere", "Tere!"), Normalization(trim=True, case_fold=True)),
            "blank-goodbye": ItemAnswer(("Head aega", "Nägemist"), Normalization(trim=True, case_fold=True)),
        },
        max_attempts=2,
        reveal_answer="after_final_attempt",
    ),
}
