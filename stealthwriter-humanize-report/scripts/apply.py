"""Write humanized chunks back into the original .docx.

Usage (run from the work folder that holds chunks.json and <chunk>_final.txt files):
    python3 apply.py report.docx out.docx

Each final paragraph replaces the text of its original paragraph, so styles,
numbering and tables survive. A bold label at the start of a list item
(e.g. "Staff:") stays bold if the new text still starts with it.
"""
import docx, json, os, sys

src, out = sys.argv[1], sys.argv[2]
d = docx.Document(src)
P = d.paragraphs
ch = json.load(open('chunks.json'))
done = []
for k, v in ch.items():
    f = f'{k}_final.txt'
    if not os.path.exists(f):
        continue
    paras = [x.strip() for x in open(f).read().strip().split('\n\n')]
    assert len(paras) == len(v['ids']), (k, len(paras), len(v['ids']))
    for i, new in zip(v['ids'], paras):
        p = P[i]
        runs = p.runs
        lab = runs[0].text if runs else ''
        if runs and runs[0].bold and lab.strip() and new.startswith(lab.strip()):
            rest = new[len(lab.rstrip()):]
            if lab.endswith(' ') and rest.startswith(' '):
                rest = rest[1:]
            if len(runs) > 1:
                runs[1].text = rest
            else:
                p.add_run(rest)
            start = 2
        elif runs:
            runs[0].text = new
            start = 1
        else:
            p.add_run(new)
            start = 1
        for r in runs[start:]:
            r._r.getparent().remove(r._r)
    done.append(k)
d.save(out)
print('applied', done)
