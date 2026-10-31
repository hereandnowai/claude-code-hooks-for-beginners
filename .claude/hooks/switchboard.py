# THE SWITCHBOARD READER
# Every hook script asks this file one question before it does anything:
# "am I switched on?" The answer lives in switchboard.json, right next to this file.
#
# You never need to edit this file. To switch a hook on or off, edit switchboard.json.
#
# It also writes one line to hook-log.txt every time a hook runs, ON or OFF.
# That log is where you look when "nothing happened".

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent            # <project>/.claude/hooks
PROJECT = HERE.parents[1]                         # <project>
SWITCHBOARD = HERE / "switchboard.json"
LOG = PROJECT / "hook-log.txt"


def log(event, name, state):
    """Add one line to hook-log.txt. Never let a log line crash a hook."""
    try:
        now = datetime.now().strftime("%H:%M:%S")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{now}  {event:<17} {name:<20} {state}\n")
    except Exception:
        pass


def read_if_on(name):
    """Read what Claude Code sent us. If this hook is switched OFF, answer
    'carry on' and stop the script right here. If it is ON, hand back the message."""
    # Read the message first, always. Claude Code is waiting to hand it over.
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        data = {}
    event = data.get("hook_event_name", "?")

    try:
        switches = json.loads(SWITCHBOARD.read_text(encoding="utf-8"))
    except Exception as problem:
        # A missing comma in switchboard.json must not fail silently. Say so in the chat.
        log(event, name, "BROKEN SWITCHBOARD")
        print(json.dumps({"systemMessage":
                          f"⚠️ switchboard.json could not be read, so every hook is off: {problem}"}))
        sys.exit(0)

    if switches.get(name) is not True:
        log(event, name, "off")
        print(json.dumps({"continue": True}))
        sys.exit(0)

    log(event, name, "ON")
    return data
