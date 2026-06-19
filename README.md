# Everyday AI News 📬

每天北京时间 7 点自动抓取**前一天**的全球 AI 新闻 (国际 + 中文),用 Claude 生成中文热点总结后,通过邮件发送到你的收件箱。

```
RSS (TechCrunch / OpenAI / NVIDIA / 36氪 / 雷锋网 / 爱范儿 ...)
        ↓  feedparser 抓取 + 按昨天发布过滤 + AI 关键词过滤 + 去重
        ↓  Claude Sonnet 生成中文热点总结 (可选)
        ↓  Jinja2 渲染响应式 HTML 模板 (顶部摘要卡 + 分类列表)
        ↓  Resend API 投递
        ↓
    📧 chenzhipengsr43@gmail.com
        ↑
GitHub Actions cron (UTC 23:07 = 北京次日 07:07)
```

## 项目结构

```
everyday_news/
├── src/
│   ├── feeds.py        # RSS 源列表 (国际 6 + 厂商 6 + 中文 5)
│   ├── fetcher.py      # 抓取 + 日期过滤 + AI 关键词过滤 + 去重
│   ├── summarizer.py   # 调用 Claude Sonnet 生成中文热点总结
│   ├── renderer.py     # 调用 Jinja2 渲染
│   ├── sender.py       # Resend 发送邮件
│   └── main.py         # 主入口
├── templates/
│   └── email.html.j2   # 响应式邮件模板 (含 AI 摘要卡片)
├── .github/workflows/
│   └── daily.yml       # 每天 07:07 北京时间触发
├── requirements.txt
└── .env.example
```

## 数据源

抓取的 RSS 源分三类,所有中文源和综合科技源会经过 **AI 关键词过滤**,只保留与 AI/大模型/智能体相关的条目。

- **国际媒体**:TechCrunch AI、The Verge AI、VentureBeat AI、MIT Tech Review、Ars Technica AI、Wired AI
- **厂商博客**:OpenAI、Google DeepMind、Google Research、Hugging Face、NVIDIA、AWS Machine Learning
- **中文媒体**:36氪、36氪快讯、雷锋网、钛媒体、爱范儿 (经 AI 关键词过滤)

AI 关键词覆盖中英文术语 (`GPT` / `Claude` / `LLM` / `大模型` / `智能体` ...) 与主流厂商 (`OpenAI` / `Anthropic` / `通义` / `文心` / `豆包` / `Kimi` / `DeepSeek` / `智谱` / `讯飞` / `商汤` / `MiniMax` / `阶跃` / `零一` / `腾讯混元` / `英伟达` / `华为盘古` ...)。

要自定义,直接编辑 `src/feeds.py` 的 `FEEDS` 列表 (4-tuple: 名称、URL、分类、是否启用 AI 过滤) 和 `AI_KEYWORDS`。

## 一、本地调试

### 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 申请 Resend API Key

1. 打开 https://resend.com 注册账号 (免费版每月 3000 封邮件,完全够用)
2. 进入 [API Keys](https://resend.com/api-keys),点击 **Create API Key**,复制 `re_xxx...`
3. 想要更专业的发件域名,可以在 [Domains](https://resend.com/domains) 添加并配置 DNS;**不配置也能直接用** `onboarding@resend.dev` 测试

### 3. (可选) 申请 Anthropic API Key

用于让 Claude 生成中文热点总结,**不配置也能正常发邮件**,只是没有顶部摘要卡。

1. 打开 https://console.anthropic.com/ 注册并充值
2. 进入 **API Keys**,创建并复制 `sk-ant-xxx...`

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 RESEND_API_KEY、(可选) ANTHROPIC_API_KEY
```

然后 export 一下:

```bash
set -a; source .env; set +a
```

### 5. 试运行

不发邮件,只生成预览 HTML:

```bash
python -m src.main --dry-run
open output/preview.html        # 浏览器查看效果
```

跳过 Claude 总结 (省 API 费用,快速调试抓取/模板):

```bash
python -m src.main --dry-run --no-summary
```

指定历史日期 (适合首次测试,昨天可能还没新闻):

```bash
python -m src.main --date 2026-06-18 --dry-run
```

正式发邮件:

```bash
python -m src.main
```

## 二、部署到 GitHub Actions

### 1. 推到 GitHub

```bash
git init
git add .
git commit -m "init: daily AI news digest"
gh repo create everyday-news --private --source=. --push
```

### 2. 配置 Secrets

进入仓库的 **Settings → Secrets and variables → Actions → New repository secret**,添加:

| Name                | 是否必需 | Value                                                   |
| ------------------- | -------- | ------------------------------------------------------- |
| `RESEND_API_KEY`    | ✅ 必需  | 你的 Resend API key,例如 `re_AbCd1234...`              |
| `MAIL_FROM`         | ✅ 必需  | `AI Daily <onboarding@resend.dev>` (或你验证过的域名)   |
| `MAIL_TO`           | ✅ 必需  | `chenzhipengsr43@gmail.com`                             |
| `ANTHROPIC_API_KEY` | 可选     | `sk-ant-xxx...` — 不配置则邮件不带 AI 摘要,正文照常发 |

### 3. 手动触发一次验证

进入 **Actions → Daily AI News → Run workflow**,可以选填日期。看到绿色 ✅ 且邮箱收到邮件就成功了。

之后每天北京时间 07:07 会自动跑。

## 三、常见问题

**Q: 为什么是 7:07 不是 7:00?**
GitHub Actions 整点排队严重,可能延迟 5-30 分钟。`:07` 错峰能更准时。

**Q: 收不到邮件?**
1. 先看 GitHub Actions 日志,搜索 `邮件已发送,id=xxx`
2. 检查 Gmail **垃圾邮件**文件夹
3. 用 `onboarding@resend.dev` 发件时,Gmail 可能直接拒收 — 建议在 Resend 验证一个自己的域名

**Q: 中文源抓到的内容很多和 AI 无关?**
中文源 (36氪/雷锋网/钛媒体/爱范儿) 默认开启 AI 关键词过滤,只保留命中关键词的条目。如果想完全保留,把 `src/feeds.py` 里对应行的第 4 个字段从 `True` 改成 `False`。如果想加更多关键词,编辑同文件的 `AI_KEYWORDS`。

**Q: 想加更多 RSS 源?**
编辑 `src/feeds.py` 的 `FEEDS` 列表,追加 `(显示名, RSS URL, 分类, 是否启用 AI 过滤)`。分类目前有 `国际` / `厂商` / `中文`,新分类会自动作为邮件中的一个分组。

**Q: 想换总结模型?**
环境变量 `CLAUDE_MODEL` 可以指定具体模型 ID,默认 `claude-sonnet-4-20250514`。摘要 prompt 在 `src/summarizer.py` 的 `SYSTEM_PROMPT`,可以按口味改字数/语气/格式。

**Q: 不想用 Claude,想换 OpenAI / 国产模型?**
改 `src/summarizer.py` 的 `summarize()` 实现即可,主流程只要求它返回 `str | None`。返回 `None` 时模板会自动隐藏摘要区块。

**Q: 昨天没有新闻怎么办?**
邮件会照常发出,只是内容是"今天没有抓到新的 AI 新闻"占位。如果想跳过空邮件,在 `src/main.py` 的 `if not items` 分支里改成 `return 0`。

**Q: Wired / Google Research 偶尔报 SSL 或连接错误?**
这些是 RSS 源端偶发的瞬时错误,fetcher 会打 WARNING 后跳过,不影响其他源和邮件正常发出。

## License

MIT
# AI_DAILY
# AI_DAILY
