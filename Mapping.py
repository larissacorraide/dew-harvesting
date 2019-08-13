#Importing libraries ---------------------------------------------------------------------------------------------------

import pandas as pd


# defining variables ---------------------------------------------------------------------------------------------------


temperature_label = "Temperatura"
humidity_label = "Umidade"
dew_label = "Ponto_orvalho"
wind_label="Vento_velocidade"
pressure_label = "Pressao"
name_label ="nome"

date_label ="datetime"

station_label = "cod"
latitude_label = "lat"
altitude_label = "alt"
longitude_label ="lon"

select = [temperature_label,humidity_label,dew_label,wind_label,date_label,
          name_label,latitude_label,longitude_label,altitude_label]

# Reading main data-----------------------------------------------------------------------------------------------------
df = pd.read_csv('all_data_all_weather_stations.csv')

df = df[select]
print(df)