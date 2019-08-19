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
season_label = "Season"

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

def season(df):
    if ((df[datetime_label].month == 12) or (df[datetime_label].month == 1) or
        (df[datetime_label].month == 2)):
        season = 1

    elif ((df[datetime_label].month == 3) or (df[datetime_label].month == 4) or
    (df[datetime_label].month == 5)):
        season = 2

    elif ((df[datetime_label].month == 6) or (df[datetime_label].month == 7) or
          (df[datetime_label].month == 8)):
        season = 3

    elif ((df[datetime_label].month == 9 ) or (df[datetime_label].month == 10) or
          (df[datetime_label].month == 11)):
        season = 4

    return season


# Reading main data and selecting---------------------------------------------------------------------------------------
df = pd.read_csv('all_data_all_weather_stations.csv') # reading data
#df = df.sample(n=1000)
df = df[select] # selecting variables
df[datetime_label] = pd.to_datetime(df[datetime_label]) # converting to datetime

df = df[df[datetime_label].apply(lambda d: d.hour == 6)] # Selecting data 6am
df[estimation_label] = df.apply(dew_estimation_function, axis=1) #Estimating dew yield
df[season_label] = df.apply(season, axis=1) #Classifying seasons

df1 = df.groupby([df[name_label], df[season_label]])[estimation_label].mean().reset_index().rename(
    columns={name_label:name_label,season_label : season_label, estimation_label:estimation_label}) # Average Dew yield mean by weather station and season

df1.set_index(name_label, inplace = True) #selecting index
df1[estimation_label] = round(df1[estimation_label],3)
df1.to_csv('dew_estimation.csv', encoding="utf-8") #Saving data

df_season1 = df1[df1[season_label].apply(lambda d: d == 1)] # Filtering data by season 1
df_season2 = df1[df1[season_label].apply(lambda d: d == 2)] # Filtering data by season 2
df_season3 = df1[df1[season_label].apply(lambda d: d == 3)] # Filtering data by season 3
df_season4 = df1[df1[season_label].apply(lambda d: d == 4)] # Filtering data by season 4

df_season1.to_csv('df_season1.csv',encoding="utf-8") #Saving data seasons 1
df_season2.to_csv('df_season2.csv',encoding="utf-8") #Saving data seasons 2
df_season3.to_csv('df_season3.csv',encoding="utf-8") #Saving data seasons 3
df_season4.to_csv('df_season4.csv',encoding="utf-8") #Saving data seasons 4
