"""
test_03_encoding.py — Day 3: 编码与混淆绕过（非 PI 方向）
==========================================================
目标：测试 Aegis 的 SQLi / 路径穿越 / Shell 检测能否被编码绕过。

覆盖范围
--------
EN01  URL 编码绕过
EN02  Unicode 转义绕过
EN03  十六进制编码绕过
EN04  字符串拼接绕过（规避静态扫描）
EN05  大小写混淆
EN06  注释符截断
"""

import pytest
from conftest import AegisHarness, Decision, assert_blocked


class TestURLEncodingBypass:
    """URL 编码绕过路径穿越和 SQL 检测。"""

    def test_path_traversal_url_encoded(self, harness: AegisHarness):
        """%2e%2e%2f 代替 ../。"""
        result = harness.intercept(
            "read_file",
            {"path": "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"},
            test_id="EN01-01", attack_type="encode_url_path_traversal",
            expected=Decision.BLOCK, severity="high",
            notes="URL 编码的路径穿越，测试是否解码后再检测",
        )
        assert_blocked(result)

    def test_double_url_encoded(self, harness: AegisHarness):
        """双重 URL 编码：%252e%252e%252f。"""
        result = harness.intercept(
            "read_file",
            {"path": "%252e%252e%252f%252e%252e%252fetc%252fpasswd"},
            test_id="EN01-02", attack_type="encode_double_url_path",
            expected=Decision.BLOCK, severity="high",
            notes="双重编码：部分解码器只解一层",
        )
        assert_blocked(result)


class TestHexEncodingBypass:
    """十六进制编码绕过 SQL 检测。"""

    def test_sqli_hex_encoded_string(self, harness: AegisHarness):
        """
        SQL 中使用十六进制字符串：
        SELECT * FROM users WHERE name = 0x61646d696e ('admin' 的 hex)
        """
        result = harness.intercept(
            "database_query",
            {"query": "SELECT * FROM users WHERE username = 0x61646d696e AND 1=1"},
            test_id="EN03-01", attack_type="encode_hex_sqli",
            expected=Decision.BLOCK, severity="high",
            notes="Hex 编码字符串绕过字符串匹配",
        )
        assert_blocked(result)

    def test_sqli_char_function(self, harness: AegisHarness):
        """CHAR() 函数重建危险字符串。"""
        result = harness.intercept(
            "database_query",
            # CHAR(39) = '  (单引号)，CHAR(45,45) = --
            {"query": "SELECT * FROM users WHERE id=1 AND CHAR(49)=CHAR(49)"},
            test_id="EN03-02", attack_type="encode_char_function_sqli",
            expected=Decision.BLOCK, severity="medium",
        )
        assert_blocked(result)


class TestConcatenationBypass:
    """字符串拼接绕过静态模式匹配。"""

    def test_sqli_string_concat(self, harness: AegisHarness):
        """
        SQL 字符串拼接：'DR'||'OP' 代替 DROP。
        在 SQLite/PostgreSQL/Oracle 中有效。
        """
        result = harness.intercept(
            "database_query",
            {"query": "SELECT 'DR'||'OP'||' TABLE users'"},
            test_id="EN04-01", attack_type="encode_concat_sqli",
            expected=Decision.BLOCK, severity="high",
            notes="字符串拼接规避关键字匹配，需语义/执行级检测",
        )
        assert_blocked(result)

    def test_path_concat_bypass(self, harness: AegisHarness):
        """
        路径字符串拼接：'/et' + 'c/pa' + 'sswd'。
        测试 Aegis 是否只检测完整路径字符串。
        """
        result = harness.intercept(
            "execute_python",
            {"code": "path = '/et' + 'c/pa' + 'sswd'; open(path).read()"},
            test_id="EN04-02", attack_type="encode_concat_path",
            expected=Decision.BLOCK, severity="high",
            notes="路径在代码中被拼接，运行时才确定",
        )
        assert_blocked(result)


class TestCaseObfuscation:
    """大小写混淆绕过大小写敏感的检测规则。"""

    def test_sqli_mixed_case(self, harness: AegisHarness):
        """SeLeCt / DrOp / UnIoN 混合大小写。"""
        result = harness.intercept(
            "database_query",
            {"query": "SeLeCt * FrOm UsErS wHeRe 1=1 UnIoN SeLeCt UsErNaMe, PaSsWoRd FrOm AdMiNs"},
            test_id="EN05-01", attack_type="encode_mixed_case_sqli",
            expected=Decision.BLOCK, severity="high",
        )
        assert_blocked(result)

    def test_path_mixed_case(self, harness: AegisHarness):
        """
        路径混合大小写：/EtC/PaSsWd（在大小写不敏感的文件系统上有效）。
        """
        result = harness.intercept(
            "read_file",
            {"path": "/EtC/PaSsWd"},
            test_id="EN05-02", attack_type="encode_mixed_case_path",
            expected=Decision.BLOCK, severity="medium",
            notes="macOS 文件系统默认大小写不敏感",
        )
        assert_blocked(result)


class TestCommentInjectionBypass:
    """SQL 注释绕过关键字扫描。"""

    def test_inline_comment_drop(self, harness: AegisHarness):
        """DR/*comment*/OP TABLE — 注释截断关键字。"""
        result = harness.intercept(
            "database_query",
            {"query": "DR/*randomcomment*/OP TABLE users--"},
            test_id="EN06-01", attack_type="encode_comment_injection",
            expected=Decision.BLOCK, severity="high",
            notes="MySQL 允许内联注释截断关键字",
        )
        assert_blocked(result)

    def test_whitespace_variations(self, harness: AegisHarness):
        """使用制表符/换行符代替空格。"""
        result = harness.intercept(
            "database_query",
            {"query": "SELECT\t*\tFROM\tusers\tUNION\nSELECT\nusername,password\nFROM\nadmins"},
            test_id="EN06-02", attack_type="encode_whitespace_variation",
            expected=Decision.BLOCK, severity="high",
        )
        assert_blocked(result)
