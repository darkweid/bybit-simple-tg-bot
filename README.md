# Telegram Trading Bot for Bybit

## ENG 🇬🇧

### Description
This is a simple trading bot for Bybit, designed to perform basic trading functions such as opening and closing positions automatically. It interacts with the Bybit API and sends notifications via Telegram, helping traders monitor market movements and execute trading strategies.

### Features
- Automatically open and close positions on Bybit.
- Monitor market prices and evaluate profit targets.
- Send trading notifications via Telegram.
- Configurable profit targets and trade amounts through environment variables.
- Uses aiogram for Telegram bot integration and Bybit's API for trading operations.

### Technologies
- Python 3
- `aiogram` (for Telegram bot integration)
- `pybit` (for interaction with Bybit API)
- `environs` (for environment variable management)

### Requirements
- Python 3.8 or higher
- Bybit API Key and Secret
- Telegram Bot Token and Chat ID
- Environment variables configured in `.env` file

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/darkweid/bybit-simple-tg-bot.git
    cd bybit-simple-tg-bot
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Create a `.env` file with the following content:
    ```
    API_KEY=your_bybit_api_key
    API_SECRET=your_bybit_api_secret
    TELEGRAM_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    SYMBOL=BTCUSDT # Example
    TARGET_PROFIT_PERCENT=0.5  # Profit target
    AMOUNT=0.001  # Trade amount (e.g. BTC for BTCUSDT pair)
    ```
    ### Example Trading Pairs
    The bot supports a range of trading pairs for Bybit. You can specify the trading pair in your `.env` file using the `SYMBOL` variable. Here are some examples:

    - `BTCUSDT` - Bitcoin to Tether
    - `ETHUSDT` - Ethereum to Tether
    - `SOLUSDT` - Solana to Tether
    - `XRPUSDT` - Ripple to Tether
    - `LTCUSDT` - Litecoin to Tether

    Feel free to change the `SYMBOL` variable to match your preferred trading pair.
    For the full list of available trading pairs on Bybit, visit [Bybit Markets](https://www.bybit.com/en-US/trade/spot).

4. Run the bot:
    ```bash
    python main.py
    ```

### Usage
- `/start` - Start the bot.
- `/trade` - Open a new position.
- `/status` - Check the status of the current open position.



### License
This project is licensed under the MIT License.

---

# Telegram Trading Bot для Bybit

## RUS🇷🇺

## Описание
Это простой торговый бот для Bybit, который автоматически выполняет основные торговые функции, такие как открытие и закрытие позиций. Бот взаимодействует с API Bybit и отправляет уведомления через Telegram, помогая трейдерам отслеживать рыночные движения и исполнять торговые стратегии.

### Основные функции
- Автоматическое открытие и закрытие позиций на Bybit.
- Мониторинг рыночных цен и оценка целевой прибыли.
- Отправка торговых уведомлений через Telegram.
- Настраиваемые целевые прибыли и объемы сделок через переменные окружения.
- Использование aiogram для интеграции с Telegram и API Bybit для торговых операций.

### Технологии
- Python 3
- `aiogram` (для интеграции с Telegram)
- `pybit` (для работы с API Bybit)
- `environs` (для управления переменными окружения)

### Требования
- Python 3.8 или выше
- Ключ и секрет Bybit API
- Токен бота Telegram и ID чата
- Переменные окружения, настроенные в файле `.env`

### Установка
1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/darkweid/bybit-simple-tg-bot.git
    cd bybit-simple-tg-bot
    ```

2. Создайте виртуальное окружение и установите зависимости:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Создайте файл `.env` со следующим содержанием:
    ```
    API_KEY=ваш_ключ_от_bybit
    API_SECRET=ваш_секретный_ключ_от_bybit
    TELEGRAM_TOKEN=ваш_токен_бота_telegram
    TELEGRAM_CHAT_ID=ваш_id_чата_telegram
    SYMBOL=BTCUSDT
    TARGET_PROFIT_PERCENT=0.5  # Пример целевой прибыли
    AMOUNT=0.001  # Объем сделки в целевой валюте (например BTC для пары BTCUSDT)
    ```
    ### Примеры валютных пар
    Бот поддерживает множество торговых пар для Bybit. Вы можете указать торговую пару в файле `.env`, используя переменную `SYMBOL`. Вот некоторые примеры:

    - `BTCUSDT` - Bitcoin к Tether
    - `ETHUSDT` - Ethereum к Tether
    - `SOLUSDT` - Solana к Tether
    - `XRPUSDT` - Ripple к Tether
    - `LTCUSDT` - Litecoin к Tether
    Вы можете изменить значение переменной `SYMBOL`, чтобы использовать предпочитаемую торговую пару.
    Для получения полного списка доступных торговых пар на Bybit посетите [Рынки Bybit](https://www.bybit.com/en-US/trade/spot).

4. Запустите бота:
    ```bash
    python main.py
    ```

### Использование
- `/start` - Запуск бота.
- `/trade` - Открыть новую позицию.
- `/status` - Проверить статус текущей открытой позиции.



### Лицензия
Этот проект лицензирован под лицензией MIT.
