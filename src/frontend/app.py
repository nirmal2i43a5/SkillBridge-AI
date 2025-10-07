import json
import os
from pathlib import Path
from typing import List

import requests
import streamlit as st

# Backend API URL (local by default, can override with env var)
API_URL = os.getenv("SKILLMATCH_API_URL", "http://localhost:8000")

# ------------------------------
# Streamlit Page Setup
# ------------------------------
st.set_page_config(page_title="Resume Skill Matcher", layout="wide")
st.title("Resume Skill Matcher")

st.write("Upload a resume and discover matching job postings.")

# ------------------------------
# Sidebar: Job Indexing
# ------------------------------
with st.sidebar:
    st.header("Job Indexing")
    example_jobs = st.checkbox("Load RemoteOK jobs", value=True)
    top_k = st.slider("Top K", min_value=1, max_value=10, value=5)

if example_jobs and st.sidebar.button("Index RemoteOK jobs"):
    try:
        resp_api = requests.get("https://remoteok.io/api", headers={"User-Agent": "Mozilla/5.0"})
        if resp_api.ok:
            jobs = resp_api.json()[1:]  # first element is metadata

            payload = {"jobs": []}
            for job in jobs:
                payload["jobs"].append({
                    "job_id": str(job.get("id")),
                    "title": job.get("position"),
                    "description": job.get("description"),
                    "company": job.get("company"),
                    "location": job.get("location"),
                })

            resp = requests.post(f"{API_URL}/jobs/index", json=payload, timeout=30)
            if resp.ok:
                st.success(f"Indexed {resp.json().get('indexed')} jobs from RemoteOK")
            else:
                st.error(f"Backend error: {resp.text}")
        else:
            st.error(f"RemoteOK API failed with status {resp_api.status_code}")
    except Exception as e:
        st.error(f"Error fetching RemoteOK jobs: {e}")

# ------------------------------
# Main: Resume Input
# ------------------------------
uploaded = st.file_uploader("Resume (PDF)", type=["pdf"])
text_input = st.text_area("Or paste resume text", height=200)

# ------------------------------
# Main: Get Recommendations
# ------------------------------
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
                    st.subheader(f"{rec['title']} ({rec.get('company') or 'Company N/A'})")
                    st.write(f"📊 Match score: {rec['score']:.3f}")
                    st.write(f"✅ Matched skills: {', '.join(rec['matched_skills']) or 'n/a'}")
        else:
            st.error(f"Backend error: {resp.text}")
