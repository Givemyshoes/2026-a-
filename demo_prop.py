# -*- coding: utf-8 -*-
"""演示：函数怎么调用、返回值怎么拿到、拿到后怎么用"""
import math

def prop(problem, C, T):
    C = max(C, 1e-9)
    if problem == 1:
        return 820.0, 2600.0, 0.36, 7e-9*math.exp(-0.89/C)
    TK = T + 273.15
    if problem in (2, 3):
        return (650 + 128*C,
                1450 + 2736*C/(C+1),
                0.21 + 0.38*C/(C+1),
                2.4e-3*math.exp(-0.45/C)*math.exp(-3850/TK))
    return (760 + 90*C, 1850 + 2150*C/(C+1),
            0.12 + 0.20*C/(C+1), 4.2e-4*math.exp(-0.30/C)*math.exp(-3850/TK))

print('=' * 60)
print('第 1 步：先看 prop 到底"吐"出什么')
print('=' * 60)
结果 = prop(2, 2.55, 28.0)
print('prop(2, 2.55, 28.0) 返回的是：')
print('   ', 结果)
print('   类型是', type(结果).__name__, '，长度是', len(结果))
print('   它其实是把 4 个数"打包"成一个元组')

print()
print('=' * 60)
print('第 2 步：怎么把 4 个数拿出来 —— 解包赋值')
print('=' * 60)
rho, cp, kk, D = prop(2, 2.55, 28.0)
print('   rho =', rho)
print('   cp  =', cp)
print('   kk  =', kk)
print('   D   =', D)
print('   左边 4 个名字 <-> 右边 4 个数，一一对应装进去')

print()
print('=' * 60)
print('第 3 步：只要其中几个 —— 用 _ 当"垃圾桶"')
print('=' * 60)
_, _, _, D = prop(2, 2.55, 28.0)
print('   _, _, _, D = prop(...)   ->  D =', D)
print('   或者用下标：prop(...)[3] ->  ', prop(2, 2.55, 28.0)[3])

print()
print('=' * 60)
print('第 4 步：21 个点都算一遍，装进列表')
print('=' * 60)
rho = [0.0]*21
cp  = [0.0]*21
kk  = [0.0]*21
for r in range(21):
    # 第 r 个点：水分 = 2.55，温度 = 28
    rho[r], cp[r], kk[r], _ = prop(2, 2.55, 28.0)

print('   算完以后：')
print('   rho[0]  =', rho[0])
print('   rho[10] =', rho[10])
print('   kk[10]  =', kk[10])
print('   kk[20]  =', kk[20])

print()
print('=' * 60)
print('第 5 步：在公式里怎么用这些数')
print('=' * 60)
dt, dr, r = 1.0, 0.001, 10          # 拿第 10 个点举例
T = [[0.0]*21 for _ in range(3)]
T[0][9], T[0][10], T[0][11] = 28.0, 28.0, 28.0

净流入 = ((r+0.5)*dr)*(0.5*(kk[10]+kk[11]))*(T[0][11]-T[0][10])/dr \
       - ((r-0.5)*dr)*(0.5*(kk[10]+kk[9]))*(T[0][10]-T[0][9])/dr
T[1][10] = T[0][10] + 净流入 * dt / (rho[10]*cp[10]*((r*dr)*dr))

print('   公式里写的 rho[10]、cp[10]、kk[10]，')
print('   取出来的就是第 4 步存进去的那几个数：')
print('      rho[10] =', rho[10])
print('      cp[10]  =', cp[10])
print('      kk[10]  =', kk[10])
print('   代入后 T[1][10] =', T[1][10])
print('   （这里 T 处处相等，所以净流入=0，温度不变，符合预期）')

print()
print('=' * 60)
print('第 6 步：真实用的时候，输入的不是常数，而是 t 时刻的值')
print('=' * 60)
print('''
    for t in range(nstep):
        # 每个点用它【当地、当时】的 C 和 T 去问 prop
        for r in range(21):
            rho[r], cp[r], kk[r], _ = prop(problem, C[t][r], T[t][r])
                                                    ^^^^^^^  ^^^^^^^
                                                    第 t 步、第 r 个点的水分和温度

        # 温度公式里直接用 rho[r] cp[r] kk[r]
        ...
''')
