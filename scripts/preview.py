#!/usr/bin/env python3
"""試作サイトをローカルサーバーで開く（目視確認用）。
  python3 scripts/preview.py <slug> [port]
"""
import functools, http.server, socketserver, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
slug = sys.argv[1] if len(sys.argv) > 1 else sys.exit("使い方: preview.py <slug>")
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
d = ROOT / "prospects" / slug / "site"
if not d.exists(): sys.exit(f"エラー: {d} がありません")
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(d))
print(f"http://localhost:{port}/  (Ctrl+C で終了)")
socketserver.TCPServer(("", port), h).serve_forever()
