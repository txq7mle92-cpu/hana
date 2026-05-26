import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://syokugan-ohkoku.com/"
# 分类入口
CATEGORIES = {
    "先行予約": "item/order-syokugan/yoyaku/index.php",
    "新食玩": "item/order-syokugan/new/index.php",
    "入荷済": "item/order-syokugan/nyuka/index.php"
}

def fetch_details(url):
    """进入商品详情页，精准挖出5个核心数据"""
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.encoding = 'EUC-JP'
        soup = BeautifulSoup(res.text, 'lxml')
        
        # 定义获取函数
        def get_text_by_label(label):
            for row in soup.find_all('tr'):
                if label in row.get_text():
                    return row.find_all('td')[-1].get_text(strip=True)
            return "无"

        return {
            "img": BASE_URL + soup.find('img', {'class': 'item-image'})['src'].lstrip('/') if soup.find('img', {'class': 'item-image'}) else "",
            "jan": get_text_by_label('JAN'),
            "stock": get_text_by_label('在庫'),
            "p1": get_text_by_label('希望小売'),
            "p2": get_text_by_label('販売価格'),
            "p3": get_text_by_label('代引・振込')
        }
    except:
        return {"img": "", "jan": "N/A", "stock": "N/A", "p1": "N/A", "p2": "N/A", "p3": "N/A"}

def run_spider():
    final_data = {}
    for cat_name, path in CATEGORIES.items():
        print(f"正在抓取分类: {cat_name}")
        res = requests.get(BASE_URL + path, headers={"User-Agent": "Mozilla/5.0"})
        res.encoding = 'EUC-JP'
        soup = BeautifulSoup(res.text, 'lxml')
        
        items = []
        for a in soup.find_all('a', href=True):
            if 'code=' in a['href']:
                url = BASE_URL + a['href'].lstrip('/')
                title = a.get_text(strip=True)
                if len(title) < 3: continue
                
                details = fetch_details(url)
                details['title'] = title
                items.append(details)
                time.sleep(0.5) # 保护性延时
        final_data[cat_name] = items
        
    with open("shokugan_list.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_spider()
