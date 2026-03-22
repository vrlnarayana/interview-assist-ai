# Technical Interview Copilot

Local Streamlit app for adaptive interviews using your OpenAI API key.

## What it does
- Reads your JD and candidate files from this folder.
- Builds a candidate-specific question bank with expected good answers and rating guides.
- Lets you capture interview answers by microphone (`st.audio_input`) or pasted transcript.
- Scores each answer across technical, functional, and leadership dimensions.
- Suggests adaptive next questions on the fly.
- Produces a final recommendation report and saves it in `reports/`.

## Files expected (already present)
- `Technical_Lead_Full_Stack_AI_Enabled_Systems.pdf`
- `Jayalakshmi_TechnicalLead.docx` (or PDF variant)
- `NehaK.A_TechnicalLead.pdf`
- Optional: `*_resume_analysis.pdf`, `*_resume_score.pdf`

## Run
```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Usage
1. Enter your OpenAI API key in the sidebar.
2. Select candidate.
3. Click `Generate Dossier`.
4. Ask the suggested question.
5. Record answer or paste transcript.
6. Click `Evaluate Answer & Get Next Question` repeatedly.
7. Click `Generate Final Report` at the end.

## Notes
- Interview model default: `gpt-4.1`
- Transcription model default: `gpt-4o-mini-transcribe`
- You can change both from sidebar.
