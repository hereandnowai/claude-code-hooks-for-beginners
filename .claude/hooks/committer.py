# HOOK 9 - THE COMMITTER
# Runs when Claude finishes its answer (Stop).
# It reads .lint-clean.json - the list HOOK 8 (the Linter) left behind - and
# commits exactly those files. Nothing else. It never runs "git add ." and it
# never pushes: what leaves this machine stays your decision.
#
# One commit per answer, not one per file, so the log reads like the lesson:
# one question from you, one commit.

import json
import subprocess
from pathlib import Path

from switchboard import read_if_on

PROJECT = Path(__file__).resolve().parents[2]
CLEAN = Path(__file__).resolve().parent / ".lint-clean.json"
STAMP_PENDING = Path(__file__).resolve().parent / ".stamp-pending.json"

read_if_on("9-committer")   # stops here, quietly, if the Committer is switched OFF


def git(*args):
    """Run a git command inside this project and hand back (worked?, output)."""
    result = subprocess.run(["git", *args], cwd=str(PROJECT),
                            capture_output=True, text=True, timeout=20)
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def done(message=None):
    print(json.dumps({"systemMessage": message} if message else {"continue": True}))
    raise SystemExit


try:
    files = json.loads(CLEAN.read_text(encoding="utf-8"))
except Exception:
    files = []

if not files:
    done()

# ---- Safety catch 1: is this folder its own repository? ----
# If the lesson sits inside a bigger repo, a commit here would land in THAT
# repo's history. Refuse, and say so plainly.
ok, top = git("rev-parse", "--show-toplevel")
if not ok:
    done("📦 The Committer found no git repository here, so nothing was committed.")
if Path(top).resolve() != PROJECT:
    CLEAN.unlink(missing_ok=True)
    done(f"📦 The Committer is switched off: this folder lives inside a bigger repo ({Path(top).name}). "
         "Open the lesson as its own repository to try this hook.")

# ---- Safety catch 2: is the Stamp still waiting? ----
# HOOK 6 sends Claude back for a missing stamp. Committing now would commit the
# half-done file, so we wait one turn and let the Stamp finish first.
try:
    if json.loads(STAMP_PENDING.read_text(encoding="utf-8")):
        done("📦 The Committer is waiting for the Stamp to finish.")
except Exception:
    pass

# ---- Stage exactly the files the Linter approved ----
staged = [name for name in files if (PROJECT / name).is_file()]
if not staged:
    CLEAN.unlink(missing_ok=True)
    done()

# git will not add a file that .gitignore throws away, and the playground is
# thrown away on purpose. Drop those with an explanation instead of a git error.
ok, listed = git("check-ignore", "--", *staged)
if ok and listed:
    ignored = [line.strip() for line in listed.splitlines() if line.strip()]
    staged = [name for name in staged if name not in ignored]
    if not staged:
        CLEAN.unlink(missing_ok=True)
        done(f"📦 Nothing committed: .gitignore throws away {', '.join(ignored[:3])}.")

ok, output = git("add", "--", *staged)
if not ok:
    done(f"📦 git add failed: {output.splitlines()[0] if output else 'unknown error'}")

# Is there anything actually different? (Claude often rewrites a file identically.)
unchanged, _ = git("diff", "--cached", "--quiet")
if unchanged:
    CLEAN.unlink(missing_ok=True)
    done("📦 Nothing new to commit.")

names = ", ".join(staged[:3]) + (f" and {len(staged) - 3} more" if len(staged) > 3 else "")
ok, output = git("commit", "-m", f"Claude: {names} (ruff clean)")
CLEAN.unlink(missing_ok=True)

if not ok:
    first = output.splitlines()[0] if output else "unknown error"
    done(f"📦 git commit failed: {first}")

_, sha = git("rev-parse", "--short", "HEAD")
done(f"📦 Committed {len(staged)} file(s) as {sha}: {names}")
