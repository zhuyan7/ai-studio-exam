# 方案设计文档

## 1. 需求收敛

题目要求「学习辅导 AI 助教」限定一门学科，做讲懂—练对—记下—再练的闭环。团队选定 **Python 程序设计** 作为学科，理由：

- 知识点体系清晰，可枚举为树形结构
- 编程题可真实运行判对错，MVP 第③项「练习可作答、可判定对错」能做扎实
- 题库可自建 JSON，不依赖外部数据源

MVP 四项中选 ②③④，①作为加分项：

| 项 | 选择理由 |
|---|---|
| ②错题录入与自动归类 | 闭环入口，归类靠 LLM 判断知识点 |
| ③薄弱点针对性练习 | 闭环核心，出题靠 LLM，判对错靠真实运行 |
| ④学习进度记录 | 闭环反馈，从②③数据统计掌握度 |
| ①知识点问答（加分） | 顺手实现，限定学科范围 |

## 2. 架构

```
浏览器 (单页 HTML/JS)
    │  HTTP
    ▼
FastAPI ── 路由层 ──┬── wrong_book   ── LLM 归类 ──┐
                    ├── practice     ── LLM 出题 ──┤
                    ├── progress     ── 统计      ──┤
                    └── qa           ── LLM 问答 ──┤
                                                      ▼
                              SQLite (tutor.db) ◄── 数据持久化
                                                      ▲
                              subprocess 判题引擎 ────┘
```

## 3. 数据模型

- `knowledge_points`：知识点树（20 个，id/name/parent/desc）
- `questions`：题库（seed 题库 + LLM 生成题，含测试用例 JSON）
- `wrong_questions`：错题本（录入时间、归类知识点、题型）
- `practice_records`：练习记录（作答、是否通过、知识点）
- `mastery`：掌握度（按知识点聚合：总次数/正确/错误/掌握度分）

掌握度 = correct / total，简单直观，未引入遗忘曲线。

## 4. 判题引擎设计

核心思路：学生代码（定义函数）+ 测试用例（调用表达式 + 期望值）拼成一段脚本，subprocess 真实运行，逐条 eval 比对。

```python
# 拼接脚本示意
{学生代码}              # def add(a,b): return a+b
import json
__tests = json.loads(...)
for __t in __tests:
    __got = eval(__t['call'])   # eval("add(1,2)")
    __ok = __got == __t['expected']
```

安全措施：subprocess 超时（默认 5 秒）防死循环；捕获 stderr。未做 import 白名单（已知问题）。

## 5. LLM 调用策略

- **错题归类**：temperature=0，json_mode，要求返回 `{kp_id, kp_name, qtype}`
- **练习生成**：temperature=0.7，json_mode，要求返回含 stem/solution/tests
- **知识点问答**：temperature=0.4，system prompt 限定只答 Python 相关

DeepSeek 使用 OpenAI 兼容接口，`response_format={"type":"json_object"}` 强制 JSON 输出，减少解析失败。

## 6. 遇到的问题与解决

| 问题 | 解决 |
|---|---|
| LLM 输出 JSON 偶有格式偏差 | 开启 json_mode + try/except 降级提示 |
| 学生代码死循环卡死判题 | subprocess timeout=5s |
| expected 中 true/null 与 Python True/None 不一致 | 测试用例以 JSON 存储，脚本内 json.loads 自动转换 |
| 评委复现需零配置 | SQLite 文件库 + 种子数据启动即建表 + Docker 一键启动 |

## 7. 未完成与降级

- 选择题/填空题判对错未实现：当前仅编程题可自动判，非编程题归类后仅记录不判题
- RAG 未接入：预留接口，若有教材 PDF 可扩展向量检索
- import 白名单未做：考核环境可接受，生产需加固
- 多用户隔离未做：当前单用户，mastery 按知识点全局聚合

## 8. 取舍说明

- 选 SQLite 而非 Postgres：零配置，评委复现成本最低
- 选原生前端而非 React：零构建，避免前端工程化拖累复现
- 判题用 subprocess 而非在线 judge：足够考核演示，且无外部依赖