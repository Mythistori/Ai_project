SYSTEM_PROMPT = "You are an expert AI recruitment assistant. Always respond with valid JSON only. No markdown, no backticks, no extra text."


def analyze_prompt(cv_text: str, jd_text: str) -> str:
    return f"""Analyze this CV against the job description.

CV:
{cv_text}

Job Description:
{jd_text}

Return ONLY this JSON (no markdown, no backticks):
{{
  "candidate_name": "Full name from CV",
  "score": 85,
  "verdict": "hire",
  "score_breakdown": {{
  "skills_match": 40,
  "experience_match": 25,
  "education_match": 15,
  "job_fit": 20
}},
  "matching_skills": ["Python", "SQL"],
  "missing_skills": ["Docker"],
  "experience_years": "3 years",
  "education": "BSc Computer Science, SDU",
  "strengths": "Strong backend skills with proven experience.",
  "weaknesses": "Lacks cloud experience.",
  "hr_summary": "Strong junior candidate with Python background.",
  "questions": [
    {{"type": "technical", "text": "Explain your experience with Python?"}},
    {{"type": "technical", "text": "How do you handle database optimization?"}},
    {{"type": "behavioral", "text": "Tell me about a challenging project?"}},
    {{"type": "behavioral", "text": "How do you handle tight deadlines?"}},
    {{"type": "situational", "text": "What would you do if requirements changed mid-sprint?"}}
  ]
}}

Rules:
- score: integer 0-100
- verdict: one of exactly "hire", "maybe", "reject"
"""


def compare_prompt(cv1_text: str, cv2_text: str, jd_text: str) -> str:
    return f"""Compare these two candidates for this job. 

CANDIDATE 1 CV:
{cv1_text}

CANDIDATE 2 CV:
{cv2_text}

Job Description:
{jd_text}

Return ONLY this exact JSON structure (no markdown, no backticks, no extra text):
{{
  "winner": 1,
  "winner_reason": "Candidate 1 has stronger Python skills and more relevant experience.",
  "candidate1": {{
    "name": "Full name of candidate 1",
    "score": 82,
    "verdict": "hire",
    "hr_summary": "Strong backend developer with 3 years experience."
  }},
  "candidate2": {{
    "name": "Full name of candidate 2",
    "score": 65,
    "verdict": "maybe",
    "hr_summary": "Junior developer with limited experience."
  }},
  "comparison": {{
    "skills_edge": 1,
    "experience_edge": 1,
    "education_edge": 2,
    "overall_fit_edge": 1
  }}
}}

Rules:
- winner: must be integer 1 or 2
- score: integer 0-100
- verdict: one of exactly "hire", "maybe", "reject"
- All fields above are REQUIRED
- score_breakdown values must add up to 100
- skills_match, experience_match, education_match, job_fit must be integers
"""