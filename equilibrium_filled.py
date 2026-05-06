"""
约会信号博弈 v1 — 均衡求解器

实现完美贝叶斯均衡（PBE）的求解：
  - 分离均衡 (Separating, LCSE 形式)
  - 混同均衡 (Pooling, s=0 形式)
  - 半分离均衡 (Semi-Separating)

数学模型见: docs/math.md（v1 阶段是设计文档 §2 节）

============================================================
你的任务: 实现下面四个标记为 TODO 的函数:
  1. check_scc
  2. solve_separating
  3. solve_pooling
  4. solve_semi_separating

其他代码（数据结构、辅助函数、参数验证、入口函数）我已经写好。
写完后跑 `python -m pytest test_equilibrium.py -v` 验证。
============================================================
"""

from dataclasses import dataclass
from typing import Optional, List, Union


# ============================================================
# 数据结构（已完成 — 不要修改）
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
    s_S: float = 0.0           # S 类型选择的信号水平
    s_C: float = 0.0           # C 类型选择的信号水平
    accept_threshold: float = 0.0   # B 的接受阈值
    welfare_AS: float = 0.0    # S 类型的均衡效用
    welfare_AC: float = 0.0    # C 类型的均衡效用
    welfare_B: float = 0.0     # B 的均衡期望效用


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
    s_h: float = 0.0    # S 类型选择的高信号
    q: float = 0.0      # C 类型混合到高信号的概率
    r: float = 0.0      # B 看到高信号时接受的概率
    welfare_AS: float = 0.0
    welfare_AC: float = 0.0
    welfare_B: float = 0.0


Equilibrium = Union[
    SeparatingEquilibrium,
    PoolingEquilibrium,
    SemiSeparatingEquilibrium,
]


# ============================================================
# 辅助函数（已完成）
# ============================================================

def mu_star(params: GameParams) -> float:
    """
    计算 B 的接受阈值 μ*
    μ* = -v_C / (v_S - v_C)
    含义: B 必须相信 P(t=S | s) > μ* 才会接受
    """
    return -params.v_C / (params.v_S - params.v_C)


def mrs_S(params: GameParams) -> float:
    """
    计算 S 类型的 MRS = b(S) / c(S)
    含义: S 类型为 1 单位接受概率最多愿意付出的信号水平
    """
    return params.b_S / params.c_S


def mrs_C(params: GameParams) -> float:
    """
    计算 C 类型的 MRS = b(C) / c(C)
    含义: C 类型为 1 单位接受概率最多愿意付出的信号水平
          也是 LCSE 的最优分离信号水平
    """
    return params.b_C / params.c_C


def validate_params(params: GameParams) -> None:
    """验证参数是否在合理范围，不合理直接抛错"""
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
# 核心算法（你来实现）
# ============================================================

def check_scc(params: GameParams) -> bool:
    """
    TODO 1: 检查 SCC（Single-Crossing Condition）

    SCC 的严格版本: MRS_S > MRS_C
                    <=> b(S)/c(S) > b(C)/c(C)

    含义: 认真型对这段关系的"性价比"比不认真型高，
          所以认真型愿意付出更高的信号水平。

    提示: 用上面的 mrs_S 和 mrs_C 函数。这个函数应该非常短（一行）。

    返回:
        SCC 成立返回 True，否则返回 False
    """
    # TODO: 实现这里
    raise NotImplementedError("check_scc: 待实现")


def solve_separating(params: GameParams) -> Optional[SeparatingEquilibrium]:
    """
    TODO 2: 求解分离均衡（LCSE 形式）

    存在条件: SCC 成立

    均衡形式（Cho-Kreps 精炼后）:
        - S 选 s* = b(C)/c(C) = MRS_C
        - C 选 0
        - B 看到 s >= s* 接受、s < s* 拒绝

    福利计算:
        - S 被接受: welfare_AS = b(S) - c(S) * s*
        - C 被拒绝: welfare_AC = 0
        - B 期望效用: welfare_B = p0 * v(S)
          (概率 p0 接受 S 得 v(S)，概率 1-p0 拒绝 C 得 0)

    返回 None 表示分离均衡不存在
    """
    # TODO: 实现这里
    # 步骤:
    #   1. 用 check_scc 检查，不成立返回 None
    #   2. 计算 s_star = mrs_C(params)
    #   3. 算各方福利
    #   4. 构造并返回 SeparatingEquilibrium 对象
    raise NotImplementedError("solve_separating: 待实现")


def solve_pooling(params: GameParams) -> Optional[PoolingEquilibrium]:
    """
    TODO 3: 求解 (0, 0) 混同均衡

    存在条件: p0 > μ*
        含义: B 默认信任足够高，看到 s=0 也愿意接受

    均衡形式:
        - 两类型都选 s = 0
        - B 看到 s = 0 接受
        - 离均衡路径上 B 看到 s > 0 都认为是 C，拒绝

    福利计算:
        - S 被接受、零投入: welfare_AS = b(S)
        - C 被接受、零投入: welfare_AC = b(C)
        - B 期望效用: welfare_B = p0 * v(S) + (1 - p0) * v(C)

    注意: 用严格不等式 p0 > μ*，不是 p0 >= μ*

    返回 None 表示混同均衡不存在
    """
    # TODO: 实现这里
    raise NotImplementedError("solve_pooling: 待实现")


def solve_semi_separating(params: GameParams) -> Optional[SemiSeparatingEquilibrium]:
    """
    TODO 4: 求解半分离均衡

    存在条件:
        - SCC 成立
        - p0 < μ*

    均衡形式:
        - S 永远选高信号 s_h
        - C 以概率 q 选 s_h、以概率 1-q 选 0
        - B 看到 s_h 时以概率 r 接受
        - B 看到 s = 0 时拒绝

    三个均衡条件:
        方程1（B 在 s_h 处无差异）:
            后验 μ(s_h) = μ*
            => q = p0 * (1 - μ*) / ((1 - p0) * μ*)

        方程2（C 在 s_h 和 0 之间无差异）:
            r * b(C) - c(C) * s_h = 0
            => r = c(C) * s_h / b(C)

        方程3（s_h 的确定）:
            v1 简化处理: 取 s_h = MRS_C = b(C)/c(C)
            （和分离均衡的最优信号相同）
            这种处理对应 r = 1 的极端情形。
            更严格的处理留给 v2。

    福利计算（按上述简化）:
        - S 必接受: welfare_AS = r * b(S) - c(S) * s_h
        - C 在 s_h 和 0 之间无差异（效用都为 0）: welfare_AC = 0
        - B 的期望:
            welfare_B = p0 * r * v(S) + (1 - p0) * q * r * v(C)

            [S 概率 p0 选 s_h、被接受概率 r、B 得 v(S)]
            [C 概率 (1-p0) * q 选 s_h、被接受概率 r、B 得 v(C)]
            [C 概率 (1-p0) * (1-q) 选 0、被拒绝、B 得 0]

    返回 None 表示半分离均衡不存在
    """
    # TODO: 实现这里
    # 步骤:
    #   1. 检查 SCC 和 p0 < μ*
    #   2. 计算 q = p0 * (1 - μ*) / ((1 - p0) * μ*)
    #   3. 检查 q ∈ (0, 1)
    #   4. 取 s_h = mrs_C(params)（v1 简化）
    #   5. 计算 r = c_C * s_h / b_C
    #   6. 检查 r ∈ (0, 1]
    #   7. 算各方福利
    #   8. 构造并返回 SemiSeparatingEquilibrium 对象
    raise NotImplementedError("solve_semi_separating: 待实现")


# ============================================================
# 主入口（已完成）
# ============================================================

def solve_all(params: GameParams) -> List[Equilibrium]:
    """
    求解所有可能的 PBE
    返回列表 — 同一组参数下可能存在多个均衡
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
# 直接运行此文件可以快速测试（已完成）
# ============================================================

if __name__ == "__main__":
    # 标准参数（讲解里反复用的那组）
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
