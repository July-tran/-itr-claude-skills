---
name: assess-candidate
description: IAT — Interview Assessment Tool. Screens candidate CVs against a Job Description, levelling framework, and interviewer persona. Use this skill whenever the user wants to assess or screen a candidate, generate interview questions, score a CV against a JD, identify strengths/weaknesses/risk signals, or produce a candidate assessment report. Trigger on /assess, /screen, /iat, "assess this CV", "screen the candidate", "interview prep for [name]", "analyze [name]'s CV", "generate interview questions for", or any mention of CV screening or candidate evaluation.
---

# IAT — Interview Assessment Tool

Perform a rigorous, evidence-based candidate assessment. Work through each phase in order.

---

## Phase 0 — Check the Tracking Log

Before doing any work, capture the project directory and run:

```bash
PROJECT_DIR=$(pwd)
python "{{SKILL_DIR}}/scripts/track.py" --base-dir "$PROJECT_DIR" --show
```

This prints `output/tracking.json` as a table showing every CV previously processed:
- File name, candidate name, date assessed, score, match level, recommendation, output file

Use this to:
- **Skip already-processed CVs** — tell the user which ones are done and ask if they want to re-run
- **Detect new CVs** — only process files not yet in the log
- If the user explicitly says "re-assess" or "re-run", process regardless of history

If `tracking.json` doesn't exist yet, proceed normally (first run).

---

## Phase 1 — Extract All Inputs

Run the extraction script, passing the project directory explicitly:

```bash
python "{{SKILL_DIR}}/scripts/extract_inputs.py" --base-dir "$PROJECT_DIR"
```

**How asset caching works:**
- JD, levelling, and persona files are extracted once and cached as **Markdown** in `assets/`
  (`assets/jd.md`, `assets/levelling.md`, `assets/persona.md`)
- On subsequent runs the cached files are read directly — no DOCX/XLSX parsing needed
- Cache is automatically invalidated when the source file changes (mtime + size check)
- CVs are always extracted fresh since they change with each batch
- Force a full refresh anytime: `python extract_inputs.py --force-refresh`

The script returns JSON with:
- `cv_files`: list of `{file_name, text}` — all CVs found
- `jd_text`, `levelling_text`, `persona_text` — from cache or freshly extracted
- `assets_refreshed`: which assets were re-extracted this run
- `errors`: any files that couldn't be found or read

If `assets/*.txt` files already exist, you can also read them directly with the Read tool
instead of running the script — they are plain text and human-readable.

If the script errors entirely, fall back to reading `assets/*.txt` directly.

---

## Phase 2 — Analyze Each Candidate

For each CV, complete all steps below before moving to the next candidate.

### 2a. Parse the Candidate Profile

From CV text, extract:
- Name, email, phone, location
- All skills (every technology, framework, tool mentioned anywhere)
- Work experience: title, company, duration, key achievements (with metrics)
- Projects: name, technologies, measurable impact
- Education, certifications
- **Total years of professional experience** (calculate from date ranges)
- **AI/LLM-specific years** (GenAI, LLMs, agents, RAG work specifically)

### 2b. Parse JD Requirements

From JD text, extract:
- Role title
- Required skills (must-have) vs preferred skills (nice-to-have)
- Minimum years of experience
- Core tech stack
- Key responsibilities and domain

### 2c. Level Mapping

Using the levelling framework:
- Determine what level the JD targets
- Map the candidate to their actual level based on years + skills
- State the level fit: **Under-qualified** | **Good Match** | **Over-qualified**
- List specific gaps vs expected level (precise, not generic)
- List where candidate meets or exceeds expectations

### 2d. Strengths, Weaknesses, Risk Signals

**Strengths** — only with specific evidence:
> `[Strength] — Evidence: [specific project/metric from CV]`

**Weaknesses** — with concrete impact:
> `[Gap] — Impact: [why this matters for the role]`

**Risk Signals** — be rigorous. Flag:
- Skills listed but never demonstrated in any project or job
- Impact metrics that seem implausibly high without context
- Very short tenures (< 6 months) at multiple companies
- AI/LLM experience that appears academic/tutorial rather than production
- Vague "led" or "architected" claims without specifics
- Achievements that contradict the candidate's level or timeline

Rate each: **High** | **Medium** | **Low**

### 2e. Score (100 points)

| Component | Max | Method |
|---|---|---|
| Skill match | 30 | Required coverage × 21 pts + Preferred coverage × 9 pts |
| Experience | 25 | General years vs requirement (15 pts) + AI years (10 pts) |
| Tech stack | 20 | Fraction of JD tech stack present in candidate skills |
| Level fit | 15 | How well candidate maps to the expected level |
| Project relevance | 10 | Relevant projects with measurable impact |

Risk penalties: −3 per High-severity risk, −1 per Medium.

Show the breakdown explicitly. Derive:
- **Match level**: Strong (≥80) / Moderate (≥60) / Weak (<60)
- **Recommendation**: Strongly Recommend (≥85) / Recommend (≥70) / Proceed with Caution (≥55) / Do Not Proceed (<55)

### 2f. Interview Questions (20 minimum) — Moderate and Strong matches only

**Only generate interview questions if the candidate's match level is Moderate (≥60) or Strong (≥80).**

For Weak match candidates (<60), set `"questions": []` in the JSON and skip this step entirely. There is no value in preparing interview questions for candidates who will not be progressed.

When generating questions, tailor to the interviewer's persona from the persona file. General principles:
- Ask about *implementation*, not concepts — "walk me through exactly how you built X"
- For every claimed metric: "walk me through how you measured that"
- Include 2–3 questions where the honest answer is "I don't know" or "I haven't done that" — designed to reward honesty over bluffing
- If the persona uses STAR methodology, frame project/experience questions as "Tell me about a time when…"

Categories (distribute across all):
- `skill_validation` — genuine understanding vs keyword-dropping
- `deep_probe` — implementation details of claimed expertise
- `project_verification` — verify specific CV claims
- `risk_investigation` — probe red flags directly
- `scenario_based` — realistic problem, assess reasoning
- `behavioral` — soft skills, decision-making

For each question include:
- **Category**
- **Rationale** — why this question for this specific candidate
- **1–2 follow-ups** to go deeper

---

## Phase 3 — Write Excel Output

First, write `assessment_data.json` to the working directory with this structure:

```json
{
  "candidate": {
    "name": "", "email": "", "phone": "", "location": "",
    "skills": [], "total_years": 0.0, "ai_years": 0.0, "file_name": ""
  },
  "jd": {
    "role_title": "", "required_skills": [], "preferred_skills": [], "tech_stack": []
  },
  "level": {
    "candidate_level": 2, "candidate_level_title": "Middle",
    "expected_level": 2, "expected_level_title": "Middle",
    "level_fit": "Good Match", "gaps": [], "strengths_vs_level": []
  },
  "analysis": {
    "strengths": [{"point": "", "evidence": ""}],
    "weaknesses": [{"point": "", "impact": ""}],
    "risk_signals": [{"signal": "", "explanation": "", "severity": "Medium"}],
    "matching_skills": [], "missing_skills": [], "overall_assessment": ""
  },
  "score": {
    "total_score": 0.0, "match_level": "Moderate", "recommendation": "",
    "breakdown": {
      "skill_match": 0, "experience_relevance": 0, "tech_stack_alignment": 0,
      "level_fit": 0, "project_relevance": 0
    }
  },
  "questions": [
    {"question": "", "category": "skill_validation", "persona_tags": [], "rationale": "", "follow_ups": []}
  ],
  "persona_insights": {}
}
```

Then run:
```bash
python "{{SKILL_DIR}}/scripts/write_excel.py" --base-dir "$PROJECT_DIR"
```

The script reads `assessment_data.json` from `$PROJECT_DIR` and writes:
- `output/assessment_<CandidateName>.xlsx`
- `output/assessment_<CandidateName>.json`
- Updates `output/tracking.json` with this candidate's result

After writing the individual file, always regenerate the summary:

```bash
python "{{SKILL_DIR}}/scripts/write_summary.py" --base-dir "$PROJECT_DIR"
```

This reads **all** `output/assessment_*.json` files and overwrites `output/candidates_summary.xlsx` with 4 sheets:
- **1 - Ranking Overview** — all candidates ranked by score with colour-coded match level
- **2 - Score Breakdown** — component scores side-by-side (skill match, experience, tech stack, level fit, project)
- **3 - Strengths & Concerns** — top 3 strengths + concerns + risk signals per candidate
- **4 - Skills Comparison** — matrix of ✓/✗ for every skill across all candidates

---

## Phase 4 — Present Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CANDIDATE: [Name]   ROLE: [Role Title]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SCORE: XX/100 ([Match Level])
 → [Recommendation]

 LEVEL: [Candidate Level] vs Expected [Expected Level] — [Fit]

 STRENGTHS
  • [Point] — [Evidence]
  • ...

 CONCERNS
  • [Weakness or Risk]
  • ...

 OUTPUT → output/assessment_[Name].xlsx
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then ask: "Want me to drill deeper on any skill area, adjust question difficulty, or re-run with a different persona focus?"
