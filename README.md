# 🌦️ 台灣天氣降雨機率API + 🚌 公車站牌API

一個整合台灣天氣資訊與公車動態資訊的API服務，提供即時天氣降雨機率判斷和公車站牌到站時間查詢。

## 📋 功能特色

### 🌦️ 天氣功能
- 🌧️ **即時天氣資料**：爬取中央氣象署官方網站
- 🎯 **智能判斷**：降雨機率≥50%自動判定為"rain"，否則為"no_rain"
- 🏙️ **支援全台縣市**：涵蓋22個縣市的天氣資料
- 🌐 **中文支援**：完整支援中文城市名稱，自動處理URL編碼

### 🚌 公車功能
- 🚏 **即時站牌資訊**：爬取台北市公車動態資訊系統
- ⏰ **到站時間預估**：提供各路線公車預估到站時間
- 🔄 **動態更新**：即時獲取最新的公車動態狀態
- 📍 **站牌查詢**：支援站牌ID查詢功能

### 🚀 技術特色
- 🚀 **FastAPI框架**：簡單易用的HTTP API接口
- 🔄 **雙重爬蟲策略**：結合requests和selenium確保資料獲取成功
- 🌐 **CORS支援**：允許跨域請求，方便前端整合

## 🚀 快速開始

### 安裝依賴

```bash
# 安裝基本依賴
pip install -r requirements.txt

# 如果需要公車站牌功能，額外安裝：
pip install selenium beautifulsoup4 chromedriver-autoinstaller
```

### 啟動API服務

```bash
python app.py
```

服務將在 `http://localhost:8000` 啟動，同時提供天氣查詢和公車站牌查詢功能

### 查看API文檔

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📡 API端點詳細說明

### 1. API首頁 - 查看API資訊
```http
GET /
```

**功能**：提供API概覽、使用說明和端點列表

**回應範例**：
```json
{
  "message": "台灣天氣降雨機率API + 公車站牌API",
  "description": "獲取台灣各縣市的降雨機率，判斷是否會下雨（>=50%機率）+ 公車站牌動態資訊",
  "endpoints": {
    "/weather": "獲取預設城市（台北市）的天氣狀態",
    "/weather/{city}": "獲取指定城市的天氣狀態",
    "/cities": "獲取支援的城市列表",
    "/encode/{city}": "獲取城市名稱的URL編碼（測試用）",
    "/bus_stop": "獲取公車站牌動態資訊（需要 slid 參數）"
  },
  "usage_examples": {
    "天氣_直接中文": "http://localhost:8000/weather/臺北市",
    "天氣_URL編碼": "http://localhost:8000/weather/%E8%87%BA%E5%8C%97%E5%B8%82",
    "公車站牌": "http://localhost:8000/bus_stop?slid=1417",
    "說明": "✅ 可以直接使用中文，瀏覽器會自動編碼"
  },
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### 2. 公車站牌動態資訊 - 🚌 新功能
```http
GET /bus_stop?slid={站牌ID}
```

**功能**：獲取台北市公車站牌的即時動態資訊，包含各路線到站時間

**參數說明**：
- `slid`：站牌ID（必填，整數）
- 站牌ID可從台北市公車動態資訊系統或相關APP獲得

**使用範例**：
```bash
# 查詢站牌ID 1417（民生西路口站）
curl 'http://localhost:8000/bus_stop?slid=1417'

# 查詢其他站牌
curl 'http://localhost:8000/bus_stop?slid=5678'
```

**成功回應**：
```json
[
  {
    "route": "292",
    "stop_name": "民生西路口",
    "direction": "去程",
    "eta": "將到站",
    "eta_flag": "Y"
  },
  {
    "route": "304承德",
    "stop_name": "民生西路口", 
    "direction": "去程",
    "eta": "7分",
    "eta_flag": "Y"
  },
  {
    "route": "63",
    "stop_name": "民生西路口",
    "direction": "去程",
    "eta": "將到站",
    "eta_flag": "Y"
  }
]
```

**回應欄位說明**：
- `route`：公車路線號碼
- `stop_name`：站牌名稱
- `direction`：行駛方向（去程/返程）
- `eta`：預估到站時間（如："3分"、"將到站"、"末班已過"）
- `eta_flag`：到站狀態標記

**錯誤回應**：
```json
{
  "detail": "爬蟲錯誤：無法獲取站牌資訊"
}
```

### 3. 預設天氣查詢 - 台北市天氣
```http
GET /weather
```

**功能**：快速獲取台北市的天氣狀態，無需指定城市參數

**使用範例**：
```bash
curl http://localhost:8000/weather
```

**回應範例**：
```json
{
  "status": "success",
  "rain_probability": 75,
  "will_rain": true,
  "message": "rain",
  "city": "臺北市"
}
```

### 4. 指定城市天氣查詢 - 主要功能
```http
GET /weather/{city}
```

**功能**：獲取指定城市的降雨機率和天氣狀態

**參數說明**：
- `city`：城市名稱（支援中文，如：臺北市、高雄市）
- 支援直接中文輸入，瀏覽器會自動處理URL編碼

**使用範例**：
```bash
# 方法1：直接使用中文（推薦）
curl "http://localhost:8000/weather/臺北市"
curl "http://localhost:8000/weather/高雄市"
curl "http://localhost:8000/weather/臺中市"

# 方法2：手動URL編碼
curl "http://localhost:8000/weather/%E8%87%BA%E5%8C%97%E5%B8%82"
```

**成功回應**：
```json
{
  "status": "success",
  "rain_probability": 65,
  "will_rain": true,
  "message": "rain",
  "city": "高雄市"
}
```

**錯誤回應（不支援的城市）**：
```json
{
  "status": "error",
  "message": "不支援的城市：台北",
  "received_parameter": "台北",
  "decoded_city": "台北",
  "supported_cities": ["基隆市", "新北市", "臺北市", "..."],
  "tip": "請使用正確的城市名稱，如：臺北市、高雄市等"
}
```

### 5. 支援城市列表
```http
GET /cities
```

**功能**：查看所有支援的台灣縣市列表

**使用範例**：
```bash
curl http://localhost:8000/cities
```

**回應範例**：
```json
{
  "status": "success",
  "cities": [
    "基隆市", "新北市", "臺北市", "桃園市", "新竹縣", "新竹市",
    "苗栗縣", "臺中市", "南投縣", "彰化縣", "雲林縣", "嘉義縣",
    "嘉義市", "臺南市", "高雄市", "屏東縣", "臺東縣", "花蓮縣",
    "宜蘭縣", "澎湖縣", "金門縣", "連江縣"
  ],
  "count": 22,
  "usage_note": "可以直接使用中文城市名稱，如: /weather/臺北市"
}
```

### 6. URL編碼工具 - 測試輔助
```http
GET /encode/{city}
```

**功能**：將中文城市名稱轉換為URL編碼格式，用於測試和調試

**使用範例**：
```bash
curl http://localhost:8000/encode/臺北市
```

**回應範例**：
```json
{
  "status": "success",
  "original": "臺北市",
  "encoded": "%E8%87%BA%E5%8C%97%E5%B8%82",
  "encoded_url": "http://localhost:8000/weather/%E8%87%BA%E5%8C%97%E5%B8%82",
  "direct_url": "http://localhost:8000/weather/臺北市",
  "note": "兩種URL都可以使用"
}
```

### 7. 健康檢查
```http
GET /health
```

**功能**：檢查API服務是否正常運行

**使用範例**：
```bash
curl http://localhost:8000/health
```

**回應範例**：
```json
{
  "status": "healthy",
  "message": "API服務正常運行",
  "encoding_support": "✅ 支援中文城市名稱直接輸入",
  "bus_stop_support": "✅ 支援公車站牌動態資訊查詢"
}
```

## 🌟 完整使用範例

### 場景1：檢查台北市是否會下雨
```bash
# 請求
curl "http://localhost:8000/weather/臺北市"

# 回應
{
  "status": "success",
  "rain_probability": 75,
  "will_rain": true,
  "message": "rain",
  "city": "臺北市"
}
```

### 場景2：查詢公車站牌動態資訊
```bash
# 請求 - 查詢民生西路口站（站牌ID: 1417）
curl 'http://localhost:8000/bus_stop?slid=1417'

# 回應
[
  {
    "route": "292",
    "stop_name": "民生西路口",
    "direction": "去程", 
    "eta": "將到站",
    "eta_flag": "Y"
  },
  {
    "route": "304承德",
    "stop_name": "民生西路口",
    "direction": "去程",
    "eta": "7分",
    "eta_flag": "Y"
  }
]
```

### 場景3：批量查詢多個城市天氣
```bash
# 查詢台北市
curl "http://localhost:8000/weather/臺北市"

# 查詢高雄市
curl "http://localhost:8000/weather/高雄市"

# 查詢台中市
curl "http://localhost:8000/weather/臺中市"
```

### 場景4：在網頁瀏覽器中使用
```
天氣查詢：
http://localhost:8000/weather/臺北市
http://localhost:8000/weather/高雄市

公車站牌查詢：
http://localhost:8000/bus_stop?slid=1417

查看交互式API文檔：
http://localhost:8000/docs
```

### 場景5：JavaScript/Ajax請求
```javascript
// 查詢天氣 - 使用fetch API
fetch('http://localhost:8000/weather/臺北市')
  .then(response => response.json())
  .then(data => {
    console.log('降雨機率:', data.rain_probability + '%');
    console.log('會下雨嗎:', data.will_rain ? '會' : '不會');
  });

// 查詢公車站牌 - 使用fetch API
fetch('http://localhost:8000/bus_stop?slid=1417')
  .then(response => response.json())
  .then(data => {
    data.forEach(bus => {
      console.log(`${bus.route}路線 - ${bus.eta}`);
    });
  });

// 使用jQuery查詢天氣
$.get('http://localhost:8000/weather/臺北市', function(data) {
  if (data.status === 'success') {
    alert(`${data.city}降雨機率: ${data.rain_probability}%`);
  }
});
```

### 場景6：Python requests
```python
import requests

# 查詢天氣
response = requests.get('http://localhost:8000/weather/臺北市')
data = response.json()

if data['status'] == 'success':
    print(f"{data['city']} 降雨機率: {data['rain_probability']}%")
    print(f"會下雨嗎: {'會' if data['will_rain'] else '不會'}")

# 查詢公車站牌
response = requests.get('http://localhost:8000/bus_stop?slid=1417')
bus_data = response.json()

print("公車動態資訊:")
for bus in bus_data:
    print(f"{bus['route']}路線 - {bus['direction']} - {bus['eta']}")
```

## 🏙️ 支援城市

- **北部**：基隆市、新北市、臺北市、桃園市、新竹縣、新竹市
- **中部**：苗栗縣、臺中市、南投縣、彰化縣
- **南部**：雲林縣、嘉義縣、嘉義市、臺南市、高雄市、屏東縣
- **東部**：臺東縣、花蓮縣、宜蘭縣
- **離島**：澎湖縣、金門縣、連江縣

⚠️ **注意**：請使用完整的縣市名稱（如"臺北市"而非"台北"）

## 🎯 降雨判斷規則

- **降雨機率 ≥ 50%** → `"will_rain": true`, `"message": "rain"`
- **降雨機率 < 50%** → `"will_rain": false`, `"message": "no_rain"`

## 📝 完整回應格式說明

### 成功回應格式
```json
{
  "status": "success",        // 狀態：success
  "rain_probability": 75,     // 降雨機率（0-100的整數）
  "will_rain": true,          // 是否會下雨（boolean）
  "message": "rain",          // 簡化訊息："rain" 或 "no_rain"
  "city": "臺北市"            // 查詢的城市名稱
}
```

### 錯誤回應格式
```json
{
  "status": "error",          // 狀態：error
  "message": "錯誤描述",       // 詳細錯誤訊息
  "city": "城市名稱",         // 查詢的城市（如果有）
  "received_parameter": "...", // 接收到的參數（僅城市錯誤時）
  "decoded_city": "...",      // 解碼後的城市名稱（僅城市錯誤時）
  "supported_cities": [...],  // 支援的城市列表（僅城市錯誤時）
  "tip": "使用建議"           // 使用提示（僅城市錯誤時）
}
```

## 🔧 技術架構

- **Web框架**：FastAPI + CORS中間件
- **ASGI服務器**：Uvicorn
- **爬蟲技術**：
  - 主要：Selenium WebDriver（處理動態內容）
  - 備用：requests + BeautifulSoup（靜態內容）
- **目標網站**：
  - 天氣資料：[中央氣象署縣市預報](https://www.cwa.gov.tw/V8/C/W/County/index.html)
  - 公車資料：[台北市公車動態資訊系統](https://pda5284.gov.taipei/MQS/stoplocation.jsp)
- **資料解析**：正則表達式 + HTML解析
- **編碼處理**：UTF-8 + URL編碼自動轉換
- **瀏覽器自動化**：ChromeDriver 自動安裝和配置
- **API文檔**：自動生成 Swagger UI 和 ReDoc

## 🛠️ 開發測試

### 測試爬蟲功能
```bash
python weather_scraper.py
```

### 測試API服務
```bash
# 啟動服務
python app.py

# 健康檢查
curl http://localhost:8000/health

# 測試預設城市天氣
curl http://localhost:8000/weather

# 測試指定城市天氣
curl "http://localhost:8000/weather/臺北市"

# 測試公車站牌查詢
curl 'http://localhost:8000/bus_stop?slid=1417'

# 查看支援城市
curl http://localhost:8000/cities

# 查看API文檔
open http://localhost:8000/docs
```

## ⚠️ 注意事項

### 天氣功能
1. **網站結構變化**：中央氣象署網站如有改版，可能需要調整爬蟲邏輯
2. **請求頻率**：建議適度使用，避免對官方網站造成負荷
3. **城市名稱**：請使用完整正確的縣市名稱（如"臺北市"而非"台北"）

### 公車功能
4. **站牌ID**：需要正確的台北市公車站牌ID，可從台北市公車APP或相關網站獲得
5. **服務範圍**：目前僅支援台北市公車系統，其他縣市暫不支援
6. **資料即時性**：公車動態資訊會隨時變動，建議即時查詢

### 技術需求
7. **Chrome瀏覽器**：使用selenium時需要安裝Chrome瀏覽器和ChromeDriver
8. **網路連線**：需要穩定的網路連線來存取氣象署和公車系統網站
9. **編碼問題**：API完全支援中文，瀏覽器會自動處理URL編碼
10. **端口變更**：FastAPI版本使用8000端口

## 🔍 故障排除

### 常見問題

**Q: 城市名稱錯誤怎麼辦？**
```bash
# 查看支援的城市列表
curl http://localhost:8000/cities

# 使用完整縣市名稱，例如：
# ✅ 正確："臺北市"、"高雄市"
# ❌ 錯誤："台北"、"高雄"
```

**Q: 公車站牌查詢失敗怎麼處理？**
```bash
# 確認站牌ID是否正確
curl 'http://localhost:8000/bus_stop?slid=1417'

# 常見問題：
# ✅ 正確：使用有效的台北市公車站牌ID
# ❌ 錯誤：使用不存在或其他縣市的站牌ID
# ❌ 錯誤：缺少slid參數或參數格式錯誤
```

**Q: 爬蟲失敗怎麼處理？**
1. 檢查網路連線
2. 確認Chrome瀏覽器已安裝
3. 檢查氣象署網站和公車系統是否正常運作
4. 查看API日誌訊息以了解具體錯誤

**Q: 中文編碼問題？**
- API完全支援中文城市名稱
- 可以直接在瀏覽器網址列輸入中文
- 程式會自動處理URL編碼轉換

## 📄 授權

本專案僅供學習和研究使用，請遵守相關網站的使用條款。 