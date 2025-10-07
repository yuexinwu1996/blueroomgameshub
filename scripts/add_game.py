#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键添加游戏命令行工具
自动抓取游戏信息、搜索攻略、总结内容并更新网站
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from game_scraper import GameScraper
from guide_summarizer import GuideSummarizer


class GameAdder:
    """游戏添加器"""

    def __init__(self):
        """初始化添加器"""
        # 这些函数将被注入（在实际使用时由Claude提供）
        self.web_fetch = None
        self.web_search = None
        self.scraper = None
        self.summarizer = None

    def setup_tools(self, web_fetch_fn, web_search_fn):
        """
        设置Web工具

        Args:
            web_fetch_fn: WebFetch函数
            web_search_fn: WebSearch函数
        """
        self.web_fetch = web_fetch_fn
        self.web_search = web_search_fn
        self.scraper = GameScraper(web_fetch_fn, web_search_fn)
        self.summarizer = GuideSummarizer(web_fetch_fn)

    def process_game_url(self, url: str, interactive: bool = True) -> tuple:
        """
        处理游戏URL，抓取信息并生成摘要

        Args:
            url: 游戏页面URL
            interactive: 是否交互式确认

        Returns:
            (game_data, guide_data) 元组
        """
        print("="*60)
        print("🔍 正在分析游戏信息...")
        print("="*60)

        # 步骤1: 抓取游戏基础信息
        game_info = self.scraper.scrape_game_info(url)
        print(f"✓ 已获取游戏名称: {game_info.get('title', 'Unknown')}")

        # 步骤2: 搜索最佳攻略
        print("\n🔍 正在搜索最佳攻略...")
        guides = self.scraper.search_best_guides(game_info.get('title', 'Unknown'))
        print(f"✓ 找到 {len(guides)} 个攻略来源")

        # 步骤3: 智能分类和打分
        print("\n🎯 正在智能分类和评分...")
        game_info = self.scraper.categorize_game(
            game_info,
            game_info.get('description', '')
        )
        print(f"✓ 难度: {game_info.get('difficulty', 'Medium')}")
        print(f"✓ 机制: {', '.join(game_info.get('mechanisms', []))}")

        # 步骤4: 创建完整的游戏数据
        game_data = self._create_full_game_data(game_info)

        # 步骤5: 创建攻略数据
        print("\n📚 正在总结攻略内容...")
        guide_data = self.summarizer.create_guide_data(game_info, guides)
        print(f"✓ 已生成攻略数据")

        # 步骤6: 显示摘要
        print("\n" + "="*60)
        summary = self.scraper.generate_game_summary(game_info, guides)
        print(summary)

        guide_summary = self.summarizer.format_guide_summary(guide_data)
        print(guide_summary)

        # 步骤7: 等待用户确认（如果是交互模式）
        if interactive:
            confirmed = self._confirm_addition()
            if not confirmed:
                print("\n❌ 已取消添加游戏")
                return None, None

        return game_data, guide_data

    def _create_full_game_data(self, game_info: dict) -> dict:
        """创建完整的游戏数据结构"""
        return {
            "slug": game_info.get("slug", "unknown-game"),
            "title": game_info.get("title", "Unknown Game"),
            "summary": game_info.get("description", "An exciting escape room game.")[:200],
            "difficulty": game_info.get("difficulty", "Medium"),
            "mechanisms": game_info.get("mechanisms", ["hidden-objects", "logic-puzzles"]),
            "categories": game_info.get("themes", ["mystery"]),
            "players_min": game_info.get("players_min", 1),
            "players_max": game_info.get("players_max", 4),
            "time_minutes": game_info.get("duration_min", 45),
            "languages": ["en"],
            "rating": game_info.get("rating", 4.0),
            "play_url": game_info.get("url", ""),
            "thumbnail": f"/assets/images/games/{game_info.get('slug', 'default')}.jpg",
            "guide_slug": game_info.get("slug", "unknown-game"),
            "pv7_norm": game_info.get("pv7_norm", 0.0),
            "guide_clicks7_norm": game_info.get("guide_clicks7_norm", 0.0),
            "recency": game_info.get("recency", 1.0),
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "meta_description": f"Play {game_info.get('title', 'Unknown Game')} - {game_info.get('difficulty', 'Medium')} difficulty escape room game. {game_info.get('description', '')[:100]}..."
        }

    def _confirm_addition(self) -> bool:
        """
        等待用户确认

        Returns:
            True如果用户确认，False如果取消
        """
        print("\n" + "="*60)
        response = input("请确认信息是否准确？(输入 'yes' 或 '确认' 继续): ").strip().lower()
        return response in ['yes', 'y', '确认', 'ok']

    def add_to_site(self, game_data: dict, guide_data: dict) -> bool:
        """
        添加游戏到网站数据

        Args:
            game_data: 游戏数据
            guide_data: 攻略数据

        Returns:
            成功返回True
        """
        try:
            # 导入build_site模块
            from build_site import add_game_to_data

            print("\n" + "="*60)
            print("💾 正在更新数据文件...")
            print("="*60)

            # 添加到数据文件
            add_game_to_data(game_data, guide_data)

            print("\n✅ 数据文件更新成功!")
            return True

        except Exception as e:
            print(f"\n❌ 更新数据失败: {e}")
            return False

    def rebuild_site(self) -> bool:
        """
        重新生成网站页面

        Returns:
            成功返回True
        """
        try:
            print("\n" + "="*60)
            print("🔨 正在重新生成网站页面...")
            print("="*60)

            # 导入并运行build_site
            from build_site import (
                build_games_index,
                render_game_detail,
                render_guide_detail,
                GAMES,
                GUIDES,
                GAMES_BY_SLUG,
                GUIDES_BY_SLUG
            )

            # 重新加载数据（因为刚刚更新了JSON文件）
            import json
            DATA_DIR = ROOT / "assets" / "data"

            with open(DATA_DIR / "games.json", encoding="utf-8") as fh:
                updated_games = json.load(fh)

            with open(DATA_DIR / "guides.json", encoding="utf-8") as fh:
                updated_guides = json.load(fh)

            # 生成游戏列表页
            print("📄 生成游戏列表页...")
            build_games_index()

            # 为每个游戏生成详情页
            print(f"📄 生成 {len(updated_games)} 个游戏详情页...")
            for game in updated_games:
                render_game_detail(game)

            # 为每个攻略生成详情页
            print(f"📄 生成 {len(updated_guides)} 个攻略详情页...")
            for guide in updated_guides:
                render_guide_detail(guide)

            print("\n✅ 网站页面生成完成!")
            return True

        except Exception as e:
            print(f"\n❌ 生成页面失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="一键添加游戏到BlueRoom.cc"
    )
    parser.add_argument(
        "url",
        help="游戏页面URL"
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="跳过确认步骤（自动添加）"
    )
    parser.add_argument(
        "--no-rebuild",
        action="store_true",
        help="只更新数据，不重新生成页面"
    )

    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════╗
║         BlueRoom.cc 游戏自动添加工具                     ║
║         Game Auto-Adder Tool                             ║
╚══════════════════════════════════════════════════════════╝
""")

    adder = GameAdder()

    # 注意: 在实际使用时，这些工具函数需要由调用者提供
    # 例如在Claude Code环境中，这些会是WebFetch和WebSearch工具
    print("⚠️  注意: 此工具需要在Claude Code环境中运行，以使用WebFetch和WebSearch功能")
    print("⚠️  请使用Claude直接调用此工具，而不是独立运行\n")

    # 占位符 - 实际使用时会被替换
    # adder.setup_tools(web_fetch_function, web_search_function)

    print(f"🔗 目标URL: {args.url}\n")

    # 在这里，工具应该由外部（Claude）调用
    # 以下代码仅作为示例说明流程

    print("""
使用说明:
---------
在Claude Code中使用此工具的方式：

```python
from add_game import GameAdder

adder = GameAdder()

# Claude会提供这些工具函数
adder.setup_tools(
    web_fetch_fn=lambda url, prompt: WebFetch(url=url, prompt=prompt),
    web_search_fn=lambda query: WebSearch(query=query)
)

# 处理游戏URL
game_data, guide_data = adder.process_game_url(
    "https://example.com/game",
    interactive=True  # 需要用户确认
)

if game_data and guide_data:
    # 添加到网站
    adder.add_to_site(game_data, guide_data)

    # 重新生成页面
    adder.rebuild_site()
```
""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
