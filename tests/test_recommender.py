from src.features.embedding_generator import EmbeddingGenerator
from src.recommender.recommender import JobPosting, ResumeRecommender

def test_recommender_returns_ranked_jobs():
    jobs = [
        JobPosting(job_id="1", title="ML Engineer", description="python sklearn aws"),
        JobPosting(job_id="2", title="Frontend Developer", description="react javascript css"),
    ]
    recommender = ResumeRecommender(embedding_generator=EmbeddingGenerator(prefer_tfidf=True))
    recommender.index_jobs(jobs)
    recs = recommender.recommend_for_resume_text("Experienced with Python, AWS, and ML pipelines", top_k=1)
    assert recs[0].job.job_id == "1"
    assert "python" in recs[0].matched_skills or "aws" in recs[0].matched_skills
