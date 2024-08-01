import tkinter as tk
import numpy as np
import random
import time
from threading import Thread, Lock

class Game2048:
    def __init__(self, root, size):
            self.root = root
            self.size = size
            self.score = 0
            self.start_time = time.time()
            self.game_over = False
            self.lock = Lock()
            self.grid = np.zeros((size, size), dtype=int)

            self.root.title("2048 Game")
            
            self.top_frame = tk.Frame(self.root)
            self.top_frame.grid(row=0, column=0, columnspan=2, pady=10)

            self.score_label = tk.Label(self.top_frame, text=f"YOUR SCORE: {self.score}", font=("Helvetica Neue", 20))
            self.score_label.grid(row=0, column=0, padx=20, sticky=tk.W)

            self.time_label = tk.Label(self.top_frame, text=f"TIME: {int(time.time() - self.start_time)}", font=("Helvetica Neue", 20))
            self.time_label.grid(row=0, column=1, padx=20, sticky=tk.W)

            self.canvas = tk.Canvas(self.root, width=606, height=606)
            self.canvas.grid(row=1, column=0, columnspan=2)

            self.bottom_frame = tk.Frame(self.root)
            self.bottom_frame.grid(row=2, column=0, columnspan=2, pady=10)

            self.credit_label1 = tk.Label(self.bottom_frame, text="POWERED by JUICE", font=("Helvetica Neue", 12))
            self.credit_label1.grid(row=3, column=0, padx=10, sticky=tk.W)

            self.credit_label2 = tk.Label(self.bottom_frame, text="https://github.com/pure-deep-love/mini_games.git", font=("Helvetica Neue", 12))
            self.credit_label2.grid(row=3, column=1, padx=10, sticky=tk.W)

            self.root.bind("<KeyPress>", self.key_press)
            
            self.ran_num()
            self.ran_num()
            self.printg()

            self.print_thread = Thread(target=self.printg_periodically)
            self.print_thread.start()

    def printg(self):
        with self.lock:
            self.score_label.config(text=f"YOUR SCORE: {self.score}")
            self.time_label.config(text=f"TIME: {int(time.time() - self.start_time)}")
            
            self.canvas.delete("all")
            cell_width = 600 // self.size
            for i in range(self.size):
                for j in range(self.size):
                    x0, y0 = j * cell_width + 3, i * cell_width + 3
                    x1, y1 = x0 + cell_width, y0 + cell_width
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")
                    if self.grid[i][j] != 0:
                        self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(self.grid[i][j]), font=("Helvetica Neue", 20))

    def ran_num(self):
        a, b = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        while self.grid[a][b] != 0:
            a, b = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        self.grid[a][b] = 2

    def compress(self, arr, st):
        tmp = np.zeros(self.size, dtype=int)
        j = 0 if st == 0 else self.size - 1
        for i in range(self.size):
            if arr[i] != 0:
                tmp[j] = arr[i]
                j = j + 1 if st == 0 else j - 1
        return tmp

    def merge(self, arr, st):
        tmp = self.compress(arr, st)
        for i in range(self.size - 1):
            if tmp[i] == tmp[i + 1] and tmp[i] != 0:
                tmp[i] *= 2
                self.score += tmp[i]
                tmp[i + 1] = 0
        return self.compress(tmp, st)

    def move(self, key):
        with self.lock:
            if key == 'w':
                for i in range(self.size):
                    self.grid[:, i] = self.merge(self.grid[:, i], 0)
            elif key == 's':
                for i in range(self.size):
                    self.grid[:, i] = self.merge(self.grid[:, i], 1)
            elif key == 'a':
                for i in range(self.size):
                    self.grid[i, :] = self.merge(self.grid[i, :], 0)
            elif key == 'd':
                for i in range(self.size):
                    self.grid[i, :] = self.merge(self.grid[i, :], 1)

    def check(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return True
        return False

    def key_press(self, event):
        keys = ['w', 'a', 's', 'd', 'q']
        if event.char in keys:
            self.move(event.char)
            if self.check():
                self.ran_num()
                self.printg()
            else:
                self.game_over = True
                self.root.unbind("<KeyPress>")
                self.canvas.create_text(300, 350, text="Game Over!", font=("Helvetica Neue", 40), fill="red")

    def printg_periodically(self):
        while not self.game_over:
            time.sleep(1)
            self.printg()

class SizeSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("2048")

        self.label_2048 = tk.Label(self.root, text="2048", font=("Helvetica Neue", 32))
        self.label_2048.grid(row=0, column=0, columnspan=2, pady=20)  

        self.label_1 = tk.Label(self.root, text="Enter grid size (3 <= size <= 20):", font=("Helvetica Neue", 16))
        self.label_1.grid(row=1, column=0, pady=20)  

        self.entry = tk.Entry(self.root, font=("Helvetica Neue", 16))
        self.entry.grid(row=1, column=1, pady=20) 

        self.label_2 = tk.Label(self.root, text="Use w,a,s,d to control!", font=("Helvetica Neue", 16))
        self.label_2.grid(row=2, column=0, columnspan=2, pady=20)  

        self.button = tk.Button(self.root, text="Start Game", font=("Helvetica Neue", 16), command=self.start_game)
        self.button.grid(row=3, column=0, columnspan=2, pady=20)  

    def start_game(self):
        try:
            size = min(max(int(self.entry.get()), 3), 20)
            self.root.destroy()
            root = tk.Tk()
            game = Game2048(root, size)
            root.mainloop()
        except ValueError:
            self.label.config(text="Please enter a valid number (3 <= size <= 20).")

if __name__ == "__main__":
    root = tk.Tk()
    app = SizeSelector(root)
    root.mainloop()
