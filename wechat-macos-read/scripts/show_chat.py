#!/usr/bin/env python3
# Filter carved messages down to one chat and print a clean, time-sorted transcript.
# Usage:
#   python3 show_chat.py messages.json --keywords "台州,神仙居,出发"
#   python3 show_chat.py messages.json --chatroom 51882152148@chatroom   (exact, if known)
#   python3 show_chat.py messages.json --all                              (dump every group page)
import sys, json, argparse, datetime, hashlib, re

def txt(m):
    c = m[3]
    return c if isinstance(c, str) else ''

def clean(c):
    # drop binary/garbled content (non-text records) and control chars
    if not c: return ''
    if c.startswith('(/'): return ''
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', c): return ''
    if c.count('�') > 0: return ''
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('json')
    ap.add_argument('--keywords', default='')
    ap.add_argument('--chatroom', default='')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--min-msgs', type=int, default=2)
    args = ap.parse_args()

    groups = json.load(open(args.json))
    kws = [k.strip() for k in args.keywords.split(',') if k.strip()]

    if args.chatroom:
        h = hashlib.md5(args.chatroom.encode()).hexdigest()
        sys.stderr.write("target table: Msg_%s (note: table name not stored in leaf pages; "
                         "use --keywords to locate)\n" % h)

    # dedup identical pages
    seen = set(); pages = []
    for g in groups:
        sig = tuple(sorted(set((m[0], txt(m)[:16]) for m in g['msgs'] if txt(m))))
        if not sig or sig in seen: continue
        seen.add(sig); pages.append(g)

    def match(g):
        if args.all: return True
        if not kws: return True
        t = ' '.join(txt(m) for m in g['msgs'])
        return any(k in t for k in kws)

    rows = {}
    for g in pages:
        if not match(g): continue
        for m in g['msgs']:
            c = clean(txt(m))
            if not c: continue
            rows[(m[0], m[1], c)] = g['off']

    out = sorted(rows.keys())
    sys.stderr.write("matched clean messages: %d\n" % len(out))
    for ct, s, c in out:
        ts = datetime.datetime.fromtimestamp(ct).strftime('%Y-%m-%d %H:%M') if ct else '?'
        print(f"{ts}  s{s}: {c}")

if __name__ == '__main__':
    main()
