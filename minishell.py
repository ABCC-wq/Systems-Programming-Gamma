#!/usr/bin/env python3
"""
Mini Shell in Python
COSC-3411 System Programming - Gamma Team (Lambda topic)

A simple Unix-style shell written in Python. It supports:

  BUILT-IN COMMANDS (handled by the shell itself):
    cd [dir]       change current directory (no arg => HOME)
    pwd            print the current working directory
    echo [args...] print arguments separated by spaces
    exit [code]    leave the shell (default exit code 0)
    help           show built-in commands
    clear          clear the screen
    env            print all environment variables
    export VAR=VAL set an environment variable
    unset VAR      remove an environment variable
    history        show previously typed commands

  EXTERNAL COMMANDS:
    Anything else is executed as an external program using subprocess
    (e.g. ls, cat, grep, python3, ...). Arguments support quoted strings
    like:   echo "hello world"   or   grep 'foo bar' file.txt

The shell handles Ctrl-C cleanly (cancels the current line instead of
killing the shell) and Ctrl-D to exit.

Usage:
    python3 minishell.py
"""

import os
import sys
import shlex
import subprocess
import signal


# -----------------------------------------------------------------------------
# Shell state (kept in a single object so built-ins can modify it)
# -----------------------------------------------------------------------------

class Shell:
    def __init__(self):
        self.history = []         # list of every command line the user typed
        self.last_exit_code = 0   # exit code of the last command (like $?)

        # Map built-in names to the methods that implement them.
        # Adding a new built-in = adding one entry here + one method below.
        self.builtins = {
            'cd':      self.builtin_cd,
            'pwd':     self.builtin_pwd,
            'echo':    self.builtin_echo,
            'exit':    self.builtin_exit,
            'help':    self.builtin_help,
            'clear':   self.builtin_clear,
            'env':     self.builtin_env,
            'export':  self.builtin_export,
            'unset':   self.builtin_unset,
            'history': self.builtin_history,
        }

    # -------------------------------------------------------------------------
    # PROMPT
    # -------------------------------------------------------------------------

    def get_prompt(self):
        """Build a shell prompt that shows user@host and current directory."""
        user = os.environ.get('USER', 'user')
        try:
            host = os.uname().nodename.split('.')[0]
        except AttributeError:
            host = 'localhost'   # safety net (os.uname doesn't exist on Windows)

        cwd = os.getcwd()
        # Replace the home directory with ~ to keep the prompt short
        home = os.path.expanduser('~')
        if cwd.startswith(home):
            cwd = '~' + cwd[len(home):]

        # ANSI colors: green for user@host, blue for path
        return f"\033[1;32m{user}@{host}\033[0m:\033[1;34m{cwd}\033[0m$ "

    # -------------------------------------------------------------------------
    # MAIN LOOP (REPL: Read - Eval - Print - Loop)
    # -------------------------------------------------------------------------

    def run(self):
        """Read commands from the user and execute them until exit."""
        # Ignore Ctrl-C in the shell process itself.
        # We'll catch KeyboardInterrupt below to cancel the current input line.
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        print("Mini Shell (Python) — type 'help' for built-in commands, 'exit' to quit.")

        while True:
            try:
                line = input(self.get_prompt())
            except KeyboardInterrupt:
                # User pressed Ctrl-C: cancel the current line, fresh prompt
                print()
                continue
            except EOFError:
                # User pressed Ctrl-D: graceful exit
                print()
                break

            line = line.strip()
            if not line:
                continue  # empty line, just show a new prompt

            self.history.append(line)

            # Parse the line into a list of tokens (handles quotes correctly)
            try:
                tokens = shlex.split(line)
            except ValueError as e:
                # e.g. unmatched quote
                print(f"minishell: syntax error: {e}", file=sys.stderr)
                self.last_exit_code = 2
                continue

            if not tokens:
                continue

            self.execute(tokens)

    # -------------------------------------------------------------------------
    # DISPATCH: built-in or external?
    # -------------------------------------------------------------------------

    def execute(self, tokens):
        """Run a parsed command. Dispatch to a built-in or to subprocess."""
        command = tokens[0]
        args = tokens[1:]

        # Built-ins are handled inside the current Python process,
        # because things like 'cd' must change OUR cwd, not a child's.
        if command in self.builtins:
            try:
                self.builtins[command](args)
            except SystemExit:
                raise   # let 'exit' propagate up
            except Exception as e:
                print(f"minishell: {command}: {e}", file=sys.stderr)
                self.last_exit_code = 1
            return

        # Otherwise: try to run it as an external program
        self.run_external(command, args)

    def run_external(self, command, args):
        """Spawn an external program and wait for it to finish."""
        try:
            # subprocess.run() forks + execs + waits for us.
            # We set SIGINT back to default in the child so Ctrl-C kills the
            # child (not the shell), via the preexec_fn hook.
            result = subprocess.run(
                [command] + args,
                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
            )
            self.last_exit_code = result.returncode
        except FileNotFoundError:
            print(f"minishell: {command}: command not found", file=sys.stderr)
            self.last_exit_code = 127     # standard "command not found" code
        except PermissionError:
            print(f"minishell: {command}: permission denied", file=sys.stderr)
            self.last_exit_code = 126
        except KeyboardInterrupt:
            # The child got Ctrl-C; print a newline so the prompt is clean
            print()
            self.last_exit_code = 130

    # -------------------------------------------------------------------------
    # BUILT-IN COMMANDS
    # -------------------------------------------------------------------------

    def builtin_cd(self, args):
        """Change directory. No arg -> HOME. '-' -> previous dir (like bash)."""
        if len(args) > 1:
            print("minishell: cd: too many arguments", file=sys.stderr)
            self.last_exit_code = 1
            return

        if not args:
            target = os.environ.get('HOME', '/')
        elif args[0] == '-':
            target = os.environ.get('OLDPWD')
            if not target:
                print("minishell: cd: OLDPWD not set", file=sys.stderr)
                self.last_exit_code = 1
                return
            print(target)   # bash prints the new directory when using 'cd -'
        else:
            # Expand ~ and environment variables like $HOME
            target = os.path.expanduser(os.path.expandvars(args[0]))

        try:
            old_pwd = os.getcwd()
            os.chdir(target)
            os.environ['OLDPWD'] = old_pwd
            os.environ['PWD'] = os.getcwd()
            self.last_exit_code = 0
        except FileNotFoundError:
            print(f"minishell: cd: {target}: No such file or directory", file=sys.stderr)
            self.last_exit_code = 1
        except NotADirectoryError:
            print(f"minishell: cd: {target}: Not a directory", file=sys.stderr)
            self.last_exit_code = 1
        except PermissionError:
            print(f"minishell: cd: {target}: Permission denied", file=sys.stderr)
            self.last_exit_code = 1

    def builtin_pwd(self, args):
        """Print working directory."""
        print(os.getcwd())
        self.last_exit_code = 0

    def builtin_echo(self, args):
        """Print arguments separated by spaces.
        Supports -n flag (don't print trailing newline) like real echo."""
        newline = True
        if args and args[0] == '-n':
            newline = False
            args = args[1:]
        text = ' '.join(args)
        if newline:
            print(text)
        else:
            print(text, end='', flush=True)
        self.last_exit_code = 0

    def builtin_exit(self, args):
        """Exit the shell with an optional integer exit code."""
        code = 0
        if args:
            try:
                code = int(args[0])
            except ValueError:
                print(f"minishell: exit: {args[0]}: numeric argument required",
                      file=sys.stderr)
                code = 2
        print("exit")
        sys.exit(code)

    def builtin_help(self, args):
        """Show a short help message listing the built-ins."""
        print("Built-in commands:")
        print("  cd [dir]        change directory (no arg => HOME; '-' => previous)")
        print("  pwd             print working directory")
        print("  echo [-n] ...   print arguments")
        print("  exit [code]     leave the shell")
        print("  help            show this message")
        print("  clear           clear the screen")
        print("  env             print environment variables")
        print("  export VAR=VAL  set an environment variable")
        print("  unset VAR       remove an environment variable")
        print("  history         show command history")
        print()
        print("Anything else is executed as an external program (ls, cat, ...).")
        self.last_exit_code = 0

    def builtin_clear(self, args):
        """Clear the screen using the standard ANSI escape sequence."""
        # \033[H moves the cursor to the top-left; \033[J clears below it.
        print("\033[H\033[J", end='')
        self.last_exit_code = 0

    def builtin_env(self, args):
        """Print every environment variable as KEY=VALUE."""
        for key, value in sorted(os.environ.items()):
            print(f"{key}={value}")
        self.last_exit_code = 0

    def builtin_export(self, args):
        """Set environment variables: export NAME=VALUE [NAME=VALUE ...]."""
        if not args:
            print("minishell: export: usage: export NAME=VALUE", file=sys.stderr)
            self.last_exit_code = 1
            return
        for arg in args:
            if '=' not in arg:
                print(f"minishell: export: '{arg}': not a valid identifier",
                      file=sys.stderr)
                self.last_exit_code = 1
                continue
            name, value = arg.split('=', 1)
            if not name.isidentifier():
                print(f"minishell: export: '{name}': not a valid identifier",
                      file=sys.stderr)
                self.last_exit_code = 1
                continue
            os.environ[name] = value
        self.last_exit_code = 0

    def builtin_unset(self, args):
        """Remove one or more environment variables."""
        if not args:
            print("minishell: unset: usage: unset NAME [NAME ...]", file=sys.stderr)
            self.last_exit_code = 1
            return
        for name in args:
            os.environ.pop(name, None)   # silent if not set, like bash
        self.last_exit_code = 0

    def builtin_history(self, args):
        """Show the list of previously typed commands."""
        for i, cmd in enumerate(self.history, 1):
            print(f"  {i:>4}  {cmd}")
        self.last_exit_code = 0


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------

def main():
    shell = Shell()
    try:
        shell.run()
    except SystemExit:
        raise
    except Exception as e:
        # Last-resort safety net so the shell never dies silently
        print(f"minishell: fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
