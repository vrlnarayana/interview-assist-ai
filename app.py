import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
from openai import OpenAI


APP_TITLE = "Technical Interview Copilot"
BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def extract_text_from_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except Exception as exc:
        return f"[Failed to read PDF: {path.name}. Error: {exc}]"


def extract_text_from_docx(path: Path) -> str:
    try:
        import docx

        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as exc:
        return f"[Failed to read DOCX: {path.name}. Error: {exc}]"


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return f"[Failed to read file: {path.name}. Error: {exc}]"


def find_first(candidates: List[str]) -> Optional[Path]:
    for name in candidates:
        p = BASE_DIR / name
        if p.exists():
            return p
    return None


def clean_json_blob(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def call_json(client: OpenAI, model: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or "{}"
    return clean_json_blob(content)


def build_dossier(
    client: OpenAI,
    model: str,
    jd_text: str,
    candidate_name: str,
    resume_text: str,
    existing_analysis: str,
) -> Dict[str, Any]:
    system_prompt = (
        "You are a principal interviewer. Return strict JSON only. "
        "Design an interview plan with balanced technical, functional, and leadership screening."
    )
    user_prompt = f"""
Create a candidate dossier for tomorrow's interview.

Return JSON with this exact shape:
{{
  "candidate_name": "",
  "fit_summary": "",
  "risk_flags": [""],
  "strengths": [""],
  "coverage_topics": [
    {{"topic": "", "dimension": "technical|functional|leadership", "priority": "high|medium|low", "why": ""}}
  ],
  "question_bank": [
    {{
      "id": "Q1",
      "dimension": "technical|functional|leadership",
      "topic": "",
      "question": "",
      "strong_answer_should_include": [""],
      "weak_answer_signals": [""],
      "rating_guide_1_to_5": {{"1": "", "3": "", "5": ""}}
    }}
  ],
  "initial_recommendation_before_interview": "Strong hire|Hire|Borderline|No hire"
}}

Job Description:
{jd_text[:32000]}

Candidate Resume:
{resume_text[:22000]}

Prior Candidate Analysis:
{existing_analysis[:12000]}
"""
    return call_json(client, model, system_prompt, user_prompt)


def transcribe_audio(client: OpenAI, transcription_model: str, audio_file: Any) -> str:
    transcription = client.audio.transcriptions.create(
        model=transcription_model,
        file=("candidate_response.wav", audio_file.getvalue(), audio_file.type or "audio/wav"),
    )
    return getattr(transcription, "text", "").strip()


def evaluate_turn(
    client: OpenAI,
    model: str,
    jd_text: str,
    candidate_name: str,
    resume_text: str,
    dossier: Dict[str, Any],
    turn_history: List[Dict[str, Any]],
    asked_question: str,
    candidate_answer: str,
) -> Dict[str, Any]:
    system_prompt = (
        "You are an expert technical panel. Return strict JSON only. "
        "Score answers objectively and propose the next best question while balancing topic coverage."
    )
    user_prompt = f"""
Evaluate this interview turn.

Return JSON with exact keys:
{{
  "scores": {{
    "technical": {{"score": 1-5, "reason": ""}},
    "functional": {{"score": 1-5, "reason": ""}},
    "leadership": {{"score": 1-5, "reason": ""}}
  }},
  "answer_quality": "strong|mixed|weak",
  "evidence_hit": [""],
  "gaps": [""],
  "follow_up_probe": "",
  "next_question": {{
    "dimension": "technical|functional|leadership",
    "topic": "",
    "question": "",
    "expected_good_points": [""]
  }},
  "interviewer_note": "",
  "running_recommendation": "Strong hire|Hire|Borderline|No hire"
}}

JD:\n{jd_text[:26000]}

Candidate:\n{candidate_name}\n
Resume:\n{resume_text[:18000]}

Dossier:\n{json.dumps(dossier)[:20000]}

Turn history (latest first):\n{json.dumps(turn_history[-6:])}

Asked question:\n{asked_question}

Candidate answer transcript:\n{candidate_answer}
"""
    return call_json(client, model, system_prompt, user_prompt)


def final_report(
    client: OpenAI,
    model: str,
    candidate_name: str,
    dossier: Dict[str, Any],
    turn_history: List[Dict[str, Any]],
) -> Dict[str, Any]:
    system_prompt = "You are a hiring committee reviewer. Return strict JSON only."
    user_prompt = f"""
Create final recommendation from interview transcript.

Return JSON exactly with keys:
{{
  "candidate": "",
  "final_recommendation": "Strong hire|Hire|Borderline|No hire",
  "overall_score_100": 0,
  "dimension_scores": {{"technical": 0, "functional": 0, "leadership": 0}},
  "hire_rationale": [""],
  "concerns": [""],
  "must_verify_next_round": [""],
  "decision_statement": "",
  "questionwise_ratings": [
    {{"question": "", "technical": 0, "functional": 0, "leadership": 0, "notes": ""}}
  ]
}}

Dossier:\n{json.dumps(dossier)[:22000]}

Turns:\n{json.dumps(turn_history)}

Compute dimension scores 0-100 based on observed evidence only.
"""
    return call_json(client, model, system_prompt, user_prompt)


def render_question_bank(bank: List[Dict[str, Any]]) -> None:
    for q in bank:
        st.markdown(f"**{q.get('id', '')} | {q.get('dimension', '').title()} | {q.get('topic', '')}**")
        st.write(q.get("question", ""))
        st.caption("Strong answer should include:")
        for pt in q.get("strong_answer_should_include", []):
            st.write(f"- {pt}")
        st.caption("Weak answer signals:")
        for pt in q.get("weak_answer_signals", []):
            st.write(f"- {pt}")


def report_to_markdown(report: Dict[str, Any], candidate: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = REPORT_DIR / f"{candidate.replace(' ', '_')}_{ts}.md"

    lines = []
    lines.append(f"# Interview Recommendation - {report.get('candidate', candidate)}")
    lines.append("")
    lines.append(f"Final Recommendation: **{report.get('final_recommendation', 'N/A')}**")
    lines.append(f"Overall Score (100): **{report.get('overall_score_100', 0)}**")
    lines.append("")
    lines.append("## Dimension Scores")
    dim = report.get("dimension_scores", {})
    lines.append(f"- Technical: {dim.get('technical', 0)}")
    lines.append(f"- Functional: {dim.get('functional', 0)}")
    lines.append(f"- Leadership: {dim.get('leadership', 0)}")
    lines.append("")
    lines.append("## Hire Rationale")
    for item in report.get("hire_rationale", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Concerns")
    for item in report.get("concerns", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Must Verify In Next Round")
    for item in report.get("must_verify_next_round", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Decision Statement")
    lines.append(report.get("decision_statement", ""))
    lines.append("")
    lines.append("## Questionwise Ratings")
    for item in report.get("questionwise_ratings", []):
        q = item.get("question", "")
        lines.append(
            f"- Q: {q} | T:{item.get('technical', 0)} F:{item.get('functional', 0)} L:{item.get('leadership', 0)} | {item.get('notes', '')}"
        )

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def bootstrap_data() -> Dict[str, Dict[str, Optional[Path]]]:
    jd_path = find_first([
        "Technical_Lead_Full_Stack_AI_Enabled_Systems.pdf",
        "jd.pdf",
        "JD.pdf",
    ])

    return {
        "Jayalakshmi": {
            "resume": find_first([
                "Jayalakshmi_TechnicalLead.docx",
                "Jayalakshmi_TechnicalLead-20260319142728.pdf",
            ]),
            "analysis": find_first([
                "Jayalakshmi_resume_analysis.pdf",
                "Jayalakshmi_resume_score.pdf",
            ]),
            "jd": jd_path,
        },
        "Neha": {
            "resume": find_first(["NehaK.A_TechnicalLead.pdf"]),
            "analysis": find_first([
                "NehaK_resume_analysis.pdf",
                "NehaK_resume_score.pdf",
            ]),
            "jd": jd_path,
        },
    }


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption("Adaptive interview assistant for technical, functional, and leadership screening")

    data_map = bootstrap_data()

    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        model = st.text_input("Interview model", value="gpt-4.1")
        transcription_model = st.text_input("Transcription model", value="gpt-4o-mini-transcribe")
        candidate = st.selectbox("Candidate", list(data_map.keys()))
        st.write("Files detected:")
        cdata = data_map[candidate]
        st.write(f"- JD: {cdata.get('jd').name if cdata.get('jd') else 'Missing'}")
        st.write(f"- Resume: {cdata.get('resume').name if cdata.get('resume') else 'Missing'}")
        st.write(f"- Analysis: {cdata.get('analysis').name if cdata.get('analysis') else 'Missing'}")

    if not api_key:
        st.warning("Enter your OpenAI API key in the sidebar.")
        return

    cdata = data_map[candidate]
    if not cdata.get("jd") or not cdata.get("resume"):
        st.error("Missing JD or resume file. Place files in the app folder and refresh.")
        return

    client = OpenAI(api_key=api_key)

    if "dossier" not in st.session_state:
        st.session_state.dossier = None
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "last_transcript" not in st.session_state:
        st.session_state.last_transcript = ""

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("1) Build Candidate Dossier")
        if st.button("Generate Dossier"):
            with st.spinner("Reading files and generating interview plan..."):
                jd_text = extract_text(cdata["jd"]) if cdata.get("jd") else ""
                resume_text = extract_text(cdata["resume"]) if cdata.get("resume") else ""
                analysis_text = extract_text(cdata["analysis"]) if cdata.get("analysis") else ""
                st.session_state.source = {
                    "jd_text": jd_text,
                    "resume_text": resume_text,
                    "analysis_text": analysis_text,
                }
                st.session_state.dossier = build_dossier(
                    client=client,
                    model=model,
                    jd_text=jd_text,
                    candidate_name=candidate,
                    resume_text=resume_text,
                    existing_analysis=analysis_text,
                )
                st.session_state.turns = []
                bank = st.session_state.dossier.get("question_bank", [])
                st.session_state.current_question = bank[0]["question"] if bank else ""

        dossier = st.session_state.dossier
        if dossier:
            st.success("Dossier ready")
            st.write(f"**Fit Summary:** {dossier.get('fit_summary', '')}")
            st.write(f"**Pre-Interview Recommendation:** {dossier.get('initial_recommendation_before_interview', '')}")
            st.write("**Risk Flags:**")
            for risk in dossier.get("risk_flags", []):
                st.write(f"- {risk}")

    with col_b:
        st.subheader("2) Topic Coverage")
        dossier = st.session_state.dossier
        if dossier:
            topics = dossier.get("coverage_topics", [])
            for t in topics:
                st.write(
                    f"- [{t.get('dimension','').title()} | {t.get('priority','').title()}] {t.get('topic','')}: {t.get('why','')}"
                )

    st.subheader("3) Question Bank (Expected Answers + Rating Guide)")
    dossier = st.session_state.dossier
    if dossier:
        render_question_bank(dossier.get("question_bank", []))

    st.subheader("4) Live Interview")
    if dossier:
        if not st.session_state.current_question:
            bank = dossier.get("question_bank", [])
            st.session_state.current_question = bank[0]["question"] if bank else ""

        st.write(f"**Ask this now:** {st.session_state.current_question}")

        audio = st.audio_input("Record candidate answer")
        manual_answer = st.text_area("Or paste candidate answer transcript", value="", height=120)

        if st.button("Evaluate Answer & Get Next Question"):
            transcript = ""
            with st.spinner("Transcribing and evaluating..."):
                if audio is not None:
                    transcript = transcribe_audio(client, transcription_model, audio)
                if manual_answer.strip():
                    transcript = (transcript + "\n" + manual_answer).strip() if transcript else manual_answer.strip()

                if not transcript:
                    st.error("No answer captured. Record audio or paste transcript.")
                else:
                    st.session_state.last_transcript = transcript
                    evaluation = evaluate_turn(
                        client=client,
                        model=model,
                        jd_text=st.session_state.source["jd_text"],
                        candidate_name=candidate,
                        resume_text=st.session_state.source["resume_text"],
                        dossier=dossier,
                        turn_history=st.session_state.turns,
                        asked_question=st.session_state.current_question,
                        candidate_answer=transcript,
                    )
                    turn = {
                        "question": st.session_state.current_question,
                        "answer": transcript,
                        "evaluation": evaluation,
                    }
                    st.session_state.turns.append(turn)
                    next_q = evaluation.get("next_question", {}).get("question", "")
                    if next_q:
                        st.session_state.current_question = next_q

        if st.session_state.last_transcript:
            st.caption("Latest transcript")
            st.write(st.session_state.last_transcript)

        if st.session_state.turns:
            st.markdown("**Turn Ratings**")
            for i, t in enumerate(st.session_state.turns, start=1):
                ev = t.get("evaluation", {})
                scores = ev.get("scores", {})
                st.write(
                    f"{i}. {ev.get('answer_quality','').title()} | "
                    f"T:{scores.get('technical', {}).get('score', '-')}/5 "
                    f"F:{scores.get('functional', {}).get('score', '-')}/5 "
                    f"L:{scores.get('leadership', {}).get('score', '-')}/5"
                )
                st.caption(ev.get("interviewer_note", ""))

        st.subheader("5) Final Recommendation Report")
        if st.button("Generate Final Report"):
            if not st.session_state.turns:
                st.error("No interview turns captured yet.")
            else:
                with st.spinner("Generating final recommendation..."):
                    rep = final_report(
                        client=client,
                        model=model,
                        candidate_name=candidate,
                        dossier=dossier,
                        turn_history=st.session_state.turns,
                    )
                    report_path = report_to_markdown(rep, candidate)
                    st.success(f"Report generated: {report_path.name}")
                    st.write(f"**Recommendation:** {rep.get('final_recommendation', '')}")
                    st.write(f"**Overall Score:** {rep.get('overall_score_100', 0)}")
                    st.write("**Decision Statement**")
                    st.write(rep.get("decision_statement", ""))
                    st.download_button(
                        "Download JSON Report",
                        data=json.dumps(rep, indent=2),
                        file_name=f"{candidate.lower()}_report.json",
                        mime="application/json",
                    )


if __name__ == "__main__":
    main()
