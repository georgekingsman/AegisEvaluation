# Technical Summary

## Scope

This repository evaluates Aegis as a pre-execution firewall for AI agent tool calls. The study focuses on adversarial prompting, encoded payloads, file and network misuse, data exfiltration, multi-step attack chains, and workflow compatibility.

## Result Accounting

Two result sets appear in this repository and they should not be mixed.

| Track | System Under Test | Total | Blocked | Bypass | False Positive | Notes |
|------|-------------------|-------|---------|--------|----------------|-------|
| A | Real Aegis gateway, rule-based | 84 | 65 | 18 | 1 | Main evaluation reported in week plan and slides |
| B | DeepSeek-Chat LLM baseline | 80 | 73 | 5 | 0 | Comparison baseline reported in findings log |

The counts differ because the comparison baseline did not include every environment-dependent case from the real gateway track, and one file/network case remained fixture-dependent.

## Real Aegis Track

The main evaluation targets the real Docker gateway running on localhost:8080. This is the artifact used for the 84-test headline numbers.

| Category | Total | Blocked | Bypass | False Positive |
|---------|-------|---------|--------|----------------|
| Baseline | 16 | 15 | 1 | 0 |
| Prompt Injection | 13 | 6 | 7 | 0 |
| Encoding | 10 | 9 | 1 | 0 |
| File and Network | 14 | 10 | 4 | 0 |
| Exfiltration | 7 | 3 | 4 | 0 |
| Multi-step | 7 | 5 | 2 | 0 |
| Workflow | 14 | 13 | 0 | 1 |
| Total | 84 | 65 | 18 | 1 |

## DeepSeek Baseline Track

The secondary track uses the same harness with a DeepSeek-Chat classifier as a comparison baseline.

| Category | Total | Blocked | Bypass | False Positive |
|---------|-------|---------|--------|----------------|
| Baseline | 16 | 15 | 1 | 0 |
| Prompt Injection | 13 | 13 | 0 | 0 |
| Encoding | 10 | 10 | 0 | 0 |
| File and Network | 13 | 11 | 2 | 0 |
| Exfiltration | 7 | 6 | 1 | 0 |
| Multi-step | 7 | 6 | 1 | 0 |
| Workflow | 14 | 12 | 0 | 0 |
| Total | 80 | 73 | 5 | 0 |

## Key Findings

1. Rule-based Aegis is fast and deterministic, but semantic prompt injection is its clearest weakness.
2. Tool aliasing and category confusion expose a policy-routing weakness: benign tool names can suppress scrutiny of dangerous arguments.
3. Stateless per-call evaluation misses cumulative or multi-step behaviors such as chunked exfiltration and read-then-exfil chains.
4. The DeepSeek baseline closes many semantic gaps, but the latency cost is substantial.

## Reproducibility Notes

- The main artifact assumes a running Aegis gateway at localhost:8080.
- tests/conftest.py automatically prefers the real gateway, then DeepSeek, then a local stub.
- The quickest validation path is tests/test_00_setup.py followed by tests/test_01_baseline.py.

## Supporting Artifacts

- Slides: slides/aegis_evaluation.md
- Script: slides/presentation_script.md
- Findings log: findings/findings_log.md
- Matrix: findings/test_matrix.md
