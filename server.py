import json, http.server, socketserver, chess, chess.engine, pyautogui, time, os

STOCKFISH = r"C:\chess_helper\stockfish\stockfish\stockfish-windows-x86-64.exe"
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH)
CONFIG = r"C:\chess_helper\config.json"

def board_rect():
    if os.path.exists(CONFIG):
        cfg=json.load(open(CONFIG))
        return tuple(cfg.get("rect",(0,0,800,800)))
    return (0,0,800,800)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/fen":
            n = int(self.headers.get("Content-Length", 0))
            fen = self.rfile.read(n).decode()
            try:
                board = chess.Board(fen)
                res = engine.play(board, chess.engine.Limit(time=0.1))
                move = res.move.uci() if res.move else ""
            except Exception as e:
                move = ""
            data = json.dumps({"move": move}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/click":
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n).decode()
            try:
                data = json.loads(body)
                move = data["move"]
                flip = data.get("flip", False)
            except Exception:
                move = body
                flip = False
            try:
                rx,ry,rw,rh = board_rect()
                cell = rw/8.0
                def sq_px(s):
                    col = ord(s[0])-97
                    row = 8-int(s[1])
                    if flip:
                        col = 7-col
                        row = 7-row
                    return (rx+col*cell+cell/2, ry+row*cell+cell/2)
                x1,y1 = sq_px(move[0:2])
                x2,y2 = sq_px(move[2:4])
                pyautogui.moveTo(x1,y1,duration=0.05)
                pyautogui.mouseDown()
                pyautogui.moveTo(x2,y2,duration=0.1)
                pyautogui.mouseUp()
            except Exception as e:
                pass
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
        else:
            self.send_response(404); self.end_headers()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    def log_message(self, *a): pass

with socketserver.TCPServer(("", 8765), Handler) as httpd:
    print("Server on http://127.0.0.1:8765")
    httpd.serve_forever()
