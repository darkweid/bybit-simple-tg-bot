import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from pybit.unified_trading import HTTP
import logging
from environs import Env

# Загрузка переменных окружения
env = Env()
env.read_env()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка конфигурации из .env
BYBIT_API_KEY = env.str("API_KEY")
BYBIT_API_SECRET = env.str("API_SECRET")
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = env.str("TELEGRAM_CHAT_ID")
SYMBOL = env.str("SYMBOL")
TARGET_PROFIT_PERCENT = env.float("TARGET_PROFIT_PERCENT")
AMOUNT = 10

# Инициализация Telegram бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализация клиента Bybit
session = HTTP(
    testnet=True,
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET
)


class TradingBot:
    def __init__(self):
        self.active_position = None
        self.monitor_task = None

    async def open_position(self) -> bool:
        """Открытие позиции"""
        try:
            response = session.place_order(
                category="spot",
                symbol=SYMBOL,
                side="Buy",
                orderType="MARKET",
                qty=str(AMOUNT),
                marketUnit="quoteCoin"
            )

            if response['retCode'] == 0:
                order_id = response['result']['orderId']
                order_book = await self.get_order_book()
                entry_price = order_book.get('bid')
                target_price = round(entry_price * (1 + TARGET_PROFIT_PERCENT / 100), 3)
                target_amount = round(AMOUNT * (1 + TARGET_PROFIT_PERCENT / 100), 3)

                self.active_position = {
                    'order_id': order_id,
                    'symbol': SYMBOL,
                    'entry_price': entry_price,
                    'amount': AMOUNT,
                    'target_price': target_price,
                    'target_amount': target_amount
                }

                logger.info(f"Открыта новая позиция: {self.active_position}")

                # Запускаем мониторинг позиции
                self.monitor_task = asyncio.create_task(self.monitor_position())

                return True
        except Exception as e:
            logger.error(f"Ошибка при открытии позиции: {e}")
        return False

    async def close_position(self) -> bool:
        """Закрытие позиции"""
        try:
            response = session.place_order(
                category="spot",
                symbol=SYMBOL,
                side="Sell",
                orderType="MARKET",
                qty=str(self.active_position['target_amount']),
                marketUnit="quoteCoin"
            )

            if response['retCode'] == 0:
                order_book = await self.get_order_book()
                ask_price = order_book.get('ask')
                profit = (ask_price / self.active_position['entry_price'] - 1) * self.active_position['amount']
                profit_percentage = ((ask_price / self.active_position['entry_price']) - 1) * 100

                await self.send_notification(f"✅ Позиция закрыта с прибылью!\n"
                                             f"Валютная пара: {self.active_position['symbol']}\n"
                                             f"Прибыль: {profit:.2f} USDT\n"
                                             f"Процент прибыли: {profit_percentage:.2f}%\n"
                                             f"Цена входа: {self.active_position['entry_price']}\n"
                                             f"Цена выхода: {ask_price}")
                logger.info(f"Позиция закрыта успешно: {self.active_position}")
                self.active_position = None

                # Останавливаем мониторинг позиции
                if self.monitor_task:
                    self.monitor_task.cancel()
                    self.monitor_task = None
                return True
        except Exception as e:
            logger.error(f"Ошибка при закрытии позиции: {e}")
        return False

    async def monitor_position(self) -> None:
        """Мониторинг открытой позиции"""
        while True:
            try:
                if self.active_position:
                    order_book = await self.get_order_book()
                    bid_price = order_book.get('bid')
                    ask_price = order_book.get('ask')

                    if bid_price is None or ask_price is None:
                        logger.error("Не удалось получить цены для ордербука")
                        continue

                    # Вычисление прибыли
                    if ask_price >= self.active_position['target_price']:
                        # Закрываем позицию при достижении целевой прибыли
                        await self.close_position()


            except Exception as e:
                logger.error(f"Ошибка при мониторинге позиции: {e}")

            await asyncio.sleep(1)

    @staticmethod
    async def send_notification(message):
        """Отправка уведомления в Telegram"""
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            logger.info(f"Отправлено уведомление в Telegram: {message}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления в Telegram: {e}")

    @staticmethod
    async def get_order_book() -> dict:
        """Получение orderbook для получения цен покупки и продажи"""
        try:
            response = session.get_orderbook(category="spot", symbol=SYMBOL)
            bid_price = float(response['result']['b'][0][0])  # Цена покупки
            ask_price = float(response['result']['a'][0][0])  # Цена продажи
            return {'bid': bid_price, 'ask': ask_price}
        except Exception as e:
            logger.error(f"Ошибка при получении orderbook: {e}")

    @staticmethod
    async def start_bot():
        await dp.start_polling(bot)


# Инициализация бота
trading_bot = TradingBot()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я торговый бот для Bybit.\n"
        "Доступные команды:\n"
        "/trade - открыть новую позицию\n"
        "/status - проверить текущую позицию"
    )


@dp.message(Command("status"))
async def status_command(message: types.Message):
    if trading_bot.active_position:
        order_book = await trading_bot.get_order_book()
        current_price = order_book.get('bid')
        current_profit = ((current_price / trading_bot.active_position['entry_price']) - 1) * 100

        await message.answer(
            f"📊 Текущая позиция:\n"
            f"Валютная пара: {trading_bot.active_position['symbol']}\n"
            f"Цена входа: {trading_bot.active_position['entry_price']}\n"
            f"Текущая цена: {current_price}\n"
            f"Текущая прибыль: {current_profit:.2f}%\n"
            f"Целевая прибыль: {TARGET_PROFIT_PERCENT}%"
        )
    else:
        await message.answer("❌ Нет открытых позиций")


@dp.message(Command("trade"))
async def trade_command(message: types.Message):
    if trading_bot.active_position:
        await message.answer("❌ У вас уже есть открытая позиция!")
        return

    try:
        if await trading_bot.open_position():
            await message.answer(
                f"✅ Позиция открыта!\n"
                f"Валютная пара: {trading_bot.active_position['symbol']}\n"
                f"Цена входа: {trading_bot.active_position['entry_price']}\n"
                f"Целевая цена: {trading_bot.active_position['target_price']}"
            )
        else:
            await message.answer("❌ Ошибка при открытии позиции")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {e}")


async def main():
    # Проверка наличия всех необходимых переменных окружения
    required_vars = ["API_KEY", "API_SECRET", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_vars if not env.str(var, "")]

    if missing_vars:
        logger.error(f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}")
        return

    logger.info(f"Бот запущен. Валютная пара: {SYMBOL}, Целевая прибыль: {TARGET_PROFIT_PERCENT}%")
    await trading_bot.send_notification(
        f"🚀 Бот запущен. Валютная пара: {SYMBOL}\n"
        f"Целевая прибыль: {TARGET_PROFIT_PERCENT}%")

    # Запуск бота
    await trading_bot.start_bot()


if __name__ == "__main__":
    asyncio.run(main())
