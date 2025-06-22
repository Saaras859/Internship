import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')


def check_account():
    account = api.get_account()
    print("\n=== ACCOUNT INFO ===")
    print(f"Status         : {account.status}")
    print(f"Cash           : ${account.cash}")
    print(f"Buying Power   : ${account.buying_power}")
    print(f"Portfolio Value: ${account.portfolio_value}")


def get_stock_price(symbol):
    trade = api.get_latest_trade(symbol)
    print(f"\n=== {symbol.upper()} Latest Price ===")
    print(f"Price: ${trade.price}")
    return trade.price


def place_order(symbol, qty, side):
    print(f"\nPlacing {side.upper()} order for {qty} share(s) of {symbol.upper()}...")
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )
        print(f"✅ Order submitted! ID: {order.id}")
    except Exception as e:
        print(f"❌ Failed to place order: {e}")


def check_positions():
    positions = api.list_positions()
    if not positions:
        print("\nYou have no open positions.")
        return {}
    print("\n=== CURRENT POSITIONS ===")
    pos_dict = {}
    for pos in positions:
        print(f"Symbol: {pos.symbol}, Qty: {pos.qty}, Side: {pos.side}")
        pos_dict[pos.symbol] = float(pos.qty)
    return pos_dict


def place_sell_order_if_owned(symbol, qty):
    positions = check_positions()
    owned_qty = positions.get(symbol.upper(), 0)
    if owned_qty >= qty:
        place_order(symbol, qty, 'sell')
    else:
        print(f"\nCannot sell {qty} shares of {symbol.upper()} — insufficient holdings (owned: {owned_qty}).")


if __name__ == "__main__":
    check_account()

    stock = "AAPL"
    get_stock_price(stock)

    place_order(stock, qty=1, side="buy")

    place_sell_order_if_owned(stock, qty=1)
