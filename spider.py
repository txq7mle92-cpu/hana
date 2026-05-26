import requests
from bs4 import BeautifulSoup
import json

def get_all_items():
    # 目标分类列表页（请在此列出所有你想抓的分类页面）
    target_pages = [
        "https://syokugan-ohkoku.com/item/order-syokugan/new/index.php"
    ]
    
    all_data = []
    
    for url in target_pages:
        try:
            # 增加更伪装的 Header
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Referer": "https://syokugan-ohkoku.com/"
            }
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'EUC-JP'
            
            # 使用 lxml 提高解析能力
            soup = BeautifulSoup(res.text, 'lxml')
            
            # 直接抓取表格行，这是最稳的方法
            # 找到所有包含商品信息的表格单元
            items = soup.find_all('tr') 
            
            for item in items:
                # 在每一行里找，如果有特定的标题或者图片，就抓下来
                text = item.get_text(separator="|").strip()
                if len(text) > 20: # 过滤掉无效行
                    all_data.append({"raw_content": text})
                    
        except Exception as e:
            print(f"抓取失败: {e}")
            
    with open("shokugan_list.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_all_items()
