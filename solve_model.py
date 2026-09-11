# -*- coding: utf-8 -*-
"""
药材烘干模型：问题1 / 问题2、3 / 问题4 通用模板
--------------------------------------------------
核心思想：公式体完全一样，只有"物性怎么取"随题目变化。
   题1：rho,cp,k 是常数，D 只依赖 C
   题2/3：rho,cp,k 依赖 C，D 依赖 C 和 T
   题4：同题2/3，但系数不同（且半径收缩，本模板未含）
"""
import math
import numpy as np
import openpyxl

# ==================== 1. 读附件1，插值到每秒 ====================
def load_air(path='A题/附件/附件1.xlsx'):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = [r for i, r in enumerate(ws.iter_rows(values_only=True)) if i > 0]
    T60 = [r[1] for r in rows]
    C60 = [r[2] for r in rows]
    T1, C1 = [T60[0]], [C60[0]]
    for k in range(1, len(T60)):
        for j in range(1, 61):
            T1.append(T60[k-1] + (T60[k] - T60[k-1]) * j / 60)
            C1.append(C60[k-1] + (C60[k] - C60[k-1]) * j / 60)
    return T1, C1

T_AIR, C_AIR = load_air()

def env(t):
    """环境条件。附件1 只到 14400 s，之后进入恒温干燥阶段（数据平台值）"""
    ti = int(round(t))
    if ti <= 14400:
        return T_AIR[ti], C_AIR[ti]
    return 50.0, 0.05

# ==================== 2. 物性：唯一随题目变化的地方 ====================
def props_arr(problem, C, T_C):
    """返回逐点的 (rho, cp, k, D)。输入输出都是 numpy 数组。"""
    C = np.maximum(C, 1e-9)
    if problem == 1:                                  # 附录2
        D = 7e-9 * np.exp(-0.89 / C)
        return (np.full_like(C, 820.0), np.full_like(C, 2600.0),
                np.full_like(C, 0.36), D)
    TK = T_C + 273.15                                 # 开尔文！
    if problem in (2, 3):                             # 附录3
        rho = 650 + 128 * C
        cp  = 1450 + 2736 * C / (C + 1)
        k   = 0.21 + 0.38 * C / (C + 1)
        D   = 2.4e-3 * np.exp(-0.45 / C) * np.exp(-3850 / TK)
        return rho, cp, k, D
    rho = 760 + 90 * C                                # 附录4（问题4）
    cp  = 1850 + 2150 * C / (C + 1)
    k   = 0.12 + 0.20 * C / (C + 1)
    D   = 4.2e-4 * np.exp(-0.30 / C) * np.exp(-3850 / TK)
    return rho, cp, k, D

# ==================== 3. 求解器：一套公式通吃 ====================
def solve(problem, t_end, dt=1.0, N=20, R=0.02,
          h=25.0, hm=8e-7, C_init=2.55, T_init=28.0,
          stop_at=None, T_air_func=None):
    dr = R / N
    r  = np.arange(N + 1) * dr
    T  = np.full(N + 1, T_init)
    C  = np.full(N + 1, C_init)
    envf = T_air_func if T_air_func is not None else env

    nstep = int(round(t_end / dt))
    for n in range(nstep):
        t = n * dt
        Ta, Ca = envf(t)

        # ---------- 温度：用当前的 C 取物性 ----------
        rho, cp, k, _ = props_arr(problem, C, T)
        kR = 0.5 * (k[1:-1] + k[2:])         # 界面 i+1/2 （只取内部点 i=1..N-1）
        kL = 0.5 * (k[1:-1] + k[:-2])        # 界面 i-1/2
        Tn = T.copy()
        T[1:-1] = Tn[1:-1] + dt / (rho[1:-1] * cp[1:-1] * r[1:-1] * dr) * (
            (r[1:-1] + dr/2) * kR * (Tn[2:]   - Tn[1:-1]) / dr
          - (r[1:-1] - dr/2) * kL * (Tn[1:-1] - Tn[:-2])  / dr)
        kh = 0.5 * (k[0] + k[1])
        T[0] = Tn[0] + 4 * kh * dt * (Tn[1] - Tn[0]) / (rho[0] * cp[0] * dr**2)
        T[N] = Tn[N] + dt / (rho[N] * cp[N]) * (
            2 * k[N] * (Tn[N-1] - Tn[N]) / dr**2
          - 2 * h    * (Tn[N]   - Ta)    / dr)

        # ---------- 水分：用刚更新好的 T 取 D ----------
        _, _, _, D = props_arr(problem, C, T)
        DR = 0.5 * (D[1:-1] + D[2:])
        DL = 0.5 * (D[1:-1] + D[:-2])
        Cn = C.copy()
        C[1:-1] = Cn[1:-1] + dt / (r[1:-1] * dr) * (
            (r[1:-1] + dr/2) * DR * (Cn[2:]   - Cn[1:-1]) / dr
          - (r[1:-1] - dr/2) * DL * (Cn[1:-1] - Cn[:-2])  / dr)
        Dh = 0.5 * (D[0] + D[1])
        C[0] = Cn[0] + 4 * Dh * dt * (Cn[1] - Cn[0]) / dr**2
        C[N] = Cn[N] + dt * (
            2 * D[N] * (Cn[N-1] - Cn[N]) / dr**2
          - 2 * hm   * (Cn[N]   - Ca)    / dr)

        if stop_at is not None and C.max() < stop_at:
            return T, C, (n + 1) * dt
    return T, C, t_end

# ==================== 4. 自检 ====================
if __name__ == '__main__':
    print('=== 问题1（附录2）3小时内的抽取点 ===')
    T1, C1, _ = solve(1, 1800)
    for idx, rc in [(0,'0'), (5,'0.5'), (10,'1.0'), (15,'1.5'), (20,'2.0')]:
        print('r=%s cm : T=%.4f  C=%.4f' % (rc, T1[idx], C1[idx]))

    print()
    print('=== 问题2（附录3）跑到烘干合格 ===')
    T2, C2, tdry = solve(2, 600000, stop_at=0.15)
    print('烘干结束时间 = %d s = %.2f h = %.2f 天' % (tdry, tdry/3600, tdry/86400))
    print('结束时 C: 中心=%.4f 表面=%.4f' % (C2[0], C2[-1]))
