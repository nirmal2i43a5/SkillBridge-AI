import argparse
import json
from pathlib import Path

from src.embeddings.text_embedder import TextEmbedder
from src.recommender.recommender import JobPosting, ResumeRecommender


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resume -> Job recommendation pipeline")
    parser.add_argument("resume", type=Path, help="Path to resume text file")
    parser.add_argument("jobs", type=Path, help="Path to JSON job postings (list of dicts)")
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    resume_text = args.resume.read_text(encoding="utf-8")
    job_payload = json.loads(args.jobs.read_text(encoding="utf-8"))
    jobs = [JobPosting(**entry) for entry in job_payload["jobs"]]

    recommender = ResumeRecommender(embedding_generator=TextEmbedder())
    recommender.index_jobs(jobs)
    recommendations = recommender.recommend_for_resume_text(resume_text, top_k=args.top_k)

    for rank, rec in enumerate(recommendations, start=1):
        matched = ", ".join(rec.matched_skills) or "-"
        print(f"{rank}. {rec.job.title} ({rec.job.company or 'Company N/A'}) | score={rec.score:.3f} | skills={matched}")


if __name__ == "__main__":
    main()
