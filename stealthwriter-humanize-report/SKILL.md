---
name: stealthwriter-humanize-report
description: Humanize a full report (.docx) through StealthWriter in Chrome, section by section - humanize, fix scrambled facts, humanize again - and put the text back into the original Word file. Use whenever the user asks to humanize a report, paper, lab report or assignment, make it pass AI detectors, or mentions StealthWriter.
---

# StealthWriter report humanizer

The goal is a fully humanized report that keeps every fact, number and name from the original. StealthWriter beats the AI detectors, but it scrambles facts on every run, and scrambled facts cost marks. That's why every section goes through **humanize → fix → humanize again**, and why the final output is checked against the original, not just against the detector score.

## What you need

- The report as a .docx (attached, or on the user's computer).
- Claude in Chrome, with StealthWriter (https://app.stealthwriter.ai) open and logged in. If a chrome-browser skill is listed, load it first, then load the Chrome tools in one ToolSearch call (tabs_context_mcp, navigate, computer, find, get_page_text, javascript_tool, browser_batch).
- If the report's facts come from somewhere else (lab requirements, an earlier draft, another chat), pull that in for context so you know what the correct facts are.
- Keep whatever mode and level the user has selected in StealthWriter.

## 1. Prepare the report

Work on a copy in a `work/` folder. Never edit the upload.

1. Convert to text with pandoc to see the structure and word count.
2. List paragraphs with python-docx: index, style, word count, first 60 characters.
3. Pick the body paragraphs to humanize. **Leave alone:** title page, table of contents, headings, tables, figure and table captions, references. Short label lines (under ~12 words) that aren't list items can stay too.

## 2. Split into chunks by context

StealthWriter's input box has a word limit (1,000 words on the free plan; check the counter on the page). Split the body so each chunk:

- stays under the limit,
- covers **one section or phase only**. Never mix two different sections in one chunk, because the humanizer blends context across paragraphs,
- keeps a whole section together if it fits. If it doesn't, split at a subsection boundary (for example 2.1–2.3, then 2.4–2.9), never mid-subsection.

The introduction can go with the first part of the first section if it fits.

Save the chunks to `work/chunks.json` as `{"C1": {"ids": [paragraph indices], "text": "paragraphs joined by blank lines"}, ...}`. One paragraph per blank-line block is what lets you put the text back into the .docx later.

**Check the daily limit before starting.** The free plan gives 10 humanizations a day; the reset time is shown in StealthWriter. Each chunk costs 2 runs. Tell the user up front how many runs the report needs. If it's more than they have left, say so and suggest splitting it over two days or upgrading.

## 3. The pipeline, for each chunk

### Pass 1
Put the text in StealthWriter and humanize. Typing is slow and unreliable, so set the textarea with JavaScript and click the button in the same call:

```js
const ta=document.querySelector('textarea');
const t=`...chunk text...`;
const setter=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
setter.call(ta,t); ta.dispatchEvent(new Event('input',{bubbles:true}));
await new Promise(r=>setTimeout(r,500));
[...document.querySelectorAll('button')].find(b=>b.innerText.trim()=='Humanize').click();
await new Promise(r=>setTimeout(r,25000)); 'done'
```

Use a template literal (backticks) and escape any backticks or `${` in the text. Then read the result with get_page_text. If a popup appears (usage limit, upsell), close it ("Maybe later") and take a screenshot to see what happened.

### Fix
Compare the result against the original, paragraph by paragraph. Fix anything that changed the meaning, and keep the humanized wording everywhere else. Typical scrambles:

- facts flipped ("only surgery is performed in X" instead of "surgery is only performed in X"),
- numbers, dates or schedule weeks mixed up,
- ratings changed ("high" instead of "critical"),
- things moved to the wrong place or person,
- technical terms swapped for wrong synonyms,
- paragraphs merged or split.

The paragraph count must match the chunk's ids. List items that start with a bold label (`Staff:`, `Public:`) must still start with that exact label.

### Pass 2
Humanize the fixed text again, the same way. This pass is the one that makes it read human after your fixes.

### Final touch
Pass 2 adds a few new mistakes of its own ("(me)" for a role, half-sentences, invented claims). Fix those **by hand**, touching only the broken words. Don't run a third pass: each run fixes some errors and creates new ones, so a third run just restarts the problem and burns a daily run.

Note the detector score StealthWriter shows. Save the result as `work/<chunk>_final.txt`.

## 4. Put it back into the .docx

Run `scripts/apply.py` (in this skill's folder) from `work/`:

```bash
cd work && python3 <skill-dir>/scripts/apply.py report.docx out.docx
```

It writes each final paragraph into its original paragraph, so styles, numbering, tables and the bold labels on list items survive. Before running it, check for list items whose bold label no longer starts the new text, and fix those text files. Paragraphs with superscripts or special formatting (like 10^11) get flattened to one run, so re-check those.

## 5. Check before sending

- Convert the original and the output to PDF (`soffice --headless --convert-to pdf`) and compare which page key headings land on. The table of contents page numbers must still match. If text grew and pushed headings, tell the user to update the TOC in Word.
- Read the final text once more against the original for numbers, names and table/figure references.
- Name the file `<original name>_HUMANIZED.docx` (add `_partial` if not every section is done) and send it to the user.

## 6. If the daily limit hits mid-way

Deliver the partial .docx right away, say which sections are done and which are still original, and offer two options: continue after the reset (a scheduled task if the session can create one; Chrome must stay open with StealthWriter logged in), or upgrading the plan. A scheduled message needs everything to resume: remaining chunk names, the file paths in `work/`, the pipeline steps and the apply command.

## Report back

Keep it short: what's done, a few examples of facts StealthWriter scrambled and you fixed, the detector scores, what was left untouched (title page, TOC, tables, captions), and anything the user must check themselves.
