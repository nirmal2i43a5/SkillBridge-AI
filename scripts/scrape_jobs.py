
"""Fetch RemoteOK job listings into JSON."""
import argparse
from pathlib import Path


# run once, near the top of your notebook
import sys
repo_root = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd().parents[1]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))
    
from src.data_collection.remoteok_api import fetch_to_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch RemoteOK job postings")
    parser.add_argument(
        "--keyword",
        help="Case-insensitive keyword filter applied to title and description",
    )
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        help="Filter by tag (repeatable). Example: --tag python",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/jobs.json"),
        help="Destination JSON file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = fetch_to_json(
        keyword=args.keyword,
        tags=args.tags,
        output_path=args.output,
    )
    print(f"Stored {count} job postings into {args.output}")


if __name__ == "__main__":
    main()
