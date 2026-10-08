"""Application workflow, separate from the Streamlit interface."""

import re
from pathlib import Path

from chatbot.faq import retrieve, source_context
from chatbot.llm import AIError, generate_assignment_answer

OUT_OF_DOMAIN = (
    "I can help with your AI internship chatbot assignment and its implementation. "
    "That question is outside this scope. Ask about the project requirements, Python, "
    "Streamlit, FAQ retrieval, AI integration, testing, or deployment."
)


def assignment_sources(faqs):
    try:
        text = (Path(__file__).resolve().parents[1] / "data" / "assignment.txt").read_text(encoding="utf-8")
    except OSError:
        raise AIError("Could not load the assignment reference. Check data/assignment.txt.") from None
    return [*faqs, {"id": "ASSIGNMENT", "question": "Original AI Internship Chatbot Task Assignment", "answer": text}]

NO_MATCH = (
    "I couldn't find that information in the FAQ knowledge base. "
    "I can help with the internship's technologies, chatbot requirements, README, "
    "deployment, submission, and evaluation. Try one of those topics or browse the FAQ library."
)


def answer_question(question, faqs, mode, api_key="", model="gemini-2.5-flash"):
    question = question.strip()
    if not question or len(question) > 4000:
        raise AIError("Enter a question between 1 and 4,000 characters.")
    normalized = re.sub(r"[^a-z0-9\s]", "", question.casefold())
    normalized = " ".join(normalized.split())
    if normalized in {"hi", "hello", "hey", "hi there", "hello there", "good morning", "good afternoon", "good evening", "salam", "assalamualaikum", "help", "what can you do", "how can you help me"}:
        return {
            "content": "Hello! I can help you with the AI internship assignment. Ask about required technologies, the README, deployment, submission, or evaluation. For example: **What do I submit at the end?**",
            "sources": [], "mode": "Welcome",
        }
    if normalized in {"thanks", "thank you", "thanks a lot", "thank you very much"}:
        return {"content": "You're welcome! Feel free to ask another question about the internship assignment.", "sources": [], "mode": "Conversation"}
    if normalized in {"how are you", "how are you doing", "how r u", "how are u", "hows it going"}:
        return {"content": "I'm ready to help! How is your chatbot project going? Ask me about the assignment or how to build it.", "sources": [], "mode": "Conversation"}
    if mode == "AI answers":
        sources = assignment_sources(faqs)
        source_by_id = {row["id"]: row for row in sources}
        result = generate_assignment_answer(question, api_key, model, source_context(sources), list(source_by_id))
        if result["kind"] == "out_of_domain":
            # Never display the model's generated content after a scope rejection.
            return {"content": OUT_OF_DOMAIN, "sources": [], "mode": "Outside assignment scope"}
        content = result["answer"].strip()
        if result["kind"] == "implementation_guidance":
            content = "**Implementation guidance**\n\n" + content
        cited_ids = list(dict.fromkeys(result["source_ids"]))
        matches = [source_by_id[source_id] for source_id in cited_ids]
        return {"content": content, "sources": matches, "mode": mode}
    # Preserve the real question when a user starts it with a greeting.
    lookup_question = re.sub(r"^(?:hi|hello|hey|good morning|good afternoon|good evening)\b[\s,!.:;-]*", "", question, flags=re.IGNORECASE)
    matches = retrieve(lookup_question or question, faqs)
    if not matches:
        return {"content": NO_MATCH, "sources": [], "mode": "No FAQ match"}
    content = "\n\n".join(f"{row['answer']} [{row['id']}]" for row in matches)
    return {"content": content, "sources": matches, "mode": mode}


def export_chat(messages):
    """Export only conversation content, never API configuration."""
    sections = ["# FAQ Chatbot conversation"]
    for message in messages:
        sections.append(f"## {message['role'].title()}\n\n{message['content']}")
        if message.get("mode"):
            sections.append(f"Answer mode: {message['mode']}")
        if message.get("sources"):
            sections.append("Sources: " + ", ".join(row["id"] for row in message["sources"]))
    return "\n\n".join(sections)
