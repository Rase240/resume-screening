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