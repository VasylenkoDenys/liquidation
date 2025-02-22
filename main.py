import json
import websocket
import telebot
import time
time.sleep(2)

# 🔹 API-ключи
telegram_token = "7849765435:AAGKSvUGXFmjTkxGFIphqiGIubinOedJvJg"
chat_id = "1466935078"
bot = telebot.TeleBot(telegram_token)

# 🔹 Возможные WebSocket URL Bybit
BYBIT_WS_URLS = [
    "wss://stream.bybit.com/v5/public/linear",  # Фьючерсы
    "wss://stream.bybit.com/v5/public/spot",    # Спот-рынок
    "wss://stream.bybit.com/realtime_public",   # Старый URL (может работать)
]

def on_message(ws, message):
    print(f"Получены данные: {message}")

def on_error(ws, error):
    print(f"Ошибка WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket закрыт: {close_status_code}, {close_msg}")

def on_open(ws):
    print("✅ Успешное подключение!")
    subscribe_msg = {
        "op": "subscribe",
        "args": ["liquidation.BTCUSDT", "liquidation.ETHUSDT", "liquidation.SOLUSDT"]
    }
    ws.send(json.dumps(subscribe_msg))

# 🔹 Перебираем доступные WebSocket-серверы
for url in BYBIT_WS_URLS:
    print(f"🔄 Пробуем подключиться к {url}...")
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()
