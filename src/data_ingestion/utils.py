from collections import Counter

def print_statistics(jobs):
    """Prints summary like number of jobs, top skills, etc."""
    if not jobs:
        print("No jobs found.")
        return

    skills = [s for j in jobs for s in j.skills]
    tags = [t for j in jobs for t in j.tags]

    print("\n==== Job Summary ====")
    print(f"Total jobs: {len(jobs)}")
    print(f"Unique skills: {len(set(skills))}")
    print(f"Unique tags: {len(set(tags))}")

    print("\nTop 10 Skills:")
    for skill, count in Counter(skills).most_common(10):
        print(f"  {skill}: {count}")

    print("\nTop 10 Tags:")
    for tag, count in Counter(tags).most_common(10):
        print(f"  {tag}: {count}")
