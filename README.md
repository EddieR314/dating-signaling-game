# dating-signaling-game v1 — 核心算法实现

> v1 第一阶段：用 Python 实现信号博弈的均衡求解器。
> 完成这一步后，我们再加 Streamlit UI。

---

## 你现在拿到了什么

```
dating-signaling-v1/
├── equilibrium.py         # 主代码：4 个 TODO 等你实现
├── test_equilibrium.py    # 测试用例：17 个，全部期望输出已手算
└── README.md              # 本文件
```

---

## 今晚的目标

**不是做完 v1，是做完一件事**：

> 把 4 个 TODO 函数写完，跑 `pytest` 看到 17 个测试全过。

预估时间：**1.5 - 3 小时**（取决于你对 Python 的熟练度和卡多久）。

做不完没关系，**做卡了来找我**。

---

## 第一步：装 Python 环境

如果你已经有 Python 3.9+ 的环境，跳过这步。

### 检查你有没有 Python

打开命令行（macOS / Linux 是 Terminal、Windows 是 cmd 或 PowerShell），输入：

```bash
python --version
```

或者：

```bash
python3 --version
```

如果显示版本号 ≥ 3.9（比如 `Python 3.11.5`），✅ 通过。

如果提示找不到命令，去 [python.org](https://www.python.org/downloads/) 下载安装最新版。

### 装 pytest

唯一需要的依赖。终端里跑：

```bash
pip install pytest
```

或者：

```bash
pip3 install pytest
```

---

## 第二步：把这三个文件放到一个文件夹

随便挑个位置，比如桌面新建一个文件夹叫 `dating-signaling-v1`，把 `equilibrium.py`、`test_equilibrium.py`、`README.md` 都放进去。

终端进入这个文件夹：

```bash
cd 你放文件的路径
```

---

## 第三步：先跑一次测试，看看初始状态

```bash
python -m pytest test_equilibrium.py -v
```

应该看到：
- 3 个**辅助函数测试**通过（`test_mu_star_standard`、`test_mrs_S_standard`、`test_mrs_C_standard`）—— 因为这些函数我已经实现
- 14 个**核心算法测试**报错（`NotImplementedError`）—— 因为 4 个 TODO 还没实现

**这是预期的**。看到这个状态说明环境装对了。

---

## 第四步：按顺序填 4 个 TODO

打开 `equilibrium.py`，找到 4 个标记为 `# TODO` 的函数，**按顺序**实现：

### TODO 1: `check_scc`（最简单，预计 5 分钟）

只要返回 `MRS_S > MRS_C`。**一行就够**。

写完后跑：

```bash
python -m pytest test_equilibrium.py::test_check_scc_standard -v
python -m pytest test_equilibrium.py::test_check_scc_violated -v
python -m pytest test_equilibrium.py::test_check_scc_boundary -v
```

三个都过了再继续。

### TODO 2: `solve_separating`（预计 15-30 分钟）

按函数文档里的步骤来：
1. 用 `check_scc` 检查
2. 算 `s_star = mrs_C(params)`
3. 算各方福利
4. 构造并返回 `SeparatingEquilibrium` 对象

**Python 提示** — 怎么构造对象：

```python
return SeparatingEquilibrium(
    s_S=s_star,
    s_C=0.0,
    accept_threshold=s_star,
    welfare_AS=...,
    welfare_AC=...,
    welfare_B=...,
)
```

写完跑相关测试：

```bash
python -m pytest test_equilibrium.py -k separating -v
```

### TODO 3: `solve_pooling`（预计 15 分钟）

逻辑类似但更简单。**注意是严格不等式 `p0 > μ*`，不是 `>=`**。

写完跑：

```bash
python -m pytest test_equilibrium.py -k pooling -v
```

### TODO 4: `solve_semi_separating`（预计 30-60 分钟，最难）

按文档里的步骤来。注意：
- 公式有点多，但都给你了，逐步代入
- 检查 q 在 (0, 1) 之间，否则返回 None
- 检查 r 在 (0, 1] 之间（半开半闭），否则返回 None

写完跑：

```bash
python -m pytest test_equilibrium.py -k semi -v
```

### 全部通过后

```bash
python -m pytest test_equilibrium.py -v
```

应该看到 **17 passed**。✅

也可以直接运行 `equilibrium.py` 看输出：

```bash
python equilibrium.py
```

会打印标准参数下的均衡求解结果。

---

## 卡住了怎么办

### "Python 报错 SyntaxError"

语法错了。常见的：
- 忘了写冒号 `:`（Python 函数定义、if、for 都要）
- 缩进不一致（Python 用缩进表示代码块，每层 4 空格，不要混用 Tab）
- 括号没配对

### "测试失败但我觉得我写对了"

1. 看具体哪个用例失败、对比期望值和实际值
2. 把那组参数手算一遍（参考第七块讲解）
3. 注意**严格不等式 vs 非严格不等式**——这是最常见的错误

### "我不知道怎么访问对象的字段"

```python
params = GameParams(p0=0.4, b_S=4, ...)
print(params.p0)        # 输出 0.4，注意是点不是方括号
print(params.b_S)       # 输出 4
```

### "我不会用 dataclass"

不需要会。你只需要：
- **读取**字段：`params.p0`
- **构造**对象：`SeparatingEquilibrium(s_S=..., s_C=..., ...)`

就这两个操作，会就够了。

### "卡住超过 30 分钟"

回到对话来找我。把:
- 你卡住的具体函数
- 测试报错的输出（复制粘贴）
- 你当前的代码

都发给我。**不要硬撑**——卡住的成本远超问问题的成本。

---

## 完成的标志

- 4 个 TODO 函数都实现了
- `python -m pytest test_equilibrium.py -v` 显示 **17 passed**
- 你能用自己的话讲清楚每个函数在做什么

完成后告诉我，我们进下一步：**用 Streamlit 把这套算法包成可视化网页**。

---

## 一些工程小提示

1. **保持代码简洁** — 每个函数本质都是几行数学运算。如果你写得很长，多半是哪里搞复杂了。
2. **不要修改 `test_equilibrium.py`** — 测试用例是你代码正确性的"裁判"。
3. **不要修改类型定义和已实现的辅助函数** — 这些是契约。
4. **别一次性写完 4 个再跑测试** — 一个一个写、一个一个跑测试。
5. **报错信息是你的朋友** — Python 的报错通常会告诉你哪行有问题，认真读。

---

加油 — 这一步过了，你就完成了 v1 最重要的一块。

**关键提醒**: 这一步你做完之后，**整个 v1 项目数学层的工作就都结束了**。
后面 Streamlit UI 部分会简单得多——大概只需要再花一两天。
