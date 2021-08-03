from alice_blue import *
# adding a sample line for repox
from helpers import nifty50_tickers, get_client, load_transactions_logs, update_transactions, save_transactions_logs
from helpers import wait_till_trading_close, get_client_balance
from constants import NULL_POS_RESP
from orders import entry_logic, check_pos_status
from process_stream import get_date
from process_stream import initiate_df, update_df, save_dfs


def on_open():
    global socket_opened
    socket_opened = True
    print("Websocket opened successfully!")


def on_message(message):
    global client
    global dfs
    global pos
    global trans_logs
    global BALANCE
    global CAN_TRADE

    symbol = message['instrument'].symbol
    print(f"{symbol} LTP: {message['ltp']}")

    # handle marketfeed
    try:
        dfs[symbol] = update_df(dfs[symbol], message)
    except Exception as e:
        print(f"Unable to update df for {symbol}...")
        print(f"Error => {e.args}")

    # logic for orders
    curr_qty = pos[symbol][0]

    # TODO: add a market regime filter to identify suitable environment to trade with
    # CAN_TRADE = check_conditions(pos["Nifty 50"])

    if symbol != "Nifty 50" and CAN_TRADE:
        try:
            if pos[symbol][0] == 0 and CAN_TRADE:  # not in a trade => check logic
                pos[symbol] = entry_logic(client, dfs[symbol], symbol)
            else:  # in a trade => check if we have a position (because of limit order)
                pos[symbol] = check_pos_status(client, pos[symbol], dfs[symbol], symbol)

        except Exception as e:
            print("Unable to run logic for checking trades...")
            print(f"Error => {e.args}")

        # TODO: need to check the log for executed trades
        # transaction logs
        try:
            entry = [get_date(message["exchange_time_stamp"]), symbol, pos[symbol][1], pos[symbol][0]]
            if curr_qty != entry[-1]:
                trans_logs = update_transactions(trans_logs, entry)

        except Exception as e:
            print("Failed to create logs...")
            print(f"Error => {e.args}")


def on_close():
    print("Websocket closed!")
    print("Saving files...")
    global dfs
    global trans_logs
    save_dfs(dfs)
    save_transactions_logs(trans_logs)


def on_keyboard_interrupt():
    on_close()


def main(client):
    global tickers
    global dfs
    global socket_opened

    # establish connection with websocket
    client.start_websocket(socket_open_callback=on_open,
                           subscribe_callback=on_message,
                           socket_close_callback=on_close,
                           socket_error_callback=on_close,
                           run_in_background=True)

    # wait for connection to be established
    while not socket_opened:
        pass

    # marketfeed subscriptions
    instruments = [client.get_instrument_by_symbol("NSE", ticker) for ticker in tickers]
    client.subscribe(instruments, LiveFeedType.MARKET_DATA)

    wait_till_trading_close()


if __name__ == "__main__":

    # TODO: need to create a script that runs in the morning to check for range bound stocks for tickers list
    tickers = nifty50_tickers()
    tickers.append("Nifty 50")
    dfs = {ticker: initiate_df() for ticker in tickers}
    pos = {ticker: NULL_POS_RESP for ticker in tickers}  # [shares, oms order id, target, stoploss]
    trans_logs = load_transactions_logs()
    socket_opened = False
    client = get_client(False)
    BALANCE = get_client_balance(client)
    CAN_TRADE = True
    try:
        main(client)
    except KeyboardInterrupt:
        on_keyboard_interrupt()
        print("Exiting...")
