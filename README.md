# Aegis Security Evaluation

This repository evaluates Aegis as a pre-execution firewall for AI agent tool calls under adversarial prompting and realistic workflow scenarios.

## Suggested GitHub About

Description:

Evaluate Aegis as a pre-execution firewall for AI agent tool calls under adversarial prompting and realistic workflows.

Suggested topics:

- agent-security
- runtime-guardrails
- prompt-injection
- red-teaming
- ai-security
- tool-call-security

## What This Repository Contains

- A reproducible pytest harness for the real Aegis Docker gateway
- A comparison baseline using DeepSeek-Chat through the same harness
- A full attack matrix covering prompt injection, exfiltration, file and network misuse, encoding tricks, and multi-step attacks
- Slides and speaking notes for research presentation

## Start Here

- Executive summary: EXECUTIVE_SUMMARY.md
- Technical summary: findings/summary.md
- Full findings log: findings/findings_log.md
- Full test matrix: findings/test_matrix.md
- Slide deck: slides/aegis_evaluation.md

## Result Tracks

Two different result tracks appear in this repository.

| Track | System | Total Tests | Blocked | Bypass | False Positive | Notes |
|------|--------|-------------|---------|--------|----------------|-------|
| A | Real Aegis gateway, rule-based | 84 | 65 | 18 | 1 | Main artifact used in week plan and slides |
| B | DeepSeek-Chat baseline | 80 | 73 | 5 | 0 | Comparison baseline recorded in findings log |

These counts should not be mixed. The totals differ because the DeepSeek baseline excluded a small number of environment-dependent cases and one fixture-dependent file/network case.

## Repository Layout

```
Aegis🤖/
├── README.md
├── EXECUTIVE_SUMMARY.md
├── week_plan.md
├── setup/
│   ├── install.sh
│   └── requirements.txt
├── tests/
│   ├── conftest.py
│   ├── test_00_setup.py
│   ├── test_01_baseline.py
│   ├── test_02_prompt_injection.py
│   ├── test_03_encoding.py
│   ├── test_04_file_network.py
│   ├── test_05_exfiltration.py
│   ├── test_06_multistep.py
│   └── test_07_workflow.py
├── attack_payloads/
├── findings/
│   ├── summary.md
│   ├── findings_log.md
│   ├── test_matrix.md
│   └── screenshots/
│       └── README.md
└── slides/
    ├── aegis_evaluation.md
    └── presentation_script.md
```

## Reproducibility

### Environment

- Python 3.13.x
- pytest 9.x
- A running Aegis gateway at localhost:8080 for the primary track
- Optional DeepSeek API key for the comparison baseline

### Upstream Version Pinning

For strict reproducibility, record the exact upstream Aegis version used for the primary track before presenting or sharing this artifact.

- Upstream repository: github.com/Justin0504/Aegis
- Evaluated commit hash: REPLACE_WITH_EXACT_COMMIT
- Evaluated Docker image tag: REPLACE_WITH_IMAGE_TAG
- Local gateway URL during evaluation: http://localhost:8080

If these values are not pinned, later reruns may exercise different rules or behaviors than the results reported here.

### Primary Track: Real Aegis Gateway

1. Start the upstream Aegis Docker gateway so that localhost:8080 is reachable.
2. Confirm the gateway health endpoint returns status ok.
3. Install this repository's Python dependencies.
4. Run the setup test, then run the category tests.

Typical local workflow:

```bash
./setup/install.sh
python -m pytest tests/test_00_setup.py -v
python -m pytest tests/test_01_baseline.py -v
python -m pytest tests/test_02_prompt_injection.py -v
python -m pytest tests/test_03_encoding.py -v
python -m pytest tests/test_04_file_network.py -v
python -m pytest tests/test_05_exfiltration.py -v
python -m pytest tests/test_06_multistep.py -v
python -m pytest tests/test_07_workflow.py -v
```

Optional full run:

```bash
python -m pytest tests/ -v --tb=short
python -m pytest tests/ --html=findings/report.html --self-contained-html
```

### Secondary Track: DeepSeek Baseline

If the real gateway is unavailable, the harness can fall back to a DeepSeek classifier.

Required environment variables:

```bash
export DEEPSEEK_API_KEY="<your-key>"
export DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
export DEEPSEEK_MODEL="deepseek-chat"
```

The harness connection order is:

1. Real Aegis gateway
2. DeepSeek-Chat baseline
3. Local keyword stub

## Output Conventions

Test outcomes are recorded with the following markers in findings/test_matrix.md.

| Marker | Meaning |
|--------|---------|
| ✅ BLOCKED | Aegis blocked the action |
| ❌ BYPASS | The attack bypassed the defense |
| ⚠️ PARTIAL | Partial detection or incomplete mitigation |
| 🚫 FALSE_POS | Benign action was blocked |
| ❓ UNCLEAR | Outcome needs manual review |
| ⏭️ SKIPPED | Not executed in the current run |

## Evidence And Deliverables

- findings/findings_log.md stores the detailed technical findings and comparison notes.
- findings/test_matrix.md stores the final case-by-case matrix for the real gateway track.
- findings/screenshots/README.md documents the expected screenshot evidence to accompany the written report.
- slides/aegis_evaluation.md and slides/presentation_script.md package the work for presentation.

## Key Caveat

This repository reports both a fast rule-based gateway result and an LLM baseline result. Any summary should label clearly which track it refers to.
