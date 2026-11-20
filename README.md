# Python 学习辅导 AI 助教

> GDUF AI Studio 2026 二轮考核 · 方向一 · 选题 B：学习辅导 AI 助教（学科：Python 程序设计）

面向 **Python 程序设计** 这门课的闭环学习助教：录入错题自动归类 → 依据薄弱点生成针对性练习 → 真实运行代码判对错 → 记录掌握度。不是通用问答机器人，而是限定学科的「讲懂—练对—记下—再练」闭环。

## 解决什么问题

直接拿通用大模型当助教，效果停留在「这道题答案是什么」。真正的学习需要重复：记下做错的题、针对薄弱环节再练一遍、看到自己的进度。本应用把范围收窄到 Python 一门课，让知识点可组织、错题可归类、生成的练习真正落在薄弱点上，且**编程题能真实运行判对错**，不靠模型猜。

## 技术栈

- **后端**：Python 3.11 + FastAPI + Uvicorn
- **存储**：SQLite（开箱即用，无需额外服务）
- **大模型**：DeepSeek（OpenAI 兼容接口），用于错题归类、练习生成、知识点问答
- **判题**：subprocess 真实运行学生 Python 代码 + 测试用例比对
- **前端**：原生 HTML/CSS/JS 单页，零构建零依赖
- **部署**：Docker / docker-compose

## 目录结构

```
python-tutor-ai/
├── app/
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 配置（环境变量）
│   ├── db.py              # SQLite 初始化与种子数据
│   ├── models.py          # Pydantic 请求/响应模型
│   ├── llm.py             # DeepSeek 调用封装
│   ├── prompts.py         # prompt 模板
│   ├── judge.py           # 代码判题引擎（subprocess 运行）
│   └── routers/
│       ├── wrong_book.py  # ② 错题录入与自动归类
│       ├── practice.py    # ③ 薄弱点针对性练习
│       ├── progress.py    # ④ 学习进度/掌握度
│       └── qa.py          # ① 知识点问答（加分项）
├── data/
│   ├── knowledge_tree.json   # Python 知识点体系（20 个）
│   └── seed_questions.json   # 示例题库（8 道编程题，含测试用例）
├── static/                # 前端单页
├── tests/
│   └── test_judge.py      # 判题引擎自检
├── docs/
│   └── design.md          # 方案设计文档
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 环境搭建与启动

### 方式一：本地运行

```bash
# 1. 安装依赖（Python 3.11+）
pip install -r requirements.txt

# 2. 配置 DeepSeek API Key
cp .env.example .env
#   编辑 .env，填入 DEEPSEEK_API_KEY=sk-你的真实key
#   key 获取：https://platform.deepseek.com/

# 3. 启动
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. 打开浏览器
#   http://localhost:8000
```

### 方式二：Docker

```bash
# 1. 配置 .env（同上）
cp .env.example .env  # 填入 DEEPSEEK_API_KEY

# 2. 构建并启动
docker-compose up -d --build

# 3. 访问 http://localhost:8000
# 4. 数据持久化在 ./data 目录，停止不丢
# 5. 停止
docker-compose down
```

容器内端口 `8000`，数据持久化路径 `/app/data`，环境变量通过 `.env` 注入。

## 功能清单与验证方式

| MVP | 功能 | 验证方式 |
|---|---|---|
| ② | 错题录入与自动归类 | 打开「错题本」页，输入题目→录入→自动归类到知识点，列表可见归类标签 |
| ③ | 薄弱点针对性练习 | 先录几道错题制造薄弱点，点「按薄弱点生成练习」→出题→作答→提交判题，对错由真实运行判定 |
| ④ | 学习进度/掌握度 | 「学习进度」页展示各知识点掌握度条形图、正确率、薄弱点排序 |
| ① | 知识点问答（加分） | 「知识点问答」页提问 Python 概念，回答限定学科范围 |

**判题原理**：学生提交的 Python 代码（定义函数）+ 题目测试用例（调用表达式+期望值）拼成脚本，subprocess 真实运行，逐条 `eval` 比对。对错确定，不依赖 LLM。

**示例数据**：`data/seed_questions.json` 内置 8 道 Python 编程题（覆盖函数/递归/列表/字符串/字典/循环/异常等知识点），评审无需自行构造即可跑通主流程。

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/wrong` | 录入错题，自动归类 |
| GET | `/api/wrong` | 列出错题 |
| GET | `/api/practice/seed` | 从题库取题 |
| POST | `/api/practice/generate` | 按薄弱点生成练习 |
| POST | `/api/practice/submit?qid=...` | 提交作答并判对错 |
| GET | `/api/progress/mastery` | 各知识点掌握度 |
| GET | `/api/progress/weak` | 薄弱点排序 |
| GET | `/api/progress/summary` | 总览统计 |
| POST | `/api/qa` | 知识点问答 |

交互式文档：启动后访问 `http://localhost:8000/docs`（Swagger UI）。

## 自检

```bash
python -m pytest tests/ -v
```

判题引擎测试不依赖网络与 API Key，验证核心判对错逻辑。

## 团队分工

| 成员 | 负责部分 |
|---|---|
| （待填写） | |
| （待填写） | |
| （待填写） | |
| （待填写） | |

> 请各队按实际分工填写，答辩时需能讲清各自负责部分与整体设计。

## 已知问题与未完成部分

- 判题引擎在沙箱内运行学生代码，已设超时（默认 5 秒）防死循环，但未做 import 白名单限制，生产环境需加固
- 选择题/填空题的自动判对错尚未实现，当前判题仅支持编程题（coding）
- RAG（结合教材/课件检索）为可选加分项，当前未接入，预留了扩展点
- 掌握度计算为简单正确率，未引入遗忘曲线等更精细模型

## 技术选型说明

- **DeepSeek**：OpenAI 兼容接口，国内可直连，价格低，适合学生项目
- **SQLite**：零配置，文件即数据库，便于 Docker 持久化与评审复现
- **subprocess 判题**：Python 学科天然优势，代码可真实运行，对错确定不靠 LLM 猜
- **原生前端**：零构建零依赖，避免前端工程化增加复现负担

## 许可

本项目为 GDUF AI Studio 考核作品，核心实现由团队自行完成，允许参考公开资料。