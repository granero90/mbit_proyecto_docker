from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import os
from copy import deepcopy

def main():
        ##CONFIG
        config = json.load(open('/app/code/in/docker_config.json', 'r'))

        ##MONGODB CONFIG
        ################################
        ####### Incluir código #########
        ################################

        df_global = pd.DataFrame(columns=['Symbol', 'AggregateTradeId', 'Price', 'Quantity', 'TradeTime', 'Variable'])

        def get_stocastic(df):
                global suma, suma2, suma3
                global rank, rank2, rank3

                def each_serie(x):
                        limit = config["rango1"]
                        limit2 = config["rango2"]
                        limit3 = config["rango3"]
                        global suma, suma2, suma3
                        global rank, rank2, rank3
                        suma += x
                        suma2 += x
                        suma3 += x
                        if suma >= limit:
                                while suma >= limit:
                                        suma = suma-limit
                                        rank += 1
                        elif suma <= -limit:
                                while suma <= -limit:
                                        suma = suma+limit
                                        rank += 1
                        if suma2 >= limit2:
                                while suma2 >= limit2:
                                        suma2 = suma2-limit2
                                        rank2 += 1
                        elif suma2 <= -limit2:
                                while suma2 <= -limit2:
                                        suma2 = suma2+limit2
                                        rank2 += 1
                        if suma3 >= limit3:
                                while suma3 >= limit3:
                                        suma3 = suma3-limit3
                                        rank3 += 1
                        elif suma3 <= -limit3:
                                while suma3 <= -limit3:
                                        suma3 = suma3+limit3
                                        rank3 += 1
                        return f"{rank},{rank2},{rank3}"

                df['ManualRolling'] = df['Price'].astype(float) - df['Price'].shift(periods=+1).astype(float) 
                df=df.fillna(method='bfill')

                rank,suma,rank2,suma2,rank3,suma3 = 0,0,0,0,0,0
                df[["Rank","Rank2","Rank3"]] = df['ManualRolling'].apply(each_serie).str.split(',', 2, expand=True)
                df["Rank"] = df['Rank'].astype(int)
                df["Rank2"] = df['Rank2'].astype(int)
                df["Rank3"] = df['Rank3'].astype(int)
                df["Quantity"]=df["Quantity"].astype(float)

                DeltaAuction = sum(df.loc[df.Rank < config['series']].loc[df.Variable == "Ask"]["Quantity"]) - sum(df.loc[df.Rank < config['series']].loc[df.Variable == "Bid"]["Quantity"])
                Delta2Auction = sum(df.loc[df.Rank2 < config['series']].loc[df.Variable == "Ask"]["Quantity"]) - sum(df.loc[df.Rank2 < config['series']].loc[df.Variable == "Bid"]["Quantity"])
                Delta3Auction = sum(df.loc[df.Rank3 < config['series']].loc[df.Variable == "Ask"]["Quantity"]) - sum(df.loc[df.Rank3 < config['series']].loc[df.Variable == "Bid"]["Quantity"])

                max_series = max(df["Rank"])
                max_series2 = max(df["Rank2"])
                max_series3 = max(df["Rank3"])
                
                return DeltaAuction, Delta2Auction, Delta3Auction, max_series, max_series2, max_series3

        def fill_variable(x):
                global variable
                if x > 0: 
                        variable = "Ask"
                elif x < 0: 
                        variable = "Bid"
                elif x == 0: 
                        variable = np.nan
                return variable

        timestamp = int(datetime.timestamp(datetime.now())*1e3)
        cursorMarket = collectionMarket.find({}).sort([("AggregateTradeId", DESCENDING)])
        df_market =  pd.DataFrame(list(cursorMarket))

        df_partition = df_market[['Symbol', 'AggregateTradeId', 'Price', 'Quantity', 'TradeTime']]\
                .drop_duplicates(["AggregateTradeId","TradeTime"],keep='first')\
                .reset_index(drop=True)

        df_partition['Diff']=df_partition['Price'].astype(float) - df_partition['Price'].astype(float).shift(periods=-1)
        df_partition["Variable"]=df_partition['Diff'].apply(fill_variable)
        df_partition["Variable"]=df_partition["Variable"].fillna(method='bfill')

        df_global = pd.concat([df_global, df_partition]).drop("Diff",axis=1)

        df_global=df_global.loc[df_global.TradeTime >= int(datetime.timestamp(datetime.now() - timedelta(minutes=config['time_window']))*1e3)]
        df_global=df_global.drop_duplicates(["AggregateTradeId"],keep="first").sort_values("AggregateTradeId",ascending=False).reset_index(drop=True)
        df=deepcopy(df_global)

        return get_stocastic(df)