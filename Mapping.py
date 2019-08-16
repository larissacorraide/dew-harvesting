#Importing libraries ---------------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import math
import datetime

# defining variables ---------------------------------------------------------------------------------------------------

temperature_label = "Temperatura"
humidity_label = "Umidade"
dew_label = "Ponto_orvalho"
wind_label="Vento_velocidade"
pressure_label = "Pressao"
name_label ="nome"
estimation_label = "Estimation"

datetime_label ="datetime"

station_label = "cod"
latitude_label = "lat"
altitude_label = "alt"
longitude_label ="lon"

select = [temperature_label,humidity_label,dew_label,wind_label,datetime_label,
          name_label,latitude_label,longitude_label,altitude_label]

# functions ------------------------------------------------------------------------------------------------------------

def dew_estimation_function (row):

    try:
        H = row[altitude_label]/1000
        Ta= row[temperature_label]
        Td= row[dew_label]
        L = row [latitude_label]
        C=0
        w = row[wind_label]

        dew_estimation = np.round((((0.37 * (1 + (0.204323 * H) - (0.0238893 * (H ** 2)) - (18.0123 -
                        (1.04963 * H) + (0.21891 * (H ** 2))) * (10 ** (-3)) * Td) * (((Td + 273.15) / 285) ** 4)
                        *((1 - (C / 8)))) + (0.06 * (Td - Ta) * (1 + (100 * (1 - math.exp(-(w / 4.4) ** 20)))))/12))*7,4)


        if ((dew_estimation < 0) or (w >= 4.4)):
            dew_estimation = 0

        return dew_estimation

    except:
        print("Erro")


# Reading main data and selecting---------------------------------------------------------------------------------------
df = pd.read_csv('all_data_all_weather_stations.csv')
df = df[select]

df[datetime_label] = pd.to_datetime(df[datetime_label])

df = df[df[datetime_label].apply(lambda d: d.hour == 6)] # Selecting data 6am

df[estimation_label] = df.apply(dew_estimation_function, axis=1) #Estimating dew yield

df1 = df.groupby([df[name_label], df[datetime_label].dt.month])[estimation_label].mean() #Dew yield mean by weather station

df1.to_csv('teste.csv',encoding="utf-8") #Saving data


#df[datetime_label].dt.month