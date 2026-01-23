# Examples

These examples show safe, copy/paste-friendly formatting for fenced code blocks.

## Example 1: Single file, single fenced block

~~~md
# README.md
Project overview goes here.
~~~

## Example 2: Multiple files, separate fenced blocks

README.md
~~~md
# Project Title
Short description.
~~~

tools/new-skill.sh
~~~bash
#!/usr/bin/env bash
echo "Hello"
~~~

## Example 3: User wants the whole response in one block

Use an outer `~~~` fence so inner backticks remain safe to copy.

~~~md
Here is the full response in one block.

```bash
python tools/validate.py
```
~~~

## Example 4: Avoid nested backticks inside an outer backtick fence

If the outer fence is ``` use `~~~` for inner examples instead:

~~~md
```md
Here is a markdown file.

~~~bash
echo "Inner block uses tildes"
~~~
```
~~~
