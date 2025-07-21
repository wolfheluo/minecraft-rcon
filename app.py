from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import json
import datetime
import os
import socket
import time
import struct
import threading
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'minecraft-rcon-secret-key-2025')

RCON_HOST = os.getenv('RCON_HOST', 'localhost')
RCON_PORT = int(os.getenv('RCON_PORT', 25575))
RCON_PASSWORD = os.getenv('RCON_PASSWORD', '')
CONSOLE_PASSWORD = 'supernova'

class SimpleRcon:
    """簡單的 RCON 客戶端實作，避免多執行緒問題"""
    
    def __init__(self, host, port, password, timeout=10):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.socket = None
        self.request_id = 1
        
    def connect(self):
        """連線到 RCON 伺服器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            
            # 發送認證封包
            auth_packet = self._create_packet(3, self.password)  # 3 = SERVERDATA_AUTH
            self.socket.send(auth_packet)
            
            # 讀取認證回應
            response = self._read_packet()
            if response is None or response[0] != self.request_id:
                raise Exception("RCON 認證失敗")
            
            return True
        except Exception as e:
            if self.socket:
                self.socket.close()
                self.socket = None
            raise Exception(f"無法連線到 RCON: {str(e)}")
    
    def command(self, cmd):
        """執行 RCON 指令"""
        if not self.socket:
            raise Exception("未連線到 RCON")
        
        try:
            # 發送指令封包
            self.request_id += 1
            cmd_packet = self._create_packet(2, cmd)  # 2 = SERVERDATA_EXECCOMMAND
            self.socket.send(cmd_packet)
            
            # 讀取回應
            response = self._read_packet()
            if response is None:
                return ""
            
            return response[2].decode('utf-8', errors='replace')
        except Exception as e:
            raise Exception(f"執行指令失敗: {str(e)}")
    
    def disconnect(self):
        """斷線"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def _create_packet(self, packet_type, data):
        """創建 RCON 封包"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        packet_id = self.request_id
        packet = struct.pack('<ii', packet_id, packet_type) + data + b'\x00\x00'
        return struct.pack('<i', len(packet)) + packet
    
    def _read_packet(self):
        """讀取 RCON 封包"""
        try:
            # 讀取封包長度
            length_data = self._recv_all(4)
            if not length_data:
                return None
            
            length = struct.unpack('<i', length_data)[0]
            if length < 10:  # 最小封包大小
                return None
            
            # 讀取封包內容
            packet_data = self._recv_all(length)
            if not packet_data:
                return None
            
            packet_id, packet_type = struct.unpack('<ii', packet_data[:8])
            payload = packet_data[8:-2]  # 移除結尾的兩個 null 字節
            
            return (packet_id, packet_type, payload)
        except Exception:
            return None
    
    def _recv_all(self, n):
        """確保接收完整的數據"""
        data = b''
        while len(data) < n:
            chunk = self.socket.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data

def safe_rcon_command(command, timeout=10):
    """安全的 RCON 指令執行函數，適用於多執行緒環境"""
    rcon = None
    try:
        rcon = SimpleRcon(RCON_HOST, RCON_PORT, RCON_PASSWORD, timeout)
        rcon.connect()
        response = rcon.command(command)
        return {"success": True, "response": response if response else "指令執行成功（無回應）"}
    except socket.timeout:
        return {"success": False, "error": "連線逾時"}
    except ConnectionRefusedError:
        return {"success": False, "error": "無法連線到 Minecraft 伺服器，請檢查伺服器是否開啟 RCON"}
    except Exception as e:
        error_msg = str(e)
        if "認證失敗" in error_msg:
            return {"success": False, "error": "RCON 密碼錯誤"}
        return {"success": False, "error": f"RCON 錯誤：{error_msg}"}
    finally:
        if rcon:
            rcon.disconnect()

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

@app.route('/')
def index():
    """首頁 - 顯示伺服器狀態和地圖"""
    return render_template('index.html')

@app.route('/console')
def console():
    """控制台頁面 - 需要密碼驗證"""
    if not session.get('authenticated'):
        return render_template('login.html')
    return render_template('console.html')

@app.route('/login', methods=['POST'])
def login():
    """處理登入驗證"""
    password = request.form.get('password')
    if password == CONSOLE_PASSWORD:
        session['authenticated'] = True
        return redirect(url_for('console'))
    else:
        return render_template('login.html', error="密碼錯誤")

@app.route('/logout')
def logout():
    """登出"""
    session.pop('authenticated', None)
    return redirect(url_for('index'))

@app.route('/rcon', methods=['POST'])
def rcon_control():
    command = request.form.get('command') or request.json.get('command')
    
    if command:
        result = safe_rcon_command(command)
        if result["success"]:
            log_command(command, result["response"])
            output = result["response"]
        else:
            log_command(command, "", result["error"])
            output = f"❌ {result['error']}"
    else:
        output = "未提供指令"
    
    if request.is_json:
        return jsonify({"success": result.get("success", False), "response": output})
    else:
        return render_template('console.html', output=output)

@app.route('/api/server-status')
def server_status():
    """檢查伺服器狀態的 API 端點"""
    result = safe_rcon_command("list")
    if result["success"]:
        return jsonify({"status": "online", "players": result["response"]})
    else:
        return jsonify({"status": "offline", "error": result["error"]})

@app.route('/api/players')
def get_players():
    """獲取在線玩家列表的 API 端點"""
    result = safe_rcon_command("list")
    if result["success"]:
        response = result["response"]
        # 解析玩家列表
        players = []
        if response:
            # 通常格式是: "There are X of a max of Y players online: player1, player2, player3"
            if ":" in response:
                player_part = response.split(":")[-1].strip()
                if player_part and player_part != "":
                    players = [name.strip() for name in player_part.split(",") if name.strip()]
        return jsonify({"success": True, "players": players})
    else:
        return jsonify({"success": False, "error": result["error"], "players": []})

@app.route('/api/test-connection')
def test_connection():
    """測試 RCON 連線的 API 端點"""
    result = safe_rcon_command("list")
    
    connection_info = {
        "host": RCON_HOST,
        "port": RCON_PORT,
        "password_set": bool(RCON_PASSWORD),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if result["success"]:
        return jsonify({
            "success": True, 
            "message": "RCON 連線正常",
            "connection_info": connection_info,
            "test_response": result["response"]
        })
    else:
        return jsonify({
            "success": False, 
            "message": "RCON 連線失敗",
            "connection_info": connection_info,
            "error": result["error"]
        }), 500

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """API 端點用於執行指令"""
    data = request.get_json()
    command = data.get('command', '')
    
    if not command:
        return jsonify({"error": "未提供指令"}), 400
    
    result = safe_rcon_command(command)
    if result["success"]:
        log_command(command, result["response"])
        return jsonify({"success": True, "response": result["response"]})
    else:
        log_command(command, "", result["error"])
        return jsonify({"success": False, "error": result["error"]}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5020, debug=False)
