#Importing libraries ---------------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import math
from geopandas.geoseries import Point
import datetime

# defining variables ---------------------------------------------------------------------------------------------------

temperature_label = "Temperatura"
humidity_label = "Umidade"
dew_label = "Ponto_orvalho"
wind_label="Vento_velocidade"
pressure_label = "Pressao"
name_label ="nome"
region_label = "NM_MICRO"
estimation_label = "Estimation"
temperature_difference_label ="Temperature difference"

datetime_label ="datetime"

station_label = "cod"
latitude_label = "lat"
altitude_label = "alt"
longitude_label ="lon"
season_label = "Season"

Ra = 0.28705

select = [temperature_label,humidity_label,dew_label,wind_label,datetime_label,
          name_label,latitude_label,longitude_label,altitude_label,pressure_label,station_label]

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

def other_parameters (row):

    temp = row[temperature_label]
    T = row[temperature_label]+ 273.15
    Hr = row[humidity_label]
    P = row[pressure_label]
    w = row[wind_label]
    d = row[dew_label]
    pressure_vapor_saturation = math.exp(-7511.52 / T + 89.63121 + 0.02399897 * T - (1.1654551 * math.pow(10, -5) *
                                math.pow(T, 2)) - 1.2810336 * math.pow(10, -8) * math.pow(T,3) + 2.0998405 *
                                math.pow(10, -11) * math.pow(T, 4) - 12.150799 * math.log(T));

    pressure_vapor  = (Hr / 100) * pressure_vapor_saturation

    mixing_ratio  = np.round((0.62198 * (pressure_vapor / (P - pressure_vapor))*1000),3)
    specific_volume = (Ra * T / P) * (1 + 1.6078 * mixing_ratio)
    water_avaibility = np.round(((1/specific_volume) * mixing_ratio) * w * 3600/1000,3)
    energy = -((1000/mixing_ratio)*1.005*(d- temp) - 1*2260)* 0.0002778
    return pd.Series({"mixing_ratio":mixing_ratio,'water_avaibility':water_avaibility, 'energy': energy})


# Reading main data and selecting---------------------------------------------------------------------------------------
df = pd.read_csv('all_data_all_weather_stations.csv') # reading data
df = df[select] # selecting variables
df = df[(df.cod != "C891")]
df =df.sample(500)
df[datetime_label] = pd.to_datetime(df[datetime_label]) # converting to datetime
df_parameters = df


# Estimating dew yield -------------------------------------------------------------------------------------------------
df = df[df[datetime_label].apply(lambda d: d.hour == 6)] # Selecting data 6am
df[estimation_label] = df.apply(dew_estimation_function, axis=1) #Estimating dew yield
df[season_label] = df.apply(season, axis=1) #Classifying seasons

# Average parameters (11pm to 6am)--------------------------------------------------------------------------------------

df_parameters = df_parameters[df_parameters[datetime_label].apply(lambda d: (d.hour <= 6 or d.hour == 23 ))] #filtering time
df_parameters[season_label] = df_parameters.apply(season, axis=1) #Classifying seasons

df_parameters[temperature_difference_label] = df_parameters[temperature_label] - df_parameters[dew_label] #temperature diference
df_parameters[["mixing_ratio",'water_avaibility','energy']] = df_parameters.apply(other_parameters, axis=1) #Other parameters

#print(df_parameters)

average_humidity = round(df_parameters.groupby([df_parameters[name_label], df_parameters[season_label]])[humidity_label].mean(),3)
average_temperature = round(df_parameters.groupby([df_parameters[name_label], df_parameters[season_label]])[temperature_label].mean(),3)
average_difference_temperature = round(df_parameters.groupby([df_parameters[name_label], df_parameters[season_label]])[temperature_difference_label].mean(),3)
average_mixing_ratio = round(df_parameters.groupby([df_parameters[name_label], df_parameters[season_label]])["mixing_ratio"].mean(),3)
average_energy = round(df_parameters.groupby([df_parameters[name_label], df_parameters[season_label]])["energy"].mean(),3)
average_water_avaibility = round(df_parameters.groupby([df_parameters[name_label], df_parameters[season_label]])["water_avaibility"].mean(),3)

df_complete = pd.concat([average_humidity, average_temperature, average_difference_temperature, average_mixing_ratio,
               average_energy,average_water_avaibility], axis=1).reset_index()

#print (df_complete)
# Agruping by season----------------------------------------------------------------------------------------------------
df1 = df.groupby([df[name_label], df[season_label]])[estimation_label].mean().reset_index().rename(
    columns={name_label:name_label,season_label : season_label, estimation_label:estimation_label}) # Average Dew yield mean by weather station and season

df1.set_index([name_label, season_label],inplace = True) #selecting index
df_complete.set_index([name_label, season_label],inplace = True) #selecting index

df1[estimation_label] = round(df1[estimation_label],3)

result = pd.merge(df_complete,df1, how= 'outer', left_index= True, right_index= True)
result = result.reset_index()
result.set_index(name_label)

df_season1 = result[result[season_label].apply(lambda d: d == 1)] # Filtering data by season 1
df_season2 = result[result[season_label].apply(lambda d: d == 2)] # Filtering data by season 2
df_season3 = result[result[season_label].apply(lambda d: d == 3)] # Filtering data by season 3
df_season4 = result[result[season_label].apply(lambda d: d == 4)] # Filtering data by season 4

df_season1.to_csv('df_season1.csv',encoding="utf-8") #Saving data seasons 1
df_season2.to_csv('df_season2.csv',encoding="utf-8") #Saving data seasons 2
df_season3.to_csv('df_season3.csv',encoding="utf-8") #Saving data seasons 3
df_season4.to_csv('df_season4.csv',encoding="utf-8") #Saving data seasons 4
