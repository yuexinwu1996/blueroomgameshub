#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏信息爬虫模块
从游戏链接提取信息、搜索攻略、智能分类
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse


class GameScraper:
    """游戏信息爬虫类"""

    DIFFICULTY_KEYWORDS = {
        'easy': ['beginner', 'easy', 'simple', 'starter', '简单', '入门'],
        'medium': ['medium', 'intermediate', 'moderate', '中等', '中级'],
        'hard': ['hard', 'difficult', 'challenging', '困难', '挑战'],
        'insane': ['insane', 'extreme', 'expert', 'master', '极难', '专家']
    }

    MECHANISM_KEYWORDS = {
        'hidden-objects': ['hidden object', 'find items', 'search', '隐藏物品', '寻找'],
        'ciphers': ['cipher', 'code', 'decode', 'cryptic', '密码', '解码'],
        'logic-puzzles': ['logic', 'puzzle', 'riddle', '逻辑', '谜题'],
        'math-puzzles': ['math', 'number', 'calculation', '数学', '计算'],
        'pattern-recognition': ['pattern', 'sequence', 'match', '模式', '序列'],
        'inventory': ['inventory', 'items', 'combine', '物品', '组合'],
        'navigation': ['map', 'maze', 'navigate', '地图', '迷宫'],
        'time-pressure': ['timer', 'race', 'speed', '计时', '限时']
    }

    def __init__(self, web_fetch_fn, web_search_fn):
        """
        初始化爬虫

        Args:
            web_fetch_fn: WebFetch工具函数
            web_search_fn: WebSearch工具函数
        """
        self.web_fetch = web_fetch_fn
        self.web_search = web_search_fn

    def scrape_game_info(self, url: str) -> Dict:
        """
        从游戏链接提取基础信息

        Args:
            url: 游戏页面URL

        Returns:
            包含游戏信息的字典
        """
        # 使用WebFetch抓取游戏页面
        prompt = """请提取以下信息：
        1. 游戏名称（英文）
        2. 游戏简介/描述
        3. 游戏难度（如果有提到）
        4. 玩家评分（如果有）
        5. 游戏类型/标签
        6. 推荐玩家数量（如果有）
        7. 预计游戏时长（如果有）

        请以结构化的方式返回，每项信息单独一行。
        """

        raw_info = self.web_fetch(url, prompt)

        # 解析抓取的信息
        game_info = self._parse_raw_info(raw_info, url)

        return game_info

    def _parse_raw_info(self, raw_text: str, url: str) -> Dict:
        """解析原始抓取信息"""
        info = {
            'title': '',
            'description': '',
            'difficulty': 'Medium',  # 默认中等
            'rating': 4.0,  # 默认4.0
            'players_min': 1,
            'players_max': 4,
            'duration_min': 30,
            'url': url,
            'mechanisms': [],
            'themes': []
        }

        # 简单的文本解析逻辑（实际使用中会更复杂）
        lines = raw_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 提取游戏名称
            if '名称' in line or 'title' in line.lower() or 'name' in line.lower():
                info['title'] = self._extract_value(line)

            # 提取描述
            elif '描述' in line or '简介' in line or 'description' in line.lower():
                info['description'] = self._extract_value(line)

            # 提取难度
            elif '难度' in line or 'difficulty' in line.lower():
                difficulty_text = line.lower()
                info['difficulty'] = self._detect_difficulty(difficulty_text)

            # 提取评分
            elif '评分' in line or 'rating' in line.lower() or 'score' in line.lower():
                rating_match = re.search(r'(\d+\.?\d*)', line)
                if rating_match:
                    info['rating'] = float(rating_match.group(1))

        return info

    def _extract_value(self, line: str) -> str:
        """从行中提取值"""
        # 尝试提取冒号后的内容
        if '：' in line:
            return line.split('：', 1)[1].strip()
        elif ':' in line:
            return line.split(':', 1)[1].strip()
        return line.strip()

    def _detect_difficulty(self, text: str) -> str:
        """从文本中检测难度级别"""
        text_lower = text.lower()

        for difficulty, keywords in self.DIFFICULTY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return difficulty.capitalize()

        return 'Medium'  # 默认中等

    def search_best_guides(self, game_name: str) -> List[Dict]:
        """
        搜索该游戏的最佳攻略

        Args:
            game_name: 游戏名称

        Returns:
            攻略信息列表
        """
        guides = []

        # 搜索YouTube视频攻略
        youtube_query = f"{game_name} walkthrough guide solution"
        youtube_results = self.web_search(youtube_query + " site:youtube.com")

        # 解析YouTube搜索结果
        youtube_guides = self._parse_youtube_results(youtube_results)
        guides.extend(youtube_guides[:3])  # 取前3个

        # 搜索文字攻略
        text_query = f"{game_name} complete walkthrough guide"
        text_results = self.web_search(text_query)

        # 解析文字攻略结果
        text_guides = self._parse_text_results(text_results, game_name)
        guides.extend(text_guides[:2])  # 取前2个

        return guides

    def _parse_youtube_results(self, search_results: str) -> List[Dict]:
        """解析YouTube搜索结果"""
        guides = []

        # 提取YouTube视频ID的正则表达式
        video_id_pattern = r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'

        matches = re.findall(video_id_pattern, search_results)
        for video_id in matches:
            guides.append({
                'type': 'youtube',
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            })

        return guides

    def _parse_text_results(self, search_results: str, game_name: str) -> List[Dict]:
        """解析文字攻略搜索结果"""
        guides = []

        # 提取URL的简单正则
        url_pattern = r'https?://[^\s<>"]+(?:walkthrough|guide|solution)[^\s<>"]*'
        urls = re.findall(url_pattern, search_results)

        for url in urls[:2]:  # 只取前2个
            guides.append({
                'type': 'text',
                'url': url
            })

        return guides

    def categorize_game(self, game_info: Dict, description: str = '') -> Dict:
        """
        智能分类和打分

        Args:
            game_info: 基础游戏信息
            description: 游戏描述文本（用于分析）

        Returns:
            增强的游戏信息（包含分类、机制等）
        """
        text = (game_info.get('description', '') + ' ' + description).lower()

        # 检测游戏机制
        mechanisms = []
        for mechanism, keywords in self.MECHANISM_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    mechanisms.append(mechanism)
                    break

        # 如果没检测到，添加默认机制
        if not mechanisms:
            mechanisms = ['hidden-objects', 'logic-puzzles']

        # 去重
        mechanisms = list(set(mechanisms))

        # 检测主题
        themes = self._detect_themes(text)

        # 生成slug
        slug = self._generate_slug(game_info.get('title', 'unknown-game'))

        # 更新game_info
        game_info['slug'] = slug
        game_info['mechanisms'] = mechanisms[:4]  # 最多4个机制
        game_info['themes'] = themes[:3]  # 最多3个主题

        # 初始化热度数据（新游戏）
        game_info['pv7_norm'] = 0.0
        game_info['guide_clicks7_norm'] = 0.0
        game_info['recency'] = 1.0  # 新游戏recency最高

        return game_info

    def _detect_themes(self, text: str) -> List[str]:
        """检测游戏主题"""
        theme_keywords = {
            'mystery': ['mystery', 'detective', '神秘', '侦探'],
            'horror': ['horror', 'scary', 'fear', '恐怖', '惊悚'],
            'sci-fi': ['sci-fi', 'science', 'space', 'future', '科幻', '未来'],
            'fantasy': ['fantasy', 'magic', 'wizard', '奇幻', '魔法'],
            'adventure': ['adventure', 'explore', '冒险', '探索'],
            'historical': ['historical', 'ancient', '历史', '古代']
        }

        themes = []
        for theme, keywords in theme_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    themes.append(theme)
                    break

        return themes if themes else ['mystery']  # 默认mystery主题

    def _generate_slug(self, title: str) -> str:
        """生成URL友好的slug"""
        # 转小写
        slug = title.lower()
        # 移除特殊字符
        slug = re.sub(r'[^\w\s-]', '', slug)
        # 空格转连字符
        slug = re.sub(r'[\s_]+', '-', slug)
        # 移除多余连字符
        slug = re.sub(r'-+', '-', slug)
        # 去除首尾连字符
        slug = slug.strip('-')

        return slug or 'unknown-game'

    def estimate_difficulty_score(self, difficulty: str) -> int:
        """将难度转换为数值分数"""
        difficulty_scores = {
            'Easy': 1,
            'Medium': 2,
            'Hard': 3,
            'Insane': 4
        }
        return difficulty_scores.get(difficulty, 2)

    def generate_game_summary(self, game_info: Dict, guides: List[Dict]) -> str:
        """
        生成游戏信息摘要（供用户确认）

        Args:
            game_info: 游戏信息
            guides: 攻略列表

        Returns:
            格式化的摘要文本
        """
        # 难度图标
        difficulty_icons = {
            'Easy': '🔥',
            'Medium': '🔥🔥',
            'Hard': '🔥🔥🔥',
            'Insane': '🔥🔥🔥🔥'
        }

        difficulty = game_info.get('difficulty', 'Medium')
        icon = difficulty_icons.get(difficulty, '🔥🔥')

        summary = f"""
=== 游戏信息摘要 ===

📌 游戏名称: {game_info.get('title', 'Unknown')}
🔗 原始链接: {game_info.get('url', 'N/A')}
🆔 Slug: {game_info.get('slug', 'unknown')}

📝 描述: {game_info.get('description', 'N/A')[:200]}...

🎯 难度: {difficulty} ({icon})
⭐ 建议评分: {game_info.get('rating', 4.0)}/5.0
👥 玩家数: {game_info.get('players_min', 1)}-{game_info.get('players_max', 4)}人
⏱️  游戏时长: {game_info.get('duration_min', 30)}-{game_info.get('duration_min', 30) + 30}分钟

🎮 游戏机制:
"""

        for mechanism in game_info.get('mechanisms', []):
            summary += f"  - {mechanism}\n"

        summary += "\n🎨 主题标签:\n"
        for theme in game_info.get('themes', []):
            summary += f"  - {theme}\n"

        summary += f"\n📚 找到 {len(guides)} 个攻略来源:\n"
        for i, guide in enumerate(guides, 1):
            if guide['type'] == 'youtube':
                summary += f"  {i}. [YouTube] https://www.youtube.com/watch?v={guide['video_id']}\n"
            else:
                summary += f"  {i}. [网页] {guide['url']}\n"

        summary += "\n" + "="*50 + "\n"
        summary += "请确认以上信息是否准确？\n"
        summary += "如需修改，请告诉我需要调整的内容。\n"
        summary += "确认无误后，输入 'yes' 或 '确认' 继续添加游戏。\n"

        return summary
