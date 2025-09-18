#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI PR Review runner
- PR差分を取得（pull_request なら base..head、手動なら HEAD^..HEAD）
- 日本語プロンプトを作成
- OpenAI Chat Completions に投げる
- PR にコメント投稿

依存: requests
環境変数: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL, (任意)OPENAI_PROJECT, GITHUB_TOKEN
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple

import requests


def run(cmd: list[str], check: bool = True, text: bool = True) -> str:
    res = subprocess.run(cmd, capture_output=True, text=text)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{res.stderr}")
    return res.stdout


def load_event() -> dict:
    p = os.getenv("GITHUB_EVENT_PATH")
    if not p or not Path(p).exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_base_head(event: dict) -> Tuple[str, str, int]:
    """
    pull_request イベントなら base/head/PR番号、
    それ以外（workflow_dispatch等）は HEAD^..HEAD で比較。
    """
    if event.get("pull_request"):
        pr = event["pull_request"]
        base = pr.get("base", {}).get("sha", "")
        head = pr.get("head", {}).get("sha", "")
        number = pr.get("number") or event.get("number")
        return base or "", head or "", int(number)
    # 手動実行など
    head = run(["git", "rev-parse", "HEAD"]).strip()
    try:
        base = run(["git", "rev-parse", "HEAD^"]).strip()
    except Exception:
        base = ""
    return base, head, 0


def build_diff(base: str, head: str) -> Tuple[str, str]:
    """
    base..head の unified diff（0行コンテキスト）と変更ファイル一覧。
    50KB にトリムした diff も返す。
    """
    if not head:
        return "", ""
    if base:
        try:
            run(["git", "fetch", "--no-tags", "--depth=1", "origin", base], check=False)
        except Exception:
            pass

    diff = run(["git", "diff", "--unified=0", base, head], check=False)
    files = run(["git", "diff", "--name-only", base, head], check=False).replace("\n", " ").strip()

    if not diff.strip():
        return "", files

    # 50KB truncate
    diff_bytes = diff.encode("utf-8")
    trunc = diff_bytes[: 50 * 1024].decode("utf-8", errors="ignore")
    return trunc, files


def build_prompt(diff_preview: str, files: str) -> str:
    header = """あなたは熟練のソフトウェアレビュアです。以下の「PR差分（unified diff）」を読み、**日本語**でレビューしてください。

# 出力（Markdown）
- **概要**（3～6行）：最重要の改善点の要約
- **指摘（重要度ラベル付き）**：
  - ラベル：`BLOCKER` / `MAJOR` / `MINOR` / `NICE`
  - 箇条書きで、可能なら `path:line` を明示（不明なら「行特定不可」と記載）
  - **根拠・理由**、**代替案**、**短いコード断片** を添付
- **観点**：セキュリティ/安全性、性能、可読性/保守性、テスト（境界値/失敗系/fixture/CI）
- **パッチ提案（任意）**：小規模修正は差分断片を Markdown で
- **総評** と **次アクション**

# 方針
- 差分にないコードの詳細は仮定しない
- 行番号やファイル名の“でっち上げ”は禁止（不明は不明と明記）
- 冗長説明より **actionable** を優先
- Python：I/O例外、型/None、リソース解放、pytestのfixture/capsys/tmp_path
- C：未初期化、境界チェック、安全API、寿命/所有権、size_t/符号、errno、free/close漏れ
- Makefile/CI：並列安定性、キャッシュ、ログの可観測性、偽陽性抑制
- 大規模差分は危険箇所を優先し、残りはサマリ
"""
    body = f"""
---
[変更ファイル]
{files}
---
[差分プレビュー(最大約50KB)]
{diff_preview}
""".strip()
    return header + "\n\n" + body


def call_openai(prompt: str) -> Tuple[int, str, dict]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    project = os.getenv("OPENAI_PROJECT", "").strip()

    if not api_key:
        return 0, "OpenAI API key is empty", {}

    url = f"{base}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if project:
        headers["OpenAI-Project"] = project

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "あなたは一流のコードレビュアです。出力は日本語のMarkdownで、簡潔かつ行動可能に。"},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        try_json = r.json()
    except Exception as e:
        return -1, f"OpenAI request failed: {e}", {}

    if r.status_code != 200:
        err = try_json.get("error", {}).get("message") if isinstance(try_json, dict) else None
        return r.status_code, f"OpenAI HTTP {r.status_code}: {err or '(no message)'}", try_json

    content = try_json.get("choices", [{}])[0].get("message", {}).get("content", "") or "(empty output)"
    return 200, content, try_json


def post_comment_to_pr(event: dict, body_md: str) -> None:
    if not event.get("pull_request"):
        print("No PR context (probably workflow_dispatch). Skipping comment.")
        return
    token = os.getenv("GITHUB_TOKEN", "")
    repo = os.getenv("GITHUB_REPOSITORY", "")
    if not token or not repo:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY missing. Skipping comment.")
        return

    owner, repo_name = repo.split("/")
    pr_number = event["pull_request"]["number"]

    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    data = {"body": body_md}

    resp = requests.post(url, headers=headers, json=data, timeout=30)
    if resp.status_code >= 300:
        print(f"Failed to post comment: HTTP {resp.status_code} {resp.text}", file=sys.stderr)


def main() -> int:
    event = load_event()
    base, head, _ = resolve_base_head(event)

    diff_preview, files = build_diff(base, head)
    if not diff_preview.strip():
        msg = "AIレビュー: 対象となるコード差分が見つかりませんでした。"
        print(msg)
        post_comment_to_pr(event, msg)
        return 0

    prompt = build_prompt(diff_preview, files)
    code, out, raw = call_openai(prompt)

    # デバッグ用アーティファクト（任意で保存してもらえる）
    Path("prompt.txt").write_text(prompt, encoding="utf-8")
    Path("openai_raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    body = f"<!-- ai-pr-review:jp -->\n\n{out if code == 200 else f'OpenAI API error: {out}'}"
    print(body)
    post_comment_to_pr(event, body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
