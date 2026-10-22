# stdin (simplified) -> stdout Taiwan traditional (OpenCC s2twp) for YouTube's 中文（繁體） title/description translation.
# #hashtags pass through unchanged so both versions feed the same tag pages; URLs, English and IPA are untouched anyway.
import re, sys
import opencc

cc = opencc.OpenCC("s2twp")
sys.stdout.write("".join(p if p.startswith("#") else cc.convert(p) for p in re.split(r"(#\S+)", sys.stdin.read())))
