import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://syokugan-ohkoku.com/"
# 增加分类，涵盖更多可能
TARGET_URLS = [
    "https://syokugan-ohkoku.com/item/order-syokugan/yoyaku/index.php",
    "https://syokugan-ohkoku.com/item/order-syokugan/new/index.php",
    "https://syokugan-ohkoku.com/item/order-syokugan/nyuka/index.php"
]

def fetch_product(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        res.encoding = 'EUC-JP'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 暴力提取所有表格文字
        full_text = soup.get_text(separator="|")
        
        # 定义一个简单的提取器
        def find_val(keyword):
            if keyword in full_text:
                return full_text.split(keyword)[1].split("|")[0].strip()
            return "N/A"

        # 尝试获取图片
        img = soup.find('img', {'class': 'item-image'})
        img_src = BASE_URL + img['src'].lstrip('/') if img else ""

        return {
            "img": img_src,
            "jan": find_val("JAN"),
            "stock": find_val("在庫状況"),
            "p1": find_val("希望小売価格"),
            "p2": find_val("当店販売価格"),
            "p3": find_val("代引・振込")
        }
    except:
        return {"img": "", "jan": "Error", "stock": "Error", "p1": "Error", "p2": "Error", "p3": "Error"}

def main():
    all_data = []
    for start_url in TARGET_URLS:
        try:
            res = requests.get(start_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            res.encoding = 'EUC-JP'
            soup = BeautifulSoup(res.text, 'html.parser')
            # 获取所有链接
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "item.php" in href or "ItemDetail" in href:
                    full_link = href if href.startswith('http') else BASE_URL + href.lstrip('/')
                    title = a.get_text(strip=True)
                    if len(title) > 2:
                        product = fetch_product(full_link)
                        product['title'] = title
                        product['url_origin'] = full_link # 调试用
                        all_data.append(product)
                        time.sleep(1) # 增加延迟，防止被拦截
        except:
            continue
            
    with open("shokugan_list.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
