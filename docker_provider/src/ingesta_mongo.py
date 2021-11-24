from pymongo import MongoClient, DESCENDING
from datetime import datetime
import time
import logging
import websocket
import json, os

##Config
config = json.load(open('/app/code/in/docker_config.json', 'r'))

#DIRECTORY
directory = f"/app/code/out/{config['symbol']}"
if not os.path.exists(directory):
        os.makedirs(directory)

# LOGGING CONFIG
timeStamp = int(datetime.timestamp(datetime.now())*1e3)
logging.basicConfig(level=logging.INFO, filename=f'{directory}/{timeStamp}-ingesta_mongo.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

logging.info('La ejecución ha comenzado.')

##Connection to DB MongoDB

################################
####### Incluir código #########
################################

collection.drop_indexes()
collection.create_index([('AggregateTradeId', DESCENDING)], unique=True)

socket='wss://stream.binance.com:9443/ws'

def on_open(self):
    logging.info(f"Conexión abierta.")
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params":
        [
         f"{config['symbol']}@aggTrade"
        ],
        "id": 1
        }

    ws.send(json.dumps(subscribe_message))

def on_message(self, message):
   
    d = json.loads(message)
    dataM =  {"Symbol": d["s"],
              "AggregateTradeId": d["a"],
              "Price": d["p"],
              "Quantity": d["q"],
              "TradeTime": d["T"],
              "Timestamp": int(time.time() * 1e3)
            }

    collection.insert_one(dataM)
    logging.info(f"Se ha ingestado un nuevo registro con el campo AggregateTradeId: {d['a']}.")

def on_error(self, error):
    logging.error(f"Error: {str(error)}")

def on_close(self):
    logging.info(f"Se cierra la conexión.")
    unsubscribe_message = {
        "method": "UNSUBSCRIBE",
        "params": [
         f"{config['symbol']}@aggTrade"
        ],
        "id": 1
        }
    ws.send(json.dumps(unsubscribe_message))

ws = websocket.WebSocketApp(socket,
                            on_open=on_open,
                            on_message=on_message,
                            on_error = on_error,
                            on_close=on_close)

ws.run_forever(ping_interval=300, ping_timeout=60)