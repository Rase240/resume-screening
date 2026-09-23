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

def score(role, candidate):
    text = candidate["text"]
    parsed = candidate["parsed"]
    corrected_skills = parsed.get("skills", [])
    search_text = text + "\n" + "; ".join(corrected_skills)
    required = role.get("required_skills", [])
    preferred = role.get("preferred_skills", [])
    matched_req = [s for s in required if has_skill(search_text, s)]
    matched_pref = [s for s in preferred if has_skill(search_text, s)]
    missing = [s for s in required if s not in matched_req]
    degree_min = norm(role.get("education", ""))
    education_text = parsed.get("education", "") or text
    degree_score = 100 if not degree_min else (100 if any(DEGREES.get(k,0) >= DEGREES.get(degree_min, 99) for k in DEGREES if has_skill(education_text,k)) else 0)
    min_years = float(role.get("min_experience", 0) or 0)
    experience_score = 100 if not min_years else min(100, round(parsed.get("years", 0) / min_years * 100))
    location = norm(role.get("location", ""))
    location_score = 100 if not location or role.get("work_mode") == "Remote" else (100 if location in norm(text) else 0)
    job_text = " ".join([role.get("title", ""), role.get("description", ""), " ".join(required), " ".join(preferred)])
    semantic = round(similarity(job_text, job_relevant_text(text)) * 100)
    categories = {
        "Required skills": round(len(matched_req)/len(required)*100) if required else 100,
        "Preferred skills": round(len(matched_pref)/len(preferred)*100) if preferred else 100,
        "Experience": experience_score, "Education": degree_score,
        "Location": location_score, "Language similarity": semantic,
    }
    weights = role.get("weights") or {"Required skills": 35, "Preferred skills": 10, "Experience": 15, "Education": 10, "Location": 5, "Language similarity": 25}
    active = {k: v for k,v in weights.items() if not ((k == "Required skills" and not required) or (k == "Preferred skills" and not preferred) or (k == "Education" and not degree_min) or (k == "Experience" and not min_years) or (k == "Location" and (not location or role.get("work_mode") == "Remote")))}
    total = sum(active.values()) or 1
    overall = round(sum(categories[k] * v for k,v in active.items()) / total)
    reasons = []
    if matched_req: reasons.append(f"Matches {len(matched_req)} of {len(required)} required skills")
    if missing: reasons.append(f"Missing evidence for {', '.join(missing[:3])}")
    if min_years: reasons.append(f"Estimated {parsed.get('years', 0):g} years against {min_years:g} required")
    return {"score": max(0,min(100,overall)), "categories": categories, "matched": matched_req + matched_pref, "missing": missing, "evidence": [{"requirement": s, "excerpt": evidence(text,s) or "Confirmed by reviewer in corrected skill details."} for s in matched_req + matched_pref], "explanation": ". ".join(reasons) + ("." if reasons else " Review the resume evidence and role description.")}
