import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3"
}
BASE_URL = "https://syokugan-ohkoku.com/"

def main():
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        res.encoding = 'EUC-JP'
        soup = BeautifulSoup(res.text, 'lxml')
        
        yoyaku_list = []
        nyuka_list = []
        other_list = []
        seen_urls = set()
        
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            url = href if href.startswith('http') else BASE_URL + href
            if url in seen_urls: continue
                
            title = link.get_text(strip=True)
            if not title and link.find('img'):
                title = link.find('img').get('alt', '').strip()
            
            if not title or len(title) < 2 or "一覧" in title or "カート" in title:
                continue
                
            seen_urls.add(url)
            
            if "予約" in title or "先行" in title:
                yoyaku_list.append({"title": title, "url": url})
            elif "入荷" in title or "済" in title:
                nyuka_list.append({"title": title, "url": url})
            elif "食玩" in title or "BOX" in title or "キャンディ" in title:
                other_list.append({"title": title, "url": url})
                
        other_list = other_list[:30]

        if not yoyaku_list and not nyuka_list and not other_list:
            title_text = f"【系统诊断】代码: {res.status_code}，页面大小: {len(res.text)}，找到链接: {len(links)}个。"
            if res.status_code == 403:
                title_text += " (403说明网站拦截了海外IP)"
            other_list.append({"title": title_text, "url": BASE_URL})

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
                "新食玩情報": [{"title": f"【网络请求失败】{str(e)}", "url": BASE_URL}]
            }, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
