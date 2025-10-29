from src.preprocessing.text_cleaner import TextCleaner
from src.preprocessing.skill_extractor import SkillExtractor

def test_text_cleaner_removes_noise():
    cleaner = TextCleaner(stopwords={"and"})
    text = "Email me at test@example.com and visit https://example.com!"
    cleaned = cleaner.clean(text)
    assert "testexamplecom" not in cleaned
    assert "https" not in cleaned
    assert "visit" in cleaned

def test_skill_extractor_matches_multiple_occurrences():
    extractor = SkillExtractor(skills=["python", "docker"])
    matches = extractor.extract("Python developer with Docker and python scripting experience")
    skills = {m.skill.lower(): m.occurrences for m in matches}
    assert skills["python"] == 2
    assert skills["docker"] == 1
