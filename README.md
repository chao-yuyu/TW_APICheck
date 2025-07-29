# 🌦️ 台灣天氣降雨機率API

一個即時抓取台灣中央氣象署天氣資料的API服務，能夠獲取今天的降雨機率並判斷是否會下雨。

## 📋 功能特色

- 🌧️ **即時天氣資料**：爬取中央氣象署官方網站
- 🎯 **智能判斷**：降雨機率≥50%自動判定為"rain"，否則為"no_rain"
- 🏙️ **支援全台縣市**：涵蓋22個縣市的天氣資料
- 🚀 **RESTful API**：簡單易用的HTTP API接口
- 🔄 **雙重爬蟲策略**：結合requests和selenium確保資料獲取成功
- 🌐 **中文支援**：完整支援中文城市名稱，自動處理URL編碼

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 啟動API服務

```bash
python app.py
```

服務將在 `http://localhost:5000` 啟動

## 📡 API端點詳細說明

### 1. API首頁 - 查看API資訊
```http
GET /
```

**功能**：提供API概覽、使用說明和端點列表

**回應範例**：
```json
{
  "message": "台灣天氣降雨機率API",
  "description": "獲取台灣各縣市的降雨機率，判斷是否會下雨（≥50%機率）",
  "endpoints": {
    "/weather": "獲取預設城市（台北市）的天氣狀態",
    "/weather/<city>": "獲取指定城市的天氣狀態",
    "/cities": "獲取支援的城市列表",
    "/encode/<city>": "獲取城市名稱的URL編碼（測試用）"
  },
  "usage_examples": {
    "直接中文": "http://localhost:5000/weather/臺北市",
    "URL編碼": "http://localhost:5000/weather/%E8%87%BA%E5%8C%97%E5%B8%82",
    "說明": "✅ 可以直接使用中文，瀏覽器會自動編碼"
  }
}
```

### 2. 預設天氣查詢 - 台北市天氣
```http
GET /weather
```

**功能**：快速獲取台北市的天氣狀態，無需指定城市參數

**使用範例**：
```bash
curl http://localhost:5000/weather
```

**回應範例**：
```json
{
  "status": "success",
  "rain_probability": 65,
  "will_rain": true,
  "message": "rain",
  "city": "臺北市"
}
```

### 3. 指定城市天氣查詢 - 主要功能
```http
GET /weather/<city>
```

**功能**：獲取指定城市的降雨機率和天氣狀態

**參數說明**：
- `city`：城市名稱（支援中文，如：臺北市、高雄市）
- 支援直接中文輸入，瀏覽器會自動處理URL編碼

**使用範例**：
```bash
# 方法1：直接使用中文（推薦）
curl "http://localhost:5000/weather/臺北市"
curl "http://localhost:5000/weather/高雄市"
curl "http://localhost:5000/weather/臺中市"

# 方法2：手動URL編碼
curl "http://localhost:5000/weather/%E8%87%BA%E5%8C%97%E5%B8%82"
```

**成功回應**：
```json
{
  "status": "success",
  "rain_probability": 75,
  "will_rain": true,
  "message": "rain",
  "city": "臺北市"
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

### 4. 支援城市列表
```http
GET /cities
```

**功能**：查看所有支援的台灣縣市列表

**使用範例**：
```bash
curl http://localhost:5000/cities
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

### 5. URL編碼工具 - 測試輔助
```http
GET /encode/<city>
```

**功能**：將中文城市名稱轉換為URL編碼格式，用於測試和調試

**使用範例**：
```bash
curl http://localhost:5000/encode/臺北市
```

**回應範例**：
```json
{
  "status": "success",
  "original": "臺北市",
  "encoded": "%E8%87%BA%E5%8C%97%E5%B8%82",
  "encoded_url": "http://localhost:5000/weather/%E8%87%BA%E5%8C%97%E5%B8%82",
  "direct_url": "http://localhost:5000/weather/臺北市",
  "note": "兩種URL都可以使用"
}
```

### 6. 健康檢查
```http
GET /health
```

**功能**：檢查API服務是否正常運行

**使用範例**：
```bash
curl http://localhost:5000/health
```

**回應範例**：
```json
{
  "status": "healthy",
  "message": "API服務正常運行",
  "encoding_support": "✅ 支援中文城市名稱直接輸入"
}
```

## 🌟 完整使用範例

### 場景1：檢查台北市是否會下雨
```bash
# 請求
curl "http://localhost:5000/weather/臺北市"

# 回應
{
  "status": "success",
  "rain_probability": 85,
  "will_rain": true,
  "message": "rain",
  "city": "臺北市"
}
```

### 場景2：批量查詢多個城市
```bash
# 查詢台北市
curl "http://localhost:5000/weather/臺北市"

# 查詢高雄市
curl "http://localhost:5000/weather/高雄市"

# 查詢台中市
curl "http://localhost:5000/weather/臺中市"
```

### 場景3：在網頁瀏覽器中使用
```
直接在瀏覽器網址列輸入：
http://localhost:5000/weather/臺北市
http://localhost:5000/weather/高雄市
```

### 場景4：JavaScript/Ajax請求
```javascript
// 使用fetch API
fetch('http://localhost:5000/weather/臺北市')
  .then(response => response.json())
  .then(data => {
    console.log('降雨機率:', data.rain_probability + '%');
    console.log('會下雨嗎:', data.will_rain ? '會' : '不會');
  });

// 使用jQuery
$.get('http://localhost:5000/weather/臺北市', function(data) {
  if (data.status === 'success') {
    alert(`${data.city}降雨機率: ${data.rain_probability}%`);
  }
});
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

- **Web框架**：Flask + Flask-CORS
- **爬蟲技術**：
  - 主要：Selenium WebDriver（處理動態內容）
  - 備用：requests + BeautifulSoup（靜態內容）
- **目標網站**：[中央氣象署縣市預報](https://www.cwa.gov.tw/V8/C/W/County/index.html)
- **資料解析**：正則表達式 + HTML解析
- **編碼處理**：UTF-8 + URL編碼自動轉換

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
curl http://localhost:5000/health

# 測試預設城市
curl http://localhost:5000/weather

# 測試指定城市
curl "http://localhost:5000/weather/臺北市"

# 查看支援城市
curl http://localhost:5000/cities
```

### API測試腳本
```bash
#!/bin/bash
echo "=== API測試腳本 ==="

echo "1. 健康檢查"
curl http://localhost:5000/health
echo -e "\n"

echo "2. 預設城市（台北市）"
curl http://localhost:5000/weather
echo -e "\n"

echo "3. 指定城市測試"
curl "http://localhost:5000/weather/高雄市"
echo -e "\n"

echo "4. 支援城市列表"
curl http://localhost:5000/cities
echo -e "\n"

echo "5. 錯誤測試（不支援的城市）"
curl "http://localhost:5000/weather/不存在市"
echo -e "\n"
```

## ⚠️ 注意事項

1. **網站結構變化**：中央氣象署網站如有改版，可能需要調整爬蟲邏輯
2. **請求頻率**：建議適度使用，避免對官方網站造成負荷
3. **Chrome瀏覽器**：使用selenium時需要安裝Chrome瀏覽器和ChromeDriver
4. **網路連線**：需要穩定的網路連線來存取氣象署網站
5. **城市名稱**：請使用完整正確的縣市名稱（如"臺北市"而非"台北"）
6. **編碼問題**：API完全支援中文，瀏覽器會自動處理URL編碼

## 🔍 故障排除

### 常見問題

**Q: 城市名稱錯誤怎麼辦？**
```bash
# 查看支援的城市列表
curl http://localhost:5000/cities

# 使用完整縣市名稱，例如：
# ✅ 正確："臺北市"、"高雄市"
# ❌ 錯誤："台北"、"高雄"
```

**Q: 爬蟲失敗怎麼處理？**
1. 檢查網路連線
2. 確認Chrome瀏覽器已安裝
3. 檢查氣象署網站是否正常運作
4. 查看API日誌訊息以了解具體錯誤

**Q: 中文編碼問題？**
- API完全支援中文城市名稱
- 可以直接在瀏覽器網址列輸入中文
- 程式會自動處理URL編碼轉換

## 📄 授權

本專案僅供學習和研究使用，請遵守相關網站的使用條款。 