"""
约会信号博弈 v1 — 均衡求解器（已填好所有 TODO 的参考版本）

★ 这是一份参考答案文件，方便你和自己写的版本做对比。
★ TODO 1 用 Eddie 的展开写法，TODO 2-4 用标准答案。
"""

from dataclasses import dataclass
from typing import Optional, List, Union


# ============================================================
# 数据结构
# ============================================================

@dataclass
class GameParams:
    """博弈参数"""
    p0: float    # 先验信念: P(t = S)
    b_S: float   # S 类型被接受的回报
    b_C: float   # C 类型被接受的回报
    c_S: float   # S 类型的单位信号成本
    c_C: float   # C 类型的单位信号成本
    v_S: float   # B 接受 S 的效用（应为正）
    v_C: float   # B 接受 C 的效用（应为负）


@dataclass
class SeparatingEquilibrium:
    """分离均衡"""
    type: str = "separating"
    s_S: float = 0.0
    s_C: float = 0.0
    accept_threshold: float = 0.0
    welfare_AS: float = 0.0
    welfare_AC: float = 0.0
    welfare_B: float = 0.0


@dataclass
class PoolingEquilibrium:
    """混同均衡（v1 只考察 s=0 形式）"""
    type: str = "pooling"
    s_pooled: float = 0.0
    welfare_AS: float = 0.0
    welfare_AC: float = 0.0
    welfare_B: float = 0.0


@dataclass
class SemiSeparatingEquilibrium:
    """半分离均衡"""
    type: str = "semi-separating"
    s_h: float = 0.0
    q: float = 0.0
    r: float = 0.0
    welfare_AS: float = 0.0
    welfare_AC: float = 0.0
    welfare_B: float = 0.0


Equilibrium = Union[
    SeparatingEquilibrium,
    PoolingEquilibrium,
    SemiSeparatingEquilibrium,
]


# ============================================================
# 辅助函数
# ============================================================

def mu_star(params: GameParams) -> float:
    """B 的接受阈值 μ* = -v_C / (v_S - v_C)"""
    return -params.v_C / (params.v_S - params.v_C)


def mrs_S(params: GameParams) -> float:
    """S 类型的 MRS = b(S) / c(S)"""
    return params.b_S / params.c_S


def mrs_C(params: GameParams) -> float:
    """C 类型的 MRS = b(C) / c(C)"""
    return params.b_C / params.c_C


def validate_params(params: GameParams) -> None:
    """验证参数是否在合理范围"""
    if params.p0 <= 0 or params.p0 >= 1:
        raise ValueError(f"p0 必须在 (0, 1) 区间内，当前: {params.p0}")
    if params.b_S <= 0 or params.b_C <= 0:
        raise ValueError(f"b(S), b(C) 必须为正，当前: b_S={params.b_S}, b_C={params.b_C}")
    if params.c_S <= 0 or params.c_C <= 0:
        raise ValueError(f"c(S), c(C) 必须为正，当前: c_S={params.c_S}, c_C={params.c_C}")
    if params.v_S <= 0:
        raise ValueError(f"v(S) 必须为正（B 想接受 S），当前: {params.v_S}")
    if params.v_C >= 0:
        raise ValueError(f"v(C) 必须为负（B 不想接受 C），当前: {params.v_C}")


def approx_eq(a: float, b: float, tol: float = 1e-9) -> bool:
    """浮点数近似相等"""
    return abs(a - b) < tol


# ============================================================
# 核心算法
# ============================================================

def check_scc(params: GameParams) -> bool:
    """
    SCC（Single-Crossing Condition）: MRS_S > MRS_C
    """
    return params.b_S / params.c_S > params.b_C / params.c_C


def solve_separating(params: GameParams) -> Optional[SeparatingEquilibrium]:
    """
    分离均衡（LCSE 形式）
    存在条件: SCC 成立
    """
    # 1. 检查 SCC
    if not check_scc(params):
        return None

    # 2. 计算最优分离信号
    s_star = mrs_C(params)

    # 3. 算各方福利
    welfare_AS = params.b_S - params.c_S * s_star
    welfare_AC = 0.0
    welfare_B = params.p0 * params.v_S

    # 4. 构造并返回
    return SeparatingEquilibrium(
        s_S=s_star,
        s_C=0.0,
        accept_threshold=s_star,
        welfare_AS=welfare_AS,
        welfare_AC=welfare_AC,
        welfare_B=welfare_B,
    )


def solve_pooling(params: GameParams) -> Optional[PoolingEquilibrium]:
    """
    (0, 0) 混同均衡
    存在条件: p0 > μ*
    """
    # 1. 检查 p0 > μ*（严格不等式）
    if params.p0 <= mu_star(params):
        return None

    # 2. 算各方福利（两类型都被接受、零投入）
    welfare_AS = params.b_S
    welfare_AC = params.b_C
    welfare_B = params.p0 * params.v_S + (1 - params.p0) * params.v_C

    # 3. 构造并返回
    return PoolingEquilibrium(
        s_pooled=0.0,
        welfare_AS=welfare_AS,
        welfare_AC=welfare_AC,
        welfare_B=welfare_B,
    )


def solve_semi_separating(params: GameParams) -> Optional[SemiSeparatingEquilibrium]:
    """
    半分离均衡
    存在条件: SCC 成立 + p0 < μ*
    """
    # 1. 检查 SCC
    if not check_scc(params):
        return None

    # 2. 检查 p0 < μ*
    mu = mu_star(params)
    if params.p0 >= mu:
        return None

    # 3. 计算 q
    q = params.p0 * (1 - mu) / ((1 - params.p0) * mu)

    # 4. 检查 q ∈ (0, 1)
    if q <= 0 or q >= 1:
        return None

    # 5. 取 s_h = MRS_C（v1 简化）
    s_h = mrs_C(params)

    # 6. 计算 r 并检查 r ∈ (0, 1]
    r = params.c_C * s_h / params.b_C
    if r <= 0 or r > 1:
        return None

    # 7. 算各方福利
    welfare_AS = r * params.b_S - params.c_S * s_h
    welfare_AC = 0.0
    welfare_B = params.p0 * r * params.v_S + (1 - params.p0) * q * r * params.v_C

    # 8. 构造并返回
    return SemiSeparatingEquilibrium(
        s_h=s_h,
        q=q,
        r=r,
        welfare_AS=welfare_AS,
        welfare_AC=welfare_AC,
        welfare_B=welfare_B,
    )


# ============================================================
# 主入口
# ============================================================

def solve_all(params: GameParams) -> List[Equilibrium]:
    """
    求解所有可能的 PBE
    """
    validate_params(params)

    equilibria: List[Equilibrium] = []

    sep = solve_separating(params)
    if sep is not None:
        equilibria.append(sep)

    pool = solve_pooling(params)
    if pool is not None:
        equilibria.append(pool)

    semi = solve_semi_separating(params)
    if semi is not None:
        equilibria.append(semi)

    return equilibria


# ============================================================
# 直接运行此文件可以快速测试
# ============================================================

if __name__ == "__main__":
    standard = GameParams(
        p0=0.4,
        b_S=4, b_C=2,
        c_S=0.5, c_C=1,
        v_S=3, v_C=-2,
    )

    print("=" * 50)
    print("约会信号博弈 v1 - 快速测试")
    print("=" * 50)
    print(f"参数: {standard}")
    print(f"μ* = {mu_star(standard)}")
    print(f"MRS_S = {mrs_S(standard)}")
    print(f"MRS_C = {mrs_C(standard)}")
    print(f"SCC 成立? {check_scc(standard)}")
    print()
    print("均衡:")
    for eq in solve_all(standard):
        print(f"  {eq}")
