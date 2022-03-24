import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

df_falta_agua = pd.read_csv('falta-agua-jun2018-jun2019.csv')
df_fuga_agua = pd.read_csv('fugas-de-agua-jun8-al-jun19.csv')

# valid_cols = ['no. Folio', 'usuario', 'fecha', 'tipo de problema', 'zona', 'colonia', 'solucion/respuesta', 'status folio']
same_cols = set(df_falta_agua.columns) & set(df_fuga_agua.columns)

valid_cols = ['usuario','fecha','zona']
df_falta_agua = df_falta_agua[valid_cols]

print(df_falta_agua.describe())
print()
print(df_fuga_agua.describe())
print()

df_falta_agua.fecha = pd.to_datetime(df_falta_agua.fecha)
df_falta_agua = df_falta_agua.set_index('fecha')
df_falta_agua = df_falta_agua.loc[df_falta_agua.index.dropna()]
df_falta_agua['Year'] = df_falta_agua.index.year
df_falta_agua['Month'] = df_falta_agua.index.month
df_falta_agua['Week'] = df_falta_agua.index.isocalendar().week
df_falta_agua['Weekday Name'] = df_falta_agua.index.weekday
df_falta_agua['Date'] = df_falta_agua.index.date
df_falta_agua['Time'] = [float('{0}.{1}'.format(el.time().hour, el.time().minute)) for el in df_falta_agua.index]

df_fuga_agua.fecha = pd.to_datetime(df_fuga_agua.fecha)
df_fuga_agua = df_fuga_agua.set_index('fecha')
df_fuga_agua = df_fuga_agua.loc[df_fuga_agua.index.dropna()]
df_fuga_agua['Year'] = df_fuga_agua.index.year
df_fuga_agua['Month'] = df_fuga_agua.index.month
df_fuga_agua['Week'] = df_fuga_agua.index.isocalendar().week
df_fuga_agua['Weekday Name'] = df_fuga_agua.index.weekday
df_fuga_agua['Date'] = df_fuga_agua.index.date
df_fuga_agua['Time'] = [float('{0}.{1}'.format(el.time().hour, el.time().minute)) for el in df_fuga_agua.index]

print(df_falta_agua.describe())
print()

df_falta_agua = df_falta_agua[df_falta_agua.Month == 6]
df_falta_agua = df_falta_agua[df_falta_agua.Year == 2018]

print(df_falta_agua.head())