import sys
import numpy as np
import random
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog,QLabel, QPushButton, QLineEdit, QVBoxLayout, QGridLayout, QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QMutex, QMutexLocker, pyqtSignal
from PyQt5.QtGui import QIcon

class Game2048(QMainWindow):
    update_signal = pyqtSignal()

    def __init__(self, size):
        super().__init__()
        self.size = size
        self.score = 0
        self.start_time = time.time()
        self.game_over = False
        self.mutex = QMutex()
        self.grid = np.zeros((size, size), dtype=int)
        self.cooldown = False
        self.key_of_press = set()
        self.keys = ['w', 'a', 's', 'd']
        self.num_cnt = 0

        self.initUI()
        self.ran_num()
        self.ran_num()
        self.num_cnt += 2
        self.printg()

        self.update_signal.connect(self.printg_above)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def initUI(self):
        self.setWindowTitle("2048 Game")
        self.setWindowIcon(QIcon("R-C.ico"))

        cell_size = 606 // self.size
        window_width = cell_size * self.size + 20
        window_height = cell_size * self.size + 150  # Increase height for Game Over message and New Game button

        self.setGeometry(300, 300, window_width, window_height)
        self.setFixedSize(window_width, window_height)

        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.score_label = QLabel(f"SCORE: {self.score}")
        self.score_label.setStyleSheet("font-size: 25px;")
        top_layout.addWidget(self.score_label)

        self.time_label = QLabel(f"TIME: {int(time.time() - self.start_time)}")
        self.time_label.setStyleSheet("font-size: 25px;")
        self.time_label.setAlignment(Qt.AlignRight)
        top_layout.addWidget(self.time_label)

        self.game_over_label = QLabel()  # New label for Game Over message
        self.game_over_label.setStyleSheet("font-size: 30px; color: red;")
        self.game_over_label.setAlignment(Qt.AlignCenter)
        self.game_over_label.setText("")  # Initially empty
        self.game_over_label.setVisible(False)

        self.new_game_button = QPushButton("New Game")  # New button for starting a new game
        self.new_game_button.setStyleSheet("font-size: 20px;")
        self.new_game_button.clicked.connect(self.start_new_game)
        self.new_game_button.setVisible(False)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)

        bottom_layout = QHBoxLayout()
        self.credit_label1 = QLabel("POWERED by JUICE")
        self.credit_label1.setStyleSheet("font-size: 18px;")
        bottom_layout.addWidget(self.credit_label1)

        self.credit_label2 = QLabel("https://github.com/pure-deep-love/mini_games.git")
        self.credit_label2.setStyleSheet("font-size: 18px;")
        bottom_layout.addWidget(self.credit_label2)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(self.grid_layout)
        main_layout.addWidget(self.game_over_label)  # Add Game Over label
        main_layout.addWidget(self.new_game_button)  # Add New Game button
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def printg_above(self):
        with QMutexLocker(self.mutex):
            self.score_label.setText(f"SCORE: {self.score}")
            self.time_label.setText(f"TIME: {int(time.time() - self.start_time)}")
            if self.game_over:
                self.game_over_label.setText("Game Over!")  # Update Game Over label
                self.game_over_label.setVisible(True)  # Ensure Game Over label is visible
                self.new_game_button.setVisible(True)  # Show New Game button

    def printg(self):
        cell_size = 606 // self.size

        for i in range(self.size):
            for j in range(self.size):
                item = self.grid_layout.itemAtPosition(i, j)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()

        self.grid_layout.setSpacing(0)
        for i in range(self.size):
            for j in range(self.size):
                frame = QFrame(self)
                frame.setFixedSize(cell_size, cell_size)
                frame.setFrameShape(QFrame.Box)
                frame.setLineWidth(2)
                if self.grid[i][j] != 0:
                    frame.setStyleSheet("background-color: white;")
                    label = QLabel(str(self.grid[i][j]), self)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("font-size: 20px;")
                    self.grid_layout.addWidget(frame, i, j)
                    self.grid_layout.addWidget(label, i, j)
                else:
                    frame.setStyleSheet("background-color: #d9d9d9;")
                    self.grid_layout.addWidget(frame, i, j)

        if self.game_over:
            self.game_over_label.setGeometry(
                0, 0, self.width(), self.height() - 150
            )
            self.game_over_label.setVisible(True)
            self.new_game_button.setGeometry(
                (self.width() - self.new_game_button.width()) // 2,
                self.height() - self.new_game_button.height() - 20,
                self.new_game_button.width(),
                self.new_game_button.height()
            )
            self.new_game_button.setVisible(True)
        else:
            self.game_over_label.setVisible(False)
            self.new_game_button.setVisible(False)

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
                self.num_cnt -= 1
        return self.compress(tmp, st)

    def move(self, key):
        with QMutexLocker(self.mutex):
            moved = False
            if key == 'w':
                for i in range(self.size):
                    new_col = self.merge(self.grid[:, i], 0)
                    if not np.array_equal(self.grid[:, i], new_col):
                        moved = True
                    self.grid[:, i] = new_col
            elif key == 's':
                for i in range(self.size):
                    new_col = self.merge(self.grid[:, i], 1)
                    if not np.array_equal(self.grid[:, i], new_col):
                        moved = True
                    self.grid[:, i] = new_col
            elif key == 'a':
                for i in range(self.size):
                    new_row = self.merge(self.grid[i, :], 0)
                    if not np.array_equal(self.grid[i, :], new_row):
                        moved = True
                    self.grid[i, :] = new_row
            elif key == 'd':
                for i in range(self.size):
                    new_row = self.merge(self.grid[i, :], 1)
                    if not np.array_equal(self.grid[i, :], new_row):
                        moved = True
                    self.grid[i, :] = new_row
            return moved

    def check(self):
        if np.any(self.grid == 0):
            return True
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.grid[i][j] == self.grid[i][j + 1] or self.grid[j][i] == self.grid[j + 1][i]:
                    return True
        return False

    def keyPressEvent(self, event):
        if self.cooldown or self.game_over:
            return

        if event.text() in self.keys:
            self.key_of_press.add(event.text())

    def keyReleaseEvent(self, event):
        if self.cooldown or self.game_over:
            return

        if event.text() in self.keys and event.text() in self.key_of_press:
            self.cooldown = True
            moved = self.move(event.text())
            if moved:
                self.ran_num()
                self.num_cnt += 1
                self.printg()
                if not self.check():
                    self.game_over = True
                    self.timer.stop()  # Stop the timer when the game is over
                    self.printg_above()
            QTimer.singleShot(120, self.reset_cooldown)

    def reset_cooldown(self):
        self.cooldown = False

    def update_timer(self):
        self.update_signal.emit()

    def start_new_game(self):
        size, ok = QInputDialog.getInt(self, "Enter Grid Size", "Grid size (3-20):", self.size, 3, 20)
        if ok:
            self.size = size
            self.score = 0
            self.start_time = time.time()
            self.game_over = False
            self.grid = np.zeros((size, size), dtype=int)
            self.ran_num()
            self.ran_num()
            self.num_cnt = 2
            self.printg()
            self.printg_above()
            self.timer.start(1000)

class SizeSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("2048")
        self.setWindowIcon(QIcon("R-C.ico"))
        layout = QVBoxLayout()

        self.label_2048 = QLabel("2048")
        self.label_2048.setStyleSheet("font-size: 32px;")
        self.label_2048.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_2048)

        self.label_1 = QLabel("Enter grid size (3 <= size <= 20):")
        self.label_1.setStyleSheet("font-size: 20px;")
        self.label_1.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_1)

        self.entry = QLineEdit(self)
        self.entry.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.entry)

        self.label_2 = QLabel("Use w, a, s, d to control!", self)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.label_2)

        self.button = QPushButton("Start Game", self)
        self.button.setStyleSheet("font-size: 16px;")
        self.button.clicked.connect(self.start_game)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setGeometry(400, 400, 400, 300)
        self.show()

    def start_game(self):
        try:
            size = int(self.entry.text())
            if 3 <= size <= 20:
                self.game_window = Game2048(size)
                self.game_window.show()
                self.close()
            else:
                self.label_1.setText("Please enter a number between 3 and 20.")
        except ValueError:
            self.label_1.setText("Invalid input! Please enter a number.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    selector = SizeSelector()
    sys.exit(app.exec_())
