import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
BASE_URL = "https://syokugan-ohkoku.com/"

def main():
    res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
    res.encoding = 'EUC-JP'
    soup = BeautifulSoup(res.text, 'lxml')
    
    yoyaku_list = []
    nyuka_list = []
    other_list = []
    
    seen_urls = set()
    
    # 暴力扫描所有链接，不再受限于复杂的表格排版
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'item.php' in href or 'ItemDetail' in href:
            url = href if href.startswith('http') else BASE_URL + href
            
            if url in seen_urls:
                continue
                
            title = link.get_text(strip=True)
            if not title and link.find('img'):
                title = link.find('img').get('alt', '').strip()
            
            if not title or len(title) < 2 or "一覧" in title:
                continue
                
            seen_urls.add(url)
            
            # 智能归类
            if "予約" in title or "先行" in title:
                yoyaku_list.append({"title": title, "url": url})
            elif "入荷" in title or "済" in title:
                nyuka_list.append({"title": title, "url": url})
            else:
                other_list.append({"title": title, "url": url})
    
    beijing_time = datetime.utcnow() + timedelta(hours=8)
    result = {
        "update_time": beijing_time.strftime("%Y-%m-%d %H:%M:%S"),
        "先行予約商品": yoyaku_list,
        "最新入荷済": nyuka_list,
        "新食玩情報": other_list,
    }
        
    with open("shokugan_list.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
