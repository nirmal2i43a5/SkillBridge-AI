import json
import os
import re
import hashlib
from pathlib import Path
from typing import List

import requests
import streamlit as st

# Backend API URL (local by default, can override with env var)
API_URL = os.getenv("SKILLMATCH_API_URL", "http://127.0.0.1:8000")


# Streamlit Page Setup
st.set_page_config(page_title="Resume Skill Matcher", layout="wide")
st.title("Resume Skill Matcher")

st.write("Upload a resume and discover matching job postings.")

# Sidebar: Job Indexing
with st.sidebar:
    st.header("Job Indexing")
    load_adzuna_jobs = st.checkbox("Load Adzuna jobs", value=True)
    top_k = st.slider("Top K", min_value=1, max_value=10, value=5)


ADZUNA_JOBS_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "adzuna_data_jobs.json"

if load_adzuna_jobs and st.sidebar.button("Index Adzuna Jobs"):
    if not ADZUNA_JOBS_PATH.exists():
        st.error(f"Error: {ADZUNA_JOBS_PATH.name} not found.")
        st.info("Please run the data collection script first.")
    else:
        try:
            with open(ADZUNA_JOBS_PATH, "r", encoding="utf-8") as f:
                jobs = json.load(f)

            payload = {"jobs": []}
            for job in jobs:
                # Map all new AdzunaJob fields to the payload
                job_id = str(job.get("id"))
                # Fix for missing IDs in Adzuna data
                if not job_id or job_id == "None":
                    url = job.get("job_url", "")
                    # Try to extract ID from URL (e.g. details/5429625850)
                    match = re.search(r'(?:details|ad)/(\d+)', url)
                    if match:
                        job_id = match.group(1)
                    else:
                        # Fallback: deterministic hash
                        unique_str = f"{job.get('job_title')}{job.get('company')}"
                        job_id = hashlib.md5(unique_str.encode()).hexdigest()

                payload["jobs"].append({
                    "job_id": job_id,
                    "title": job.get("job_title"),
                    "description": job.get("job_description"),
                    "company": job.get("company"),
                    "location": job.get("location"),
                    "url": job.get("job_url"),
                    "posted_date": job.get("posted_date"),
                    "category": job.get("category"),
                    "job_type": job.get("job_type"),
                    "experience_level": job.get("experience_level"),
                    "role_type": job.get("role_type"),
                    "skills": job.get("skills", []),
                    "tags": job.get("tags", []),
                    "min_years_experience": job.get("min_years_experience", 0.0),
                })

            resp = requests.post(f"{API_URL}/jobs/index", json=payload, timeout=100)
            if resp.ok:
                st.success(f"Indexed {resp.json().get('indexed')} jobs from {ADZUNA_JOBS_PATH.name}")
            else:
                st.error(f"Backend error: {resp.text}")
        except Exception as e:
            st.error(f"Error processing Adzuna jobs file: {e}")


# Resume Input
uploaded = st.file_uploader("Resume (PDF)", type=["pdf"])
text_input = st.text_area("Or paste resume text", height=200)


#  Get Recommendations

if st.button("Get recommendations"):
    resp = None
    if uploaded is not None:
        files = {"upload": (uploaded.name, uploaded.read(), "application/pdf")}
        resp = requests.post(
            f"{API_URL}/recommend/file",
            files=files,
            data={"top_k": top_k},
            timeout=60,
        )
    elif text_input.strip():
        payload = {"resume_text": text_input, "top_k": top_k}
        resp = requests.post(f"{API_URL}/recommend/text", json=payload, timeout=30)
    else:
        st.warning("Please upload a PDF or paste resume text.")

    if resp is not None:
        if resp.ok:
            results: List[dict] = resp.json().get("recommendations", [])
            if not results:
                st.info("No recommendations found.")
            else:
                for rec in results:
                    st.subheader(f"{rec.get('title')} at {rec.get('company') or 'N/A'}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Match Score", f"{rec.get('score', 0):.2%}")
                    with col2:
                        st.metric("Experience Level", rec.get('experience_level') or 'N/A')
                    with col3:
                        st.metric("Job Type", rec.get('job_type') or 'N/A')

                    st.write(f"**Location:** {rec.get('location') or 'N/A'}")
                    st.write(f"**Role:** {rec.get('role_type') or 'N/A'}")

                    with st.expander("Matched Skills"):
                        st.info(f"{', '.join(rec.get('matched_skills', [])) or 'None'}")
                    
                    with st.expander("All Job Skills"):
                        st.success(f"{', '.join(rec.get('skills', [])) or 'None'}")
                        
                    if rec.get('url'):
                        st.link_button("View Job Posting", rec['url'])
                    
                    st.divider()
        else:
            st.error(f"Backend error: {resp.text}")
