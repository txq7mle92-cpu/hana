import requests
from bs4 import BeautifulSoup
import json
import time

# 核心：使用 Session 来保持像浏览器一样的访问状态
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
})

BASE_URL = "https://syokugan-ohkoku.com/"

def parse_item(url):
    """精准解析详情页"""
    try:
        res = session.get(url, timeout=15)
        res.encoding = 'EUC-JP' # 关键：强制设置编码
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 定义一个提取器，专门找表格里的文字
        def get_cell(label):
            # 找到包含该label的行，并取其旁边的td
            for td in soup.find_all('td'):
                if label in td.get_text():
                    next_td = td.find_next_sibling('td')
                    return next_td.get_text(strip=True) if next_td else "N/A"
            return "N/A"

        return {
            "title": soup.find('h1').get_text(strip=True) if soup.find('h1') else "Unknown",
            "jan": get_cell("JAN"),
            "stock": get_cell("在庫"),
            "p1": get_cell("希望小売価格"),
            "p2": get_cell("販売価格"),
            "p3": get_cell("代引")
        }
    except:
        return None

def main():
    # 这里放置你的分类页 URL
    category_url = "https://syokugan-ohkoku.com/item/order-syokugan/new/index.php"
    res = session.get(category_url)
    res.encoding = 'EUC-JP'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    results = []
    # 抓取所有符合条件的商品链接
    for a in soup.find_all('a', href=True):
        if 'item.php?code=' in a['href']:
            link = BASE_URL + a['href'].lstrip('/')
            print(f"正在抓取: {link}")
            data = parse_item(link)
            if data:
                results.append(data)
            time.sleep(1.5) # 必须增加延迟，否则会被网站直接断开
    
    with open("shokugan_list.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
