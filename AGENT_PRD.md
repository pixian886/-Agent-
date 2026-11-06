# 《从零开始Agent学习》Agent 开发课程需求文档（PRD）

> 版本：v1.0  
> 日期：2026-11-03  
> 项目类型：实践周项目后续扩展 / 下学期长期课程  
> 配套文档：`PRD.md`（Python 课程）、`AGENT_系统设计.md`  
> 当前状态：M13 A0–A3、M14 A4–A7 内容与 M15 结业项目及验收已完成

---

## 0. 文档说明

- Agent 课程建立在已完成的 Python 课程（L01–L11）之上，不重复 Python 基础。
- 全程使用真实 LLM API，学员自备 Key（BYOK）。
- 平台只负责课程、练习、轨迹校验与进度；**不保存学员 Key，不执行 Agent 代码，不代调用 LLM**。
- 本文档是 Agent 课程的开发、内容生产与验收依据。

---

## 1. 项目定位

**面向完成 Python 先修的零基础学员，从一次真实 API 调用开始，逐步构建可运行、可评测、可部署的 Agent 应用。**

课程不教模型训练，不把低代码平台作为主线；重点是：

- 理解 LLM API 与消息结构；
- 会写工具、工具注册表与 ReAct 循环；
- 会做记忆、检索与上下文工程；
- 会用轨迹规则评估 Agent；
- 能完成一个多角色协作的结业项目。

---

## 2. 课程目标

| 目标 | 说明 |
|-|-|
| 会调用 | 用 OpenAI 兼容接口完成真实 API 调用，能处理超时、限流与错误 |
| 会构建 | 从零写出工具注册表、ReAct 循环、记忆与 RAG |
| 会评估 | 用轨迹规则检查工具选择、参数、步数与最终答案 |
| 会协作 | 能设计两个以上角色的多 Agent 协作 |
| 会交付 | 结业项目可运行、可部署、有完整轨迹与 README |

---

## 3. 学员画像与先修

### 3.1 学员画像

- 完成 Python 课程 L01–L11，或具备同等基础；
- 能独立安装依赖、运行脚本、读写 `.env`；
- 自备可用的 LLM API Key；
- 本机可访问 LLM 服务。

### 3.2 硬性先修

| 能力 | 对应 Python 课 |
|-|-|
| 函数、类、列表/字典、嵌套结构 | L04–L06 |
| JSON 解析与文件读写 | L07 |
| `requests`、状态码、超时 | L08 |
| 异常、重试、`.env`、Key 安全 | L09 |
| SQLite 增删改查 | L10 |
| FastAPI 最小接口 | L11 |

> 未完成 Python 课程也可以浏览 Agent 课程，但平台会显示先修提示；不硬锁。

---

## 4. 项目范围

### 4.1 包含

- 多课程目录与课程切换；
- Agent 课程第 0 章 1 课 + 7 章 21 课 + 2 节结业课，共 24 课；
- 概念题、编程题、本地作业、轨迹题；
- 轨迹 JSON 校验与规则判定；
- 轨迹查看器；
- Agent 课程进度与结业项目。

### 4.2 不包含

- 模型训练、SFT、GRPO、Agentic-RL；
- GPU、模型微调、数据集训练；
- 把 Coze/Dify/n8n 作为主线；
- 服务端保存学员 Key；
- 服务平台代调用 LLM；
- 教师后台、班级管理、多租户。

---

## 5. 课程结构

课程 ID：`agent`  
课程标题：**Agent 开发：从 API 到多智能体**  
先修课程：`python`

| 章节 | 课时 | 标题 | 核心内容 | 练习 |
|-|-|-|-|-|
| 第 0 章 名词地图 | a00 | AI 时代名词地图 | LLM、Token、Prompt、Agent、Tool、ReAct、Memory/RAG、MCP、Skill、Harness、Workflow、Multi-Agent、Eval/Trace | 单选 + 填空 |
| 第 1 章 LLM 与真实 API | a01 | 从一次 API 调用开始 | OpenAI 兼容接口、`base_url`、messages、BYOK | 单选 + 本地作业 |
| 第 1 章 | a02 | 消息、提示词与参数 | system/user/assistant、提示词五要素、少样本、结构化输出、temperature、max_tokens、流式 | 2 单选 + 2 编程 |
| 第 1 章 | a03 | 错误、重试与成本 | 401/429/5xx、timeout、退避、token 成本 | 单选 + 本地作业 |
| 第 2 章 工具调用 | a04 | 工具三要素 | 名称、描述、参数、执行函数 | 编程 |
| 第 2 章 | a05 | 工具注册表 | 字典注册、按名调用、参数校验 | 编程 |
| 第 2 章 | a06 | 真实工具与失败处理 | 搜索/时间/SQLite 工具、错误返回 | 轨迹题 + 本地作业 |
| 第 3 章 ReAct | a07 | 思考-行动-观察 | ReAct 原理、与 CoT 的区别 | 单选 |
| 第 3 章 | a08 | 手写 ReAct 循环 | Action 解析、最大步数、Finish | 编程 |
| 第 3 章 | a09 | 轨迹与失败模式 | 循环、工具误用、幻觉、终止条件 | 轨迹题 |
| 第 4 章 记忆与 RAG | a10 | 对话记忆 | SQLite 存历史、窗口裁剪 | 编程 |
| 第 4 章 | a11 | 分块与检索 | chunk、embedding、关键词/向量检索 | 编程 |
| 第 4 章 | a12 | RAG 管道 | 文档 → 分块 → 检索 → 注入 → 回答 | 轨迹题 + 本地作业 |
| 第 5 章 上下文与 MCP | a13 | 上下文工程 | 裁剪、摘要、优先级、结构化上下文 | 单选 |
| 第 5 章 | a14 | MCP | 协议、工具发现、接一个 MCP 工具 | 单选 + 本地作业 |
| 第 5 章 | a15 | 工具安全 | prompt injection、越权、沙箱 | 轨迹题 |
| 第 6 章 评估、安全与成本 | a16 | 评测集与指标 | 任务集、成功率、步数、成本 | 单选 + 编程 |
| 第 6 章 | a17 | 轨迹规则 | 必需工具、顺序、最大步数、最终答案 | 轨迹题 |
| 第 6 章 | a18 | 成本与限流 | token 预算、缓存、限流、降级 | 单选 + 本地作业 |
| 第 7 章 多 Agent | a19 | 多 Agent 角色 | 分工、消息、共享状态 | 编程 |
| 第 7 章 | a20 | 编排与冲突 | 顺序/并行/监督者、终止条件 | 轨迹题 |
| 第 7 章 | a21 | 框架对照 | 手写 vs LangGraph/AutoGen，何时用 | 单选 |
| 结业项目 | a22 | 项目设计 | 选题、角色、工具、评测、从零搭建跟做 | 本地作业 ×2 |
| 结业项目 | a23 | 交付与演示 | 部署、README、轨迹、演示 | 本地作业 + 轨迹题 |

---

## 6. 功能需求

| 编号 | 功能 | 描述 | 验收标准 |
|-|-|-|-|
| F-A01 | 多课程目录 | 展示 Python 与 Agent 两门课程及先修关系 | `/courses` 可打开；两门课程卡片可进入路线页 |
| F-A02 | Agent 路线 | 第 0 章 + 7 章，共 24 课，显示完成度与继续学习 | 路线页按章节顺序展示；完成度按 Agent 课时计算 |
| F-A03 | 课时页复用 | Agent 课时复用 Markdown、概念卡、对比卡、步骤动画 | 24 课均可打开；卡片可放大；步骤动画可切换 |
| F-A04 | 概念题与编程题 | 复用现有单选、填空、站内编程题 | 判题四态正常；刷新恢复作答 |
| F-A05 | 本地作业 | 复杂 Agent 任务在本机完成，平台给答案与「标记完成」 | 任务卡含步骤、起步代码、常见报错、折叠答案；不执行代码 |
| F-A06 | 轨迹题 | 学员粘贴轨迹 JSON，平台按规则判定 | 规则全部通过为 `accepted`；否则 `wrong_answer`；展示每条规则结果；刷新回填 |
| F-A07 | 轨迹查看器 | 把轨迹按步骤展示 | 时间线显示 thought/action/observation；工具名与参数可读 |
| F-A08 | 课程进度隔离 | Python 与 Agent 进度互不影响 | 两门课程完成度分别计算；切换课程不串数据 |
| F-A09 | Key 安全 | 平台不保存 Key，不代调用 LLM | 页面与日志不出现真实 Key；课程示例只出现占位 Key |
| F-A10 | 结业项目 | 轨迹 + 本地验收 | 提交多角色轨迹并通过规则；本地项目可运行、有 README |
| F-A11 | 内容校验 | Agent 课程文件启动时校验 | 课时、练习、轨迹规则缺失时启动失败并输出文件路径 |
| F-A12 | 先修提示 | 未完成 Python 课程时提示先修 | Agent 路线页显示「建议先完成 Python 课程」，不阻止访问 |

---

## 7. 关键业务规则

| 规则 | 定义 |
|-|-|
| 课程切换 | 顶部导航提供课程入口；`/roadmap` 默认进入 Python 课程 |
| 课程完成 | 该课程全部课时完成；Agent 课程按 24 课计算 |
| 先修关系 | Agent 课程先修为 Python；只提示，不硬锁 |
| 轨迹题判定 | 校验 JSON 结构 → 逐条规则；全部通过 `accepted`，任意失败 `wrong_answer` |
| 轨迹题保存 | 最新轨迹存入 `exercise_progress.last_answer`；刷新回填 |
| 轨迹题限制 | JSON ≤ 100KB；steps ≤ 50；字符串字段 ≤ 2000 字符 |
| 轨迹题安全 | 平台只解析 JSON，不执行代码、不访问网络、不调用 LLM |
| 本地作业 | 平台不检查、不执行、不上传；学员自报完成 |
| 真实 API | 课程示例与项目使用真实 API；课堂练习可用录制回放 |
| Key 安全 | Key 只放学员本机 `.env`；平台不存储、不打印、不提交 |
| 成本控制 | 示例默认 `temperature=0`、限制 `max_tokens`、重试上限 3 次 |
| 模型兼容 | OpenAI 兼容接口；`LLM_API_KEY` / `LLM_MODEL_ID` / `LLM_BASE_URL` |
| 内容引用 | Hello-Agents 作为知识映射参考，不复制原文；标注来源 |
| 不展示次数 | 练习界面不显示提交次数；`attempts` 仅内部统计 |

---

## 8. 轨迹题设计

### 8.1 轨迹 JSON

```json
{
  "version": 1,
  "task_id": "a09-reAct-weather",
  "model": "deepseek-chat",
  "steps": [
    {"type": "thought", "content": "需要先查询北京天气"},
    {"type": "action", "tool": "get_weather", "arguments": {"city": "beijing"}},
    {"type": "observation", "content": "北京 26℃"},
    {"type": "thought", "content": "信息足够，可以回答"},
    {"type": "finish", "content": "北京今天 26℃，适合出行。"}
  ],
  "final_answer": "北京今天 26℃，适合出行。"
}
```

### 8.2 支持规则

| 规则 | 说明 |
|-|-|
| `required_tool` | 必须调用指定工具，可要求参数键 |
| `tool_order` | 多个工具按顺序出现 |
| `max_steps` | 总步骤不超过上限 |
| `min_steps` | 总步骤不少于下限 |
| `max_tool_calls` | 工具调用次数不超过上限 |
| `forbidden_tool` | 不得调用指定工具 |
| `final_answer_contains` | 最终答案必须包含关键词 |
| `no_error_steps` | 不得出现 `error` 类型步骤 |

示例：

```json
"rules": [
  {"type": "required_tool", "tool": "get_weather", "args": ["city"]},
  {"type": "max_steps", "value": 8},
  {"type": "final_answer_contains", "value": "26"}
]
```

### 8.3 判定结果

```json
{
  "status": "accepted",
  "message": "轨迹通过全部规则",
  "rule_results": [
    {"rule": "required_tool", "passed": true, "detail": "已调用 get_weather"},
    {"rule": "max_steps", "passed": true, "detail": "5 步，未超过 8 步"}
  ]
}
```

- 任一规则失败即为 `wrong_answer`；
- 规则结果全部展示，不只显示第一条；
- 解析失败返回 `wrong_answer`，提示 JSON 位置。

---

## 9. 课程内容设计

### 9.1 每课结构

1. 学习目标：1–2 条；
2. 概念讲解：至少 1 个视觉卡片；
3. 可运行代码：真实 API 示例，Key 用占位；
4. 步骤动画：重点课 2–4 步；
5. 练习：概念题、编程题、轨迹题或本地作业；
6. 小结：3–5 条。

正文 600–1500 字；代码必须在 Python 3.10+ 运行通过。

### 9.2 视觉安排

| 课时 | 组件 | 内容 |
|-|-|-|
| a00 | 概念卡 + 对比卡 | LLM → Agent → Harness 关系图；chatbot / workflow / agent 对比 |
| a01 | 概念卡 | 一次 LLM 调用：messages → API → response |
| a02 | 对比卡 | system / user / assistant 三种消息 |
| a03 | 步骤动画 | 429 重试与退避 |
| a04 | 概念卡 | 工具三要素：名称、描述、参数、执行 |
| a05 | 对比卡 | 直接调用 vs 注册表调用 |
| a06 | 步骤动画 | 模型选择工具 → 执行 → 观察 |
| a07 | 概念卡 | ReAct 的思考-行动-观察循环 |
| a08 | 步骤动画 | 一次 ReAct 循环的 4 步 |
| a09 | 概念卡 | 失败轨迹：循环、误用、幻觉 |
| a10 | 概念卡 | 记忆是带时间戳的对话表 |
| a11 | 对比卡 | 关键词检索 vs 向量检索 |
| a12 | 步骤动画 | RAG 五步管道 |
| a13 | 概念卡 | 上下文预算像行李箱 |
| a14 | 概念卡 | MCP 是工具插座 |
| a15 | 提示卡 | prompt injection 与工具越权 |
| a16 | 概念卡 | 评测集、成功率、步数、成本 |
| a17 | 对比卡 | 规则判题 vs LLM-as-Judge |
| a18 | 步骤动画 | 限流、缓存、降级 |
| a19 | 概念卡 | 多 Agent 分工 |
| a20 | 步骤动画 | 监督者编排 |
| a21 | 对比卡 | 手写 vs 框架 |
| a22–a23 | 项目清单 | 选题、角色、工具、评测、部署 |

### 9.3 前置课 a00：AI 时代名词地图

**目标**：不写代码、不需要 Key，先建立一张名词地图。学员学完能区分常见概念，知道后面每章在讲什么。

**必须讲清**：

| 名词 | 一句话解释 | 常见误解 |
|-|-|-|
| LLM | 能按上下文预测下一个 token 的模型 | 不是知识库，也不是数据库 |
| Token / Context | 模型读写文本的计量单位与窗口 | 不是字数；窗口有上限 |
| Prompt | 给模型的指令与上下文 | 不是越长越好 |
| Agent | LLM + 工具 + 循环 + 状态 | 不是会聊天的 chatbot |
| Tool / Function Calling | Agent 可调用的外部函数 | 不是模型自己执行 |
| ReAct | 思考 → 行动 → 观察的循环 | 不是唯一范式 |
| Memory / RAG | 记住历史；先检索再回答 | RAG 不是微调 |
| MCP | 连接 Agent 与工具/数据源的协议 | 不是某个框架 |
| Skill | 可复用的流程知识与步骤 | 不是单个工具 |
| Harness | 包在 Agent 循环外的工程外壳：工具协议、权限、状态、trace、评测 | 不是模型本身 |
| Workflow | 固定步骤的流程编排 | 稳定任务优先用 workflow |
| Multi-Agent | 多个角色按职责协作 | 不是角色扮演越多越好 |
| Eval / Trace | 评测集与执行轨迹 | demo 不等于可交付 |

**关系图**：

- LLM 是大脑；
- Agent = LLM + tools + loop + state；
- Harness 是外壳；
- MCP 连接工具/数据；
- Skill 是可复用流程；
- RAG 是检索增强；
- ReAct 是循环范式；
- Eval/Trace 是质量保障。

**讲完能回答**：

1. chatbot、workflow、agent 的区别？
2. tool、skill、MCP 各解决什么问题？
3. 为什么 harness 决定 Agent 是否可交付？

**不展开**：Transformer 数学、框架 API、微调、Agentic-RL。

**练习**：单选「MCP 的作用」；填空「连接 Agent 与外部工具/数据源的协议简称」。

### 9.4 内容依据

- OpenAI Chat Completions API 文档；
- `requests` 官方文档；
- MCP 官方规范；
- SQLite 官方文档；
- Anthropic《Building effective agents》、OpenAI《A practical guide to building agents》；
- Hello-Agents（Datawhale，CC BY-NC-SA 4.0）作为知识映射参考，不复制原文；
- Agent-Learning-Hub（Datawhale）作为学习路线与名词索引参考，只引用链接与要点，不复制原文；
- 所有示例使用 OpenAI 兼容接口，不绑定单一厂商。

---

## 10. 非功能需求

| 类别 | 要求 |
|-|-|
| 并发 | 30 人以内；轨迹判题不执行代码，单次 < 100ms |
| 安全 | 不存 Key、不代调用 LLM、不执行 Agent 代码；CSRF 与限流沿用 M9 |
| 数据 | 轨迹只保留最新一份；不保存提交历史 |
| 内容 | Agent 课程文件与 Python 课程分离；启动时校验 |
| 兼容 | 桌面 Chrome / Edge；页面离线可用，真实 API 任务需联网 |
| 可维护 | 课程内容用 JSON + Markdown 维护，新增课程不改代码 |
| 成本 | 示例限制 token；重试上限；建议使用小模型 |

---

## 11. 里程碑

| 阶段 | 交付物 | 完成标准 |
|-|-|-|
| M11 多课程底座 | 课程目录、`/courses`、Agent 路线、进度隔离 | 已完成：两门课程可切换，Python 课程不回归 |
| M12 轨迹题引擎 | `trajectory_task` 解析、规则、结果展示、回填 | 已完成：合法轨迹通过，缺工具/超步数/答案不符均返回逐条结果 |
| M13 A0–A3 内容 | 10 课正文、视觉、练习 | 已完成：a00–a09 可打开，15 道练习可提交，4 张新 SVG |
| M14 A4–A7 内容 | 12 课正文、视觉、练习 | 已完成：a10–a21 可打开，Agent 合计 31 道练习，5 张新 SVG |
| M15 结业与验收 | a22–a23、结业项目、验收记录 | 已完成：a22/a23 上线，结业轨迹 `ag33` 通过规则，验收记录已补 |

---

## 12. 风险与应对

| 风险 | 影响 | 应对 |
|-|-|-|
| 学员 Key 泄露 | 高 | 平台不存 Key；课程只出现占位；示例强调 `.env` 与 `.gitignore` |
| API 成本失控 | 中 | 小模型、`max_tokens`、重试上限、成本示例 |
| 模型差异导致结果不稳定 | 中 | 轨迹题按工具/步骤规则判定，不比对自然语言全文 |
| 轨迹伪造 | 中 | 要求真实运行并保留工具参数；结业项目演示 + 抽查 |
| 内容量过大 | 中 | 先完成 A1–A3，再逐章扩展；复用卡片模板 |
| API 变更 | 中 | 只依赖 OpenAI 兼容接口；示例集中在客户端封装 |
| Prompt injection | 中 | a15 专门讲工具越权与输入隔离；示例使用只读工具 |

---

## 13. 验收清单

- [ ] `/courses` 显示 Python 与 Agent 两门课程；
- [ ] Agent 路线显示第 0 章 + 7 章，共 24 课与完成度；
- [ ] 未完成 Python 时显示先修提示，但不阻止访问；
- [ ] a00 能区分 LLM、Agent、Harness、MCP、Skill、Workflow 等名词；
- [ ] a00–a09 页面可打开，视觉组件正常；
- [ ] 概念题、编程题、本地作业可正常提交/标记；
- [ ] 轨迹题提交合法 JSON 返回 `accepted`；
- [ ] 轨迹题缺工具、超步数、最终答案不符时返回 `wrong_answer`；
- [ ] 轨迹规则结果逐条展示；
- [ ] 刷新页面后轨迹回填；
- [ ] Python 与 Agent 进度互不影响；
- [ ] 页面与日志不出现真实 Key；
- [ ] 结业项目轨迹通过规则，本地项目可运行；
- [ ] 现有 Python 课程全部回归通过。

---

## 14. 附录：轨迹题最小示例

```json
{
  "version": 1,
  "task_id": "a09-ReAct-weather",
  "steps": [
    {"type": "thought", "content": "先查天气"},
    {"type": "action", "tool": "get_weather", "arguments": {"city": "beijing"}},
    {"type": "observation", "content": "26℃"},
    {"type": "finish", "content": "北京 26℃"}
  ],
  "final_answer": "北京 26℃"
}
```
