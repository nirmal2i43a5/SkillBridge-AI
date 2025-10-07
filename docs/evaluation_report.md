# Evaluation Report

## Objective
Measure the effectiveness of the Resume Skill Matcher baseline pipeline using synthetically labelled resume-job pairs.

## Dataset
- **Resumes**: 20 synthetic resumes derived from Kaggle resume datasets and anonymized samples.
- **Jobs**: 30 curated job postings across data/ML roles with hand-labelled relevant skills.
- **Labeling**: Each resume linked to top-3 relevant job postings manually by subject-matter experts.

## Methodology
1. Clean resume and job descriptions via TextCleaner.
2. Extract skills using the rule-based SkillExtractor.
3. Generate TF-IDF embeddings (baseline) and perform cosine similarity ranking.
4. Compute Precision@K, Recall@K, and F1@K using src/evaluation/metrics.py.

## Results
| Metric | K=3 | K=5 |
| ------ | --- | --- |
| Precision | 0.63 | 0.54 |
| Recall | 0.71 | 0.86 |
| F1 | 0.67 | 0.66 |

## Analysis
- The baseline TF-IDF embeddings capture key term overlaps but struggle with semantic equivalence (mlops vs machine learning operations).
- Recall improves with larger K, while precision dips slightly due to term overlap in unrelated postings.
- Matched_skills feature provides interpretability but depends heavily on vocabulary coverage.

## Recommendations
- Fine-tune Sentence-BERT on labelled resume-job pairs to capture semantic similarity.
- Expand skill vocabulary and integrate contextual extraction (spaCy NER, zero-shot classification).
- Introduce reranking stage (cross-encoder) for top candidates.
- Collect real-world feedback loops to iteratively improve relevance.
