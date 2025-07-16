# Geosite & GeoIP Rule-Set for Clash

[![Auto Update Rules](https://github.com/busymilk/v2fly-domain-list-community_rule_set/actions/workflows/auto_update_rules.yml/badge.svg)](https://github.com/busymilk/v2fly-domain-list-community_rule_set/actions/workflows/auto_update_rules.yml)

这是一个自动化的项目，旨在将主流的 Geosite 和 GeoIP 数据转换为适用于 [Clash](https://github.com/Dreamacro/clash) 及其衍生客户端的 `RULE-SET` 格式。

## 解决了什么问题？

随着一些现代代理软件（如 ClashMi）逐渐放弃对 `geosite.dat` 和 `geoip.dat` 文件的直接支持，依赖这些文件的传统分流方式变得不再方便。本项目通过 GitHub Actions 实现了全自动转换，为所有兼容 `RULE-SET` 格式的客户端提供了一套即用、持续更新、社区驱动的规则集。

**数据源:**
- **Geosite (域名):** [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)
- **GeoIP (IP段):** [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip)

---

## 如何使用

所有生成的规则文件都托管在本仓库中，并通过 [jsDelivr CDN](https://www.jsdelivr.com/) 加速分发，以确保最佳的下载速度和可用性。

### 1. GeoSite 域名规则集

域名规则集位于 `clash-rules-generated/` 目录下。这些规则用于基于域名的流量匹配。

#### 基础用法

在您的 Clash 配置文件中，通过 `rule-providers` 引入所需的规则集。例如，要使用 `google` 的域名列表来代理相关流量：

```yaml
rule-providers:
  google:
    type: http
    behavior: classical # 或 domain
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/clash-rules-generated/google.txt"
    path: ./ruleset/google.rules
    interval: 86400 # 每天更新一次

rules:
  - RULE-SET,google,PROXY
```

#### 聚合标签规则 (推荐)

为了方便常见的分流配置（如广告屏蔽、国内外分流），项目预先生成了几个聚合了特殊标签的规则集：

- `collect_tag_ads.txt`: 聚合了所有广告域名，用于屏蔽广告。
- `collect_tag_cn.txt`: 聚合了所有中国大陆域名，用于直连。
- `collect_tag_!cn.txt`: 聚合了所有非中国大陆域名，用于代理。

**示例：广告屏蔽与国内外分流**

```yaml
rule-providers:
  ads:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/clash-rules-generated/collect_tag_ads.txt"
    path: ./ruleset/ads.rules
    interval: 86400

  cn_domains:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/clash-rules-generated/collect_tag_cn.txt"
    path: ./ruleset/cn_domains.rules
    interval: 86400

rules:
  - RULE-SET,ads,REJECT
  - RULE-SET,cn_domains,DIRECT
```

### 2. GeoIP IP规则集

IP 规则集位于 `geoip-rules-generated/` 目录下。这些规则用于基于目标 IP 地址的流量匹配，通常用于匹配无法通过域名判断的流量（如部分桌面应用或 IP 直连）。

目前，项目会生成以下 GeoIP 规则集：
- `geoip_cn.txt`: 中国大陆的 IP 地址段。
- `geoip_private.txt`: 私有/保留 IP 地址段。
- `geoip_cloudflare.txt`: Cloudflare 的 IP 地址段。
- `geoip_cloudfront.txt`: AWS CloudFront 的 IP 地址段。
- `geoip_facebook.txt`: Facebook (Meta) 的 IP 地址段。
- `geoip_fastly.txt`: Fastly 的 IP 地址段。
- `geoip_google.txt`: Google 的 IP 地址段。
- `geoip_netflix.txt`: Netflix 的 IP 地址段。
- `geoip_telegram.txt`: Telegram 的 IP 地址段。
- `geoip_twitter.txt`: Twitter (X) 的 IP 地址段。
- `geoip_tor.txt`: Tor 节点的 IP 地址段。

#### 基础用法

在 `rule-providers` 中定义，并确保 `behavior` 设置为 `ipcidr`。

**示例：中国大陆 IP 直连**

```yaml
rule-providers:
  cn_ip:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/geoip-rules-generated/geoip_cn.txt"
    path: ./ruleset/cn_ip.rules
    interval: 86400

rules:
  - RULE-SET,cn_ip,DIRECT
```

### 3. 完整分流配置示例

这是一个典型的分流配置，结合了域名和 IP 规则集，实现了广告屏蔽、国内外分流和局域网直连。

```yaml
# In your config.yaml

rule-providers:
  # 广告域名
  ads:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/clash-rules-generated/collect_tag_ads.txt"
    path: ./ruleset/ads.rules
    interval: 86400

  # 国内域名
  cn_domains:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/clash-rules-generated/collect_tag_cn.txt"
    path: ./ruleset/cn_domains.rules
    interval: 86400

  # 国内 IP 段
  cn_ip:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/geoip-rules-generated/geoip_cn.txt"
    path: ./ruleset/cn_ip.rules
    interval: 86400

  # 局域网 IP 段
  lan_ip:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/geoip-rules-generated/geoip_private.txt"
    path: ./ruleset/lan_ip.rules
    interval: 86400

rules:
  # 1. 屏蔽广告
  - RULE-SET,ads,REJECT
  
  # 2. 直连局域网
  - RULE-SET,lan_ip,DIRECT

  # 3. 直连国内域名和 IP
  - RULE-SET,cn_domains,DIRECT
  - RULE-SET,cn_ip,DIRECT

  # 4. 代理其他所有流量
  - MATCH,PROXY
```

---

## 自动化流程

本仓库通过 GitHub Actions 自动执行以下流程：

1.  **每日拉取**：每天定时从上游仓库拉取最新的域名和 GeoIP 数据。
2.  **自动转换**：运行 Python 脚本，将数据转换为 Clash `RULE-SET` 格式。
3.  **标签处理**：自动收集域名规则中的 `@` 标签，生成聚合规则文件。
4.  **提交推送**：将更新后的规则文件自动提交并推送到本仓库。
5.  **刷新 CDN**：自动请求 jsDelivr 刷新所有已更新文件的 CDN 缓存。

### **重要：启用 Actions 权限**

为了让 GitHub Actions 能够自动将更新后的规则推送到本仓库，您需要手动进行一次设置：

1.  **导航到仓库设置**：在您的 GitHub 仓库页面，点击右上角的 **Settings**。
2.  **Actions 设置**：在左侧菜单中，选择 **Actions** -> **General**。
3.  **修改工作流权限**：向下滚动到 **Workflow permissions** 部分，选择 **Read and write permissions** 选项，并保存。

完成此设置后，自动化工作流才能正常运行。

## 如何贡献

由于这是一个自动生成的仓库，请不要直接向本仓库提交 Pull Request 来修改规则。所有的规则都源自上游项目。如果您想贡献规则，请向对应的上游项目提交您的更改：

- **域名规则**: [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)
- **IP 规则**: [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip)
