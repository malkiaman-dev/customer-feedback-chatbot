# Deploy and verify

## GitHub

Create an empty repository in your own GitHub account. From the project folder:

```powershell
git init
git add .
git status
git commit -m "Build internship FAQ chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the placeholder URL. Review staged files before committing. `.streamlit/secrets.toml`, `.env`, virtual environments, temporary files, and Python caches are excluded by `.gitignore`. If Git asks for your identity, configure your own name and email.

## Streamlit Community Cloud

1. Sign in at https://share.streamlit.io with your GitHub account.
2. Create an app from your repository, main branch, and `app.py` entry point.
3. Choose Python 3.13 if available, or Python 3.11 or later.
4. In deployment settings, add the following secrets with your real key and an available Gemini model:

```toml
GEMINI_API_KEY = "YOUR_REAL_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
```

5. Deploy, then open the public app URL in a separate browser session.

The app defaults to AI answers when a key is configured. A successfully loaded key is not proof that it is valid; test an actual supported question.

## Live verification checklist

- App opens without running Python locally.
- Supported question returns a Gemini answer and a relevant source.
- A paraphrase such as "What tech stack?" finds the technology FAQ.
- An unknown question such as "What is the internship salary?" returns the no-match message.
- FAQ library search, Ask this question, New conversation, and Download chat work.
- Invalid configuration produces a clear error without exposing the key.
- Layout is usable on desktop and phone; keyboard focus is visible.
- Both the GitHub URL and public deployment URL are included in submission.

Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
