# HOOK 7 (part 1) - THE SCOREBOARD
# Runs just AFTER Claude uses any tool (PostToolUse).
# It counts what Claude did and keeps the score in scoreboard.json.
# Open that file and watch the numbers climb while Claude works.

import json
from pathlib import Path

from switchboard import read_if_on

PROJECT = Path(__file__).resolve().parents[2]
SCOREBOARD = PROJECT / "scoreboard.json"

data = read_if_on("7-scoreboard")   # stops here, quietly, if the Scoreboard is switched OFF
tool_name = data.get("tool_name", "")

# Load the current score, or start from zero.
if SCOREBOARD.exists():
    score = json.loads(SCOREBOARD.read_text(encoding="utf-8"))
else:
    score = {"files read": 0, "files written": 0, "commands run": 0, "other": 0, "total": 0}

# Sort the tool into a bucket by its Claude Code name.
if tool_name == "Bash":
    score["commands run"] += 1
elif tool_name in ("Read", "Glob", "Grep", "LS"):
    score["files read"] += 1
elif tool_name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
    score["files written"] += 1
else:
    score["other"] += 1
score["total"] += 1

SCOREBOARD.write_text(json.dumps(score, indent=2), encoding="utf-8")

print(json.dumps({"continue": True}))
