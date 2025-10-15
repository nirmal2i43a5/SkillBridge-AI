#!/usr/bin/env python
"""CLI helper to fetch job postings from the Adzuna API."""
import argparse
from pathlib import Path
import sys

# Add project root to the Python path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.data_collection.adzuna_client import fetch_all_data_jobs

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Adzuna Job Posting Scraper")
    parser.add_argument(
        "--pages", type=int, default=5, help="Number of pages to fetch per role."
    )
    parser.add_argument(
        "--location", type=str, default="Canada", help="Geographic location for job search."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "data" / "processed" / "adzuna_data_jobs.json",
        help="Path to save the output JSON file.",
    )
    return parser.parse_args()


def main() -> None:
    """Main function to run the scraper."""
    args = parse_args()
    print(f"Starting Adzuna job fetcher...")
    print(f" - Location: {args.location}")
    print(f" - Pages per role: {args.pages}")
    print(f" - Output file: {args.output}")

    # Define common stopwords to improve text cleaning
    stopwords = ["the", "a", "an", "and", "or", "in", "on", "for", "to"]
    
    fetch_all_data_jobs(
        pages_per_role=args.pages,
        location=args.location,
        output_path=str(args.output),
        stopwords=stopwords,
    )
    print("Job fetching complete.")


if __name__ == "__main__":
    main()
