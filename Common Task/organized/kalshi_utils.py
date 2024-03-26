import uuid
import kalshi_python
from kalshi_python.models import *
from pprint import pprint
from datetime import datetime 
import pandas as pd

class KalshiAPI:
    def __init__(self):
        self.config = kalshi_python.Configuration()
        self.config.host = 'https://demo-api.kalshi.co/trade-api/v2'
        self.kalshi_api = kalshi_python.ApiInstance(
            email='mahdouch@bu.edu',
            password='GetHooked9165*',
            configuration=self.config,
        )

    def get_api_client(self):
        return self.kalshi_api       

    def format_event_ticker(self, ticker):
        today = datetime.now()
        event = ticker + '-' + today.strftime('%y%b%d').upper()
        return event

    def get_event_markets(self, event):
        event_details = self.kalshi_api.get_event(event)
        # extract markets
        markets = event_details.markets
        return markets

    def get_exchange_status(self):
        exchangeStatus = self.kalshi_api.get_exchange_status()
        return exchangeStatus
    
    def place_orders(self, prediction, markets):
        # round prediction to int with 0.5 rounding
        prediction = int(round(prediction))
        # for each market, place an order
        def place_quick_order(market, side, action = 'buy', quantity = 1):
            # create a quick order
            orderUuid = str(uuid.uuid4())
            orderResponse = self.kalshi_api.create_order(
                CreateOrderRequest(
                    ticker = market.ticker,
                    action = action,
                    type ='market',
                    count = quantity,
                    client_order_id = orderUuid,
                    side = side,
                )                            
            )
            return orderResponse, orderUuid

        order_list = []
        for market in markets:
            cap_strike = market.cap_strike
            floor_strike = market.floor_strike
            side = None
            # Check if no floor strike
            if floor_strike == None:
                # If prediction is less than cap_strike, create a quick buy order
                if prediction < cap_strike:
                    side = "yes"
                    order_response, order_uuid = place_quick_order(market, side = "yes")
                else:
                    side = "no"
                    order_response, order_uuid = place_quick_order(market, side = "no")
            elif cap_strike == None:
                if prediction > floor_strike:
                    side = "yes"
                    order_response, order_uuid = place_quick_order(market, side = "yes")
                else:
                    side = "no"
                    order_response, order_uuid = place_quick_order(market, side = "no")
            else:
                if prediction == cap_strike or prediction == floor_strike:
                    side = "yes"
                    order_response, order_uuid = place_quick_order(market, side = "yes")
                else:
                    side = "no"
                    order_response, order_uuid = place_quick_order(market, side = "no")
            order_dict = {
                'market': market,
                'order_response': order_response,
                'order_uuid': order_uuid,
                'quantity': 1,
                'type': 'market',
                'ticker': market.ticker,
                'action': 'buy',
                'side': side           
            }
            order_list.append(order_dict)
        return order_list
    
    def log_order(self, order_list, history_path, prediction):
        # check if 
        expected_columns = ['date_time', 'client_order_id', 'ticker', 'subtitle', 'cap_strike', 'floor_strike', 'prediction', 'type', 'action', 'side', 'quantity', 'result', 'return']
        try:
            df = pd.read_csv(history_path)
        except:
            df = pd.DataFrame(columns=expected_columns)
            
        for order in order_list:
            order_dict = {}
            try:
                order['order_response'] = order['order_response'].to_dict()
            except:
                pass
            try:
                order['market'] = order['market'].to_dict()
            except:
                pass
            order_dict['date_time'] = order['order_response']['order']['created_time']
            order_dict['client_order_id'] = order['order_response']['order']['client_order_id']
            order_dict['ticker'] = order['order_response']['order']['ticker']
            order_dict['subtitle'] = order['market']['subtitle']
            order_dict['cap_strike'] = order['market']['cap_strike']
            order_dict['floor_strike'] = order['market']['floor_strike']
            if order_dict['cap_strike'] == None:
                order_dict['cap_strike'] = 1000
            if order_dict['floor_strike'] == None:
                order_dict['floor_strike'] = -1000
            order_dict['prediction'] = prediction
            order_dict['type'] = order['order_response']['order']['type']
            order_dict['action'] = order['order_response']['order']['action']
            order_dict['side'] = order['order_response']['order']['side']
            order_dict['quantity'] = order['quantity']
            order_dict['result'] = 0
            order_dict['return'] = 0
            
            df = pd.concat([df, pd.DataFrame([order_dict])], ignore_index=True)
            
        df.to_csv(history_path, index=False)
        
    def update_old_orders(self, history_path):
        settlements = self.kalshi_api.get_portfolio_settlements()
        try:
            df = pd.read_csv(history_path)
        except:
            return
        df['date_time'] = pd.to_datetime(df['date_time'])

        # look for orders that have not been created today
        today = datetime.now().date()
        rows = df[(df['result'] == 0) & (df['return'] == 0) & (df['date_time'].dt.date != today)]

        for index, row in rows.iterrows():
            ticker = row['ticker']
            for settlement in settlements.settlements:
                if settlement.ticker == ticker:
                    revenue = settlement.revenue
                    no_cost = settlement.no_total_cost
                    yes_cost = settlement.yes_total_cost
                    total_cost = no_cost + yes_cost
                    if revenue == 0:
                        result = -1
                        return_val = -total_cost
                    else:
                        result = 1
                        return_val = revenue
                    df.at[index, 'result'] = result
                    df.at[index, 'return'] = return_val
                    break

        df.to_csv(history_path, index=False)