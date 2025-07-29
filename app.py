from flask import Flask, jsonify, request
from flask_cors import CORS
from weather_scraper import WeatherScraper
import json
import urllib.parse

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 初始化天氣爬蟲
weather_scraper = WeatherScraper()

# 台灣縣市列表
TAIWAN_CITIES = [
    "基隆市", "新北市", "臺北市", "桃園市", "新竹縣", "新竹市", 
    "苗栗縣", "臺中市", "南投縣", "彰化縣", "雲林縣", "嘉義縣", 
    "嘉義市", "臺南市", "高雄市", "屏東縣", "臺東縣", "花蓮縣", 
    "宜蘭縣", "澎湖縣", "金門縣", "連江縣"
]

def decode_city_name(city_name):
    """解碼城市名稱，處理URL編碼"""
    try:
        # Flask會自動解碼，但確保正確處理
        decoded_city = urllib.parse.unquote(city_name, encoding='utf-8')
        return decoded_city.strip()
    except Exception as e:
        print(f"城市名稱解碼錯誤: {e}")
        return city_name

@app.route('/', methods=['GET'])
def home():
    """API首頁"""
    return jsonify({
        "message": "台灣天氣降雨機率API",
        "description": "獲取台灣各縣市的降雨機率，判斷是否會下雨（>60%機率）",
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
        },
        "example": {
            "url": "/weather/臺北市",
            "response": {
                "status": "success",
                "city": "臺北市",
                "rain_probability": 75,
                "will_rain": True,
                "message": "下雨"
            }
        }
    })

@app.route('/weather', methods=['GET'])
def get_default_weather():
    """獲取預設城市（台北市）的天氣狀態"""
    return get_weather_by_city("臺北市")

@app.route('/weather/<path:city>', methods=['GET'])
def get_weather_by_city(city):
    """獲取指定城市的天氣狀態"""
    try:
        # 解碼城市名稱
        decoded_city = decode_city_name(city)
        
        print(f"接收到的城市參數: {city}")
        print(f"解碼後的城市名稱: {decoded_city}")
        
        # 檢查城市是否在支援列表中
        if decoded_city not in TAIWAN_CITIES:
            return jsonify({
                "status": "error",
                "message": f"不支援的城市：{decoded_city}",
                "received_parameter": city,
                "decoded_city": decoded_city,
                "supported_cities": TAIWAN_CITIES,
                "tip": "請使用正確的城市名稱，如：臺北市、高雄市等"
            }), 400
        
        # 獲取天氣資料
        result = weather_scraper.get_rain_status(decoded_city)
        
        if result["status"] == "error":
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"服務錯誤：{str(e)}",
            "city": city,
            "decoded_city": decode_city_name(city) if city else None
        }), 500

@app.route('/cities', methods=['GET'])
def get_supported_cities():
    """獲取支援的城市列表"""
    return jsonify({
        "status": "success",
        "cities": TAIWAN_CITIES,
        "count": len(TAIWAN_CITIES),
        "usage_note": "可以直接使用中文城市名稱，如: /weather/臺北市"
    })

@app.route('/encode/<city>', methods=['GET'])
def get_encoded_city(city):
    """獲取城市名稱的URL編碼（測試和調試用）"""
    try:
        encoded = urllib.parse.quote(city, encoding='utf-8')
        return jsonify({
            "status": "success",
            "original": city,
            "encoded": encoded,
            "encoded_url": f"http://localhost:5000/weather/{encoded}",
            "direct_url": f"http://localhost:5000/weather/{city}",
            "note": "兩種URL都可以使用"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"編碼錯誤：{str(e)}",
            "city": city
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        "status": "healthy",
        "message": "API服務正常運行",
        "encoding_support": "✅ 支援中文城市名稱直接輸入"
    })

@app.errorhandler(404)
def not_found(error):
    """404錯誤處理"""
    return jsonify({
        "status": "error",
        "message": "找不到請求的端點",
        "available_endpoints": ["/", "/weather", "/weather/<city>", "/cities", "/encode/<city>", "/health"],
        "tip": "城市名稱可以直接使用中文，如: /weather/臺北市"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500錯誤處理"""
    return jsonify({
        "status": "error",
        "message": "內部伺服器錯誤"
    }), 500

if __name__ == '__main__':
    print("🌦️  台灣天氣降雨機率API啟動中...")
    print("📍 支援的城市:", ", ".join(TAIWAN_CITIES[:5]), "等", len(TAIWAN_CITIES), "個城市")
    print("🔗 API端點:")
    print("   - GET /weather - 獲取台北市天氣")
    print("   - GET /weather/<city> - 獲取指定城市天氣")
    print("   - GET /cities - 獲取支援城市列表")
    print("   - GET /encode/<city> - 獲取城市URL編碼")
    print("   - GET /health - 健康檢查")
    print("\n📋 使用範例:")
    print("   🎯 直接中文: curl 'http://localhost:5000/weather/臺北市'")
    print("   🔗 URL編碼: curl http://localhost:5000/weather/%E8%87%BA%E5%8C%97%E5%B8%82")
    print("   ✨ 兩種方式都支援！")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 