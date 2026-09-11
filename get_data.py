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

get_each_second(T_air,T_AIR)
get_each_second(C_air,C_AIR)

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

object_t_2 , object_c_2 = [] , []

object_t_2 = create_object(object_t_2,10801)
object_c_2 = create_object(object_c_2,10801)  

#第二问初始化
initialize(object_t_2,T_AIR,10800)
initialize(object_c_2,2.55,10800)


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
        self.object_t_2 = object_t_2
        self.object_c_2 = object_c_2            #第二问数据

######################################################################################
    def D(self,t,r):                                                #第一问的动态数据
        return 7*10**(-9)*math.exp(-0.89/self.object_c[t][r])           
######################################################################################
    def D_2(self,t,r):                                              
        return 2.4*10**(-3)*math.exp(0.45/self.object_c_2[t][r])*math.exp(3850/self.object_t_2[t][r])

    def p_2(self,t,r):
        return 650+128*self.object_c_2[t][r]
                                                                    #第二问的动态数据
    def c_p_2(self,t,r):
        return 1450+2736*self.object_c_2[t][r]/(1+self.object_c_2[t][r])

    def k_2(self,t,r):
        return 0.21+0.38*self.object_c_2[t][r]/(1+self.object_c_2[t][r])
######################################################################################
class formula(data):
    def __init__(self):
        super().__init__()

######################################################################################
####下面是第一，二小问计算公式
                            #a->p,b->c_p,c->k,d->D
    def center_t(self,t,r,a,b,c,d):
        self.object_t[t+1][r] = self.object_t[t][r] + (self.object_t[t][r+1] - self.object_t[t][r])*4*self.k*self.dt/(self.p*self.c_p*self.dr**2)

    def inner_t(self,t,r,a,b,c,d):                                          #温度公式                                                                                
        self.object_t[t+1][r] = self.object_t[t][r] + ((((r+0.5)/1000)*self.k*(self.object_t[t][r+1]-self.object_t[t][r])/self.dr)-(((r-0.5)/1000)*self.k*(self.object_t[t][r]-self.object_t[t][r-1])/self.dr))*self.dt/(self.p*self.c_p*(r/1000)*self.dr)

    def surface_t(self,t,r,a,b,c,d):
        self.object_t[t+1][r] = self.object_t[t][r] + ((2*self.k*(self.object_t[t][r-1]-self.object_t[t][r])/self.dr**2)-2*self.h*(self.object_t[t][r]-self.T_air[t])/self.dr)*self.dt/(self.p*self.c_p)
######################################################################################
    def center_c(self,t,r,a,b,c,d):
        self.object_c[t+1][r] = self.object_c[t][r] + (self.object_c[t][r+1] - self.object_c[t][r])*4*self.dt*(self.D(t,r)+self.D(t,r+1))/2/self.dr**2

    def inner_c(self,t,r,a,b,c,d):                                          #水分公式
        self.object_c[t+1][r] = self.object_c[t][r] + (((r+0.5)/1000)*(self.D(t,r+1)+self.D(t,r))/2*(self.object_c[t][r+1]-self.object_c[t][r])/self.dr-((r-0.5)/1000)*(self.D(t,r)+self.D(t,r-1))/2*(self.object_c[t][r]-self.object_c[t][r-1])/self.dr)*self.dt/(r/1000*self.dr)

    def surface_c(self,t,r,a,b,c,d):
        self.object_c[t+1][r] = self.object_c[t][r] + (2*self.D(t,r)*(self.object_c[t][r-1]-self.object_c[t][r])/self.dr**2-2*self.h_m*(self.object_c[t][r]-self.C_air[t])/self.dr)*self.dt
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

for t in range(1800):
    for r in range(21):
        if r == 0:
            formula().center_c(t,r)
        elif r == 20:
            formula().surface_c(t,r)
        else:
            formula().inner_c(t,r)


# print(object_t)
# print(object_c)

