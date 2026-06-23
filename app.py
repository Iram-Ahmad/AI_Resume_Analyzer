import streamlit as st
import matplotlib.pyplot as plt
from utils.pdf_parser import extract_text_from_pdf

# 👉 NEW IMPORTS (PDF REPORT)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄")

st.title("📄 AI Resume Analyzer (ATS Pro + Dashboard)")
st.write("Resume vs Job Description Smart Matching System")

# -----------------------------
# SKILL DATABASE
# -----------------------------
SKILLS_DB = {
    "software": [
        "python", "java", "c++", "sql", "machine learning",
        "deep learning", "pandas", "numpy", "streamlit",
        "flask", "django", "git", "github",
        "html", "css", "javascript", "react",
        "nodejs", "docker", "aws"
    ],
    "data": [
        "excel", "power bi", "tableau", "data analysis",
        "statistics", "pandas", "numpy", "sql"
    ],
    "finance": [
        "accounting", "financial analysis", "excel",
        "budgeting", "erp"
    ],
    "marketing": [
        "seo", "social media", "google ads",
        "content writing", "marketing strategy"
    ]
}

# -----------------------------
# FIELD DETECTION
# -----------------------------
def detect_field(text):
    text = text.lower()
    scores = {}

    for category, skills in SKILLS_DB.items():
        score = sum(1 for skill in skills if skill in text)
        scores[category] = score

    best_field = max(scores, key=scores.get)

    if scores[best_field] == 0:
        return "unknown"

    return best_field

# -----------------------------
# RESUME SKILLS
# -----------------------------
def extract_skills(text, field):
    text = text.lower()
    found = []

    if field == "unknown":
        return found

    for skill in SKILLS_DB[field]:
        if skill in text:
            found.append(skill)

    return found

# -----------------------------
# JD SKILLS EXTRACTION
# -----------------------------
def extract_jd_skills(jd_text):
    jd_text = jd_text.lower()
    jd_skills = []

    for category in SKILLS_DB:
        for skill in SKILLS_DB[category]:
            if skill in jd_text:
                jd_skills.append(skill)

    return list(set(jd_skills))

# -----------------------------
# MATCH SCORE
# -----------------------------
def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0, [], resume_skills

    matched = []
    missing = []

    for skill in jd_skills:
        if skill in resume_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    score = (len(matched) / len(jd_skills)) * 100

    return round(score, 2), matched, missing

# -----------------------------
# CHART FUNCTION
# -----------------------------
def show_chart(matched, missing):
    labels = ['Matched Skills', 'Missing Skills']
    values = [len(matched), len(missing)]

    fig, ax = plt.subplots()
    ax.bar(labels, values)

    ax.set_title("ATS Skill Analysis")
    st.pyplot(fig)

# -----------------------------
# NEW FEATURE: AI FEEDBACK
# -----------------------------
def generate_feedback(score, missing):
    if score >= 80:
        return "🔥 Excellent profile! High chances of selection."
    elif score >= 50:
        return f"⚠️ Good profile but improve: {', '.join(missing[:3])}"
    else:
        return f"❌ Low match. Focus on learning: {', '.join(missing[:5])}"

# -----------------------------
# NEW FEATURE: PDF REPORT
# -----------------------------
def generate_pdf_report(score, matched, missing):
    file_name = "resume_report.pdf"
    doc = SimpleDocTemplate(file_name)

    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("AI Resume Analysis Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Match Score: {score}%", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Matched Skills:", styles["Heading2"]))
    content.append(Paragraph(", ".join(matched) if matched else "None", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Missing Skills:", styles["Heading2"]))
    content.append(Paragraph(", ".join(missing) if missing else "None", styles["Normal"]))

    doc.build(content)
    return file_name

# -----------------------------
# UI
# -----------------------------
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description Here")

if uploaded_file is not None:

    resume_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📌 Resume Text")
    st.text_area("Resume Content", resume_text, height=250)

    # Field detection
    field = detect_field(resume_text)

    st.subheader("🎯 Detected Field")
    if field == "unknown":
        st.error("Field not detected clearly")
    else:
        st.success(field.upper())

    # Resume skills
    resume_skills = extract_skills(resume_text, field)

    st.subheader("🧠 Resume Skills")
    for skill in resume_skills:
        st.write("✔", skill)

    # JD analysis
    if jd_text:

        jd_skills = extract_jd_skills(jd_text)

        st.subheader("📊 Job Description Skills")
        for skill in jd_skills:
            st.write("🔹", skill)

        score, matched, missing = calculate_match_score(resume_skills, jd_skills)

        st.subheader("📈 ATS MATCH SCORE")
        st.metric("Match %", f"{score}%")

        st.write("### ✔ Matched Skills")
        for m in matched:
            st.write("✔", m)

        st.write("### ❌ Missing Skills")
        for m in missing:
            st.write("➖", m)

        # CHART
        show_chart(matched, missing)

        # -----------------------------
        # NEW UI: AI FEEDBACK
        # -----------------------------
        st.subheader("🤖 AI Feedback")
        st.info(generate_feedback(score, missing))

        # -----------------------------
        # NEW UI: DOWNLOAD REPORT
        # -----------------------------
        if st.button("📄 Download Report"):
            file = generate_pdf_report(score, matched, missing)

            with open(file, "rb") as f:
                st.download_button(
                    label="⬇ Download PDF Report",
                    data=f,
                    file_name="ATS_Report.pdf",
                    mime="application/pdf"
                )