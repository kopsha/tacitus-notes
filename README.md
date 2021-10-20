# tacitus-notes

[Publius Cornelius Tacitus](https://en.wikipedia.org/wiki/Tacitus) was a Roman
historian and politician. And quite recently, he started writing notes on our git
repositories.


## the dream

Walk through git log, up to last tag or target commit, and collect each commit
message in a markdown format:
- prettify it,
- *replace ticket numbers with urls*
- print on console

## shellscript version

```bash
git describe --tags --abbrev=0
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```


## python version

Run this script in your project directory and see what happens.

```bash
python tacitus.py
```

