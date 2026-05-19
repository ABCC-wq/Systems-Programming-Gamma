# Mini Shell in Python

A simple Unix-style command-line shell written in Python.

**Course:** COSC-3411 System Programming
**Project:** Mini Shell in Python (Lambda topic)
**Team:** Gamma

---

## Features

### Built-in commands (handled inside the shell)

| Command | Description |
|---------|-------------|
| `cd [dir]` | Change directory. No argument goes to `$HOME`. `cd -` returns to the previous directory. Supports `~` and environment variables in the path. |
| `pwd` | Print the current working directory. |
| `echo [-n] [args...]` | Print arguments separated by spaces. `-n` suppresses the trailing newline. |
| `exit [code]` | Leave the shell with an optional exit code (default 0). |
| `help` | Show the list of built-in commands. |
| `clear` | Clear the screen. |
| `env` | Print all environment variables. |
| `export VAR=VALUE` | Set an environment variable (so child processes inherit it). |
| `unset VAR` | Remove an environment variable. |
| `history` | Show every command typed during this session. |

### External commands

Anything that isn't a built-in is executed as an external program through `subprocess`. So `ls`, `cat`, `grep`, `python3`, `mkdir`, and so on all work.

Arguments support quoted strings via Python's `shlex` module:
```
echo "hello world"
grep 'foo bar' file.txt
```

### Signal handling

- **Ctrl-C** while at the prompt cancels the current line and shows a fresh prompt (instead of killing the shell).
- **Ctrl-C** while an external command is running kills only that command, not the shell.
- **Ctrl-D** at an empty prompt exits the shell cleanly.

---

## Requirements

- Python **3.6 or later** (standard library only — no third-party packages)
- Linux or macOS (the shell uses Unix-specific features like `os.uname()` and `preexec_fn`)

Check your Python version:
```bash
python3 --version
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ABCC-wq/Systems-Programming_101-Gamma.git
   cd Systems-Programming_101-Gamma
   ```

2. (Optional) Make the script directly executable:
   ```bash
   chmod +x minishell.py
   ```

That's it — no dependencies to install.

---

## Usage

Start the shell:
```bash
python3 minishell.py
```

You'll see a colored prompt similar to a real shell:

```
Mini Shell (Python) — type 'help' for built-in commands, 'exit' to quit.
user@hostname:~/projects$
```

### Example session

```
user@hostname:~$ pwd
/home/user
user@hostname:~$ echo hello world
hello world
user@hostname:~$ cd /tmp
user@hostname:/tmp$ pwd
/tmp
user@hostname:/tmp$ cd -
/home/user
user@hostname:~$ ls
Desktop  Documents  Downloads
user@hostname:~$ export GREETING=hi
user@hostname:~$ env | grep GREETING
GREETING=hi
user@hostname:~$ unset GREETING
user@hostname:~$ history
     1  pwd
     2  echo hello world
     3  cd /tmp
     4  pwd
     5  cd -
     6  ls
     7  export GREETING=hi
     8  env | grep GREETING
     9  unset GREETING
    10  history
user@hostname:~$ exit
exit
```

---

## Known Limitations (Intentional — "Basic" Scope)

This is a **basic** mini shell. The following are intentionally **not** supported:

- **Pipes** (`ls | grep py`) — would need `os.pipe()` and process chaining.
- **Redirection** (`> output.txt`, `< input.txt`, `2>&1`).
- **Variable expansion in arguments** — typing `echo $HOME` prints the literal string `$HOME`, not the home directory. Use `env` to inspect variables. (Built-in `cd` does expand `~` and `$VAR` in its argument, though.)
- **Background jobs** (`sleep 10 &`).
- **Command chaining** (`cmd1 && cmd2`, `cmd1 ; cmd2`).
- **Globbing** (`*.txt` is passed literally to the program; many programs like `ls` do their own globbing, so `ls *.txt` still works for them).

Adding any of these would push the project from "basic" to "medium/advanced" scope, which the team chose not to do for time reasons.

---

## Project Structure

```
Systems-Programming_101-Gamma/
├── minishell.py     # the entire shell (built-ins + external command runner)
└── README.md        # this file
```

---

## How It Works (Design Overview)

The shell runs a classic **REPL** (Read–Eval–Print Loop):

1. **Read** — `input()` shows a prompt and waits for a line of text.
2. **Parse** — `shlex.split()` splits the line into tokens, respecting single and double quotes. (`shlex` is Python's standard library lexer for shell-like syntax.)
3. **Dispatch** — the first token is looked up in a built-in command table:
   - If it's a built-in, the corresponding Python method runs **inside the shell process**. This is essential for commands like `cd` and `export`, because they must change the shell's own state, not a child's.
   - Otherwise, `subprocess.run()` is called to fork a new process, exec the program, and wait for it to finish.
4. **Loop** — go back to step 1 until the user types `exit` or hits Ctrl-D.

### Why not use Python's `os.system()`?

`os.system()` runs commands through `/bin/sh`, which would defeat the whole purpose — we'd be wrapping a real shell instead of building one. `subprocess.run([cmd] + args)` runs the program directly without any shell in between, so we have full control over parsing, signals, and exit codes.

### Why built-ins must be built in

A separate process cannot change the parent's working directory. If `cd /tmp` were an external command, it would change the directory of a child process that immediately exits, leaving the shell's own directory untouched. The same applies to `export`, `unset`, and `exit`. These commands **must** be handled by the shell itself.

### Signal handling

When the shell starts, it tells the kernel to **ignore SIGINT** (Ctrl-C) in the shell process via `signal.signal(SIGINT, SIG_IGN)`. This way, hitting Ctrl-C at the prompt doesn't kill the shell — the input is just cancelled and a new prompt appears.

For external commands, we pass `preexec_fn=lambda: signal.signal(SIGINT, SIG_DFL)` to `subprocess.run()`. That function runs **inside the child process before exec**, restoring the default Ctrl-C behavior so the user can interrupt a long-running program (like `sleep 60`) without killing the shell.

---

## Demo Tips

Good things to demonstrate during the presentation:

1. Show the prompt updating when you `cd` around.
2. Run a few external commands: `ls`, `cat README.md`, `date`.
3. Show `cd -` jumping back to the previous directory.
4. Show `export`/`env`/`unset` together.
5. Show `history` listing what you've typed.
6. Trigger an error: type `xyznotreal` to show the "command not found" message.
7. Press Ctrl-C at a prompt to show the shell doesn't die.
8. Run `sleep 30`, then press Ctrl-C to kill only the child.

---

## Team Members

- Member 1
- Member 2
- Member 3
- Member 4
- Member 5

*(Fill in your team members' names before submitting.)*

---

## License

This project was developed for educational purposes as part of COSC-3411.
