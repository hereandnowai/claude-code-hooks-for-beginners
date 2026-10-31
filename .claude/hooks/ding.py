# HOOK 7 (part 3) - THE DING
# Runs when Claude finishes answering (Stop).
# It makes a sound so you can look away from the screen and still know
# when Claude is done. Works on Mac, Linux and Windows.

import json
import platform
import subprocess

from switchboard import read_if_on

MESSAGE = "Claude is done"   # what the Mac voice says. Change it!

read_if_on("7-scoreboard")   # one switch for all three parts of Hook 7

system = platform.system()   # "Darwin" = Mac, "Linux", or "Windows"
try:
    if system == "Darwin":
        subprocess.run(["say", MESSAGE], timeout=8)
    elif system == "Windows":
        subprocess.run(["powershell", "-c", "[console]::beep(880,400); [console]::beep(1175,400)"], timeout=8)
    else:
        # Linux: try a desktop notification first, then a sound file if one exists.
        subprocess.run(["notify-send", "Claude Code", MESSAGE], timeout=8)
        subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], timeout=8)
except Exception:
    pass   # no sound on this machine? No problem. Never let a hook crash over a beep.

print(json.dumps({"continue": True}))
