# -*- coding: utf-8 -*-
"""
最简可复用模板：四个问题共用一套公式
-------------------------------------
看两件事就够了：
  1) prop()  —— 唯一随题目变的地方
  2) solve() —— 公式里用的是 rho[r]、cp[r]、kk[r]、D[r] 这些"当场算出来的变量"
"""
import math, time, openpyxl

# ---------- 常量 ----------
dt, dr, N = 1.0, 0.001, 20      # 20 段 -> 21 个点, r=0 是中心, r=N 是表面
h, hm = 25.0, 8e-7

# ---------- 环境条件（附件1，插值到每秒）----------
def load_air(path='A题/附件/附件1.xlsx'):
    ws = openpyxl.load_workbook(path, data_only=True).active
    rows = [r for i, r in enumerate(ws.iter_rows(values_only=True)) if i > 0]
    A, B = [x[1] for x in rows], [x[2] for x in rows]
    T, C = [A[0]], [B[0]]
    for k in range(1, len(A)):
        for j in range(1, 61):
            T.append(A[k-1] + (A[k]-A[k-1])*j/60)
            C.append(B[k-1] + (B[k]-B[k-1])*j/60)
    return T, C

T_AIR, C_AIR = load_air()
def env(t):
    return (T_AIR[t], C_AIR[t]) if t <= 14400 else (50.0, 0.05)

# ============================================================
# ① 物性：唯一随题目变的地方
#    输入当地的水分 C 和温度 T(摄氏度)，返回 rho, cp, k, D
# ============================================================
def prop(problem, C, T):
    C = max(C, 1e-9)
    if problem == 1:                                  # 附录2
        return 820.0, 2600.0, 0.36, 7e-9*math.exp(-0.89/C)
    TK = T + 273.15                                   # 开尔文
    if problem == 2 or problem == 3:                  # 附录3
        return (650 + 128*C,
                1450 + 2736*C/(C+1),
                0.21 + 0.38*C/(C+1),
                2.4e-3*math.exp(-0.45/C)*math.exp(-3850/TK))
    return (760 + 90*C,                               # 附录4（问题4）
            1850 + 2150*C/(C+1),
            0.12 + 0.20*C/(C+1),
            4.2e-4*math.exp(-0.30/C)*math.exp(-3850/TK))

# ============================================================
# ② 求解：公式只有这一份
# ============================================================
def solve(problem, nstep, stop_at=None):
    T = [[0.0]*21 for _ in range(nstep+1)]      # 温度场 T[t][r]
    C = [[0.0]*21 for _ in range(nstep+1)]      # 水分场 C[t][r]
    for r in range(21):
        T[0][r] = 28.0                          # 药材初温
        C[0][r] = 2.55                          # 药材初水分

    for t in range(nstep):
        Ta, Ca = env(t)

        # ----- (a) 先算出 21 个点各自的物性 -----
        rho = [0.0]*21
        cp  = [0.0]*21
        kk  = [0.0]*21
        for r in range(21):
            rho[r], cp[r], kk[r], _ = prop(problem, C[t][r], T[t][r])

        # ----- (b) 温度 -----
        kh = 0.5*(kk[0] + kk[1])
        T[t+1][0] = T[t][0] + (T[t][1]-T[t][0]) * 4*kh*dt / (rho[0]*cp[0]*dr**2)

        for r in range(1, N):
            kR = 0.5*(kk[r] + kk[r+1])                     # 界面 r+1/2
            kL = 0.5*(kk[r] + kk[r-1])                     # 界面 r-1/2
            净流入 = ((r+0.5)*dr)*kR*(T[t][r+1]-T[t][r])/dr \
                   - ((r-0.5)*dr)*kL*(T[t][r]-T[t][r-1])/dr
            T[t+1][r] = T[t][r] + 净流入 * dt / (rho[r]*cp[r]*((r*dr)*dr))

        T[t+1][N] = T[t][N] + ( 2*kk[N]*(T[t][N-1]-T[t][N])/dr**2
                              - 2*h*(T[t][N]-Ta)/dr ) * dt / (rho[N]*cp[N])

        # ----- (c) 用刚更新好的温度算 D（耦合就在这）-----
        D = [0.0]*21
        for r in range(21):
            D[r] = prop(problem, C[t][r], T[t+1][r])[3]

        # ----- (d) 水分：形状和温度完全一样，但没有 rho*cp -----
        Dh = 0.5*(D[0] + D[1])
        C[t+1][0] = C[t][0] + (C[t][1]-C[t][0]) * 4*Dh*dt / dr**2

        for r in range(1, N):
            DR = 0.5*(D[r] + D[r+1])
            DL = 0.5*(D[r] + D[r-1])
            净流入 = ((r+0.5)*dr)*DR*(C[t][r+1]-C[t][r])/dr \
                   - ((r-0.5)*dr)*DL*(C[t][r]-C[t][r-1])/dr
            C[t+1][r] = C[t][r] + 净流入 * dt / ((r*dr)*dr)

        C[t+1][N] = C[t][N] + ( 2*D[N]*(C[t][N-1]-C[t][N])/dr**2
                              - 2*hm*(C[t][N]-Ca)/dr ) * dt

        # ----- (e) 判停 -----
        if stop_at is not None and max(C[t+1]) < stop_at:
            return T[:t+2], C[:t+2], t+1

    return T, C, nstep

# ============================================================
# ③ 用一下
# ============================================================
if __name__ == '__main__':
    t0 = time.time()

    T1, C1, _ = solve(1, 1800)
    print('【问题1】t=1800s')
    for r in [0, 5, 10, 15, 20]:
        print('   r=%.1fcm  T=%.4f  C=%.4f' % (r*0.1, T1[1800][r], C1[1800][r]))

    T2, C2, te = solve(2, 250000, stop_at=0.15)
    print('【问题2】烘干结束 = %d s = %.2f 天' % (te, te/86400))

    print('耗时 %.1f 秒' % (time.time()-t0))
