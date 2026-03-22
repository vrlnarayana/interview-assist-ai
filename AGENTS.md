# Repository Guidelines

## Project Structure & Module Organization
- Main application: `app.py` (Streamlit UI + OpenAI-driven interview workflow).
- Dependency manifest: `requirements.txt`.
- User docs: `README.md`, `INTERVIEW_GUIDE.md`.
- Input assets (JD/resumes/analysis): top-level PDF/DOCX files in the repo root.
- Generated outputs: `reports/` (final interview recommendation files).
- Local environments: `.venv311/` (preferred), `.venv/` (legacy). Do not commit virtualenv contents.

## Build, Test, and Development Commands
- Create environment: `python3.11 -m venv .venv311`
- Activate: `source .venv311/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Run app locally: `streamlit run app.py`
- Quick syntax check: `python -m py_compile app.py`

Use `.venv311` for all development to avoid Python 3.7 compatibility issues.

## Coding Style & Naming Conventions
- Language: Python.
- Follow PEP 8 with 4-space indentation.
- Prefer clear function names in `snake_case` (e.g., `build_dossier`, `final_report`).
- Keep Streamlit UI labels user-friendly; keep backend helper functions pure where possible.
- Keep prompts and JSON schemas explicit and stable; avoid silent schema drift.

## Testing Guidelines
- No formal test suite exists yet.
- Minimum validation before PR:
  - `python -m py_compile app.py`
  - Run app and verify: dossier generation, turn evaluation, report generation.
- If adding complex logic, create focused unit tests under a future `tests/` directory using `pytest`.

## Commit & Pull Request Guidelines
- Follow conventional style seen in history: `docs: ...`, `fix: ...`, `feat: ...`.
- Keep commits scoped and atomic (one logical change per commit).
- PRs should include:
  - What changed and why
  - Any prompt/schema updates
  - Manual test steps and outcomes
  - Screenshots for UI changes (Streamlit pages)

## Security & Configuration Tips
- Never hardcode API keys; use sidebar input or `OPENAI_API_KEY` env var.
- Do not commit candidate-sensitive outputs unless explicitly required.
- Treat resume/JD files as confidential hiring data.
