# 8 色调系统 (Tone System)

每个单词根据语义场景匹配一个色调。LLM 分析单词的核心意象后选择。

## 色调定义

### 1. 沉思 (Meditative)
**触发词**: 哲学、本质、意义、存在、时间、记忆、死亡、灵魂、命运、transcribe、ephemeral、melancholy
```
BG_COLOR:     #F5F2ED
ACCENT_COLOR: #8B5E3C
ACCENT_GLOW:  rgba(139,94,60,0.3)
MUTED_COLOR:  #C4B5A0
TEXT_COLOR:    #2D2926
TEXT_MUTED:    #5C5350
```

### 2. 锐利 (Sharp)
**触发词**: 精确、逻辑、切割、分析、判断、边界、incisive、acute、precise、dissect
```
BG_COLOR:     #F0F1F3
ACCENT_COLOR: #D4380D
ACCENT_GLOW:  rgba(212,56,13,0.3)
MUTED_COLOR:  #8C8C8C
TEXT_COLOR:    #1A1A1A
TEXT_MUTED:    #595959
```

### 3. 温暖 (Warm)
**触发词**: 人、情感、关系、归属、家、陪伴、nurture、embrace、compassion、tender
```
BG_COLOR:     #FBF6F0
ACCENT_COLOR: #CF7C3A
ACCENT_GLOW:  rgba(207,124,58,0.3)
MUTED_COLOR:  #D4C4A8
TEXT_COLOR:    #3D2B1F
TEXT_MUTED:    #7A6855
```

### 4. 技术 (Technical)
**触发词**: 系统、工程、机制、协议、架构、algorithm、protocol、compile、debug
```
BG_COLOR:     #F4F6F8
ACCENT_COLOR: #0070C0
ACCENT_GLOW:  rgba(0,112,192,0.3)
MUTED_COLOR:  #A0B4C8
TEXT_COLOR:    #1C2833
TEXT_MUTED:    #566573
```

### 5. 科研 (Academic)
**触发词**: 发现、假说、实验、观察、证据、hypothesis、empirical、theorem、axiom
```
BG_COLOR:     #F2F4F6
ACCENT_COLOR: #2E5090
ACCENT_GLOW:  rgba(46,80,144,0.3)
MUTED_COLOR:  #9BAEC4
TEXT_COLOR:    #1B2631
TEXT_MUTED:    #515A5A
```

### 6. 创意 (Creative)
**触发词**: 创造、想象、变形、打破、艺术、improvise、innovate、disrupt、metamorphosis
```
BG_COLOR:     #FFF8F0
ACCENT_COLOR: #E85D26
ACCENT_GLOW:  rgba(232,93,38,0.3)
MUTED_COLOR:  #C9A87C
TEXT_COLOR:    #2C1810
TEXT_MUTED:    #6B5344
```

### 7. 商业 (Commercial)
**触发词**: 增长、策略、市场、竞争、效率、leverage、optimize、scale、arbitrage
```
BG_COLOR:     #F5F5F0
ACCENT_COLOR: #1A7A4C
ACCENT_GLOW:  rgba(26,122,76,0.3)
MUTED_COLOR:  #A8C4B0
TEXT_COLOR:    #1C2826
TEXT_MUTED:    #4D5E58
```

### 8. 默认 (Default)
**触发词**: 通用、其他
```
BG_COLOR:     #F7F5F2
ACCENT_COLOR: #6B5B4F
ACCENT_GLOW:  rgba(107,91,79,0.3)
MUTED_COLOR:  #B5A99A
TEXT_COLOR:    #2D2926
TEXT_MUTED:    #6B625C
```

## 选择规则

1. 分析单词的**核心意象**（不是字面意思）
2. 匹配触发词最接近的色调
3. 同一个词在不同语境下可能不同色调（如 `scale` 科研/商业皆可），选最贴合词根本义的
4. 拿不准就用**默认**
