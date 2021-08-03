from alice_blue import TransactionType, OrderType, ProductType

from constants import LOSS_EXIT, PROFIT_EXIT, STDEV, N_PERIODS, RSI_OVERSOLD, RSI_OVERBOUGHT
from constants import TRANSACTIONS, MAX_LOSS_PER_TRADE, NULL_POS_RESP
from helpers import round_
from math import floor


def calc_entry_params(df):
    dev = (df.iloc[-1, -3] - df.iloc[-1, -2]) / STDEV
    sl = (LOSS_EXIT - STDEV) * dev
    sl = round_(sl)
    target = (STDEV - PROFIT_EXIT) * dev
    target = round_(target)
    # TODO: define max loss per trade as per client margin available (like threshold of .1%)
    quantity = floor(MAX_LOSS_PER_TRADE / sl)
    return target, sl, quantity


def check_pos_status(client, pos, df, scrip):
    response = client.get_order_history(pos[1])
    # we get 4 'data' objects when we place bracket order, so need to check the status of the first one
    # order_status in ['open', 'open pending', 'validation pending', 'put order req received']
    order_status = response['data'][0]['order_status']
    if order_status == "open":
        # check if scrip has entered the bands before execution
        if df.iloc[-1, -2] < df.iloc[-1, 3] < df.iloc[-1, -4]:
            close_order_status = client.cancel_order(pos[1])
            if close_order_status['message'] == 'Order placed successfully':
                return NULL_POS_RESP
            else:
                print(f"Failed to cancel order for {scrip}!")
                print(close_order_status['message'])
    return pos


# bracket order implementation
def entry_logic(client, df, scrip):
    # size check
    if df.shape[0] < N_PERIODS:
        return NULL_POS_RESP

    ltp = df.iloc[-1, 3]
    rsi = df.iloc[-1, -1]
    u = df.iloc[-1, -4]
    m = df.iloc[-1, -3]
    l = df.iloc[-1, -2]
    std = (u-m)/STDEV

    l_bound = m - LOSS_EXIT*std
    u_bound = m + LOSS_EXIT*std

    if (l_bound < ltp < l) and (rsi < RSI_OVERSOLD):  # buy logic
        target, sl, quantity = calc_entry_params(df)
        if quantity == 0:
            return NULL_POS_RESP
        response = _entry_order(client, TransactionType.Buy, scrip, ltp, quantity, target, sl)
        return [*response, target, sl]  # qty here

    elif (u < ltp < u_bound) and (rsi > RSI_OVERBOUGHT):  # sell logic
        target, sl, quantity = calc_entry_params(df)
        if quantity == 0:
            return NULL_POS_RESP
        response = _entry_order(client, TransactionType.Sell, scrip, ltp, quantity, target, sl)
        return [*response, target, sl]  # qty here

    return NULL_POS_RESP


def _entry_order(client, order_type, scrip, price, quantity, target, stop_loss):
    side = TRANSACTIONS[order_type]

    order_response = client.place_order(transaction_type=order_type,
                                        instrument=client.get_instrument_by_symbol('NSE', scrip),
                                        quantity=quantity,
                                        order_type=OrderType.Limit,
                                        product_type=ProductType.BracketOrder,
                                        price=round(price, 2),
                                        trigger_price=None,
                                        stop_loss=round(stop_loss, 2),
                                        square_off=round(target, 2),
                                        trailing_sl=None,
                                        is_amo=False)

    # check if order actually successful
    if order_response["message"] == 'Order placed successfully':
        print(f"Order placed for {scrip} at for qty = {side * quantity}!")
        return [quantity * side, order_response['data']['oms_order_id']]

    # else return the same position status
    else:
        print(f"Failed to place order for {scrip}!")
        print(order_response["message"])

    return NULL_POS_RESP[:3]
