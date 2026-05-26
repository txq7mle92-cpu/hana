import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# 目标商品页
TARGET_URL = "https://syokugan-ohkoku.com/item.php?code=2602151"

def get_data():
    try:
        # 使用浏览器标识请求
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        res = requests.get(TARGET_URL, headers=headers, timeout=10)
        
        # 强制指定编码为 EUC-JP，这是解决乱码的核心
        res.encoding = 'EUC-JP'
        
        soup = BeautifulSoup(res.text, 'lxml')
        
        # 精准提取信息
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "商品名称获取失败"
        
        # 抓取图片（假设图片在某个特定的容器内）
        img_tag = soup.find('img', {'class': 'item-image'}) or soup.find('div', {'id': 'item-img'}).find('img')
        img_url = img_tag['src'] if img_tag else ""
        if img_url and not img_url.startswith('http'):
            img_url = "https://syokugan-ohkoku.com/" + img_url.lstrip('/')

        # 提取表格数据 (根据该网站常见的结构)
        data = {}
        for row in soup.find_all('tr'):
            text = row.get_text(separator='|')
            if 'JAN' in text: data['jan'] = text.split('|')[-1]
            if '在庫' in text: data['stock'] = text.split('|')[-1]
            if '希望小売価格' in text: data['p1'] = text.split('|')[-1]
            if '当店販売価格' in text: data['p2'] = text.split('|')[-1]
            if '代引・振込' in text: data['p3'] = text.split('|')[-1]

        # 整理结果
        result = {
            "update_time": (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "product": {
                "title": title,
                "img": img_url,
                "jan": data.get('jan', '未知'),
                "stock": data.get('stock', '未知'),
                "p1": data.get('p1', '未知'),
                "p2": data.get('p2', '未知'),
                "p3": data.get('p3', '未知')
            }
        }
        
        with open("shokugan_list.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_data()
