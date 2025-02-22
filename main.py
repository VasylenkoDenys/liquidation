import json
import websocket
import telebot
import time
time.sleep(2)

# 🔹 API-ключи
telegram_token = "7849765435:AAGKSvUGXFmjTkxGFIphqiGIubinOedJvJg"
chat_id = "1466935078"
bot = telebot.TeleBot(telegram_token)

# 🔹 WebSocket URL для фьючерсов Bybit
BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

# 🔹 Функция обработки сообщений WebSocket
def on_message(ws, message):
    data = json.loads(message)

    if "topic" in data and "liquidation" in data["topic"]:  # Проверяем, что это ликвидация
        liquidation = data["data"]
        
        for event in liquidation:  # Может быть несколько ликвидаций в одном сообщении
            symbol = event["symbol"]
            side = "🟥 Short" if event["side"] == "Sell" else "🟩 Long"
            size = float(event["size"])
            price = float(event["price"])
            value = size * price  # Общая сумма ликвидации в USDT

            if value > 100000:  # Фильтр по ликвидациям > $100K
                msg = f"⚡ Крупная ликвидация {symbol}!\n💰 {side} ликвидировано на {value:.2f} USDT\n📉 Цена: {price:.2f}"
                bot.send_message(chat_id, msg)
                print(msg)  # Лог в консоль

def on_error(ws, error):
    print(f"Ошибка WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Соединение закрыто")

def on_open(ws):
    print("🔗 WebSocket подключён! Ожидаем ликвидации...")
    subscribe_msg = {
        "op": "subscribe",
        "args": ["liquidation.BTCUSDT", "liquidation.ETHUSDT", "liquidation.SOLUSDT"]
    }
    ws.send(json.dumps(subscribe_msg))

# Подключаемся к WebSocket Bybit
ws = websocket.WebSocketApp(
    BYBIT_WS_URL,  
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.on_open = on_open
ws.run_forever()
