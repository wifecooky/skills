# lldb command module: dump all readable+writable anonymous (heap) regions to a file.
# Usage inside lldb:  command script import dumpmem.py ; dumpmem /path/out.bin
import lldb

def dumpmem(debugger, command, result, internal_dict):
    outpath = command.strip()
    process = debugger.GetSelectedTarget().GetProcess()
    if not process or not process.IsValid():
        print("NO_PROCESS"); return
    regions = process.GetMemoryRegions()
    info = lldb.SBMemoryRegionInfo()
    err = lldb.SBError()
    total = 0; written = 0
    out = open(outpath, "wb")
    for i in range(regions.GetSize()):
        if not regions.GetMemoryRegionAtIndex(i, info):
            continue
        if not info.IsReadable() or not info.IsWritable():
            continue
        name = info.GetName()
        if name:
            low = name.lower()
            if (".dylib" in low or ".app" in low or "/system/" in low
                    or ".framework" in low or low.endswith(".bin")):
                continue
        start = info.GetRegionBase(); end = info.GetRegionEnd()
        size = end - start
        if size <= 0 or size > 1024*1024*1024:
            continue
        data = process.ReadMemory(start, size, err)
        if err.Success() and data:
            out.write(data); total += size; written += 1
    out.close()
    print("DUMPED_REGIONS=%d BYTES=%d -> %s" % (written, total, outpath))

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f dumpmem.dumpmem dumpmem')
