# Executive Summary

## Research Question

Can Aegis, a pre-execution firewall for AI agent tool calls, reliably enforce runtime security policies under adversarial prompting and realistic agent workflows?

## Evaluation Setup

- Target system: real Aegis Docker gateway on localhost:8080
- Primary track: rule-based Aegis gateway exercised through pytest
- Baseline track: DeepSeek-Chat LLM classifier using the same harness where applicable
- Agentic validation: DeepSeek function-calling agent as the direct Aegis integration path (8 scenarios) + OpenClaw CLI (v2026.3.2) as real agent-framework validation
- Test harness: Python 3.13.5, pytest 9.0.2, requests with trust_env=False
- Evaluation window: 2026-03-14 to 2026-03-16

## Two Result Tracks

| Track | System | Total Tests | Blocked | Bypass | False Positive | Avg Latency |
|------|--------|-------------|---------|--------|----------------|-------------|
| A | Real Aegis rule engine | 84 | 65 | 18 | 1 | ~5ms |
| B | DeepSeek-Chat baseline | 80 | 73 | 5 | 0 | ~2774ms |

The totals differ because the DeepSeek baseline excluded a small number of environment-dependent cases and one fixture-dependent file/network case.

## Three Main Findings

1. Prompt injection is the largest weakness in the real rule-based gateway.
   Rule-based Aegis bypassed 7 of 13 prompt injection tests because matching is tied to exact phrases and limited field names.

2. Tool-name-driven policy routing creates systematic blind spots.
   Dangerous arguments can be allowed when wrapped in benign-sounding tool names such as maintenance_helper or database_query.

3. Fast rules and strong semantics trade off sharply.
   The real gateway is roughly 300 times faster than the LLM baseline, but it also shows materially more bypasses on semantic attacks and disguised exfiltration.

## Why This Matters

The current Aegis design is effective for many explicit, single-call attacks, but it is not yet a strong boundary against paraphrased prompt injection, encoded content, and multi-step abuse patterns. That makes it a good candidate for hybrid defenses rather than a complete runtime security solution by itself.

## Recommended Next Steps

1. Add a lightweight semantic layer for prompt injection and disguised exfiltration.
2. Add cross-call state or taint tracking for read-then-exfil attack chains.
3. Separate tool-name classification from argument-level risk scoring.

## Where To Look Next

- Technical summary: findings/summary.md
- Full findings log: findings/findings_log.md
- Full matrix: findings/test_matrix.md
- Agentic agent test: tests/test_agentic_deepseek.py
- Slides: slides/aegis_evaluation.md

## Agentic Tool Validation

Aegis was also validated with real agentic tools per instructor requirement:

- **DeepSeek function-calling agent**: 8 scenarios through Aegis. Benign tasks allowed; base64-encoded attacks blocked (HIGH); SSRF blocked (MEDIUM); explicit attacks self-refused by the LLM.
- **OpenClaw CLI v2026.3.2**: Benign tasks completed normally; SSRF blocked by OpenClaw's native URL filter even under social engineering attempts. In this setup, OpenClaw served as real framework validation rather than direct Aegis interception because `--local` did not route tool calls to external MCP servers.
- **Key finding**: Defense-in-depth operates across three layers (LLM self-refusal, Aegis rules, framework native security). Aegis provides unique centralized audit and human-in-the-loop capabilities.
