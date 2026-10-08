import unittest
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest

from chatbot.llm import AIError, generate_answer


class StarterTests(unittest.TestCase):
    def test_missing_key(self):
        with self.assertRaisesRegex(AIError, "API key"):
            generate_answer("Hello", "", "example-model")

    @patch("chatbot.llm.requests.post")
    def test_source_context_and_answer(self, post):
        post.return_value = Mock(ok=True, status_code=200)
        post.return_value.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "The answer [1]."}]}}]
        }
        self.assertEqual(generate_answer("Question", "test-key", "example-model", "[1] Source"), "The answer [1].")
        self.assertIn("[1] Source", post.call_args.kwargs["json"]["contents"][0]["parts"][0]["text"])

    @patch("chatbot.llm.requests.post")
    def test_quota_error(self, post):
        post.return_value = Mock(ok=False, status_code=429)
        with self.assertRaisesRegex(AIError, "usage limit"):
            generate_answer("Hello", "test-key", "example-model")

    def test_app_loads_without_key(self):
        app = AppTest.from_file("app.py").run(timeout=15)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.title[0].value, "FAQ Chatbot")
        app.radio(key="answer_mode").set_value("FAQ preview").run()
        app.chat_input[0].set_value("Which technologies are required?").run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Streamlit", app.session_state["messages"][-1]["content"])

    def test_retrieval(self):
        from pathlib import Path
        from chatbot.faq import load_faqs, retrieve
        faqs = load_faqs(Path("data/faqs.json"))
        self.assertEqual(retrieve("Which technologies are required?", faqs)[0]["id"], "FAQ-02")
        self.assertEqual(retrieve("What should the README include?", faqs)[0]["id"], "FAQ-04")
        self.assertEqual(retrieve("How old is the moon?", faqs), [])


if __name__ == "__main__":
    unittest.main()
