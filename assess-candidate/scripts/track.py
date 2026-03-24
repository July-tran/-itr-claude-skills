"""
track.py — Manages output/tracking.json for the IAT assess-candidate skill.

Usage:
  python track.py --show                        # print current log as a table
  python track.py --add assessment_data.json    # append/update a processed entry
  python track.py --processed <cv_file_name>    # exit 0 if already done, 1 if not
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def _resolve_base_dir() -> Path:
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--base-dir" and i < len(sys.argv):
            return Path(sys.argv[i + 1]).resolve()
        if arg.startswith("--base-dir="):
            return Path(arg.split("=", 1)[1]).resolve()
    return Path.cwd()

TRACKING_FILE = _resolve_base_dir() / "output" / "tracking.json"


# ── Read / write ───────────────────────────────────────────────────────────────

def load() -> list[dict]:
    if TRACKING_FILE.exists():
        try:
            return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save(records: list[dict]):
    TRACKING_FILE.parent.mkdir(exist_ok=True)
    TRACKING_FILE.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ── Commands ───────────────────────────────────────────────────────────────────

def cmd_show():
    records = load()
    if not records:
        print("No candidates assessed yet.")
        return

    # Column widths
    W = {"cv": 30, "name": 22, "date": 12, "score": 7, "match": 10, "rec": 28, "file": 40}
    sep = "-" * (sum(W.values()) + len(W) * 3)
    hdr = (
        f"{'CV File':<{W['cv']}}  "
        f"{'Candidate':<{W['name']}}  "
        f"{'Date':<{W['date']}}  "
        f"{'Score':>{W['score']}}  "
        f"{'Match':<{W['match']}}  "
        f"{'Recommendation':<{W['rec']}}  "
        f"{'Output File':<{W['file']}}"
    )

    print(f"\n{'IAT — Processed Candidates':^{len(sep)}}")
    print(sep)
    print(hdr)
    print(sep)

    for r in records:
        score_str = f"{r.get('score', 0):.1f}/100"
        print(
            f"{r.get('cv_file',''):<{W['cv']}.{W['cv']}}  "
            f"{r.get('candidate_name',''):<{W['name']}.{W['name']}}  "
            f"{r.get('assessed_at','')[:10]:<{W['date']}}  "
            f"{score_str:>{W['score']}}  "
            f"{r.get('match_level',''):<{W['match']}.{W['match']}}  "
            f"{r.get('recommendation',''):<{W['rec']}.{W['rec']}}  "
            f"{r.get('output_file',''):<{W['file']}.{W['file']}}"
        )

    print(sep)
    print(f"  Total: {len(records)} candidate(s) assessed.\n")


def cmd_add(data_file: str):
    path = Path(data_file)
    if not path.exists():
        print(f"ERROR: {data_file} not found", file=sys.stderr)
        sys.exit(1)

    d = json.loads(path.read_text(encoding="utf-8"))
    cand   = d.get("candidate", {})
    score  = d.get("score", {})
    name   = cand.get("name", "Unknown")
    cv_file = cand.get("file_name", "")

    # Build output file path (use same base dir as TRACKING_FILE)
    safe_name  = name.replace(" ", "_")
    output_file = str(TRACKING_FILE.parent / f"assessment_{safe_name}.xlsx")

    record = {
        "cv_file":        cv_file,
        "candidate_name": name,
        "assessed_at":    datetime.now().isoformat(timespec="seconds"),
        "score":          score.get("total_score", 0),
        "match_level":    score.get("match_level", ""),
        "recommendation": score.get("recommendation", ""),
        "output_file":    output_file,
        "role":           d.get("jd", {}).get("role_title", ""),
        "level_fit":      d.get("level", {}).get("level_fit", ""),
    }

    records = load()

    # Update existing entry if same CV file was re-run
    existing = next((i for i, r in enumerate(records) if r.get("cv_file") == cv_file), None)
    if existing is not None:
        records[existing] = record
        print(f"Updated tracking entry for: {name} ({cv_file})")
    else:
        records.append(record)
        print(f"Added tracking entry for: {name} ({cv_file})")

    save(records)


def cmd_processed(cv_file: str) -> bool:
    """Return True (exit 0) if already in log, False (exit 1) if not."""
    records = load()
    found = any(r.get("cv_file") == cv_file for r in records)
    if found:
        match = next(r for r in records if r.get("cv_file") == cv_file)
        print(
            f"ALREADY PROCESSED: {match['candidate_name']} — "
            f"{match['score']:.1f}/100 ({match['match_level']}) "
            f"on {match['assessed_at'][:10]}"
        )
    return found


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="IAT tracking log manager")
    parser.add_argument("--base-dir", metavar="PATH",
                        help="Project root directory (defaults to cwd)")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--show",      action="store_true",
                       help="Print the full tracking log")
    group.add_argument("--add",       metavar="DATA_FILE",
                       help="Add/update entry from assessment_data.json")
    group.add_argument("--processed", metavar="CV_FILE",
                       help="Check if a CV file has been processed (exit 0=yes, 1=no)")

    args = parser.parse_args()

    if args.show:
        cmd_show()
    elif args.add:
        cmd_add(args.add)
    elif args.processed:
        found = cmd_processed(args.processed)
        sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()
