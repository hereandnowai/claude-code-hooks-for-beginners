# HOOK 2 - THE DIARY
# Runs every time you press Enter (UserPromptSubmit).
# It writes your message into claude-diary.md with the date and time,
# and it also tells Claude what time it is right now.

import json
from datetime import datetime   # gives us today's date and the current time
from pathlib import Path        # a friendly way to work with file paths

from switchboard import read_if_on

# Where is the project folder? This file lives at
#   <project>/.claude/hooks/diary.py
# so we go up two folders to reach <project>.
PROJECT = Path(__file__).resolve().parents[2]
DIARY = PROJECT / "claude-diary.md"

# Read what Claude Code sent us. For this event it includes your message as "prompt".
data = read_if_on("2-diary")   # stops here, quietly, if the Diary is switched OFF
prompt = data.get("prompt", "")

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")   # e.g. 2026-10-30 10:42:15

# If the diary does not exist yet, start it with a title.
if not DIARY.exists():
    DIARY.write_text("# My Claude diary\n\n", encoding="utf-8")

# Add one line per message. "a" means append (add to the end, never overwrite).
with DIARY.open("a", encoding="utf-8") as f:
    f.write(f"- **{now}** - {prompt}\n")

# Bonus: Claude has no clock. Give it one.
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": f"The current local date and time is {now}."
    }
}))
