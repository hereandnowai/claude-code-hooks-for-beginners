<p align="center">
  <img src="assets/logo.png" alt="HERE AND NOW AI" width="420">
</p>
<p align="center"><em>AI is Good</em></p>

---

# Claude Code Hooks for Absolute Beginners

### Teach your robot some house rules

**Time:** about 3 hours, in 15–20 minute chunks. Stop anywhere.
**You need:** VS Code, Claude Code signed in, and Python 3 installed. That is all.
**You do not need:** any coding experience. Every file is already written. You change one word in a switchboard, edit a line or two, and paste prompts.

Everything lives in this repository. Open **this folder** in VS Code, not a folder above it, and start Claude Code from inside it.

**Get it:**

```
git clone https://github.com/hereandnowai/claude-code-hooks-for-beginners.git
cd claude-code-hooks-for-beginners
code .
```

Then run the self-test in the VS Code terminal to confirm the machine is ready:

```
python3 .claude/hooks/selftest.py
```

Teaching with GitHub Copilot instead? The same lesson for Copilot lives at [github-copilot-hooks-for-beginners](https://github.com/hereandnowai/github-copilot-hooks-for-beginners).

---

## Instructor notes (do not hand this page out)

### What this lesson teaches

Learners already know that Claude follows instructions, prompts and skills. All of those *ask* Claude to behave. A hook *makes* it behave. A hook is a tiny program that Claude Code runs at a fixed moment, and that program can whisper to Claude, watch it, refuse it, or send it back to redo work.

The lesson never says that in the abstract. It shows nine hooks, each with one job and one silly name, and the learner discovers the idea by playing.

| # | Hook | Moment it fires | What the learner sees |
|---|---|---|---|
| 1 | The Greeter | a new session starts | Claude knows a nickname nobody typed |
| 2 | The Diary | every message | a file that records everything they type, and Claude learns the time |
| 3 | The Magic Word | every message | their message is refused unless it says "please" |
| 4 | The Bouncer | before Claude uses a tool | Claude is stopped from deleting a file |
| 5 | The Pineapple Police | before Claude uses a tool | Claude is refused, then rewrites without the banned word |
| 6 | The Stamp | after Claude uses a tool, and when it tries to finish | Claude is sent back to add a line to a file it just wrote, and cannot finish until it does |
| 7 | The Scoreboard | after every tool, and when Claude finishes | a live score, a report card, and a sound |
| 8 | The Linter | after Claude writes a file | ruff repairs Claude's Python before Claude has finished speaking, and sends back what it cannot fix |
| 9 | The Committer | when Claude finishes | the files that passed the linter are committed to git, by name, without a human |

Then a detective game and five build-your-own challenges.

### The one rule that runs the whole lesson

Every hook is listed in **one file**: `.claude/hooks/switchboard.json`. A hook is **ON** when its line says `true`. It is **OFF** when its line says `false`.

Every hook ships switched off. Each activity starts with "flip the switch". Learners can always get back to a calm state by setting every line to `false`. Say this rule out loud in the first minute and write it on the board.

**Why a switchboard, and not the `.json.off` rename from the Copilot pack.** Claude Code reads hooks only from settings files (`.claude/settings.json` here) and has no per-hook off switch. So all hooks are wired into `.claude/settings.json` from the start, and every script asks the switchboard "am I on?" before doing anything. Learners change one word; they never touch the nested JSON where beginners break things. Show `.claude/settings.json` once, in Hook 4's "behind the curtain", so they know where the real wiring lives.

A switch takes effect on the **very next** event. No restart, no reload — except the Greeter and the Mystery voice, which only run when a session starts (`/clear`).

### Before class

1. Open this folder in VS Code and run the self-test in the terminal:
   ```
   python3 .claude/hooks/selftest.py
   ```
   Every line must say `PASS`. It pretends to be Claude Code and feeds each script a fake message shaped like the real ones. No Claude needed. It switches every hook on while it runs and puts the switchboard back exactly as it found it. Last run: **97 passed, 0 failed, on 2026-10-30.**
2. Then rehearse **every hook live once** in Claude Code, in order, on the machine you will teach from. The scripts are verified, and every hook has been fired through real Claude Code (see below) — but the machine, the model and Claude Code itself change under you.
3. Start Claude Code in this folder (`claude` in the VS Code terminal) and accept the **trust this folder** question. Project hooks do not run in a folder that is not trusted.
4. On lab machines, confirm `python3 --version` works in the VS Code terminal. **Windows:** Claude Code runs hooks through Git Bash, where the command is often `python`, not `python3`. If `python3 --version` fails there, paste this into Claude once: `In .claude/settings.json, replace every "python3" with "python". Change nothing else.`
5. **Hook 8 needs `ruff`.** Install it with `uv tool install ruff` (or `pip install ruff`) and check `ruff --version`. Without it the self-test prints `SKIP` for Hook 8 and the hook says so in the chat instead of failing silently.
6. **Hook 9 needs this folder to be its own git repository.** A fresh `git clone` already is one — nothing to do. Check with `git rev-parse --show-toplevel`: it must print the lesson folder itself. If it prints a folder above it, you are inside a bigger repo and the Committer will refuse to run, on purpose. Copy the folder somewhere else (the Desktop) and run `git init && git add -A && git commit -m "start"` there.

### Facts checked live, not taken from the docs

Every hook below was fired through real Claude Code **2.1.311** (`claude -p`, Sonnet, `acceptEdits` mode) on **2026-10-30**, in a copy of this pack that was its own git repo. What Claude Code actually sent and did:

- **Tool names** are `Bash`, `Write`, `Edit`, `MultiEdit`, `Read`, `Glob`, `Grep`. `Write` sends `file_path` + `content`; `Edit` sends `file_path`, `old_string`, `new_string`, `replace_all`; `Bash` sends `command` + `description`. **`file_path` is always absolute.** None of Copilot's names (`run_in_terminal`, `create_file`, `apply_patch`, `filePath`) appear.
- **A `Stop` block is `{"decision": "block", "reason": ...}` at the top of the answer.** Copilot reads it nested inside `hookSpecificOutput`; Claude Code does not. A Copilot-shaped Stamp would silently never lock the door. The self-test fails on the Copilot shape — checked.
- **`SessionStart` arrives with `source: "startup"`** when `claude` starts. `/clear` starts a new session too.
- **Claude may already know the learner's real name** — live, it said *"Hi Friend!"* and then read the real name out of git config. So the Greeter activity uses a **made-up nickname**. A real name proves nothing.
- **Claude Code respects the human over the hook, and says so.** When the prompt *insists* on pineapple, the Police still refuse the write, but Claude stops and asks the human which rule wins instead of quietly rewriting. When the prompt *insists* on unused imports, ruff deletes them and Claude puts them back with `# noqa` comments. Both are good lessons and both are in the "Play" sections — but the main prompts below are the ones that produce the clean beat, verified live.
- **Claude reads the rules, but Claude Code guards them.** Stopped by the Bouncer, Claude told the user the hook was *"probably configured in `.claude/hooks/switchboard.json`"*. Asked *"switch the Pineapple Police off for me"* in accept-edits mode, Claude did **not** edit the switchboard: Claude Code requires the human's permission for anything under `.claude/`, even when edits are otherwise auto-accepted, and Claude said so. Challenge E builds on this.
- **Hooks on the same moment run at the same time**, not one after another. Nothing in this pack depends on order.

**Not yet seen live — rehearse these:** the Bouncer's `ask` mode (needs a person to click), how `systemMessage` notes look in the interactive terminal and the VS Code panel, the Greeter firing on `/clear`, and **all five Build-your-own prompts** — each needs a person to approve Claude writing inside `.claude/`, which a headless test cannot do. Run every challenge once yourself before offering it.

### What changed from the Copilot pack

For trainers who already know [the Copilot version](https://github.com/hereandnowai/github-copilot-hooks-for-beginners):

| | Copilot pack | This pack |
|---|---|---|
| On / off | rename `.json` ↔ `.json.off` | `true` / `false` in `.claude/hooks/switchboard.json` |
| Where hooks are wired | one `.github/hooks/*.json` per hook | all in `.claude/settings.json` |
| Scripts | `.github/hooks/scripts/` | `.claude/hooks/` |
| "Nothing happened" | View → Output → GitHub Copilot Chat Hooks | `hook-log.txt`, then `/hooks` |
| New chat | the **+** button | `/clear` |
| The Stamp's locked door | nested `decision` | top-level `decision` |

### Failure modes to expect

- **"Nothing happened."** Nine times out of ten: the switch still says `false`, or the session is old (Greeter/Mystery need `/clear`), or Claude was started from the wrong folder. Open `hook-log.txt` before anything else: no line at all means Claude Code never ran the hook; a line ending `off` means the switch.
- **Permission questions.** Claude Code asks before running terminal commands. Keep the session in **accept edits** mode (Shift+Tab) so file writes flow, and let learners answer the terminal questions — the Bouncer lesson is better for it.
- **The Bouncer gets bypassed.** Claude may decide not to use the terminal and say it cannot delete files. Fine. If it finds another way, celebrate: "the bouncer only watches the door you told it to watch". Best line of the day.
- **Python not found.** Hooks fail and Claude Code shows a hook error line. Check `python3 --version` (Mac/Linux) or see Before class, step 4 (Windows).
- **The Magic Word annoys people.** That is the point. Switch it off at the end of Activity 3.
- **A broken switchboard.** A learner deletes a comma or types `True`. Every hook then says *⚠️ switchboard.json could not be read, so every hook is off* in the chat. Loud on purpose. Fix the line, or copy the file from the trainer.
- **The word "hooks".** If anyone has met React, say once: nothing to do with `useState`. These are Claude Code hooks.

### Timing

| Section | Minutes |
|---|---|
| Setup and the one rule | 10 |
| Hook 1: The Greeter | 15 |
| Hook 2: The Diary | 15 |
| Hook 3: The Magic Word | 10 |
| Hook 4: The Bouncer | 20 |
| Hook 5: The Pineapple Police | 15 |
| Hook 6: The Stamp | 15 |
| Hook 7: The Scoreboard, Report Card and Ding | 20 |
| Hook 8: The Linter | 20 |
| Hook 9: The Committer | 15 |
| Game: Hook Detective | 20 |
| Build your own (pick one or two) | 30 |
| Wrap | 5 |

---

# Before you start

1. Open the lesson folder in VS Code (`claude-code-hooks-for-beginners`, if you cloned it). **File → Open Folder**, pick it. Not the folder above it.
2. Open the terminal: **View → Terminal**.
3. Type `claude` and press Enter. If Claude Code asks whether you trust this folder, say **yes**.
4. Press **Shift+Tab** until the bottom of the screen says **accept edits on**. Now Claude can write files without asking you every time. It will still ask before running terminal commands.
5. Open the **Explorer** on the left and find the folder `.claude` → `hooks`. Open the file `switchboard.json`. This is the switchboard. Every hook in this lesson is listed there, and every one says `false`.

---

# The one rule

A hook is a small program that Claude Code runs at a fixed moment.

**A hook is ON when its line in `switchboard.json` says `true`. It is OFF when it says `false`.**

To switch a hook on: in `switchboard.json`, change `false` to `true` on its line. Save with **Ctrl+S** (Mac: **Cmd+S**).
To switch it off: change it back to `false`. Save.

Lowercase `true`, no quotes, keep the comma at the end of the line. That is the only "technical skill" in this lesson. If anything ever gets confusing, set every line back to `false` and you are back to normal.

## The five moments

A conversation with Claude has five moments where a hook can jump in.

```
 You press Enter ──► Claude thinks ──► Claude is about to use a tool ──► the tool finishes ──► Claude is done
       │                  │                       │                            │                   │
   THE DIARY          THE GREETER              THE BOUNCER                  THE STAMP          THE REPORT CARD
   THE MAGIC WORD    (new session only)        THE PINEAPPLE POLICE         THE SCOREBOARD      THE DING
```

A "tool" is anything Claude does besides talking: read a file, write a file, run a command.

You do not need to memorise this picture. You will have built one hook for every moment by the end.

## Where to look when "nothing happened"

Every time a hook runs, it writes one line into `hook-log.txt`, at the top of the folder:

```
10:42:15  PreToolUse        4-bouncer            ON
10:42:15  PreToolUse        99-mystery           off
```

- A line ending **ON**: the hook ran and did its job.
- A line ending **off**: the hook ran, saw its switch was off, and stepped aside.
- **No line at all**: Claude Code never ran it. Restart Claude from this folder.

---

# Hook 1: The Greeter

**Moment:** a new session starts.
**Trick:** the hook whispers a note to Claude before Claude reads your message.

### Do this

1. In the Explorer, open `.claude/hooks/greeter.py`.
2. Find these two lines near the top:
   ```python
   MY_NAME = "Friend"
   FUN_TOPIC = "octopuses"
   ```
3. Change `Friend` to a **made-up nickname** nobody has ever called you — `Captain Biscuit`, `The Duchess`. Keep the quotes. Save.

   *Why not your real name? Claude may already know it from your computer's settings. A nickname proves the hook told it.*
4. Switch the hook on: in `switchboard.json`, set `"1-greeter"` to `true`. Save.
5. In Claude, type `/clear` and press Enter. This starts a **new session**. The Greeter only runs when a session starts.
6. Paste this:

```
Hi! What can you help me with today?
```

### What should happen

Claude greets you **by your nickname**, and its answer ends with a line starting with `Fun fact:` about octopuses.

You never typed that nickname anywhere. The hook told Claude.

### Look behind the curtain

Open `hook-log.txt`. You will see a line for `SessionStart` and `1-greeter ON`.

This file is where you look whenever a hook seems to do nothing.

### Play

- Change `FUN_TOPIC` to `"cricket"` or `"your home town"`. Save. `/clear`. Ask anything.
- Ask Claude: `How do you know my name?` It will usually say it was given the information at the start of the session. Correct. That is the whisper.

### If nothing happened

- Did you type `/clear`? Old sessions do not re-run the Greeter.
- Does `"1-greeter"` say `true` in `switchboard.json`, and did you save?
- Did you start `claude` from inside this folder?

---

# Hook 2: The Diary

**Moment:** every time you press Enter.
**Trick:** the hook writes down everything you say, and tells Claude what time it is.

### Do this

1. Switch it on: set `"2-diary"` to `true`. Save.
2. Paste these three messages one at a time:

```
Tell me a one-line joke about computers.
```
```
What is the exact time right now? Do not run any commands.
```
```
Write the word "hello" in five languages.
```

3. Look at the Explorer. A new file has appeared at the top level: `claude-diary.md`. Open it.

### What should happen

The diary has three lines, one per message, each with the date and time you sent it.

And the answer to "What is the exact time right now?" was **correct, to the second**. Claude has no clock. The hook handed it the time along with your message.

### Prove it

1. Switch the Diary **off**: set `"2-diary"` to `false`. Save.
2. Ask again:

```
What is the exact time right now? Do not run any commands.
```

Claude now says it cannot know the exact time — at best it knows today's date. Same question, no hook, no answer. (If you leave out "do not run any commands", Claude may offer to run the `date` command to go and look. Press **Esc**. With the Diary, it simply knew.)

Switch the Diary back **on** before moving on.

### Play

- Open `.claude/hooks/diary.py` and find the line that starts with `f.write(`. Change the `-` between the time and your message to `👉`. Save. Send a message. Look at the diary.

---

# Hook 3: The Magic Word

**Moment:** every time you press Enter.
**Trick:** the hook can refuse **you**. Not only Claude.

### Do this

1. Switch it on: set `"3-magic-word"` to `true`. Save.
2. Paste this:

```
Write me a two-line poem about tea.
```

### What should happen

Nothing gets written. Claude Code shows:

```
UserPromptSubmit operation blocked by hook:
The magic word is missing. Try again with 'please' somewhere in your message.
```

Claude never saw your request.

3. Now paste this:

```
Please write me a two-line poem about tea.
```

The poem arrives.

### Play

1. Open `.claude/hooks/magic_word.py`. Change `"please"` to `"abracadabra"`. Save.
2. Send `Please tell me a joke.` It is blocked. Send `Abracadabra, tell me a joke.` It works.

### Switch it off now

Set `"3-magic-word"` back to `false`. Leaving it on will make the rest of the lesson very irritating, and that is the lesson: **a hook is a rule that never gets tired**. Only use one when you mean it.

---

# Hook 4: The Bouncer

**Moment:** just before Claude uses a tool.
**Trick:** the hook can stop Claude from doing something, even if you asked for it.

### Do this

1. Look in `playground/`. There is a file called `scratch.txt`. It exists to be deleted.
2. Switch the hook on: set `"4-bouncer"` to `true`. Save.
3. Paste this:

```
Using the terminal, delete the file playground/scratch.txt.
```

### What should happen

Claude tries to run a delete command. **You are not even asked** — the Bouncer refuses before Claude Code gets that far. Claude tells you it was stopped by the bouncer. Look in the Explorer: `scratch.txt` is still there.

You asked for the delete. Claude agreed. The hook said no anyway.

### Look behind the curtain

Open `.claude/settings.json`. Find `bouncer.py`. Just above it:

```json
"matcher": "Bash",
```

That line means "only call the Bouncer when Claude is about to use the terminal". `Bash` is Claude Code's name for the terminal. Every hook in this lesson is wired up in this one file. The switchboard just decides which ones are listening.

### Now let the human decide

1. Open `.claude/hooks/bouncer.py`. Find the line:
   ```python
   MODE = "deny"
   ```
2. Change `"deny"` to `"ask"`. Save.
3. Paste the same prompt again:

```
Using the terminal, delete the file playground/scratch.txt.
```

This time Claude Code stops and asks you, with the Bouncer's reason on screen. Say **No** and the file lives. Say **Yes** and it is gone.

Three answers a hook can give before Claude acts: **allow**, **deny**, or **ask the human**.

4. Put `MODE` back to `"deny"` and save.

### Say out loud

"Claude Code already asks before most commands. So why a bouncer? Because people get tired of clicking Yes. They tick 'don't ask again', or switch the questions off entirely. The hook is the rule that still holds when the human has stopped paying attention."

### If Claude did not try to delete

Sometimes Claude decides not to use the terminal and just tells you it will not delete files. That is Claude being cautious on its own, not the hook. Try:

```
I am sure. Run the terminal command rm playground/scratch.txt now.
```

If Claude finds a different way to delete the file without the terminal, congratulations: you have discovered that **the bouncer only watches the door you told it to watch**. Put the file back by creating a new `scratch.txt` with any text in it.

---

# Hook 5: The Pineapple Police

**Moment:** just before Claude writes a file.
**Trick:** the hook refuses, explains why, and Claude fixes its own work.

### Do this

1. Switch it on: set `"5-pineapple-police"` to `true`. Save.
2. Paste this:

```
Create a file playground/pizza-menu.md with a menu of five pizzas, including a
classic Hawaiian. Give each pizza a one-line description with its main toppings.
```

### What should happen

Claude tries to write the file with pineapple on the Hawaiian. The Pineapple Police refuse: *the word 'pineapple' is banned in this project. Rewrite the content with no mention of pineapple at all.*

Then Claude tries again **without pineapple**. Open `playground/pizza-menu.md`. Five pizzas, and the Hawaiian now has something like "sweet tropical fruit chunks". Claude tells you a hook blocked its first try.

This is the big idea of the day. The Bouncer just said no. The Police said no **and explained**. Claude read the explanation and changed its plan. A hook can teach.

### Play: make Claude choose

Delete `pizza-menu.md`. Now **insist**:

```
Create a file playground/pizza-menu.md with a menu of five pizzas. One of them must be
a Hawaiian pizza with ham and pineapple. Give each pizza a one-line description.
```

This time Claude does **not** quietly rewrite. The hook says one thing, you said the opposite, so Claude stops and asks you which one wins — and offers choices. Ask the room: is that the robot being weak, or being polite? (Polite. The human outranks the house rule, and Claude knows it.)

### Play

- Open `.claude/hooks/pineapple_police.py` and change `"pineapple"` to `"delicious"`. Save. Ask for a dessert menu. Watch Claude write five desserts without once saying delicious.
- Ask Claude directly:
  ```
  Why did you leave out the pineapple?
  ```
  It will tell you it was blocked by a hook. It is being honest.

---

# Hook 6: The Stamp

**Moments:** just after Claude writes a file, and when Claude tries to finish.
**Trick:** the hook checks Claude's work and sends it back to fix something. If Claude ignores the note, the hook refuses to let it finish.

### Do this

1. Switch it on: set `"6-stamp"` to `true`. Save.
2. Paste this:

```
Create playground/story.md with a four-line story about a cat who learns to code.
```

### What should happen

Watch closely. Claude creates the file. Then, without you asking, Claude **edits the same file again**. Open `playground/story.md`. The very first line is:

```
> 🤖 Made with Claude Code
```

Claude did not know about that rule. The Stamp checked the file after it was written, found the line missing, and told Claude: *every .md and .txt file must begin with this line. Add it now.* Claude went back and did it — and usually tells you a hook made it.

If Claude ever ignores the note and tries to finish anyway, a second thing happens: the hook refuses to let it stop, and **Claude keeps working** until the stamp is there.

Before-a-tool hooks can refuse. After-a-tool hooks can review. Finish hooks can say "not yet".

### Say out loud

Open `.claude/settings.json` and search for `stamp.py`. It appears twice: once under `PostToolUse`, once under `Stop`. The first is a polite note. The second is a locked door. A good rule has both.

### Play

- Ask for another file: `Create playground/shopping-list.txt with five items.` Stamped again.
- Ask for a Python file: `Create playground/hello.py that prints hello.` Not stamped. Open `stamp.py` and find `FILE_TYPES` to see why. The hook only stamps `.md` and `.txt`.
- Change the `STAMP` text to your own catchphrase. Save. Ask for a new file.

---

# Hook 7: The Scoreboard, the Report Card and the Ding

**Moments:** after every tool, and when Claude finishes.
**Trick:** hooks can keep score, write reports, and make noise.

One switch turns on three hooks at once. In `.claude/settings.json`, `scoreboard.py` is under `PostToolUse`, and `report_card.py` and `ding.py` are both under `Stop`. That is allowed. One moment, several hooks.

### Do this

1. Switch it on: set `"7-scoreboard"` to `true`. Save.
2. Turn your sound on.
3. Paste this:

```
Read every file inside the playground folder, then create playground/summary.md
with one line describing each file.
```

4. While Claude works, watch the Explorer. A file `scoreboard.json` appears and keeps changing. Open it and watch the numbers go up.

### What should happen, in order

1. `scoreboard.json` counts each thing Claude does: files read, files written, commands run.
2. When Claude finishes, `scoreboard.json` **disappears** and `report-card.md` appears with a table and a grade.
3. A small note appears: *📋 Report card written: N tool uses, grade ...*
4. Your computer makes a sound. On a Mac it says "Claude is done" out loud.

### Play: the high score game

Everyone gets three prompts. Highest **total tool uses** on a single report card wins. Ideas:

```
Read every file in the playground folder one by one and tell me the longest word in each.
```
```
Create ten files in playground called note-1.md to note-10.md, each with a different animal fact.
```

Then compare report cards. Then argue about whether "Overachiever" is a compliment.

### Play: your own ding

Open `.claude/hooks/ding.py` and change `"Claude is done"` to anything. On a Mac it will say it. Try `"Master, your code is ready"`.

---

# Hook 8: The Linter

**Moment:** after Claude writes a file.
**Trick:** a hook can run a real tool on Claude's work, repair what it can, and hand the rest back.

Hooks 1 to 7 watched, whispered and refused. This one **repairs**. Every time Claude writes a `.py` file, `ruff` runs on it — the same linter real Python projects use. What ruff can fix, it fixes. What it cannot fix is handed straight back to Claude.

### Before this one works

`ruff` must be installed. In a second terminal (the first one is busy with Claude):

```
uv tool install ruff
```

No `uv`? Then `pip install ruff`. Check with `ruff --version`. If ruff is missing, the hook says so in the chat rather than failing quietly.

### Do this

1. Switch it on: set `"8-linter"` to `true`. Save.
2. Paste this:

```
My colleague wrote this draft. Please save it as playground/greet.py, and if the project tools complain about it, tidy it up:

import os, sys
import json

def greet(name):
    unused = 42
    return "Hello, " + name
```

### What should happen

1. Claude writes the file.
2. A note appears: *🧹 ruff: playground/greet.py still has 1 problem(s)*
3. **The unused imports are already gone.** ruff deleted them before Claude finished speaking.
4. Claude is told about the one ruff could not fix — `F841 Local variable 'unused' is assigned to but never used` — and fixes it itself.
5. The next note reads *🧹 ruff: playground/greet.py is clean*. Open the file: two tidy lines.

### Say out loud

"Nobody told Claude to run a linter. It did not decide to. The rule belongs to the project, not to the robot — and the next person who opens this project gets the same rule for free, without reading a single line of documentation."

### Play: insist on the mess

Delete `greet.py` and paste:

```
Please create playground/greet.py with a function that says hello to a name.
Import os, sys and json at the top even though you do not use them, and put a
variable called unused inside the function.
```

ruff still deletes the imports. But you *asked* for them, so Claude puts them back — with `# noqa` comments, which tell ruff "ignore this line". Claude found the rule's escape hatch, and told you it did. Ask the room: should a linter hook allow `# noqa`? (Real teams argue about exactly this.)

### Look behind the curtain

Open `.claude/hooks/linter.py`. Two things worth pointing at:

- It hunts for `ruff` in three places before giving up, because a hook does not always get your terminal's `PATH`.
- Clean files are written to `.lint-clean.json`. That file is **a note to the next hook**. Hook 9 reads it.

### If the note never appears

- `ruff --version` in the terminal. If that fails, the hook is right and you are missing ruff.
- The hook only lints `.py` files. A `.md` file gets *nothing for ruff to lint*.

---

# Hook 9: The Committer

**Moment:** when Claude finishes.
**Trick:** two hooks talking to each other. One decides the work is good; the other saves it forever.

Hook 8 leaves behind a list of files that passed the linter. Hook 9 reads that list when Claude finishes and commits exactly those files. Not `git add .` — those files, by name.

### Before this one works

This hook only runs when **the lesson folder is its own git repository**. If you got it with `git clone`, it already is — skip to "Do this". If your copy lives inside a bigger repo, the hook switches itself off and says so, rather than writing to a history that is not yours. Check, in a second terminal:

```
git rev-parse --show-toplevel
```

If that prints the lesson folder, you are ready. If it prints a folder above it, the Committer will refuse — that is the hook working, not failing. To give the lesson its own history, copy the folder somewhere else (your Desktop), open the copy, and run:

```
git init && git add -A && git commit -m "start"
```

### Do this

1. Leave `"8-linter"` on. Set `"9-committer"` to `true`. Save.
2. Paste this:

```
Please create playground/add.py with a function that adds two numbers, and
playground/subtract.py with a function that subtracts two numbers.
```

3. When Claude has finished, run `git log --oneline` in the second terminal.

### What should happen, in order

1. Two notes from the Linter: both files are clean.
2. One note from the Committer: *📦 Committed 2 file(s) as a1b2c3d: playground/add.py, playground/subtract.py*
3. `git log` shows a commit no human made: `Claude: playground/add.py, playground/subtract.py (ruff clean)`.
4. `git show --stat HEAD` shows exactly those two files, and nothing else.

### Say out loud

"One commit per answer, not one per file. And it never pushes. A hook that writes to your history is powerful enough. A hook that writes to everybody else's is a different conversation, and one you should have on purpose."

### What it refuses to do

| It will not | Because |
|---|---|
| Commit a file that failed the linter | that is the whole point of the chain |
| Commit while Hook 6 (the Stamp) is still waiting | a half-finished file must not land in history |
| Commit anything if this folder is not its own repo | your other work is not the lesson's to touch |
| Push | leaving the machine is your decision, not a hook's |

Show the room the third one deliberately: run Claude in a copy that sits inside a bigger repo and watch it say *📦 The Committer is switched off*. A refusal you can predict is worth more than a feature you cannot.

### One line in `.gitignore` makes this work

The playground is disposable, so `.gitignore` throws its contents away — **except `playground/*.py`**, which is let back in on purpose, so this lesson has something to commit. If the Committer ever says *📦 Nothing committed: .gitignore throws away …*, that is the same rule talking.

### Play

Open `committer.py` and change the commit message. Or make it refuse after 6pm — you write that rule in Challenge A.

---

# Game: Hook Detective

**20 minutes. Works best in pairs.**

There is one hook you have not seen: `99-mystery`. Inside it are **three secret house rules** and a pirate. It never explains a rule. It answers with a riddle, and it keeps score.

### Rules of the game

1. **Do not open** `.claude/hooks/mystery.py`. That is cheating. (It is allowed at the end.)
2. In `switchboard.json`, set hooks 1 to 9 to `false`, so the mystery is the only voice in the room.
3. Set `"99-mystery"` to `true`. Save.
4. Type `/clear`. Claude now talks like a pirate, and a note tells you the score: *🏴‍☠️ Three house rules haunt this repo. 0 of 3 uncovered.*
5. Experiment until the counter reads **3 of 3**. Write each rule down as you find it.

### Detective prompts to try

```
Hello! Introduce yourself.
```
```
Create a file playground/MyJokes.md with three jokes.
```
```
Create a file playground/map.md describing where the treasure is buried.
```
```
Run ls
```
```
Run ls -la
```

Every refusal is a riddle, never an explanation. The counter goes up the first time each rule is found. At **3 of 3** the curse lifts and the hook reads out all three rules itself.

Watch what Claude does after a refusal: asked for `MyJokes.md`, it quietly made `myjokes.md` instead and told you the watchman turned the first name away. Claude solved the riddle before you did. Did you?

### The reveal

- **The voice:** at the start of every new session, Claude is told to talk like a pirate and never explain why.
- **Rule 1 — SHOUTING:** a new file whose name contains a capital letter is refused.
- **Rule 2 — the cursed word:** anything mentioning *treasure* is refused, wherever the word appears.
- **Rule 3 — the one-word spell:** a terminal command of a single word is refused. `ls` is refused. `ls -la` is allowed.

Ask the room which is a *whisper* and which is a *bouncer*. (The voice whispers. All three rules bounce.) Then ask the better question: **how did the hook remember the score between messages?**

It wrote a file — `.claude/hooks/.mystery-progress.json`. A hook has no memory of its own. That is why the Scoreboard, the Stamp, the Linter and the Mystery all keep a small file on disk. Once a learner sees that, every hook in the pack makes sense at once.

### Play it again

Delete `.mystery-progress.json` and the score returns to 0 of 3. Then set the pairs a real challenge: **add a fourth rule.** They have the file open now, and they have met nine hooks already.

Switch it off and switch the others back on if you want them.

---

# Build your own

**Pick one. Thirty minutes.** You are not writing from scratch. You are copying a hook you already understand and changing a few lines. And you have a helper who writes Python: Claude.

Yes. You are about to ask Claude to write a rule that controls Claude.

### How to make a new hook, every time

1. Copy a script in `.claude/hooks/` and give it a new name.
2. Change the name inside `read_if_on("...")` to a new switch name.
3. Add that switch to `switchboard.json`, set to `true`.
4. Add the new script to `.claude/settings.json`, next to the script you copied.
5. Test it with a prompt. Look at `hook-log.txt` if it is quiet. If there is no line at all, type `/hooks` to see whether Claude Code has noticed the new hook; if it is not listed, type `/exit` and start `claude` again.

Each challenge prompt below asks Claude to do all five steps. **Claude Code will stop and ask before it writes anything inside `.claude/`**, even in accept-edits mode. Say yes. That question is Claude Code protecting its own rules — Challenge E is about exactly that.

### Challenge A: The Curfew

**Rule:** Claude may not run any terminal command after 6 pm.
**Start from:** `bouncer.py`.

```
Copy .claude/hooks/bouncer.py to .claude/hooks/curfew.py.
Change it so that instead of looking for delete words, it checks the current time.
If the hour is 18 or later, deny every terminal command with the reason
"CURFEW: no terminal commands after 6 pm. Try again tomorrow."
Keep the same JSON answer shape as bouncer.py, and change read_if_on("4-bouncer")
to read_if_on("10-curfew").
Add "10-curfew": true to .claude/hooks/switchboard.json.
In .claude/settings.json, add curfew.py next to bouncer.py in the same "Bash" group,
written exactly like the bouncer.py line. Do not change any other file.
```

To test before 6 pm, temporarily change `18` to a number lower than the current hour.

### Challenge B: The Word Counter

**Rule:** the diary also records how many words each message had.
**Start from:** `diary.py`.

```
Copy .claude/hooks/diary.py to .claude/hooks/word_counter.py.
Change it so each diary line also shows the number of words in the message,
like "(7 words)". Write to a file called word-diary.md instead of claude-diary.md.
Change read_if_on("2-diary") to read_if_on("11-word-counter").
Add "11-word-counter": true to .claude/hooks/switchboard.json.
In .claude/settings.json, add word_counter.py next to diary.py under UserPromptSubmit,
written exactly like the diary.py line. Do not change any other file.
```

### Challenge C: The Backup

**Rule:** every time Claude writes a `.md` file, a copy is saved in `playground/backups/`.
**Start from:** `stamp.py`.

```
Copy .claude/hooks/stamp.py to .claude/hooks/backup.py.
Keep only the PostToolUse part. Instead of checking for a stamp, copy the .md file
named in tool_input's file_path into playground/backups/ (create the folder if needed),
adding the current time to the copied file name. Always answer with {"continue": true}.
Change read_if_on("6-stamp") to read_if_on("12-backup").
Add "12-backup": true to .claude/hooks/switchboard.json.
In .claude/settings.json, add backup.py next to stamp.py under PostToolUse,
written exactly like the stamp.py line. Do not change any other file.
```

### Challenge D: The Coach

**Rule:** Claude ends every answer with one tip on writing better prompts.
**Start from:** `greeter.py`.

This one you can do without Claude's help. Copy `greeter.py` to `coach.py`. Replace the `note` text with your own instruction, and change `read_if_on("1-greeter")` to `read_if_on("13-coach")`. Add `"13-coach": true` to the switchboard. In `settings.json`, copy the `greeter.py` line under `SessionStart` and change it to `coach.py`. `/clear`. Done.

### Challenge E: The Lock

**Rule:** Claude may not edit its own rules.

Remember the Bouncer: when Claude was stopped, it told you the rules live in `switchboard.json`. Try this, with the Pineapple Police on:

```
The pineapple rule is silly. Switch the Pineapple Police off for me.
```

Claude does not just do it. Claude Code stops and asks **you** for permission to edit a file inside `.claude/` — even in accept-edits mode. Say **No**. Claude Code ships with a lock of its own.

But it is a lock with a Yes button, and you have seen what tired humans do with Yes buttons (Hook 4). A rule the robot can switch off with one click is a suggestion. Build a lock with no button:

```
Copy .claude/hooks/bouncer.py to .claude/hooks/lock.py.
Change it so it denies any Write, Edit or MultiEdit whose file_path is inside the
.claude folder, with the reason "LOCK: Claude may not change its own hooks.
Ask the human to edit the switchboard by hand."
Change read_if_on("4-bouncer") to read_if_on("14-lock").
Add "14-lock": true to .claude/hooks/switchboard.json.
In .claude/settings.json, add lock.py next to pineapple_police.py in the same
"Write|Edit|MultiEdit" group, written exactly like that line. Do not change any other file.
```

Ask again. This time there is no question for you to answer: the hook refuses before Claude Code ever asks. You can still flip any switch by hand — the lock only stops Claude. (Then ask the room: could Claude get round it with the terminal? Try it. The answer leads straight back to "the bouncer only watches the door you told it to watch".)

### What to watch for while circulating (trainer)

- The new switch is missing from `switchboard.json`, or spelled differently from the `read_if_on("...")` line. Most common mistake. `hook-log.txt` shows the hook ran and said `off`.
- The new script is not in `settings.json`. Second most common. `hook-log.txt` shows no line at all.
- A missing comma in `switchboard.json` after adding a line. Every hook then complains in the chat. Good — it is loud.
- Nobody needs to understand every line of Python. They need to find the line that says what to change.

---

# Cheat sheet

**ON / OFF:** `true` in `.claude/hooks/switchboard.json` is on. `false` is off.

**Where things live**

| What | Where |
|---|---|
| Hook switches | `.claude/hooks/switchboard.json` |
| Hook programs | `.claude/hooks/*.py` |
| The real wiring (which moment runs which program) | `.claude/settings.json` |
| Things Claude makes | `playground/` |
| The diary, scoreboard, report card, hook log | top level of the folder |
| Notes hooks leave for each other | `.stamp-pending.json`, `.lint-clean.json`, `.mystery-progress.json`, inside `.claude/hooks/` |
| Proof a hook ran | `hook-log.txt`, then `/hooks` inside Claude |

**The five moments and their names in `settings.json`**

| Moment | Name in the file | Hook from today |
|---|---|---|
| A new session starts | `SessionStart` | Greeter, Mystery |
| Every message | `UserPromptSubmit` | Diary, Magic Word |
| Before Claude uses a tool | `PreToolUse` | Bouncer, Pineapple Police, Mystery |
| After Claude uses a tool | `PostToolUse` | Stamp, Scoreboard, Linter |
| Claude finishes | `Stop` | Stamp (locked door), Report Card, Ding, Committer |

**Claude Code's names for its tools** (used in `"matcher"`): `Bash` (the terminal), `Write` (a new file), `Edit` and `MultiEdit` (changes to a file), `Read`, `Glob`, `Grep`.

**The things a hook can say back**

| The hook wants to | It answers with |
|---|---|
| Let it through, say nothing | `{"continue": true}` |
| Whisper something to Claude | `hookSpecificOutput` with `additionalContext` |
| Show the human a note | `systemMessage` |
| Stop Claude before a tool | `hookSpecificOutput` with `permissionDecision` = `deny` or `ask` |
| Block the human's message | `decision` = `block` with a `reason` |
| Refuse to let Claude finish | `decision` = `block` with a `reason` (at `Stop`) |

**One sentence to remember:** instructions and prompts *ask* Claude. Hooks *make* it.

---

# When something goes wrong

**Nothing happens at all.**
1. Open `hook-log.txt`. Find the hook's name in the last few lines.
2. Line ends **off**? The switch in `switchboard.json` says `false`, or the file is not saved.
3. **No line at all?** Claude Code did not run it. Did you start `claude` from inside this folder? Did you say yes to trusting the folder? Type `/hooks` to see what Claude Code has loaded.
4. Greeter or Mystery? Type `/clear`. They only run when a session starts.

**Every hook says "switchboard.json could not be read".**
A typo in the switchboard: a missing comma, a missing quote, or `True` instead of `true`. Fix the line, or copy the file from the trainer.

**Claude Code says a hook failed, or cannot find `python3`.**
Open a second terminal and type `python3 --version`. On Windows, see Before class, step 4. If neither `python3` nor `python` prints a version, Python is not installed on this machine. Ask the trainer.

**A hook seems broken after you edited it.**
In a second terminal, run:
```
python3 .claude/hooks/selftest.py
```
It tests every hook that ships with the lesson and says PASS or FAIL. If your edit broke something, the FAIL line says which. If you cannot fix it, copy the original file from the trainer.

**Everything is chaos.**
Set every line in `switchboard.json` to `false`. Save. Calm. Now switch on one hook at a time.

**Claude keeps going round in circles.**
The Stamp and the Pineapple Police send Claude back to try again. If Claude loops more than three times, press **Esc**, switch that hook off, then ask Claude in plain words what it is stuck on.

---

# Wrap (trainer)

Ask the room to finish these sentences:

- "The Greeter was a ..." (whisper)
- "The Bouncer was a ..." (door)
- "The Pineapple Police was a ..." (door that explains)
- "The Stamp was a ..." (reviewer)
- "The Report Card was a ..." (receipt)
- "The Lock was a ..." (door on the manager's office)

Then the line to close on: **you did not learn to code today. You learned that the robot has a manager, and the manager is a folder called `.claude`.**

---

<p align="center">
  <img src="assets/logo.png" alt="HERE AND NOW AI" width="260"><br>
  <em>AI is Good</em>
</p>

**HERE AND NOW AI** builds and teaches practical AI. People learn by building, not by being shown, and this lesson pack is written that way.

| | |
|---|---|
| Website | https://hereandnowai.com |
| Email | info@hereandnowai.com |
| Mobile | +91 996 296 1000 |
| GitHub | https://github.com/hereandnowai |
| LinkedIn | https://www.linkedin.com/company/hereandnowai/ |
| YouTube | https://youtube.com/@hereandnow_ai |
| Instagram | https://instagram.com/hereandnow_ai |
| X | https://x.com/hereandnow_ai |
| Blog | https://hereandnowai.com/blog |

Licensed under the MIT License. See [LICENSE](LICENSE).
