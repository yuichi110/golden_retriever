# Architecture Plan: Golden Rules & Practical Samples Engine for AI Agents

- **Status**: Accepted
- **Target Project**: `golden_retriever` (`gret`)
- **Author**: Antigravity & Yuichi Ito
- **Date**: 2026-10-26 (Updated)

---

## 1. Executive Summary & Objective

本設計は、AI コーディングエージェント（Antigravity, Cursor, Claude Code, GitHub Copilot 等）が、**MCP (Model Context Protocol) などの複雑な設定なしに、ローカル CLI コマンド (`gret`) を通じて組織の「ゴールデンルール（設計・規約）」および「実践的な動くサンプルコード（uv / Docker 等）」を自律取得・参照・適用できるようにする** ためのアーキテクチャ計画です。

先行プロジェクト（`drawlib` の `_rules` 実装）の実績をベースとしつつ、以下の要件を満たす洗練されたフラット設計を採用します。

1. **ゼロコンフィグ & ポータビリティ**:
   `src/gret` にルール（Markdown）と実コード（Examples）を内包し、`uvx gret` 単体で完全オフライン・ゼロコンフィグで即座に動作可能にする。
2. **フラットで無駄のない構成**:
   過剰なサブパッケージや `builtin/` ネストを排除し、`src/gret/*.py`, `src/gret/rules/**/*.md`, `src/gret/examples/**` の直感的かつ対称的な配置にする。
3. **完全対称なカスケード上書き（Override）機構**:
   プロジェクトローカル（`.gret/`）に同名ファイルを置くだけで、内蔵ルール・サンプルを 1対1 で完全にオーバーライドできるようにする。
4. **本体開発のクリーンさの維持**:
   実コードサンプル（`examples/`）は依存実体（`node_modules`, `.venv`）を含めず純粋なソースコードのみとし、本体の `ruff` / `ty` / `pytest` から除外することで見通しを保つ。

---

## 2. Directory Layout

無駄な階層を作らず、ロジックとコンテンツを明確に分けたフラット構成とします。

```text
golden_retriever/
├── pyproject.toml              # gret CLI 本体のビルド・依存定義 (uv)
├── README.md
├── .agents/
│   ├── plans/
│   │   └── rules_and_samples_architecture.md
│   └── rules/
│       └── code-style-guide.md
├── src/
│   └── gret/
│       ├── __init__.py
│       ├── cli.py              # メインエントリーポイント & サブコマンド登録
│       ├── rules.py            # rules サブコマンド (list, show, search, bootstrap)
│       ├── samples.py          # sample サブコマンド (list, tree, cat, init)
│       ├── config.py           # パス解決 (ローカル .gret/ -> ユーザー設定 -> 内蔵 のカスケード探索)
│       │
│       ├── rules/              # ★ 標準ゴールデンルール (Markdown)
│       │   ├── python/
│       │   │   ├── error-handling.md
│       │   │   └── project-structure.md
│       │   └── api/
│       │       └── rest-design.md
│       │
│       └── examples/           # ★ 実践的な動くサンプル群 (独立プロジェクト)
│           └── python/
│               └── fastapi-simple/
│                   ├── pyproject.toml  # サンプル独自の uv 設定
│                   ├── Dockerfile
│                   ├── docker-compose.yml
│                   ├── README.md
│                   └── src/ ...
└── tests/
    └── gret/
        ├── test_cli.py
        ├── test_rules.py
        └── test_samples.py
```

---

## 3. Core Architectural Mechanisms

### 3.1. 完全対称なカスケード解決（Cascade Lookup）
ルールおよびサンプルは、同一の相対パス構造で探索されます。

```text
【探索順序（優先度順）】
1. カレントプロジェクト固有:  ./.gret/rules/<topic>.md
                           ./.gret/examples/<topic>/
2. ユーザー・組織設定:        ~/.config/gret/rules/<topic>.md
                           ~/.config/gret/examples/<topic>/
3. 内蔵デフォルト (Built-in): src/gret/rules/<topic>.md
                           src/gret/examples/<topic>/
```

- **メリット**:
  内蔵パスと上書きパスが `rules/...` および `examples/...` で 1対1 に完全対応するため、パス解決ロジックが極限までシンプルになり、ユーザーにとっても直感的に上書きが可能です。
- **Python 3.11+ `importlib.resources` での堅牢な内蔵パス解決**:
  ```python
  from importlib.resources import files

  builtin_rules_dir = files("gret").joinpath("rules")
  builtin_examples_dir = files("gret").joinpath("examples")
  ```

### 3.2. ツール競合の防止（`pyproject.toml` 設定）
`src/gret/examples/` 配下のサンプルプロジェクトは独立した環境を持つため、ルートのリンターやテストが誤検知しないよう除外設定を行います。

```toml
[tool.ruff]
extend-exclude = ["src/gret/examples"]

[tool.pytest.ini_options]
addopts = "--ignore=src/gret/examples"
```

---

## 4. CLI Command Specification

### 4.1. `gret rules` (ルール参照)

| コマンド | 説明 | 主な出力 |
| :--- | :--- | :--- |
| `gret rules list` | 利用可能なルールトピック一覧と概要を表示 | 一覧テキスト（カテゴリ別） |
| `gret rules show <topic>` | 指定トピックのルール全文を Markdown 形式で表示 | Markdown (stdout) |
| `gret rules search <query>` | キーワードでルール・トピックを全文検索 | 関連トピック候補 |
| `gret rules bootstrap` | AI Agent の指示書 (`AGENTS.md`) に貼るプロンプトを出力 | ガイド文 (stdout) |

> **AI エラー自己修復**:
> 存在しないトピックが指定された場合は、エラー出力と共に利用可能なトピック一覧と `Did you mean ...?` を返し、AI Agent が自律的に正しいトピックを指定し直せるようにする。

### 4.2. `gret sample` (サンプルコード閲覧 & スキャフォールド)

| コマンド | 説明 | AI のユースケース |
| :--- | :--- | :--- |
| `gret sample list` | 利用可能な実動サンプル一覧を表示 | どんな構成があるか探索 |
| `gret sample tree <topic>` | サンプルのファイルツリー構造を表示 | 構成を把握（ファイルは汚さない） |
| `gret sample cat <topic> <path>` | 指定ファイルのコードを標準出力に表示 | 特定の `Dockerfile` 等を1ターンで閲覧 |
| `gret sample init <topic> [dest]` | 指定ディレクトリに実動サンプル一式を展開 | スキャフォールディングによる開発開始 |

---

## 5. Phased Implementation Roadmap

### Phase 1: `gret rules` の実装（ルール参照基盤）
- [ ] `src/gret/rules.py` を作成し、Typer サブコマンド `rules`（`list`, `show`）を実装。
- [ ] `src/gret/rules/` ディレクトリを作成し、パイロット版ルール（例: `python/error-handling.md`）を追加。
- [ ] `gret rules bootstrap` を実装し、エージェント向け指示プロンプトを出力可能にする。
- [ ] 単体テスト（`tests/gret/test_rules.py`）を追加。

### Phase 2: カスケード探索 & 上書き機能
- [ ] `src/gret/config.py` にカスケード探索（`.gret/` -> `~/.config/gret/` -> `src/gret/`）ロジックを実装。
- [ ] プロジェクトローカルでのルール上書き動作テストを追加。
- [ ] 存在しないトピック指定時の「Did you mean?」サジェスト機能を追加。

### Phase 3: `gret sample` の実装（実践サンプル基盤）
- [ ] `src/gret/samples.py` を作成し、Typer サブコマンド `sample`（`list`, `tree`, `cat`, `init`）を実装。
- [ ] `src/gret/examples/` ディレクトリを作成し、パイロット版実動サンプル（例: `python/fastapi-simple/`）を追加。
- [ ] `pyproject.toml` にリンター・テストの exclude 設定（`src/gret/examples`）を追加。
- [ ] 単体テスト（`tests/gret/test_samples.py`）を追加。

### Phase 4: CI & エコシステム整備
- [ ] サンプルプロジェクト群を検証する専用コマンド（例: `./gcli test examples`）を整備。
- [ ] README に `gret rules` と `gret sample` の使用例と AI 連携ガイドを追記。
