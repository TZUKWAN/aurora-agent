# Aurora Agent 最终版任务清单

> 合并自：审计遗留修复(A)、功能扩充(B)、Codex借鉴(C)三份清单。
> 去重规则：A1 SessionDB 与 C5 对话回溯合并；A8 CLI 与 C4 非交互执行合并。
> 所有任务统一编号 T01-T24，按优先级 P0→P4 排列。

---

## 优先级总览

| 级别 | 任务 | 简述 |
|------|------|------|
| **P0** | T01 | SessionDB 持久化 + 对话回溯 |
| **P0** | T02 | PPT 实际文件导出 |
| **P0** | T03 | CLI 功能扩充 + 非交互执行模式 |
| **P0** | T04 | 配置与部署完善 |
| **P1** | T05 | 项目信息结构化输入 |
| **P1** | T06 | 评估引擎 LLM 升级 |
| **P1** | T07 | 自动质量审核与迭代优化 |
| **P1** | T08 | DOCX 导出增强 |
| **P1** | T09 | AGENTS.md 层级化指令 |
| **P2** | T10 | 商业计划书大纲编辑器 |
| **P2** | T11 | 答辩模拟与评分系统 |
| **P2** | T12 | 竞品分析模块 |
| **P2** | T13 | VisualDesigner 集成 |
| **P2** | T14 | 沙箱安全机制 |
| **P2** | T15 | 多图片输入支持 |
| **P3** | T16 | Web API 服务 (FastAPI) |
| **P3** | T17 | MCP 协议支持 |
| **P3** | T18 | 竞赛资料库扩充 |
| **P3** | T19 | 团队与导师信息管理 |
| **P3** | T20 | SwarmBus 多智能体通信集成 |
| **P3** | T21 | TaskDecomposer LLM 动态分解 |
| **P4** | T22 | PDF 导出 |
| **P4** | T23 | 多语言支持 (中英文) |
| **P4** | T24 | TUI 终端界面 |

---

## P0 — 核心可用性

---

### T01. SessionDB 持久化 + 对话回溯

> 合并原 A1 (SessionDB 集成) + C5 (对话回溯与历史编辑)

**问题**: 会话不持久化，CLI 重启后丢失；无法回溯编辑历史消息。

#### 1.1 SessionDB 增强

**文件**: `aurora/memory/session_db.py`

- 修改 `__init__` 签名为 `__init__(self, db_path: Optional[str] = None)`
- 当 `db_path` 为 None 时，从 `Config.session.db_path` 读取
- 添加 `list_sessions()` 方法：返回所有 session 摘要列表
- 添加 `delete_session(session_id)` 方法：删除指定 session
- 添加 `search_sessions(keyword)` 方法：按项目名搜索 session
- 添加 `cleanup_old_sessions(max_age_days=30)` 方法：清理过期 session

#### 1.2 对话回溯系统

**文件**: `aurora/history.py`（新建）

- `ConversationHistory` 类：管理消息列表与编辑历史
- `add(role, content)` 方法：添加消息
- `edit(index, new_content)` 方法：编辑指定位置的消息，截断后续消息
- `undo()` / `redo()` 方法：撤销/重做操作
- `get_messages()` 方法：返回当前消息列表
- `branch_from(index)` 方法：从指定位置创建分支（保留原始历史）

#### 1.3 Agent 集成

**文件**: `aurora/agent.py`

- 在 `__init__` 中初始化 `self.memory = MemoryManager(config.session.db_path)`
- 将 `self.messages: List` 替换为 `self.history = ConversationHistory()`
- 在 `run()` 中：messages 为空时自动创建/恢复 session
- 将用户输入和 AI 回复保存到 session
- 添加 `edit_message(index, new_content)` 方法：编辑后从该点重新执行
- 添加 `list_sessions()` / `load_session(session_id)` 方法

#### 1.4 工具层集成

**文件**: `aurora/tools/business_plan_tools.py`

- `_bp_generate_handler`：生成完成后将完整 plan 保存到 session
- `_bp_section_write_handler`：章节内容保存到 session 的 sections 表
- `_bp_export_handler`：导出时从 session 读取最新 plan 数据

#### 1.5 CLI 集成

**文件**: `aurora/cli.py`

- 添加 `sessions` / `history` 子命令：列出所有历史 session
- 添加 `resume <session_id>` 子命令：恢复指定 session
- 添加 `delete <session_id>` 子命令：删除指定 session
- chat 模式启动时检查是否有未完成 session，提示是否恢复
- chat 循环中添加快捷命令：
  - `/edit <N>`: 编辑第 N 条消息
  - `/undo`: 撤销最近操作
  - `/redo`: 重做
  - `/history`: 显示完整历史（带编号，标注已编辑消息）

#### 1.6 测试

**文件**: `tests/test_memory.py`（重写）, `tests/test_history.py`（新建）

- 测试 create_or_update_session / save_section / load_session
- 测试 list_sessions / delete_session / cleanup_old_sessions
- 测试 ConversationHistory 的 add/edit/undo/redo/branch
- 测试 Agent 与 MemoryManager 的集成
- 测试编辑消息后对话重新执行

---

### T02. PPT 实际文件导出

> 原A4

**问题**: `PPTGenerator` 只生成 JSON 结构，不生成实际 .pptx 文件。

#### 2.1 PPTX 导出器

**文件**: `aurora/presentation/pptx_exporter.py`（新建）

- `PPTXExporter` 类
- `__init__`: 初始化 python-pptx 模板
- `export(ppt_content, filepath)` 方法：将 PPTGenerator 的 JSON 转换为 .pptx
- 为每页 slide 设置布局：标题居中、要点列表、配色方案
- 生成封面页：项目名、团队名、竞赛名、日期
- 生成内容页：标题 + 要点列表（每页最多 5 个要点）
- 生成结尾页：感谢语 + 联系方式
- `_apply_theme(prs, theme_name)` 私有方法：支持自定义主题（莫兰迪、商务蓝、科技风等）

#### 2.2 Generator 集成

**文件**: `aurora/presentation/ppt_generator.py`

- 添加 `export_to_pptx(ppt_content, filepath, theme)` 方法：调用 PPTXExporter

#### 2.3 工具注册

**文件**: `aurora/tools/presentation_tools.py`

- 修改 `ppt_generate` handler：生成 JSON 后可选调用导出 .pptx
- 添加 `ppt_export` 工具：将已有 PPT JSON 导出为 .pptx 文件
- 注册新工具到 registry

#### 2.4 依赖与测试

- `pyproject.toml`: 在 optional-dependencies.export 中添加 `python-pptx>=1.0`
- `tests/test_pptx_export.py`（新建）：测试基本导出、不同主题、文件格式验证

---

### T03. CLI 功能扩充 + 非交互执行模式

> 合并原 A8 (CLI 扩充) + C4 (Headless Exec)

**问题**: CLI 只有 `chat` 子命令，缺少快捷命令和自动化执行能力。

#### 3.1 交互式子命令

**文件**: `aurora/cli.py`

- 添加 `generate` 子命令：
  ```
  aurora generate --name "AI助手" --tech "人工智能" --market "企业" --competition internet_plus
  ```
  - 支持 `--output` 指定输出路径
  - 支持 `--format md|docx` 指定格式
- 添加 `evaluate` 子命令：
  ```
  aurora evaluate --tech "AI" --innovation "原创算法" --team "985团队" --competition internet_plus
  ```
- 添加 `match` 子命令：`aurora match --tech "AI" --market "企业"`
- 添加 `export` 子命令：`aurora export <session_id> --format docx`
- 所有子命令支持 `--config` 指定配置文件路径

#### 3.2 非交互执行模式 (Headless Exec)

**文件**: `aurora/cli.py`

- 添加 `exec` 子命令：`aurora exec "生成一份AI教育领域的商业计划书"`
- 参数：`--prompt / -p`（必填）、`--output / -o`、`--format / -f`（text/json/md）、`--config`、`--model`、`--timeout`（秒）、`--quiet / -q`
- 执行流程：初始化 Agent → `agent.run(prompt)` → 输出到 stdout 或文件
- 退出码：0=成功，1=失败

#### 3.3 批处理

**文件**: `aurora/batch.py`（新建）

- `BatchProcessor` 类
- `process_file(tasks_file)` 方法：从 JSON/YAML 读取任务列表逐个执行
- `process_stdin()` 方法：从 stdin 逐行读取任务
- 支持并行执行（`--parallel` 参数）
- 支持失败重试（`--retry` 参数）

- `aurora/cli.py` 添加 `batch` 子命令：
  ```
  aurora batch tasks.json --parallel 3 --retry 2 --output-dir ./output
  ```

#### 3.4 测试

- `tests/test_cli.py`（新建）：测试各子命令参数解析与执行流程
- `tests/test_exec.py`（新建）：测试 exec 模式、超时处理、批处理

---

### T04. 配置与部署完善

> 原A9

#### 4.1 环境变量模板

**文件**: `.env.example`（新建）

- 列出所有环境变量及说明：
  ```
  AURORA_API_KEY=        # LLM API 密钥（必填）
  AURORA_BASE_URL=       # API 地址（必填）
  AURORA_MODEL=          # 模型名称（可选，覆盖 config.yaml）
  ```

#### 4.2 dotenv 支持

**文件**: `aurora/config.py`

- 添加 `from dotenv import load_dotenv`（可选依赖）
- 在 `load_config` 中自动加载 `.env` 文件

#### 4.3 日志配置

**文件**: `aurora/logging_config.py`（新建）

- 统一配置 logging
- 在 `aurora/config.py` 中添加 `LoggingConfig` dataclass
- 在 `load_config` 中配置日志级别和输出格式

#### 4.4 版本信息

- `aurora/__init__.py` 中添加 `__version__ = "0.1.0"`
- CLI 添加 `--version` 参数
- chat 模式启动时显示版本号

#### 4.5 测试

- `tests/test_config.py`（新建）：测试配置加载、环境变量覆盖、validate_config

---

## P1 — 功能完整性

---

### T05. 项目信息结构化输入

> 原B8

**问题**: project_info 是自由字典，缺少结构化验证。

#### 5.1 数据模型

**文件**: `aurora/models/project.py`（新建）

- Pydantic `ProjectInfo` 模型
- 字段：project_name, technology, problem, solution, product, target_market, business_model, team_background, funding, milestones 等
- 每个字段添加 description 和 validator

**文件**: `aurora/models/plan.py`（新建）

- `BusinessPlan` Pydantic 模型：metadata + sections
- `Section` 模型：title, content, word_count
- `FinancialData` 模型：unit_price, volumes, costs 等

**文件**: `aurora/models/evaluation.py`（新建）

- `EvaluationResult` 模型：overall_score, dimensions, suggestions, feedback
- `DimensionScore` 模型：name, score, feedback, suggestions

#### 5.2 自然语言解析器

**文件**: `aurora/parser.py`（新建）

- `parse_project_input(user_input)` 方法：使用 LLM 从自然语言中提取 ProjectInfo
- 返回结构化 ProjectInfo 对象

#### 5.3 Agent 集成

**文件**: `aurora/agent.py`

- 在 `run()` 中：对用户输入先调用 parser 提取结构化信息
- 将结构化信息传递给各工具 handler
- 修改所有工具 handler：接收 Pydantic 模型而非原始 dict

#### 5.4 测试

- `tests/test_models.py`（新建）：测试 ProjectInfo 验证逻辑、parser 提取功能

---

### T06. 评估引擎 LLM 升级

> 原A5

**问题**: 评估完全基于关键词匹配，无法给出有价值建议。

#### 6.1 LLM 评估

**文件**: `aurora/evaluation/engine.py`

- 修改 `__init__` 签名为 `__init__(self, config: Optional[Config] = None)`
- 初始化 LLM 客户端（与 generator 相同模式）
- 添加 `_llm_evaluate(project_info, dimensions)` 方法：使用 LLM 按维度打分（0-100），给出具体反馈和改进建议
- 修改 `evaluate` 方法：优先使用 LLM 评估，LLM 不可用时回退到关键词匹配
- 添加 `_parse_llm_evaluation(response_text)` 方法：解析 LLM 返回的 JSON 格式评估结果

#### 6.2 测试

- `tests/test_evaluation.py`：添加 LLM 评估的 mock 测试，确保关键词回退测试仍通过

---

### T07. 自动质量审核与迭代优化

> 原B6

**目标**: 生成内容后自动审核质量，发现问题自动重新生成。

#### 7.1 质量审核器

**文件**: `aurora/quality/auditor.py`（新建）

- `PlanAuditor` 类
- `__init__(self, config)`: 初始化 LLM 客户端
- `audit(plan)` 方法：
  1. 检查各章节字数是否达标
  2. 检查章节间逻辑一致性（财务数据是否前后矛盾）
  3. 检查是否有空洞废话（"将不断优化" "持续提升" 等）
  4. 检查是否有重复内容
  5. 使用 LLM 判断内容质量
- `audit_section(section_id, content, project_info)` 方法：审核单章节
- `check_consistency(plan)` 方法：检查全文一致性
- `score_quality(plan)` 方法：对 plan 整体质量打分（0-100）
- 返回结构化审核报告：问题列表 + 严重程度 + 修改建议

#### 7.2 自动优化器

**文件**: `aurora/quality/optimizer.py`（新建）

- `PlanOptimizer` 类
- `optimize(plan, audit_report)` 方法：根据 audit_report 逐一修复，使用 LLM 重写不达标章节，最大迭代 3 次
- `optimize_section(section_id, content, issues)` 方法：修复单章节

#### 7.3 工具与 Agent 集成

**文件**: `aurora/tools/quality_tools.py`（新建）

- 注册 `plan_audit` / `plan_optimize` 工具

**文件**: `aurora/agent.py`

- 注册 quality_tools
- 在 `bp_generate` handler 中：生成后自动触发 audit
- 如果 audit 分数低于 70，自动触发 optimize

#### 7.4 测试

- `tests/test_quality.py`（新建）：测试 audit 流程、optimize 流程、闭环（generate → audit → optimize → audit）

---

### T08. DOCX 导出增强

> 原A7

**问题**: DOCX 导出简陋，只有标题+正文。legacy_scripts 中有完善的排版逻辑。

#### 8.1 图表引擎

**文件**: `aurora/visuals/chart_engine.py`（新建）

- 移植 `legacy_scripts/plan-ai/visual_chart_engine.py` 核心函数
- 提取 `draw_org_chart`, `draw_timeline`, `draw_flow_chart`, `draw_matrix` 等函数
- 去除硬编码 Windows 字体路径，改为自动检测系统字体

#### 8.2 DOCX 排版器

**文件**: `aurora/business_plan/docx_builder.py`（新建）

- 移植 `legacy_scripts/plan-ai/build_docx_final.py` 的排版逻辑
- 提取页边距、字体、标题样式设置
- 提取表格生成、图片插入和定位逻辑

#### 8.3 Generator 集成

**文件**: `aurora/business_plan/generator.py`

- 修改 `export_to_docx`：使用新的 DocxBuilder
- 支持封面页、目录、页眉页脚
- 支持在指定章节位置插入生成的图表
- 支持设置不同竞赛的模板样式

#### 8.4 测试

- `tests/test_docx_builder.py`（新建）：测试基本 DOCX 生成、图表插入、不同模板样式

---

### T09. AGENTS.md 层级化指令系统

> 原C2

**目标**: 不同竞赛、不同项目可有不同行为规则，通过文件层级继承。

#### 9.1 指令文件层级

- `~/.aurora/AGENTS.md` — 全局指令（适用所有项目）
- `<workspace>/AGENTS.md` — 项目级指令（适用当前项目）
- `<workspace>/AGENTS.override.md` — 覆盖指令（最高优先级）

#### 9.2 指令加载器

**文件**: `aurora/instructions/loader.py`（新建）

- `InstructionLoader` 类
- `load_instructions(workspace_path)` 方法：读取三级文件并按优先级合并
- `parse_instructions(content)` 方法：解析指令段（`[system]`、`[competition]`、`[writing-style]`、`[section-rules]`、`[forbidden]`）

#### 9.3 Agent 与 CLI 集成

**文件**: `aurora/agent.py`

- 在 `_build_messages` 中：加载指令文件并注入到 system prompt

**文件**: `aurora/cli.py`

- `chat` 命令添加 `--workspace` 参数
- 启动时显示已加载的指令层级

#### 9.4 默认模板

**文件**: `aurora/instructions/default_agents.md`（新建）

- 默认全局指令：基础写作规范、禁止项、质量标准

#### 9.5 测试

- `tests/test_instructions.py`（新建）：测试加载、层级合并、覆盖机制

---

## P2 — 竞争力提升

---

### T10. 商业计划书大纲编辑器

> 原B1

#### 10.1 编辑器核心

**文件**: `aurora/business_plan/editor.py`（新建）

- `PlanEditor` 类：管理当前 plan 的编辑状态
- `update_section(section_id, new_content)`: 更新章节
- `regenerate_section(section_id, instructions)`: 根据用户指令重新生成（调用 LLM）
- `reorder_sections(new_order)`: 调整章节顺序
- `merge_sections(section_ids)`: 合并章节
- `split_section(section_id, split_points)`: 拆分章节
- `get_diff(original, modified)`: 对比修改差异
- `validate_plan()`: 校验完整性（章节是否有内容、字数是否达标）

#### 10.2 工具注册

**文件**: `aurora/tools/editor_tools.py`（新建）

- 注册 `plan_edit_section` / `plan_regenerate_section` / `plan_validate` / `plan_word_count` 工具

**文件**: `aurora/agent.py`

- 注册 editor_tools，添加 `self.current_plan` 属性

#### 10.3 测试

- `tests/test_editor.py`（新建）：测试所有编辑操作、validate_plan

---

### T11. 答辩模拟与评分系统

> 原B4

#### 11.1 模拟器

**文件**: `aurora/defense/simulator.py`（新建）

- `DefenseSimulator` 类
- `simulate(project_info, competition_id, difficulty)` 方法：
  1. 根据竞赛评分维度生成针对性问题
  2. 按难度分三档：初赛（基础）、复赛（深入）、决赛（压力测试）
  3. 每轮生成 1 个问题，等待回答，评价并追问
- `generate_questions(project_info, count, focus_area)` 方法：批量生成答辩题
- `evaluate_answer(question, answer, project_info)` 方法：评价回答质量
- `generate_defense_script(project_info)` 方法：生成完整答辩逐字稿（含 Q&A 预案）
- `score_defense(questions_answers)` 方法：对整场答辩打分

#### 11.2 Prompt 模板

**文件**: `aurora/defense/prompts.py`（新建）

- 定义不同难度的评委角色 prompt
- 定义评分标准 prompt
- 定义追问策略 prompt

#### 11.3 工具注册

**文件**: `aurora/tools/defense_tools.py`（新建）

- 注册 `defense_simulate` / `defense_questions` / `defense_evaluate` / `defense_script` 工具

**文件**: `aurora/agent.py`

- 注册 defense_tools

#### 11.4 测试

- `tests/test_defense.py`（新建）：测试问题生成、回答评价、整场答辩模拟

---

### T12. 竞品分析模块

> 原B3

#### 12.1 分析器

**文件**: `aurora/competition/competitor_analyzer.py`（新建）

- `CompetitorAnalyzer` 类
- `analyze(project_info, industry)` 方法：web_search 搜索竞品 → LLM 分析优劣势 → 生成对比矩阵 → 差异化定位建议
- `generate_matrix(competitors, dimensions)` 方法：生成对比矩阵数据
- `suggest_positioning(project_info, competitors)` 方法：生成差异化定位策略

#### 12.2 工具注册

**文件**: `aurora/tools/competitor_tools.py`（新建）

- 注册 `competitor_analyze` / `competitor_matrix` 工具

**文件**: `aurora/agent.py`

- 注册 competitor_tools

#### 12.3 测试

- `tests/test_competitor_analyzer.py`（新建）：测试搜索+LLM 分析流程、矩阵生成

---

### T13. VisualDesigner 集成

> 原A2

#### 13.1 Designer 增强

**文件**: `aurora/visuals/designer.py`

- 修改 `__init__` 签名为 `__init__(self, config: Optional[Config] = None)`
- 添加 `generate_chart(project_info, chart_type)` 方法
- 添加离线回退：LLM 不可用时使用预制 HTML 模板
- 添加 `_build_fallback_chart(data, chart_type)` 私有方法：基于 Matplotlib 生成 PNG

#### 13.2 Renderer 增强

**文件**: `aurora/visuals/renderer.py`

- 修改 `__init__` 签名，接受可选 config
- 添加 `render_to_file(html_content, output_path, width, height)` 方法
- 添加 `render_chart_html(project_info, chart_type, output_path)` 一步完成方法
- 添加 Playwright 未安装时的回退逻辑（Matplotlib 直接生成 PNG）

#### 13.3 Generator 集成

**文件**: `aurora/business_plan/generator.py`

- 初始化 `self.visual_designer` 和 `self.renderer`
- 添加 `_generate_section_visuals(project_info, section_id)` 方法
- 修改 `_gen_market_analysis`：生成市场规模柱状图
- 修改 `_gen_financial_analysis`：生成 3 年营收折线图、利润柱状图
- 修改 `export_to_docx`：将图表插入到对应章节

#### 13.4 工具与测试

**文件**: `aurora/tools/visuals_tools.py`（新建）

- 注册 `generate_chart` / `list_chart_types` 工具

**文件**: `aurora/agent.py`

- 在 `_register_all_tools` 中注册 visuals_tools

- `tests/test_visuals.py`（新建）：测试 fallback 模式、基本渲染、与 generator 集成

---

### T14. 沙箱安全机制

> 原C3

#### 14.1 策略定义

**文件**: `aurora/sandbox/policy.py`（新建）

- `SandboxPolicy` 枚举：`READ_ONLY` / `WORKSPACE_WRITE` / `FULL_ACCESS`
- `SandboxConfig` dataclass: policy + allowed_paths + denied_paths

#### 14.2 安全守卫

**文件**: `aurora/sandbox/guard.py`（新建）

- `SandboxGuard` 类：拦截所有文件操作
- `check_read(path)` / `check_write(path)` / `check_execute(path)` 方法
- `validate_path(path, operation)` 方法：综合校验路径安全性
- 拦截：写入系统目录、覆盖已有文件、删除文件、路径遍历攻击

#### 14.3 工具注册集成

**文件**: `aurora/tools/registry.py`

- 修改 `dispatch` 方法：执行 handler 前通过 SandboxGuard 校验
- `register` 方法支持为工具标记安全等级（safe / cautious / dangerous）

#### 14.4 导出安全

**文件**: `aurora/business_plan/generator.py`

- 修改 `export_to_docx` / `export_to_markdown`：通过 SandboxGuard 校验输出路径

#### 14.5 CLI 与配置

**文件**: `aurora/cli.py`

- 添加 `--sandbox` 参数：`aurora chat --sandbox read-only`

**文件**: `aurora/config.py`

- 在 `Config` 中添加 `sandbox: SandboxConfig` 字段

#### 14.6 测试

- `tests/test_sandbox.py`（新建）：测试路径校验、权限拦截、危险操作拒绝

---

### T15. 多图片输入支持

> 原C7

#### 15.1 图片处理器

**文件**: `aurora/image/handler.py`（新建）

- `ImageHandler` 类（需要支持 vision 的模型）
- `analyze_image(image_path, prompt)` 方法：使用 LLM 分析图片内容
- `extract_product_info(image_path)` 方法：从产品截图提取功能特征
- `extract_team_info(image_path)` / `extract_market_data(image_path)` / `describe_competition_poster(image_path)` 方法

#### 15.2 工具与 Agent 集成

**文件**: `aurora/tools/image_tools.py`（新建）

- 注册 `analyze_image` / `extract_from_image` 工具

**文件**: `aurora/agent.py`

- 在 `run()` 中检测 `@image:path` 引用，自动传递图片给 LLM

#### 15.3 CLI 集成

**文件**: `aurora/cli.py`

- 添加 `-i / --image` 参数：`aurora chat -i product.png`
- 支持多图片：`aurora chat -i img1.png,img2.png`

#### 15.4 测试

- `tests/test_image.py`（新建）：测试图片分析、信息提取

---

## P3 — 生态扩展

---

### T16. Web API 服务 (FastAPI)

> 原B5

#### 16.1 应用初始化

**文件**: `aurora/web/app.py`（新建）

- 创建 FastAPI app，配置 CORS、异常处理、日志中间件
- startup/shutdown 事件处理（初始化 AuroraAgent）

#### 16.2 路由

**文件**: `aurora/web/routes/plan.py`（新建）

- `POST /api/plan/generate` / `POST /api/plan/section` / `PUT /api/plan/section/{section_id}` / `GET /api/plan/{session_id}` / `POST /api/plan/export`

**文件**: `aurora/web/routes/competition.py`（新建）

- `GET /api/competitions` / `GET /api/competitions/{id}` / `POST /api/competitions/match` / `POST /api/competitions/analyze`

**文件**: `aurora/web/routes/evaluation.py`（新建）

- `POST /api/evaluation/evaluate` / `POST /api/evaluation/diagnose` / `POST /api/evaluation/suggest`

**文件**: `aurora/web/routes/chat.py`（新建）

- `POST /api/chat`（支持 SSE 流式输出） / `GET /api/chat/history/{session_id}`

**文件**: `aurora/web/routes/defense.py`（新建）

- `POST /api/defense/start` / `POST /api/defense/answer` / `GET /api/defense/result/{session_id}`

#### 16.3 Schema 与依赖注入

**文件**: `aurora/web/schemas.py`（新建）

- Pydantic 模型：GeneratePlanRequest/Response, EvaluateRequest/Response, MatchRequest/Response, ChatRequest/Response

**文件**: `aurora/web/dependencies.py`（新建）

- 依赖注入：获取 AuroraAgent / MemoryManager 实例

#### 16.4 依赖与测试

- `pyproject.toml`: 添加 `fastapi>=0.111.0`, `uvicorn>=0.30.0`，添加 `aurora-web` 入口点
- `tests/test_web_api.py`（新建）：FastAPI TestClient 测试所有端点、异常请求、SSE 流式输出

---

### T17. MCP 协议支持

> 原C1

#### 17.1 MCP 客户端

**文件**: `aurora/mcp/client.py`（新建）

- `MCPClient` 类：管理 MCP 服务器连接
- `connect(server_name)` / `list_tools(server_name)` / `call_tool(server_name, tool_name, args)` / `disconnect` / `disconnect_all` 方法

#### 17.2 MCP 服务端

**文件**: `aurora/mcp/server.py`（新建）

- `MCPServer` 类：将 Aurora 工具注册为 MCP 工具
- `start(port)` / `handle_request(method, params)` 方法
- 暴露工具：`aurora_generate_plan` / `aurora_generate_section` / `aurora_evaluate` / `aurora_match_track` / `aurora_export` / `aurora_defense_simulate`

#### 17.3 配置与工具发现

**文件**: `aurora/mcp/config.py`（新建）

- 定义 MCP 配置 schema（TOML 或 YAML）
- 支持多服务器配置 + 工具审批模式

**文件**: `aurora/tools/mcp_tools.py`（新建）

- 自动发现并注册 MCP 客户端工具到 ToolRegistry

#### 17.4 Agent 与 CLI 集成

**文件**: `aurora/agent.py`

- 初始化 MCPClient、注册 MCP 工具、添加 `start_mcp_server()` 方法

**文件**: `aurora/cli.py`

- 添加 `mcp-server` / `mcp list` / `mcp test <server>` 子命令

#### 17.5 依赖与测试

- `pyproject.toml`: 添加 `mcp>=1.0` 依赖
- `tests/test_mcp.py`（新建）：测试客户端连接、服务端暴露工具、端到端调用

---

### T18. 竞赛资料库扩充

> 原B2

#### 18.1 数据扩充

**文件**: `aurora/competition/database.py`

- 添加以下竞赛数据：
  - 创青春（全国大学生创业大赛）
  - 中国"互联网+"大学生创新创业大赛（已有）
  - 挑战杯（已有）
  - 三创赛（已有）
  - 中国大学生"互联网+"创新大赛
  - "华为杯"中国大学生智能设计竞赛
  - 全国大学生电子设计竞赛
  - 中国国际大学生创新大赛（新版）
  - 大学生创新创业训练计划（大创）
  - "挑战杯"大学生课外学术科技作品竞赛
- 每个竞赛包含：名称、级别、赛道列表、评分维度与权重、报名时间、答辩流程、注意事项
- 为每个赛道添加详细关键词库

#### 18.2 匹配算法升级

**文件**: `aurora/competition/track_matcher.py`

- 升级为 TF-IDF 或简单语义相似度替代纯关键词匹配
- 添加 `match_with_reasons` 方法：返回详细匹配原因分析
- 添加 `suggest_competition(project_info)` 方法：根据项目推荐最适合的竞赛
- 考虑项目阶段对匹配结果的影响

#### 18.3 测试

- `tests/test_competition.py`：为每个新竞赛添加测试用例，测试 `suggest_competition`

---

### T19. 团队与导师信息管理

> 原B7

#### 19.1 数据模型与管理器

**文件**: `aurora/team/models.py`（新建）

- `TeamMember` dataclass：姓名、角色、技能、背景、联系方式
- `Advisor` dataclass：姓名、领域、职称、院校

**文件**: `aurora/team/manager.py`（新建）

- `TeamManager` 类
- `add_member` / `remove_member` 方法
- `suggest_roles(team_members, project_info)` 方法：根据项目建议团队分工
- `evaluate_team_completeness(team_members)` 方法：评估团队是否完整
- `generate_team_section(team_members, project_info)` 方法：生成团队介绍章节
- `suggest_advisor(team_members, project_info)` 方法：建议需要的导师类型

#### 19.2 工具注册与测试

**文件**: `aurora/tools/team_tools.py`（新建）

- 注册 `team_add_member` / `team_suggest_roles` / `team_evaluate` / `team_generate_section` 工具

- `tests/test_team.py`（新建）

---

### T20. SwarmBus 多智能体通信集成

> 原A3

#### 20.1 Bus 增强

**文件**: `aurora/swarm/bus.py`

- 将 `asyncio.get_event_loop().time()` 替换为 `time.time()`（修复弃用警告）
- 添加 `unsubscribe(recipient, queue)` / `clear()` / `get_latest(recipient, count=5)` 方法

#### 20.2 Orchestrator 集成

**文件**: `aurora/swarm/orchestrator.py`

- `_execute_with_role` 开始时：agent 通过 bus 发布 "开始处理" 消息
- `_execute_with_role` 结束时：agent 通过 bus 发布 "处理完成" 消息（含结果摘要）
- agent 可通过 bus 查询其他 agent 的中间结果
- `_synthesize_results`：从 bus 历史提取通信记录，辅助合成

#### 20.3 测试

- `tests/test_swarm_bus.py`（新建）：测试 send/receive、broadcast、subscribe/unsubscribe、get_history

---

### T21. TaskDecomposer LLM 动态分解

> 原A6

#### 21.1 LLM 分解

**文件**: `aurora/swarm/decomposer.py`

- 添加 `__init__(self, config=None)`，初始化可选 LLM 客户端
- 修改 `decompose`：先尝试 LLM 分解，失败回退到硬编码
- LLM prompt：分析用户需求，输出 JSON 格式子任务列表（id, description, target_role, dependencies）
- 添加 `_parse_decomposition(response_text)` / `_fallback_decompose(task)` 方法

#### 21.2 测试

- `tests/test_decomposer.py`（新建）：测试硬编码分解、LLM 分解 mock

---

## P4 — 锦上添花

---

### T22. PDF 导出

> 原B9

**文件**: `aurora/export/pdf_exporter.py`（新建）

- `PDFExporter` 类：Markdown → HTML → PDF（weasyprint 或 fpdf2）
- 支持中文字体、封面、目录、页眉页脚

**文件**: `aurora/tools/export_tools.py`（新建）

- 注册 `export_pdf` 工具

- `pyproject.toml`: 添加可选依赖 `fpdf2>=2.7` 或 `weasyprint>=60`
- `tests/test_pdf_export.py`（新建）

---

### T23. 多语言支持 (中英文)

> 原B10

**文件**: `aurora/i18n/`（新建目录）

- `zh.py`：中文文本模板
- `en.py`：英文文本模板
- `__init__.py`：语言选择逻辑

- 修改所有 section generator：根据 language 参数选择模板语言
- 修改 LLM prompt：根据 language 参数切换中英文
- 修改 CLI：添加 `--lang zh|en` 参数
- `tests/test_i18n.py`（新建）

---

### T24. TUI 终端界面

> 原C6

#### 24.1 TUI 应用

**文件**: `aurora/tui/app.py`（新建）

- `AuroraTUI` 类：基于 textual 或 rich
- 布局：左侧对话面板 | 右上预览面板 | 右下工具状态面板 | 底部输入栏
- 快捷键：`Ctrl+S` 保存 / `Ctrl+E` 导出 / `Ctrl+P` 预览 Markdown / `Ctrl+H` 历史 / `Tab` 切换面板 / `Ctrl+C` 退出

#### 24.2 组件

**文件**: `aurora/tui/widgets/chat.py`（新建）— 聊天消息列表，支持 Markdown 渲染

**文件**: `aurora/tui/widgets/preview.py`（新建）— 计划内容预览，实时更新

**文件**: `aurora/tui/widgets/status.py`（新建）— 工具执行状态

#### 24.3 CLI 与依赖

**文件**: `aurora/cli.py`

- 添加 `--tui` 参数：`aurora chat --tui`

- `pyproject.toml`: 添加可选依赖 `textual>=0.50` 或 `rich>=13.0`
- `tests/test_tui.py`（新建）

---

## 依赖关系图

```
T04 (配置) ──────→ 所有任务（基础依赖）
T01 (SessionDB) ─→ T03 (CLI 需要 session 管理)
T05 (结构化)   ─→ T06 (评估需要结构化数据)
                ─→ T07 (质量审核需要结构化数据)
                ─→ T10 (编辑器需要结构化数据)
T08 (DOCX)     ─→ T13 (图表需插入 DOCX)
T17 (MCP)      ─→ T16 (Web API 可暴露 MCP 服务)
T20 (SwarmBus) ─→ T21 (分解器结果通过 bus 传递)
```

---

## 建议执行顺序

**第一批（P0 全部）**:
1. T04 → T01 → T02 → T03

**第二批（P1 按依赖）**:
2. T05 → T06 → T07 → T08 → T09

**第三批（P2 可并行）**:
3. T10 / T11 / T12 / T13 / T14 / T15（互相独立，可并行开发）

**第四批（P3 按依赖）**:
4. T18 / T19 / T20 / T21 → T16 → T17

**第五批（P4）**:
5. T22 / T23 / T24
