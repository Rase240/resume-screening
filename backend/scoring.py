"""Deterministic, inspectable matching. Scores are estimates, never hiring decisions."""
import re
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ALIASES = {
    "javascript": ["js", "ecmascript"], "typescript": ["ts"],
    "python": ["py"], "postgresql": ["postgres"], "kubernetes": ["k8s"],
    "amazon web services": ["aws"], "google cloud platform": ["gcp"],
    "machine learning": ["ml"], "natural language processing": ["nlp"],
    "react": ["react.js", "reactjs"], "node.js": ["nodejs", "node"],
}
KNOWN_SKILLS = ["Python", "Java", "JavaScript", "TypeScript", "React", "Node.js", "Go", "SQL", "PostgreSQL", "MySQL", "MongoDB", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "FastAPI", "Django", "Flask", "Next.js", "Machine Learning", "NLP", "PyTorch", "TensorFlow", "Data Analysis", "Power BI", "Tableau", "Git", "CI/CD", "REST APIs", "GraphQL", "Figma", "Excel"]
DEGREES = {"phd": 4, "doctorate": 4, "master": 3, "mba": 3, "bachelor": 2, "b.tech": 2, "b.e.": 2, "associate": 1, "diploma": 1}

def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def variants(skill):
    key = norm(skill)
    return [key] + ALIASES.get(key, [])

def has_skill(text, skill):
    return any(re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", text, re.I) for v in variants(skill))

def evidence(text, term):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    return next((x[:240] for x in lines if has_skill(x, term)), "")

def job_relevant_text(text):
    excluded = re.compile(r"\b(date of birth|dob|age|gender|sex|marital|nationality|religion|ethnicity|race|pronouns?)\b", re.I)
    lines = [x for x in text.splitlines() if not excluded.search(x)]
    body = "\n".join(lines[1:])  # Drop the name/header line.
    body = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", " ", body)
    body = re.sub(r"(?<!\d)(?:\+?\d[\d ()-]{8,}\d)(?!\d)", " ", body)
    return body

def parse_resume(text, filename=""):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    email = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"(?<!\d)(?:\+?\d[\d ()-]{8,}\d)(?!\d)", text)
    name = next((x for x in lines[:6] if len(x) < 65 and not any(z in x.lower() for z in ["@", "resume", "curriculum", "http", "phone", "email"]) and not re.search(r"\d", x)), filename.rsplit(".",1)[0].replace("_", " "))
    yrs = [float(x) for x in re.findall(r"(\d{1,2}(?:\.\d)?)\s*\+?\s*(?:years|yrs)\b", text, re.I)]
    years = min(max(yrs), 50) if yrs else 0
    if not yrs:
        found = [int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", text)]
        if len(found) >= 2:
            years = min(max(date.today().year - min(found), 0), 50)
    degree = next((k.title() for k in DEGREES if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", text, re.I)), "Not identified")
    skill_list = [s for s in KNOWN_SKILLS if has_skill(text, s)]
    title = next((x for x in lines[1:6] if len(x) < 90 and not re.search(r"@|\d{5,}", x)), "")
    certificates = [x[:120] for x in lines if re.search(r"certif|credential|license", x, re.I)][:5]
    work_history = [x[:180] for x in lines if re.search(r"\b(engineer|developer|designer|analyst|manager|consultant|intern|architect|lead)\b", x, re.I) and x != name][:6]
    return {"name": name, "email": email.group(0) if email else "", "phone": phone.group(0).strip() if phone else "", "title": title, "skills": skill_list, "years": years, "education": degree, "certifications": certificates, "work_history": work_history}

def similarity(job_text, resume_text):
    if not job_text.strip() or not resume_text.strip():
        return 0
    # Word and character n-grams capture phrasing and close terminology. This
    # local, reproducible fallback needs no network model or paid API.
    scores = []
    for analyzer, ngram in [("word", (1, 2)), ("char_wb", (3, 5))]:
        try:
            matrix = TfidfVectorizer(analyzer=analyzer, ngram_range=ngram, stop_words="english" if analyzer == "word" else None, max_features=12000).fit_transform([job_text, resume_text[:30000]])
            scores.append(float(cosine_similarity(matrix[0], matrix[1])[0, 0]))
        except ValueError:
            scores.append(0)
    return round(min(1, scores[0] * .65 + scores[1] * .35), 3)
