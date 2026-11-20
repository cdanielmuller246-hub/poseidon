"""Simulador local de los formularios de control del ESP01.

Uso: python esp01_simulator.py
Los formularios del panel deben apuntar a http://127.0.0.1:8000.
El estado de las torres se conserva mientras este proceso siga en ejecución.
"""

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json


HOST = "127.0.0.1"
PORT = 8000
TOWER_COMMANDS = {
    "command11": ("1", "ON"), "command10": ("1", "OFF"),
    "command21": ("2", "ON"), "command20": ("2", "OFF"),
    "command31": ("3", "ON"), "command30": ("3", "OFF"),
    "command41": ("4", "ON"), "command40": ("4", "OFF"),
}
states = {"1": False, "2": False, "3": False, "4": False}


class ESP01Simulator(BaseHTTPRequestHandler):
    def send_json(self, payload):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") == "/status":
            self.send_json({"states": states})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Simulador ESP01 activo. Abre el panel de control para enviar ordenes.")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        fields = parse_qs(body, keep_blank_values=True)
        password = fields.get("password", [""])[0]
        commands = {key: values[0] for key, values in fields.items() if key.startswith("command")}

        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] POST {self.path}")
        print(f"  Clave recibida: {password if password else '(vacía)'}")
        if commands:
            for name, value in commands.items():
                print(f"  Orden: {name} = {value}")
                mapping = TOWER_COMMANDS.get(name)
                if mapping and value == mapping[1]:
                    tower, state = mapping
                    states[tower] = state == "ON"
        else:
            print("  No se recibió ningún campo de orden.")

        self.send_json({"ok": True, "states": states})

    def log_message(self, format_string, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), ESP01Simulator)
    print(f"Simulador ESP01 listo en http://{HOST}:{PORT}")
    print("Las cuatro torres empiezan apagadas; el estado cambia al recibir cada orden.")
    print("Deja esta ventana abierta mientras haces la prueba. Ctrl+C para detenerlo.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSimulador detenido.")
    finally:
        server.server_close()
