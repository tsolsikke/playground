#!/usr/bin/env python3
"""
AI PR Review script for GitHub Actions.

- 使い方（Actions想定）:
  1) actions/checkout の後にこのスクリプトを実行
  2) OPENAI_API_KEY と GITHUB_TOKEN を env で渡す
  3) pull_request イベントであれば、PR番号・base/head は自動取得
  4) 差分を OpenAI へ投げて、レビュー結果を PR にコメント投稿

- 追加の引数（ローカル実行や手動指定用）:
  --base <base_ref_or_sha>
  --head <head_ref_or_sha>
  --pr <number>
  --repo <owner/repo>
  --model <openai_model> (default: gpt-4o-mini)
  --max-chars <N>        (diffをN文字に切り詰め、過大トークンを防止・既定: 40000)

標準ライブラリのみで動作（requests不要）
"""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import textwrap
import urllib.request
import urllib.error

# ---------- Utilities ----------

def run(cmd: list[str], check: bool = True) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDERR:\n{p.stderr}")
    return p.stdout

def env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)

def read_event_payload() -> dict | None:
    """GITHUB_EVENT_PATH があれば読み込む"""
    p = env("GITHUB_EVENT_PATH")
    if not p or not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# ---------- Diff collection ----------

def resolve_base_head(args) -> tuple[str, str]:
    # 優先度: 引数 > イベントペイロード > 環境変数
    base = args.base
    head = args.head

    payload = read_event_payload()
    if not base and payload and "pull_request" in payload:
        base = payload["pull_request"]["base"]["sha"]
    if not head and payload and "pull_request" in payload:
        head = payload["pull_request"]["head"]["sha"]

    if not base:
        base = env("GITHUB_BASE_SHA") or env("GITHUB_BASE_REF")  # 例: "main"
    if not head:
        head = env("GITHUB_SHA")  # 現在の HEAD

    if not base or not head:
        raise SystemExit("ERROR: base/head が特定できません。--base/--head を指定してください。")

    # fetch して diff 可能にしておく（base が ref 名の場合も sha の場合も網羅）
    try:
        run(["git", "fetch", "origin", "--depth=1", str(base)], check=False)
    except Exception:
        pass
    return base, head

def collect_diff(base: str, head: str) -> str:
    # 統一diff（最小行数）で十分。巨大PR向けに必要なら -- . ':!docs' 等の除外も可能
    diff = run(["git", "diff", "--unified=0", f"{base}...{head}"], check=False)
    if not diff.strip():
        diff = "(No changes in diff or empty diff)"
    return diff

def trim(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    suffix = f"\n\n[diff was truncated to first {limit} characters]"
    return text[:max(0, limit - len(suffix))] + suffix

# ---------- OpenAI ----------

def openai_chat(api_key: str, model: str, user_content: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"

    sys_prompt = (
        "あなたは厳密で経験豊富なコードレビュアーです。"
        "以下に示す unified diff をレビューしてください。"
        "論理的なバグ、エッジケース、セキュリティリスク、性能、可読性、"
        "テスト、Python/C のベストプラクティスへの準拠に注目してください。"
        "指摘は箇条書きで、可能であればコード例も含めてください。"
        "必ず日本語で出力してください。"
    )

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise SystemExit(f"OpenAI API error: {e.code} {e.reason}\n{detail}")
    except Exception as e:
        raise SystemExit(f"OpenAI API request failed: {e}")

    try:
        return payload["choices"][0]["message"]["content"].strip()
    except Exception:
        return json.dumps(payload, indent=2)

# ---------- GitHub comment ----------

def post_pr_comment(repo: str, pr_number: int, body: str, token: str) -> None:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    data = json.dumps({"body": body}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as _:
            pass
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise SystemExit(f"GitHub comment failed: {e.code} {e.reason}\n{detail}")

def detect_pr_context(args) -> tuple[str, int]:
    # repo: owner/name
    repo = args.repo or env("GITHUB_REPOSITORY")
    if not repo:
        raise SystemExit("ERROR: repo が不明です。--repo か GITHUB_REPOSITORY を指定してください。")

    pr_number = args.pr
    if not pr_number:
        payload = read_event_payload()
        if payload and "pull_request" in payload:
            pr_number = payload["pull_request"]["number"]
    if not pr_number:
        # 手動実行なら手入力してね
        raise SystemExit("ERROR: PR番号が不明です。--pr を指定するか pull_request イベントで実行してください。")

    return repo, int(pr_number)

# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--head")
    ap.add_argument("--pr", type=int)
    ap.add_argument("--repo")  # owner/name
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    ap.add_argument("--max-chars", type=int, default=int(os.environ.get("REVIEW_MAX_CHARS", "40000")))
    args = ap.parse_args()

    openai_api_key = env("OPENAI_API_KEY")
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        return 2

    base, head = resolve_base_head(args)
    diff = collect_diff(base, head)
    diff_trimmed = trim(diff, args.max_chars)

    prompt = textwrap.dedent(f"""
    Please review the following Git unified diff between base `{base}` and head `{head}`.
    Provide bullet-point feedback. When suggesting changes, include minimal code snippets.

    --- BEGIN DIFF ---
    {diff_trimmed}
    --- END DIFF ---
    """).strip()

    review = openai_chat(openai_api_key, args.model, prompt)

    # 出力を常に標準出力へ（ログとして残す）
    print("===== AI REVIEW START =====")
    print(review)
    print("===== AI REVIEW END =====")

    # PRコメント投稿（GITHUB_TOKEN があれば自動でコメント）
    gh_token = env("GITHUB_TOKEN") or env("GH_TOKEN")
    if gh_token:
        try:
            repo, pr_number = detect_pr_context(args)
            post_pr_comment(repo, pr_number, review, gh_token)
            print(f"Posted AI review as PR comment on {repo}#{pr_number}")
        except SystemExit as e:
            # 文脈がないならコメント投稿はスキップ（標準出力のみ）
            print(str(e), file=sys.stderr)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
