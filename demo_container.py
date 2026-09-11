# -*- coding: utf-8 -*-
"""
一个能看懂的迷你示例：换"容器"不用改"公式"
==========================================
只做两件事：
  1) 让你看清 list 和 numpy 数组的读写方式一模一样
  2) 用同一套公式体跑两种容器，证明结果完全一致
"""
import numpy as np

# ==========================================================
# 第 1 步：两种容器长什么样
# ==========================================================
print('---------- 第 1 步：两种容器 ----------')

# 旧办法：嵌套 list（要写循环，行数写死）
def 造list容器(行数, 列数):
    容器 = []
    for t in range(行数):
        容器.append([0.0] * 列数)
    return 容器

# 新办法：numpy（一行）
a = 造list容器(3, 4)          # 3 行 4 列
b = np.zeros((3, 4))          # 3 行 4 列

print('a 是', type(a).__name__, '  b 是', type(b).__name__)

# 两种容器的读写方式完全相同
a[1][2] = 7.5
b[1][2] = 7.5
print('读出来:', a[1][2], b[1][2], ' -> 一模一样')
print()

# ==========================================================
# 第 2 步：同一套公式，跑两种容器
# ==========================================================
print('---------- 第 2 步：同一套公式 ----------')

# 迷你物理问题：4 个格点，算 5 步
# 规则随便定（就是"每个点被左右邻居拉平"），只看代码形状
def 计算(造容器):
    T = 造容器(6, 4)              # 6 个时刻 x 4 个位置

    # --- 初始化：第 0 行 ---
    for r in range(4):
        T[0][r] = 0.0
    T[0][3] = 100.0               # 最右边给个初值

    # --- 公式体：下面这些行，两种容器都是同一份代码 ---
    for t in range(5):
        for r in range(4):
            if r == 0:
                T[t+1][r] = T[t][r] + 0.1 * (T[t][r+1] - T[t][r])
            elif r == 3:
                T[t+1][r] = T[t][r] + 0.1 * (T[t][r-1] - T[t][r])
            else:
                T[t+1][r] = T[t][r] + 0.1 * (T[t][r+1] - 2*T[t][r] + T[t][r-1])
    return T

def 造list(行数, 列数):
    return [[0.0] * 列数 for _ in range(行数)]

def 造numpy(行数, 列数):
    return np.zeros((行数, 列数))

结果1 = 计算(造list)
结果2 = 计算(造numpy)

print('list 容器最后一行:', [round(v, 4) for v in 结果1[5]])
print('numpy容器最后一行:', [round(float(v), 4) for v in 结果2[5]])
print('-> 一模一样，说明公式体不用改')
print()

# ==========================================================
# 第 3 步：对应到你自己的代码，只改这 3 处
# ==========================================================
print('---------- 第 3 步：你要改的地方 ----------')
print('''
原来（写死行数 + 嵌套list）：
    def create_object(object):
        for t in range(1801):          <-- 问题2 要 20 万行，装不下
            row = [0]
            object.append(row)
            for r in range(20):
                line = [0]
                object[t].append(line)
        return object

    object_t, object_c = [], []
    object_t = create_object(object_t)
    object_c = create_object(object_c)

    initialize(object_t, T_AIR)        <-- 靠判断"是不是同一个列表"来区分
    initialize(object_c, 2.55)

改成（numpy，行数可以随时调）：
    NSTEP = 250000                     # 问题1写1800，问题2~4写250000

    object_t = np.zeros((NSTEP + 1, 21))
    object_c = np.zeros((NSTEP + 1, 21))

    object_t[0, :] = 28.0              # 药材初温
    object_c[0, :] = 2.55              # 药材初水分

公式部分：一行都不用改！

唯一要小心的地方：
    Tn = object_t[t].copy()            # numpy 的 object_t[t] 是"视图"，
                                       # 想要一份旧值的副本必须加 .copy()
''')
