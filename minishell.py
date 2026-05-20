#!/usr/bin/env python3
# Mini Shell - System Programming
# Members: Ali Almousa, Hassan Albrahim, Ahmad Alsahan, Abdulaziz Almotairi

import os
import sys
import subprocess

def get_prompt():
    cwd = os.getcwd()
    home = os.path.expanduser('~')
    if cwd.startswith(home):
        cwd = '~' + cwd[len(home):]
    return f"{cwd}$ "

def run_command(command, args):
    # check if its a builtin command first
    if command == 'exit':
        print("Bye!")
        sys.exit(0)

    elif command == 'pwd':
        print(os.getcwd())

    elif command == 'echo':
        print(' '.join(args))

    elif command == 'clear':
        os.system('clear')

    elif command == 'help':
        print("Commands: cd, pwd, echo, clear, history, exit")
        print("Anything else will run as a system command")

    elif command == 'cd':
        if len(args) == 0:
            os.chdir(os.path.expanduser('~'))
        else:
            try:
                os.chdir(args[0])
            except FileNotFoundError:
                print(f"cd: {args[0]}: No such file or directory")

    elif command == 'history':
        for i, cmd in enumerate(history, 1):
            print(f"{i}  {cmd}")

    else:
        # run it as external command
        try:
            subprocess.run([command] + args)
        except FileNotFoundError:
            print(f"{command}: command not found")


# main program
history = []

print("Mini Shell - type 'help' for commands")

while True:
    try:
        line = input(get_prompt())
    except KeyboardInterrupt:
        print()
        continue
    except EOFError:
        break

    line = line.strip()
    if line == '':
        continue

    history.append(line)

    # split into command and arguments
    parts = line.split()
    command = parts[0]
    args = parts[1:]

    run_command(command, args)
