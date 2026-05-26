import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://syokugan-ohkoku.com/"
# 列表页通常包含在导航栏中，这里根据你的网站结构进行遍历
# 如果有分页，需根据页面逻辑添加，这里先抓取首页及主要入口
START_URLS = [
    "https://syokugan-ohkoku.com/item/order-syokugan/index.php",
    # 如果有更多分页，可以在此添加
]

def get_product_details(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.encoding = 'EUC-JP' # 核心：解决乱码
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 提取详情
        details = {"jan": "未知", "stock": "未知", "p1": "未知", "p2": "未知", "p3": "未知"}
        
        # 暴力定位表格中的数据
        for row in soup.find_all('tr'):
            text = row.get_text(separator='|')
            if 'JAN' in text: details['jan'] = text.split('|')[-1].strip()
            if '在庫' in text: details['stock'] = text.split('|')[-1].strip()
            if '希望小売価格' in text: details['p1'] = text.split('|')[-1].strip()
            if '当店販売価格' in text: details['p2'] = text.split('|')[-1].strip()
            if '代引・振込' in text: details['p3'] = text.split('|')[-1].strip()
        
        return details
    except:
        return {}

def main():
    all_products = []
    # 抓取入口列表
    for start_url in START_URLS:
        res = requests.get(start_url, headers={"User-Agent": "Mozilla/5.0"})
        res.encoding = 'EUC-JP'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 找到所有商品链接
        for a in soup.find_all('a', href=True):
            if 'item.php?code=' in a['href'] or 'ItemDetail' in a['href']:
                product_url = a['href'] if a['href'].startswith('http') else BASE_URL + a['href'].lstrip('/')
                title = a.get_text(strip=True)
                
                # 抓取详情
                details = get_product_details(product_url)
                details.update({"title": title, "url": product_url})
                all_products.append(details)
                time.sleep(0.5) # 遵守礼貌，防封IP
    
    with open("shokugan_list.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
