from datetime import datetime
import requests
import json
import os, logging
import telebot

def main():
        ##CONFIG
        config = json.load(open('/app/code/in/docker_config.json', 'r'))

        ##DIRECTORY
        directory = f"/app/code/out/{config['symbol']}"
        if not os.path.exists(directory):
                os.makedirs(directory)

        ##LOGGING CONFIG
        timeStamp = int(datetime.timestamp(datetime.now())*1e3)
        logging.basicConfig(level=logging.INFO, filename=f'{directory}/{timeStamp}-consume.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

        ##PRINT PARAMS
        logging.info("Parámetros archivo config:")
        for k, v in config.items():
                logging.info("{0}: {1}".format(k, v))

        ##TELEGRAM CONFIG
        tb = telebot.TeleBot(config["api_telebot"])
        logging.info('La ejecución ha comenzado.')

        Flag = 0
        rent_ac = 0

        while True:
                r = requests.get("https://api.binance.com/api/v3/klines", params={"symbol":config['symbol'].upper(), "interval":"1d", "limit":1})
                if r.status_code == 200: 
                        open_ = float(r.json()[0][1])
                        price = float(r.json()[0][4])
                        netchange = round((price - open_)/price*100,2)
                
                ################################
                ####### Incluir código #########
                ################################

                if r.status_code == 200: 

                        ################################
                        ####### Incluir código #########
                        ################################

                if ((max_series >= config["series"]) and (max_series2 >= config["series"]) and (max_series3 >= config["series"])):
                        logging.info(f"Datos Suficientes: - Symbol: {config['symbol'].upper()} - Price: {price} - DeltaAuction: {DeltaAuction} - Delta2Auction: {Delta2Auction} - Delta3Auction: {Delta3Auction} - Netchange: {netchange}")
                        if (DeltaAuction > 0 and Delta2Auction > 0 and Delta3Auction > 0 and Flag == 0):
                                precio_compra = price
                                text2print = f"🤖🤖🤖 SEÑAL DE COMPRA 🤖🤖🤖\n- Símbolo: {config['symbol'].upper()}\n- Precio de compra: {price}."
                                logging.info(text2print)
                                if config["telegram_groupId"] != 0: tb.send_message(config["telegram_groupId"], text2print)
                                Flag = 1
                        elif (DeltaAuction < 0 and Delta2Auction < 0 and Delta3Auction < 0 and Flag == 1):
                                precio_venta = price
                                rent = (precio_venta-precio_compra)*100/precio_compra
                                rent_ac += rent
                                flag_result = "📈📈📈" if rent > 0 else "📉📉📉"
                                flag_result_ac = "📈📈📈" if rent_ac > 0 else "📉📉📉"
                                text2print = f"🤖🤖🤖 SEÑAL DE VENTA 🤖🤖🤖\n- Símbolo: {config['symbol'].upper()}\n- Precio de venta: {price}\n- Rentabilidad: {round(float(rent),3)} {flag_result}\n- Rentabilidad acumulada: {rent_ac} {flag_result_ac}"
                                logging.info(text2print)
                                if config["telegram_groupId"] != 0: tb.send_message(config["telegram_groupId"], text2print)
                                Flag = 0
                else:
                        logging.info(f"Datos Insuficientes: - Symbol: {config['symbol'].upper()} - Price: {price} - DeltaAuction: {DeltaAuction} - Delta2Auction: {Delta2Auction} - Delta3Auction: {Delta3Auction} - Netchange: {netchange}")

if __name__ == '__main__':
        main()
