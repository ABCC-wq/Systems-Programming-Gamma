#!/usr/bin/env python3
# Mini Shell - COSC-3411 System Programming
# Gamma Team (Lambda topic)
# Members: Ali Almousa, Hassan Albrahim, Ahmad Alsahan, Abdulaziz Almotairi

import os
import sys
import shlex
import subprocess
import signal


class Shell:
    def __init__(self):
        self.history = []
        self.last_exit_code = 0

        # map commands to their functions
        self.builtins = {
            'cd':      self.cmd_cd,
            'pwd':     self.cmd_pwd,
            'echo':    self.cmd_echo,
            'exit':    self.cmd_exit,
            'help':    self.cmd_help,
            'clear':   self.cmd_clear,
            'env':     self.cmd_env,
            'export':  self.cmd_export,
            'unset':   self.cmd_unset,
            'history': self.cmd_history,
        }

    def get_prompt(self):
        user = os.environ.get('USER', 'user')
        host = os.uname().nodename
        cwd = os.getcwd()
        home = os.path.expanduser('~')
        if cwd.startswith(home):
            cwd = '~' + cwd[len(home):]
        return f"\033[1;32m{user}@{host}\033[0m:\033[1;34m{cwd}\033[0m$ "

    def run(self):
        # ignore ctrl+c in the main shell
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        print("Mini Shell -- type 'help' for commands, 'exit' to quit")

        while True:
            try:
                line = input(self.get_prompt())
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                print()
                break

            line = line.strip()
            if not line:
                continue

            self.history.append(line)

            try:
                tokens = shlex.split(line)
            except ValueError as e:
                print(f"Error: {e}")
                continue

            if tokens:
                self.execute(tokens)

    def execute(self, tokens):
        cmd = tokens[0]
        args = tokens[1:]

        if cmd in self.builtins:
            try:
                self.builtins[cmd](args)
            except SystemExit:
                raise
            except Exception as e:
                print(f"minishell: {e}")
        else:
            self.run_external(cmd, args)

    def run_external(self, cmd, args):
        try:
            # run the command as a child process
            # preexec_fn restores ctrl+c for the child process only
            result = subprocess.run(
                [cmd] + args,
                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)
            )
            self.last_exit_code = result.returncode
        except FileNotFoundError:
            print(f"minishell: {cmd}: command not found")
            self.last_exit_code = 127
        except PermissionError:
            print(f"minishell: {cmd}: permission denied")
            self.last_exit_code = 126
        except KeyboardInterrupt:
            print()

    # ---- built-in commands ----

    def cmd_cd(self, args):
        if len(args) > 1:
            print("cd: too many arguments")
            return

        if not args:
            target = os.environ.get('HOME', '/')
        elif args[0] == '-':
            target = os.environ.get('OLDPWD', '')
            if not target:
                print("cd: OLDPWD not set")
                return
            print(target)
        else:
            target = os.path.expanduser(os.path.expandvars(args[0]))

        try:
            prev = os.getcwd()
            os.chdir(target)
            os.environ['OLDPWD'] = prev
            os.environ['PWD'] = os.getcwd()
        except FileNotFoundError:
            print(f"cd: {target}: No such file or directory")
        except NotADirectoryError:
            print(f"cd: {target}: Not a directory")
        except PermissionError:
            print(f"cd: {target}: Permission denied")

    def cmd_pwd(self, args):
        print(os.getcwd())

    def cmd_echo(self, args):
        # support -n flag like real echo
        if args and args[0] == '-n':
            print(' '.join(args[1:]), end='')
        else:
            print(' '.join(args))

    def cmd_exit(self, args):
        code = 0
        if args:
            try:
                code = int(args[0])
            except ValueError:
                print(f"exit: {args[0]}: numeric argument required")
                code = 1
        print("exit")
        sys.exit(code)

    def cmd_help(self, args):
        print("Built-in commands:")
        print("  cd [dir]       - change directory")
        print("  pwd            - print working directory")
        print("  echo [args]    - print text")
        print("  exit [code]    - exit the shell")
        print("  help           - show this help")
        print("  clear          - clear screen")
        print("  env            - show environment variables")
        print("  export VAR=VAL - set environment variable")
        print("  unset VAR      - remove environment variable")
        print("  history        - show command history")
        print("\nAnything else runs as an external command (ls, cat, etc.)")

    def cmd_clear(self, args):
        os.system('clear')

    def cmd_env(self, args):
        for key, val in os.environ.items():
            print(f"{key}={val}")

    def cmd_export(self, args):
        if not args:
            print("usage: export VAR=VALUE")
            return
        for arg in args:
            if '=' not in arg:
                print(f"export: invalid format: {arg}")
                continue
            name, value = arg.split('=', 1)
            os.environ[name] = value

    def cmd_unset(self, args):
        if not args:
            print("usage: unset VAR")
            return
        for name in args:
            if name in os.environ:
                del os.environ[name]

    def cmd_history(self, args):
        for i, cmd in enumerate(self.history, 1):
            print(f"  {i}  {cmd}")


# main entry point
if __name__ == '__main__':
    shell = Shell()
    shell.run()
