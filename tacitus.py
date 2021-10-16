#!/usr/bin/env python3
import re
import subprocess


def exec(command):
    """runs shell command and capture the output"""

    result = subprocess.run(command, shell=True, capture_output=True)

    if result.returncode:
        return result.stderr.decode("utf-8").strip(), result.returncode

    return result.stdout.decode("utf-8").strip(), result.returncode


def parse_history(raw_log):
    """given raw git log, parses into commit subject and body"""

    history = list()
    remaining = raw_log
    sep = True
    while sep:
        raw_entry, sep, remaining = remaining.partition("<<<")
        subject, x_sep, body = raw_entry.partition(">>>")
        if x_sep:
            subject = subject.strip()
            body = body.strip()
            history.append((subject, body))
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
    for subject, body in history:
        notes = list()
        subject = re.sub(r"^\*\s+", r"", subject)
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


def main():
    since, error_code = exec("git describe --tags --abbrev=0")
    if error_code:
        # if no tag was found, get first commit
        since, error_code = exec("git rev-list --max-parents=0 HEAD | head -1")
    else:
        # pick only major versions
        since = re.sub(r"^(v?\d+\.\d+).*", r"\1", since)

    git_log, error_code = exec(
        f"git --no-pager log {since}..HEAD --format='%s>>>%b<<<'"
    )
    if error_code:
        print("Cannot read git history, reason:", git_log)

    history = parse_history(git_log)
    markdown_text = generate_release_notes(
        history, title="release title", include_body=False
    )

    print(markdown_text)


if __name__ == "__main__":
    main()
