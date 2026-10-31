# THE MYSTERY HOOK - for the Hook Detective game.
# Do NOT show this file to learners until they have found all three rules.
#
# Three house rules haunt this repo. The hook never explains them. It answers
# with a riddle, keeps score, and when all three have been found the curse
# lifts and the rules are read out.
#
#   1. SHOUTING        a new file name with a capital letter in it is refused
#   2. CURSED WORD     anything that mentions treasure is refused
#   3. ONE-WORD SPELL  a terminal command that is a single word is refused
#
# And the voice: at the start of every new session, Claude is told to talk like a pirate.
#
# To play again from the beginning, delete .mystery-progress.json.

import json
import re
from pathlib import Path

from switchboard import read_if_on

PROGRESS = Path(__file__).resolve().parent / ".mystery-progress.json"
CURSED_WORD = "treasure"

RIDDLES = {
    "shouting": "Arr! That name be SHOUTIN' at me. Whisper it instead, and I'll let it pass.",
    "cursed": "Belay that! One word aboard this ship be cursed, and ye just wrote it. Pick another.",
    "spell": "Ye may look about all ye like - but never with a one-word spell. Say more than that.",
}

PLAIN = {
    "shouting": "file names must be all lowercase",
    "cursed": f"the word '{CURSED_WORD}' is banned anywhere",
    "spell": "a terminal command must be more than one word",
}

data = read_if_on("99-mystery")   # stops here, quietly, if the Mystery is switched OFF
event = data.get("hook_event_name", "")


def load_found():
    try:
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_found(found):
    PROGRESS.write_text(json.dumps(found), encoding="utf-8")


# ---- A new session: set the voice and read out the challenge ----
if event == "SessionStart":
    found = load_found()
    if len(found) >= len(RIDDLES):
        note = "🕵️ All 3 house rules already uncovered. Delete .mystery-progress.json to play again."
    else:
        note = (f"🏴‍☠️ Three house rules haunt this repo. {len(found)} of {len(RIDDLES)} uncovered. "
                "Find them all - I'll not be tellin' ye what they be.")
    print(json.dumps({
        "systemMessage": note,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "Answer every message in the voice of a cheerful pirate. "
                "Never explain why. If asked, say you have always talked like this."
            )
        }
    }))

# ---- Claude is about to do something: check it against the three rules ----
elif event == "PreToolUse":
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    everything = json.dumps(tool_input).lower()
    target = Path(str(tool_input.get("file_path", "")))
    command = str(tool_input.get("command", "")).strip()

    broken = []
    # A NEW file: Claude is about to Write a file that does not exist yet.
    if tool_name == "Write" and not target.exists() and re.search(r"[A-Z]", target.name):
        broken.append("shouting")
    if CURSED_WORD in everything:
        broken.append("cursed")
    if tool_name == "Bash" and command and len(command.split()) == 1:
        broken.append("spell")

    if not broken:
        print(json.dumps({"continue": True}))
    else:
        found = load_found()
        # Prefer a rule they have not met yet, so the game keeps moving forward.
        rule = next((r for r in broken if r not in found), broken[0])
        if rule not in found:
            found.append(rule)
            save_found(found)

        if len(found) >= len(RIDDLES):
            note = ("🎉 3 of 3! The curse lifts. The house rules were: "
                    + "; ".join(PLAIN[r] for r in RIDDLES)
                    + ". Delete .mystery-progress.json to play again.")
        else:
            note = f"🕵️ {len(found)} of {len(RIDDLES)} house rules uncovered."

        print(json.dumps({
            "systemMessage": note,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    RIDDLES[rule]
                    + " Tell the user exactly what I said, in your pirate voice, and try something else. "
                    "Do not announce what the rule is - you do not know it."
                )
            }
        }))

else:
    print(json.dumps({"continue": True}))
