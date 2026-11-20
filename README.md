# chess-com-auto-bot

Automated chess.com assistant: reads the board FEN directly from the page, computes the best move with Stockfish, highlights it, and auto-moves the mouse.

## How it works
1. Tampermonkey script (`helper.user.js`) reads FEN from chess.com DOM and sends it to a local Python server.
2. Server (`server.py`) runs Stockfish and returns the best move.
3. Tampermonkey highlights the move; Python clicks the squares via pyautogui.

## Setup
1. Install Python 3.10+ and add to PATH.
2. Install deps: `pip install chess python-chess pyautogui`
3. Install Stockfish and put binary at `C:\chess_helper\stockfish\stockfish\stockfish-windows-x86-64.exe` (or edit path in server.py).
4. Install Tampermonkey extension, create new script, paste `helper.user.js`.
5. Run `python server.py`.
6. Open chess.com — best move highlighted and auto-played.

## Files
- `server.py` — local HTTP server + Stockfish + auto-click
- `helper.user.js` — Tampermonkey bridge
- `auto.py` — standalone YOLO OCR mode (optional)
- `helper.py` — manual FEN mode
- `get_coords.py` — board coordinate capture

## License
MIT
