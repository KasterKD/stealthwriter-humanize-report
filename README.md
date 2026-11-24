# StealthWriter report humanizer (Claude skill)

A Claude skill that humanizes a full Word report through [StealthWriter](https://app.stealthwriter.ai), one section at a time, without losing the facts.

StealthWriter passes AI detectors but scrambles facts on every run. This skill runs each section through **humanize → fix the scrambled facts → humanize again → small hand fixes**, then writes the text back into your original .docx so the formatting, tables and table of contents stay intact.

## What you need

- Claude (claude.ai or the desktop app) with **Claude in Chrome** installed
- A StealthWriter account, open and logged in in Chrome
- Your report as a .docx

## Install

1. Download `stealthwriter-humanize-report.skill` from this repo (or zip the `stealthwriter-humanize-report` folder yourself).
2. In Claude, open the Skills section in Settings and upload the file.

For Claude Code, copy the `stealthwriter-humanize-report` folder into `~/.claude/skills/`.

## Use

Attach your report and say something like:

> Humanize this report with StealthWriter. It's open in my Chrome.

## Notes

- The free StealthWriter plan allows 10 humanizations a day. Each section uses 2, so a long report may take two days.
- Title page, table of contents, headings, tables and captions are left as they are.
- Always read the final report yourself before you submit it.
