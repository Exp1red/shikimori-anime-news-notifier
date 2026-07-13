import os
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import time
import requests
import re

SHIKIMORI_API_URL = "https://shikimori.io/api/topics"
USER_AGENT = "ShikimoriAnimeNotifier/1.0"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LAST_ID_FILE = "last_id.txt"

HEADERS = {
    "User-Agent": USER_AGENT
}

def get_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_last_id(last_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(last_id))

def fetch_topics(limit=10):
    params = {
        "forum": "news",
        "limit": limit,
        "order": "id",
        "order_direction": "desc",
        "type": "Topics::NewsTopic"
    }

    response = requests.get(SHIKIMORI_API_URL, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def send_to_discord(topics):
    if not topics:
        print("Нет новых новостей для отправки.")
        return

    for topic in topics:
        embed = build_embed(topic)
        payload = {
            "embeds": [embed]
        }

        webhook_urls = parse_csv_values(DISCORD_WEBHOOK_URL)
        if not DISCORD_WEBHOOK_URL or not webhook_urls:
            return
        for webhook_url in webhook_urls:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code not in (200, 204):
                print(f"Ошибка отправки в Discord: {response.status_code} - {response.text}")
            else:
                print(f"Отправлена новость: {topic.get('topic_title')} (ID {topic.get('id')})")
            time.sleep(1)


def parse_csv_values(value):
    return [item.strip() for item in str(value).split(",") if item.strip()]

def build_embed(topic):
    html_body = topic.get('html_body', '')
    html_footer = topic.get('html_footer', '')
    linked = topic.get('linked')

    description = clean_html_to_text(html_body)
    if len(description) > 600:
        description = description[:600].rsplit(' ', 1)[0] + '…'

    video_url = extract_youtube_url(html_footer)
    if video_url:
        description += f'\n\n🎬 [Смотреть на YouTube]({video_url})'

    embed = {
        "title": topic.get('topic_title', 'Новость'),
        "url": f"https://shikimori.one/forum/news/{topic.get('id')}",
        "description": description,
        "color": 0x00b0f4,
        "timestamp": topic.get('created_at', datetime.now(timezone.utc).isoformat()),
        "footer": {"text": "Shikimori News"}
    }

    img_url = get_image_url(linked)
    if img_url:
        embed["image"] = {"url": img_url}

    return embed

def extract_youtube_url(html_footer):
    if not html_footer:
        return None
    soup = BeautifulSoup(html_footer, 'html.parser')
    video_link = soup.find('a', class_='video-link')
    if video_link:
        href = video_link.get('href')
        if href and ('youtu.be' in href or 'youtube.com' in href):
            if href.startswith('//'):
                href = 'https:' + href
            return href
    return None

def get_image_url(linked):
    if not linked or not linked.get('image'):
        return None
    img = linked['image']
    url = img.get('original')
    if url and 'missing_original' not in url:
        return f'https://shikimori.one{url}'
    return None

def clean_html_to_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, 'html.parser')

    for br in soup.find_all('br'):
        br.replace_with('\n')

    for a in soup.find_all('a'):
        href = a.get('href')
        text = a.get_text(strip=True)
        if href and text:
            if href.startswith('/'):
                href = f'https://shikimori.one{href}'
            a.replace_with(f'[{text}]({href})')
        else:
            a.replace_with(text)

    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s*\.\.\.\s*View$', '', text)
    return text

def main():
    if not DISCORD_WEBHOOK_URL:
        print("Ошибка: DISCORD_WEBHOOK_URL не задан")
        return

    last_id = get_last_id()
    print(f"Последний отправленный ID: {last_id}")

    try:
        topics = fetch_topics(limit=10)
    except Exception as e:
        print(f"Ошибка получения новостей: {e}")
        return

    if not topics:
        print("Новостей нет.")
        return

    new_topics = [t for t in topics if t.get("id", 0) > last_id]
    if not new_topics:
        print("Новых новостей нет.")
        return

    new_topics.sort(key=lambda x: x.get("id", 0))
    send_to_discord(new_topics)

    max_id = max(t.get("id", 0) for t in topics)
    save_last_id(max_id)
    print(f"Обновлён last_id: {max_id}")

if __name__ == "__main__":
    main()