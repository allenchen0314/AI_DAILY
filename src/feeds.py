"""RSS 源配置 - 全球主流 AI 新闻媒体

格式: (显示名, RSS URL, 分类, ai_only)
  - ai_only=False: 该源已经是 AI 专题,所有条目直接保留
  - ai_only=True : 该源是综合科技媒体,需在标题/摘要中命中 AI 关键词才保留
"""

FEEDS = [
    # === 国际科技媒体 (AI 专题,无需过滤) ===
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "国际", False),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "国际", False),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "国际", False),
    ("MIT Technology Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed", "国际", False),
    ("Ars Technica AI", "https://arstechnica.com/ai/feed/", "国际", False),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss", "国际", False),

    # === 厂商 / 实验室官方博客 ===
    ("OpenAI Blog", "https://openai.com/blog/rss.xml", "厂商", False),
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml", "厂商", False),
    ("Google Research", "https://blog.research.google/feeds/posts/default", "厂商", False),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml", "厂商", False),
    ("NVIDIA Blog", "https://blogs.nvidia.com/feed/", "厂商", True),  # NVIDIA 也涉及游戏/汽车,过滤
    ("AWS Machine Learning", "https://aws.amazon.com/blogs/machine-learning/feed/", "厂商", False),

    # === 中文综合科技媒体 (需关键词过滤) ===
    # 注: 机器之心、量子位、新智元、虎嗅、极客公园 的官方 RSS 已下线或反爬。
    ("36氪", "https://36kr.com/feed", "中文", True),
    ("36氪快讯", "https://36kr.com/feed-newsflash", "中文", True),
    ("雷锋网", "https://www.leiphone.com/feed", "中文", True),
    ("钛媒体", "https://www.tmtpost.com/rss.xml", "中文", True),
    ("爱范儿", "https://www.ifanr.com/feed", "中文", True),
]


# AI 关键词 - 用于综合科技媒体的过滤
AI_KEYWORDS = [
    # 通用术语
    "AI", "A.I.", "人工智能", "AGI", "通用人工智能",
    "大模型", "大语言模型", "LLM", "基础模型", "Foundation Model",
    "生成式", "Generative", "AIGC",
    "多模态", "Multimodal",
    "智能体", "Agent", "AI Agent",
    "机器学习", "深度学习", "神经网络", "强化学习",
    "Machine Learning", "Deep Learning",
    "NLP", "自然语言", "计算机视觉", "CV",
    "Transformer", "扩散模型", "Diffusion",
    "RAG", "向量数据库", "Embedding",
    "推理", "训练", "微调", "Fine-tun",
    "算力", "GPU", "TPU", "推理芯片",
    "提示词", "Prompt",

    # 国际产品 / 公司
    "ChatGPT", "GPT-", "GPT4", "GPT5", "OpenAI",
    "Claude", "Anthropic",
    "Gemini", "DeepMind", "Google AI",
    "Llama", "Meta AI",
    "Mistral", "Grok", "xAI",
    "Copilot", "Microsoft AI",
    "Perplexity", "Stable Diffusion", "Midjourney", "Sora",
    "Hugging Face",

    # 中国厂商 / 产品
    "通义", "千问", "Qwen",
    "文心", "百度智能云", "百度AI",
    "豆包", "Doubao", "Coze", "扣子",
    "Kimi", "月之暗面", "Moonshot",
    "智谱", "ChatGLM", "GLM-",
    "百川", "Baichuan",
    "MiniMax", "海螺",
    "DeepSeek", "深度求索",
    "讯飞", "星火",
    "商汤", "日日新",
    "阶跃", "Step-",
    "零一", "Yi-",
    "腾讯混元", "Hunyuan",
    "字节", "火山引擎", "即梦",
    "可灵", "Kling",
    "英伟达", "NVIDIA",
    "华为", "盘古",
    "联想", "联想AI",

    # 应用类
    "数字人", "数字员工",
    "AI编程", "AI代码", "AI助手",
    "Vibe Coding", "Coding Agent",
    "具身智能", "人形机器人",
    "自动驾驶", "FSD",
]
