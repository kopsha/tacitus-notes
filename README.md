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

First, install the tiny script:

```bash
$ pip install tacitus-notes
```

Then, run this command in your project directory and see what happens:

```bash
$ tacitus-notes
```

You can use `--first` and `--last` arguments to define ranges
```bash
$ tacitus-notes --first=<commit_hash> --last=<commit_hash>
```
