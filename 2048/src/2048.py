import numpy as np
import random

N = max(int(input('input size: ')), 3)

g = np.array([[0 for i in range(N)]for i in range(N)])

def printg():
    print('-' * 6 * N)
    for i in range(N):
        for j in range(N):
            print(g[i][j], end='\t')
        if i != N - 1:
            print(end='\n\n')
    print()
    print('-' * 6 * N)
    

def ran_num():
    a = random.randint(0, N - 1)
    b = random.randint(0, N - 1)
    while(g[a][b]):
        a = random.randint(0, N - 1)
        b = random.randint(0, N - 1)      
    g[a][b] = 2  

def compress(arr, st):
    tmp = np.array([0 for i in range(N)])
    start, end, step = 0, N, 1
    j = 0
    if st == 1:
        start, end, step = N - 1, -1, -1
        j = N - 1
    for i in range(start, end, step):
        if arr[i] != 0:
            tmp[j] = arr[i]
            j = j + 1 if st == 0 else j - 1
    return tmp

def merge(arr, st):
    tmp = compress(arr, st)
    start, end, step = N - 2, -1, -1
    if st == 1:
        start, end, step = 1, N, 1
    i = start
    while flag := i > end if st == 0 else i < end:
        if tmp[i] == tmp[i + 1 if st == 0 else i - 1]:
            tmp[i] += tmp[i + 1 if st == 0 else i - 1]
            tmp[i + 1 if st == 0 else i - 1] = 0
            i = i - 1 if st == 0 else i + 1
        i = i - 1 if st == 0 else i + 1
    arr = compress(tmp, st)
    return arr

def move(key):
    for i in range(N):
        if key == 'w':
            g[:, i] = merge(g[:, i], 0)
        elif key == 's':
            g[:, i] = merge(g[:, i], 1)
        elif key == 'a':
            g[i, :] = merge(g[i, :], 0)
        elif key == 'd':
            g[i, :] = merge(g[i, :], 1)

def check():
    cnt = 0
    for i in range(N):
        for j in range(N):
            if g[i][j] != 0:
                cnt += 1
    if cnt < N * N:
        return True
    return False

ran_num(), ran_num()
printg()

ending = False
while (not ending) :
    move(input())
    if check():
        ran_num()
        printg()
    else:
        ending = True
        print("Game Over!")