
# V2Fly Domain List Community - Clash Rule-Set

这是一个自动化的项目，旨在将 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) 的域名列表转换为适用于 [Clash](https://github.com/Dreamacro/clash) 的 `RULE-SET` 格式。

## 项目目标

`domain-list-community` 项目提供了高质量、社区维护的域名列表，用于路由决策。然而，其原生格式（`dat` 文件）并不直接兼容 Clash 的 `RULE-SET`。本项目通过 GitHub Actions 实现了自动化转换，为 Clash 用户提供即用型的规则集。

## 规则文件

所有的规则文件都生成在 `clash-rules-generated/` 目录下。

### 主要规则

该目录下的每个 `.txt` 文件都对应 `domain-list-community` 中的一个域名列表。您可以直接在您的 Clash 配置文件中使用这些文件的 URL。

例如，要使用 `google` 规则集，您可以在配置文件中这样写：

```yaml
rule-providers:
  google:
    type: http
    behavior: classical
    url: "https://raw.githubusercontent.com/busymilk/v2fly-domain-list-community_rule_set/main/clash-rules-generated/google.txt"
    path: ./ruleset/google.rules
    interval: 86400
```

### 聚合标签规则

为了方便使用，本项目还提供了根据源文件中的 `@` 标签（如 `@ads`, `@cn`）聚合而成的特殊规则文件：

- `collect_tag_ads.txt`: 聚合了所有被标记为广告（`@ads`）的域名。
- `collect_tag_cn.txt`: 聚合了所有被明确标记为中国大陆（`@cn`）的域名。
- `collect_tag_!cn.txt`: 聚合了所有非中国大陆（`@!cn`）的域名。

这些文件对于实现常见的广告屏蔽和分流策略非常有用。

## 自动化更新

本仓库通过 GitHub Actions 自动执行以下流程：

1.  **每日拉取**：每天定时从 `v2fly/domain-list-community` 拉取最新的规则。
2.  **自动转换**：运行 Python 脚本，将规则转换为 Clash `RULE-SET` 格式，并处理所有 `include:` 标签。
3.  **标签处理**：自动收集带 `@` 标签的域名，生成聚合规则文件，并从原始文件中移除标签以确保兼容性。
4.  **提交推送**：将更新后的规则文件自动提交并推送到本仓库。

## 如何贡献

由于这是一个自动生成的仓库，请不要直接向本仓库提交 Pull Request 来修改规则。所有的规则都源自上游的 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) 项目。如果您想贡献规则，请向上游项目提交您的更改。
