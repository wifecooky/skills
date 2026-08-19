---
name: wechat-macos-read
description: 读取本地微信（macOS 微信 4.x）某个群/联系人的聊天记录，全程不关闭 SIP。原理是把微信副本 ad-hoc 重签名（去掉 hardened runtime）并用 CFFIXED_USER_HOME 指回原账号数据，让它照常登录并把聊天记录解密缓存进内存，再用 lldb dump 内存、直接解析其中的 SQLite 页（WCDB / SQLCipher）把消息碾出来。当用户想导出/分析自己本地微信某个群的消息、或基于某群消息做东西（旅游计划、总结、时间线）时使用。仅限 Apple Silicon macOS、微信 4.x、用户本人在场操作自己的账号。
---

# wechat-macos-read

不关闭 SIP，从本地运行中的微信读取指定群/联系人的聊天记录。

## 适用与前提
- **仅** macOS（Apple Silicon）+ 微信 4.x（数据在 `~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/`）。
- 只处理**用户本人**、**当前登录**的微信；用户需在场（要点开目标聊天、可能要确认登录）。
- 需要 `lldb`（Xcode Command Line Tools）、`python3`（含 numpy）。
- 不触碰 `/Applications/WeChat.app` 原版；不关闭 SIP；用完可删除副本。

## 核心原理（为什么能不关 SIP）
1. 微信 4.x 库是 SQLCipher 加密，密钥只在内存里；直接读内存被 SIP + hardened runtime 挡住。
2. 把微信**拷贝**出来 `codesign --force --deep --sign -` 重签名 → 去掉 hardened runtime，lldb 就能 attach（SIP 保持开启）。
3. 重签名后 sandbox/keychain 权限没了、找不到账号 → 用 `CFFIXED_USER_HOME` 指向原容器 Data 目录，让它照常登录。
4. 微信显示某个聊天时，会把该聊天的消息**解密后缓存在内存**。dump 内存 → 解析 SQLite 叶子页 → 直接拿到明文消息，**不需要找密钥**。

关键限制：**只有"当前打开过的聊天"才在内存缓存里**。所以必须让用户点开目标群并向上滚动加载历史，才能 dump 到完整消息。

## 执行步骤

### 1. 环境检查
确认微信 4.x 数据目录存在、lldb 可用：
```
ls -d ~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_* 2>/dev/null
xcrun -f lldb
```
若不是微信 4.x（无 xwechat_files）或非 Apple Silicon，停止并说明不适用。

### 2. 准备重签名副本
```
bash scripts/setup_wechat.sh
```
拷贝 `/Applications/WeChat.app` → `~/.wechat-read/WeChatDbg.app` 并 ad-hoc 重签名。原版不动。

### 3. 启动副本（指回原账号数据）
```
bash scripts/launch_wechat.sh
```
> 会先 `pkill WeChat`（关掉正在跑的微信，含用户的正常微信），再用 `CFFIXED_USER_HOME` 启动副本。
> 副本弹出 **"Open WeChat"** 时让用户点一下（或扫码登录）。

### 4. 让用户加载目标聊天（关键人工步骤）
明确告诉用户：
> 在微信里**打开「<目标群名>」**，并**向上滚动**把要的历史消息显示出来（只有显示过的消息才会进内存）。完成后告诉我。

### 5. dump 内存并碾出消息
拿到微信 PID 后：
```
PID=$(pgrep -x WeChat | head -1)
bash scripts/dump.sh "$PID" ~/.wechat-read/dump.bin
python3 scripts/carve.py ~/.wechat-read/dump.bin ~/.wechat-read/messages.json
```
`carve.py` 解析所有 SQLite 叶子页里的微信消息记录，按"页"（= 同一张 Msg 表 = 同一个聊天）分组输出。

### 6. 定位目标群 + 导出
```
python3 scripts/show_chat.py ~/.wechat-read/messages.json --keywords "群里会出现的词,地名,人名"
```
`show_chat.py` 按关键词/时间筛出目标聊天的干净会话（去掉二进制/其他群），按时间排序打印。
- 微信里群消息表名是 `Msg_<md5(chatroom_id)>`；如果知道 chatroom id（形如 `xxxxx@chatroom`），可 `--chatroom xxxxx@chatroom` 精确定位（脚本会算 md5 并优先匹配）。
- 用消息内容 + 发言人交叉判断，锁定目标群那几页（同页 = 同群）。

### 7. 交付
拿到干净会话后，按用户需求产出（旅游计划 HTML、总结、时间线等）。写 HTML 时注意 CJK 排版、手机友好、light/dark。**内容含真实姓名 → 存成本地文件，不要自动发布成 artifact。**

### 8. 收尾
```
pkill -9 -x WeChat 2>/dev/null      # 关掉副本
rm -rf ~/.wechat-read/dump.bin      # 删掉几个 GB 的内存 dump
# 需要的话删副本： rm -rf ~/.wechat-read/WeChatDbg.app
```
提醒用户：原版微信没动、SIP 全程没关；之后正常打开 `/Applications/WeChat` 即可。

## 常见问题
- **副本启动即崩（SIGTRAP）**：确认用的是 `codesign --force --deep --sign -`（去掉 hardened runtime）而不是保留 `--options runtime`——保留 runtime 会触发微信反篡改自杀。
- **登录界面显示但没数据 / 找不到账号**：`CFFIXED_USER_HOME` 没指对，确认指向 `~/Library/Containers/com.tencent.xinWeChat/Data`。
- **dump 里没有目标群消息**：用户没点开该群或没向上滚动 → 回到第 4 步。
- **`codesign` Operation not permitted**：不要改 `/Applications` 里的原版（会被 TCC 挡），必须用副本方案（setup 脚本已如此）。

## 边界
- 这是本人读取本人本地数据的取证式方法；不要用于他人设备/账号。
- 依赖微信版本的表结构（`Msg_*` 表、`message_content` 列）；微信大版本更新后 `carve.py` 可能要跟着调。
