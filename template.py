# -*- coding: utf-8 -*-
"""
药材烘干 —— 可复用公式模板
================================
问题 1 / 2 / 3 / 4 共用【同一套公式】，
唯一随题目变化的，是第 2 节的 props() 物性函数。
"""
import math
import time
import numpy as np
import openpyxl

# ============================================================
# 0. 常量
# ============================================================
dt = 1.0          # 时间步长 (s)
dr = 0.001        # 空间步长 (m) = 0.1 cm
N  = 20           # 径向分段数 -> 共 21 个点, r[0]=中心, r[N]=表面
h  = 25.0         # 对流换热系数   W/(m^2*K)   （题目只给一次, 四问共用）
hm = 8e-7         # 对流传质系数   m/s         （同上）
T_init = 28.0     # 药材初温 (摄氏度)
C_init = 2.55     # 药材初水分 (kg/kg)

# ============================================================
# 1. 环境条件：读附件1, 线性插值到每秒
# ============================================================
def load_env(path='A题/附件/附件1.xlsx'):
    ws = openpyxl.load_workbook(path, data_only=True).active
    rows = [r for i, r in enumerate(ws.iter_rows(values_only=True)) if i > 0]
    T60 = [r[1] for r in rows]
    C60 = [r[2] for r in rows]
    T, C = [T60[0]], [C60[0]]                    # t=0
    for k in range(1, len(T60)):
        for j in range(1, 61):                   # 每 60 s 之间插 60 个数
            T.append(T60[k-1] + (T60[k] - T60[k-1]) * j / 60)
            C.append(C60[k-1] + (C60[k] - C60[k-1]) * j / 60)
    return T, C

T_AIR, C_AIR = load_env()

def env(t):
    """烘房温度、水分浓度。附件1 只到 14400 s, 之后是恒温干燥阶段"""
    if t <= 14400:
        return T_AIR[t], C_AIR[t]
    return 50.0, 0.05

# ============================================================
# 2. 物性   ★★★ 唯一随题目变化的地方 ★★★
# ============================================================
def props(problem, C, T_C):
    """给定当地水分浓度 C 和温度 T_C(摄氏度), 返回 (rho, cp, k, D)"""
    C = max(C, 1e-9)

    if problem == 1:                                     # 附录2
        rho, cp, k = 820.0, 2600.0, 0.36
        D = 7e-9 * math.exp(-0.89 / C)
        return rho, cp, k, D

    TK = T_C + 273.15                                    # 换成开尔文

    if problem in (2, 3):                                # 附录3
        rho = 650 + 128 * C
        cp  = 1450 + 2736 * C / (C + 1)
        k   = 0.21 + 0.38 * C / (C + 1)
        D   = 2.4e-3 * math.exp(-0.45 / C) * math.exp(-3850 / TK)
        return rho, cp, k, D

    rho = 760 + 90 * C                                   # 附录4 (问题4)
    cp  = 1850 + 2150 * C / (C + 1)
    k   = 0.12 + 0.20 * C / (C + 1)
    D   = 4.2e-4 * math.exp(-0.30 / C) * math.exp(-3850 / TK)
    return rho, cp, k, D

# ============================================================
# 3. 求解器   ★★★ 公式只有这一份, 四个问题共用 ★★★
# ============================================================
def solve(problem, nstep, stop_at=None):
    T = np.zeros((nstep + 1, N + 1))          # 温度场
    C = np.zeros((nstep + 1, N + 1))          # 水分场
    T[0, :] = T_init
    C[0, :] = C_init

    for t in range(nstep):
        Ta, Ca = env(t)

        # ---------- (a) 先算出 21 个点各自的物性 ----------
        rho = [0.0] * (N + 1)
        cp  = [0.0] * (N + 1)
        k   = [0.0] * (N + 1)
        for r in range(N + 1):
            rho[r], cp[r], k[r], _ = props(problem, C[t, r], T[t, r])

        # ---------- (b) 更新温度 ----------
        # 中心 r=0
        kh = 0.5 * (k[0] + k[1])
        T[t+1, 0] = T[t, 0] + 4*kh*dt*(T[t,1] - T[t,0]) / (rho[0]*cp[0]*dr**2)

        # 内部 r=1..N-1
        for r in range(1, N):
            kR = 0.5 * (k[r] + k[r+1])                       # 界面 r+1/2
            kL = 0.5 * (k[r] + k[r-1])                       # 界面 r-1/2
            净流入 = (r+0.5)*dr * kR * (T[t,r+1] - T[t,r]) / dr \
                   - (r-0.5)*dr * kL * (T[t,r]   - T[t,r-1]) / dr
            T[t+1, r] = T[t, r] + dt / (rho[r]*cp[r]*(r*dr)*dr) * 净流入

        # 表面 r=N
        T[t+1, N] = T[t, N] + dt/(rho[N]*cp[N]) * (
              2*k[N]*(T[t,N-1] - T[t,N])/dr**2
            - 2*h   *(T[t,N]   - Ta)   /dr )

        # ---------- (c) 用刚更新好的温度算 D ----------
        D = [0.0] * (N + 1)
        for r in range(N + 1):
            D[r] = props(problem, C[t, r], T[t+1, r])[3]

        # ---------- (d) 更新水分 ----------
        Dh = 0.5 * (D[0] + D[1])
        C[t+1, 0] = C[t, 0] + 4*Dh*dt*(C[t,1] - C[t,0]) / dr**2

        for r in range(1, N):
            DR = 0.5 * (D[r] + D[r+1])
            DL = 0.5 * (D[r] + D[r-1])
            净流入 = (r+0.5)*dr * DR * (C[t,r+1] - C[t,r]) / dr \
                   - (r-0.5)*dr * DL * (C[t,r]   - C[t,r-1]) / dr
            C[t+1, r] = C[t, r] + dt / ((r*dr)*dr) * 净流入

        C[t+1, N] = C[t, N] + dt * (
              2*D[N]*(C[t,N-1] - C[t,N])/dr**2
            - 2*hm  *(C[t,N]   - Ca)   /dr )

        # ---------- (e) 判停 ----------
        if stop_at is not None and C[t+1].max() < stop_at:
            return T[:t+2], C[:t+2], t + 1

    return T, C, nstep

# ============================================================
# 4. 用一下
# ============================================================
if __name__ == '__main__':
    t0 = time.time()

    # ----- 问题1：跑 1800 s -----
    T1, C1, _ = solve(1, 1800)
    print('【问题1】t = 1800 s')
    print('   r/cm      温度       水分浓度')
    for r in [0, 5, 10, 15, 20]:
        print('   %4.1f   %8.4f   %8.4f' % (r*0.1, T1[1800, r], C1[1800, r]))

    # ----- 问题2：跑到 C<0.15 -----
    T2, C2, te = solve(2, 250000, stop_at=0.15)
    print()
    print('【问题2】烘干结束')
    print('   结束时间 = %d s = %.2f h = %.2f 天' % (te, te/3600, te/86400))
    print('   中心 C = %.4f   表面 C = %.4f' % (C2[te, 0], C2[te, N]))

    print()
    print('总耗时 %.1f 秒' % (time.time() - t0))
