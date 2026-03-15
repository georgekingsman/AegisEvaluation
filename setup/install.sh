#!/usr/bin/env bash
# Aegis 评估环境一键安装脚本
set -e

echo "=== Aegis Evaluation Setup ==="

# 1. 安装测试依赖
pip install -r "$(dirname "$0")/requirements.txt"

# 2. 提示真实网关前置条件
gateway_url="${AEGIS_GATEWAY_URL:-http://localhost:8080}"
echo "[i] Primary evaluation target: ${gateway_url}"
echo "[i] This repository expects a running Aegis Docker gateway for the main 84-test track."

# 3. 网关健康检查
python - <<'PY'
import os
import sys
import urllib.request

gateway = os.environ.get("AEGIS_GATEWAY_URL", "http://localhost:8080")
health_url = f"{gateway}/health"

try:
    with urllib.request.urlopen(health_url, timeout=3) as response:
        body = response.read().decode("utf-8", errors="replace")
    print(f"[✓] Gateway reachable: {health_url}")
    print(f"    Response: {body}")
except Exception as exc:
    print(f"[!] Gateway not reachable: {health_url}")
    print(f"    Reason: {exc}")
    print("    Start the upstream Aegis Docker gateway before running the main evaluation track.")
PY

# 4. DeepSeek 基线提示
if [[ -n "${DEEPSEEK_API_KEY:-}" ]]; then
    echo "[i] DeepSeek baseline variables detected. Harness can fall back to deepseek-chat if gateway is unavailable."
else
    echo "[i] DeepSeek baseline disabled. Set DEEPSEEK_API_KEY only if you want the comparison track."
fi

echo "=== Setup done. Recommended next step: python -m pytest tests/test_00_setup.py -v ==="
