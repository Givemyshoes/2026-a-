# -*- coding: utf-8 -*-
"""演示一个时间步里，"备料"和"用料"的先后顺序"""
import math

次数 = 0
def prop(problem, C, T):
    global 次数
    次数 += 1
    if problem == 1:
        return 820.0, 2600.0, 0.36, 7e-9*math.exp(-0.89/C)
    TK = T + 273.15
    return (650+128*C, 1450+2736*C/(C+1), 0.21+0.38*C/(C+1),
            2.4e-3*math.exp(-0.45/C)*math.exp(-3850/TK))

N, dt, dr = 20, 1.0, 0.001
T = [[28.0]*21 for _ in range(2)]     # 只跑 1 步，所以 2 行就够
C = [[2.55]*21 for _ in range(2)]
Ta, Ca = 28.0088, 0.0196365
problem = 2

print('=' * 62)
print('一个时间步的内部流程')
print('=' * 62)

print()
print('【备料 1】循环 21 次，把 21 个点的 rho/cp/kk 都算出来')
rho = [0.0]*21
cp  = [0.0]*21
kk  = [0.0]*21
for r in range(21):
    rho[r], cp[r], kk[r], _ = prop(problem, C[0][r], T[0][r])
print('   -> 调用 prop 的次数累计 =', 次数)

print()
print('【用料 1】温度三个公式，直接取 rho[r] cp[r] kk[r]')
kh = 0.5*(kk[0] + kk[1])
T[1][0] = T[0][0] + (T[0][1]-T[0][0]) * 4*kh*dt / (rho[0]*cp[0]*dr**2)
for r in range(1, N):
    kR = 0.5*(kk[r] + kk[r+1])
    kL = 0.5*(kk[r] + kk[r-1])
    净 = ((r+0.5)*dr)*kR*(T[0][r+1]-T[0][r])/dr - ((r-0.5)*dr)*kL*(T[0][r]-T[0][r-1])/dr
    T[1][r] = T[0][r] + 净 * dt / (rho[r]*cp[r]*((r*dr)*dr))
T[1][N] = T[0][N] + (2*kk[N]*(T[0][N-1]-T[0][N])/dr**2 - 2*25.0*(T[0][N]-Ta)/dr)*dt/(rho[N]*cp[N])
print('   -> 调用 prop 的次数还是', 次数, '（公式里只是"取"，没有再调用）')

print()
print('【备料 2】再用【刚更新的】温度，算 21 个点的 D')
D = [0.0]*21
for r in range(21):
    D[r] = prop(problem, C[0][r], T[1][r])[3]      # <- 注意是 T[1][r]，新温度！
print('   -> 调用 prop 的次数累计 =', 次数)

print()
print('【用料 2】水分三个公式，直接取 D[r]')
Dh = 0.5*(D[0]+D[1])
C[1][0] = C[0][0] + (C[0][1]-C[0][0]) * 4*Dh*dt / dr**2
for r in range(1, N):
    DR = 0.5*(D[r]+D[r+1]); DL = 0.5*(D[r]+D[r-1])
    净 = ((r+0.5)*dr)*DR*(C[0][r+1]-C[0][r])/dr - ((r-0.5)*dr)*DL*(C[0][r]-C[0][r-1])/dr
    C[1][r] = C[0][r] + 净 * dt / ((r*dr)*dr)
C[1][N] = C[0][N] + (2*D[N]*(C[0][N-1]-C[0][N])/dr**2 - 2*8e-7*(C[0][N]-Ca)/dr)*dt
print('   -> 调用 prop 的次数还是', 次数)

print()
print('=' * 62)
print('结论：一个时间步共调用 prop %d 次 = 21(备温度料) + 21(备水分料)' % 次数)
print('      跑到 20 万步就是 %d 次调用' % (次数*200000))
print('=' * 62)

print()
print('对比：如果"不备料"，直接在公式里调用函数，会长这样：')
print("""
    T[t+1][r] = T[t][r] + ( 0.5*(prop(problem,C[t][r],T[t][r])[2]
                                + prop(problem,C[t][r+1],T[t][r+1])[2])
                            * ... ) / ( prop(problem,C[t][r],T[t][r])[0]
                                      * prop(problem,C[t][r],T[t][r])[1] * ...)
    ...又长又慢，同一个点的物性被反复算好几遍
""")
print('所以：先备料、后用料，是"图省事 + 图快"。')
