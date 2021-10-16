#!/usr/bin/env python3
import subprocess


def exec(command):
    print(command)
    result = subprocess.run(command, shell=True, capture_output=True)

    if result.returncode:
        return result.stderr.decode("utf-8").strip(), result.returncode

    return result.stdout.decode("utf-8").strip(), result.returncode


def main():
    since, error_code = exec("git describe --tags --abbrev=0")
    if error_code:
        # if no tag was found, get first commit
        since, error_code = exec("git log --format='%h' | head -1")

    git_log, error_code = exec(f"git log {since}..HEAD --notes")
    if error_code:
        print("Cannot read git history, reason:", git_log)

    print("history repeats itself")
    print(git_log)


if __name__ == "__main__":
    main()
