"""Regression checks for FAQ matching, AI errors, and UI navigation."""
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import requests
from streamlit.testing.v1 import AppTest

from chatbot.faq import load_faqs, retrieve
from chatbot.llm import AIError, generate_answer, generate_assignment_answer
from chatbot.service import answer_question, export_chat

FAQS = load_faqs(Path("data/faqs.json"))


class WorkflowTests(unittest.TestCase):
    @patch("chatbot.service.generate_assignment_answer")
    def test_greetings_and_greeting_with_question(self, generate):
        for question in ["hi", "Hello!", "thank you", "What can you do?", "how are you"]:
            result = answer_question(question, FAQS, "AI answers", "fake-key")
            self.assertNotEqual(result["mode"], "No FAQ match")
            self.assertEqual(result["sources"], [])
        generate.assert_not_called()
        result = answer_question("Hi, which technologies are required?", FAQS, "FAQ preview")
        self.assertEqual(result["sources"][0]["id"], "FAQ-02")

    def test_all_faq_questions_find_their_source(self):
        for row in FAQS:
            with self.subTest(row=row["id"]):
                self.assertEqual(retrieve(row["question"], FAQS)[0]["id"], row["id"])

    def test_paraphrases_and_unrelated_questions(self):
        for question, expected in [("What tech stack?", "FAQ-02"), ("Is hosting required?", "FAQ-05"), ("How is it graded?", "FAQ-07")]:
            self.assertEqual(retrieve(question, FAQS)[0]["id"], expected)
        for question in ["What is the internship salary?", "What is the project deadline?", "Who won the football match?", "   "]:
            self.assertEqual(retrieve(question, FAQS), [])

    @patch("chatbot.service.generate_assignment_answer")
    def test_preview_no_match_never_calls_ai(self, generate):
        result = answer_question("What is the project deadline?", FAQS, "FAQ preview", "fake-key")
        self.assertEqual(result["sources"], [])
        generate.assert_not_called()

    def test_invalid_input(self):
        for question in [" ", "a" * 4001]:
            with self.assertRaises(AIError):
                answer_question(question, FAQS, "FAQ preview")

    @patch("chatbot.service.generate_assignment_answer")
    def test_ai_uses_full_assignment_when_no_faq_matches(self, generate):
        question = "How do I split PDF text into useful chunks for Student 2?"
        self.assertEqual(retrieve(question, FAQS), [])
        generate.return_value = {"kind": "implementation_guidance", "answer": "Split into overlapping chunks. [ASSIGNMENT]", "source_ids": ["ASSIGNMENT"]}
        result = answer_question(question, FAQS, "AI answers", "fake-key")
        self.assertIn("Implementation guidance", result["content"])
        self.assertEqual(result["sources"][0]["id"], "ASSIGNMENT")
        self.assertIn("PDF Question", generate.call_args.args[3])

    @patch("chatbot.service.generate_assignment_answer")
    def test_outside_domain_content_is_discarded(self, generate):
        generate.return_value = {"kind": "out_of_domain", "answer": "This unrelated generated content must never be shown.", "source_ids": []}
        result = answer_question("Who won the football match?", FAQS, "AI answers", "fake-key")
        self.assertEqual(result["mode"], "Outside assignment scope")
        self.assertNotIn("unrelated generated content", result["content"])
        self.assertEqual(result["sources"], [])

    @patch("chatbot.service.generate_assignment_answer")
    def test_unspecified_assignment_fact(self, generate):
        generate.return_value = {"kind": "not_specified", "answer": "The assignment does not specify a deadline. [ASSIGNMENT]", "source_ids": ["ASSIGNMENT"]}
        result = answer_question("What is the project deadline?", FAQS, "AI answers", "fake-key")
        self.assertIn("does not specify", result["content"])
        self.assertEqual(result["mode"], "AI answers")

    @patch("chatbot.llm.generate_answer")
    def test_structured_answer_validation(self, generate):
        for response in ["not JSON", '{"kind":"assignment_fact","answer":"ok","source_ids":["made-up"]}', '{"kind":"unexpected","answer":"ok","source_ids":[]}']:
            generate.return_value = response
            with self.assertRaises(AIError):
                generate_assignment_answer("Question", "fake-key", "model", "context", ["FAQ-02"])
        generate.return_value = '{"kind":"assignment_fact","answer":"Use Python.","source_ids":["FAQ-02"]}'
        result = generate_assignment_answer("Question", "fake-key", "model", "context", ["FAQ-02"])
        self.assertEqual(result["source_ids"], ["FAQ-02"])
        self.assertIn("response_schema", generate.call_args.kwargs)

    def test_duplicate_dataset_identifiers(self):
        with patch.object(Path, "read_text", return_value=json.dumps([FAQS[0], FAQS[0]])):
            with self.assertRaisesRegex(ValueError, "unique"):
                load_faqs(Path("invalid.json"))

    @patch("chatbot.llm.requests.post")
    def test_timeout_and_malformed_response(self, post):
        post.side_effect = requests.Timeout()
        with self.assertRaisesRegex(AIError, "too long"):
            generate_answer("Question", "fake-key", "model")
        post.side_effect = None
        post.return_value = Mock(ok=True, status_code=200)
        for payload in [None, [], {"candidates": []}, {"candidates": [{"content": {"parts": []}}]}]:
            post.return_value.json.return_value = payload
            with self.assertRaises(AIError):
                generate_answer("Question", "fake-key", "model")

    def test_suggestion_and_clear(self):
        app = AppTest.from_file("app.py").run()
        app.radio(key="answer_mode").set_value("FAQ preview").run()
        next(button for button in app.button if button.label == "Required technologies").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["messages"][-1]["sources"][0]["id"], "FAQ-02")
        self.assertIn("FAQ-02", export_chat(app.session_state["messages"]))
        next(button for button in app.button if button.label == "New conversation").click().run()
        self.assertEqual(app.session_state["messages"], [])

    def test_library_search_and_ask(self):
        app = AppTest.from_file("app.py").run()
        app.radio(key="answer_mode").set_value("FAQ preview").run()
        app.radio(key="navigation").set_value("FAQ library").run()
        next(field for field in app.text_input if field.label == "Search FAQs").set_value("README").run()
        self.assertIn("README", app.expander[0].label if app.expander[0].label != "AI configuration" else app.expander[1].label)
        app.button(key="ask_FAQ-04").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["navigation"], "Chat")
        self.assertEqual(app.session_state["messages"][-1]["sources"][0]["id"], "FAQ-04")

    @patch("chatbot.service.generate_assignment_answer")
    def test_mocked_ai_flow_and_retry(self, generate):
        app = AppTest.from_file("app.py").run()
        app.radio(key="answer_mode").set_value("AI answers").run()
        if any(toggle.key == "use_custom_key" for toggle in app.toggle):
            app.toggle(key="use_custom_key").set_value(True).run()
        if any(field.key == "session_api_key" for field in app.text_input):
            app.text_input(key="session_api_key").set_value("fake-key").run()
        generate.side_effect = AIError("The API usage limit was reached.")
        app.chat_input[0].set_value("Which technologies are required?").run()
        self.assertTrue(app.error)
        self.assertEqual(app.session_state["messages"], [])
        generate.side_effect = None
        generate.return_value = {"kind": "assignment_fact", "answer": "Use Python and Streamlit. [FAQ-02]", "source_ids": ["FAQ-02"]}
        # Retry is shown on the next render after the failed question is stored.
        app.run()
        next(button for button in app.button if button.label == "Retry last question").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["messages"][-1]["mode"], "AI answers")
        self.assertIn("[FAQ-02]", generate.call_args.args[3])

    @patch("chatbot.service.generate_assignment_answer", return_value={"kind": "assignment_fact", "answer": "Use Python and Streamlit. [FAQ-02]", "source_ids": ["FAQ-02"]})
    def test_saved_key_default_and_session_override(self, generate):
        app = AppTest.from_file("app.py")
        app.secrets["GEMINI_API_KEY"] = "saved-test-key"
        app.run()
        self.assertEqual(app.radio(key="answer_mode").value, "AI answers")
        self.assertFalse(app.toggle(key="use_custom_key").value)
        app.chat_input[0].set_value("Which technologies are required?").run()
        self.assertEqual(generate.call_args.args[1], "saved-test-key")
        app.toggle(key="use_custom_key").set_value(True).run()
        self.assertTrue(app.chat_input[0].disabled)
        app.text_input(key="session_api_key").set_value("replacement-test-key").run()
        app.chat_input[0].set_value("Which technologies are required?").run()
        self.assertEqual(generate.call_args.args[1], "replacement-test-key")
        app.toggle(key="use_custom_key").set_value(False).run()
        app.chat_input[0].set_value("Which technologies are required?").run()
        self.assertEqual(generate.call_args.args[1], "saved-test-key")
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
