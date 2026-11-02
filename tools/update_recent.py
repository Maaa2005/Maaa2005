"""README.md の「最近の更新」欄を、公開リポジトリの最新コミットで書き換える。

GitHub Actions（.github/workflows/recent.yml）から毎朝動かす。
取得に失敗したときは README を変えずに終わる（ページを壊さないため）。
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request

OWNER = "Maaa2005"
# 載せるリポジトリ（プロフィールに出している作品だけ）。共同のリポもあるので、本人のコミットだけを読む
REPOS = [
    "Stellise",
    "web-capability-compiler",
    "aun-protocol",
    "KASANE",
    "local-rag-agent",
]
LIMIT = 4
START, END = "<!-- recent:start -->", "<!-- recent:end -->"
JST = dt.timezone(dt.timedelta(hours=9))


def fetch(url, token):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-recent"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.load(res)


def is_bot(commit):
    login = ((commit.get("author") or {}).get("login") or "").lower()
    name = (commit.get("commit", {}).get("author", {}).get("name") or "").lower()
    return login.endswith("[bot]") or "dependabot" in login or name.endswith("[bot]")


SKIP = re.compile(r"^(merge branch|(chore|build|ci)\(deps\)|chore: bump|bump )", re.I)


def headline(message):
    """見せる1行を返す。依存の更新や中身の無いマージは None。

    「Merge pull request #n from ...」は本文にある変更依頼の題名を使う。
    """
    lines = [ln.strip() for ln in message.strip().splitlines()]
    first = lines[0] if lines else ""
    if first.lower().startswith("merge pull request"):
        first = next((ln for ln in lines[1:] if ln), "")
    if not first or SKIP.match(first):
        return None
    return first


def latest_human_commit(commits):
    """人が書いた、見せる価値のある最新コミットと、その1行を返す。"""
    for c in commits:
        if is_bot(c):
            continue
        line = headline(c.get("commit", {}).get("message", ""))
        if line:
            return c, line
    return None


def build_lines(items):
    """items: (repo, datetime, subject, url) のリスト。新しい順に LIMIT 件を行にする。"""
    items = sorted(items, key=lambda x: x[1], reverse=True)[:LIMIT]
    lines = []
    for repo, when, subject, url in items:
        subject = subject.replace("|", "/").replace("<", "‹").replace(">", "›")
        if len(subject) > 60:
            subject = subject[:59] + "…"
        lines.append(f"- <samp>{when.astimezone(JST):%m/%d}</samp>　**[{repo}]({url})** — {subject}")
    return lines


def replace_block(text, lines):
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("markers not found in README")
    body = "\n".join([START, *lines, END])
    return pattern.sub(lambda _: body, text)


def main():
    readme = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    token = os.environ.get("GITHUB_TOKEN", "")
    items = []
    for repo in REPOS:
        try:
            commits = fetch(f"https://api.github.com/repos/{OWNER}/{repo}/commits?author={OWNER}&per_page=50", token)
        except Exception as e:  # 1つ失敗しても他は載せる
            print(f"skip {repo}: {e}", file=sys.stderr)
            continue
        found = latest_human_commit(commits)
        if not found:
            continue
        c, line = found
        when = dt.datetime.fromisoformat(c["commit"]["committer"]["date"].replace("Z", "+00:00"))
        items.append((repo, when, line, f"https://github.com/{OWNER}/{repo}"))
    if not items:
        print("no data; README unchanged", file=sys.stderr)
        return
    with open(readme, encoding="utf-8") as fh:
        text = fh.read()
    new = replace_block(text, build_lines(items))
    if new != text:
        with open(readme, "w", encoding="utf-8") as fh:
            fh.write(new)
        print("README updated")
    else:
        print("no change")


if __name__ == "__main__":
    main()
