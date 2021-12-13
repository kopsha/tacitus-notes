#!/usr/bin/env python3
import argparse
import re
import sys
import subprocess

from ._version import __version__


def exec(command):
    """runs shell command and capture the output"""

    result = subprocess.run(command, shell=True, capture_output=True)

    if result.returncode:
        return result.stderr.decode("utf-8").strip(), result.returncode

    return result.stdout.decode("utf-8").strip(), result.returncode


def exec_no_fail(command):
    """runs shell command and capture the output"""

    result = subprocess.run(command, shell=True, capture_output=True)

    if result.returncode:
        print(f"Error executing: {command}")
        sys.exit(result.stderr.decode("utf-8").strip())

    return result.stdout.decode("utf-8").strip()


def parse_issue_tracking(subject):
    """parse and build issue tracker url from issue number"""

    has_tracker_ref = re.compile(r"\[#(\w+)\]")
    if ref := has_tracker_ref.findall(subject):
        issue_id = ref[0]
        url = f"https://www.pivotaltracker.com/story/show/{issue_id}"
        subject = has_tracker_ref.sub("", subject)
    else:
        url = None

    return url, subject


def parse_github_pr(subject):
    has_github_pr = re.compile(r"\(#\d+\)")
    if ref := has_github_pr.findall(subject):
        pr_ref = ref[0]
        subject = has_github_pr.sub("", subject)
    else:
        pr_ref = None

    return pr_ref, subject


def parse_history(raw_log):
    """given raw git log, parses into commit subject and body"""

    history = list()
    remaining = raw_log
    sep = True
    while sep:
        raw_entry, sep, remaining = remaining.partition("<<<")
        subject, x_sep, body = raw_entry.partition(">>>")
        if x_sep:
            body = body.strip()
            _, subject = parse_github_pr(subject)
            issue_url, subject = parse_issue_tracking(subject)
            subject = subject.strip()
            history.append((subject, body, issue_url))
        else:
            assert not bool(
                subject.strip()
            ), f"Cannot skip non-empty sequence: {subject.strip()}"

    return history


def generate_release_notes(history, title, include_body=True):
    """renders release notes from history using markdown syntax"""

    updates = list()
    fixes = list()

    is_fix = re.compile(r"(fix|fixes|fixed|hotfix)", re.IGNORECASE)
    for subject, body, url in history:
        notes = list()
        subject = re.sub(r"^\*\s+", r"", subject)

        if url:
            notes.append(f"* [{subject.capitalize()}]({url})")
        else:
            notes.append(f"* {subject.capitalize()}")

        if body and include_body:
            for line in body.split("\n"):
                line = line.strip()
                if line.startswith("Co-authored-by:"):
                    continue

                extra = re.sub(r"^\*\s+", r"", line)
                if extra:
                    notes.append(f"  * {extra.capitalize()}")

        full_note = "\n".join(notes)
        if is_fix.match(subject):
            fixes.append(full_note)
        else:
            updates.append(full_note)

    release_notes = list()
    release_notes.extend(
        (
            f"# {title.title()}",
            "",
            "",
        )
    )

    if updates:
        release_notes.extend(
            (
                "## Features and improvements",
                "",
            )
        )
        release_notes.extend(updates)
        release_notes.extend(("", ""))

    if fixes:
        release_notes.extend(
            (
                "## Fixes",
                "",
            )
        )
        release_notes.extend(fixes)

    text = "\n".join(release_notes)
    return text


def detect_range_start(first_arg):
    """
    picks first commit as follows:
    * from `first` argument, or
    * last major version found in tag, or
    * the first commit in history
    """

    if first_arg:
        commit_hash = exec_no_fail(f"git rev-parse --short {first_arg}")
        return commit_hash

    commit_hash, error_code = exec("git describe --tags --abbrev=0")
    if error_code:
        commit_hash = exec_no_fail("git rev-list --max-parents=0 HEAD | head -1")
    else:
        commit_hash = re.sub(r"^(v?\d+\.\d+).*", r"\1", commit_hash)

    return commit_hash


def detect_range_end(last_arg):
    """picks last commit from argument or head"""

    if last_arg:
        commit_hash = exec_no_fail(f"git rev-parse --short {last_arg}")
    else:
        commit_hash = "HEAD"

    return commit_hash


def main():
    parser = argparse.ArgumentParser(
        description="Generate release notes in markdown format"
    )
    parser.add_argument("--first", help="Commit hash to use as starting point")
    parser.add_argument("--last", help="Commit hash to use as stopping point")
    parser.add_argument(
        "--version", action="store_true", help="Shows application version and quits"
    )
    args = parser.parse_args()

    if args.version:
        print(f"{parser.prog} v{__version__}")
        sys.exit()

    first = detect_range_start(args.first)
    last = detect_range_end(args.last)

    git_log = exec_no_fail(f"git --no-pager log {first}..{last} --format='%s>>>%b<<<'")
    history = parse_history(git_log)

    proposed_tag, _ = exec("git describe")
    markdown_text = generate_release_notes(
        history, title=f"Release {proposed_tag}", include_body=False
    )

    print(markdown_text)


if __name__ == "__main__":
    main()
