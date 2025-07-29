from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import chromedriver_autoinstaller
from weather_scraper import WeatherScraper
import json
import urllib.parse
from typing import Dict, Any, List

# 自動安裝 ChromeDriver
chromedriver_autoinstaller.install()

# 創建單一的 FastAPI 應用實例
app = FastAPI(
    title="台灣天氣降雨機率API + 公車站牌API",
    description="獲取台灣各縣市的降雨機率，判斷是否會下雨（>=50%機率）+ 公車站牌動態資訊",
    version="1.0.0"
)

# 允許跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化天氣爬蟲
weather_scraper = WeatherScraper()

# 台灣縣市列表
TAIWAN_CITIES = [
    "基隆市", "新北市", "臺北市", "桃園市", "新竹縣", "新竹市", 
    "苗栗縣", "臺中市", "南投縣", "彰化縣", "雲林縣", "嘉義縣", 
    "嘉義市", "臺南市", "高雄市", "屏東縣", "臺東縣", "花蓮縣", 
    "宜蘭縣", "澎湖縣", "金門縣", "連江縣"
]

# 公車站牌動態資訊爬蟲函數
async def fetch_stop_dynamic(slid: int):
    url = f'https://pda5284.gov.taipei/MQS/stoplocation.jsp?slid={slid}'

    options = Options()
    options.add_argument("--headless")  # 無頭模式
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        rows = soup.select('tr.ttego1, tr.ttego2')
        data = []
        for tr in rows:
            cols = tr.find_all('td')
            if len(cols) >= 4:
                eta_td = cols[3]
                data.append({
                    'route': cols[0].text.strip(),
                    'stop_name': cols[1].text.strip(),
                    'direction': cols[2].text.strip(),
                    'eta': eta_td.text.strip(),
                    'eta_flag': eta_td.get('data-deptimen1', '')
                })
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬蟲錯誤：{str(e)}")
    finally:
        driver.quit()

# 公車站牌 API 端點
@app.get("/bus_stop")
async def get_bus_stop(slid: int = Query(..., description="站牌 ID")):
    """獲取公車站牌動態資訊"""
    return await fetch_stop_dynamic(slid)

def decode_city_name(city_name: str) -> str:
    """解碼城市名稱，處理URL編碼"""
    try:
        # FastAPI會自動解碼，但確保正確處理
        decoded_city = urllib.parse.unquote(city_name, encoding='utf-8')
        return decoded_city.strip()
    except Exception as e:
        print(f"城市名稱解碼錯誤: {e}")
        return city_name

@app.get("/", response_model=Dict[str, Any])
async def home():
    """API首頁"""
    return {
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

@app.get("/weather", response_model=Dict[str, Any])
async def get_default_weather():
    """獲取預設城市（台北市）的天氣狀態"""
    return await get_weather_by_city("臺北市")

@app.get("/weather/{city}", response_model=Dict[str, Any])
async def get_weather_by_city(city: str = Path(..., description="城市名稱")):
    """獲取指定城市的天氣狀態"""
    try:
        # 解碼城市名稱
        decoded_city = decode_city_name(city)
        
        print(f"接收到的城市參數: {city}")
        print(f"解碼後的城市名稱: {decoded_city}")
        
        # 檢查城市是否在支援列表中
        if decoded_city not in TAIWAN_CITIES:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": f"不支援的城市：{decoded_city}",
                    "received_parameter": city,
                    "decoded_city": decoded_city,
                    "supported_cities": TAIWAN_CITIES,
                    "tip": "請使用正確的城市名稱，如：臺北市、高雄市等"
                }
            )
        
        # 獲取天氣資料
        result = weather_scraper.get_rain_status(decoded_city)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"服務錯誤：{str(e)}",
                "city": city,
                "decoded_city": decode_city_name(city) if city else None
            }
        )

@app.get("/cities", response_model=Dict[str, Any])
async def get_supported_cities():
    """獲取支援的城市列表"""
    return {
        "status": "success",
        "cities": TAIWAN_CITIES,
        "count": len(TAIWAN_CITIES),
        "usage_note": "可以直接使用中文城市名稱，如: /weather/臺北市"
    }

@app.get("/encode/{city}", response_model=Dict[str, Any])
async def get_encoded_city(city: str = Path(..., description="要編碼的城市名稱")):
    """獲取城市名稱的URL編碼（測試和調試用）"""
    try:
        encoded = urllib.parse.quote(city, encoding='utf-8')
        return {
            "status": "success",
            "original": city,
            "encoded": encoded,
            "encoded_url": f"http://localhost:8000/weather/{encoded}",
            "direct_url": f"http://localhost:8000/weather/{city}",
            "note": "兩種URL都可以使用"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"編碼錯誤：{str(e)}",
                "city": city
            }
        )

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "message": "API服務正常運行",
        "encoding_support": "✅ 支援中文城市名稱直接輸入",
        "bus_stop_support": "✅ 支援公車站牌動態資訊查詢"
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404錯誤處理"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "找不到請求的端點",
            "available_endpoints": ["/", "/weather", "/weather/{city}", "/cities", "/encode/{city}", "/health", "/bus_stop"],
            "tip": "城市名稱可以直接使用中文，如: /weather/臺北市；公車站牌: /bus_stop?slid=1417",
            "docs": "訪問 /docs 查看完整API文檔"
        }
    )

if __name__ == '__main__':
    import uvicorn
    
    print("🌦️  台灣天氣降雨機率API + 🚌 公車站牌API 啟動中...")
    print("📍 支援的城市:", ", ".join(TAIWAN_CITIES[:5]), "等", len(TAIWAN_CITIES), "個城市")
    print("🔗 API端點:")
    print("   - GET /weather - 獲取台北市天氣")
    print("   - GET /weather/{city} - 獲取指定城市天氣")
    print("   - GET /cities - 獲取支援城市列表")
    print("   - GET /encode/{city} - 獲取城市URL編碼")
    print("   - GET /bus_stop?slid={站牌ID} - 獲取公車站牌動態資訊")
    print("   - GET /health - 健康檢查")
    print("   - GET /docs - 自動生成的API文檔")
    print("   - GET /redoc - ReDoc格式的API文檔")
    print("\n📋 使用範例:")
    print("   🎯 直接中文: curl 'http://localhost:8000/weather/臺北市'")
    print("   🔗 URL編碼: curl http://localhost:8000/weather/%E8%87%BA%E5%8C%97%E5%B8%82")
    print("   🚌 公車站牌: curl 'http://localhost:8000/bus_stop?slid=1417'")
    print("   ✨ 兩種方式都支援！")
    print("   📚 API文檔: http://localhost:8000/docs")
    
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False) 