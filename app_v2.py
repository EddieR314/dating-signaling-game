"""
约会信号博弈可视化 — Streamlit 应用 (v2 修复字体)
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np
import matplotlib
import matplotlib.font_manager as fm

from equilibrium import (
    GameParams,
    mu_star, mrs_S, mrs_C,
    solve_all,
    SeparatingEquilibrium,
    PoolingEquilibrium,
    SemiSeparatingEquilibrium,
)

st.set_page_config(
    page_title="信号博弈在恋爱场景的可视化",
    page_icon="💕",
    layout="wide",
)

# ============================================================
# 中文字体配置 (兼容 Linux 服务器和 Windows 本地)
# ============================================================

def setup_chinese_font():
    """按平台优先级设置中文字体. 支持 Linux/Mac/Windows."""
    candidate_fonts = [
        "Noto Sans CJK SC",
        "Noto Sans CJK JP",
        "WenQuanYi Zen Hei",
        "WenQuanYi Micro Hei",
        "PingFang SC",
        "Heiti SC",
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]

    available_fonts = {f.name for f in fm.fontManager.ttflist}

    chosen = None
    for font in candidate_fonts:
        if font in available_fonts:
            chosen = font
            break

    if chosen:
        matplotlib.rcParams["font.sans-serif"] = [chosen] + candidate_fonts
    else:
        matplotlib.rcParams["font.sans-serif"] = candidate_fonts

    matplotlib.rcParams["axes.unicode_minus"] = False


setup_chinese_font()

DEFAULTS = {
    "p0": 0.40, "b_S": 4.0, "b_C": 2.0,
    "c_S": 0.5, "c_C": 1.0, "v_S": 3.0, "v_C": -2.0,
}

st.title("信号博弈在恋爱场景的可视化")
st.markdown("**基于 Spence (1973) 信号博弈理论的均衡解演示**")

st.markdown("""
在追求关系中,被追求方面临一个判断难题:对方究竟是认真的,还是只是出于一时的兴趣。
直接的言语难以传递信息,因为不同动机的追求者都可以说出同样的话。

但行为有所不同。一些行为对认真者而言成本可控,对不认真者则成本高昂——长期的坚持、
远距离的迁移、持续的时间投入都属于此类。当一种行为对两类人的代价存在显著差异时,
这种行为本身便成为可信的信号。

本项目以 Spence (1973) 的信号博弈理论为基础,在恋爱场景中演示这一机制的均衡解。
其中一些结论可能符合直观经验——例如「为什么备胎现象普遍存在」、
「为什么追了很久才在一起的关系往往更稳定」等问题,都能在这个框架中找到精确的数学解释。
""")

st.divider()

with st.sidebar:
    st.header("参数面板")
    st.caption("拖动滑块,右侧实时更新均衡分析。")

    if st.button("恢复默认值"):
        for key, val in DEFAULTS.items():
            st.session_state[key] = val
        st.rerun()

    st.divider()

    p0 = st.slider("对方的初始信任度", 0.05, 0.95, st.session_state.get("p0", DEFAULTS["p0"]), 0.05, key="p0")
    with st.expander("说明"):
        st.markdown("""
对应模型中的先验概率 p₀,即被追求方在观察到任何信号之前,
对追求者「为认真型」的主观概率判断。

较高值对应高信任环境(熟人介绍、小圈子),较低值对应低信任环境(交友软件、陌生人圈子)。
""")

    st.markdown("---")

    b_S = st.slider("认真型从被接受获得的价值", 0.5, 5.0, st.session_state.get("b_S", DEFAULTS["b_S"]), 0.1, key="b_S")
    with st.expander("说明"):
        st.markdown("""
认真型追求者(类型 S)被接受时获得的效用 b(S)。
反映该类型对这段关系的看重程度。
""")

    b_C = st.slider("不认真型从被接受获得的价值", 0.5, 5.0, st.session_state.get("b_C", DEFAULTS["b_C"]), 0.1, key="b_C")
    with st.expander("说明"):
        st.markdown("""
不认真型追求者(类型 C)被接受时获得的效用 b(C)。
通常假设 b(C) < b(S),即不认真型对该关系的看重程度较低。
""")

    if b_C >= b_S:
        st.warning("⚠ 通常假设认真型对该关系更看重。当前设置 b(C) ≥ b(S),与该假设相悖。")

    st.markdown("---")

    c_S = st.slider("认真型每单位投入的痛苦感", 0.1, 2.0, st.session_state.get("c_S", DEFAULTS["c_S"]), 0.05, key="c_S")
    with st.expander("说明"):
        st.markdown("""
认真型追求者投入单位信号(时间、金钱、心力)的主观成本 c(S)。
取值越低,代表该类型的「投入心理代价」越小。
""")

    c_C = st.slider("不认真型每单位投入的痛苦感", 0.1, 2.0, st.session_state.get("c_C", DEFAULTS["c_C"]), 0.05, key="c_C")
    with st.expander("说明"):
        st.markdown("""
不认真型追求者投入单位信号的主观成本 c(C)。
通常假设 c(C) > c(S)——即不认真型为同样的投入承受更大的心理代价。

c(S) 与 c(C) 的差距是 Single-Crossing Condition 的核心,
也是分离均衡得以存在的根本条件。
""")

    if c_C <= c_S:
        st.warning("⚠ 通常假设不认真者付出代价更高。当前设置违反 Single-Crossing Condition。")

    st.markdown("---")

    v_S = st.slider("被追求方接受「认真型」的价值", 0.5, 5.0, st.session_state.get("v_S", DEFAULTS["v_S"]), 0.1, key="v_S")
    with st.expander("说明"):
        st.markdown("""
被追求方(B)接受认真型追求者获得的效用 v(S),为正数。
""")

    v_C = st.slider("被追求方接受「不认真型」的损失", -5.0, -0.5, st.session_state.get("v_C", DEFAULTS["v_C"]), 0.1, key="v_C")
    with st.expander("说明"):
        st.markdown("""
被追求方接受不认真型追求者所蒙受的损失 v(C),为负数。
反映被欺骗或错误匹配的预期代价。
""")

params = GameParams(p0=p0, b_S=b_S, b_C=b_C, c_S=c_S, c_C=c_C, v_S=v_S, v_C=v_C)
equilibria = solve_all(params)


def draw_face(ax, x, y, radius, mood):
    face = Circle((x, y), radius, fill=True, facecolor="#FFE4B5",
                  edgecolor="black", linewidth=1.5, zorder=3)
    ax.add_patch(face)
    eye_y = y + radius * 0.2
    eye_offset = radius * 0.3
    ax.plot([x - eye_offset], [eye_y], "ko", markersize=3, zorder=4)
    ax.plot([x + eye_offset], [eye_y], "ko", markersize=3, zorder=4)
    mouth_y = y - radius * 0.25
    mouth_w = radius * 0.4
    if mood == "happy":
        theta = np.linspace(np.pi * 1.15, np.pi * 1.85, 30)
        mx = x + mouth_w * np.cos(theta)
        my = mouth_y + radius * 0.5 + mouth_w * np.sin(theta) * 0.6
        ax.plot(mx, my, "k-", linewidth=1.5, zorder=4)
    elif mood == "sad":
        theta = np.linspace(np.pi * 0.15, np.pi * 0.85, 30)
        mx = x + mouth_w * np.cos(theta)
        my = mouth_y - radius * 0.3 + mouth_w * np.sin(theta) * 0.6
        ax.plot(mx, my, "k-", linewidth=1.5, zorder=4)
    else:
        ax.plot([x - mouth_w, x + mouth_w], [mouth_y, mouth_y],
                "k-", linewidth=1.5, zorder=4)


def make_narrative_chart(params, equilibria):
    fig, ax = plt.subplots(figsize=(12, 5))
    main_eq = equilibria[0] if equilibria else None
    pos_S = (1, 3); pos_C = (1, 1); pos_B = (5, 2)

    if isinstance(main_eq, SeparatingEquilibrium):
        s_invest = main_eq.s_S; c_invest = main_eq.s_C
        s_accepted = True; c_accepted = False
        scenario_title = "分离均衡 (Separating Equilibrium)"
    elif isinstance(main_eq, PoolingEquilibrium):
        s_invest = 0; c_invest = 0
        s_accepted = True; c_accepted = True
        scenario_title = "混同均衡 (Pooling Equilibrium)"
    elif isinstance(main_eq, SemiSeparatingEquilibrium):
        s_invest = main_eq.s_h; c_invest = main_eq.s_h * main_eq.q
        s_accepted = True; c_accepted = main_eq.q > 0.5
        scenario_title = f"半分离均衡 (q = {main_eq.q*100:.0f}% 伪装)"
    else:
        s_invest = 0; c_invest = 0
        s_accepted = False; c_accepted = False
        scenario_title = "无标准均衡"

    draw_face(ax, *pos_S, 0.35, "happy" if s_accepted else "sad")
    ax.text(pos_S[0], pos_S[1] + 0.6, "认真型追求者", ha="center", fontsize=11, fontweight="bold")
    draw_face(ax, *pos_C, 0.35, "happy" if c_accepted else "sad")
    ax.text(pos_C[0], pos_C[1] - 0.6, "不认真型追求者", ha="center", fontsize=11, fontweight="bold")

    if s_accepted or c_accepted:
        b_mood = "happy" if (s_accepted and not c_accepted) else "neutral"
    else:
        b_mood = "neutral"
    draw_face(ax, *pos_B, 0.4, b_mood)
    ax.text(pos_B[0], pos_B[1] + 0.7, "被追求方", ha="center", fontsize=11, fontweight="bold")

    max_invest = max(s_invest, c_invest, 0.5)
    if s_invest > 0.01:
        width_S = 1 + 4 * (s_invest / max(max_invest, 1))
        arrow_S = FancyArrowPatch(
            (pos_S[0] + 0.4, pos_S[1]), (pos_B[0] - 0.5, pos_B[1] + 0.3),
            arrowstyle=f"-|>, head_length=0.4, head_width={width_S * 0.15}",
            linewidth=width_S, color="steelblue", zorder=2, mutation_scale=15)
        ax.add_patch(arrow_S)
        ax.text((pos_S[0] + pos_B[0]) / 2, (pos_S[1] + pos_B[1] + 0.3) / 2 + 0.3,
                f"投入 {s_invest:.2f}", ha="center", fontsize=10, color="steelblue", fontweight="bold")
    else:
        ax.text((pos_S[0] + pos_B[0]) / 2, (pos_S[1] + pos_B[1] + 0.3) / 2 + 0.2,
                "(无投入)", ha="center", fontsize=9, color="gray", style="italic")

    if c_invest > 0.01:
        width_C = 1 + 4 * (c_invest / max(max_invest, 1))
        arrow_C = FancyArrowPatch(
            (pos_C[0] + 0.4, pos_C[1]), (pos_B[0] - 0.5, pos_B[1] - 0.3),
            arrowstyle=f"-|>, head_length=0.4, head_width={width_C * 0.15}",
            linewidth=width_C, color="indianred", zorder=2, mutation_scale=15)
        ax.add_patch(arrow_C)
        if isinstance(main_eq, SemiSeparatingEquilibrium):
            label = f"伪装投入 {main_eq.s_h:.2f}\n(概率 {main_eq.q*100:.0f}%)"
        else:
            label = f"投入 {c_invest:.2f}"
        ax.text((pos_C[0] + pos_B[0]) / 2, (pos_C[1] + pos_B[1] - 0.3) / 2 - 0.4,
                label, ha="center", fontsize=10, color="indianred", fontweight="bold")
    else:
        ax.text((pos_C[0] + pos_B[0]) / 2, (pos_C[1] + pos_B[1] - 0.3) / 2 - 0.2,
                "(无投入)", ha="center", fontsize=9, color="gray", style="italic")

    if s_accepted:
        ax.text(pos_B[0] + 0.7, pos_B[1] + 0.3, "✓ 接受", fontsize=11, color="green", fontweight="bold")
    if not s_accepted and not c_accepted:
        ax.text(pos_B[0] + 0.7, pos_B[1], "✗ 全部拒绝", fontsize=11, color="red", fontweight="bold")
    if c_accepted and not s_accepted:
        ax.text(pos_B[0] + 0.7, pos_B[1] - 0.3, "? 接受不认真", fontsize=11, color="orange", fontweight="bold")
    if s_accepted and c_accepted:
        ax.text(pos_B[0] + 0.7, pos_B[1] - 0.3, "✓ 全部接受", fontsize=11, color="darkgreen", fontweight="bold")

    ax.set_title(scenario_title, fontsize=13, pad=15)
    ax.set_xlim(0, 8); ax.set_ylim(0, 4.5)
    ax.set_aspect("equal"); ax.axis("off")
    return fig


def make_combo_charts(params, equilibria):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    main_eq = equilibria[0] if equilibria else None

    ax1 = axes[0]
    if isinstance(main_eq, SeparatingEquilibrium):
        s_val = main_eq.s_S; c_val = main_eq.s_C
    elif isinstance(main_eq, PoolingEquilibrium):
        s_val = main_eq.s_pooled; c_val = main_eq.s_pooled
    elif isinstance(main_eq, SemiSeparatingEquilibrium):
        s_val = main_eq.s_h; c_val = main_eq.q * main_eq.s_h
    else:
        s_val = 0; c_val = 0

    bars = ax1.bar(["认真型", "不认真型"], [s_val, c_val],
                   color=["steelblue", "indianred"], edgecolor="black", linewidth=1)
    ax1.set_ylabel("投入水平", fontsize=11)
    ax1.set_title("两类追求者的均衡投入", fontsize=12, pad=10)
    ax1.grid(True, alpha=0.3, axis="y")
    for bar, val in zip(bars, [s_val, c_val]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 f"{val:.2f}", ha="center", fontsize=11, fontweight="bold")
    ax1.set_ylim(0, max(s_val, c_val, 1) * 1.3)

    ax2 = axes[1]
    if isinstance(main_eq, SeparatingEquilibrium):
        threshold = main_eq.accept_threshold; s_pos = main_eq.s_S; c_pos = main_eq.s_C
        title2 = "接受门槛与投入位置"
    elif isinstance(main_eq, PoolingEquilibrium):
        threshold = 0; s_pos = 0; c_pos = 0
        title2 = "接受门槛(全接受)"
    elif isinstance(main_eq, SemiSeparatingEquilibrium):
        threshold = main_eq.s_h; s_pos = main_eq.s_h; c_pos = 0
        title2 = "接受门槛与投入位置"
    else:
        threshold = 0; s_pos = 0; c_pos = 0
        title2 = "(均衡不存在)"

    max_x = max(threshold * 1.5, mrs_S(params), 3)
    ax2.axhline(y=0.5, xmin=0.05, xmax=0.95, color="lightgray", linewidth=8, zorder=1)
    if threshold > 0:
        ax2.axvspan(0, threshold, alpha=0.2, color="red", zorder=0)
        ax2.text(threshold / 2, 0.85, "拒绝区", ha="center", fontsize=10, color="darkred")
    ax2.axvspan(threshold, max_x, alpha=0.2, color="green", zorder=0)
    ax2.text((threshold + max_x) / 2, 0.85, "接受区", ha="center", fontsize=10, color="darkgreen")
    if threshold > 0:
        ax2.axvline(x=threshold, color="black", linewidth=2, linestyle="--", zorder=2)
        ax2.text(threshold, 0.15, f"门槛 = {threshold:.2f}",
                 ha="center", fontsize=10, fontweight="bold")
    ax2.scatter([s_pos], [0.5], color="steelblue", s=300, zorder=5,
                edgecolors="white", linewidth=2, label=f"认真型 (s={s_pos:.2f})")
    ax2.scatter([c_pos], [0.5], color="indianred", s=300, zorder=5,
                edgecolors="white", linewidth=2, marker="s", label=f"不认真型 (s={c_pos:.2f})")
    ax2.set_xlim(-0.2, max_x); ax2.set_ylim(0, 1)
    ax2.set_xlabel("投入水平", fontsize=11); ax2.set_yticks([])
    ax2.set_title(title2, fontsize=12, pad=10)
    ax2.legend(loc="upper right", fontsize=9)

    ax3 = axes[2]
    if main_eq:
        welfares = [main_eq.welfare_AS, main_eq.welfare_AC, main_eq.welfare_B]
    else:
        welfares = [0, 0, 0]
    labels3 = ["认真型\n效用", "不认真型\n效用", "被追求方\n期望效用"]
    colors3 = ["steelblue", "indianred", "darkgreen"]
    bars3 = ax3.bar(labels3, welfares, color=colors3, edgecolor="black", linewidth=1)
    ax3.set_ylabel("效用", fontsize=11)
    ax3.set_title("均衡下三方福利", fontsize=12, pad=10)
    ax3.grid(True, alpha=0.3, axis="y")
    ax3.axhline(y=0, color="black", linewidth=0.5)
    for bar, val in zip(bars3, welfares):
        y_offset = 0.1 if val >= 0 else -0.2
        ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + y_offset,
                 f"{val:.2f}", ha="center", fontsize=10, fontweight="bold")
    plt.tight_layout()
    return fig


def make_main_chart(params, equilibria):
    fig, ax = plt.subplots(figsize=(10, 5))
    s_max = max(mrs_S(params) * 1.2, 5)
    threshold_S = mrs_S(params)
    ax.axvspan(0, min(threshold_S, s_max), alpha=0.15, color="blue",
               label=f"认真型承受范围 (≤ {threshold_S:.2f})")
    threshold_C = mrs_C(params)
    ax.axvspan(0, min(threshold_C, s_max), alpha=0.15, color="red",
               label=f"不认真型承受范围 (≤ {threshold_C:.2f})")
    main_eq = equilibria[0] if equilibria else None

    if isinstance(main_eq, SeparatingEquilibrium):
        threshold = main_eq.accept_threshold
        ax.plot([0, threshold], [0, 0], color="black", linewidth=2)
        ax.plot([threshold, threshold], [0, 1], color="black", linewidth=2,
                linestyle="--", alpha=0.5)
        ax.plot([threshold, s_max], [1, 1], color="black", linewidth=2, label="对方的接受策略")
        ax.scatter([main_eq.s_S], [1], color="blue", s=200, zorder=5,
                   label=f"认真型选择 (s = {main_eq.s_S:.2f})", edgecolors="white", linewidth=2)
        ax.scatter([main_eq.s_C], [0], color="red", s=200, zorder=5,
                   label=f"不认真型选择 (s = {main_eq.s_C:.2f})", edgecolors="white", linewidth=2)
    elif isinstance(main_eq, PoolingEquilibrium):
        ax.plot([0, s_max], [1, 1], color="black", linewidth=2, label="对方的接受策略 (全接受)")
        ax.scatter([0], [1], color="purple", s=300, zorder=5,
                   label="两类型都选 s = 0", edgecolors="white", linewidth=2)
    elif isinstance(main_eq, SemiSeparatingEquilibrium):
        threshold = main_eq.s_h
        ax.plot([0, threshold], [0, 0], color="black", linewidth=2)
        ax.plot([threshold, threshold], [0, main_eq.r], color="black",
                linewidth=2, linestyle="--", alpha=0.5)
        ax.plot([threshold, s_max], [main_eq.r, main_eq.r], color="black",
                linewidth=2, label=f"接受率 = {main_eq.r:.2f}")
        ax.scatter([main_eq.s_h], [main_eq.r], color="blue", s=200, zorder=5,
                   label=f"认真型选择 (s = {main_eq.s_h:.2f})", edgecolors="white", linewidth=2)
        ax.scatter([0], [0], color="red", s=150, zorder=5, alpha=0.5,
                   label=f"不认真型: {(1-main_eq.q)*100:.0f}% 选 0",
                   edgecolors="white", linewidth=2)
        ax.scatter([main_eq.s_h], [main_eq.r * 0.5], color="red", s=150,
                   zorder=5, marker="^",
                   label=f"不认真型: {main_eq.q*100:.0f}% 伪装",
                   edgecolors="white", linewidth=2)

    ax.set_xlabel("投入度 s", fontsize=12)
    ax.set_ylabel("接受概率", fontsize=12)
    ax.set_xlim(-0.2, s_max); ax.set_ylim(-0.1, 1.2)
    ax.legend(loc="center right", fontsize=9)
    ax.grid(True, alpha=0.3)
    return fig


def render_separating(eq):
    st.markdown("### 分离均衡 (Separating Equilibrium)")
    col1, col2, col3 = st.columns(3)
    col1.metric("认真型最优投入度", f"{eq.s_S:.2f}")
    col2.metric("不认真型最优投入度", f"{eq.s_C:.2f}")
    col3.metric("接受门槛", f"{eq.accept_threshold:.2f}")
    st.markdown(f"""
当前参数下,博弈达到分离均衡。

认真型追求者选择投入水平 {eq.s_S:.2f},不认真型追求者选择不投入。
被追求方依据观察到的投入水平做出判断:投入达到 {eq.accept_threshold:.2f} 即接受,否则拒绝。

这一结果的稳定性来源于不认真型的最优放弃:在该投入水平下,
不认真型即使被接受,所获效用也低于不投入(因为投入成本超过被接受收益)。
故不认真型选择不投入是其个体最优策略。

这种均衡常常对应「追了很久才在一起」的恋爱叙事——例如从大一追到大三的故事。
其中的「很久」并非时间的浪费,而是博弈论意义上必要的信号成本——
它使真心得以被识别。
""")
    with st.expander("均衡福利"):
        st.markdown(f"""
- 认真型追求者效用:{eq.welfare_AS:.2f}
- 不认真型追求者效用:{eq.welfare_AC:.2f}(未投入,被拒绝)
- 被追求方期望效用:{eq.welfare_B:.2f}
""")


def render_pooling(eq):
    st.markdown("### 混同均衡 (Pooling Equilibrium)")
    col1, col2 = st.columns(2)
    col1.metric("共同投入度", f"{eq.s_pooled:.2f}")
    col2.metric("接受率", "100%")
    st.markdown("""
当前参数下,博弈达到混同均衡。

两种类型的追求者均选择零投入,被追求方对所有追求一律接受。
其内在逻辑为:被追求方的先验信任度足够高(p₀ > μ*),
即使在没有任何信号支持的情况下,接受的期望效用仍为正。
此时「投入」作为信号的功能完全消失。

这种均衡常出现于熟人介绍、小圈子约会等高信任环境。配对效率高,
但代价是无法保证配对质量——可能接受到的是不认真者。

当市场扩大、陌生人比例上升,先验信任度 p₀ 下降,这一均衡将不再成立,
并被分离均衡或半分离均衡取代。
""")
    with st.expander("均衡福利"):
        st.markdown(f"""
- 认真型追求者效用:{eq.welfare_AS:.2f}(被接受,零投入)
- 不认真型追求者效用:{eq.welfare_AC:.2f}(被接受,零投入)
- 被追求方期望效用:{eq.welfare_B:.2f}
""")


def render_semi_separating(eq):
    st.markdown("### 半分离均衡 (Semi-Separating Equilibrium)")
    col1, col2, col3 = st.columns(3)
    col1.metric("认真型投入度", f"{eq.s_h:.2f}")
    col2.metric("不认真型伪装率", f"{eq.q*100:.1f}%")
    col3.metric("被追求方接受率", f"{eq.r*100:.1f}%")
    st.markdown(f"""
当前参数下,博弈达到半分离均衡。

认真型追求者仍选择高水平投入。不认真型则采取混合策略:
以 {eq.q*100:.1f}% 的概率伪装为认真型(投入相同水平),
以 {(1-eq.q)*100:.1f}% 的概率选择零投入。

被追求方观察到高投入信号时,无法 100% 区分追求者类型,
故采取混合接受策略,接受概率为 {eq.r*100:.1f}%。

这一均衡是博弈论对「备胎现象」的精确解释:
当先验信任度不足时,部分不认真者发现伪装在期望意义上仍然有利可图,
故选择以一定概率投入伪装。市场上同时存在真心追求者、伪装者、
半信半疑接受者、果断拒绝者——这是博弈的均衡结果,而非市场失灵。

要消除此现象,需提高先验信任度 p₀ 至 μ* 以上,
或拉大两类型的成本差距 c(C) - c(S),使伪装的代价显著高于收益。
""")
    with st.expander("均衡福利"):
        st.markdown(f"""
- 认真型追求者效用:{eq.welfare_AS:.2f}
- 不认真型追求者效用:{eq.welfare_AC:.2f}(在两种选择间无差异)
- 被追求方期望效用:{eq.welfare_B:.2f}
""")


if not equilibria:
    st.markdown("### 当前参数下,标准均衡形式不存在")
    st.markdown("""
此参数组合可能违反了模型的基本假设(如 Single-Crossing Condition)。
请调整参数,确保 c(S) < c(C) 且 p₀ 在合理范围内。
""")
elif len(equilibria) == 1:
    eq = equilibria[0]
    if isinstance(eq, SeparatingEquilibrium):
        render_separating(eq)
    elif isinstance(eq, PoolingEquilibrium):
        render_pooling(eq)
    elif isinstance(eq, SemiSeparatingEquilibrium):
        render_semi_separating(eq)
else:
    st.markdown("### 多重均衡 (Multiple Equilibria)")
    st.markdown("""
当前参数下存在多个完美贝叶斯均衡。这是不完全信息动态博弈中的常见现象——
同一参数组合下可能存在多个稳定的策略组合。最终市场停留于哪一均衡,
通常取决于历史路径、群体共识等理论之外的因素。

下面分别展示各均衡的详情:
""")
    st.markdown("---")
    for eq in equilibria:
        if isinstance(eq, SeparatingEquilibrium):
            render_separating(eq)
        elif isinstance(eq, PoolingEquilibrium):
            render_pooling(eq)
        elif isinstance(eq, SemiSeparatingEquilibrium):
            render_semi_separating(eq)
        st.markdown("---")

st.divider()
st.subheader("均衡可视化")

st.markdown("#### 博弈结构示意")
fig1 = make_narrative_chart(params, equilibria)
st.pyplot(fig1, use_container_width=True)
st.caption("""
图示当前均衡下三方的策略与状态。箭头粗细表示投入水平,
表情表示该角色在均衡结果中的得失状态。
""")

st.markdown("#### 关键指标")
fig2 = make_combo_charts(params, equilibria)
st.pyplot(fig2, use_container_width=True)

with st.expander("严谨版图表: 信号 vs 接受概率"):
    st.markdown("""
此图展示信号(投入度)与接受概率的关系,以及两类型的承受范围。
该呈现保留博弈论标准教科书的图表形式,适合已了解模型的读者深入分析。
""")
    fig3 = make_main_chart(params, equilibria)
    st.pyplot(fig3, use_container_width=True)
    st.markdown("""
- 阴影区表示对应类型「在最优情形下」愿意承受的最大投入水平
- 黑线表示被追求方的接受策略
- 圆点位置反映均衡下各类型的实际选择
""")

st.divider()

with st.expander("项目说明"):
    st.markdown("""
本项目以 Spence (1973) 信号博弈理论为基础,在恋爱场景中演示该机制的均衡解。
Spence 的原始研究关注劳动力市场中的教育信号问题,
并于 2001 年因此获得诺贝尔经济学奖。
其抽象化的博弈结构可以应用于任何「一方拥有私有信息、另一方依据可观察行为做推断」
的场景,恋爱仅是其中之一。

本项目展示的不仅是均衡的存在性,更是该理论对现实现象的解释力。
例如「为什么真心人会过度投入」、「备胎现象的市场结构性解释」、
「为什么对方的忽冷忽热反而强化了被追求方的判断难度」等问题,
都可以在此框架内得到精确的数学描述。
""")

with st.expander("数学背景"):
    st.markdown(r"""
本项目实现的是离散两类型、连续信号空间下的标准信号博弈模型。

**玩家**:发送者 A(追求方)、接收者 B(被追求方)

**类型空间**:A 的私有类型 $t \in \{S, C\}$,先验 $P(t=S) = p_0$

**信号空间**:A 选择投入度 $s \in [0, +\infty)$

**效用函数**:
- $U_A(t, s, a) = a \cdot b(t) - c(t) \cdot s$
- $U_B(t, a) = a \cdot v(t)$

**关键假设**:Single-Crossing Condition,$c(S) < c(C)$
(更准确的形式:$\text{MRS}_S > \text{MRS}_C$)

**求解方法**:完美贝叶斯均衡 (PBE) 配合 Cho-Kreps 直觉准则精炼

**三种均衡形式**:
- 分离均衡 (LCSE):$s^* = b(C)/c(C)$
- 混同均衡:$s = 0$,存在条件 $p_0 > \mu^* = -v(C) / (v(S) - v(C))$
- 半分离均衡:$S$ 选 $s_h$、$C$ 以概率 $q$ 模仿,存在条件 $p_0 < \mu^*$ + SCC
""")
    st.markdown("**当前参数下的关键值:**")
    col1, col2, col3 = st.columns(3)
    col1.metric("μ* (接受阈值)", f"{mu_star(params):.4f}")
    col2.metric("MRS_S", f"{mrs_S(params):.4f}")
    col3.metric("MRS_C", f"{mrs_C(params):.4f}")

with st.expander("模型局限"):
    st.markdown("""
本模型为简化建模,呈现的是核心机制而非全貌。其主要简化包括:

- 类型空间为离散二元(认真 / 不认真),现实中是连续光谱
- 信号为一维标量,现实中包含多维度(时间、金钱、情感投入等)
- 效用函数为线性形式
- 单期博弈,未考虑动态多轮的关系演化
- 双方完全理性,不考虑情绪与认知偏差

放松这些假设可得到更复杂的模型(连续类型空间、多维信号、动态博弈、行为博弈等),
也是博弈论与信息经济学的活跃研究方向。

本项目仅用于理论机制的演示,不应作为对具体关系的预测或建议工具。
""")

with st.expander("参考文献"):
    st.markdown("""
1. Spence, M. (1973). Job Market Signaling. *Quarterly Journal of Economics* 87(3): 355-374.

2. Cho, I.-K., & Kreps, D. M. (1987). Signaling Games and Stable Equilibria.
   *Quarterly Journal of Economics* 102(2): 179-221.

3. Sobel, J. (2009). Signaling Games. In *Encyclopedia of Complexity and Systems Science*.

4. Mas-Colell, A., Whinston, M. D., & Green, J. R. (1995).
   *Microeconomic Theory*, Chapter 13. Oxford University Press.
""")

st.divider()

st.caption("""
**操作提示**:拖动左侧任意滑块,页面将实时更新均衡分析。可尝试以下参数组合:

- 「对方的初始信任度」调至 0.7 → 进入混同均衡
- 「对方的初始信任度」调至 0.2 → 进入半分离均衡(对应备胎现象)
- 「不认真型每单位投入的痛苦感」调至接近认真型水平 → 信号失效,分离均衡崩溃
""")

st.markdown("""
---

*本项目为应用数学专业一年级本科生的兴趣作品。模型为简化建模,
旨在演示博弈论对现实场景的解释力,不构成任何恋爱建议。*

*源代码:[GitHub](https://github.com/EddieR314/dating-signaling-game)*
""")
