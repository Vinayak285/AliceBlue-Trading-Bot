def _entry_order(client, order_type, scrip, quantity):
    side = TRANSACTIONS[order_type]

    order_response = client.place_order(transaction_type=order_type,
                                        instrument=client.get_instrument_by_symbol('NSE', scrip),
                                        quantity=quantity,
                                        order_type=OrderType.Market,
                                        product_type=ProductType.Intraday,
                                        price=0.0,
                                        trigger_price=None,
                                        stop_loss=None,
                                        square_off=None,
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

    return [0, '']


def entry_logic(client, df, scrip):
    # size check
    if df.shape[0] < N_PERIODS:
        return [0, '', 0., 0.]

    price = df.iloc[-1, 3]
    rsi = df.iloc[-1, -1]

    if price < df.iloc[-1, -2] and rsi < RSI_OVERSOLD:  # buy
        target, sl, quantity = calc_params(df)
        if quantity <= 0:
            return [0, '', 0., 0.]
        response = _entry_order(client, TransactionType.Buy, scrip, quantity)
        return [*response, target, sl]  # qty here

    elif price > df.iloc[-1, -4] and rsi > RSI_OVERBOUGHT:  # sell
        target, sl, quantity = calc_params(df)
        if quantity <= 0:
            return [0, '', 0., 0.]
        response = _entry_order(client, TransactionType.Sell, scrip, quantity)
        return [*response, target, sl]  # qty here

    return [0, '', 0., 0.]


def _exit_order(client, scrip, pos):
    trans_type = TRANSACTIONS_INV[pos[0]]

    order_response = client.place_order(transaction_type=trans_type,
                                        instrument=client.get_instrument_by_symbol('NSE', scrip),
                                        quantity=abs(pos[0]),
                                        order_type=OrderType.Market,
                                        product_type=ProductType.Intraday,
                                        price=0.0,
                                        trigger_price=None,
                                        stop_loss=None,
                                        square_off=None,
                                        trailing_sl=None,
                                        is_amo=False)

    # check if order execution was successful
    if order_response["message"] == 'Order placed successfully':
        print(f"Closed position in {scrip}!")
        return [0, order_response['data']['oms_order_id'], 0., 0.]

    # else return the same position status
    else:
        print(f"Failed to close position in {scrip}!")
        print(order_response["message"])
        return pos


def exit_logic(client, pos, df, scrip):
    price = df.iloc[-1, 3]

    if pos[0] > 0 and (price > pos[-2] or price < pos[-1]):
        return _exit_order(client, scrip, pos)  # qty here

    elif pos[0] < 0 and (price < pos[-2] or price > pos[-1]):
        return _exit_order(client, scrip, pos)  # qty here

    return pos
