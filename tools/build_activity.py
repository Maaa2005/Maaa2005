"""毎日の積み重ね assets/activity-dark.svg・assets/activity-light.svg を作る。

GitHub の草（この1年の日ごとの活動数）を読み、プロフィールと同じ色で描く。
GitHub Actions（.github/workflows/recent.yml）が毎朝動かす。取得に失敗したときは何も書き換えない。
手元で試すときは --placeholder（集計前の空の表）か --sample（形を見るための作り物の数字）を付ける。
--sample の画像はコミットしないこと。
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request

OWNER = "Maaa2005"
ASSETS = next((a for a in sys.argv[1:] if not a.startswith("--")), "assets")
W, H = 880, 256
CELL, GAP = 12, 3
X0, Y0 = 44, 110

THEMES = {
    "dark": dict(bg="#161B22", border="#30363D", fg="#E6EDF3", sub="#8B949E", accent="#B4A7FF",
                 levels=["#252B35", "#2E2A55", "#4B3FA0", "#7B6CE0", "#C9C1FF"]),
    "light": dict(bg="#FFFFFF", border="#E4E1F0", fg="#1C1A2B", sub="#6E6A86", accent="#6D5BD0",
                  levels=["#EEEBF7", "#DCD6FB", "#B4A7FF", "#8B7CF6", "#5B48C2"]),
}
QUERY = """query($login: String!) { user(login: $login) { contributionsCollection {
  contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } } }"""
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch(token):
    body = json.dumps({"query": QUERY, "variables": {"login": OWNER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-activity"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    return weeks, cal["totalContributions"]


def sample_weeks(seed=7):
    """形を見るためだけの作り物。コミットしない。"""
    rnd = random.Random(seed)
    end = dt.date(2026, 11, 2)
    start = end - dt.timedelta(days=end.weekday() + 1 + 52 * 7)
    weeks, day = [], start
    while day <= end:
        week = []
        for _ in range(7):
            if day > end:
                break
            busy = 0.35 + 0.6 * (day - start).days / 371
            week.append((day.isoformat(), rnd.choice([0, 0, 1, 2, 3, 5, 8, 13]) if rnd.random() < busy else 0))
            day += dt.timedelta(days=1)
        weeks.append(week)
    return weeks, sum(c for w in weeks for _, c in w)


def level(count, cuts):
    if count <= 0:
        return 0
    for i, c in enumerate(cuts, start=1):
        if count <= c:
            return i
    return 4


def streak(weeks):
    days = [c for w in weeks for _, c in w]
    n = 0
    for c in reversed(days):
        if c > 0:
            n += 1
        elif n == 0:
            continue  # 今日がまだ0なら昨日から数える
        else:
            break
    return n


def render(weeks, total, theme, placeholder=False):
    t = THEMES[theme]
    counts = sorted(c for w in weeks for _, c in w if c > 0)
    cuts = [counts[int(len(counts) * q)] for q in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]
    cells, months, last_month, last = [], [], None, (X0, Y0)
    for x, week in enumerate(weeks):
        for date, count in week:
            d = dt.date.fromisoformat(date)
            y = (d.weekday() + 1) % 7  # 日曜が一番上
            lv = 0 if placeholder else level(count, cuts)
            cx, cy = X0 + x * (CELL + GAP), Y0 + y * (CELL + GAP)
            cells.append(f'<rect x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" rx="3" fill="{t["levels"][lv]}"/>')
            last = (cx, cy)
            if d.day <= 7 and y == 0 and d.month != last_month:
                months.append(f'<text x="{cx}" y="{Y0 - 10}" class="m">{MONTHS[d.month - 1]}</text>')
                last_month = d.month
    s = streak(weeks)
    if placeholder:
        head = f'<text x="{X0}" y="54" class="big">—</text><text x="{X0}" y="74" class="lab">updating every morning</text>'
    else:
        head = (f'<text x="{X0}" y="54" class="big">{total:,}</text>'
                f'<text x="{X0}" y="74" class="lab">contributions in the last year</text>')
        if s >= 7:
            head += (f'<text x="{W - X0}" y="54" class="big" text-anchor="end">{s}</text>'
                     f'<text x="{W - X0}" y="74" class="lab" text-anchor="end">day streak</text>')
    legend_x = W - X0 - 5 * (CELL + 3) - 34
    legend = (f'<text x="{legend_x - 8}" y="{H - 22}" class="m" text-anchor="end">Less</text>'
              + "".join(f'<rect x="{legend_x + i * (CELL + 3)}" y="{H - 32}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>' for i, c in enumerate(t["levels"]))
              + f'<text x="{legend_x + 5 * (CELL + 3) + 6}" y="{H - 22}" class="m">More</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub の活動（この1年、日ごと）">
  <style>
    .big {{ font: italic 400 34px 'Instrument Serif', 'Iowan Old Style', Georgia, serif; fill: {t["fg"]}; }}
    .lab {{ font: 400 12px -apple-system, 'Segoe UI', Inter, sans-serif; fill: {t["sub"]}; }}
    .m {{ font: 400 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: {t["sub"]}; }}
    .today {{ fill: none; stroke: {t["accent"]}; stroke-width: 1.5; animation: pulse 2.8s ease-in-out infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity: .25; }} 50% {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{ .today {{ animation: none; opacity: .8; }} }}
  </style>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{t["bg"]}" stroke="{t["border"]}"/>
  {head}
  {''.join(months)}
  {''.join(cells)}
  <rect class="today" x="{last[0] - 2.5}" y="{last[1] - 2.5}" width="{CELL + 5}" height="{CELL + 5}" rx="4.5"/>
  {legend}
</svg>
'''


def main():
    if "--placeholder" in sys.argv or "--sample" in sys.argv:
        weeks, total = sample_weeks()
        placeholder = "--placeholder" in sys.argv
    else:
        token = os.environ.get("GITHUB_TOKEN", "")
        try:
            weeks, total = fetch(token)
        except Exception as e:  # 取れなければ前の画像のまま
            print(f"activity: fetch failed, unchanged: {e}", file=sys.stderr)
            return
        placeholder = False
    for theme in THEMES:
        out = os.path.join(ASSETS, f"activity-{theme}.svg")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(render(weeks, total, theme, placeholder))
        print("wrote", out)


if __name__ == "__main__":
    main()
