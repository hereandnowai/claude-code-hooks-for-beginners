# HOOK 4 - THE BOUNCER
# Runs just BEFORE Claude uses a tool (PreToolUse).
# If Claude is about to run a terminal command that deletes things,
# the bouncer stops it at the door.

import json
import re     # lets us search text for patterns (like "rm" or "del")

from switchboard import read_if_on

# What the bouncer does when it catches something:
#   "deny" = block it, no questions asked
#   "ask"  = pause and let the human decide
MODE = "deny"

# Words that delete things, in Linux/Mac (rm, rmdir) and Windows (del, Remove-Item).
DELETE_WORDS = r"\b(rm|rmdir|del|erase|Remove-Item)\b"

data = read_if_on("4-bouncer")             # stops here, quietly, if the Bouncer is switched OFF
tool_name = data.get("tool_name", "")       # which tool Claude wants to use
tool_input = data.get("tool_input", {})     # what it wants to give that tool

# We only care about the terminal. In Claude Code that tool is called "Bash".
if tool_name == "Bash":
    command = str(tool_input.get("command", ""))
    if re.search(DELETE_WORDS, command):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": MODE,
                "permissionDecisionReason": (
                    f"BOUNCER: the command '{command}' deletes things. "
                    "Deleting is not allowed in this project. "
                    "Tell the user you were stopped by the bouncer and do not try another way."
                )
            }
        }))
        raise SystemExit

# Anything else walks straight in.
print(json.dumps({"continue": True}))
