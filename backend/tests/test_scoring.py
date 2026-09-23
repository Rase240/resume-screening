from scoring import parse_resume, score

ROLE={"title":"Backend Engineer","description":"Build Python APIs with PostgreSQL and AWS", "required_skills":["Python","PostgreSQL"],"preferred_skills":["AWS"],"min_experience":3,"education":"bachelor","location":"","work_mode":"Remote"}

def test_parser_extracts_contact_skills_and_experience():
    parsed=parse_resume("Ada Test\nBackend Engineer\nada@example.test\n+1 555 010 1234\n5 years Python and PostgreSQL experience\nBachelor of Engineering", "resume.pdf")
    assert parsed["name"]=="Ada Test"
    assert parsed["email"]=="ada@example.test"
    assert parsed["years"]==5
    assert "Python" in parsed["skills"]
    assert parsed["education"]=="Bachelor"

def test_evidence_and_missing_are_explainable():
    good={"text":"Ada Test\nBachelor of Science\n5 years building Python APIs with PostgreSQL on AWS.","parsed":{"years":5}}
    weak={"text":"Ada Test\n2 years building static websites with HTML and CSS.","parsed":{"years":2}}
    a,b=score(ROLE,good),score(ROLE,weak)
    assert a["score"]>b["score"]
    assert a["missing"]==[]
    assert "PostgreSQL" in b["missing"]
    assert any("PostgreSQL" in e["excerpt"] for e in a["evidence"])

def test_skill_match_uses_word_boundaries():
    result=score({**ROLE,"required_skills":["Go"],"preferred_skills":[]},{"text":"Worked with Google Analytics", "parsed":{"years":0}})
    assert result["categories"]["Required skills"]==0

def test_reviewer_skill_correction_changes_match_with_attribution():
    candidate={"text":"Built backend systems for four years.","parsed":{"years":4,"skills":["Python","PostgreSQL"],"education":"Bachelor"}}
    result=score(ROLE,candidate)
    assert result["categories"]["Required skills"]==100
    assert result["evidence"][0]["excerpt"]=="Confirmed by reviewer in corrected skill details."
