# Mini Shell in Python

A simple Unix-style command-line shell written in Python.

**Course:** COSC-3411 — System Programming
**Project:** Mini Shell in Python (Lambda topic)

## Team Members

| Name | Student ID |
|------|------------|
| Ali Almousa | 201902641 |
| Hassan Albrahim | 202001844 |
| Ahmad J Alsahan | 202201041 |
| Abdulaziz Almotairi | 202200065 |

---

## Features

### Built-in Commands

| Command | Description |
|---------|-------------|
| `cd [dir]` | Change directory. No argument goes to the home folder. |
| `pwd` | Print the current working directory. |
| `echo [args]` | Print arguments separated by spaces. |
| `clear` | Clear the terminal screen. |
| `history` | Show every command typed in this session. |
| `help` | Show the list of built-in commands. |
| `exit` | Leave the shell. |

### External Commands

Anything that is not a built-in is executed as an external program through `subprocess`. So commands like `ls`, `cat`, `grep`, `date`, `mkdir`, `python3`, and so on all work normally.

### Error Handling

- Typing a command that does not exist prints `command not found` instead of crashing.
- Typing `cd` into a folder that does not exist prints `No such file or directory`.
- Pressing **Ctrl-C** at the prompt does not kill the shell — it just shows a fresh prompt.
- Pressing **Ctrl-D** exits the shell cleanly.

---

## Requirements

- Python **3** (no third-party libraries needed)
- Linux or macOS (we tested on Kali Linux)

Check your Python version:

```bash
python3 --version
```

---

## Installation and Usage

Clone the repository and run the shell:

```bash
git clone https://github.com/ABCC-wq/Systems-Programming-Gamma.git
cd Systems-Programming-Gamma
python3 minishell.py
```

You should see the prompt:

```
Mini Shell - type 'help' for commands
~$
```

Type `help` to see the list of built-in commands or `exit` to leave.

---

## Example Session

```
~$ pwd
/home/kali
~$ echo hello world
hello world
~$ cd /tmp
/tmp$ ls
some_file.txt  another_folder
/tmp$ cd
~$ history
1  pwd
2  echo hello world
3  cd /tmp
4  ls
5  cd
6  history
~$ xyz
xyz: command not found
~$ exit
Bye!
```

---

## How It Works

The shell runs in a simple loop:

1. **Read** — show a prompt and use `input()` to read a line from the user.
2. **Parse** — split the line into the command name and its arguments using `line.split()`.
3. **Dispatch** — if the command matches one of our built-ins (`cd`, `pwd`, `echo`, etc.), call the matching code directly. Otherwise, run it as an external program with `subprocess.run()`.
4. **Loop** — go back to step 1 until the user types `exit`.

### Why Built-ins Cannot Be External

Some commands, like `cd` and `exit`, **must** be handled inside the shell. If `cd` ran as a subprocess, that subprocess would change its own directory and immediately exit — our shell's directory would not change. So these are coded directly inside the shell.

### Why subprocess Instead of os.system or eval

- `eval()` would let users run arbitrary Python code — that's a security hole.
- `os.system()` hands the command off to `/bin/sh`, which defeats the point of writing our own shell.
- `subprocess.run()` runs the program directly without an intermediate shell, which is safer and gives us proper control over errors.

---

## Limitations

Because the assignment asked for a basic shell, the following are not supported:

- **Pipes** (`ls | grep py`)
- **Redirection** (`> output.txt`, `< input.txt`)
- **Variable expansion** — `echo $HOME` prints the literal text `$HOME`, not the value.
- **Quoted arguments** — `echo "hello world"` includes the quotes (we use basic `.split()`).
- **Background jobs** (`sleep 10 &`)
- **Command chaining** (`cmd1 && cmd2`)

---

## Project Files

```
Systems-Programming-Gamma/
├── minishell.py        # the shell code
├── README.md           # this file
├── .gitignore
├── Report.docx         # full project report
└── Presentation.pptx   # presentation slides
```
