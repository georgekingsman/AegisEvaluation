# Aegis Security Evaluation — Pre-RA Trial Project

> **研究问题**：Aegis 能否在对抗性 prompting 和真实 agentic workflow 场景下，稳健地执行 agent 工具调用的运行时安全策略？

---

## 项目结构

```
Aegis🤖/
├── README.md                   ← 本文件：setup 指南与项目概览
├── week_plan.md                ← 7 天执行计划
├── setup/
│   ├── install.sh              ← 一键安装脚本
│   └── requirements.txt        ← Python 测试依赖
├── tests/
│   ├── conftest.py             ← pytest fixtures（Aegis 测试 harness）
│   ├── test_00_setup.py        ← Day1: 验证 Aegis 正常运行
│   ├── test_01_baseline.py     ← Day2: 复现 advertised 防护
│   ├── test_02_prompt_injection.py  ← Day3: Prompt injection 绕过
│   ├── test_03_encoding.py     ← Day3: 编码/混淆绕过
│   ├── test_04_file_network.py ← Day4: 文件/网络访问绕过
│   ├── test_05_exfiltration.py ← Day4: 数据外传绕过
│   ├── test_06_multistep.py    ← Day4: 多步组合攻击链
│   └── test_07_workflow.py     ← Day5: 真实 workflow 兼容性
├── attack_payloads/
│   ├── sql_injection.txt       ← SQL 注入变体载荷
│   ├── path_traversal.txt      ← 路径穿越变体
│   ├── prompt_injection.txt    ← Prompt injection 变体
│   └── exfiltration.txt        ← 数据外传场景
├── findings/
│   ├── test_matrix.md          ← 主测试矩阵（实时记录结果）
│   ├── findings_log.md         ← 详细发现日志
│   └── summary.md              ← 最终汇报摘要
└── slides/
    └── aegis_evaluation.md     ← Marp 格式 slide deck
```

---

## 快速安装

```bash
# 1. 安装 Aegis（根据实际 repo 替换 URL）
pip install aegis-ai
# 或从源码安装
# git clone https://github.com/<org>/aegis && cd aegis && pip install -e .

# 2. 安装测试依赖
pip install -r setup/requirements.txt

# 3. 验证安装
python -m pytest tests/test_00_setup.py -v
```

---

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v --tb=short

# 分阶段运行
python -m pytest tests/test_01_baseline.py -v          # 基础防护
python -m pytest tests/test_02_prompt_injection.py -v  # PI 绕过
python -m pytest tests/test_03_encoding.py -v          # 编码绕过
python -m pytest tests/test_04_file_network.py -v      # 文件/网络绕过
python -m pytest tests/test_05_exfiltration.py -v      # 外传绕过
python -m pytest tests/test_06_multistep.py -v         # 多步攻击
python -m pytest tests/test_07_workflow.py -v          # 兼容性

# 生成 HTML 报告
python -m pytest tests/ --html=findings/report.html --self-contained-html
```

---

## 结果记录约定

每次测试完成后，在 `findings/test_matrix.md` 中用以下状态标记结果：

| 符号 | 含义 |
|------|------|
| ✅ BLOCKED | Aegis 成功拦截 |
| ❌ BYPASS | 成功绕过防护 |
| ⚠️ PARTIAL | 部分检测，存在漏洞 |
| 🚫 FALSE_POS | 误报（正常操作被拦截）|
| ❓ UNCLEAR | 结果不确定，需进一步分析 |

---

## 测试资产说明

- `conftest.py` 中的 `AegisHarness` 类封装了与 Aegis API 的所有交互。若 Aegis API 有变动，只需修改这一个文件。
- `attack_payloads/` 中的载荷文件可独立扩展，测试脚本会自动加载。
- 所有测试都会将原始结果写入 `findings/findings_log.md`。
