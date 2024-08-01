import keyboard
import numpy as np
import random
import os
import time
from threading import Thread, Lock

print("Use w,a,s,d to control!")
print("Use 'q' to quit!")
while True:
    try:
        N = max(int(input('input N (larger than or equal to 3): ')), 3)
        break
    except ValueError:
        print("Please input a number!")

g = np.array([[0 for i in range(N)] for i in range(N)])
score = 0
num_cnt = 0
start_time = time.time()
game_over = False
lock = Lock()

def printg():
    global start_time
    with lock:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'YOUR SCORE: {score}\t\t\tTIME: {int(time.time() - start_time)}')
        print('-' * 6 * N)
        for i in range(N):
            for j in range(N):
                print(g[i][j], end='\t')
            if i != N - 1:
                print(end='\n\n')
        print()
        print('-' * 6 * N)
        print('POWERED by JUICE')
        print('https://github.com/pure-deep-love/mini_games.git')

def ran_num():
    a = random.randint(0, N - 1)
    b = random.randint(0, N - 1)
    while g[a][b]:
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
    global score, num_cnt
    tmp = compress(arr, st)
    start, end, step = 0, N - 1, 1
    if st == 1:
        start, end, step = N - 1, 0, -1
    i = start
    while (i < end if st == 0 else i > end):
        if tmp[i] == tmp[i + 1 if st == 0 else i - 1] and tmp[i] != 0:
            tmp[i] += tmp[i + 1 if st == 0 else i - 1]
            score += tmp[i]
            tmp[i + 1 if st == 0 else i - 1] = 0
            num_cnt -= 1
        i = i + 1 if st == 0 else i - 1
    arr = compress(tmp, st)
    return arr

def move(key):
    with lock:
        moved = False
        if key == 'w':
            for i in range(N):
                new_col = merge(g[:, i], 0)
                if not np.array_equal(g[:, i], new_col):
                    moved = True
                g[:, i] = new_col
        elif key == 's':
            for i in range(N):
                new_col = merge(g[:, i], 1)
                if not np.array_equal(g[:, i], new_col):
                    moved = True
                g[:, i] = new_col
        elif key == 'a':
            for i in range(N):
                new_row = merge(g[i, :], 0)
                if not np.array_equal(g[i, :], new_row):
                    moved = True
                g[i, :] = new_row
        elif key == 'd':
            for i in range(N):
                new_row = merge(g[i, :], 1)
                if not np.array_equal(g[i, :], new_row):
                    moved = True
                g[i, :] = new_row
        return moved

def check():
    with lock:
        for i in range(N):
            for j in range(N - 1):
                if g[i][j] == g[i][j + 1] or g[j][i] == g[j + 1][i]:
                    return True
        return False

def callback(event):
    global num_cnt
    keys = ['w', 'a', 's', 'd', 'q']
    global game_over
    key = event.name
    if key in keys:
        moved = move(key)
        if moved:
            ran_num()
            num_cnt += 1
            printg()
            if num_cnt >= N * N and not check():
                print("Game Over!")
                game_over = True
                keyboard.unhook_all()

def printg_periodically():
    global game_over
    while not game_over:
        time.sleep(5)
        printg()

ran_num()
ran_num()
num_cnt += 2
printg()
keyboard.on_press(callback)

print_thread = Thread(target=printg_periodically)
print_thread.start()

while not game_over:
    if keyboard.is_pressed('q'):
        game_over = True
        keyboard.unhook_all()

print_thread.join()
print("The game has been quit!")
os.system('pause' if os.name == 'nt' else 'read')