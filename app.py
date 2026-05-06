"""
约会信号博弈可视化 — Streamlit 应用主文件

跑这个文件:
    streamlit run app.py

启动后浏览器会自动打开 http://localhost:8501
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib

from equilibrium import (
    GameParams,
    mu_star, mrs_S, mrs_C,
    solve_all,
    SeparatingEquilibrium,
    PoolingEquilibrium,
    SemiSeparatingEquilibrium,
)

# 页面基础配置
st.set_page_config(
    page_title="真心还是套路?",
    page_icon="💕",
    layout="wide",
)

# 中文字体
matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"
]
matplotlib.rcParams["axes.unicode_minus"] = False

# 默认参数
DEFAULTS = {
    "p0": 0.40, "b_S": 4.0, "b_C": 2.0,
    "c_S": 0.5, "c_C": 1.0, "v_S": 3.0, "v_C": -2.0,
}

# ============================================================
# 顶部
# ============================================================

st.title("💕 真心还是套路?")
st.markdown("**用诺贝尔经济学奖得主的理论,看清追求中的「投入」到底在传递什么信号**")

st.markdown("""
在追求一段关系时,你不知道对方是真心还是只是好奇试探。
你也无法直接告诉对方「我是认真的」——这句话太便宜,谁都能说。

但**行为不一样**。三年的坚持、攒够半年生活费去异地找 ta、顶着考试压力连续一个月接 ta 下晚自习——
这些是有「成本」的,而且**不同动机的人付出的成本不一样**。

这个简单的不对称,能解释你身边几乎所有恋爱故事的走向。
""")

st.divider()

# ============================================================
# 侧边栏
# ============================================================

with st.sidebar:
    st.header("🎛️ 参数面板")
    st.caption("拖动滑块,右侧实时更新均衡分析。")

    if st.button("🔄 恢复默认值"):
        for key, val in DEFAULTS.items():
            st.session_state[key] = val
        st.rerun()

    st.divider()

    p0 = st.slider(
        "对方的初始信任度",
        min_value=0.05, max_value=0.95, step=0.05,
        value=st.session_state.get("p0", DEFAULTS["p0"]),
        key="p0",
    )
    with st.expander("这是什么?"):
        st.markdown("""
还没看到任何追求行为之前,对方对「追求者是认真的」的初始判断。

较高代表 ta 在一个高信任的环境(比如熟人介绍、小圈子),
较低代表 ta 在一个鱼龙混杂的环境(比如交友软件、陌生人圈子)。
""")

    st.markdown("---")

    b_S = st.slider(
        "认真型从被接受获得的价值",
        min_value=0.5, max_value=5.0, step=0.1,
        value=st.session_state.get("b_S", DEFAULTS["b_S"]),
        key="b_S",
    )
    with st.expander("这是什么?"):
        st.markdown("""
一个「认真追求者」如果被接受了,能从这段关系中得到的整体价值。

高表示这段关系对 ta 极其重要,低表示也想要但没那么强烈。
""")

    b_C = st.slider(
        "不认真型从被接受获得的价值",
        min_value=0.5, max_value=5.0, step=0.1,
        value=st.session_state.get("b_C", DEFAULTS["b_C"]),
        key="b_C",
    )
    with st.expander("这是什么?"):
        st.markdown("""
一个「不太认真的追求者」如果被接受了,能从中获得的价值。

注意这个值通常**小于**认真型——因为不认真的人对这段关系本来就没那么在乎。
""")

    if b_C >= b_S:
        st.warning("⚠️ 通常假设认真型对这段关系更看重。当前设置颠倒了这一假设。")

    st.markdown("---")

    c_S = st.slider(
        "认真型每单位投入的痛苦感",
        min_value=0.1, max_value=2.0, step=0.05,
        value=st.session_state.get("c_S", DEFAULTS["c_S"]),
        key="c_S",
    )
    with st.expander("这是什么?"):
        st.markdown("""
认真追求者每「投入一份」(一次约会、一份心意、一段付出)的主观成本。

较低代表「陪你做什么都不累、心里甜」,较高代表「虽然认真但也累」。
""")

    c_C = st.slider(
        "不认真型每单位投入的痛苦感",
        min_value=0.1, max_value=2.0, step=0.05,
        value=st.session_state.get("c_C", DEFAULTS["c_C"]),
        key="c_C",
    )
    with st.expander("这是什么?"):
        st.markdown("""
不认真追求者每「投入一份」的主观成本。

通常**大于**认真型——因为做自己心不在焉的事,本身就是煎熬。

这两个数字的差距,是整个理论的发动机:差距越大,「投入」越能区分真假。
""")

    if c_C <= c_S:
        st.warning("⚠️ 通常假设不认真者付出的痛苦感更大(理论的核心假设)。当前设置违反了这一假设。")

    st.markdown("---")

    v_S = st.slider(
        "被追求方接受「认真型」的价值",
        min_value=0.5, max_value=5.0, step=0.1,
        value=st.session_state.get("v_S", DEFAULTS["v_S"]),
        key="v_S",
    )
    with st.expander("这是什么?"):
        st.markdown("""
对方如果接受了一个真正认真的追求者,能从这段关系中获得的价值。

这是个正数——大家都想要真心。
""")

    v_C = st.slider(
        "被追求方接受「不认真型」的损失",
        min_value=-5.0, max_value=-0.5, step=0.1,
        value=st.session_state.get("v_C", DEFAULTS["v_C"]),
        key="v_C",
    )
    with st.expander("这是什么?"):
        st.markdown("""
对方如果误接受了一个不认真的追求者,会蒙受的损失(情感伤害、时间浪费等)。

这是个**负数**——被骗了肯定亏。
""")

# 求解均衡
params = GameParams(p0=p0, b_S=b_S, b_C=b_C, c_S=c_S, c_C=c_C, v_S=v_S, v_C=v_C)
equilibria = solve_all(params)

# ============================================================
# 主显示区
# ============================================================

def render_separating(eq: SeparatingEquilibrium):
    st.markdown("### 🟢 当前市场状态:分离均衡")
    col1, col2, col3 = st.columns(3)
    col1.metric("认真型最优投入度", f"{eq.s_S:.2f}")
    col2.metric("不认真型最优投入度", f"{eq.s_C:.2f}")
    col3.metric("接受门槛", f"{eq.accept_threshold:.2f}")

    st.markdown(f"""
在当前参数下,市场达到了一种「清爽」的平衡:

**认真追求者**会投入 **{eq.s_S:.2f} 单位**——这不是凭运气定的数字,
是「刚好让不认真者放弃伪装」的最低投入。

**不认真追求者**会选择不投入。原因是:他们如果模仿认真者的高投入,
付出的成本会超过被接受能拿到的好处。**伪装不划算,所以他们自动放弃。**

**对方**看到投入达到 {eq.accept_threshold:.2f} 就接受、低于就拒绝。
这个判断不需要看任何「内心」——光看行为就能区分。

这种均衡常常对应「追了很久才在一起」的恋爱故事——比如那种从大一追到大三的故事。
那个「很久」不是浪费时间,是数学上必要的「信号成本」,它让真心被识别出来。
""")

    with st.expander("📊 看一下双方的具体福利"):
        st.markdown(f"""
在这个均衡下:
- **认真追求者**效用:{eq.welfare_AS:.2f}
- **不认真追求者**效用:{eq.welfare_AC:.2f}(没投入、被拒绝)
- **对方**期望效用:{eq.welfare_B:.2f}
""")


def render_pooling(eq: PoolingEquilibrium):
    st.markdown("### 🟡 当前市场状态:混同均衡(高信任市场)")
    col1, col2 = st.columns(2)
    col1.metric("共同投入度", f"{eq.s_pooled:.2f}")
    col2.metric("接受率", "100%")

    st.markdown("""
在当前参数下,市场进入「无需信号」的状态:

**不管认真还是不认真**,追求者都会选择零投入——因为「投入」传递不了任何信息,
对方的信任已经足够高,不需要看行为也愿意接受。

**对方**会无差别接受所有追求。这看起来很好——配对效率高、没人浪费时间。
但代价是:**配对质量没有保证**,可能接受到的是不认真的人。

这种均衡常常出现在「熟人介绍」、「小圈子约会」这种环境里——大家彼此熟悉、信任度天然很高,
确实不需要「用行动证明」。

但当市场扩大、陌生人变多,这种均衡会崩溃——后面那两种均衡会接管。
""")

    with st.expander("📊 看一下双方的具体福利"):
        st.markdown(f"""
在这个均衡下:
- **认真追求者**效用:{eq.welfare_AS:.2f}(被接受、零投入)
- **不认真追求者**效用:{eq.welfare_AC:.2f}(被接受、零投入)
- **对方**期望效用:{eq.welfare_B:.2f}
""")


def render_semi_separating(eq: SemiSeparatingEquilibrium):
    st.markdown("### 🔴 当前市场状态:半分离均衡(鱼龙混杂)")
    col1, col2, col3 = st.columns(3)
    col1.metric("认真型投入度", f"{eq.s_h:.2f}")
    col2.metric("不认真型伪装率", f"{eq.q*100:.1f}%")
    col3.metric("被追求方接受率", f"{eq.r*100:.1f}%")

    st.markdown(f"""
在当前参数下,市场处于最贴近现实的混乱状态:

**认真追求者**仍然投入到高水平({eq.s_h:.2f})。

**不认真追求者**会以一定概率(这里是 {eq.q*100:.1f}%)伪装成认真者——
他们也投入高水平,赌对方接受。剩下 {(1-eq.q)*100:.1f}% 的不认真者会摆烂、零投入。

**对方**看到高投入时也无法 100% 确定——可能是真心,可能是装的。
所以接受是一种「赌博」。

这种均衡对应**「备胎现象」在博弈论里的精确解释**:

不是「渣男渣女道德败坏」,是当**信任度不够高**时,
一部分不认真者发现「假装认真」赌一把仍然有利可图,
于是市场上同时存在真心追求者、伪装者、半信半疑接受者、果断拒绝者。

这是市场的均衡状态,不是「出了 bug」。要让它消失,需要要么**提高信任度**
(参数面板里第一个滑块),要么**让伪装更痛苦**(拉大两种类型的成本差距)。
""")

    with st.expander("📊 看一下双方的具体福利"):
        st.markdown(f"""
在这个均衡下:
- **认真追求者**效用:{eq.welfare_AS:.2f}
- **不认真追求者**效用:{eq.welfare_AC:.2f}(在两种选择间无差异)
- **对方**期望效用:{eq.welfare_B:.2f}
""")


# 显示均衡
if not equilibria:
    st.markdown("### ❓ 当前参数下,标准均衡形式都不存在")
    st.markdown("""
这种参数设置非常特殊,可能违反了模型的基本假设。

试着拉动滑块,让「认真型成本 < 不认真型成本」,并让「信任度」在合理范围内。
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
    st.markdown("### ⚖️ 当前参数下,多种均衡同时存在")
    st.markdown("""
这是博弈论里特有的现象——同一组「游戏规则」下,可能有多种稳定的「游戏结果」。

市场最终停在哪一种,取决于历史、文化、第一批参与者的行为模式等「非理性」因素。

你正在看到的均衡有:
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

# ============================================================
# 主图
# ============================================================

st.divider()
st.subheader("📈 信号 vs 接受概率")


def make_main_chart(params: GameParams, equilibria):
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
        ax.plot([threshold, s_max], [1, 1], color="black", linewidth=2,
                label="对方的接受策略")
        ax.scatter([main_eq.s_S], [1], color="blue", s=200, zorder=5,
                   label=f"认真型选择 (s = {main_eq.s_S:.2f})",
                   edgecolors="white", linewidth=2)
        ax.scatter([main_eq.s_C], [0], color="red", s=200, zorder=5,
                   label=f"不认真型选择 (s = {main_eq.s_C:.2f})",
                   edgecolors="white", linewidth=2)
    elif isinstance(main_eq, PoolingEquilibrium):
        ax.plot([0, s_max], [1, 1], color="black", linewidth=2,
                label="对方的接受策略 (全接受)")
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
                   label=f"认真型选择 (s = {main_eq.s_h:.2f})",
                   edgecolors="white", linewidth=2)
        ax.scatter([0], [0], color="red", s=150, zorder=5, alpha=0.5,
                   label=f"不认真型: {(1-main_eq.q)*100:.0f}% 选 0",
                   edgecolors="white", linewidth=2)
        ax.scatter([main_eq.s_h], [main_eq.r * 0.5], color="red", s=150,
                   zorder=5, marker="^",
                   label=f"不认真型: {main_eq.q*100:.0f}% 伪装",
                   edgecolors="white", linewidth=2)

    ax.set_xlabel("投入度 s", fontsize=12)
    ax.set_ylabel("接受概率", fontsize=12)
    ax.set_xlim(-0.2, s_max)
    ax.set_ylim(-0.1, 1.2)
    ax.legend(loc="center right", fontsize=9)
    ax.grid(True, alpha=0.3)

    return fig


fig = make_main_chart(params, equilibria)
st.pyplot(fig, use_container_width=True)

st.markdown("""
这张图把「博弈结局」画在了一起。看圆点的位置:

- **蓝色圆点**是认真型选择的投入水平
- **红色圆点**是不认真型选择的投入水平
- **黑线**是对方的接受策略——投入到了门槛上方就接受

当蓝点和红点分开时(一在高、一在 0),说明信号成功区分了类型。
""")

# ============================================================
# 折叠面板
# ============================================================

st.divider()

with st.expander("📖 这个项目想做什么"):
    st.markdown("""
这是一个把博弈论搬进恋爱场景的可视化教学工具。

它基于 Spence (1973) 的信号博弈理论——一个让 Spence 在 2001 年获得诺贝尔经济学奖的工作。
Spence 原本研究的是「教育与求职」,但同样的数学结构可以解释**任何「一方有信息、另一方靠观察行为来猜」的场景**。
恋爱只是其中之一。

你在这里能看到的不只是「哪种均衡存在」,而是这个理论**对现实的解释力**——
为什么真心人会「过度投入」、为什么「备胎现象」是市场结构问题不是道德问题、
为什么对方「忽冷忽热」反而让你更上头有数学基础。
""")

with st.expander("🧮 数学背景(给想深挖的人)"):
    st.markdown(r"""
本项目实现的是离散两类型、连续信号空间下的标准信号博弈模型。

**玩家**:发送者 A(追求方)、接收者 B(被追求方)

**类型空间**:A 私有类型 $t \in \{S, C\}$,先验 $P(t=S) = p_0$

**信号空间**:A 选择投入度 $s \in [0, +\infty)$

**效用函数**:
- $U_A(t, s, a) = a \cdot b(t) - c(t) \cdot s$
- $U_B(t, a) = a \cdot v(t)$

**关键假设**:Single-Crossing Condition,$c(S) < c(C)$(更准确:$\text{MRS}_S > \text{MRS}_C$)

**求解**:完美贝叶斯均衡 + Cho-Kreps 直觉准则精炼

**三种均衡**:
- 分离均衡 (LCSE):$s^* = b(C)/c(C)$
- 混同均衡:$s = 0$,存在条件 $p_0 > \mu^* = -v(C) / (v(S) - v(C))$
- 半分离均衡:S 选 $s_h$、C 以概率 $q$ 模仿,存在条件 $p_0 < \mu^*$ + SCC
""")

    st.markdown("**当前参数下的关键值**:")
    col1, col2, col3 = st.columns(3)
    col1.metric("μ* (接受阈值)", f"{mu_star(params):.4f}")
    col2.metric("MRS_S", f"{mrs_S(params):.4f}")
    col3.metric("MRS_C", f"{mrs_C(params):.4f}")

with st.expander("⚠️ 模型局限性"):
    st.markdown("""
这个模型有意做了大量简化,用最干净的数学结构呈现核心机制。它不是恋爱建议工具。

主要简化包括:
- 类型只分两种(「认真」vs「不认真」),现实中是连续光谱
- 投入是一维标量,现实中包含时间、金钱、情感等多维度
- 效用函数线性,现实中可能凸或凹
- 单期博弈,现实中是动态多轮的
- 双方完全理性,现实中有情绪、偏见、非理性

把这些放松后会得到更复杂的版本——更接近现实,也更难求解。
这些扩展是博弈论的活跃研究方向。

**核心提示**:模型是用来理解机制的,不是用来预测具体关系的。
「我和 ta 现在是分离均衡」这种说法没有意义。
""")

with st.expander("📚 参考文献"):
    st.markdown("""
1. **Spence, M. (1973).** Job Market Signaling. *QJE* 87(3): 355-374.

   (信号博弈的开山之作。Spence 因这条研究获 2001 年诺贝尔经济学奖。)

2. **Cho, I.-K. & Kreps, D. M. (1987).** Signaling Games and Stable Equilibria. *QJE* 102(2): 179-221.

   (引入「直觉准则」——本项目用来精炼分离均衡的工具。)

3. **Sobel, J. (2009).** Signaling Games. In *Encyclopedia of Complexity and Systems Science*.

   (信号博弈的现代综述,适合深入。)

4. **Mas-Colell, Whinston & Green (1995).** *Microeconomic Theory*, Ch. 13.

   (博弈论标准教科书。)
""")

# ============================================================
# 页脚
# ============================================================

st.divider()

st.caption("""
💡 **提示**:拖动左侧任意滑块,整个页面会瞬间重新计算。试试这些有意思的参数组合:

- 把「对方的初始信任度」调到 0.7 → 进入混同均衡
- 把「对方的初始信任度」调到 0.2 → 进入半分离均衡(备胎现象)
- 把「不认真型每单位投入的痛苦感」调低到接近认真型 → 信号失效,分离均衡崩溃
""")

st.markdown("""
---

*本项目是应用数学专业一年级本科生的兴趣作品。模型为简化建模,
旨在说明博弈论的现实解释力,**不构成任何恋爱建议**。*

*源代码与详细数学推导:[GitHub 链接(待填)]*
""")
