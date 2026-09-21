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
