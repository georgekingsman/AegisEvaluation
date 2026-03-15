# Aegis Evaluation — 7 天执行计划

> 每天结束后在对应区域打勾，并把关键 findings 写入 `findings/findings_log.md`。
>
> 口径说明：本计划中的最终 headline 数字 `84 / 65 / 18 / 1` 指的是 **Track A: real Aegis rule-based gateway**。
> `findings/findings_log.md` 目前主要承载 **Track B: DeepSeek comparison baseline** 的详细分析；Track A 的权威汇总以 `findings/test_matrix.md`、`findings/summary.md` 和 `EXECUTIVE_SUMMARY.md` 为准。

---

## Day 1（周一）— 环境搭建 + Stub 跑通

**目标：** Aegis 跑起来，至少能看到 dashboard；所有 test_00 测试通过。

### 任务清单

- [x] clone / install Aegis（根据老师给的 repo 安装）
  ```bash
  pip install aegis-ai   # 或 pip install -e /path/to/aegis
  ```
- [x] 把 `tests/conftest.py` 中的 stub 替换为真实 API
  - 打开 `tests/conftest.py` → 找 `_call_aegis_real()` → 看 Aegis 文档补充
- [x] 运行 setup 测试
  ```bash
  python -m pytest tests/test_00_setup.py -v
  ```
- [x] 截图 Aegis dashboard（管理界面 / 审计日志页）
- [ ] 准备 OpenClaw 本地环境（如需要集成测试）

### 预期产出

- Aegis 版本号确认
- `test_00` 全部通过
- 1–2 张 dashboard 截图存入 `findings/screenshots/`

---

## Day 2（周二）— 基础防护复现

**目标：** 验证 README 中声称的 5 类防护是否真实有效。

### 任务清单

- [x] 运行基础测试
  ```bash
  python -m pytest tests/test_01_baseline.py -v --tb=short
  ```
- [x] 手动触发每种拦截，在 dashboard 上截图确认
- [x] 把每个测试结果填入 `findings/test_matrix.md`（替换 ❓）
- [x] 记录误报：正常操作中有哪些被误拦截

### 重点关注

- `assert_allowed` 的测试是否有失败 → 这是误报
- 每个 BLOCK 在 dashboard 上的分类是否正确
- Aegis 返回的 `reason` 字段含义

### 预期产出

- 知道 5 类防护哪些是真实 working，哪些有问题
- test_01 截图 3–5 张（每类拦截各一张）

---

## Day 3（周三）— Prompt Injection & 编码绕过

**目标：** 找第一批 bypass，聚焦 paraphrase、间接注入、编码混淆。

### 任务清单

- [x] 运行 PI 测试
  ```bash
  python -m pytest tests/test_02_prompt_injection.py -v
  python -m pytest tests/test_03_encoding.py -v
  ```
- [x] 对每个 BYPASS（`assert_blocked` 失败）：
  - 在 `findings/findings_log.md` 的"Key Bypasses"区域记录
  - 写出最小可复现步骤（3–5 行代码/payload）
  - 分析根本原因（关键字匹配 vs 语义理解）
- [x] 手动测试 `attack_payloads/prompt_injection.txt` 中的变体
- [x] 截图：Aegis ALLOWED 一个 paraphrase（证明 bypass）；BLOCKED 一个直接 PI

### 重点关注

- `PI03` 间接注入 — 这是最有研究价值的发现点
- `PI06` 多轮注入 — 检查 Aegis 是否有 session memory

### 预期产出

- 至少 1 个可复现的 PI bypass
- 间接注入是否成功/失败的结论

---

## Day 4（周四）— 文件/网络/外传/多步攻击

**目标：** 测试最重要的绕过方向：分块外传、工具别名、多步攻击链。

### 任务清单

- [x] 运行文件/网络测试
  ```bash
  python -m pytest tests/test_04_file_network.py -v
  ```
- [x] 运行外传测试（重点看 EX01-02 分块外传）
  ```bash
  python -m pytest tests/test_05_exfiltration.py -v
  ```
- [x] 运行多步攻击测试
  ```bash
  python -m pytest tests/test_06_multistep.py -v
  ```
- [x] EX01-02（分块外传）结果是核心发现 → 无论成功/失败都要详细记录
- [x] MS01-01（read .env → POST 外传的两步链）→ 验证是否有 taint tracking

### 重点关注

- **分块外传**：Aegis 是否有 session-level 累计量追踪？
- **工具别名(FN02)**：tool_name 无害但 args 危险，会被检测吗？
- **SSRF(FN03-04)**：AWS metadata endpoint 是否明确被阻断？

### 预期产出

- 分块外传实验结论（有/无 bypass）
- 多步链攻击实验结论
- 3–5 张截图

---

## Day 5（周五）— OpenClaw 集成 + 误报测试

**目标：** 把 Aegis 放到真实 OpenClaw agent workflow 上，看兼容性和误报。

### 任务清单

- [x] 运行 workflow 兼容性测试
  ```bash
  python -m pytest tests/test_07_workflow.py -v
  ```
- [x] 记录 `WF04-01` 性能测试结果（avg/max latency）
- [ ] 在真实 OpenClaw 上跑一个完整任务（例：让 agent 写一段代码并运行）
  - 观察 Aegis 是否干扰正常操作
  - 记录哪些步骤被 PENDING 需要 HITL 审核
- [x] 统计 `WF-FP` 系列的误报率

### 预期产出

- False Positive Rate（%）
- 平均拦截时延（ms）
- OpenClaw 集成体验记录（顺不顺、配置难度）

---

## Day 6（周六）— 整理 Findings

**目标：** 把所有测试结果归纳成有结论的发现。

### 任务清单

- [x] 更新 `findings/test_matrix.md` — 全部填完（替换所有 ❓）
- [x] 在 `findings/findings_log.md` 写出：
  - Works well（已验证防护）
  - Bypassed（对比基线的已验证绕过及 PoC）
  - Design limitations（架构层面的约束）
- [x] 统计最终数字：
  - Track A 测试总数：84
  - Track A：BLOCKED 65，BYPASS 18，FALSE_POS 1
  - False Positive Rate：1.2%
- [x] 选出 3 个最有研究价值的发现，准备在 slides 中重点讲

---

## Day 7（周日）— 做 Slides + Rehearsal

**目标：** 完成可展示的 deck，录一遍能讲清楚的 demo。

### 任务清单

- [x] 打开 `slides/aegis_evaluation.md`，填入真实结果：
  - Slide 5 → 65/84 BLOCKED (77.4%)，18 bypasses
  - Slide 6 → PI 语义绕过 / 工具别名混淆 / 合法域名滥用
  - Slide 10 → Policy JSON 分析（prompt-injection 只查 query/prompt 字段）
  - Slide 11 → 已填具体限制与建议
- [ ] 安装 Marp 并生成 PDF/PPTX
  ```bash
  npx @marp-team/marp-cli slides/aegis_evaluation.md --pdf
  # 或
  npx @marp-team/marp-cli slides/aegis_evaluation.md --pptx
  ```
- [ ] 录制一个 2–3 分钟的 screen recording demo（optional but 加分）
  - 展示：一次攻击被 BLOCKED + dashboard 确认
  - 展示：一次 bypass + 说明为什么
- [ ] 准备 3 分钟的口头汇报脚本

### Meeting 讲述框架（5–7 分钟）

```
1. [30s] 我测了什么：Aegis 在对抗性场景下的防护效果
2. [60s] 它能防什么：复现了 5 类 advertised 防护（截图）
3. [90s] 它防不住什么：3 个关键 bypass（特别是间接注入 / 分块外传）
4. [60s] 为什么难防：taint tracking 缺失、per-call 设计的局限
5. [60s] 下一步研究方向：我最想往哪里深挖（benchmark / taint tracking）
```

---

## 关键里程碑检查点

| 时间 | 里程碑 |
|------|--------|
| Day 1 结束 | Aegis 跑通，test_00 全部通过 |
| Day 2 结束 | 知道 5 类 advertised 防护哪些真实有效 |
| Day 3 结束 | 至少 1 个可复现的 bypass |
| Day 4 结束 | 分块外传实验结论确定 |
| Day 5 结束 | False Positive Rate 测量完毕 |
| Day 6 结束 | test_matrix.md 全部填完 |
| Day 7 结束 | Slides PDF 完成，ready for meeting |
