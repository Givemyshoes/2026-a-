import openpyxl

times, T_air, C_air = [], [], []

wb = openpyxl.load_workbook('A题\附件\附件1.xlsx', data_only=True)
ws = wb.active

for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i == 0:                 # 跳过表头
        continue
    t, T, C = row              # 解包：时间、温度、水分浓度
    times.append(t)
    T_air.append(T)
    C_air.append(C)

# print(times)
# print(T_air)
# print(C_air)

T_AIR , C_AIR = [] , []
#前1800秒的数据
def get_each_second(list,create_list):
    i_2 = 0
    for i in list:
        i_1 = i
        if i_2 != 0:
            for j in range(60):
                I = (i_1 - i_2)/60*(j+1)+i_2
                create_list.append(I)
        else:
            create_list.append(i_1)

        i_2 = i_1

    return create_list

def convert_to_K(list):
    for i in range(len(list)):
        list[i] = list[i] + 273.15
    return list

get_each_second(T_air,T_AIR)
get_each_second(C_air,C_AIR)

T_AIR = convert_to_K(T_AIR)

# print(T_AIR)
# print(C_AIR)

def create_object(object,a=1801,b=20):
    for t in range(a):
        row = [0]
        object.append(row)
        for r in range(b):
            line = [0]
            object[t].append(line)
    
    return object

# print(object)
object_t , object_c = [] , []

object_t = create_object(object_t)
object_c = create_object(object_c)

#开始温度28，水分2.55
def initialize(OBJECT,j,a=1801,b=21):
    if j == T_AIR:
        for t in range(a):
            for r in range(b):
                if t == 0:
                    OBJECT[0][r] = j[0]
                else:
                    OBJECT[t][20] = j[t]   
    else:
        for t in range(a):
            for r in range(b):
                if t == 0:
                    OBJECT[0][r] = j

    return OBJECT

#第一问初始化
initialize(object_t,T_AIR)
initialize(object_c,2.55)

# print(object_t)
# print(object_c)

# object_t_2 , object_c_2 = [] , []

# object_t_2 = create_object(object_t_2,10801)
# object_c_2 = create_object(object_c_2,10801)  
# #第二问初始化
# initialize(object_t_2,T_AIR,10800)
# initialize(object_c_2,2.55,10800)


import math

class data():
    def __init__(self):
        ##############################################################################
        self.object_t = object_t
        self.object_c = object_c
        self.T_air = T_AIR
        self.C_air = C_AIR

        self.p = 820
        self.c_p = 2600                         #第一问数据
        self.k = 0.36
        self.h = 25
        self.h_m = 8*10**(-7)
        self.dt = 1
        self.dr = 0.001
        ##############################################################################
        # self.object_t_2 = object_t_2
        # self.object_c_2 = object_c_2            #第二问数据

######################################################################################
    def D(self,t,r,b=None):                                                #第一问的动态数据
        if b is None:
            b = self.object_c
        return 7*10**(-9)*math.exp(-0.89/b[t][r])           
######################################################################################
#                                                                   #第一问的动态数据
    def D_2(self,t,r,a,b):                  
        return 2.4*10**(-3)*math.exp(-0.45/b[t][r])*math.exp(-3850/a[t][r])

    def p_2(self,t,r,a,b):
        return 650+128*b[t][r]
                                                                    #第二问的动态数据
    def c_p_2(self,t,r,a,b):
        return 1450+2736*b[t][r]/(1+b[t][r])

    def k_2(self,t,r,a,b):
        return 0.21+0.38*b[t][r]/(1+b[t][r])
######################################################################################
class formula(data):
    def __init__(self):
        super().__init__()

######################################################################################
####下面是第一，二小问计算公式
                            #a,b是列表p,c_p,k,D是系数
    def center_t(self,t,r,a=None,b=None,D=None,p=None,c_p=None,k=None):
        if a is None:
            a = self.object_t
            p = self.p
            c_p = self.c_p
            k = self.k
            D = self.D
        if b is None:
            b = self.object_c
            a[t+1][r] = a[t][r] + (a[t][r+1] - a[t][r])*4*k*self.dt/(p*c_p*self.dr**2)
        else:
            a[t+1][r] = a[t][r] + (a[t][r+1] - a[t][r])*4*((k[t][r]+k[t][r+1])/2)*self.dt/(p*c_p*self.dr**2)

    def inner_t(self,t,r,a=None,b=None,D=None,p=None,c_p=None,k=None):                                          #温度公式                                                                                
        if a is None:
            a = self.object_t
            p = self.p
            c_p = self.c_p
            k = self.k
            D = self.D
        if b is None:
            b = self.object_c
            a[t+1][r] = a[t][r] + ((((r+0.5)/1000)*k*(a[t][r+1]-a[t][r])/self.dr)-(((r-0.5)/1000)*k*(a[t][r]-a[t][r-1])/self.dr))*self.dt/(p*c_p*(r/1000)*self.dr)
        else:
            a[t+1][r] = a[t][r] + ((((r+0.5)/1000)*((k[t][r]+k[t][r+1])/2)*(a[t][r+1]-a[t][r])/self.dr)-(((r-0.5)/1000)*((k[t][r]+k[t][r+1])/2)*(a[t][r]-a[t][r-1])/self.dr))*self.dt/(p*c_p*(r/1000)*self.dr)
    def surface_t(self,t,r,a=None,b=None,D=None,p=None,c_p=None,k=None):
        if a is None:
            a = self.object_t
            p = self.p
            c_p = self.c_p
            k = self.k
            D = self.D
        if b is None:
            b = self.object_c
            a[t+1][r] = a[t][r] + ((2*k*(a[t][r-1]-a[t][r])/self.dr**2)-2*self.h*(a[t][r]-self.T_air[t])/self.dr)*self.dt/(p*c_p)
        else:
            a[t+1][r] = a[t][r] + ((2*((k[t][r]+k[t][r-1])/2)*(a[t][r-1]-a[t][r])/self.dr**2)-2*self.h*(a[t][r]-self.T_air[t])/self.dr)*self.dt/(p*c_p)
######################################################################################
    def center_c(self,t,r,a=None,b=None,D=None,p=None,c_p=None,k=None):
        if a is None:
            a = self.object_t
            p = self.p
            c_p = self.c_p
            k = self.k
        if b is None:
            b = self.object_c
            b[t+1][r] = b[t][r] + (b[t][r+1] - b[t][r])*4*self.dt*(self.D(t,r)+self.D(t,r+1))/2/self.dr**2
        else:    
            b[t+1][r] = b[t][r] + (b[t][r+1] - b[t][r])*4*self.dt*(D[t][r]+D[t][r+1])/2/self.dr**2

    def inner_c(self,t,r,a=None,b=None,D=None,p=None,c_p=None,k=None):                                          #水分公式
        if a is None:
            a = self.object_t
            p = self.p
            c_p = self.c_p
            k = self.k
        if b is None:
            b = self.object_c
            b[t+1][r] = b[t][r] + (((r+0.5)/1000)*(self.D(t,r)+self.D(t,r+1))/2*(b[t][r+1]-b[t][r])/self.dr-((r-0.5)/1000)*(self.D(t,r)+self.D(t,r-1))/2*(b[t][r]-b[t][r-1])/self.dr)*self.dt/(r/1000*self.dr)  
        else:
            b[t+1][r] = b[t][r] + (((r+0.5)/1000)*(D[t][r+1]+D[t][r])/2*(b[t][r+1]-b[t][r])/self.dr-((r-0.5)/1000)*(D[t][r]+D[t][r-1])/2*(b[t][r]-b[t][r-1])/self.dr)*self.dt/(r/1000*self.dr)
    def surface_c(self,t,r,a=None,b=None,D=None,p=None,c_p=None,k=None):
        if a is None:
            a = self.object_t
            p = self.p
            c_p = self.c_p
            k = self.k
            D = self.D
        if b is None:
            b = self.object_c
            b[t+1][r] = b[t][r] + (2*self.D(t,r)*(b[t][r-1]-b[t][r])/self.dr**2-2*self.h_m*(b[t][r]-self.C_air[t])/self.dr)*self.dt 
        else:
            b[t+1][r] = b[t][r] + (2*D[t][r]*(b[t][r-1]-b[t][r])/self.dr**2-2*self.h_m*(b[t][r]-self.C_air[t])/self.dr)*self.dt 
####
######################################################################################
####下面是第三小问计算公式
    

for t in range(1800):
    for r in range(21):
        if r == 0:
            formula().center_t(t,r)
        elif r == 20:
            formula().surface_t(t,r)
        else:
            formula().inner_t(t,r)

        if r == 0:
            formula().center_c(t,r)
        elif r == 20:
            formula().surface_c(t,r)
        else:
            formula().inner_c(t,r)


# print(object_t)
# print(object_c)

import numpy as np

object_t_2 = np.zeros((10801,21))
object_c_2 = np.zeros((10801,21))
D_2 = np.zeros((10801,21))
k_2 = np.zeros((10801,21))

initialize(object_t_2,T_AIR,10801,21)
initialize(object_c_2,2.55,10801,21)

p_2,c_p_2 = 0,0

def static_data(t,r):
    return data().p_2(t,r,object_t_2,object_c_2),data().c_p_2(t,r,object_t_2,object_c_2)

for t in range(10800):
    for r in range(21):
        D_2[t][r] = data().D_2(t,r,object_t_2,object_c_2)
        k_2[t][r] = data().k_2(t,r,object_t_2,object_c_2)
    for r in range(21):
        p_2,c_p_2 = static_data(t,r)
        if r == 0:
            formula().center_t(t,r,object_t_2,object_c_2,D_2,p_2,c_p_2,k_2)
        elif r == 20:
            formula().surface_t(t,r,object_t_2,object_c_2,D_2,p_2,c_p_2,k_2)
        else:
            formula().inner_t(t,r,object_t_2,object_c_2,D_2,p_2,c_p_2,k_2)

        if r == 0:
            formula().center_c(t,r,object_t_2,object_c_2,D_2,p_2,c_p_2,k_2)
        elif r == 20:
            formula().surface_c(t,r,object_t_2,object_c_2,D_2,p_2,c_p_2,k_2)
        else:
            formula().inner_c(t,r,object_t_2,object_c_2,D_2,p_2,c_p_2,k_2)

print(object_t_2)

