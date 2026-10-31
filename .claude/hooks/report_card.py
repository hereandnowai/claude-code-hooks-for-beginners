# HOOK 7 (part 2) - THE REPORT CARD
# Runs when Claude finishes answering (Stop).
# It reads scoreboard.json, writes a report card, and resets the score
# so the next answer starts from zero.

import json
from datetime import datetime
from pathlib import Path

from switchboard import read_if_on

PROJECT = Path(__file__).resolve().parents[2]
SCOREBOARD = PROJECT / "scoreboard.json"
REPORT = PROJECT / "report-card.md"

read_if_on("7-scoreboard")   # one switch for all three parts of Hook 7

if SCOREBOARD.exists():
    score = json.loads(SCOREBOARD.read_text(encoding="utf-8"))
    SCOREBOARD.unlink()   # delete it so the next answer starts fresh
else:
    score = {"files read": 0, "files written": 0, "commands run": 0, "other": 0, "total": 0}

total = score["total"]
if total == 0:
    grade = "💤 Just chatting (no tools used)"
elif total <= 3:
    grade = "🐢 Light work"
elif total <= 10:
    grade = "🐝 Busy bee"
else:
    grade = "🚀 Overachiever"

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
lines = [
    f"## Report card - {now}",
    "",
    "| What Claude did | How many times |",
    "|---|---|",
]
for name, count in score.items():
    if name != "total":
        lines.append(f"| {name} | {count} |")
lines += ["", f"**Total tool uses:** {total}", "", f"**Grade:** {grade}", "", "---", ""]

if not REPORT.exists():
    REPORT.write_text("# Claude report cards\n\n", encoding="utf-8")
with REPORT.open("a", encoding="utf-8") as f:
    f.write("\n".join(lines))

# systemMessage shows up in the chat as a small note from the hook.
print(json.dumps({
    "continue": True,
    "systemMessage": f"📋 Report card written: {total} tool uses, grade {grade}"
}))
