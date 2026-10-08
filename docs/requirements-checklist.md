# Assignment requirements audit

Scope: Student 1, FAQ Chatbot, in AI_Internship_Chatbot_Task_Assignment.pdf.

| Requirement | Evidence | Status |
| --- | --- | --- |
| Python application logic | chatbot/faq.py, chatbot/service.py, chatbot/llm.py | Implemented |
| Streamlit interface | app.py, .streamlit/config.toml, assets/style.css | Implemented |
| Predefined FAQ knowledge base | data/faqs.json, 10 assignment-based entries | Implemented |
| Retrieve relevant questions and answers | Weighted keyword retrieval, common aliases, weak-match rejection | Tested locally |
| AI API integration | Gemini REST client, source-grounded instructions | Mocked tests pass; supported FAQ request verified with the configured project key |
| Chat interaction and visible answers | Chat page, suggestions, persistent session history | Tested locally |
| Input validation and error handling | Question limits, dataset validation, no-match state, safe API errors, retry | Tested locally |
| Loading indication | Streamlit spinner while preparing answers | Implemented |
| Clear title and description | Chat page title and subtitle | Implemented |
| Simple, clean UI | Charcoal theme, mint accents, mobile layout rules, labeled native widgets | Desktop and phone screenshots reviewed; overflow checks passed at 375, 768, and 1024 pixels |
| File upload controls where required | FAQ project uses a predefined dataset, no uploads needed | Not applicable to Student 1 |
| Usage and project information | Project guide page, README | Implemented |
| Organized code | Separate retrieval, API, workflow, UI, assets, tests, docs | Implemented |
| README setup, description, technology and usage | README.md | Included |
| Sample/test data | data/faqs.json | Included |
| Basic testing | tests/test_starter.py, tests/test_workflows.py | Automated local checks |
| Short project demonstration | docs/demo.md | Script included; record the demo before submission |
| Explain AI pipeline | Project guide, README, docs/demo.md | Included |
| Secure API key configuration | Environment or ignored Streamlit secrets; session-only key input | Implemented |
| GitHub repository | Publish source through your GitHub account | Pending |
| Deployed application and public URL | Streamlit Community Cloud instructions | Pending |
| Test deployed main workflow | docs/deployment.md | Pending public deployment |

The project cannot be described as 100% submitted until a working GitHub URL, a working public app URL, deployed testing, and a recorded demonstration are provided. Preview mode does not meet the AI requirement on its own.

Latest verification: 20 automated tests passed. A supported FAQ question returned a live Gemini response using the configured project key. The key is stored only in the ignored local secrets file. Public deployment testing remains pending.

AI mode now uses the full assignment reference alongside the predefined FAQs. Live checks confirmed related implementation guidance, acknowledgment of an unspecified deadline, and rejection of unrelated sports and boundary-bypass weather requests. Domain classification is model-based; these checks demonstrate the tested cases rather than guarantee all possible prompts.
