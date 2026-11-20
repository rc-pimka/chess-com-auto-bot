import sys, time, json, os
sys.path.insert(0, r"C:\Users\L\Desktop\2d-chess-ocr-main")
import chess, chess.engine
import mss, numpy as np, cv2
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen
from ultralytics import YOLO
from chess_ocr_detection import process_results

STOCKFISH = r"C:\chess_helper\stockfish\stockfish\stockfish-windows-x86-64.exe"
MODEL = r"C:\Users\L\Desktop\2d-chess-ocr-main\finetuned-models\yolo26n-finetuned.pt"

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        from PyQt5.QtWidgets import QDesktopWidget
        g = QDesktopWidget().screenGeometry()
        self.setGeometry(g)
        self.arrow = None
    def set_arrow(self, c): self.arrow = c; self.update()
    def paintEvent(self, e):
        if not self.arrow: return
        x1,y1,x2,y2 = self.arrow
        p = QPainter(self); p.setPen(QPen(QColor(255,50,50,255),12)); p.drawLine(x1,y1,x2,y2)
        import math
        ang=math.atan2(y2-y1,x2-x1); s=20
        for da in (2.6,3.7):
            ax=x2-s*math.cos(ang+da); ay=y2-s*math.sin(ang+da); p.drawLine(int(x2),int(y2),int(ax),int(ay))

def square_to_pixel(sq, board_xyxy):
    x1,y1,x2,y2 = board_xyxy
    bw=x2-x1; bh=y2-y1
    col=chess.square_file(sq); row=7-chess.square_rank(sq); cell=bw/8.0
    return int(x1+col*cell+cell/2), int(y1+row*cell+cell/2)

def main():
    app=QApplication(sys.argv); overlay=Overlay(); overlay.show(); overlay.raise_()
    model=YOLO(MODEL)
    sct=mss.MSS()
    engine=chess.engine.SimpleEngine.popen_uci(STOCKFISH)
    mon = sct.monitors[1]
    print("Auto mode (YOLO OCR). Ctrl+C to stop.")
    last_fen = None
    fen_stable = 0
    try:
        while True:
            shot=sct.grab(mon)
            img=np.array(shot)[:,:, :3]
            results=model.predict(img, conf=0.25, verbose=False)
            detections, _ = process_results(results[0])
            if not detections:
                print("no board detected"); time.sleep(0.5); continue
            d = detections[0]
            fen = d.fen
            board_xyxy = d.board_xyxy
            if fen == last_fen:
                fen_stable += 1
            else:
                last_fen = fen; fen_stable = 1
            if fen_stable < 3:
                time.sleep(0.1); continue
            try:
                board=chess.Board(fen)
            except ValueError:
                print("bad fen", fen); time.sleep(0.5); continue
            ranks = fen.split()[0].split('/')
            try:
                res=engine.play(board,chess.engine.Limit(time=0.05))
                move=res.move
            except Exception as e:
                print("engine err",e); time.sleep(0.5); continue
            if not move:
                time.sleep(0.1); continue
            # validate move origin has a piece of side to move
            p = board.piece_at(move.from_square)
            if p is None or p.color != board.turn or not board.is_legal(move):
                time.sleep(0.1); continue
            x1,y1=square_to_pixel(move.from_square,board_xyxy)
            x2,y2=square_to_pixel(move.to_square,board_xyxy)
            overlay.set_arrow((x1,y1,x2,y2))
            app.processEvents()
            print("Best:",board.san(move))
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        engine.quit()

if __name__=="__main__":
    main()
