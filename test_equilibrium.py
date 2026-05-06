"""
均衡求解器测试用例

所有期望输出都是基于讲解里"标准参数"手算得出。
你不需要改这个文件，只需要让它的所有用例通过。

跑测试:
    python -m pytest test_equilibrium.py -v

或者跑单个用例:
    python -m pytest test_equilibrium.py::test_check_scc_standard -v
"""

import pytest
from equilibrium import (
    GameParams,
    mu_star, mrs_S, mrs_C,
    check_scc,
    solve_separating, solve_pooling, solve_semi_separating,
    solve_all,
    approx_eq,
)


# ============================================================
# 标准参数 — 讲解里反复用的那组
# ============================================================

@pytest.fixture
def standard():
    return GameParams(
        p0=0.4,
        b_S=4, b_C=2,
        c_S=0.5, c_C=1,
        v_S=3, v_C=-2,
    )


# ============================================================
# 辅助函数测试（已实现，应该立刻通过）
# ============================================================

def test_mu_star_standard(standard):
    """μ* = -v_C / (v_S - v_C) = 2 / 5 = 0.4"""
    assert approx_eq(mu_star(standard), 0.4)


def test_mrs_S_standard(standard):
    """MRS_S = b_S / c_S = 4 / 0.5 = 8"""
    assert approx_eq(mrs_S(standard), 8)


def test_mrs_C_standard(standard):
    """MRS_C = b_C / c_C = 2 / 1 = 2"""
    assert approx_eq(mrs_C(standard), 2)


# ============================================================
# check_scc 测试
# ============================================================

def test_check_scc_standard(standard):
    """标准参数 SCC 成立（MRS_S=8 > MRS_C=2）"""
    assert check_scc(standard) is True


def test_check_scc_violated():
    """反例: b_S 极小时 SCC 不成立"""
    # MRS_S = 0.5 / 0.5 = 1, MRS_C = 2 / 1 = 2
    params = GameParams(p0=0.4, b_S=0.5, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    assert check_scc(params) is False


def test_check_scc_boundary():
    """边界: MRS_S = MRS_C 时 SCC 不成立（要求严格不等式）"""
    # b_S=2, c_S=1, MRS_S=2 = MRS_C=2
    params = GameParams(p0=0.4, b_S=2, b_C=2, c_S=1, c_C=1, v_S=3, v_C=-2)
    assert check_scc(params) is False


# ============================================================
# solve_separating 测试
# ============================================================

def test_separating_exists(standard):
    """标准参数下分离均衡存在，s* = 2"""
    eq = solve_separating(standard)
    assert eq is not None
    assert eq.type == "separating"
    assert approx_eq(eq.s_S, 2)
    assert approx_eq(eq.s_C, 0)
    assert approx_eq(eq.accept_threshold, 2)


def test_separating_welfare(standard):
    """标准参数下福利计算正确"""
    eq = solve_separating(standard)
    # welfare_AS = b(S) - c(S) * s* = 4 - 0.5 * 2 = 3
    assert approx_eq(eq.welfare_AS, 3)
    # welfare_AC = 0 (C 被拒绝)
    assert approx_eq(eq.welfare_AC, 0)
    # welfare_B = p0 * v(S) = 0.4 * 3 = 1.2
    assert approx_eq(eq.welfare_B, 1.2)


def test_separating_none_when_scc_violated():
    """SCC 不成立时返回 None"""
    params = GameParams(p0=0.4, b_S=0.5, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    assert solve_separating(params) is None


# ============================================================
# solve_pooling 测试
# ============================================================

def test_pooling_none_at_boundary(standard):
    """标准参数下混同均衡不存在（p0=0.4 不严格大于 μ*=0.4）"""
    assert solve_pooling(standard) is None


def test_pooling_exists():
    """p0 = 0.7 > μ* = 0.4 时混同均衡存在"""
    params = GameParams(p0=0.7, b_S=4, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    eq = solve_pooling(params)
    assert eq is not None
    assert eq.type == "pooling"
    assert approx_eq(eq.s_pooled, 0)


def test_pooling_welfare():
    """p0 = 0.7 时福利计算正确"""
    params = GameParams(p0=0.7, b_S=4, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    eq = solve_pooling(params)
    # welfare_AS = b(S) = 4 (被接受、零投入)
    assert approx_eq(eq.welfare_AS, 4)
    # welfare_AC = b(C) = 2
    assert approx_eq(eq.welfare_AC, 2)
    # welfare_B = p0 * v(S) + (1-p0) * v(C) = 0.7*3 + 0.3*(-2) = 1.5
    assert approx_eq(eq.welfare_B, 1.5)


def test_pooling_none_when_p0_low():
    """p0 = 0.2 < μ* = 0.4 时混同均衡不存在"""
    params = GameParams(p0=0.2, b_S=4, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    assert solve_pooling(params) is None


# ============================================================
# solve_semi_separating 测试
# ============================================================

def test_semi_separating_none_at_boundary(standard):
    """标准参数下半分离均衡不存在（p0=0.4 不严格小于 μ*=0.4）"""
    assert solve_semi_separating(standard) is None


def test_semi_separating_exists():
    """p0 = 0.2 < μ* = 0.4 时半分离均衡存在"""
    params = GameParams(p0=0.2, b_S=4, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    eq = solve_semi_separating(params)
    assert eq is not None
    assert eq.type == "semi-separating"
    # q = p0*(1-μ*) / ((1-p0)*μ*) = 0.2*0.6 / (0.8*0.4) = 0.12/0.32 = 0.375
    assert approx_eq(eq.q, 0.375)
    # s_h = MRS_C = 2 (v1 简化)
    assert approx_eq(eq.s_h, 2)
    # r = c(C)*s_h/b(C) = 1*2/2 = 1
    assert approx_eq(eq.r, 1)


def test_semi_separating_none_when_scc_violated():
    """SCC 不成立时半分离均衡不存在"""
    params = GameParams(p0=0.2, b_S=0.5, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    assert solve_semi_separating(params) is None


# ============================================================
# solve_all 综合测试
# ============================================================

def test_solve_all_standard(standard):
    """标准参数下只有分离均衡存在"""
    eqs = solve_all(standard)
    assert len(eqs) == 1
    assert eqs[0].type == "separating"


def test_solve_all_high_p0():
    """p0 = 0.7 时分离和混同同时存在"""
    params = GameParams(p0=0.7, b_S=4, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    eqs = solve_all(params)
    types = sorted([e.type for e in eqs])
    assert "separating" in types
    assert "pooling" in types


def test_solve_all_low_p0():
    """p0 = 0.2 时分离和半分离同时存在"""
    params = GameParams(p0=0.2, b_S=4, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    eqs = solve_all(params)
    types = sorted([e.type for e in eqs])
    assert "separating" in types
    assert "semi-separating" in types


def test_solve_all_only_pooling():
    """SCC 不成立 + p0 大: 只有混同均衡"""
    # b_S=0.5 -> MRS_S=1 < MRS_C=2 (SCC 失败)
    # p0=0.8 > μ*=0.4 (混同存在)
    params = GameParams(p0=0.8, b_S=0.5, b_C=2, c_S=0.5, c_C=1, v_S=3, v_C=-2)
    eqs = solve_all(params)
    assert len(eqs) == 1
    assert eqs[0].type == "pooling"
