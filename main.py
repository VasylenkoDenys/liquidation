import json
import websocket
import telebot
import time

# 🔹 API-ключи
telegram_token = "7849765435:AAGKSvUGXFmjTkxGFIphqiGIubinOedJvJg"
chat_id = "1466935078"
bot = telebot.TeleBot(telegram_token)

# 🔹 WebSocket URL для фьючерсов Bybit
BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

# 🔹 Функция обработки сообщений WebSocket
def on_message(ws, message):
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON: {message}")
        return

    # Проверяем, что получено подтверждение подписки
    if "topic" in data and "subscribe" in data.get("op", ""):
        print("Подписка на ликвидации успешна!")  # Уведомление, что подписка прошла успешно
        return  # Это просто подтверждение подписки, пропускаем его

    # Проверяем, что данные правильной структуры для ликвидаций
    if "topic" in data and "liquidation" in data["topic"]:
        print(f"Получены данные: {data}")  # Для отладки

        # Обрабатываем данные ликвидации
        liquidation_data = data.get("data", {})

        if isinstance(liquidation_data, dict):  # Проверка, что это словарь
            symbol = liquidation_data.get("symbol", "Неизвестно")
            side = "🟥 Short" if liquidation_data.get("side") == "Sell" else "🟩 Long"
            size = float(liquidation_data.get("size", 0))
            price = float(liquidation_data.get("price", 0))
            value = size * price  # Общая сумма ликвидации в USDT

            if value > 100000:  # Фильтр по ликвидациям > $100K
                msg = f"⚡ Крупная ликвидация {symbol}!\n💰 {side} ликвидировано на {value:.2f} USDT\n📉 Цена: {price:.2f}"
                bot.send_message(chat_id, msg)
                print(msg)  # Лог в консоль
        else:
            print(f"Не удалось распарсить данные: {liquidation_data}")
    else:
        print(f"Полученные данные не соответствуют ожидаемой структуре: {data}")

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

def run_ws():
    """ Функция для подключения и переподключения WebSocket """
    while True:
        ws = websocket.WebSocketApp(
            BYBIT_WS_URL,  
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws.on_open = on_open
        ws.run_forever()
        print("Соединение потеряно, пытаемся переподключиться...")
        time.sleep(5)  # Задержка перед переподключением

# Запуск WebSocket с автоматическим переподключением
run_ws()
