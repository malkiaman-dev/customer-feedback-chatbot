# FAQ Chatbot

Student 1 FAQ chatbot for `AI_Internship_Chatbot_Task_Assignment.pdf`. Includes a predefined FAQ dataset, retrieval, a Streamlit chat UI, Gemini integration, source references, error handling, and a preview mode that works without an API key. Sample FAQs describe the provided assignment.

## Technologies

Python 3.11 or later, Streamlit, Requests, and the Google Gemini REST API.

## Local setup

Run these commands in PowerShell from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and set `GEMINI_API_KEY` to your own key from https://aistudio.google.com/apikey. Set `GEMINI_MODEL` to a model available to your account. The example model is configurable. Never commit your secrets file.

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit. You can also provide the key through the sidebar or the `GEMINI_API_KEY` environment variable. API use is subject to your provider's quota and billing settings.

Your saved API key is used by default. To replace it temporarily, open **AI configuration**, enable **Use a different API key**, and enter the replacement. Turn the option off to return to the saved key. An empty replacement disables AI chat until you enter a key. To change the saved default permanently, edit `.streamlit/secrets.toml` and restart Streamlit. Saved Streamlit secrets take precedence over environment variables.

## Usage and pipeline

The app has **Chat**, **FAQ library**, and **Project guide** pages. Without a configured key it defaults to **FAQ preview**. With a configured key it defaults to **AI answers**. Preview is for testing retrieval; use AI answers for the assignment demonstration.

Ask a question or click a suggested question. Expand Sources to inspect supporting entries. Search the FAQ library by keyword or topic, then choose Ask this question to open it in chat. New conversation clears the chat, and Download chat saves a Markdown transcript without API configuration. If an API request fails, retry the saved question.

Greetings, thanks, help requests, and "how are you" receive local conversational replies. AI mode understands assignment-related questions using the complete assignment text and FAQs, even when keyword retrieval finds no match. It can explain requirements and provide practical help building the assigned chatbot projects. Unrelated questions are declined. Preview mode continues to use FAQ matching without an API request.

In preview mode, the pipeline validates the question, removes common words, normalizes aliases, and ranks FAQs using weighted word overlap. A match must cover at least 60% of the weighted query terms; lower-ranked unrelated entries are excluded. Up to three stored answers are displayed. A question with no match returns a helpful message without an API request.

In AI mode, the complete `data/assignment.txt` reference and predefined FAQs are sent to Gemini. Structured output separates assignment facts, implementation guidance, unspecified facts, and out-of-domain requests. Assignment facts must come from the supplied reference. Practical coding advice is labeled as guidance. Missing facts, such as a deadline, must be acknowledged rather than invented. Scope rejections display a fixed local message; the generated unrelated content is discarded. Returned source identifiers are validated against the actual knowledge base. Questions are independent; previous messages are not sent to the model.

Edit `data/faqs.json` to extend the predefined FAQs. Each entry needs a unique `id`, `question`, `answer`, and optional `category` and list of `keywords`. `data/assignment.txt` contains text extracted from the provided assignment PDF. Update this reference if the assignment changes. Preview retrieval is intentionally simple, so unlisted synonyms can be missed. AI relevance and factual grounding depend on the model; inspect Sources and verify implementation advice before using it.

## Code organization

- `app.py`: Streamlit pages, configuration, and session state.
- `chatbot/faq.py`: Dataset validation and retrieval.
- `chatbot/llm.py`: Gemini API request and safe errors.
- `chatbot/service.py`: Answer workflow and chat export.
- `assets/style.css`, `.streamlit/config.toml`: Visual styles and theme.
- `data/faqs.json`, `data/assignment.txt`: Predefined FAQs and full assignment reference.
- `tests/`: Retrieval, API, and interface checks.
- `docs/`: Demo, deployment, design, and requirement checklist.

## Checks

```powershell
python -m unittest discover -s tests -v
```

Tests use mocked API responses and Streamlit's application test runner. They do not call a paid API.

Checks cover all predefined questions, paraphrases, unknown topics, invalid inputs, malformed datasets, API responses and timeouts, navigation, suggestions, preview chat, mocked AI chat and retry. In this restricted Windows environment, Streamlit's test runner can emit a temporary-directory cleanup permission error after tests. Mocked API tests verify integration behavior, not live model availability or answer quality.

All 20 automated checks passed. Desktop and phone screenshots were reviewed, and phone, tablet, and landscape overflow checks passed. The restricted Windows cleanup error did not occur when the tests were run outside the sandbox. An optional `scripts/visual_check.py` uses Playwright with installed Edge for local screenshots; it is not an application dependency.

The interface uses a charcoal theme with mint accents, an illustrated typographic welcome mark, descriptive question cards, and responsive layouts. Restart an existing Streamlit server after changing `.streamlit/config.toml` to load the current theme.

Live checks verified assignment-related guidance, a missing deadline, rejection of an unrelated sports question, and rejection of a request to bypass the domain boundary. Deployed testing is still pending public deployment.

## Deployment and submission

1. Configure an API key and test the AI workflow locally.
2. Create a GitHub repository and push the source, excluding secrets.
3. Create an app at https://share.streamlit.io, select the repository and `app.py`.
4. Add `GEMINI_API_KEY` and `GEMINI_MODEL` in deployment secrets.
5. Test the deployed main workflow and invalid inputs.
6. Submit the GitHub URL, live URL, and a short demonstration of the pipeline.

Official deployment instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

No GitHub repository or public deployment has been created yet. Live AI calls also require an API key.

See [the requirements audit](docs/requirements-checklist.md), [deployment guide](docs/deployment.md), and [demo script](docs/demo.md). Full submission compliance requires the pending public repository, deployed URL, deployed testing, and recorded demonstration.
