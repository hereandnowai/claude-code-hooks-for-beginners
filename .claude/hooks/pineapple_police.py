# HOOK 5 - THE PINEAPPLE POLICE
# Runs just BEFORE Claude uses a tool (PreToolUse).
# If Claude is about to WRITE a file that contains the banned word,
# the write is refused and Claude is told to try again without it.

import json

from switchboard import read_if_on

BANNED_WORD = "pineapple"   # the crime. Change it to anything.

data = read_if_on("5-pineapple-police")   # stops here, quietly, if the Police are switched OFF
tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

# Claude Code writes files with three tools: Write (a whole file), Edit (one change)
# and MultiEdit (several changes). We only look at what is about to be WRITTEN -
# the file name and the new text - so Claude is still allowed to delete the word.
writes_a_file = tool_name in ("Write", "Edit", "MultiEdit")
new_text = [
    str(tool_input.get("file_path", "")),
    str(tool_input.get("content", "")),                 # Write
    str(tool_input.get("new_string", "")),              # Edit
] + [str(edit.get("new_string", "")) for edit in tool_input.get("edits", [])]   # MultiEdit

if writes_a_file and BANNED_WORD in " ".join(new_text).lower():
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"PINEAPPLE POLICE: the word '{BANNED_WORD}' is banned in this project. "
                f"Rewrite the content with no mention of {BANNED_WORD} at all, then try again."
            )
        }
    }))
else:
    print(json.dumps({"continue": True}))
