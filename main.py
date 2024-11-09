import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import BotCommand
from pybit.unified_trading import HTTP
import logging
from environs import Env

# Loading environment variables
env = Env()
env.read_env()

# Logging configuration
logging.basicConfig(format=("|%(asctime)s| %(levelname)s |%(message)s"), level=logging.INFO)
logger = logging.getLogger(__name__)

# Loading configuration from .env
BYBIT_API_KEY = env.str("API_KEY")
BYBIT_API_SECRET = env.str("API_SECRET")
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = env.str("TELEGRAM_CHAT_ID")
SYMBOL = env.str("SYMBOL")
TARGET_PROFIT_PERCENT = env.float("TARGET_PROFIT_PERCENT")
AMOUNT = env.float("AMOUNT")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Initialize Bybit client
session = HTTP(
    testnet=True,  # Change to False for using mainnet
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET
)


class TradingBot:
    def __init__(self):
        """Initializes the TradingBot class.

        Sets the initial state of the bot with no active position and no monitoring task.
        """
        self.active_position = None
        self.monitor_task = None

    async def open_position(self) -> bool:
        """Opens a new trading position.

        Places a market order to buy the specified amount of the selected trading pair.
        After opening, calculates the target price based on the profit percentage and starts monitoring the position.

        Returns:
            bool: True if the position was opened successfully, False otherwise.
        """
        try:
            order_book = await self.get_order_book()
            response = session.place_order(
                category="spot",
                symbol=SYMBOL,
                side="Buy",
                orderType="MARKET",
                qty=str(AMOUNT),
                marketUnit="baseCoin"
            )

            if response['retCode'] == 0:
                order_id = response['result']['orderId']
                entry_price = order_book.get('ask')
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

                logger.info(f"New position opened: {self.active_position}")

                # Start monitoring the position
                self.monitor_task = asyncio.create_task(self.monitor_position())

                return True
        except Exception as e:
            logger.error(f"Error while opening position: {e}")
        return False

    async def close_position(self) -> bool:
        """Closes the active position.

        Places a market order to sell the specified amount of the selected trading pair.
        After closing, sends a notification with profit information and stops monitoring the position.

        Returns:
            bool: True if the position was closed successfully, False otherwise.
        """
        try:
            order_book = await self.get_order_book()
            response = session.place_order(
                category="spot",
                symbol=SYMBOL,
                side="Sell",
                orderType="MARKET",
                qty=str(AMOUNT),
                marketUnit="baseCoin"
            )

            if response['retCode'] == 0:
                bid_price = order_book.get('bid')
                profit_percentage = ((bid_price / self.active_position['entry_price']) - 1) * 100

                await send_notification(f"✅ Position closed!\n"
                                        f"Trading Pair: {self.active_position['symbol']}\n"
                                        f"Profit Percentage: {profit_percentage:.2f}%\n"
                                        f"Entry Price: {self.active_position['entry_price']}\n"
                                        f"Target Price: {self.active_position['target_price']}\n"
                                        f"Exit Price: {bid_price}")
                logger.info(f"Position closed successfully: {self.active_position}")
                self.active_position = None

                # Stop monitoring the position
                if self.monitor_task:
                    self.monitor_task.cancel()
                    self.monitor_task = None
                return True
        except Exception as e:
            logger.error(f"Error while closing position: {e}")
        return False

    async def monitor_position(self) -> None:
        """Monitors the active position.

        Continuously checks the current market prices and closes the position if the target price is reached.

        This function runs indefinitely until the position is closed.
        """
        while True:
            try:
                if self.active_position:
                    order_book = await self.get_order_book()
                    bid_price = order_book.get('bid')
                    ask_price = order_book.get('ask')

                    if bid_price is None or ask_price is None:
                        logger.error("Failed to fetch prices from the order book")
                        continue

                    # Check if the target price is reached
                    if bid_price >= self.active_position['target_price']:
                        # Close the position when the target profit is reached
                        await self.close_position()
            except Exception as e:
                logger.error(f"Error while monitoring position: {e}")

            await asyncio.sleep(0.5)

    @staticmethod
    def calculate_target(amount: float) -> float:
        """Calculates the target price based on the profit percentage.

        Args:
            amount (float): The initial amount for calculation (e.g., entry price or amount).

        Returns:
            float: The calculated target price based on the target profit percentage.
        """
        return round(amount * (1 + TARGET_PROFIT_PERCENT / 100), 3)

    @staticmethod
    async def get_order_book() -> dict:
        """Fetches the order book for the specified trading pair.

        Retrieves the current bid (buy) and ask (sell) prices from the order book.

        Returns:
            dict: A dictionary containing 'bid' and 'ask' prices.
        """
        try:
            response = session.get_orderbook(category="spot", symbol=SYMBOL)
            bid_price = float(response['result']['b'][0][0])  # Buy price
            ask_price = float(response['result']['a'][0][0])  # Sell price
            return {'bid': bid_price, 'ask': ask_price}
        except Exception as e:
            logger.error(f"Error while fetching order book: {e}")


# Bot initialization
trading_bot = TradingBot()


async def send_notification(message: str) -> None:
    """Sends a notification to Telegram.

    Sends the specified message to the Telegram chat using the bot.

    Args:
        message (str): The message to send.
    """
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f"Sent notification to Telegram: {message}")
    except Exception as e:
        logger.error(f"Error while sending notification to Telegram: {e}")


async def start_bot():
    """Starts the bot and begins polling for new messages."""
    await dp.start_polling(bot)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Handles the /start command."""
    await message.answer(
        "👋 Hello! I am a trading bot for Bybit.\n"
        "Available commands:\n"
        "/trade - open a new position\n"
        "/status - check the current position"
    )


@dp.message(Command("status"))
async def status_command(message: types.Message):
    """Handles the /status command."""
    if trading_bot.active_position:
        order_book = await trading_bot.get_order_book()
        current_price = order_book.get('bid')
        current_profit = ((current_price / trading_bot.active_position['entry_price']) - 1) * 100

        await message.answer(
            f"📊 Current position:\n"
            f"Trading Pair: {trading_bot.active_position['symbol']}\n"
            f"Entry Price: {trading_bot.active_position['entry_price']}\n"
            f"Current Price: {current_price}\n"
            f"Current Profit: {current_profit:.2f}%\n"
            f"Target Profit: {TARGET_PROFIT_PERCENT}%"
        )
    else:
        await message.answer("❌ No open positions")


@dp.message(Command("trade"))
async def trade_command(message: types.Message):
    """Handles the /trade command to open a new position."""
    if trading_bot.active_position:
        await message.answer("❌ You already have an open position!")
        return

    try:
        if await trading_bot.open_position():
            await message.answer(
                f"✅ Position opened!\n"
                f"Trading Pair: {trading_bot.active_position['symbol']}\n"
                f"Entry Price: {trading_bot.active_position['entry_price']}\n"
                f"Target Price: {trading_bot.active_position['target_price']}"
            )
        else:
            await message.answer("❌ Error while opening position")
    except Exception as e:
        await message.answer(f"❌ An error occurred: {e}")


async def set_main_menu(bot: Bot):
    """Sets the main menu commands in the Telegram bot."""
    main_menu_commands = [
        BotCommand(command='/start', description='Start the bot'),
        BotCommand(command='/trade', description='Open a position'),
        BotCommand(command='/status', description='Check current position'),
    ]
    await bot.set_my_commands(main_menu_commands)


async def main():
    """Main function to run the bot."""
    # Check for missing required environment variables
    if not all([BYBIT_API_KEY, BYBIT_API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, SYMBOL]):
        logger.error("Missing one or more required environment variables")
        return

    # Set the Telegram bot commands
    await set_main_menu(bot)

    # Start the bot
    await start_bot()


if __name__ == '__main__':
    asyncio.run(main())
