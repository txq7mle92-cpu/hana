import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}
BASE_URL = "https://syokugan-ohkoku.com/"

def get_details(url):
    # 默认值
    details = {"img": "", "jan": "未知", "stock": "未知", "p1": "未知", "p2": "未知", "p3": "未知"}
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = res.apparent_encoding  # 自动识别编码，彻底解决乱码
        soup = BeautifulSoup(res.text, 'lxml')
        
        # 抓取产品图片
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if '.jpg' in src.lower() and 'logo' not in src.lower() and 'btn' not in src.lower() and 'navi' not in src.lower():
                details["img"] = src if src.startswith('http') else BASE_URL + src.lstrip('/')
                break
                
        # 暴力抓取所有文字信息
        text_content = soup.get_text(separator='|')
        
        jan_m = re.search(r'JAN.*?(\d{13})', text_content, re.IGNORECASE)
        if jan_m: details["jan"] = jan_m.group(1)
        
        stock_m = re.search(r'在庫状況\|(.*?)\|', text_content)
        if stock_m: details["stock"] = stock_m.group(1).strip()
        
        p1_m = re.search(r'希望小売価格.*?([0-9,]+円)', text_content)
        if p1_m: details["p1"] = p1_m.group(1)
        
        p2_m = re.search(r'当店販売価格.*?([0-9,]+円)', text_content)
        if p2_m: details["p2"] = p2_m.group(1)
        
        p3_m = re.search(r'代引・振込.*?([0-9,]+円)', text_content)
        if p3_m: details["p3"] = p3_m.group(1)
        
    except Exception:
        pass
    return details

def main():
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'lxml')
        
        yoyaku_list, nyuka_list, other_list = [], [], []
        seen_urls = set()
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            url = href if href.startswith('http') else BASE_URL + href
            if url in seen_urls: continue
            
            title = link.get_text(strip=True)
            if not title and link.find('img'):
                title = link.find('img').get('alt', '').strip()
                
            if not title or len(title) < 2 or "一覧" in title or "カート" in title: continue
                
            seen_urls.add(url)
            
            # 只有商品才点进去偷偷抓取详情
            if 'item.php' in href or 'ItemDetail' in href:
                time.sleep(0.3) # 休息一下，防止被对方网站发现
                item_data = get_details(url)
                item_data["title"] = title
                
                if "予約" in title or "先行" in title:
                    yoyaku_list.append(item_data)
                elif "入荷" in title or "済" in title:
                    nyuka_list.append(item_data)
                elif "食玩" in title or "BOX" in title or "キャンディ" in title:
                    other_list.append(item_data)
            
            if len(seen_urls) > 80: break # 最多抓80个，避免超时

        beijing_time = datetime.utcnow() + timedelta(hours=8)
        result = {
            "update_time": beijing_time.strftime("%Y-%m-%d %H:%M:%S"),
            "先行予約商品": yoyaku_list,
            "最新入荷済": nyuka_list,
            "新食玩情報": other_list,
        }
            
        with open("shokugan_list.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        beijing_time = datetime.utcnow() + timedelta(hours=8)
        with open("shokugan_list.json", "w", encoding="utf-8") as f:
            json.dump({
                "update_time": beijing_time.strftime("%Y-%m-%d %H:%M:%S"),
                "新食玩情報": [{"title": f"更新失败: {str(e)}", "img": "", "jan": "", "stock": "", "p1": "", "p2": "", "p3": ""}]
            }, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
