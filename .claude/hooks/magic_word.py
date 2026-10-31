# HOOK 3 - THE MAGIC WORD
# Runs every time you press Enter (UserPromptSubmit).
# If your message does not contain the magic word, the message is BLOCKED.
# Claude never sees it. Hooks can say no to humans too.

import json

from switchboard import read_if_on

MAGIC_WORD = "please"   # change it to anything. "abracadabra" is popular.

data = read_if_on("3-magic-word")   # stops here, quietly, if the Magic Word is switched OFF
prompt = data.get("prompt", "")

if MAGIC_WORD.lower() in prompt.lower():
    # The magic word is there. Let the message through, say nothing.
    print(json.dumps({"continue": True}))
else:
    # No magic word. Block the message and explain why.
    print(json.dumps({
        "decision": "block",
        "reason": f"The magic word is missing. Try again with '{MAGIC_WORD}' somewhere in your message."
    }))
