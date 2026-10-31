# HOOK 1 - THE GREETER
# Runs once, when a new Claude Code session starts (SessionStart).
# A new session means: you start `claude`, or you type /clear.
# It whispers a secret note to Claude before Claude reads your first message.
# You never see the note in the chat. Claude does.

import json   # lets Python read and write JSON (the language hooks speak)

from switchboard import read_if_on

# ---- CHANGE THESE TWO LINES AND SAVE. THAT IS THE WHOLE ACTIVITY. ----
MY_NAME = "Friend"          # put your own name here
FUN_TOPIC = "octopuses"     # any topic you like: "space", "Chennai", "cricket"
# ---------------------------------------------------------------------

read_if_on("1-greeter")   # stops here, quietly, if the Greeter is switched OFF

# This is the secret note. Claude treats it like background knowledge.
note = (
    f"The person you are talking to is called {MY_NAME}. "
    f"Greet them by name in your first reply. "
    f"End EVERY reply with one short fun fact about {FUN_TOPIC}, "
    f"on its own line, starting with the words 'Fun fact:'."
)

# Hand the note back to Claude Code as JSON. This exact shape matters.
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": note
    }
}))
