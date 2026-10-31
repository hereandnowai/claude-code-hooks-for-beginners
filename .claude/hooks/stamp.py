# HOOK 6 - THE STAMP
# Runs at TWO moments:
#   1. Just AFTER Claude writes a file (PostToolUse). If a .md or .txt file does
#      not start with our stamp, the hook tells Claude to go back and add it.
#   2. When Claude tries to FINISH (Stop). If a file is still missing the stamp,
#      the hook refuses to let Claude finish until it is added.
# Moment 1 is a hook TALKING BACK. Moment 2 is a hook that will not take no for an answer.

import json
from pathlib import Path

from switchboard import read_if_on

STAMP = "> 🤖 Made with Claude Code"   # the line every text file must start with
FILE_TYPES = (".md", ".txt")           # we only stamp harmless text files (any spelling: .MD, .Txt)

PROJECT = Path(__file__).resolve().parents[2]
PENDING = Path(__file__).resolve().parent / ".stamp-pending.json"   # files we are still waiting on

data = read_if_on("6-stamp")   # stops here, quietly, if the Stamp is switched OFF
event = data.get("hook_event_name", "")


def is_missing_stamp(raw):
    """Return the short file name if this text file exists and lacks the stamp, else None."""
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT / path
    path = path.resolve()
    # .lower() matters: Claude will happily create "ReadMe.mD", and ".mD" is not ".md".
    if path.suffix.lower() in FILE_TYPES and path.exists():
        first_line = path.read_text(encoding="utf-8", errors="ignore").split("\n", 1)[0]
        if STAMP not in first_line:
            return str(path.relative_to(PROJECT)) if path.is_relative_to(PROJECT) else str(path)
    return None


def load_pending():
    try:
        return json.loads(PENDING.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_pending(files):
    if files:
        PENDING.write_text(json.dumps(files), encoding="utf-8")
    elif PENDING.exists():
        PENDING.unlink()


def rule_text(files):
    return (
        f"HOUSE RULE: every .md and .txt file must begin with the exact line '{STAMP}'. "
        f"These files are missing it: {', '.join(files)}. "
        "Add that line as the very first line of each of them now. "
        "You are not finished until this is done."
    )


# ---- Moment 1: just after Claude used a tool ----
if event == "PostToolUse":
    # Write, Edit and MultiEdit all say which file they touched in "file_path".
    raw = data.get("tool_input", {}).get("file_path", "")
    pending = load_pending()
    name = is_missing_stamp(raw) if raw else None
    if name and name not in pending:
        pending.append(name)
    # Drop anything that has been stamped since we last looked.
    pending = [f for f in pending if is_missing_stamp(PROJECT / f)]
    save_pending(pending)
    if pending:
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": rule_text(pending)}
        }))
    else:
        print(json.dumps({"continue": True}))

# ---- Moment 2: Claude wants to finish ----
elif event == "Stop":
    pending = [f for f in load_pending() if is_missing_stamp(PROJECT / f)]
    already_sent_back = data.get("stop_hook_active", False)   # True if we blocked once already
    if pending and not already_sent_back:
        # Refuse to finish. Claude gets the reason and must keep working.
        # In Claude Code, "decision" sits at the TOP of the answer, not inside hookSpecificOutput.
        print(json.dumps({"decision": "block", "reason": rule_text(pending)}))
    else:
        # Either everything is stamped, or we already sent Claude back once. Never loop forever.
        save_pending([])
        print(json.dumps({"continue": True}))

else:
    print(json.dumps({"continue": True}))
