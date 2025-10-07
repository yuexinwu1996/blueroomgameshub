from __future__ import annotations
from typing import Optional, List
import json
import math
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "assets" / "data"
OUTPUT_DIR = ROOT

SITE_NAME = "Blue Room Games Hub"
SITE_URL = "https://www.blueroomgameshub.com"
DEFAULT_DESCRIPTION = (
    "Discover immersive escape room games and detailed walkthroughs curated by the Blue Room Games Hub team."
)

with open(DATA_DIR / "games.json", encoding="utf-8") as fh:
    GAMES = json.load(fh)

with open(DATA_DIR / "guides.json", encoding="utf-8") as fh:
    GUIDES = json.load(fh)

GAMES_BY_SLUG = {game["slug"]: game for game in GAMES}
GUIDES_BY_SLUG = {guide["slug"]: guide for guide in GUIDES}

def trending_score(game: dict) -> float:
    return (0.7 * game.get("pv7_norm", 0.0)) + (0.2 * game.get("guide_clicks7_norm", 0.0)) + (0.1 * game.get("recency", 0.0))


def add_game_to_data(game_data: dict, guide_data: dict) -> None:
    """
    添加新游戏到数据文件

    Args:
        game_data: 游戏数据字典
        guide_data: 攻略数据字典
    """
    # 读取现有数据
    games_file = DATA_DIR / "games.json"
    guides_file = DATA_DIR / "guides.json"

    with open(games_file, encoding="utf-8") as fh:
        games = json.load(fh)

    with open(guides_file, encoding="utf-8") as fh:
        guides = json.load(fh)

    # 检查是否已存在（通过slug）
    existing_game = next((g for g in games if g["slug"] == game_data["slug"]), None)
    if existing_game:
        # 更新现有游戏
        games = [g if g["slug"] != game_data["slug"] else game_data for g in games]
    else:
        # 添加新游戏
        games.append(game_data)

    existing_guide = next((g for g in guides if g["slug"] == guide_data["slug"]), None)
    if existing_guide:
        # 更新现有攻略
        guides = [g if g["slug"] != guide_data["slug"] else guide_data for g in guides]
    else:
        # 添加新攻略
        guides.append(guide_data)

    # 重新计算排行
    games = recalculate_rankings(games)

    # 保存回文件
    with open(games_file, "w", encoding="utf-8") as fh:
        json.dump(games, fh, indent=2, ensure_ascii=False)

    with open(guides_file, "w", encoding="utf-8") as fh:
        json.dump(guides, fh, indent=2, ensure_ascii=False)

    print(f"✅ 成功添加/更新游戏: {game_data['title']}")
    print(f"✅ 成功添加/更新攻略: {guide_data['title']}")


def recalculate_rankings(games: list) -> list:
    """
    重新计算所有游戏的排行分数

    Args:
        games: 游戏列表

    Returns:
        更新后的游戏列表
    """
    # 按评分和新鲜度重新排序
    # Trending分数已经在trending_score函数中计算
    # 这里可以添加更多排行逻辑

    # 按添加日期计算recency（最新的recency=1.0）
    games_with_dates = [(g, g.get("created_date", "2024-01-01")) for g in games]
    games_with_dates.sort(key=lambda x: x[1], reverse=True)

    max_index = len(games_with_dates) - 1
    for i, (game, _) in enumerate(games_with_dates):
        # 线性衰减：最新的=1.0，最老的=0.1
        game["recency"] = 1.0 - (i / max_index * 0.9) if max_index > 0 else 1.0

    return games


def normalise_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def format_date(value: str) -> str:
    return normalise_date(value).strftime("%d %b %Y")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def render_head(title: str, description: str, canonical: str, extra_meta: str = "") -> str:
    return f"""  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{title}</title>
    <meta name=\"description\" content=\"{description}\">
    <link rel=\"canonical\" href=\"{canonical}\">
    <link rel=\"stylesheet\" href=\"/assets/css/main.css\">
    <link rel=\"preload\" href=\"/assets/js/global.js\" as=\"script\">
    {extra_meta}
  </head>"""


def render_nav(active: str = "") -> str:
    def nav_link(href: str, label: str) -> str:
        is_active = " aria-current=\"page\"" if active == href else ""
        return f"<a href=\"{href}\"{is_active}>{label}</a>"

    return f"""  <header class=\"site-header\">
    <div class=\"container\">
      <nav class=\"site-nav\" aria-label=\"Primary\">
        <a class=\"site-brand\" href=\"/\">{SITE_NAME}</a>
        <div class=\"site-nav-links\">
          {nav_link('/', 'Home')}
          {nav_link('/games/', 'Games')}
          {nav_link('/guides/', 'Guides')}
          {nav_link('/about/', 'About')}
          {nav_link('/privacy-policy/', 'Privacy')}
        </div>
        <div class=\"search-shell\" data-search>
          <form data-search-form role=\"search\" aria-label=\"Site search\">
            <label class=\"visually-hidden\" for=\"global-search\">Search site content</label>
            <input id=\"global-search\" type=\"search\" name=\"q\" placeholder=\"Search guides or games\" autocomplete=\"off\">
            <button type=\"submit\" aria-label=\"Search\">🔍</button>
          </form>
          <div class=\"search-results-panel\" data-search-results aria-expanded=\"false\"></div>
        </div>
      </nav>
    </div>
  </header>"""


def render_footer() -> str:
    return """  <footer class=\"site-footer\">
    <div class=\"container\">
      <div class=\"footer-grid\">
        <div>
          <strong>Blue Room Games Hub</strong><br>
          Escape, puzzle, and strategy news for dedicated players.
        </div>
        <div>
          <a href=\"/privacy-policy/\">Privacy policy</a> · <a href=\"/about/\">About</a>
        </div>
        <div>
          © <span id=\"current-year\">2024</span> Blue Room Games Hub. All rights reserved.
        </div>
      </div>
    </div>
  </footer>
  <script src=\"/assets/js/global.js\" defer></script>"""


def render_base(title: str, description: str, canonical_path: str, body: str, active: str = "", extra_head: str = "", scripts: Optional[List[str]] = None) -> str:
    canonical = f"{SITE_URL.rstrip('/')}{canonical_path}"
    script_tags = "".join(f"\n  <script src=\"{src}\" defer></script>" for src in (scripts or []))
    return f"""<!DOCTYPE html>
<html lang=\"en\">
{render_head(title, description, canonical, extra_head)}
<body>
{render_nav(active)}
  <main>
    <div class=\"container\">
{body}
    </div>
  </main>
{render_footer()}{script_tags}
</body>
</html>
"""


def render_game_card(game: dict) -> str:
    mechanism_html = "".join(f"<span class=\"pill\">{m}</span>" for m in game.get("mechanisms", [])[:3])
    difficulty = game.get("difficulty", "")
    summary = game.get("summary", "")
    return f"""        <article class=\"game-card\">
          <img src=\"{game['thumbnail']}\" alt=\"{game['title']} cover\" loading=\"lazy\" width=\"320\" height=\"180\">
          <div>
            <span class=\"badge-soft\">{difficulty}</span>
            <h3>{game['title']}</h3>
            <p>{summary}</p>
          </div>
          <div class=\"pill-row\">{mechanism_html}</div>
          <div class=\"card-actions\">
            <a class=\"button-link primary\" href=\"{game['play_url']}\" target=\"_blank\" rel=\"noopener\">Play now</a>
            <a class=\"button-link secondary\" href=\"/games/{game['slug']}/\">Details</a>
          </div>
        </article>"""


def render_guide_card(guide: dict) -> str:
    rating = guide.get("rating", "")
    difficulty = guide.get("difficulty", "")
    summary = guide.get("summary", "")
    return f"""        <article class=\"guide-card\">
          <img src=\"{guide['thumbnail']}\" alt=\"{guide['title']} cover\" loading=\"lazy\" width=\"320\" height=\"180\">
          <div>
            <span class=\"badge-soft\">{difficulty} guide</span>
            <h3>{guide['title']}</h3>
            <p>{summary}</p>
          </div>
          <div class=\"card-actions\">
            <a class=\"button-link primary\" href=\"/guides/{guide['slug']}/\">Watch &amp; learn</a>
            <a class=\"button-link secondary\" href=\"/games/{guide['game_slug']}/\">Game details</a>
          </div>
        </article>"""


def homepage() -> None:
    trending = sorted(GAMES, key=trending_score, reverse=True)[:12]
    newest = sorted(GAMES, key=lambda g: g.get("created_at", ""), reverse=True)[:12]
    editors = [game for game in GAMES if game.get("editor_pick")] [:12]

    # Fallback to ensure each tab has content
    if len(editors) < 12:
        editors = (editors + [game for game in GAMES if game not in editors])[:12]

    featured_game = trending[0]
    last_updated = max(g.get("last_updated_at", "") for g in GAMES)
    total_games = len(GAMES)
    total_guides = len(GUIDES)

    def cards_markup(games: list[dict]) -> str:
        return "\n".join(render_game_card(game) for game in games)

    hero_section = f"""      <section class=\"hero\">
        <div class=\"hero-intro\">
          <div class=\"badge-soft\">Premium escape room intelligence</div>
          <h1>Escape room discovery and walkthroughs engineered for speed clears.</h1>
          <p>Optimise your next run with curator-tested routes, ranked difficulty filters, and companion video guides. Every scenario is measured, tagged, and ready for instant deployment.</p>
          <div class=\"hero-metrics\">
            <span class=\"metric-pill\">{total_games} games indexed</span>
            <span class=\"metric-pill\">{total_guides} video guides</span>
            <span class=\"metric-pill\">Updated {format_date(last_updated)}</span>
          </div>
        </div>
        <div class=\"hero-visual\">
          <img src=\"/assets/images/games/placeholder-game.svg\" alt=\"Blue Room escape selection\" width=\"420\" height=\"280\" loading=\"lazy\">
        </div>
      </section>"""

    tabs_section = f"""      <section class=\"section\" id=\"featured-selection\">
        <div class=\"section-header\">
          <div>
            <h2>Featured vaults</h2>
            <p>Explore the most requested escape sessions from our community, refreshed daily with engagement metrics and editorial context.</p>
          </div>
          <a class=\"section-cta-link\" href=\"/games/\">Browse full library →</a>
        </div>
        <div class=\"tablist\" role=\"tablist\" data-tablist>
          <button class=\"tab-button\" role=\"tab\" aria-selected=\"true\" data-tab-target=\"tab-trending\">Trending</button>
          <button class=\"tab-button\" role=\"tab\" aria-selected=\"false\" data-tab-target=\"tab-new\" tabindex=\"-1\">New</button>
          <button class=\"tab-button\" role=\"tab\" aria-selected=\"false\" data-tab-target=\"tab-editors\" tabindex=\"-1\">Editor’s picks</button>
        </div>
        <div id=\"tab-trending\" class=\"tab-panel\" role=\"tabpanel\" aria-hidden=\"false\">
          <div class=\"card-grid\">
{cards_markup(trending)}
          </div>
        </div>
        <div id=\"tab-new\" class=\"tab-panel\" role=\"tabpanel\" aria-hidden=\"true\">
          <div class=\"card-grid\">
{cards_markup(newest)}
          </div>
        </div>
        <div id=\"tab-editors\" class=\"tab-panel\" role=\"tabpanel\" aria-hidden=\"true\">
          <div class=\"card-grid\">
{cards_markup(editors)}
          </div>
        </div>
      </section>"""

    featured_section = f"""      <section class=\"section\">
        <div class=\"section-header\">
          <div>
            <h2>Featured walkthrough</h2>
            <p>Run the champion route for {featured_game['title']} with breakdowns for every pincer move and fallback option.</p>
          </div>
          <a class=\"section-cta-link\" href=\"/guides/{featured_game['guide_slug']}/\">Open the guide →</a>
        </div>
        <div class=\"featured-video\">
          <div class=\"video-meta\">
            <span class=\"badge-soft\">Spotlight strategy</span>
            <h3>{featured_game['title']} speed clear tactics</h3>
            <p>Watch the curated strat session recorded with developer permission. Key timestamps map to the written walkthrough for rapid rehearsal.</p>
            <div class=\"pill-row\">
              <span class=\"pill\">Difficulty: {featured_game['difficulty']}</span>
              <span class=\"pill\">Players: {featured_game['players_min']}–{featured_game['players_max']}</span>
            </div>
          </div>
          <iframe src=\"https://www.youtube.com/embed/{featured_game['youtube_video_id']}\" title=\"{featured_game['title']} walkthrough\" loading=\"lazy\" allowfullscreen></iframe>
        </div>
      </section>"""

    trust_section = """      <section class=\"section\">
        <div class=\"section-header\">
          <div>
            <h2>Why teams trust Blue Room Games Hub</h2>
            <p>Signals, tags, and analytics-driven curation help squads choose the right room, avoid traps, and onboard new players faster.</p>
          </div>
        </div>
        <div class=\"trust-strip\">
          <div class=\"trust-item\">⚡ Rapid content refresh every 48 hours</div>
          <div class=\"trust-item\">🎯 Performance-focused rankings</div>
          <div class=\"trust-item\">📹 100% guides include HD video</div>
          <div class=\"trust-item\">🔒 Clean SEO architecture ready for deployment</div>
        </div>
      </section>"""

    body = "\n".join([hero_section, tabs_section, featured_section, trust_section])

    breadcrumb_json = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": f"{SITE_URL}/"
            }
        ]
    }

    website_json = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?search={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }

    extra = ''.join([
        "    <script type=\"application/ld+json\">" + json.dumps(website_json, ensure_ascii=False) + "</script>\n",
        "    <script type=\"application/ld+json\">" + json.dumps(breadcrumb_json, ensure_ascii=False) + "</script>"
    ])

    html = render_base(
        title="Blue Room Games Hub | Escape Room Walkthroughs & Strategy",
        description="Curated escape room discovery platform featuring data-backed rankings, instant filters, and long-form video walkthroughs for Blue Room style experiences.",
        canonical_path="/",
        body=body,
        active="/",
        extra_head=extra,
        scripts=["/assets/js/home.js"]
    )
    write_file(OUTPUT_DIR / "index.html", html)


def games_listing() -> None:
    page_size = 24
    sorted_games = sorted(GAMES, key=trending_score, reverse=True)

    # Precompute facet values
    categories = sorted({cat for game in GAMES for cat in game.get("categories", [])})
    mechanisms = sorted({mech for game in GAMES for mech in game.get("mechanisms", [])})
    languages = sorted({lang for game in GAMES for lang in game.get("languages", [])})

    def render_page(page_number: int) -> str:
        start = (page_number - 1) * page_size
        page_items = sorted_games[start:start + page_size]
        cards = "\n".join(render_game_card(game) for game in page_items)
        total_pages = math.ceil(len(sorted_games) / page_size) or 1

        def pagination_links() -> str:
            if total_pages <= 1:
                return ""
            links = []
            base_path = "/games/"
            for page in range(1, total_pages + 1):
                params = "" if page == 1 else f"?page={page}"
                cls = " class=\"current\"" if page == page_number else ""
                label = str(page)
                links.append(f"<a href=\"{base_path}{params}\"{cls}>{label}</a>")
            return "\n          ".join(links)

        pagination_markup = pagination_links()
        nav_block = (
            f"            <nav class=\"pagination\" data-games-pagination aria-label=\"pagination\">\n          {pagination_markup}\n            </nav>"
            if pagination_markup
            else ""
        )

        facet_markup = "".join(
            f"          <label class=\"facet-checkbox\"><input type=\"checkbox\" value=\"{cat}\" data-facet=\"categories\"> {cat}</label>\n"
            for cat in categories
        )
        mechanism_markup = "".join(
            f"          <label class=\"facet-checkbox\"><input type=\"checkbox\" value=\"{mech}\" data-facet=\"mechanisms\"> {mech}</label>\n"
            for mech in mechanisms
        )
        language_markup = "".join(
            f"          <label class=\"facet-checkbox\"><input type=\"checkbox\" value=\"{lang}\" data-facet=\"language\"> {lang.upper()}</label>\n"
            for lang in languages
        )

        body = f"""      <section class=\"section\">
        <div class=\"section-header\">
          <div>
            <h1>Games intelligence vault</h1>
            <p>Filter by mechanics, difficulty, or languages to pinpoint the next escape room run for your squad.</p>
          </div>
        </div>
        <div class=\"games-layout\">
          <aside class=\"facet-panel\">
            <div class=\"facet-group\">
              <h3>Categories</h3>
              <div class=\"facet-options\">
{facet_markup}              </div>
            </div>
            <div class=\"facet-group\">
              <h3>Mechanisms</h3>
              <div class=\"facet-options\">
{mechanism_markup}              </div>
            </div>
            <div class=\"facet-group\">
              <h3>Difficulty</h3>
              <div class=\"facet-options\">
                <label class=\"facet-checkbox\"><input type=\"checkbox\" value=\"Easy\" data-facet=\"difficulty\"> Easy</label>
                <label class=\"facet-checkbox\"><input type=\"checkbox\" value=\"Medium\" data-facet=\"difficulty\"> Medium</label>
                <label class=\"facet-checkbox\"><input type=\"checkbox\" value=\"Hard\" data-facet=\"difficulty\"> Hard</label>
                <label class=\"facet-checkbox\"><input type=\"checkbox\" value=\"Insane\" data-facet=\"difficulty\"> Insane</label>
              </div>
            </div>
            <div class=\"facet-group\">
              <h3>Language</h3>
              <div class=\"facet-options\">
{language_markup}              </div>
            </div>
          </aside>
          <div>
            <div class=\"games-toolbar\">
              <div class=\"search-shell\" data-search>
                <form data-search-form role=\"search\" aria-label=\"Filter games\">
                  <label for=\"games-search\" class=\"visually-hidden\">Search games</label>
                  <input id=\"games-search\" type=\"search\" placeholder=\"Search by title or tag\" autocomplete=\"off\" data-games-search>
                  <button type=\"submit\" aria-label=\"Search\">🔍</button>
                </form>
                <div class=\"search-results-panel\" data-search-results aria-expanded=\"false\"></div>
              </div>
              <div>
                <label class=\"visually-hidden\" for=\"games-sort\">Sort games</label>
                <select id=\"games-sort\" class=\"select-input\" data-games-sort>
                  <option value=\"trending\">Trending formula</option>
                  <option value=\"new\">Newest first</option>
                  <option value=\"most-rated\">Highest rated</option>
                  <option value=\"alpha\">Alphabetical</option>
                </select>
              </div>
            </div>
            <p data-results-count>{len(sorted_games)} games found</p>
            <div class=\"card-grid\" data-games-grid data-page-size=\"{page_size}\">
{cards}
            </div>
{nav_block}
          </div>
        </div>
      </section>"""

        breadcrumb_json = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Games", "item": f"{SITE_URL}/games/"}
            ]
        }

        extra = ''.join([
        "    <script type=\"application/ld+json\">" + json.dumps(breadcrumb_json, ensure_ascii=False) + "</script>"
    ])

        html = render_base(
            title="Escape Room Games Library | Blue Room Games Hub",
            description="Filter escape room games by mechanics, difficulty, team size, and recency. Ranked lists update with live engagement metrics.",
            canonical_path="/games/" + ("" if page_number == 1 else f"?page={page_number}"),
            body=body,
            active="/games/",
            extra_head=extra,
            scripts=["/assets/js/games.js"]
        )
        file_path = OUTPUT_DIR / ("games/index.html" if page_number == 1 else f"games/page/{page_number}/index.html")
        write_file(file_path, html)

    total_pages = math.ceil(len(sorted_games) / page_size) or 1
    for page in range(1, total_pages + 1):
        render_page(page)


def related_games(game: dict, limit: int = 6) -> list[dict]:
    pool = [
        candidate for candidate in GAMES
        if candidate["slug"] != game["slug"]
        and (set(candidate.get("mechanisms", [])) & set(game.get("mechanisms", []))
             or candidate.get("difficulty") == game.get("difficulty"))
    ]
    ordered = sorted(pool, key=trending_score, reverse=True)
    if len(ordered) < limit:
        for fallback in GAMES:
            if fallback["slug"] != game["slug"] and fallback not in ordered:
                ordered.append(fallback)
            if len(ordered) >= limit:
                break
    return ordered[:limit]


def render_game_detail(game: dict) -> None:
    guide = GUIDES_BY_SLUG.get(game.get("guide_slug", ""))
    related = related_games(game)
    meta_description = f"{game['title']} escape room overview with difficulty {game['difficulty']}, {game['players_min']}–{game['players_max']} players, and mechanics {', '.join(game.get('mechanisms', []))}."

    meta_grid = "".join(
        f"          <div class=\"meta-card\"><span>{label}</span><br><strong>{value}</strong></div>\n"
        for label, value in [
            ("Difficulty", game.get("difficulty")),
            ("Team size", f"{game.get('players_min')}–{game.get('players_max')}"),
            ("Est. time", f"{game.get('time_minutes')} min"),
            ("Languages", ", ".join(game.get("languages", []))),
            ("Mechanisms", ", ".join(game.get("mechanisms", []))),
            ("Categories", ", ".join(game.get("categories", []))),
        ]
    )

    related_markup = "\n".join(
        f"          <div class=\"related-card\">\n            <h4>{item['title']}</h4>\n            <p>{item['summary']}</p>\n            <a class=\"button-link secondary\" href=\"/games/{item['slug']}/\">View</a>\n          </div>"
        for item in related
    )

    guide_link_markup = "" if not guide else f"<a class=\"button-link primary\" href=\"/guides/{guide['slug']}/\">Open the guide</a>"

    body = f"""      <article class=\"section\">
        <div class=\"game-hero\">
          <div>
            <span class=\"badge-soft\">Escape room scenario</span>
            <h1>{game['title']}</h1>
            <p>{game.get('summary', '')}</p>
            <div class=\"card-actions\">
              <a class=\"button-link primary\" href=\"{game['play_url']}\" target=\"_blank\" rel=\"noopener\">Launch experience</a>
              {guide_link_markup or ''}
            </div>
          </div>
          <img src=\"{game['thumbnail']}\" alt=\"{game['title']} hero artwork\" width=\"440\" height=\"260\" loading=\"lazy\">
        </div>
        <section>
          <h2>Scenario overview</h2>
          <div class=\"meta-grid\">
{meta_grid}
          </div>
        </section>
        <section>
          <h2>In-room stream</h2>
          <iframe class=\"game-embed\" src=\"{game['play_url']}\" title=\"{game['title']} live view\" loading=\"lazy\"></iframe>
        </section>
        <section class=\"recommendations\">
          <h3>Recommended next runs</h3>
          <div class=\"related-grid\">
{related_markup}
          </div>
        </section>
      </article>
      <div class=\"cta-overlay\" data-cta-overlay aria-hidden=\"true\">
        <div class=\"cta-dialog\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Need help\">
          <h2>Need help cracking {game['title']}?</h2>
          <p>95% of teams open our companion guide before the finale. Jump in now and keep your clear streak intact.</p>
          <div class=\"cta-actions\">
            {guide_link_markup or ''}
            <a class=\"button-link secondary\" href=\"#\" data-cta-dismiss>Not now</a>
          </div>
        </div>
      </div>"""

    breadcrumb_json = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Games", "item": f"{SITE_URL}/games/"},
            {"@type": "ListItem", "position": 3, "name": game['title'], "item": f"{SITE_URL}/games/{game['slug']}/"}
        ]
    }

    video_game_json = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": game['title'],
        "genre": game.get('categories', []),
        "gamePlatform": "Escape room",
        "applicationSubCategory": "Escape room",
        "url": f"{SITE_URL}/games/{game['slug']}/",
        "playMode": "CoOp",
        "numberOfPlayers": {
            "@type": "QuantitativeValue",
            "minValue": game.get('players_min'),
            "maxValue": game.get('players_max')
        },
        "inLanguage": game.get('languages', []),
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": game.get('rating'),
            "ratingCount": 128
        }
    }

    extra = ''.join([
        "    <script type=\"application/ld+json\">" + json.dumps(video_game_json, ensure_ascii=False) + "</script>\n",
        "    <script type=\"application/ld+json\">" + json.dumps(breadcrumb_json, ensure_ascii=False) + "</script>"
    ])

    html = render_base(
        title=f"{game['title']} Escape Room | Blue Room Games Hub",
        description=meta_description,
        canonical_path=f"/games/{game['slug']}/",
        body=body,
        active="/games/",
        extra_head=extra,
        scripts=["/assets/js/game-detail.js"]
    )
    write_file(OUTPUT_DIR / f"games/{game['slug']}/index.html", html)


def render_guide_detail(guide: dict) -> None:
    game = GAMES_BY_SLUG.get(guide.get("game_slug"))
    related_guides = [GUIDES_BY_SLUG[slug] for slug in guide.get("related_slugs", []) if slug in GUIDES_BY_SLUG][:3]

    steps_markup = "\n".join(
        f"          <div class=\"summary-step\">\n            <h3>{step['title']}</h3>\n            <p>{step['description']}</p>\n          </div>"
        for step in guide.get("summary_steps", [])
    )

    faq_markup = "\n".join(
        f"          <details class=\"faq-item\">\n            <summary>{faq['question']}</summary>\n            <p>{faq['answer']}</p>\n          </details>"
        for faq in guide.get("faqs", [])
    )

    related_markup = "\n".join(
        f"        <article class=\"guide-card\">\n          <h4>{item['title']}</h4>\n          <p>{item['summary']}</p>\n          <a class=\"button-link secondary\" href=\"/guides/{item['slug']}/\">Open guide</a>\n        </article>"
        for item in related_guides
    )

    body = f"""      <div class=\"guide-layout\">
        <article class=\"guide-main\">
          <span class=\"badge-soft\">Video-first walkthrough</span>
          <h1>{guide['title']}</h1>
          <p>{guide.get('summary', '')}</p>
          <section>
            <h2>Watch the strategy session</h2>
            <iframe class=\"game-embed\" src=\"https://www.youtube.com/embed/{guide['youtube_video_id']}\" title=\"{guide['title']} video\" loading=\"lazy\" allowfullscreen></iframe>
          </section>
          <section>
            <h2>Step-by-step route</h2>
            <div class=\"summary-steps\">
{steps_markup}
            </div>
          </section>
          <section>
            <h2>FAQ</h2>
{faq_markup}
          </section>
          <div class=\"feedback-box\">
            <h3>Send tactical feedback</h3>
            <p>If you discover faster clears or new failsafes, email <a href=\"mailto:{guide['feedback_email']}\">{guide['feedback_email']}</a>.</p>
          </div>
        </article>
        <aside class=\"guide-meta-card\">
          <img src=\"{guide['thumbnail']}\" alt=\"{guide['title']} guide artwork\" width=\"320\" height=\"200\" loading=\"lazy\">
          <div class=\"pill-row\">
            <span class=\"pill\">Difficulty: {guide['difficulty']}</span>
            <span class=\"pill\">Story: {guide.get('story_depth', 'Medium')}</span>
          </div>
          <p><strong>Runtime:</strong> {guide.get('estimated_time')} minutes</p>
          <p><strong>Languages:</strong> {', '.join(guide.get('languages', []))}</p>
          <a class=\"button-link primary\" href=\"{game['play_url'] if game else '#'}\" target=\"_blank\" rel=\"noopener\">Play the game</a>
          <div>
            <h3>Recommended next guides</h3>
{related_markup}
          </div>
        </aside>
      </div>"""

    howto_json = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": guide['title'],
        "description": guide.get('summary', ''),
        "totalTime": f"PT{guide.get('estimated_time')}M",
        "step": [
            {
                "@type": "HowToStep",
                "name": step['title'],
                "text": step['description']
            }
            for step in guide.get('summary_steps', [])
        ]
    }

    faq_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq['answer']
                }
            }
            for faq in guide.get('faqs', [])
        ]
    }

    video_json = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": guide['title'],
        "description": guide.get('summary', ''),
        "thumbnailUrl": [guide['thumbnail']],
        "uploadDate": guide.get('last_updated_at'),
        "contentUrl": f"https://www.youtube.com/watch?v={guide['youtube_video_id']}",
        "embedUrl": f"https://www.youtube.com/embed/{guide['youtube_video_id']}"
    }

    breadcrumb_json = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE_URL}/guides/"},
            {"@type": "ListItem", "position": 3, "name": guide['title'], "item": f"{SITE_URL}/guides/{guide['slug']}/"}
        ]
    }

    extra = ''.join([
        "    <script type=\"application/ld+json\">" + json.dumps(video_json, ensure_ascii=False) + "</script>\n",
        "    <script type=\"application/ld+json\">" + json.dumps(howto_json, ensure_ascii=False) + "</script>\n",
        "    <script type=\"application/ld+json\">" + json.dumps(faq_json, ensure_ascii=False) + "</script>\n",
        "    <script type=\"application/ld+json\">" + json.dumps(breadcrumb_json, ensure_ascii=False) + "</script>"
    ])

    html = render_base(
        title=f"{guide['title']} | Escape Room Guide",
        description=guide.get('summary', DEFAULT_DESCRIPTION),
        canonical_path=f"/guides/{guide['slug']}/",
        body=body,
        active="/guides/",
        extra_head=extra
    )
    write_file(OUTPUT_DIR / f"guides/{guide['slug']}/index.html", html)


def guides_listing() -> None:
    cards = "\n".join(render_guide_card(guide) for guide in GUIDES)
    body = f"""      <section class=\"section\">
        <div class=\"section-header\">
          <div>
            <h1>Video strategy guides</h1>
            <p>Every guide blends HD recordings with narrative-safe notes so you can practise routes without breaking immersion.</p>
          </div>
        </div>
        <div class=\"card-grid\">
{cards}
        </div>
      </section>"""

    breadcrumb_json = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE_URL}/guides/"}
        ]
    }
    extra = "    <script type=\"application/ld+json\">" + json.dumps(breadcrumb_json, ensure_ascii=False) + "</script>"

    html = render_base(
        title="Escape Room Video Guides | Blue Room Games Hub",
        description="Watch escape room walkthroughs paired with tactical notes for rapid clears and team onboarding.",
        canonical_path="/guides/",
        body=body,
        active="/guides/",
        extra_head=extra
    )
    write_file(OUTPUT_DIR / "guides/index.html", html)


def simple_page(slug: str, title: str, heading: str, paragraphs: list[str]) -> None:
    content = "\n".join(f"        <p>{paragraph}</p>" for paragraph in paragraphs)
    body = f"""      <section class=\"section\">
        <h1>{heading}</h1>
{content}
      </section>"""
    breadcrumb_json = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": heading, "item": f"{SITE_URL}/{slug}/"}
        ]
    }
    extra = "    <script type=\"application/ld+json\">" + json.dumps(breadcrumb_json, ensure_ascii=False) + "</script>"
    html = render_base(
        title=title,
        description=paragraphs[0] if paragraphs else DEFAULT_DESCRIPTION,
        canonical_path=f"/{slug}/",
        body=body,
        active=f"/{slug}/" if slug != "privacy-policy" else "/privacy-policy/",
        extra_head=extra
    )
    write_file(OUTPUT_DIR / f"{slug}/index.html", html)


def robots_txt() -> None:
    content = """User-agent: *
Allow: /
Sitemap: https://www.blueroomgameshub.com/sitemap.xml
"""
    write_file(OUTPUT_DIR / "robots.txt", content)


def sitemap_xml() -> None:
    urls = ["/", "/games/", "/guides/", "/about/", "/privacy-policy/"]
    for game in GAMES:
        urls.append(f"/games/{game['slug']}/")
    total_pages = math.ceil(len(GAMES) / 24) or 1
    for page in range(2, total_pages + 1):
        urls.append(f"/games/?page={page}")
    for guide in GUIDES:
        urls.append(f"/guides/{guide['slug']}/")

    xml_entries = "\n".join(
        f"  <url><loc>{SITE_URL.rstrip('/')}{path}</loc></url>" for path in urls
    )
    content = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
{xml_entries}
</urlset>
"""
    write_file(OUTPUT_DIR / "sitemap.xml", content)


def main() -> None:
    homepage()
    games_listing()
    guides_listing()

    for game in GAMES:
        render_game_detail(game)

    for guide in GUIDES:
        render_guide_detail(guide)

    simple_page(
        slug="about",
        title="About Blue Room Games Hub",
        heading="About Blue Room Games Hub",
        paragraphs=[
            "Blue Room Games Hub curates escape room and puzzle experiences with a focus on measurable performance metrics.",
            "Our editorial pipeline combines community data, rapid playtesting, and narrative sensitivity to deliver actionable walkthroughs without spoiling critical beats.",
            "The site ships as a static bundle optimised for edge deployment on Cloudflare, with structured data and accessibility baked in."
        ]
    )

    simple_page(
        slug="privacy-policy",
        title="Privacy Policy | Blue Room Games Hub",
        heading="Privacy Policy",
        paragraphs=[
            "Blue Room Games Hub operates as a static experience with no tracking scripts installed at launch.",
            "We store no personal data on this site. If you choose to contact us, your email is used solely to respond to your enquiry.",
            "Future analytics or feedback tooling will be opt-in and documented transparently within this policy."
        ]
    )

    robots_txt()
    sitemap_xml()


if __name__ == "__main__":
    main()
