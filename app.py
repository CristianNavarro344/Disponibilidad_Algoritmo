##### LIBRERIAS #####
from fastapi import FastAPI
import sqlalchemy
import pandas as pd
from math import ceil
from datetime import timedelta
app = FastAPI()


##### Conexión BB.DD #####
url = 'mysql+mysqlconnector://user:password@mysql-db:3306/scm'
engine = sqlalchemy.create_engine(url)

##### Función encargada de extraer la información cargada en la bb.dd ##### 
def get_data():
    forecast_query = "SELECT * FROM forecast"
    shifts_query = "SELECT * FROM shifts"
    with engine.connect() as conn:
        forecast_by_day = pd.read_sql_query(forecast_query, conn)
        shifts = pd.read_sql_query(shifts_query, conn)

    forecast_by_day.rename(columns={'fecha':'date'}, inplace=True)
    return (shifts,forecast_by_day)

def two_highest_keyvalue(dicc):
    dicc_copy = dict(dicc)
    key1 = max(dicc_copy, key=dicc_copy.get)
    del dicc_copy[key1]
    key2 = max(dicc_copy, key=dicc_copy.get)
    return [key1, key2]

##### Microservicio 1: Extrae la información de la base de datos para enviarla al Microservicio 2 ##### 
@app.get("/get_data_from_db")
def get_data_from_db():
    shifts, forecast_by_day= get_data()
    return {"shifts": shifts.to_dict(orient="records"), "forecast_by_day": forecast_by_day.to_dict(orient="records")}

##### Microservicio 2: Recibe la información del microservicio y la utiliza en el algoritmo entregado ##### 

@app.get("/disponibility")
def disponibility():
    data = get_data_from_db()
    shifts, forecast_by_day= pd.DataFrame(data["shifts"]), pd.DataFrame(data["forecast_by_day"])
    ##### Ya no se utiliza la lectura desde CSV de shifts ##### 
    # shifts = pd.read_csv('shifts.csv', parse_dates=['Inicio_Turno','Fin_Turno'], date_parser=lambda x: pd.to_datetime(x, format="%H:%M"))

    periodos = 24
    tiempo = [(timedelta(hours=0, minutes=15*i * 96/periodos)) for i in range(int(periodos))]

    ##### Tuve que hacer un pequeño cambio en el algoritmo ya que me daba error la linea 53 y 54.
    shifts['in'] = shifts['Inicio_Turno'].apply(lambda x: int(x.total_seconds() // 3600))
    shifts['out'] = shifts['Fin_Turno'].apply(lambda x: int(x.total_seconds() // 3600) if x.total_seconds() > 0 else len(tiempo))
    # shifts['in'] = shifts['Inicio_Turno'].apply(lambda x: tiempo.index(timedelta(hours=x.hour, minutes=x.minute)))
    # shifts['out'] = shifts['Fin_Turno'].apply(lambda x: len(tiempo) if x.hour==0 and x.minute==0 else tiempo.index(timedelta(hours=x.hour, minutes=x.minute)))
    shifts['Lenght'] = shifts['out'] - shifts['in']

    ##### Ya no se utiliza la lectura desde CSV de forecaste_by_day ##### 
    # forecast_by_day = pd.read_csv('forecast_by_day.csv', parse_dates=['date'])
    forecast_by_day['date'] = forecast_by_day['date'].astype('datetime64[ns]')
    dates = forecast_by_day['date'].dt.date.unique()
    forecast_by_day['week'] = forecast_by_day['date'].dt.isocalendar().week
    forecast_by_day['day'] = forecast_by_day['date'].dt.isocalendar().day
    forecast_by_day['Forecast']=forecast_by_day['demanda']


    k1= 1
    k2 = 2
    W_real = 9

    max_wf_wk = forecast_by_day.query('day==7 or day==6')['Forecast'].max()
    b1 = ceil((k2 * max_wf_wk) / (k2-k1))
    D_week=0
    for w in forecast_by_day['week'].unique():
        d = forecast_by_day[forecast_by_day['week']==w]['Forecast'].to_list()
        D=0
        for i in d:
            D += i
        if D > D_week:
            D_week = D
    b2 = ceil(D/5)
    b3 = forecast_by_day['Forecast'].max()

    W = max(b1,b2,b3)
    print(f"Minimum workforce: {W}")
    if W_real > W:
        print("Workforce is enough, surplus: ", W_real-W)
        free_wf_wk = ceil(W_real*k1/k2)
    else:
        print("Workforce is not enough, deficit: ", W-W_real)
        free_wf_wk = ceil(W_real*k1/k2)

    print(f"Workforce free by Weekend: {free_wf_wk}")
    max_demanda_per_weekend = {w:forecast_by_day[forecast_by_day['week']==w].query('day==7 or day==6')['Forecast'].max() for w in forecast_by_day['week'].unique()}
    forecast_by_day['surplus'] = forecast_by_day.apply(lambda row: W_real - row['Forecast'] if row['day'] not in [6, 7] else W_real - max_demanda_per_weekend[row['week']], axis=1)
    max_dda_wk = forecast_by_day[(forecast_by_day['day']==7) | (forecast_by_day['day']==6)]['Forecast'].max()

    # Caso 1:2
    collab_list = [i for i in range(W_real)]
    collab_list_wknd = [collab_list[:int(len(collab_list)/2)], collab_list[int(len(collab_list)/2):]]
    collab_list_wknd = collab_list_wknd*2

    free_wknd_collab = {}
    for w, cs in zip(max_demanda_per_weekend, collab_list_wknd):
        free_wknd_collab[w] = cs


    data = []
    for c in collab_list:
        for fecha in dates:
            data.append([c, fecha])

    df_availability = pd.DataFrame(data, columns=['collaborator', 'date'])
    df_availability['availability'] = 1
    df_availability['date'] = df_availability['date'].astype('datetime64[ns]')
    df_availability['week'] = df_availability['date'].dt.isocalendar().week
    df_availability['day'] = df_availability['date'].dt.isocalendar().day

    for w in free_wknd_collab: # Dar domingo libres
        for c in free_wknd_collab[w]:
            filtro = (df_availability["collaborator"] == c) & (df_availability["day"] == 7) & (df_availability["week"] == w)
            df_availability.loc[filtro, "availability"] = 0

    day_off_by_week = {}
    for wk in  free_wknd_collab: # Pares días libres
        surplus_week = forecast_by_day[(forecast_by_day['week']==wk) & (forecast_by_day['day']!=7)][['day','surplus']].set_index('day').to_dict()['surplus']
        day_off_pairs = []
        for j in range(len(collab_list) - len(free_wknd_collab[wk])):
            keys = two_highest_keyvalue(surplus_week)
            surplus_week[keys[0]] -= 1
            surplus_week[keys[1]] -= 1
            day_off_pairs.append(keys)

        day_off_by_week[wk] = day_off_pairs

    for wk in day_off_by_week: # Dar libres entre semana
        j = 0
        for c in collab_list:
            if df_availability[(df_availability['collaborator']==c) & (df_availability['week']==wk)]['availability'].sum() == 7:
                days_off = day_off_by_week[wk][j]
                filter1 = (df_availability['collaborator']==c) & (df_availability['week']==wk) & (df_availability['day']==days_off[0])
                filter2 = (df_availability['collaborator']==c) & (df_availability['week']==wk) & (df_availability['day']==days_off[1])
                df_availability.loc[filter1, "availability"] = 0
                df_availability.loc[filter2, "availability"] = 0
                j+=1
                
    ##### Realiza la inserión de la información obtenida en la tabla 'availability' #####
    df_availability.to_sql(name='availability', con=engine, if_exists='replace', index=False)
    return "Inserted"