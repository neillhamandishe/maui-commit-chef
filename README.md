# Maui Commit Chef

## Description
This is a python script designed to work with the [pre-commit tool](https://pre-commit.com/ "Pre-commit git hooks tool") on your local git repo.

## Dependencies
- [Python](https://www.python.org/downloads "Python interpretter")
- [pre-commit tool](https://pre-commit.com/ "Pre-commit git hooks tool")
- [Conventional Commits](https://www.conventionalcommits.org)

## Installation Usage

1. Install pre-commit
    ```bash
    pip install pre-commit
    pre-commit install
    ```

2. Add maui-commit-chef as submodule
    ```bash
    git add submodule https://github.com/neillhamandishe/maui-commit-chef.git
    ```
3. Create pre-commit config file in your project root
    ```bash
    touch .pre-commit-config.yaml
    ```

    Paste the following content into the file
    ```yaml
    repos:
    -   repo: local
        hooks:
        -   id: maui-commit-chef
            name: Maui Commit Chef
            entry: python maui-commit-chef/maui-commit-chef.py
            language: python
            pass_filenames: false
    ```

## How it works
Maui Commit Chef analyses your local git repo tags using the output of ```git tag -l``` after having run a ```git fetch --all --tags``` if no tags are present, the default semver will be 0.1.0

> ⚠️ Warning: Tags must be in the format v'major'.'minor'.'patch' e.g., v0.1.0 

Commit Chef the goes over all logs from ```git log --one-line --since='Last Commit Date'``` where Last Commit Date is the date and time of the last tag.
If no tag is present then Commit Chef will use the output of ```git log --oneline```.

The commit messages are analysed using the [Conventional Commits](https://www.conventionalcommits.org) syntax. [Semver](https://semver.org) rules are applied to calculate the new semantic version.

In the event of the previous tag version differing from the calculated version, the csproj in the project root is modified to reflext the following snippet

> ℹ️ Info: This is the major purpose of this project

```xml
<ApplicationDisplayVersion>calculated version</ApplicationDisplayVersion>
<ApplicationVersion>major version</ApplicationVersion>
```

> ⚠️ Warning: The body and footer of commit messages are not parsed. Therefore, to introduce breaking changes, always have the ! in the stem of the commit message. e.g., feature!: Added some feature that breaks changes

## What this project does not do
This project does not do the following
- consider submodules
- manage git tags, remote or local, in any way.
- manage or create git commits or stage git files in any way.
