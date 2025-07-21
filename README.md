# Minecraft RCON 管理控制台

一個美觀且功能豐富的 Minecraft 伺服器管理介面，透過 RCON 協議連線到 Minecraft 伺服器進行管理。

## 功能特色

### 🎮 美觀的使用者介面
- 現代化的響應式設計
- 漸層背景和動畫效果
- 即時伺服器狀態指示器
- 深色主題的指令輸出面板

### ⚡ 快速動作
- **玩家列表** - 查看目前線上玩家
- **保存世界** - 立即保存遊戲世界
- **天氣控制** - 設定為晴天
- **時間控制** - 設定為白天或夜晚
- **伺服器管理** - 安全關閉伺服器

### 👥 玩家管理
- **踢出玩家** - 將玩家踢出伺服器
- **封鎖玩家** - 禁止玩家進入伺服器
- **OP 權限管理** - 給予或移除管理員權限

### 🌍 世界管理
- **難度設定** - 和平/簡單/普通/困難模式
- **自訂指令** - 執行任何 Minecraft 指令

## 安裝與設定

### 必要條件
- Python 3.7 或更高版本
- Minecraft 伺服器（已開啟 RCON）

### 安裝步驟

1. 克隆或下載此專案
2. 安裝必要套件：
   ```bash
   pip install -r requirements.txt
   ```

3. 修改 `app.py` 中的伺服器設定：
   ```python
   RCON_HOST = "你的伺服器IP"
   RCON_PORT = 25575  # 你的 RCON 端口
   RCON_PASSWORD = "你的RCON密碼"
   ```

4. 執行應用程式：
   ```bash
   python app.py
   ```

5. 在瀏覽器中開啟 `http://localhost:5020`

## Minecraft 伺服器 RCON 設定

在你的 Minecraft 伺服器的 `server.properties` 檔案中添加以下設定：

```properties
enable-rcon=true
rcon.port=25575
rcon.password=你的安全密碼
```

重新啟動伺服器後，RCON 功能就會生效。

## 使用方法

### 快速動作
點選預設的按鈕即可執行常用指令，如查看玩家列表、保存世界等。

### 玩家管理
在對應的輸入框中輸入玩家名稱，然後點選相應的動作按鈕。

### 自訂指令
在「自訂指令」區域輸入任何有效的 Minecraft 指令，系統會自動執行並顯示結果。

## 常用指令範例

- `list` - 顯示線上玩家
- `weather clear` - 設定晴天
- `time set day` - 設定為白天
- `gamemode creative [玩家名稱]` - 設定創造模式
- `tp [玩家1] [玩家2]` - 傳送玩家
- `give [玩家] [物品] [數量]` - 給予物品

## 安全注意事項

- 請確保 RCON 密碼足夠強壯
- 建議只在私人網路中使用
- 定期更新密碼
- 不要將 RCON 端口暴露在公共網路上

## API 端點

此應用程式也提供 REST API：

- `GET /api/server-status` - 取得伺服器狀態
- `POST /api/execute` - 執行指令（JSON 格式）

## 技術資訊

- **後端框架**: Flask
- **RCON 函式庫**: mcrcon
- **前端**: HTML5 + CSS3 + JavaScript
- **設計**: 響應式設計，支援行動裝置

## 授權

此專案採用 MIT 授權條款。

## 支援

如果您遇到任何問題，請確認：
1. Minecraft 伺服器的 RCON 設定正確
2. 網路連線正常
3. 防火牆允許相關端口通行

---

製作者：GitHub Copilot 🤖
