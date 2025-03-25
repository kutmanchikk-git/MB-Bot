

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import  httpx
from selectolax.parser import HTMLParser
from cachetools import TTLCache
from collections import defaultdict
from selectolax.lexbor import LexborHTMLParser
http_cl= httpx.AsyncClient(http2=True, timeout=5)
user_links = defaultdict(list)
cache = TTLCache(maxsize=500, ttl=3600)



async def search_music(user_id: int, query: str, low_line: int = 0, high_line: int = 10) -> InlineKeyboardBuilder:
    cache_key = f"{user_id}_{query}"
    if cache_key in cache:
        links = cache[cache_key]
    else:
        url = f"https://web.ligaudio.ru/mp3/{query}"
        html = await fetch_url(url)

    if not html.strip():
        print("Ошибка: пустая страница. Возможно, сайт блокирует парсинг.")
        return

    parser = LexborHTMLParser(html)
    links = parser.css("a.down[title]")
                    
    user_links[user_id].clear()
    keyboard = InlineKeyboardBuilder()
         
    for i, link in enumerate(links[low_line:high_line]):
        title = link.attributes.get("title", "Без названия")
        href = link.attributes.get("href", "")
        if href and href.startswith("//"):
            href = "https:" + href
        user_links[user_id].append(href)
        keyboard.add(InlineKeyboardButton(text=title, callback_data=str(i)))
    
    return keyboard.adjust(1)


async def fetch_url(url: str) -> str:
    """Загружает HTML страницы по URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://web.ligaudio.ru/",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    response = await http_cl.get(url, headers=headers)
    response.raise_for_status()

    # Если charset_encoding определена, используем её
    encoding = response.charset_encoding or "utf-8"
    return response.content.decode(encoding, errors="ignore")

