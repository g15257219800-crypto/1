# Obsidian × 坚果云同步失败排查手册

没有具体报错截图时，先按「同步链路」对号入座。  
**同一库只允许走一条同步路。** 桌面客户端、官方插件、Remotely Save 叠在一起，是最常见的失败原因。

---

## 0. 立刻先备份

任何修复动作前，把整个 Vault 复制一份到**坚果云同步目录之外**（例如桌面 `Vault备份-日期`）。  
`.obsidian` 也要一起拷。冲突、覆盖、限流后的半截同步，都可能改坏配置。

---

## 1. 先判断你走的是哪条路

打开 Obsidian → 设置 → 第三方插件，看启用了什么。

| 你现在的做法 | 属于 | 推荐？ |
|---|---|---|
| 社区插件 **Nutstore Sync**（坚果云官方）+ 单点登录 | 方案 A | **首选** |
| 社区插件 **Remotely Save** + 坚果云 WebDAV | 方案 B | 不推荐，易 503 |
| Vault 放在「我的坚果云」文件夹里，靠桌面客户端同步 | 方案 C | 能用，但容易出冲突副本 |
| 上面任意两条同时开着 | 双重同步 | **立刻关掉其中一条** |

同时开两条时，先停掉其中一条，重启 Obsidian 和坚果云客户端，再继续往下查。

---

## 2. 按报错对号入座

### 503 / Service Unavailable / Invalid response

**原因：** 撞上坚果云 WebDAV 访问频率限制。

官方数字（[帮助中心](https://help.jianguoyun.com/?p=2064)）：

- 免费版：每 30 分钟不超过 **600** 次请求
- 付费版：每 30 分钟不超过 **1500** 次请求
- 单次列目录最多 **750** 个条目（不分页的客户端会同步不全）
- 单文件上传上限默认 **500 MB**

Obsidian 几乎每打几个字就写盘。Remotely Save 一连接还会瞬间打出大量 PROPFIND。库稍大就会 503。坚果云客服曾明确不建议用 Remotely Save。

**处理：**

1. 关掉自动同步，**至少等 30 分钟**（有人反馈要等更久，最多约 6 小时）再连。
2. 不要继续狂点「立即同步」，会把窗口拉得更长。
3. 若仍在用 Remotely Save：迁到 **Nutstore Sync**。
4. 大库首次同步改「宽松模式」，跳过大附件，分批同步。
5. 关掉系统代理 / 全局 VPN 后再试（或反过来：有人用全局代理才能连上，以你当前网络为准）。

### 登录失败 / 检查连接失败 / SSO 跳转失败

1. 升级 Obsidian 和 Nutstore Sync 到最新版，重启 Obsidian。
2. 先能打开 [https://www.jianguoyun.com/](https://www.jianguoyun.com/) 并登录。
3. 暂时关掉代理、公司防火墙、广告拦截对 `jianguoyun.com` / `dav.jianguoyun.com` 的拦截。
4. 插件里走 **单点登录**，不要手填 WebDAV，除非你明确要手动模式。
5. 仍失败：卸载插件 → 重启 → 重装 → 重新授权。

### 401 / 403 / 密码错误（WebDAV 手动填写）

1. 密码必须是网页端生成的 **第三方应用密码**，不是登录密码。  
   路径：坚果云网页 → 账户信息 → 安全选项 → 添加应用密码。  
   文档：[第三方应用授权 WebDAV](https://help.jianguoyun.com/?p=2064)
2. 服务器地址必须是：

   `https://dav.jianguoyun.com/dav/`

   不要写成 `www.jianguoyun.com`，不要漏 `/dav/`。
3. 用户名是注册邮箱。
4. 若开了微信二次验证，WebDAV 不兼容，到安全选项里关掉后再试。
5. 应用密码只显示一次，丢了就重新生成。

### 流量不足 / 空间不足 / 无法上传

免费版官方额度（[流量说明](https://help.jianguoyun.com/?p=29)、[流量不足](https://help.jianguoyun.com/?p=2803)）：

- 每月上传 **1 GB**，下载 **3 GB**
- 按账号注册日起每满一个月清零，不按自然月，剩余不结转
- 网页端「账户信息」可看已用流量和下次清零时间

上传用完就不能再推笔记；下载用完新设备就拉不下来。  
大图、PDF、录音很容易把额度打光。处理：清附件、等额度刷新，或升级专业版。

### 冲突副本 / `NSConflict` / 同一笔记多个版本

多端同时改同一篇，或桌面客户端与插件抢同一文件。

1. **先不要删**冲突文件。
2. Nutstore Sync：冲突策略选智能合并；合并不了再人工看标记。
3. 桌面客户端：库里搜 `冲突`、`conflict`、`NSConflict`，对照网页端历史版本。
4. 网页端打开该文件 → 历史版本，回滚到改坏之前。
5. 以后：一台写完、等同步完成，再开另一台。

若用桌面客户端同步，建议忽略高频配置文件，避免 workspace 打架：

```
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/workspaces.json
```

Windows：`%APPDATA%\Nutstore\db\customExtRules.conf`  
macOS / Linux：`~/.nutstore/db/customExtRules.conf`  

没有就新建，一行一条，重启坚果云客户端。

### `.obsidian` 不同步，或同步后插件/主题崩了

- Nutstore Sync **默认排除** `.obsidian`。笔记能过去，主题、快捷键、插件不会。
- 要同步配置：插件设置里打开配置目录同步，并从排除规则里去掉 `.obsidian`。
- 打开前先备份。只在**一台主力电脑**改插件和快捷键，等同步完成再开手机/第二台电脑。
- 建议长期排除：

  ```
  .obsidian/workspace.json
  .obsidian/workspace-mobile.json
  ```

  这样插件和主题能对齐，各设备布局互不覆盖，能去掉大部分冲突。
- 配置同步稳定后，可再关掉配置同步，只留 Markdown，减少碎片文件请求。
- 各设备 Obsidian 版本尽量接近；电脑插件在手机上可能根本不能跑。

### 两端笔记数量对不上

1. 以坚果云网页端文件列表为基准。
2. 看手机端是否「跳过大文件」、排除规则是否更严。
3. 手动触发一次完整同步，等状态变成完成，不要中途切网络。
4. 确认两端连的是云端**同一个文件夹**。

---

## 3. 按方案把链路修到稳态

### 方案 A（推荐）：Nutstore Sync 官方插件

仓库：[nutstore/obsidian-nutstore-sync](https://github.com/nutstore/obsidian-nutstore-sync)

1. 设置 → 第三方插件 → 关闭安全模式 → 浏览 → 搜索 `Nutstore Sync` → 安装并启用。
2. 插件设置里点 **单点登录**，浏览器授权后回 Obsidian，点「检查连接」。
3. 指定云端同步目录（建议单独建 `ObsidianVault`，不要和别的资料混在一个根目录）。
4. 前几天**不要**同步 `.obsidian`，先让笔记跑稳。
5. 冲突策略：智能合并。大库打开宽松模式，并设大文件跳过阈值。
6. 电脑上如果还装着坚果云桌面客户端：升级到 **7.2.12 及以上**，并且 **不要把 Vault 放进「我的坚果云」同步文件夹**。插件自己走 WebDAV，再套一层客户端会双写。

### 方案 B：Remotely Save + WebDAV（不推荐）

仅当你必须暂时维持旧配置时：

1. 应用密码 + `https://dav.jianguoyun.com/dav/` + 注册邮箱。
2. 关掉自动同步，改为手动、拉长间隔。
3. 排除 `.obsidian`、`.trash`、`.git`、大附件。
4. 出现 503 就停，等窗口过了再连。
5. 有空迁到方案 A。

### 方案 C：只靠坚果云桌面客户端

1. Vault 放在同步文件夹里，**不要再开** Nutstore Sync / Remotely Save。
2. 用上面的 `customExtRules.conf` 忽略 workspace 一类高频文件。
3. 不要多开 Obsidian 对着同一库猛改。
4. 客户端托盘里确认没有红叉、没有「流量不足」。
5. 隐藏目录 `.obsidian` 若没上去，检查选择性同步和忽略规则，确认没有把整个 `.obsidian` 排除掉（除非你故意只同步笔记）。

---

## 4. 通用五步（任何方案都先做）

1. 能打开坚果云网页并登录。
2. 账户信息里看流量是否用完。
3. 更新 Obsidian、插件、坚果云客户端，重启。
4. 确认没有双重同步。
5. 用一个只有两三篇笔记的测试库复现。测试库也失败 = 账号/网络/插件；测试库成功 = 主力库太大、冲突或排除规则问题。

---

## 5. 仍失败时，把这些信息记下来

下一次排查只需要这些，不必再猜：

1. 方案 A / B / C，还是混用
2. 完整报错原文（503、401、流量不足、Failed to load plugin…）
3. 电脑 / 手机，Windows / macOS / Android / iOS
4. Obsidian 版本、Nutstore Sync 或 Remotely Save 版本、坚果云客户端版本
5. 免费还是付费；网页端显示的已用上传/下载流量
6. 库大概多少篇笔记、有没有大量图片/PDF
7. 是否开了代理或微信二次验证

插件日志：Nutstore Sync 设置里有详细日志，把最近一次失败那一段复制出来即可。

---

## 参考

- [坚果云 WebDAV 授权与频率限制](https://help.jianguoyun.com/?p=2064)
- [免费版流量如何计算](https://help.jianguoyun.com/?p=29)
- [流量/空间不足](https://help.jianguoyun.com/?p=2803)
- [Nutstore Sync 官方插件](https://github.com/nutstore/obsidian-nutstore-sync)
- [Remotely Save + 坚果云 503（中文论坛）](https://forum-zh.obsidian.md/t/topic/48945)
