
# V2Fly Domain List Community - Clash Rule-Set

这是一个自动化的项目，旨在将 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) 的 `dat` 格式域名列表转换为适用于 [Clash](https://github.com/Dreamacro/clash) 的 `RULE-SET` 格式。

## 项目目标

随着一些代理软件（如 ClashMi）逐渐放弃对 `geosite.dat` 的支持，直接使用上游的 `dat` 文件变得不再方便。本项目旨在解决这一问题，通过 GitHub Actions 将 `v2fly/domain-list-community` 的规则自动转换为通用的 `RULE-SET` 格式，为所有兼容此格式的客户端提供即用型的规则集。

## 规则文件

所有生成的规则文件都在各自的目录中：

- **域名规则集**: `clash-rules-generated/`
- **GeoIP 规则集**: `geoip-rules-generated/`

### 域名规则 (Geosite)

`clash-rules-generated/` 目录下的每个 `.txt` 文件都对应 `domain-list-community` 中的一个域名列表。您可以直接在您的 Clash 配置文件中使用这些文件的 URL。

例如，要使用 `google` 规则集，您可以在配置文件中这样写：

```yaml
rule-providers:
  google:
    type: http
    behavior: classical
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/clash-rules-generated/google.txt"
    path: ./ruleset/google.rules
    interval: 86400
```

**注意**: 为了获得最佳的加载速度和可用性，推荐使用 jsDelivr CDN 的 URL。

#### 聚合标签规则

为了方便使用，本项目还提供了根据源文件中的 `@` 标签（如 `@ads`, `@cn`）聚合而成的特殊规则文件：

- `collect_tag_ads.txt`: 聚合了所有被标记为广告（`@ads`）的域名。
- `collect_tag_cn.txt`: 聚合了所有被明确标记为中国大陆（`@cn`）的域名。
- `collect_tag_!cn.txt`: 聚合了所有非中国大陆（`@!cn`）的域名。

### GeoIP 规则

`geoip-rules-generated/` 目录下的文件包含了从 [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip) 的 `geoip.dat` 文件中提取的 IP 地址段（CIDR）。这些规则对于基于 IP 的分流非常有用。

目前，项目会生成以下 GeoIP 规则集：
- `geoip_cn.txt`: 中国大陆的 IP 地址段。
- `geoip_private.txt`: 私有/保留 IP 地址段。

使用示例：

```yaml
rule-providers:
  cn_ip:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/busymilk/v2fly-domain-list-community_rule_set@main/geoip-rules-generated/geoip_cn.txt"
    path: ./ruleset/cn_ip.rules
    interval: 86400
```

## 自动化更新

本仓库通过 GitHub Actions 自动执行以下流程：

1.  **每日拉取**：每天定时从 `v2fly/domain-list-community` 和 `Loyalsoldier/geoip` 拉取最新的规则数据。
2.  **自动转换**：运行 Python 脚本，将域名和 GeoIP 数据转换为 Clash `RULE-SET` 格式。
3.  **标签处理**：自动收集域名规则中的 `@` 标签，生成聚合规则文件。
4.  **提交推送**：将更新后的规则文件自动提交并推送到本仓库。
5.  **刷新 CDN**：自动请求 jsDelivr 刷新所有已更新文件的 CDN 缓存。

### **重要：启用 Actions 权限**

为了让 GitHub Actions 能够自动将更新后的规则推送到本仓库，您需要手动进行一次设置：

1.  **导航到仓库设置**：
    *   在您的 GitHub 仓库页面，点击右上角的 **Settings**。
2.  **Actions 设置**：
    *   在左侧菜单中，选择 **Actions** -> **General**。
3.  **修改工作流权限**：
    *   向下滚动到 **Workflow permissions** 部分。
    *   选择 **Read and write permissions** 选项。
    *   点击 **Save**。

完成此设置后，自动化工作流才能正常运行。

## 如何贡献

由于这是一个自动生成的仓库，请不要直接向本仓库提交 Pull Request 来修改规则。所有的规则都源自上游的 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) 项目。如果您想贡献规则，请向上游项目提交您的更改。
