#!/usr/bin/env bash
# Aegis 评估环境一键安装脚本
set -e

echo "=== Aegis Evaluation Setup ==="

# 1. 安装测试依赖
pip install -r "$(dirname "$0")/requirements.txt"

# 2. 尝试安装 Aegis（首先检查是否已安装）
if ! python -c "import aegis" 2>/dev/null; then
    echo "[!] aegis 未安装，请手动执行以下命令之一："
    echo "    pip install aegis-ai"
    echo "    pip install -e /path/to/aegis/source"
    echo "    pip install git+https://github.com/<org>/aegis.git"
else
    echo "[✓] aegis 已安装"
    python -c "import aegis; print('    版本：', getattr(aegis, '__version__', 'unknown'))"
fi

echo "=== Setup done. Run: python -m pytest tests/test_00_setup.py -v ==="
