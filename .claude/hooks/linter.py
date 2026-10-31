# HOOK 8 - THE LINTER
# Runs just AFTER Claude writes a file (PostToolUse).
# Every Python file Claude touches is handed to ruff, the linter.
# ruff quietly fixes what it can fix by itself, and reports what it cannot.
# Anything ruff could not fix is sent back to Claude to repair.
#
# Files that come out clean are remembered in .lint-clean.json.
# HOOK 9 (the Committer) reads that file when Claude finishes.
# Two hooks, one conversation: this one says "it is clean", that one commits it.

import json
import shutil
import subprocess
from pathlib import Path

from switchboard import read_if_on

PROJECT = Path(__file__).resolve().parents[2]
CLEAN = Path(__file__).resolve().parent / ".lint-clean.json"   # passed the lint, waiting to be committed

data = read_if_on("8-linter")   # stops here, quietly, if the Linter is switched OFF


def find_ruff():
    """Where is ruff? A hook does not always get your terminal's PATH,
    so look in the usual places yourself before giving up."""
    on_path = shutil.which("ruff")
    if on_path:
        return on_path
    for guess in (Path.home() / ".local" / "bin" / "ruff",
                  Path("/opt/homebrew/bin/ruff"),
                  Path("/usr/local/bin/ruff")):
        if guess.exists():
            return str(guess)
    return None


def short(path):
    return str(path.relative_to(PROJECT)) if path.is_relative_to(PROJECT) else str(path)


# ---- Which file did Claude just write? Write, Edit and MultiEdit all say so in "file_path". ----
raw = data.get("tool_input", {}).get("file_path", "")
path = Path(raw) if raw else None
if path is not None and not path.is_absolute():
    path = PROJECT / path
if path is not None:
    path = path.resolve()

if path is None or not path.is_file():
    print(json.dumps({"continue": True}))
    raise SystemExit

notes = []        # short notes for the human, shown in the chat
problems = []     # things ruff could not fix, sent back to Claude
is_clean = False

if path.suffix.lower() != ".py":
    notes.append(f"🧹 {short(path)}: nothing for ruff to lint")
    is_clean = True          # nothing to lint in a .md or .txt, so it passes
elif (ruff := find_ruff()) is None:
    notes.append("🧹 ruff is not installed, so nothing was linted. Install it with: uv tool install ruff")
else:
    try:
        result = subprocess.run(
            # --no-cache keeps ruff from leaving a .ruff_cache folder in the learner's project.
            [ruff, "check", "--fix", "--no-cache", "--output-format=concise", str(path)],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=20,
        )
        # ruff prints one line per problem, then a summary line such as
        # "Found 5 errors (4 fixed, 1 remaining)."
        lines = [ln for ln in result.stdout.splitlines() if ":" in ln and not ln.startswith("Found")]
        if result.returncode == 0:
            is_clean = True
            notes.append(f"🧹 ruff: {short(path)} is clean")
        else:
            notes.append(f"🧹 ruff: {short(path)} still has {len(lines)} problem(s)")
            problems.extend(lines)
    except Exception as problem:   # ruff missing, too slow, anything at all
        notes.append(f"🧹 ruff could not run on {short(path)}: {problem}")

# ---- Remember the clean files for HOOK 9 ----
try:
    already = json.loads(CLEAN.read_text(encoding="utf-8"))
except Exception:
    already = []
if is_clean and short(path) not in already:
    already.append(short(path))
if not is_clean:
    # A file that failed this time must not stay on yesterday's clean list.
    already = [name for name in already if name != short(path)]
if already:
    CLEAN.write_text(json.dumps(already), encoding="utf-8")
elif CLEAN.exists():
    CLEAN.unlink()

answer = {"systemMessage": " · ".join(notes)}
if problems:
    # Hand the leftovers back to Claude, in its own words.
    answer["hookSpecificOutput"] = {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            "RUFF found problems it could not fix on its own:\n"
            + "\n".join(problems)
            + "\nruff has already changed this file, so read it again before you edit it. "
            "Fix each problem, then carry on. Do not switch the linter off."
        ),
    }
print(json.dumps(answer))
