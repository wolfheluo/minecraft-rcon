from flask import Flask, request, render_template, jsonify
from mcrcon import MCRcon
import json
import datetime
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__)

RCON_HOST = os.getenv('RCON_HOST', 'localhost')
RCON_PORT = int(os.getenv('RCON_PORT', 25575))
RCON_PASSWORD = os.getenv('RCON_PASSWORD', '')

def log_command(command, response, error=None):
    """記錄指令執行日誌"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "command": command,
        "response": response,
        "error": error
    }
    # 這裡可以將日誌寫入檔案或資料庫
    print(f"[{timestamp}] Command: {command}, Response: {response}")

@app.route('/', methods=['GET', 'POST'])
def rcon_control():
    output = ""
    if request.method == 'POST':
        command = request.form['command']
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
                response = mcr.command(command)
                output = response if response else "指令執行成功（無回應）"
                log_command(command, output)
        except Exception as e:
            output = f"❌ 連線錯誤：{e}"
            log_command(command, "", str(e))
    return render_template('index.html', output=output)

@app.route('/api/server-status')
def server_status():
    """檢查伺服器狀態的 API 端點"""
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command("list")
            return jsonify({"status": "online", "players": response})
    except Exception as e:
        return jsonify({"status": "offline", "error": str(e)})

@app.route('/api/players')
def get_players():
    """獲取在線玩家列表的 API 端點"""
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command("list")
            # 解析玩家列表
            players = []
            if response:
                # 通常格式是: "There are X of a max of Y players online: player1, player2, player3"
                if ":" in response:
                    player_part = response.split(":")[-1].strip()
                    if player_part and player_part != "":
                        players = [name.strip() for name in player_part.split(",") if name.strip()]
            return jsonify({"success": True, "players": players})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "players": []})

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """API 端點用於執行指令"""
    data = request.get_json()
    command = data.get('command', '')
    
    if not command:
        return jsonify({"error": "未提供指令"}), 400
    
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(command)
            log_command(command, response)
            return jsonify({"success": True, "response": response})
    except Exception as e:
        log_command(command, "", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5020, debug=True)
