# ITR Claude Skills

Shared Claude Code skills for the ITR VN team.

---

## Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `assess-candidate` | `/assess`, `/screen`, `/iat` | Interview Assessment Tool — screens CVs against a JD, scores candidates, generates interview questions, and produces Excel reports |

---

## Installation

### Prerequisites

1. **Claude Code** installed (`npm install -g @anthropic-ai/claude-code`)
2. **Python 3.8+** with these packages:
   ```
   pip install pdfplumber python-docx openpyxl
   ```

### Install a skill

**One-time setup — copy the skill to your Claude skills folder:**

**Windows:**
```powershell
# Clone this repo
git clone https://github.com/July-tran/-itr-claude-skills.git

# Copy the skill
xcopy /E /I itr-claude-skills\assess-candidate "%USERPROFILE%\.claude\skills\assess-candidate"
```

**Mac/Linux:**
```bash
git clone https://github.com/July-tran/-itr-claude-skills.git
cp -r itr-claude-skills/assess-candidate ~/.claude/skills/
```

Then **restart Claude Code** — the skill is ready.

### Update to the latest version

```bash
cd itr-claude-skills
git pull

# Windows
xcopy /E /I /Y assess-candidate "%USERPROFILE%\.claude\skills\assess-candidate"

# Mac/Linux
cp -r assess-candidate ~/.claude/skills/
```

---

## Using `assess-candidate` (IAT)

### Project structure required

```
your-project/
├── CV/                              ← drop candidate CVs here (.pdf or .docx)
├── JD.docx                          ← job description
├── Levelling.xlsx                   ← levelling framework
├── Persona.docx                     ← interviewer persona
├── HM_Candidate_Clarification.docx  ← HM clarification (optional but recommended)
└── output/                          ← generated automatically
    ├── assessment_<Name>.xlsx
    ├── assessment_<Name>.json
    ├── candidates_summary.xlsx
    └── tracking.json
```

> **HM Clarification file** — When present, this document overrides the JD on what is truly must-have vs. nice-to-have. It also defines deal-breakers that automatically disqualify a candidate regardless of score. Always include it for more accurate analytics. The file is auto-detected by any filename containing `HM` or `CLARIF` (e.g. `HM_Candidate_Clarification_AAD.docx`).

### How to run

1. Open Claude Code in your project folder
2. Drop CV files into the `CV/` folder
3. Say one of:
   - `/assess`
   - `assess this CV`
   - `screen the candidates`
   - `generate interview questions for [Name]`

Claude will process each CV, score it, and write Excel reports to `output/`.

### Scoring (100 points)

| Component | Max | Notes |
|-----------|-----|-------|
| Skill match | 30 | Required × 21 pts + Preferred × 9 pts |
| Experience relevance | 25 | General years (15) + AI/LLM years (10) |
| Tech stack alignment | 20 | JD tech stack coverage |
| Level fit | 15 | Candidate level vs expected level |
| Project relevance | 10 | Relevant projects with measurable impact |

Risk penalties: −3 per High-severity signal, −1 per Medium.

**Match levels:** Strong (≥80) · Moderate (≥60) · Weak (<60)
**Recommendations:** Strongly Recommend (≥85) · Recommend (≥70) · Proceed with Caution (≥55) · Do Not Proceed (<55)

---

## Questions?

Contact: Thach Tran / HR Team, ITR VN
