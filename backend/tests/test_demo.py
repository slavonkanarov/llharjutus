import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.server import create_handler
from backend.service import ApiError, LessonService, public_lesson


def attempt(exercise_id, responses, key="attempt-key-001", version=1):
    return {
        "exerciseId": exercise_id,
        "exerciseVersion": version,
        "responses": responses,
        "idempotencyKey": key,
    }


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.service = LessonService()

    def test_public_lesson_has_no_private_answer_fields(self):
        body = json.dumps(public_lesson(), ensure_ascii=False)
        for private_name in ("answerKeyId", "acceptedVariants", "acceptedAnswers", "correctOption", "correctAnswer", "rubric", "aiPrompt", "normalization"):
            self.assertNotIn(private_name, body)
        self.assertIn('"gradingDisclosure"', body)

    def test_independent_variants_and_strict_diacritics(self):
        result = self.service.submit("learner-one", attempt(
            "exercise-text-1",
            {"blank-greeting": "  TERE!  ", "blank-goodbye": "Nägemist"},
        ))
        self.assertEqual(result["status"], "correct")
        self.assertNotIn("correctAnswer", result["items"][0])
        self.assertNotIn("correctAnswer", result["items"][1])

        result = self.service.submit("learner-two", attempt(
            "exercise-text-1",
            {"blank-greeting": "Tere", "blank-goodbye": "Nagemist"},
        ))
        self.assertEqual(result["status"], "partial")
        self.assertEqual([item["status"] for item in result["items"]], ["correct", "incorrect"])

    def test_reveal_only_after_final_attempt_and_scoped_progress(self):
        wrong = {"choice-meaning": "option-b"}
        first = self.service.submit("learner-one", attempt("exercise-choice-1", wrong))
        self.assertEqual(first["attemptsRemaining"], 1)
        self.assertNotIn("correctAnswer", first["items"][0])
        self.assertEqual(self.service.progress("learner-two")["exercises"]["exercise-choice-1"]["attemptsUsed"], 0)
        second = self.service.submit("learner-one", attempt("exercise-choice-1", wrong, "attempt-key-002"))
        self.assertEqual(second["items"][0]["correctAnswer"], "Пожалуйста")
        self.assertEqual(second["attemptsRemaining"], 0)
        with self.assertRaises(ApiError) as error:
            self.service.submit("learner-one", attempt("exercise-choice-1", wrong, "attempt-key-003"))
        self.assertEqual(error.exception.code, "attempt_limit")

    def test_idempotency_and_stale_version(self):
        payload = attempt("exercise-choice-1", {"choice-meaning": "option-a"})
        first = self.service.submit("learner-one", payload)
        self.assertEqual(first, self.service.submit("learner-one", payload))
        self.assertEqual(self.service.progress("learner-one")["exercises"]["exercise-choice-1"]["attemptsUsed"], 1)
        with self.assertRaises(ApiError) as error:
            self.service.submit("learner-one", attempt("exercise-choice-1", {"choice-meaning": "option-b"}))
        self.assertEqual(error.exception.code, "idempotency_conflict")
        with self.assertRaises(ApiError) as error:
            self.service.submit("learner-two", attempt("exercise-choice-1", {"choice-meaning": "option-a"}, version=2))
        self.assertEqual(error.exception.code, "stale_version")

    def test_invalid_choice_and_item_count(self):
        for responses in ({"choice-meaning": "not-visible"}, {}, {"choice-meaning": "option-a", "extra": "x"}):
            with self.assertRaises(ApiError) as error:
                self.service.submit("learner-one", attempt("exercise-choice-1", responses))
            self.assertEqual(error.exception.code, "invalid_responses")

    def test_demo_reset_only_clears_authenticated_learner(self):
        wrong = {"choice-meaning": "option-b"}
        self.service.submit("learner-one", attempt("exercise-choice-1", wrong))
        self.service.submit("learner-two", attempt("exercise-choice-1", wrong))
        self.service.reset_demo("learner-one")
        self.assertEqual(self.service.progress("learner-one")["exercises"]["exercise-choice-1"]["attemptsUsed"], 0)
        self.assertEqual(self.service.progress("learner-two")["exercises"]["exercise-choice-1"]["attemptsUsed"], 1)


class HttpBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(LessonService()))
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.http.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()

    def test_lesson_requires_authorization_and_exposes_only_public_dto(self):
        path = self.base + "/api/v1/lessons/estonian-first-words"
        with self.assertRaises(HTTPError) as error:
            urlopen(path)
        self.assertEqual(error.exception.code, 401)
        request = Request(path, headers={"Authorization": "Bearer demo-learner-one"})
        with urlopen(request) as response:
            body = response.read().decode("utf-8")
        self.assertIn("single_choice", body)
        self.assertNotIn("answerKeyId", body)
        self.assertNotIn("correctAnswer", body)


if __name__ == "__main__":
    unittest.main()
