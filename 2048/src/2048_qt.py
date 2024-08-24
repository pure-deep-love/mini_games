import sys
import numpy as np
import random
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QVBoxLayout, QGridLayout, QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QMutex, QMutexLocker, pyqtSignal
from PyQt5.QtGui import QIcon

class Game2048(QMainWindow):
    update_signal = pyqtSignal()

    def __init__(self, grid_size):
        super().__init__()
        self.grid_size = grid_size
        self.score = 0
        self.start_time = time.time()
        self.game_over = False
        self.mutex = QMutex()
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        self.cooldown = False
        self.key_pressed = set()
        self.valid_keys = [Qt.Key_W, Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]
        self.num_count = 0

        self.setup_ui()
        self.add_random_tile()
        self.add_random_tile()
        self.num_count += 2
        self.update_display()

        self.update_signal.connect(self.update_display_info)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def setup_ui(self):
        self.setWindowTitle("2048 Game")
        self.setWindowIcon(QIcon("R-C.ico"))

        cell_size = 606 // self.grid_size
        window_width = cell_size * self.grid_size + 20
        window_height = cell_size * self.grid_size + 150

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

        self.game_over_label = QLabel()
        self.game_over_label.setStyleSheet("font-size: 30px; color: red;")
        self.game_over_label.setAlignment(Qt.AlignCenter)
        self.game_over_label.setVisible(False)

        self.new_game_button = QPushButton("New Game")
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
        main_layout.addWidget(self.game_over_label)
        main_layout.addWidget(self.new_game_button)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_display_info(self):
        with QMutexLocker(self.mutex):
            self.score_label.setText(f"SCORE: {self.score}")
            self.time_label.setText(f"TIME: {int(time.time() - self.start_time)}")
            if self.game_over:
                self.game_over_label.setText("Game Over!")
                self.game_over_label.setVisible(True)
                self.new_game_button.setVisible(True)

    def update_display(self):
        cell_size = 606 // self.grid_size

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                item = self.grid_layout.itemAtPosition(i, j)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()

        self.grid_layout.setSpacing(0)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
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

    def add_random_tile(self):
        x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
        while self.grid[x][y] != 0:
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
        self.grid[x][y] = 2

    def compress(self, row_or_col, direction):
        temp = np.zeros(self.grid_size, dtype=int)
        index = 0 if direction == 0 else self.grid_size - 1
        for i in range(self.grid_size):
            if row_or_col[i] != 0:
                temp[index] = row_or_col[i]
                index = index + 1 if direction == 0 else index - 1
        return temp

    def merge(self, row_or_col, direction):
        temp = self.compress(row_or_col, direction)
        for i in range(self.grid_size - 1):
            if temp[i] == temp[i + 1] and temp[i] != 0:
                temp[i] *= 2
                self.score += temp[i]
                temp[i + 1] = 0
                self.num_count -= 1
        return self.compress(temp, direction)

    def move(self, direction_key):
        with QMutexLocker(self.mutex):
            moved = False
            if direction_key.key() == Qt.Key_W or direction_key.key() == Qt.Key_Up:
                for i in range(self.grid_size):
                    new_col = self.merge(self.grid[:, i], 0)
                    if not np.array_equal(self.grid[:, i], new_col):
                        moved = True
                    self.grid[:, i] = new_col
            elif direction_key.key() == Qt.Key_S or direction_key.key() == Qt.Key_Down:
                for i in range(self.grid_size):
                    new_col = self.merge(self.grid[:, i], 1)
                    if not np.array_equal(self.grid[:, i], new_col):
                        moved = True
                    self.grid[:, i] = new_col
            elif direction_key.key() == Qt.Key_A or direction_key.key() == Qt.Key_Left:
                for i in range(self.grid_size):
                    new_row = self.merge(self.grid[i, :], 0)
                    if not np.array_equal(self.grid[i, :], new_row):
                        moved = True
                    self.grid[i, :] = new_row
            elif direction_key.key() == Qt.Key_D or direction_key.key() == Qt.Key_Right:
                for i in range(self.grid_size):
                    new_row = self.merge(self.grid[i, :], 1)
                    if not np.array_equal(self.grid[i, :], new_row):
                        moved = True
                    self.grid[i, :] = new_row
            return moved

    def check_game_status(self):
        if np.any(self.grid == 0):
            return True
        for i in range(self.grid_size):
            for j in range(self.grid_size - 1):
                if self.grid[i][j] == self.grid[i][j + 1] or self.grid[j][i] == self.grid[j + 1][i]:
                    return True
        return False

    def keyPressEvent(self, event):
        if self.cooldown or self.game_over:
            return

        if event.key() in self.valid_keys:
            self.key_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if self.cooldown or self.game_over:
            return

        if event.key() in self.valid_keys and event.key() in self.key_pressed:
            self.key_pressed.discard(event.key())
            if not self.cooldown:
                self.cooldown = True
                moved = self.move(event)
                if moved:
                    self.add_random_tile()
                    self.num_count += 1
                    self.update_display()
                    if not self.check_game_status():
                        self.game_over = True
                        self.timer.stop()
                        self.update_display_info()
                QTimer.singleShot(120, self.reset_cooldown)

    def reset_cooldown(self):
        self.cooldown = False

    def update_timer(self):
        self.update_signal.emit()

    def start_new_game(self):
        self.close()
        self.size_selector = SizeSelector()
        self.size_selector.show()

class SizeSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("2048")
        self.setWindowIcon(QIcon("R-C.ico"))
        layout = QVBoxLayout()

        self.title_label = QLabel("2048")
        self.title_label.setStyleSheet("font-size: 32px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.size_label = QLabel("Enter grid size (3 <= size <= 20):")
        self.size_label.setStyleSheet("font-size: 20px;")
        self.size_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.size_label)

        self.size_input = QLineEdit(self)
        self.size_input.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.size_input)

        self.control_label = QLabel("Use w, a, s, d or arrow keys to control!", self)
        self.control_label.setAlignment(Qt.AlignCenter)
        self.control_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.control_label)

        self.start_button = QPushButton("Start Game", self)
        self.start_button.setStyleSheet("font-size: 16px;")
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setGeometry(400, 400, 400, 300)
        self.show()

    def start_game(self):
        try:
            size = int(self.size_input.text())
            if 3 <= size <= 20:
                self.game_window = Game2048(size)
                self.game_window.show()
                self.close()
            else:
                self.size_label.setText("Please enter a number between 3 and 20.")
        except ValueError:
            self.size_label.setText("Invalid input! Please enter a number.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    selector = SizeSelector()
    sys.exit(app.exec_())
