"""
test_00_setup.py — Day 1: 验证 Aegis 正常运行
==============================================
目标：确认安装成功、harness 可用、基础接口可调用。
"""

import sys
import importlib
import importlib.util
import pytest  # pip install pytest
from conftest import AegisHarness, Decision


class TestEnvironment:
    """验证测试环境是否就绪。"""

    def test_python_version(self):
        """Python >= 3.10。"""
        assert sys.version_info >= (3, 10), f"Python 版本过低: {sys.version}"

    def test_harness_instantiates(self):
        """AegisHarness 能正常实例化。"""
        h = AegisHarness()
        assert h is not None

    def test_aegis_importable(self):
        """
        验证 aegis 包可导入。
        未安装时跳过（不失败），避免阻塞后续测试。
        """
        if importlib.util.find_spec("aegis") is None:
            pytest.skip("aegis 未安装 — stub 模式运行，安装后取消此 skip")
        aegis = importlib.import_module("aegis")
        print(f"\n[✓] aegis 版本: {getattr(aegis, '__version__', 'unknown')}")

    def test_stub_blocks_obvious_sqli(self, harness):
        """即使在 stub 模式下，明显的 SQL 注入也应被拦截。"""
        result = harness.intercept(
            "database_query",
            {"query": "SELECT * FROM users WHERE id=1; DROP TABLE users--"},
            test_id="T00-01",
            attack_type="sql_injection_direct",
            expected=Decision.BLOCK,
            severity="critical",
        )
        assert result.decision == Decision.BLOCK

    def test_stub_allows_benign_query(self, harness):
        """正常查询不应被拦截（验证无误报）。"""
        result = harness.intercept(
            "database_query",
            {"query": "SELECT name, email FROM users WHERE id = ?", "params": [42]},
            test_id="T00-02",
            attack_type="benign_parameterized_query",
            expected=Decision.ALLOW,
            severity="low",
        )
        assert result.decision == Decision.ALLOW


class TestAegisInterface:
    """验证 Aegis 核心接口是否符合预期（安装后执行）。"""

    @pytest.mark.skipif(
        not importlib.util.find_spec("aegis"),
        reason="aegis 未安装"
    )
    def test_aegis_has_firewall_class(self):
        """Aegis 应暴露 Firewall 或等价类。"""
        import importlib as _il
        aegis = _il.import_module("aegis")
        firewall_cls = (
            getattr(aegis, "Firewall", None)
            or getattr(aegis, "AgentFirewall", None)
            or getattr(aegis, "Shield", None)
        )
        assert firewall_cls is not None, (
            "找不到 Firewall/AgentFirewall/Shield 类。"
            f"\naegis 暴露的属性: {[x for x in dir(aegis) if not x.startswith('_')]}"
        )

    @pytest.mark.skipif(
        not importlib.util.find_spec("aegis"),
        reason="aegis 未安装"
    )
    def test_aegis_dashboard_accessible(self):
        """
        Aegis dashboard/cockpit 应可访问（若有 web UI）。
        根据实际实现调整：可能是 HTTP 端点或本地 CLI。
        """
        # TODO: 安装后根据 Aegis 实际提供的 dashboard 接口调整
        pytest.skip("TODO: 安装 Aegis 后补充 dashboard 访问验证")
