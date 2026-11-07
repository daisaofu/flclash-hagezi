# FlClash HaGeZi Override

面向 **FlClash + Mihomo** 的订阅覆写脚本。基于 AIsouler/MyClash 的 MIT 许可脚本做衍生改造，增加 HaGeZi 域名拦截、FlClash 导入说明和基础配置预检。

## 功能

- 保留 MyClash 的动态地区/倍率/家宽节点分组、代理协议参数和 DNS 节点域名处理。
- HaGeZi Multi `pro.mini` 默认开启；可切换 `light` / `pro.mini` / `pro`。
- 私有网络先直连；HaGeZi 域名再硬拒绝；其后才处理国内直连规则。
- 精确域名允许名单会强制直连并跳过 HaGeZi；未列域名仍按正常规则分流。
- `AdBlock` 原策略组保留，仍可在 `REJECT` / `REJECT-DROP` / `PASS` 间选择；HaGeZi 硬拒绝独立，不受 `PASS` 影响。
- 简约分流模式也保留 HaGeZi 规则。
- TUN 栈默认 `mixed`，可配置 `system` / `gvisor`；IPv6 开关可独立设置。
- 对无效配置对象、无法处理的 `proxy-providers` 输入和无效 TUN 栈给出明确错误。

## 配置

脚本顶部 `ruleOptionsEnable`：

```js
HaGeZi: true,
HaGeZiList: 'pro.mini', // 'light' | 'pro.mini' | 'pro'
HaGeZiAllowlist: [],    // 精确域名，例如 ['example.com']
TUNStack: 'mixed',      // 'mixed' | 'system' | 'gvisor'
IPv6Enabled: false,
```

`HaGeZiAllowlist` 只接受 ASCII DNS 域名，不接受通配符、URL 或 IP 地址。名单命中时规则目标是 `PASS`：当前规则系统继续匹配，但跳过紧随其后的 HaGeZi 拒绝规则，未命中更高优先级规则时进入原有代理分流；不会强制直连。

HaGeZi `pro.mini` 原始清单分成 `pro.mini-onlydomains.txt` 精确域名和 `pro.mini.txt` 的 `*.` 子域名模式。`tools/build_hagezi.py` 把它们转换成 Mihomo domain/text 格式：裸域名匹配根域，`.domain` 匹配其子域名。仓库提供生成好的 `rulesets/hagezi-pro-mini-mihomo.txt`，由每日 GitHub Actions 刷新。启用自建仓库 Raw 地址前，脚本中的 `ruleSetRepository` 必须改成自己的 GitHub `owner/repo`。

HaGeZi `pro.mini` 生成后当前约 198,000 条规则（精确域名 + 子域名规则），原始清单持续更新，数量会变化；mihomo 每 24 小时重新拉取仓库发布的规则文件。

## 安装到 FlClash

1. 先备份当前脚本或配置。
2. FlClash → 对应配置 → `扩展` → 选择 `脚本` → `前往配置脚本`，创建本地脚本并粘贴 `Script/mihomoScript.js` 全文。
3. 返回配置页，关联脚本并重新应用。
4. 关闭 FlClash UI 的二次 `DNS 覆写`，避免覆盖脚本的 DNS 配置；这不等于关闭 Mihomo DNS。
5. 确认代理订阅提供的是 `proxies` 节点数组。当前脚本不会展开远程 `proxy-providers`；此类输入会明确报错。
6. 首次启动检查 Mihomo 是否成功下载 `hagezi` provider，并确认规则列表中顺序是 `private` → 白名单 → `hagezi` → 国内直连。

FlClash 不同版本菜单名称可能不同。覆写脚本必须在对应 Profile 中关联后才会运行；仅保存脚本不会生效。

## 测试

在仓库根目录运行：

```sh
node --check Script/mihomoScript.js
node tests/test-script.js
python3 tools/build_hagezi.py --tiers pro.mini
```

## 来源、许可和归属

- `Script/mihomoScript.js` 是 **AIsouler/MyClash** 脚本的衍生版本。保留原作者及来源说明；原项目 MIT 许可全文见本仓库 `LICENSE`。上游：[MyClash](https://github.com/AIsouler/MyClash)。
- HaGeZi 名单由每日 GitHub Actions 用 `tools/build_hagezi.py` 转换后发布在 `rulesets/`；原始清单运行时不直连下载。HaGeZi 规则集是 **GPL-3.0** 衍生数据，发布时随附 `LICENSES/GPL-3.0.txt` 与 `NOTICE-HAGEZI.txt`。上游：[hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists)。
- [Smart-Config-Kit](https://github.com/IvanSolis1989/Smart-Config-Kit) 提供了优秀的 FlClash 导入/验收文档，本项目只参考其工作流与预检思路，没有复制其脚本代码。
- [YaNet](https://github.com/dahaha-365/YaNet) 的 Mihomo 脚本使用 `mixed` TUN 栈。本项目参考该配置思路，没有复制其脚本代码；其仓库为 BSD 3-Clause。
- 本仓库不是上述上游项目的官方版本。规则名单由上游更新，误拦与兼容性问题应分别按规则源和客户端版本排查。
