#!/usr/bin/env python3
import filecmp
import os
import subprocess


def exec(command, debug=False):
    output = subprocess.check_output(command, shell=True)

    if debug:
        print(output.decode("utf-8"))

    return output.decode("utf-8")


def main():
    exec("git log $(git describe --tags --abbrev=0)..HEAD --notes", debug=True)


if __name__ == "__main__":
    main()
