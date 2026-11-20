# Chess.com Helper for Beginners
# Requires: Python 3.10+, pip install python-chess mss opencv-python numpy pillow PyQt5
# Also requires Stockfish binary (https://stockfishchess.org/download/) on PATH.

import sys
import time
import threading

try:
    import chess
    import chess.engine
except ImportError:
    print("Missing python-chess. Run: pip install python-chess")
    sys.exit(1)

try:
    import mss
    import numpy as np
    import cv2
except ImportError:
    print("Missing screen capture libs. Run: pip install mss opencv-python numpy")
    sys.exit(1)

try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import Qt, QRect
    from PyQt5.QtGui import QPainter, QColor, QPen
except ImportError:
    print("Missing PyQt5. Run: pip install PyQt5")
    sys.exit(1)


STOCKFISH_PATH = r"C:\chess_helper\stockfish\stockfish\stockfish-windows-x86-64.exe"


class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.arrow = None  # (x1,y1,x2,y2) in screen pixels

    def set_arrow(self, coords):
        self.arrow = coords
        self.update()

    def paintEvent(self, event):
        if not self.arrow:
            return
        x1, y1, x2, y2 = self.arrow
        p = QPainter(self)
        pen = QPen(QColor(0, 200, 0, 220), 6)
        p.setPen(pen)
        p.drawLine(x1, y1, x2, y2)
        # arrowhead
        import math
        ang = math.atan2(y2 - y1, x2 - x1)
        size = 18
        for da in (2.6, 3.7):
            ax = x2 - size * math.cos(ang + da)
            ay = y2 - size * math.sin(ang + da)
            p.drawLine(int(x2), int(y2), int(ax), int(ay))


def square_to_pixel(sq, board_rect):
    # board_rect: (x, y, w, h) of the board on screen
    bx, by, bw, bh = board_rect
    col = chess.square_file(sq)
    row = 7 - chess.square_rank(sq)  # screen top = rank 8
    cell = bw / 8.0
    cx = bx + col * cell + cell / 2
    cy = by + row * cell + cell / 2
    return int(cx), int(cy)


def analyze_fen(fen, time_limit=1.0):
    board = chess.Board(fen)
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except FileNotFoundError:
        print("Stockfish not found. Install and add to PATH, or set STOCKFISH_PATH.")
        return None
    result = engine.play(board, chess.engine.Limit(time=time_limit))
    engine.quit()
    return result.move


def main():
    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()

    print("Chess.com Helper started.")
    print("Enter FEN of current position (or 'q' to quit):")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if line.lower() in ("q", "quit", "exit"):
            break
        if not line:
            continue
        try:
            board = chess.Board(line)
        except ValueError:
            print("Invalid FEN")
            continue
        move = analyze_fen(line)
        if move is None:
            continue
        print(f"Best move: {move.uci()} ({board.san(move)})")
        # For demo, ask user for board rect on screen
        print("Enter board rect as x,y,w,h (or press Enter to skip overlay):")
        rect_line = input("> ").strip()
        if rect_line:
            try:
                bx, by, bw, bh = [int(v) for v in rect_line.split(",")]
                x1, y1 = square_to_pixel(move.from_square, (bx, by, bw, bh))
                x2, y2 = square_to_pixel(move.to_square, (bx, by, bw, bh))
                overlay.set_arrow((x1, y1, x2, y2))
            except Exception as e:
                print("Bad rect:", e)


if __name__ == "__main__":
    main()
