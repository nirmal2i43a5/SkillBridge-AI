import json
import os
from pathlib import Path
from typing import List
import hashlib

import requests
import streamlit as st

API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Resume Skill Matcher", layout="wide")

# --- CUSTOM CSS ---
css_path = Path(__file__).parent / "static" / "style.css"

with open(css_path, "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.markdown("""
<div class="main-header">
    <h1>Resume Skill Matcher</h1>
    <p>Upload your resume and find your perfect job match with AI-powered analysis</p>
</div>
""", unsafe_allow_html=True)


# # --- SIDEBAR ---
# with st.sidebar:
#     st.markdown("### Settings")
    
#     st.markdown("#### Job Indexing")
#     load_adzuna_jobs = st.checkbox("Load jobs API", value=True)
    
#     st.markdown("#### Recommendation")
#     top_k = st.slider("Number of Recommendations", min_value=1, max_value=10, value=5)
    
#     st.markdown("---")
    
#     ADZUNA_JOBS_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "adzuna_data_jobs.json"

#     if load_adzuna_jobs:
#         if st.button("Index Adzuna Jobs"):
#             if not ADZUNA_JOBS_PATH.exists():
#                 st.error(f"Error: {ADZUNA_JOBS_PATH.name} not found.")
#                 st.info("Please run the data collection script first.")
#             else:
#                 with st.spinner("Indexing jobs..."):
#                     try:
#                         with open(ADZUNA_JOBS_PATH, "r", encoding="utf-8") as f:
#                             jobs = json.load(f)

#                         payload = {"jobs": []}
#                         for job in jobs:
#                             unique_str = job.get("job_url") or f"{job.get('job_title', '')}_{job.get('company', '')}_{job.get('location', '')}"
#                             job_id = hashlib.md5(unique_str.encode()).hexdigest()
                            
#                             payload["jobs"].append({
#                                 "job_id": job_id,
#                                 "title": job.get("job_title"),
#                                 "description": job.get("job_description"),
#                                 "company": job.get("company"),
#                                 "location": job.get("location"),
#                                 "url": job.get("job_url"),
#                                 "posted_date": job.get("posted_date"),
#                                 "category": job.get("category"),
#                                 "job_type": job.get("job_type"),
#                                 "experience_level": job.get("experience_level"),
#                                 "role_type": job.get("role_type"),
#                                 "skills": job.get("skills", []),
#                                 "tags": job.get("tags", []),
#                             })
                        
#                         resp_persist = requests.post(f"{API_URL}/jobs/index/persist", json=payload, timeout=100)
#                         if not resp_persist.ok:
#                             st.error(f"Backend error (persist): {resp_persist.text}")
#                         else:
#                             resp_index = requests.post(f"{API_URL}/jobs/index", json=payload, timeout=100)
#                             if resp_index.ok:
#                                 st.success(f"Indexed {resp_index.json().get('indexed')} jobs successfully!")
#                             else:
#                                 st.warning(f"Jobs saved, but indexing failed: {resp_index.text}")
#                     except requests.exceptions.ConnectionError as e:
#                         st.error(f"Cannot connect to backend at {API_URL}.")
#                     except Exception as e:
#                         st.error(f"Error processing jobs: {e}")



# Resume Upload Section
st.markdown('<div class="card-container">', unsafe_allow_html=True)
st.markdown("### Upload Resume")
col1, col2 = st.columns([1, 1])

with col1:
    uploaded = st.file_uploader("Upload PDF Resume", type=["pdf"])

with col2:
    text_input = st.text_area("Or paste resume text", height=150, placeholder="Paste your resume content here...")

analyze_btn = st.button("Find Matching Jobs")
st.markdown('</div>', unsafe_allow_html=True)


# Results Section
if analyze_btn:
    resp = None
    with st.spinner("Analyzing resume and matching jobs..."):
        try:
            if uploaded is not None:
                files = {"upload": (uploaded.name, uploaded.read(), "application/pdf")}
                resp = requests.post(
                    f"{API_URL}/recommend/file",
                    files=files,
                    data={"top_k": 10},
                    timeout=60,
                )
            elif text_input.strip():
                payload = {"resume_text": text_input, "top_k": 10}
                resp = requests.post(f"{API_URL}/recommend/text", json=payload, timeout=30)
            else:
                st.warning("Please upload a PDF or paste resume text.")
        except requests.exceptions.ConnectionError:
            st.error(f"Cannot connect to backend at {API_URL}. Is it running?")

    if resp is not None:
        if resp.ok:
            results: List[dict] = resp.json().get("recommendations", [])
            
            if not results:
                st.info("No recommendations found.")
            else:
                st.markdown(f"### Top {len(results)} Recommendations")
                
                for rec in results:
                    # Job Card
                    st.markdown(f"""
                    <div class="card-container" style="padding: 1.5rem; margin-bottom: 1rem;">
                        <div class="job-card-header">
                            <div>
                                <h3 class="job-title">{rec.get('title')}</h3>
                                <div class="job-company">{rec.get('company') or 'Company Confidential'}</div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.5rem; font-weight: 700; color: #2563EB;">{rec.get('score', 0):.0%}</span>
                                <br><span style="font-size: 0.8rem; color: #6B7280;">MATCH SCORE</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Metrics Grid
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">Location</div>
                            <div class="metric-value" style="font-size: 0.9rem;">{rec.get('location') or 'Remote'}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">Experience</div>
                            <div class="metric-value" style="font-size: 0.9rem;">{rec.get('experience_level') or 'N/A'}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">Type</div>
                            <div class="metric-value" style="font-size: 0.9rem;">{rec.get('job_type') or 'Full-time'}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c4:
                         st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">Role</div>
                            <div class="metric-value" style="font-size: 0.9rem;">{rec.get('role_type') or 'N/A'}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Skills
                    matched_skills = rec.get('matched_skills', [])
                    all_skills = rec.get('skills', [])
                    
                    if matched_skills:
                        st.markdown("**Matched Skills**")
                        skills_html = "".join([f'<span class="chip chip-blue">{skill}</span>' for skill in matched_skills])
                        st.markdown(f"<div>{skills_html}</div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

                    if all_skills:
                        st.markdown("**All Job Skills**")
                        # Filter out matched skills to avoid duplicates in display if desired, or show all
                        remaining_skills = [s for s in all_skills if s not in matched_skills]
                        skills_html = "".join([f'<span class="chip chip-green">{skill}</span>' for skill in remaining_skills])
                        st.markdown(f"<div>{skills_html}</div>", unsafe_allow_html=True)

                    # Action Button
                    if rec.get('url'):
                        st.markdown(f"""
                        <div style="margin-top: 1.5rem; text-align: right;">
                            <a href="{rec['url']}" target="_blank" style="background-color: #1E3A8A; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; font-size: 0.9rem;">View Job Posting</a>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True) # End Card

        else:
            st.error(f"Backend error: {resp.text}")
