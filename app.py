"""Streamlit interface for the internship FAQ chatbot."""
import os
import base64
from pathlib import Path
import tomllib

import streamlit as st

from chatbot.faq import load_faqs
from chatbot.llm import AIError
from chatbot.service import answer_question, export_chat

ROOT = Path(__file__).parent
BOT_ICON = (ROOT / "assets" / "bot.svg").read_text(encoding="utf-8")


def bot_logo(color):
    svg = BOT_ICON.replace('stroke="currentColor"', f'stroke="{color}"')
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{encoded}" alt="" width="32" height="32">'
SUGGESTIONS = [
    ("Required technologies", "Which technologies are required?", ":material/code:"),
    ("What to submit", "What do I submit at the end?", ":material/task_alt:"),
    ("Deployment guidance", "Do I need to deploy the chatbot?", ":material/cloud_upload:"),
    ("README contents", "What should the README include?", ":material/description:"),
]
SUGGESTION_NOTES = [
    "Python, Streamlit, and the AI integration",
    "Your deliverables and final checklist",
    "Get your chatbot ready for a public URL",
    "Setup instructions and documentation",
]


def setting(name, default=""):
    try:
        configured = st.secrets.get(name)
        if configured:
            return str(configured)
    except FileNotFoundError:
        pass
    except (tomllib.TOMLDecodeError, st.errors.StreamlitAPIException):
        st.warning("The secrets configuration could not be read. Check .streamlit/secrets.toml.")
    return os.getenv(name) or default


def show_sources(matches):
    if matches:
        with st.expander(f"Sources ({len(matches)})", icon=":material/library_books:"):
            for row in matches:
                st.markdown(f"**[{row['id']}] {row['question']}**")
                st.write(row["answer"])


def clear_chat():
    st.session_state.messages = []
    st.session_state.failed_question = None
    st.session_state.pending_question = None
    st.session_state.last_error = None


def ask_faq(question):
    st.session_state.pending_question = question
    st.session_state.navigation = "Chat"


st.set_page_config(page_title="FAQ Chatbot", page_icon=":material/forum:", layout="wide")
st.html(f"<style>{(ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>")
try:
    faqs = load_faqs(ROOT / "data" / "faqs.json")
except (OSError, ValueError) as exc:
    st.error(f"Could not load the FAQ knowledge base: {exc}")
    st.stop()

for key, default in (("messages", []), ("pending_question", None), ("failed_question", None), ("last_error", None)):
    if key not in st.session_state:
        st.session_state[key] = default

configured_key = setting("GEMINI_API_KEY").strip()
with st.sidebar:
    st.html(f'<div class="wordmark"><span class="brand-mark" aria-hidden="true">{bot_logo("#102219")}</span><span>FAQ Studio<span class="brand-subtitle">Internship assistant</span></span></div>')
    with st.container(key="workspace_nav"):
        page = st.radio("Workspace", ["Chat", "FAQ library", "Project guide"], key="navigation")
    st.divider()
    st.subheader("Answer mode")
    mode = st.radio("Choose how answers are prepared", ["AI answers", "FAQ preview"], index=0 if configured_key else 1, key="answer_mode")
    st.caption("Stored FAQ answers, no API key needed." if mode == "FAQ preview" else "Ask about the full assignment or how to build your chatbot. Unrelated topics are declined.")
    with st.expander("AI configuration", expanded=mode == "AI answers" and not configured_key, icon=":material/settings:"):
        if configured_key:
            use_custom_key = st.toggle("Use a different API key", key="use_custom_key")
            if not use_custom_key:
                st.success("Using your saved API key.")
        else:
            use_custom_key = True
        if use_custom_key:
            entered_key = st.text_input("Gemini API key", type="password", key="session_api_key", help="Used for this session. Turn off Use a different API key to return to your saved key.")
            st.caption("This replacement applies to the current session.")
        else:
            entered_key = ""
        model = st.text_input("Gemini model", value=setting("GEMINI_MODEL", "gemini-2.5-flash"), key="model_name")
        st.caption("Use a model available to your account. Provider quota and billing apply.")
        st.link_button("Get a Gemini API key", "https://aistudio.google.com/apikey", width="stretch")
    api_key = entered_key.strip() if use_custom_key else configured_key
    st.divider()
    st.button("New conversation", icon=":material/add_comment:", on_click=clear_chat, width="stretch")
    if st.session_state.messages:
        st.download_button("Download chat", export_chat(st.session_state.messages), "faq-conversation.md", "text/markdown", icon=":material/download:", width="stretch")
    st.caption(f"{len(faqs)} FAQs from the supplied assignment")
    st.caption("Python + Streamlit + Gemini")

st.html('<div class="workspace-label">Your knowledge workspace</div>')

if page == "FAQ library":
    st.title("FAQ library")
    st.write("Browse the exact answers your chatbot uses. Search by topic or keyword.")
    search = st.text_input("Search FAQs", placeholder="Try deployment, README, or technologies")
    categories = ["All topics"] + sorted({row.get("category", "General") for row in faqs})
    category = st.selectbox("Topic", categories)
    visible = [row for row in faqs if (category == "All topics" or row.get("category", "General") == category) and search.casefold() in (row["question"] + " " + row["answer"] + " " + " ".join(row.get("keywords", []))).casefold()]
    st.caption(f"Showing {len(visible)} of {len(faqs)} FAQs")
    if not visible:
        st.info("No FAQs match this search. Try another keyword or choose All topics.")
    for row in visible:
        with st.expander(row["question"]):
            st.caption(f"{row['id']} | {row.get('category', 'General')}")
            st.write(row["answer"])
            st.button("Ask this question", key=f"ask_{row['id']}", icon=":material/arrow_forward:", on_click=ask_faq, args=(row["question"],))

elif page == "Project guide":
    st.title("Project guide")
    st.write("A beginner FAQ chatbot built for Student 1's internship assignment.")
    st.subheader("Start a conversation")
    st.markdown("1. Choose **FAQ preview** to explore without a key, or **AI answers** to use Gemini.\n2. Ask a specific question or select a suggested question.\n3. Open **Sources** to check the supporting FAQ.\n4. Use **New conversation** to clear the chat or **Download chat** to save it.")
    st.subheader("How an answer is prepared")
    st.markdown("**Your question → validate input → check assignment scope → prepare an answer → show sources**")
    st.write("AI mode uses the complete assignment and predefined FAQs to understand related questions, explain requirements, and offer implementation guidance. It declines unrelated topics and identifies facts the assignment does not specify. Preview mode displays matching stored FAQ answers. Questions are handled independently; previous messages are not sent to the model.")
    st.subheader("Project information")
    st.write("The sample knowledge base covers the assignment provided by Fazal Wahid, AI Team Lead. It contains predefined questions, answers, keywords, and topics. File uploads are not required for the FAQ assignment.")
    st.subheader("Before submission")
    st.markdown("- Test AI answers using a valid API key.\n- Publish the source to your GitHub repository.\n- Deploy to Streamlit Community Cloud with secrets configured.\n- Test the main workflow through the public URL.\n- Submit both URLs and record a short demonstration.")
    st.info("Before submission, test AI answers with your key, publish your GitHub repository, and verify the public deployment.")

else:
    st.title("FAQ Chatbot")
    st.write("Your assignment, explained. Every answer starts with a source.")
    status = "AI answers · Gemini" if mode == "AI answers" and api_key else "FAQ preview · No API needed" if mode == "FAQ preview" else "AI answers · API key needed"
    st.html(f'<div class="status">{status}</div>')
    if mode == "AI answers" and not api_key:
        st.info("Enter your Gemini API key under AI configuration, or switch to FAQ preview.")
    ready = mode == "FAQ preview" or bool(api_key)

    with st.container(key="conversation"):
        if not st.session_state.messages:
            st.html(f'<div class="welcome"><div class="assistant-mark" aria-hidden="true">{bot_logo("#94e2be")}<span>?</span></div><h2>Good questions.<br><span>Clear answers.</span></h2><p>From your first line of code to your final submission.<br> Ask a question, or start with a topic below.</p></div>')
            with st.container(key="suggestions"):
                for start in (0, 2):
                    columns = st.columns(2)
                    for offset, (column, (label, prompt, icon)) in enumerate(zip(columns, SUGGESTIONS[start:start + 2])):
                        with column:
                            with st.container(key=f"suggestion_{start + offset}"):
                                if st.button(label, icon=icon, width="stretch", disabled=not ready):
                                    st.session_state.pending_question = prompt
                                st.html(f'<p class="suggestion-note">{SUGGESTION_NOTES[start + offset]}</p>')
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=":material/person:" if message["role"] == "user" else ":material/forum:"):
                st.markdown(message["content"])
                if message.get("mode"):
                    st.caption(message["mode"])
                show_sources(message.get("sources", []))

        if st.session_state.failed_question:
            st.error(st.session_state.last_error)
            st.caption("Your question is saved for retry. No answer was added to the conversation.")
            if st.button("Retry last question", icon=":material/refresh:", disabled=not ready):
                st.session_state.pending_question = st.session_state.failed_question
        typed_question = st.chat_input("Ask about the internship assignment...", key="question_input", max_chars=4000, disabled=not ready)
        question = typed_question or (st.session_state.pending_question if ready else None)
        if question:
            st.session_state.pending_question = None
            with st.chat_message("user", avatar=":material/person:"):
                st.markdown(question)
            try:
                with st.spinner("Looking up FAQs and preparing your answer..."):
                    result = answer_question(question, faqs, mode, api_key, model)
                st.session_state.messages.extend([{"role": "user", "content": question.strip()}, {"role": "assistant", **result}])
                st.session_state.failed_question = None
                st.session_state.last_error = None
                st.rerun()
            except AIError as exc:
                st.session_state.failed_question = question
                st.session_state.last_error = str(exc)
                st.rerun()

    st.html('<div class="footnote">AI answers cover the assignment and related implementation guidance. Check Sources for assignment facts.</div>')
