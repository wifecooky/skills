#!/usr/bin/env python3
# Carve WeChat 4.x message records out of a memory dump by parsing decrypted
# SQLite leaf-table b-tree pages. Groups records by page (a page belongs to one
# Msg_<hash> table = one chat). Output: JSON list of {off, msgs:[[ct,sender,type,content,source,rowid]...]}.
import sys, mmap, struct, json
try:
    import numpy as np
except ImportError:
    sys.exit("need numpy: pip3 install numpy")

PS = 4096
RESERVE = 80          # SQLCipher reserved bytes at page end (IV + HMAC)
USABLE = PS - RESERVE

def varint(buf, off):
    val = 0
    for k in range(9):
        b = buf[off+k]
        if k == 8:
            return (val << 8) | b, off+9
        val = (val << 7) | (b & 0x7f)
        if not (b & 0x80):
            return val, off+k+1
    return val, off+9

def parse_leaf(page):
    if page[0] != 0x0D:               # 0x0D = leaf table b-tree page
        return None
    ncell = (page[3] << 8) | page[4]
    if ncell < 1 or ncell > 400:
        return None
    recs = []
    for c in range(ncell):
        po = 8 + 2*c
        if po+2 > USABLE:
            return None
        cell = (page[po] << 8) | page[po+1]
        if cell < 8 or cell >= USABLE:
            continue
        try:
            payload_len, o = varint(page, cell)
            rowid, o = varint(page, o)
            if payload_len < 2 or payload_len > USABLE:
                continue
            hstart = o
            hlen, o2 = varint(page, hstart)
            if hlen < 1 or hlen > 200:
                continue
            serials = []
            p = o2; hend = hstart + hlen
            while p < hend:
                s, p = varint(page, p); serials.append(s)
            vals = []; d = hend; ok = True
            for s in serials:
                if s == 0: vals.append(None)
                elif s == 1: vals.append(int.from_bytes(page[d:d+1],'big',signed=True)); d+=1
                elif s == 2: vals.append(int.from_bytes(page[d:d+2],'big',signed=True)); d+=2
                elif s == 3: vals.append(int.from_bytes(page[d:d+3],'big',signed=True)); d+=3
                elif s == 4: vals.append(int.from_bytes(page[d:d+4],'big',signed=True)); d+=4
                elif s == 5: vals.append(int.from_bytes(page[d:d+6],'big',signed=True)); d+=6
                elif s == 6: vals.append(int.from_bytes(page[d:d+8],'big',signed=True)); d+=8
                elif s == 7: vals.append(struct.unpack('>d', page[d:d+8])[0]); d+=8
                elif s == 8: vals.append(0)
                elif s == 9: vals.append(1)
                elif s >= 12 and s % 2 == 0:
                    ln=(s-12)//2; vals.append(bytes(page[d:d+ln])); d+=ln
                elif s >= 13:
                    ln=(s-13)//2; vals.append(bytes(page[d:d+ln])); d+=ln
                else: ok=False; break
                if d > USABLE: ok=False; break
            if ok: recs.append((rowid, vals))
        except Exception:
            continue
    return recs or None

# Msg schema cols (0-based): 2 local_type, 4 real_sender_id, 5 create_time,
# 11 source(TEXT), 12 message_content(TEXT)
def looks_msg(v):
    if len(v) < 15: return False
    ct = v[5]
    if not isinstance(ct, int) or ct < 1400000000 or ct > 1900000000: return False
    return isinstance(v[2], int)

def dec(x):
    return x.decode('utf-8','ignore') if isinstance(x, (bytes, bytearray)) else x

def main():
    path, outpath = sys.argv[1], sys.argv[2]
    f = open(path, 'rb'); mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ); n = len(mm)
    arr = np.frombuffer(mm, dtype=np.uint8)
    aligned = arr[0:(n//16)*16:16]
    cand = (np.nonzero(aligned == 0x0D)[0] * 16).tolist()
    sys.stderr.write("candidate pages: %d\n" % len(cand))
    groups = []
    for off in cand:
        if off + PS > n: continue
        recs = parse_leaf(mm[off:off+PS])
        if not recs: continue
        msgs = []
        for rowid, v in recs:
            if not looks_msg(v): continue
            msgs.append([v[5], v[4], v[2], dec(v[12]), dec(v[11]), rowid])
        if len(msgs) >= 2 and len(msgs) >= len(recs)*0.5:
            groups.append({'off': off, 'n': len(msgs), 'msgs': msgs})
    json.dump(groups, open(outpath,'w'), ensure_ascii=False)
    sys.stderr.write("pages kept: %d -> %s\n" % (len(groups), outpath))

if __name__ == '__main__':
    main()
