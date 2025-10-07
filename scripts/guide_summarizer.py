#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攻略总结工具
总结YouTube视频、提取关键步骤、生成FAQ
"""

import re
from typing import Dict, List, Optional


class GuideSummarizer:
    """攻略总结类"""

    def __init__(self, web_fetch_fn):
        """
        初始化总结工具

        Args:
            web_fetch_fn: WebFetch工具函数
        """
        self.web_fetch = web_fetch_fn

    def summarize_youtube_guide(self, video_id: str, game_name: str) -> Dict:
        """
        总结YouTube攻略视频

        Args:
            video_id: YouTube视频ID
            game_name: 游戏名称

        Returns:
            包含攻略信息的字典
        """
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        prompt = f"""请分析这个 {game_name} 游戏攻略视频，提取以下信息：

1. 视频标题
2. 视频时长（如果有）
3. 主要通关步骤（按顺序列出关键步骤，每步1-2句话）
4. 游戏难点提示（最难的3-5个环节）
5. 重要提示或注意事项

请以结构化格式返回，每项单独一行。
步骤部分请用"步骤1:", "步骤2:"的格式。
难点部分请用"难点1:", "难点2:"的格式。
"""

        raw_content = self.web_fetch(youtube_url, prompt)

        guide_info = self._parse_youtube_summary(raw_content, video_id, game_name)

        return guide_info

    def _parse_youtube_summary(self, raw_text: str, video_id: str, game_name: str) -> Dict:
        """解析YouTube视频摘要"""
        info = {
            'video_id': video_id,
            'video_title': '',
            'duration': '',
            'summary_steps': [],
            'key_challenges': [],
            'tips': []
        }

        lines = raw_text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 提取标题
            if '标题' in line or 'title' in line.lower():
                info['video_title'] = self._extract_value(line)

            # 提取时长
            elif '时长' in line or 'duration' in line.lower():
                info['duration'] = self._extract_value(line)

            # 提取步骤
            elif re.match(r'步骤\s*\d+|step\s*\d+', line, re.I):
                step_text = re.sub(r'步骤\s*\d+[:：]?|step\s*\d+[:：]?', '', line, flags=re.I).strip()
                if step_text:
                    info['summary_steps'].append(step_text)

            # 提取难点
            elif re.match(r'难点\s*\d+|challenge\s*\d+|difficulty\s*\d+', line, re.I):
                challenge_text = re.sub(r'难点\s*\d+[:：]?|challenge\s*\d+[:：]?|difficulty\s*\d+[:：]?', '', line, flags=re.I).strip()
                if challenge_text:
                    info['key_challenges'].append(challenge_text)

            # 提取提示
            elif '提示' in line or '注意' in line or 'tip' in line.lower() or 'note' in line.lower():
                tip_text = self._extract_value(line)
                if tip_text and len(tip_text) > 10:
                    info['tips'].append(tip_text)

        # 如果没有提取到标题，使用默认标题
        if not info['video_title']:
            info['video_title'] = f"{game_name} Complete Walkthrough"

        # 如果没有步骤，添加占位符
        if not info['summary_steps']:
            info['summary_steps'] = [
                "观看视频开始部分，了解游戏背景",
                "按照视频指引逐步解谜",
                "注意收集关键道具",
                "完成最终谜题通关"
            ]

        return info

    def _extract_value(self, line: str) -> str:
        """从行中提取值"""
        if '：' in line:
            return line.split('：', 1)[1].strip()
        elif ':' in line:
            return line.split(':', 1)[1].strip()
        return line.strip()

    def extract_key_steps(self, guide_url: str, game_name: str) -> List[str]:
        """
        从文字攻略中提取关键步骤

        Args:
            guide_url: 攻略页面URL
            game_name: 游戏名称

        Returns:
            步骤列表
        """
        prompt = f"""请从这个 {game_name} 游戏攻略中提取通关的关键步骤。

要求：
1. 按顺序列出主要步骤（5-10步）
2. 每步简洁明了（1-2句话）
3. 突出关键操作和解谜要点
4. 忽略次要细节

请用"步骤1:", "步骤2:"的格式返回。
"""

        raw_content = self.web_fetch(guide_url, prompt)

        steps = []
        lines = raw_content.split('\n')

        for line in lines:
            line = line.strip()
            if re.match(r'步骤\s*\d+|step\s*\d+', line, re.I):
                step_text = re.sub(r'步骤\s*\d+[:：]?|step\s*\d+[:：]?', '', line, flags=re.I).strip()
                if step_text:
                    steps.append(step_text)

        # 如果没提取到，返回占位符
        if not steps:
            steps = [
                "阅读游戏介绍，了解背景故事",
                "探索场景，收集可用道具",
                "分析线索，解决谜题",
                "使用道具打开新区域",
                "完成最终挑战通关"
            ]

        return steps[:10]  # 最多10步

    def generate_faq(self, game_info: Dict, guide_info: Dict) -> List[Dict]:
        """
        生成常见问题FAQ

        Args:
            game_info: 游戏信息
            guide_info: 攻略信息

        Returns:
            FAQ列表，每项包含question和answer
        """
        faq = []

        game_name = game_info.get('title', 'this game')
        difficulty = game_info.get('difficulty', 'Medium')
        mechanisms = game_info.get('mechanisms', [])

        # FAQ 1: 游戏难度
        faq.append({
            'question': f"How difficult is {game_name}?",
            'answer': f"{game_name} is rated as {difficulty} difficulty. " +
                     ("It's perfect for beginners." if difficulty == 'Easy' else
                      "It requires moderate puzzle-solving skills." if difficulty == 'Medium' else
                      "It features challenging puzzles that may require hints." if difficulty == 'Hard' else
                      "It's extremely challenging and recommended for experienced players only.")
        })

        # FAQ 2: 游戏时长
        duration = game_info.get('duration_min', 45)
        faq.append({
            'question': f"How long does it take to complete {game_name}?",
            'answer': f"On average, players complete {game_name} in {duration}-{duration + 30} minutes. " +
                     "First-time players may take longer, especially on harder difficulty levels."
        })

        # FAQ 3: 多人游戏
        players_min = game_info.get('players_min', 1)
        players_max = game_info.get('players_max', 4)
        if players_max > 1:
            faq.append({
                'question': f"Can I play {game_name} with friends?",
                'answer': f"Yes! {game_name} supports {players_min}-{players_max} players. " +
                         "Cooperative play can make puzzle-solving more fun and may help with harder challenges."
            })
        else:
            faq.append({
                'question': f"Is {game_name} single-player only?",
                'answer': f"Yes, {game_name} is designed as a single-player experience, " +
                         "though you can still collaborate with friends by sharing ideas."
            })

        # FAQ 4: 游戏机制
        if 'ciphers' in mechanisms:
            faq.append({
                'question': "Do I need to know cryptography?",
                'answer': "No advanced knowledge is required. The game provides all necessary clues " +
                         "to solve cipher puzzles. Common cipher types include substitution, Caesar, and simple codes."
            })

        if 'hidden-objects' in mechanisms:
            faq.append({
                'question': "Are there hidden objects that are easy to miss?",
                'answer': "Yes, some objects are cleverly concealed. Take your time to examine each scene carefully. " +
                         "Many players find it helpful to adjust screen brightness or zoom in on detailed areas."
            })

        if 'logic-puzzles' in mechanisms:
            faq.append({
                'question': "What if I get stuck on a logic puzzle?",
                'answer': "Try breaking down the puzzle into smaller parts. Look for patterns or rules. " +
                         "If you're still stuck, our walkthrough guide provides step-by-step solutions."
            })

        # FAQ 5: 提示系统
        faq.append({
            'question': f"Does {game_name} have a hint system?",
            'answer': "Most escape room games include an in-game hint system. If not, " +
                     "you can refer to our comprehensive walkthrough guide above for detailed solutions."
        })

        # 限制FAQ数量
        return faq[:6]

    def create_guide_data(self, game_info: Dict, guides: List[Dict]) -> Dict:
        """
        创建完整的攻略数据结构

        Args:
            game_info: 游戏信息
            guides: 攻略源列表

        Returns:
            符合guides.json格式的攻略数据
        """
        # 选择最佳攻略源（优先YouTube）
        best_guide = None
        for guide in guides:
            if guide['type'] == 'youtube':
                best_guide = guide
                break

        if not best_guide and guides:
            best_guide = guides[0]

        # 总结攻略内容
        if best_guide and best_guide['type'] == 'youtube':
            guide_summary = self.summarize_youtube_guide(
                best_guide['video_id'],
                game_info.get('title', 'Unknown Game')
            )
        else:
            # 文字攻略
            guide_summary = {
                'video_id': '',
                'video_title': f"{game_info.get('title', 'Unknown')} Walkthrough",
                'summary_steps': [],
                'key_challenges': [],
                'tips': []
            }

            if best_guide:
                steps = self.extract_key_steps(
                    best_guide['url'],
                    game_info.get('title', 'Unknown Game')
                )
                guide_summary['summary_steps'] = steps

        # 生成FAQ
        faq = self.generate_faq(game_info, guide_summary)

        # 构建攻略数据
        guide_data = {
            'slug': game_info.get('slug', 'unknown-game'),
            'title': f"{game_info.get('title', 'Unknown Game')} - Complete Walkthrough & Solutions",
            'game_title': game_info.get('title', 'Unknown Game'),
            'difficulty': game_info.get('difficulty', 'Medium'),
            'story_depth': self._estimate_story_depth(game_info),
            'rating': min(game_info.get('rating', 4.0) + 0.2, 5.0),  # 攻略评分略高于游戏
            'mechanisms': game_info.get('mechanisms', []),
            'youtube_video_id': guide_summary.get('video_id', ''),
            'video_title': guide_summary.get('video_title', ''),
            'summary_steps': guide_summary.get('summary_steps', []),
            'key_challenges': guide_summary.get('key_challenges', []),
            'tips': guide_summary.get('tips', []),
            'faq': faq,
            'meta_description': f"Complete walkthrough and solution guide for {game_info.get('title', 'Unknown Game')}. Step-by-step instructions, puzzle solutions, and helpful tips.",
            'clicks7_norm': 0.0,  # 新攻略
            'created_date': self._get_current_date()
        }

        return guide_data

    def _estimate_story_depth(self, game_info: Dict) -> str:
        """估算故事深度"""
        themes = game_info.get('themes', [])
        mechanisms = game_info.get('mechanisms', [])

        # 某些主题暗示更深的故事
        if 'mystery' in themes or 'horror' in themes or 'sci-fi' in themes:
            return 'High'
        elif 'adventure' in themes or 'fantasy' in themes:
            return 'Medium'
        else:
            return 'Low'

    def _get_current_date(self) -> str:
        """获取当前日期（ISO格式）"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')

    def format_guide_summary(self, guide_data: Dict) -> str:
        """
        格式化攻略摘要（供用户确认）

        Args:
            guide_data: 攻略数据

        Returns:
            格式化的摘要文本
        """
        summary = f"""
=== 攻略信息摘要 ===

📖 攻略标题: {guide_data.get('title', 'N/A')}
🎮 对应游戏: {guide_data.get('game_title', 'N/A')}

📊 攻略评分: {guide_data.get('rating', 4.0)}/5.0
📚 故事深度: {guide_data.get('story_depth', 'Medium')}

"""

        # YouTube视频信息
        if guide_data.get('youtube_video_id'):
            summary += f"🎥 视频攻略: https://www.youtube.com/watch?v={guide_data['youtube_video_id']}\n"
            summary += f"   标题: {guide_data.get('video_title', 'N/A')}\n\n"

        # 关键步骤
        steps = guide_data.get('summary_steps', [])
        if steps:
            summary += f"📝 通关步骤 ({len(steps)}步):\n"
            for i, step in enumerate(steps[:5], 1):  # 只显示前5步
                summary += f"   {i}. {step}\n"
            if len(steps) > 5:
                summary += f"   ... 还有 {len(steps) - 5} 步\n"
            summary += "\n"

        # FAQ
        faq = guide_data.get('faq', [])
        if faq:
            summary += f"❓ 常见问题 ({len(faq)}个):\n"
            for i, item in enumerate(faq[:3], 1):  # 只显示前3个
                summary += f"   Q{i}: {item['question']}\n"
            if len(faq) > 3:
                summary += f"   ... 还有 {len(faq) - 3} 个问题\n"

        summary += "\n" + "="*50 + "\n"

        return summary
