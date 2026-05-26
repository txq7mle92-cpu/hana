import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
BASE_URL = "https://syokugan-ohkoku.com/"

def parse_block(soup, keywords):
    products = []
    for img in soup.find_all('img', alt=True):
        alt_text = img['alt']
        src_text = img.get('src', '')
        if any(k in alt_text or k in src_text for k in keywords):
            parent = img.find_parent('table') or img.find_parent('div')
            if parent:
                for link in parent.find_all('a', href=True):
                    href = link['href']
                    if 'item.php' in href or 'ItemDetail' in href:
                        url = href if href.startswith('http') else BASE_URL + href
                        title = link.get_text(strip=True)
                        if not title and link.find('img'):
                            title = link.find('img').get('alt', '').strip()
                        if title and not any(p['url'] == url for p in products):
                            products.append({"title": title, "url": url})
            break
    return products

def main():
    res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
    res.encoding = 'EUC-JP'
    soup = BeautifulSoup(res.text, 'lxml')
    
    config = {
        "先行予約商品": ["yoyaku", "予約"],
        "新食玩情報": ["sinkom", "新食玩", "new"],
        "最新入荷済": ["nyuka", "入荷済", "入荷済み"],
        "まもなく入荷": ["mamonaku", "まもなく"],
        "再入荷": ["sai", "再入荷"]
    }
    
    beijing_time = datetime.utcnow() + timedelta(hours=8)
    result = {"update_time": beijing_time.strftime("%Y-%m-%d %H:%M:%S")}
    for key, kws in config.items():
        result[key] = parse_block(soup, kws)
        
    with open("shokugan_list.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
