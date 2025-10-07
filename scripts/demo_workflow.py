#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示工作流脚本
展示如何使用游戏添加工具的完整流程
"""


def demo_workflow():
    """演示完整的游戏添加工作流"""

    print("""
╔══════════════════════════════════════════════════════════╗
║         游戏添加工作流演示                                ║
║         Game Addition Workflow Demo                      ║
╚══════════════════════════════════════════════════════════╝

这是一个演示脚本，展示了添加新游戏的完整流程。

实际使用时，你需要在Claude Code环境中运行，
因为需要使用WebFetch和WebSearch工具。

""")

    print("="*60)
    print("工作流程说明")
    print("="*60)

    steps = [
        {
            "step": 1,
            "title": "用户提供游戏链接",
            "description": "你: 帮我添加这个游戏 https://example.com/mystery-mansion",
            "action": "Claude接收URL并开始处理"
        },
        {
            "step": 2,
            "title": "自动抓取游戏信息",
            "description": "使用WebFetch抓取游戏页面",
            "action": "提取: 游戏名称、描述、难度、评分、类型等"
        },
        {
            "step": 3,
            "title": "搜索最佳攻略",
            "description": "使用WebSearch搜索YouTube和文字攻略",
            "action": "找到最相关的3-5个攻略源"
        },
        {
            "step": 4,
            "title": "智能分类和评分",
            "description": "分析游戏机制和主题",
            "action": "自动分类: mechanisms, themes, difficulty"
        },
        {
            "step": 5,
            "title": "总结攻略内容",
            "description": "从YouTube视频或文字攻略提取关键步骤",
            "action": "生成: 通关步骤、难点提示、FAQ"
        },
        {
            "step": 6,
            "title": "显示信息摘要",
            "description": "格式化展示所有收集的信息",
            "action": "等待用户确认"
        },
        {
            "step": 7,
            "title": "用户确认",
            "description": "你: yes / 确认",
            "action": "或者提出修改建议"
        },
        {
            "step": 8,
            "title": "更新数据文件",
            "description": "添加到games.json和guides.json",
            "action": "重新计算所有游戏的排行分数"
        },
        {
            "step": 9,
            "title": "重新生成页面",
            "description": "运行build_site.py",
            "action": "生成: 游戏详情页、攻略详情页、列表页、首页"
        },
        {
            "step": 10,
            "title": "完成",
            "description": "新游戏已添加到网站",
            "action": "可以立即访问新页面"
        }
    ]

    for item in steps:
        print(f"\n【步骤 {item['step']}】{item['title']}")
        print(f"  描述: {item['description']}")
        print(f"  执行: {item['action']}")

    print("\n" + "="*60)
    print("实际使用示例")
    print("="*60)

    example_code = '''
# 在Claude Code中的使用方式：

你: 帮我添加这个游戏 https://armorgames.com/escape-blue-room-game

Claude: 好的，我来帮你添加这个游戏。

[Claude 使用 WebFetch 和 WebSearch 工具]

Claude:
=== 游戏信息摘要 ===

📌 游戏名称: Escape: Blue Room
🔗 原始链接: https://armorgames.com/escape-blue-room-game
🆔 Slug: escape-blue-room

📝 描述: A challenging point-and-click escape room game where you must
solve puzzles to escape from a mysterious blue room...

🎯 难度: Hard (🔥🔥🔥)
⭐ 建议评分: 4.7/5.0
👥 玩家数: 1-2人
⏱️  游戏时长: 30-60分钟

🎮 游戏机制:
  - hidden-objects
  - ciphers
  - logic-puzzles

🎨 主题标签:
  - mystery
  - puzzle

📚 找到 5 个攻略来源:
  1. [YouTube] https://www.youtube.com/watch?v=abc123
  2. [YouTube] https://www.youtube.com/watch?v=def456
  3. [网页] https://walkthrough.com/escape-blue-room

=== 攻略信息摘要 ===

📖 攻略标题: Escape: Blue Room - Complete Walkthrough & Solutions
🎮 对应游戏: Escape: Blue Room

📊 攻略评分: 4.8/5.0
📚 故事深度: High

🎥 视频攻略: https://www.youtube.com/watch?v=abc123
   标题: Escape Blue Room Full Walkthrough

📝 通关步骤 (8步):
   1. 检查房间四周，找到所有可点击的物品
   2. 在书架上找到红色书籍，获得第一个线索
   3. 破解墙上的密码锁（线索：书中的数字）
   4. 使用钥匙打开抽屉，获得电池
   5. 将电池安装到遥控器中
   ... 还有 3 步

❓ 常见问题 (6个):
   Q1: How difficult is Escape: Blue Room?
   Q2: How long does it take to complete?
   Q3: Do I need to know cryptography?
   ... 还有 3 个问题

==================================================
请确认以上信息是否准确？
如需修改，请告诉我需要调整的内容。
确认无误后，输入 'yes' 或 '确认' 继续添加游戏。

你: yes

Claude: 正在更新数据文件...
✅ 成功添加/更新游戏: Escape: Blue Room
✅ 成功添加/更新攻略: Escape: Blue Room - Complete Walkthrough

正在重新生成网站页面...
📄 生成游戏列表页...
📄 生成 13 个游戏详情页...
📄 生成 13 个攻略详情页...

✅ 完成！新游戏已添加到网站

你现在可以访问:
- 游戏详情: /games/escape-blue-room/
- 攻略详情: /guides/escape-blue-room/
- 游戏列表已更新，包含新游戏
- 首页Trending排行已更新
'''

    print(example_code)

    print("\n" + "="*60)
    print("技术架构")
    print("="*60)

    architecture = """
scripts/
├── game_scraper.py         # 游戏信息爬虫
│   ├── scrape_game_info()   # 抓取基础信息
│   ├── search_best_guides() # 搜索攻略
│   └── categorize_game()    # 智能分类
│
├── guide_summarizer.py     # 攻略总结工具
│   ├── summarize_youtube_guide()  # 总结YouTube视频
│   ├── extract_key_steps()        # 提取关键步骤
│   └── generate_faq()             # 生成FAQ
│
├── build_site.py           # 网站构建脚本（已增强）
│   ├── add_game_to_data()   # 添加游戏到JSON
│   ├── recalculate_rankings() # 重新计算排行
│   ├── render_game_detail()   # 生成游戏详情页
│   └── render_guide_detail()  # 生成攻略详情页
│
└── add_game.py             # 命令行工具（主入口）
    ├── GameAdder.process_game_url()  # 处理游戏URL
    ├── GameAdder.add_to_site()       # 添加到网站
    └── GameAdder.rebuild_site()      # 重新生成页面

数据流:
游戏URL → 爬虫抓取 → 攻略搜索 → 智能分类 →
用户确认 → 更新JSON → 重新计算排行 → 生成页面
"""

    print(architecture)

    print("\n" + "="*60)
    print("关键特性")
    print("="*60)

    features = [
        "✅ 全自动信息收集：无需手动填写，自动从网页提取",
        "✅ 智能攻略总结：自动搜索并总结YouTube/文字攻略",
        "✅ 自动分类打分：根据内容智能识别游戏机制和主题",
        "✅ 人工确认机制：显示摘要等待确认，确保信息准确",
        "✅ 自动排行更新：添加新游戏后自动重新计算所有排行",
        "✅ 批量页面生成：一次更新，所有相关页面自动重新生成",
        "✅ SEO优化：自动生成meta描述、结构化数据",
        "✅ 数据一致性：游戏和攻略数据自动关联"
    ]

    for feature in features:
        print(f"  {feature}")

    print("\n" + "="*60)
    print("下次使用方法")
    print("="*60)

    usage = """
当你想添加新游戏时，只需要：

1. 找到游戏的URL
2. 告诉Claude："帮我添加这个游戏 [URL]"
3. 等待Claude自动收集信息
4. 查看摘要，确认信息准确性
5. 输入"yes"确认
6. 完成！

就这么简单！
"""

    print(usage)

    print("="*60)
    print("演示结束")
    print("="*60)


if __name__ == "__main__":
    demo_workflow()
