# SELF-TEST for the trainer. Run this before class:
#     python3 .claude/hooks/selftest.py
# It pretends to be Claude Code: it sends each hook script a fake message and
# checks the answer. Every line should say PASS. No Claude needed.
# It also checks .claude/settings.json and switchboard.json.
#
# While it runs it switches every hook ON, then puts switchboard.json back
# exactly as it found it - even if a check crashes.

import atexit
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .claude/hooks
PROJECT = HERE.parents[1]                       # project root
SETTINGS = HERE.parent / "settings.json"
SWITCHBOARD = HERE / "switchboard.json"
LOG = PROJECT / "hook-log.txt"
PY = sys.executable

ORIGINAL_SWITCHES = SWITCHBOARD.read_text(encoding="utf-8")
ORIGINAL_LOG = LOG.read_text(encoding="utf-8") if LOG.exists() else None


def put_things_back():
    SWITCHBOARD.write_text(ORIGINAL_SWITCHES, encoding="utf-8")
    if ORIGINAL_LOG is None:
        LOG.unlink(missing_ok=True)
    else:
        LOG.write_text(ORIGINAL_LOG, encoding="utf-8")


atexit.register(put_things_back)


def set_all(on: bool):
    names = json.loads(ORIGINAL_SWITCHES)
    SWITCHBOARD.write_text(json.dumps({name: on for name in names}, indent=2), encoding="utf-8")


def run(script: str, payload: dict) -> dict:
    """Send payload to the script on stdin, return its parsed JSON answer as a dict."""
    result = subprocess.run(
        [PY, str(HERE / script)], input=json.dumps(payload),
        capture_output=True, text=True, cwd=PROJECT, timeout=20,
    )
    if result.returncode != 0:
        return {"_crashed": result.stderr.strip()[-300:]}
    try:
        answer = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"_not_json": result.stdout[:200]}
    if not isinstance(answer, dict):
        return {"_not_an_object": result.stdout[:200]}
    return answer


def specific(out: dict) -> dict:
    """The hookSpecificOutput part of an answer, or an empty dict if there is none."""
    part = out.get("hookSpecificOutput")
    return part if isinstance(part, dict) else {}


passed = failed = skipped = 0


def check(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS  {label}")
    else:
        failed += 1
        print(f"FAIL  {label}   {detail}")


def skip(label, why):
    """Not every machine has ruff or git. Say so out loud instead of failing."""
    global skipped
    skipped += 1
    print(f"SKIP  {label}   ({why})")


# Shaped like the real payloads Claude Code 2.1.311 sent on 2026-10-30.
common = {"session_id": "test", "transcript_path": "/tmp/t.jsonl", "cwd": str(PROJECT)}
pre = {**common, "hook_event_name": "PreToolUse", "permission_mode": "acceptEdits", "tool_use_id": "x"}
post = {**common, "hook_event_name": "PostToolUse", "permission_mode": "acceptEdits", "tool_use_id": "x",
        "tool_response": {"success": True}}
stop = {**common, "hook_event_name": "Stop", "stop_hook_active": False, "last_assistant_message": "Done."}

# --- The wiring: settings.json and switchboard.json ---
try:
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    check("settings.json is valid JSON", True)
except Exception as e:
    settings = {}
    check("settings.json is valid JSON", False, str(e))

try:
    switches = json.loads(ORIGINAL_SWITCHES)
    check("switchboard.json is valid JSON", True)
except Exception as e:
    switches = {}
    check("switchboard.json is valid JSON", False, str(e))

EVENTS = {"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"}
wired = set()
for event, groups in settings.get("hooks", {}).items():
    check(f"settings.json: '{event}' is a real event name", event in EVENTS, event)
    for group in groups:
        for hook in group.get("hooks", []):
            wired.update(re.findall(r"/\.claude/hooks/(\w+\.py)", hook.get("command", "")))
for script in sorted(wired):
    check(f"settings.json: {script} exists", (HERE / script).exists())

for script in sorted(HERE.glob("*.py")):
    if script.name in ("selftest.py", "switchboard.py"):
        continue
    names = re.findall(r'read_if_on\("([^"]+)"\)', script.read_text(encoding="utf-8"))
    check(f"{script.name} is wired in settings.json", script.name in wired)
    check(f"{script.name} has a switch in switchboard.json",
          bool(names) and all(n in switches for n in names), str(names))

already_on = [name for name, on in switches.items() if on is True]
if already_on:
    print(f"NOTE  switched ON right now: {', '.join(already_on)}  (the lesson starts with all of them off)")

# --- Every hook is silent when it is switched OFF ---
set_all(False)
diary = PROJECT / "claude-diary.md"
diary_before = diary.read_text(encoding="utf-8") if diary.exists() else None
out = run("bouncer.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "rm playground/scratch.txt"}})
check("OFF: the bouncer lets rm through", out.get("continue") is True, str(out))
out = run("magic_word.py", {**common, "hook_event_name": "UserPromptSubmit", "prompt": "write me a poem"})
check("OFF: the magic word lets a rude prompt through", out.get("continue") is True, str(out))
run("diary.py", {**common, "hook_event_name": "UserPromptSubmit", "prompt": "should not be written"})
diary_after = diary.read_text(encoding="utf-8") if diary.exists() else None
check("OFF: the diary writes nothing", diary_after == diary_before, "diary changed")
check("OFF: hook-log.txt records the hook as off", LOG.exists() and "4-bouncer" in LOG.read_text(encoding="utf-8")
      and "off" in LOG.read_text(encoding="utf-8"), "no log line")

# --- A broken switchboard is loud, not silent ---
SWITCHBOARD.write_text('{ "4-bouncer": true, }', encoding="utf-8")   # the trailing comma breaks it
out = run("bouncer.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "rm playground/scratch.txt"}})
check("a broken switchboard.json says so in the chat", "switchboard.json" in out.get("systemMessage", ""), str(out))

# From here on, everything is ON.
set_all(True)

# --- 1 greeter ---
out = run("greeter.py", {**common, "hook_event_name": "SessionStart", "source": "startup"})
check("greeter gives Claude a note", "additionalContext" in specific(out), str(out))

# --- 2 diary ---
before = diary.read_text(encoding="utf-8") if diary.exists() else ""
out = run("diary.py", {**common, "hook_event_name": "UserPromptSubmit", "prompt": "selftest line"})
after = diary.read_text(encoding="utf-8") if diary.exists() else ""
check("diary writes the prompt to claude-diary.md", "selftest line" in after and len(after) > len(before), str(out))
check("diary tells Claude the time", "additionalContext" in specific(out), str(out))
if before:
    diary.write_text(before, encoding="utf-8")   # put the diary back how we found it
else:
    diary.unlink(missing_ok=True)

# --- 3 magic word ---
out = run("magic_word.py", {**common, "hook_event_name": "UserPromptSubmit", "prompt": "write me a poem"})
check("magic word blocks a prompt without 'please'", out.get("decision") == "block", str(out))
out = run("magic_word.py", {**common, "hook_event_name": "UserPromptSubmit", "prompt": "PLEASE write me a poem"})
check("magic word allows a prompt with 'please'", out.get("continue") is True, str(out))

# --- 4 bouncer ---
out = run("bouncer.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "rm playground/scratch.txt"}})
check("bouncer denies rm", specific(out).get("permissionDecision") == "deny", str(out))
out = run("bouncer.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "del playground\\scratch.txt"}})
check("bouncer denies del (Windows)", specific(out).get("permissionDecision") == "deny", str(out))
out = run("bouncer.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "ls -la"}})
check("bouncer allows ls", out.get("continue") is True, str(out))
out = run("bouncer.py", {**pre, "tool_name": "Write", "tool_input": {"file_path": str(PROJECT / "rm.txt"), "content": "rm -rf"}})
check("bouncer ignores file tools", out.get("continue") is True, str(out))

# --- 5 pineapple police ---
menu = str(PROJECT / "playground" / "pizza-menu.md")
out = run("pineapple_police.py", {**pre, "tool_name": "Write",
          "tool_input": {"file_path": menu, "content": "# Menu\n- Hawaiian: ham and Pineapple"}})
check("pineapple police denies a Write containing pineapple", specific(out).get("permissionDecision") == "deny", str(out))
out = run("pineapple_police.py", {**pre, "tool_name": "Edit",
          "tool_input": {"file_path": menu, "old_string": "Margherita", "new_string": "Pineapple", "replace_all": False}})
check("pineapple police denies an Edit that adds pineapple", specific(out).get("permissionDecision") == "deny", str(out))
out = run("pineapple_police.py", {**pre, "tool_name": "Edit",
          "tool_input": {"file_path": menu, "old_string": "pineapple", "new_string": "mango", "replace_all": False}})
check("pineapple police lets Claude REMOVE the word", out.get("continue") is True, str(out))
out = run("pineapple_police.py", {**pre, "tool_name": "Write",
          "tool_input": {"file_path": menu, "content": "# Menu\n- Margherita"}})
check("pineapple police allows a clean file", out.get("continue") is True, str(out))
out = run("pineapple_police.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "echo pineapple"}})
check("pineapple police ignores the terminal", out.get("continue") is True, str(out))

# --- 6 stamp ---
sample = PROJECT / "playground" / "_selftest_story.md"
pending = HERE / ".stamp-pending.json"
pending.unlink(missing_ok=True)
sample.write_text("# A story\n\nOnce upon a time.\n", encoding="utf-8")
out = run("stamp.py", {**post, "tool_name": "Write", "tool_input": {"file_path": str(sample), "content": ""}})
check("stamp asks for the missing stamp", "_selftest_story.md" in specific(out).get("additionalContext", ""), str(out))
out = run("stamp.py", stop)
# Claude Code reads "decision" at the TOP of a Stop answer. Copilot's nested shape is ignored here.
check("stamp refuses to let Claude finish while a file is unstamped", out.get("decision") == "block", str(out))
out = run("stamp.py", {**stop, "stop_hook_active": True})
check("stamp gives up after one send-back (no infinite loop)", out.get("continue") is True and not pending.exists(), str(out))
out = run("stamp.py", {**post, "tool_name": "Write", "tool_input": {"file_path": str(sample), "content": ""}})
_match = re.search(r'^STAMP = "(.+?)"', (HERE / "stamp.py").read_text(encoding="utf-8"), re.M)
STAMP_NOW = _match.group(1) if _match else "> 🤖 Made with Claude Code"
sample.write_text(STAMP_NOW + "\n# A story\n", encoding="utf-8")
out = run("stamp.py", {**post, "tool_name": "Edit", "tool_input": {"file_path": str(sample), "old_string": "",
                                                                    "new_string": "", "replace_all": False}})
check("stamp is quiet once the stamp is there", out.get("continue") is True and not pending.exists(), str(out))
out = run("stamp.py", stop)
check("stamp lets Claude finish once everything is stamped", out.get("continue") is True, str(out))
sample.unlink()
pending.unlink(missing_ok=True)

# Models name files however they like. "ReadMe.mD" is a real one, seen live with
# Copilot on 2026-09-20, and ".mD" is not ".md" unless you lower-case it.
for odd_name in ("_selftest_story.mD", "_selftest_story.MD", "_selftest_notes.TXT"):
    odd = PROJECT / "playground" / odd_name
    odd.write_text("# A story\n", encoding="utf-8")
    out = run("stamp.py", {**post, "tool_name": "Write", "tool_input": {"file_path": str(odd), "content": ""}})
    check(f"stamp catches {odd_name} (extension spelled oddly)",
          odd_name in specific(out).get("additionalContext", ""), str(out))
    odd.unlink()
    pending.unlink(missing_ok=True)

# --- 7 scoreboard + report card ---
board = PROJECT / "scoreboard.json"
board.unlink(missing_ok=True)
for name in ["Read", "Write", "Bash", "Grep"]:
    run("scoreboard.py", {**post, "tool_name": name, "tool_input": {}})
score = json.loads(board.read_text(encoding="utf-8")) if board.exists() else {}
check("scoreboard counts 4 tool uses", score.get("total") == 4 and score.get("files read") == 2
      and score.get("commands run") == 1, str(score))
report = PROJECT / "report-card.md"
before = report.read_text(encoding="utf-8") if report.exists() else ""
out = run("report_card.py", stop)
after = report.read_text(encoding="utf-8") if report.exists() else ""
check("report card is written at Stop", "Busy bee" in after and not board.exists(), str(out))
check("report card shows a chat note", "Report card" in out.get("systemMessage", ""), str(out))
if before:
    report.write_text(before, encoding="utf-8")
else:
    report.unlink(missing_ok=True)

# --- 7 ding (just must not crash and must answer JSON) ---
out = run("ding.py", stop)
check("ding answers with JSON", out.get("continue") is True, str(out))

# --- 8 linter ---
import shutil as _shutil
lint_state = HERE / ".lint-clean.json"
lint_state.unlink(missing_ok=True)
_ruff = _shutil.which("ruff") or next((str(g) for g in (Path.home() / ".local/bin/ruff",
                                                        Path("/opt/homebrew/bin/ruff"),
                                                        Path("/usr/local/bin/ruff")) if g.exists()), None)
if not _ruff:
    skip("linter (HOOK 8)", "ruff is not installed - try: uv tool install ruff")
else:
    messy = PROJECT / "playground" / "_selftest_messy.py"
    messy.write_text("import os, sys\nimport json\n\n\ndef greet(name):\n    x = 1\n    return name\n", encoding="utf-8")
    out = run("linter.py", {**post, "tool_name": "Write", "tool_input": {"file_path": str(messy), "content": ""}})
    check("linter hands the unfixable problems back to Claude", "F841" in specific(out).get("additionalContext", ""), str(out))
    check("linter let ruff fix the easy ones", "import os" not in messy.read_text(encoding="utf-8"), messy.read_text(encoding="utf-8"))
    check("linter will not call a failing file clean", not lint_state.exists(), str(out))
    messy.write_text("def greet(name):\n    return name\n", encoding="utf-8")
    out = run("linter.py", {**post, "tool_name": "Edit", "tool_input": {"file_path": str(messy), "old_string": "x",
                                                                         "new_string": "", "replace_all": False}})
    check("linter passes a clean file", "is clean" in out.get("systemMessage", ""), str(out))
    check("linter remembers the clean file for HOOK 9",
          lint_state.exists() and "_selftest_messy.py" in lint_state.read_text(encoding="utf-8"), str(out))
    messy.unlink()
    lint_state.unlink(missing_ok=True)

# --- 9 committer ---
# This hook writes to git history, so it is tested in throwaway repositories
# built here and thrown away again - never in the project you are sitting in.
import tempfile as _tempfile


def run_elsewhere(script_path, project, payload):
    result = subprocess.run([PY, str(script_path)], input=json.dumps(payload),
                            capture_output=True, text=True, cwd=project, timeout=20)
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"_not_json": (result.stdout + result.stderr)[:200]}


def build_pack(root):
    """A minimal copy of this pack's shape: <root>/.claude/hooks/committer.py, switched on."""
    hooks = root / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    _shutil.copy(HERE / "committer.py", hooks / "committer.py")
    _shutil.copy(HERE / "switchboard.py", hooks / "switchboard.py")
    (hooks / "switchboard.json").write_text(json.dumps({"9-committer": True}), encoding="utf-8")
    (root / "playground").mkdir(exist_ok=True)
    return hooks


def git_init(where):
    for cmd in (["init", "-q"], ["config", "user.name", "Self Test"],
                ["config", "user.email", "selftest@example.com"]):
        subprocess.run(["git", *cmd], cwd=where, capture_output=True)


if not _shutil.which("git"):
    skip("committer (HOOK 9)", "git is not installed")
else:
    # (a) the happy path: the pack IS the repository
    own = Path(_tempfile.mkdtemp(prefix="hooks-own-")).resolve()
    hooks = build_pack(own)
    git_init(own)
    subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "start"], cwd=own, capture_output=True)
    (own / "playground" / "hello.py").write_text("print('hi')\n", encoding="utf-8")
    (hooks / ".lint-clean.json").write_text(json.dumps(["playground/hello.py"]), encoding="utf-8")
    out = run_elsewhere(hooks / "committer.py", own, stop)
    check("committer commits the files the linter approved", "Committed 1 file" in out.get("systemMessage", ""), str(out))
    log = subprocess.run(["git", "log", "--oneline", "--name-only"], cwd=own, capture_output=True, text=True).stdout
    check("committer committed that file and nothing else", "playground/hello.py" in log and "committer.py" not in log, log[:300])
    check("committer clears its list afterwards", not (hooks / ".lint-clean.json").exists(), "list still there")
    out = run_elsewhere(hooks / "committer.py", own, stop)
    check("committer stays quiet when there is nothing new", out.get("continue") is True, str(out))

    # (b) the safety catch: the pack sits INSIDE a bigger repository
    outer = Path(_tempfile.mkdtemp(prefix="hooks-outer-")).resolve()
    git_init(outer)
    inner = outer / "lesson"
    inner.mkdir()
    hooks = build_pack(inner)
    (inner / "playground" / "hello.py").write_text("print('hi')\n", encoding="utf-8")
    (hooks / ".lint-clean.json").write_text(json.dumps(["playground/hello.py"]), encoding="utf-8")
    out = run_elsewhere(hooks / "committer.py", inner, stop)
    check("committer refuses when the pack is inside a bigger repo",
          "switched off" in out.get("systemMessage", ""), str(out))
    log = subprocess.run(["git", "log", "--oneline"], cwd=outer, capture_output=True, text=True).stdout
    check("committer left the bigger repo's history alone", log.strip() == "", log[:200])

    # (c) it waits for the Stamp instead of committing a half-done file
    waiting = Path(_tempfile.mkdtemp(prefix="hooks-stamp-")).resolve()
    hooks = build_pack(waiting)
    git_init(waiting)
    (waiting / "playground" / "hello.py").write_text("print('hi')\n", encoding="utf-8")
    (hooks / ".lint-clean.json").write_text(json.dumps(["playground/hello.py"]), encoding="utf-8")
    (hooks / ".stamp-pending.json").write_text(json.dumps(["playground/hello.py"]), encoding="utf-8")
    out = run_elsewhere(hooks / "committer.py", waiting, stop)
    check("committer waits while the Stamp is still pending",
          "waiting for the Stamp" in out.get("systemMessage", ""), str(out))

    # (d) a file git is ignoring is explained, not crashed on
    ign = Path(_tempfile.mkdtemp(prefix="hooks-ignored-")).resolve()
    hooks = build_pack(ign)
    git_init(ign)
    (ign / ".gitignore").write_text("playground/*\n", encoding="utf-8")
    (ign / "playground" / "notes.md").write_text("notes\n", encoding="utf-8")
    (hooks / ".lint-clean.json").write_text(json.dumps(["playground/notes.md"]), encoding="utf-8")
    out = run_elsewhere(hooks / "committer.py", ign, stop)
    check("committer explains an ignored file instead of failing",
          "throws away" in out.get("systemMessage", ""), str(out))

    for tmp_root in (own, outer, waiting, ign):
        _shutil.rmtree(tmp_root, ignore_errors=True)

# --- 99 mystery: the three-rule detective game ---
progress = HERE / ".mystery-progress.json"
progress.unlink(missing_ok=True)
out = run("mystery.py", {**common, "hook_event_name": "SessionStart", "source": "startup"})
check("mystery: pirate note at SessionStart", "pirate" in specific(out).get("additionalContext", ""), str(out))
check("mystery: the challenge is announced", "0 of 3" in out.get("systemMessage", ""), str(out))
out = run("mystery.py", {**pre, "tool_name": "Write",
          "tool_input": {"file_path": str(PROJECT / "playground" / "MyNotes.md"), "content": ""}})
check("mystery: denies a new file called MyNotes.md", specific(out).get("permissionDecision") == "deny", str(out))
check("mystery: rule 1 is a riddle, not an explanation",
      "SHOUTIN" in specific(out).get("permissionDecisionReason", "") and "1 of 3" in out.get("systemMessage", ""), str(out))
out = run("mystery.py", {**pre, "tool_name": "Write",
          "tool_input": {"file_path": str(PROJECT / "playground" / "map.md"), "content": "here be treasure"}})
check("mystery: rule 2 catches the cursed word",
      specific(out).get("permissionDecision") == "deny" and "2 of 3" in out.get("systemMessage", ""), str(out))
out = run("mystery.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "ls", "description": "List files"}})
check("mystery: rule 3 catches a one-word command",
      specific(out).get("permissionDecision") == "deny" and "3 of 3" in out.get("systemMessage", ""), str(out))
check("mystery: the rules are revealed at 3 of 3", "lowercase" in out.get("systemMessage", ""), str(out))
out = run("mystery.py", {**pre, "tool_name": "Bash", "tool_input": {"command": "ls -la", "description": "List files"}})
check("mystery: a longer command is allowed", out.get("continue") is True, str(out))
out = run("mystery.py", {**pre, "tool_name": "Write",
          "tool_input": {"file_path": str(PROJECT / "playground" / "notes.md"), "content": ""}})
check("mystery: allows notes.md", out.get("continue") is True, str(out))
out = run("mystery.py", {**pre, "tool_name": "Edit",
          "tool_input": {"file_path": str(PROJECT / "playground" / "README.md"), "old_string": "a",
                         "new_string": "b", "replace_all": False}})
check("mystery: editing an existing file with capitals elsewhere is allowed", out.get("continue") is True, str(out))
progress.unlink(missing_ok=True)

print()
print(f"{passed} passed, {failed} failed" + (f", {skipped} skipped" if skipped else ""))
sys.exit(1 if failed else 0)
