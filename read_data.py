import numpy as np
import os
import matplotlib.pyplot as plt

# =============================================================================
# path = os.path.join(os.getcwd(),"data/phases")
# data = np.loadtxt(os.path.join(path,"xy-phase-25.txt"), delimiter=";", comments="%")
# 
# N = len(data)
# 
# 
# t = data[:N//4,0]
# 
# X = data[:N//2,1]
# Y = data[N//2:,1]
# 
# n = len(X)
# 
# X = X[n//4:2*n//3]
# Y = Y[n//4:2*n//3]
# t = t[n//4:2*n//3]
# 
# plt.plot(t,X)
# plt.plot(t,Y)
# 
# plt.scatter(X,Y)
# =============================================================================

def plot(run: str):
    path = os.path.join(os.getcwd(),"data/phases")
# =============================================================================
#     dataX = np.loadtxt(os.path.join(path,f"data_X_{run}.csv"), delimiter="ü")
#     dataY = np.loadtxt(os.path.join(path,f"data_Y_{run}.csv"), delimiter="ü")
# 
#     X = dataX[:,1]
#     Y = dataY[:,1]
# =============================================================================

    data = np.loadtxt(os.path.join(path,'xy-phase-155-2.txt'), delimiter=";", comments="%")

    N = len(data)
    X = data[:N//2,1]
    Y = data[N//2:,1]

    #fig, ax = plt.subplots()
    plt.scatter(X,Y)
    plt.axis('square')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.ticklabel_format(style='sci', axis = 'both', scilimits=(0,0))
    plt.title("X and Y quadratures")
    
plot("noise-500-param")