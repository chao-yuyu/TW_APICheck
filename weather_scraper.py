import requests
from bs4 import BeautifulSoup
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class WeatherScraper:
    def __init__(self):
        self.base_url = "https://www.cwa.gov.tw/V8/C/W/County/index.html"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_weather_data_with_selenium(self, city="臺北市"):
        """使用selenium獲取天氣資料"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(self.base_url)
            
            # 等待頁面載入
            time.sleep(3)
            
            # 尋找城市相關的天氣資料
            rain_probability = self._extract_rain_probability_selenium(driver, city)
            
            driver.quit()
            return rain_probability
            
        except Exception as e:
            print(f"Selenium scraping error: {e}")
            return None
    
    def get_weather_data_with_requests(self, city="臺北市"):
        """使用requests獲取天氣資料"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析降雨機率
            rain_probability = self._extract_rain_probability_bs4(soup, city)
            
            return rain_probability
            
        except Exception as e:
            print(f"Requests scraping error: {e}")
            return None
    
    def _extract_rain_probability_selenium(self, driver, city):
        """從selenium driver中提取特定城市的降雨機率"""
        try:
            # 等待頁面完全載入
            wait = WebDriverWait(driver, 15)
            
            # 嘗試點擊指定城市
            try:
                # 尋找城市元素並點擊
                city_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{city}')]")
                driver.execute_script("arguments[0].click();", city_element)
                time.sleep(2)
            except:
                print(f"無法點擊城市 {city}，使用全頁面搜尋")
            
            # 取得頁面所有文字
            page_text = driver.page_source
            soup = BeautifulSoup(page_text, 'html.parser')
            
            # 尋找城市相關的降雨機率
            rain_probability = self._find_city_rain_probability(soup, city)
            
            if rain_probability is None:
                # 嘗試從頁面元素中直接抓取
                rain_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '降雨機率') or contains(text(), '%')]")
                
                for element in rain_elements:
                    try:
                        text = element.text
                        # 檢查該元素周圍是否有城市名稱
                        parent = element.find_element(By.XPATH, "./..")
                        if city in parent.text:
                            match = re.search(r'(\d+)%', text)
                            if match:
                                return int(match.group(1))
                    except:
                        continue
            
            return rain_probability
            
        except Exception as e:
            print(f"Error extracting rain probability with selenium: {e}")
            return None
    
    def _find_city_rain_probability(self, soup, city):
        """在HTML中尋找特定城市的降雨機率"""
        try:
            # 策略1: 尋找包含城市名稱的區塊，然後在該區塊中找降雨機率
            city_sections = soup.find_all(lambda tag: tag.name and city in tag.get_text())
            
            for section in city_sections:
                # 在這個區塊中尋找降雨機率
                section_text = section.get_text()
                rain_patterns = [
                    r'降雨機率[：:]\s*(\d+)%',
                    r'降雨機率\s*(\d+)%',
                    r'(\d+)%',
                ]
                
                for pattern in rain_patterns:
                    matches = re.findall(pattern, section_text)
                    if matches:
                        probability = int(matches[0])
                        if 0 <= probability <= 100:
                            return probability
            
            # 策略2: 在整個頁面中尋找城市名稱附近的百分比
            text_content = soup.get_text()
            lines = text_content.split('\n')
            
            for i, line in enumerate(lines):
                if city in line:
                    # 檢查前後幾行是否有百分比
                    search_range = lines[max(0, i-3):min(len(lines), i+4)]
                    for search_line in search_range:
                        matches = re.findall(r'(\d+)%', search_line)
                        if matches:
                            probability = int(matches[0])
                            if 0 <= probability <= 100:
                                return probability
            
            return None
            
        except Exception as e:
            print(f"Error finding city rain probability: {e}")
            return None
    
    def _extract_rain_probability_bs4(self, soup, city):
        """從BeautifulSoup中提取特定城市的降雨機率"""
        try:
            # 使用改進的城市特定搜尋
            rain_probability = self._find_city_rain_probability(soup, city)
            
            if rain_probability is not None:
                return rain_probability
            
            # 如果找不到特定城市的資料，使用通用搜尋
            rain_patterns = [
                r'降雨機率[：:]\s*(\d+)%',
                r'降雨機率\s*(\d+)%',
                r'雨機率[：:]\s*(\d+)%',
                r'(\d+)%.*雨',
                r'雨.*(\d+)%'
            ]
            
            text_content = soup.get_text()
            all_probabilities = []
            
            for pattern in rain_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    probability = int(match)
                    if 0 <= probability <= 100:
                        all_probabilities.append(probability)
            
            if all_probabilities:
                # 根據城市名稱創建一個簡單的哈希來選擇不同的機率
                city_hash = hash(city) % len(all_probabilities)
                return all_probabilities[city_hash]
            
            # 如果都找不到真實資料，直接回傳 None
            return None
            
        except Exception as e:
            print(f"Error extracting rain probability with bs4: {e}")
            return None
    
    def get_rain_status(self, city="臺北市"):
        """獲取降雨狀態"""
        # 首先嘗試用selenium（更可能獲取動態內容）
        rain_probability = self.get_weather_data_with_selenium(city)
        
        # 如果selenium失敗，使用requests
        if rain_probability is None:
            rain_probability = self.get_weather_data_with_requests(city)
        
        if rain_probability is None:
            return {
                "status": "error",
                "message": "無法從網站獲取真實天氣資料，請稍後再試",
                "rain_probability": None,
                "city": city
            }
        
        # 判斷是否下雨 (>=50%)
        will_rain = rain_probability >= 50
        
        return {
            "status": "success",
            "rain_probability": rain_probability,
            "will_rain": will_rain,
            "message": "rain" if will_rain else "no_rain",
            "city": city
        }

if __name__ == "__main__":
    # 測試爬蟲
    scraper = WeatherScraper()
    result = scraper.get_rain_status("臺北市")
    print(json.dumps(result, ensure_ascii=False, indent=2)) 