import warnings
import pandas as pd
import calendar
import pydata_google_auth
import matplotlib.pyplot as plt
from google.cloud import bigquery

credentials = pydata_google_auth.get_user_credentials(
    ['https://www.googleapis.com/auth/bigquery'],
)

def print_shape(df):
    print(df.shape)

def get_cilent():
    credentials = pydata_google_auth.get_user_credentials(
    ['https://www.googleapis.com/auth/bigquery'],
    )
    client = bigquery.Client(credentials=credentials, project='ps-data-analytics-platform')
    return client

def get_sql(sql_path: str='sql/contract.sql'):
    with open (sql_path, 'r') as sql:
        sql = sql.read()
    return sql

def to_datetime(df: pd.DataFrame, col: str=None):
    if not col:
        col = 'delete_date'
    df[col] = pd.to_datetime(df[col], errors='coerce')
    df = df.dropna(subset=col)
    df = df.sort_values(by=col, ascending=False).reset_index(drop=True)
    return df

def get_df(sql, client):
    df = client.query(sql).to_dataframe()
    return df

def extract_yyyy(df, datetime_col: str='delete_date'):
    df['year'] = df[datetime_col].dt.year
    return df

def extract_mm(df, datetime_col: str='delete_date'):
    df['month'] = df[datetime_col].dt.month
    return df

def extract_dd(df, datetime_col: str='delete_date'):
    df['day'] = df[datetime_col].dt.day
    return df

def extract_dayofweek(df, datetime_col: str='delete_date'):
    df['dayofweek'] = df[datetime_col].dt.day_of_week.apply(lambda dayofweek: calendar.day_name[dayofweek])
    df['dayofweek'] = df[datetime_col].dt.day_of_week.astype(str) + '.' +df['dayofweek']
    return df

def get_data(sql_path: str='sql/first_pub.sql'):
    client = get_cilent()
    sql = get_sql(sql_path=sql_path)
    df = get_df(sql, client)
    return df

def get_preprocessing_data(sql_path: str='sql/first_pub.sql', col: str= 'mindate'):
    df = get_data(sql_path=sql_path)
    
    df = to_datetime(df, col=col)
    df = extract_yyyy(df,datetime_col=col)
    df = extract_mm(df,datetime_col=col)
    df = extract_dd(df,datetime_col=col)
    df = extract_dayofweek(df,datetime_col=col)
    return df

def get_preprocessing_data2():
    df = get_data('sql/stock_cars.sql')
    df = df[df.price != 999999999]
    #初回掲載日時
    first_pub = get_preprocessing_data(sql_path='sql/first_pub.sql',col='min_date')
    start_day_dict = first_pub.set_index('stock_id')['min_date'].to_dict()
    #掲載落ち日時
    contract = get_preprocessing_data(sql_path='sql/contract.sql',col='delete_date')
    end_day_dict = contract.set_index('stock_id')['delete_date'].to_dict()
    #初回掲載掲載落ち日時
    df['end_day']=df.stock_id.map(end_day_dict)
    df['start_day']=df.stock_id.map(start_day_dict)
    df = df.dropna(subset=['start_day'])
    
    del start_day_dict, end_day_dict, first_pub, contract
    #見やすいように並び替え。いらない
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['stock_id', 'date'])

    #最大・最小価格
    df['min_price'] = df.groupby('stock_id')['price'].transform('min')
    df['max_price'] = df.groupby('stock_id')['price'].transform('max')
    
    #値下げがあるもの印
    df['diff_price'] = df['max_price'] - df['min_price']
    
    #stockid_に車種の紐づけ
    stock_optinos = get_data('sql/stock_cars_options.sql')
    stockid_car_dict = stock_optinos.set_index('stock_id')['n_p_car_nm_n'].to_dict()
    df['car_name'] = df['stock_id'].map(stockid_car_dict)
    
    df.reset_index(inplace=True, drop=True)
    
    # 乖離が大きものを消す
    df['display_end_date'] = df.groupby('stock_id').date.transform('max')
    df['end_day_diff'] = (df['end_day']-df['display_end_date']).astype('timedelta64[D]')

    print(df.shape)
    df = df[df.end_day_diff <= 14]
    print(df.shape)
    
    #掲載日時
    df.loc[:, 'keisaiday'] = (df['end_day']-df['start_day']).astype('timedelta64[D]').astype(int)
    
    #掲載の最大・最小日時
    df.loc[:, 'display_start_date'] = df.groupby('stock_id')['date'].transform(lambda x: min(x))
    df.loc[:, 'display_end_date'] = df.groupby('stock_id')['date'].transform(lambda x: max(x))
    
    df = df[['date', 'stock_id', 'price', 'end_day', 'display_end_date', 'start_day', \
         'display_start_date', 'min_price','max_price', 'diff_price', 'car_name', \
         'end_day_diff','keisaiday']]
    return df

def get_preprocessing_data3():
    df = get_data('sql/stock_cars2.sql')
    df = df[df.price != 999999999]
    #初回掲載日時
    first_pub = get_preprocessing_data(sql_path='sql/first_pub004.sql',col='mindate')
    start_day_dict = first_pub.set_index('stock_id')['mindate'].to_dict()
    #掲載落ち日時
    contract = get_preprocessing_data(sql_path='sql/contract2.sql',col='delete_date')
    end_day_dict = contract.set_index('stock_id')['delete_date'].to_dict()
    #初回掲載掲載落ち日時
    df['end_day']=df.stock_id.map(end_day_dict)
    df['start_day']=df.stock_id.map(start_day_dict)
    df = df.dropna(subset=['start_day'])
    
    del start_day_dict, end_day_dict, first_pub, contract
    #見やすいように並び替え。いらない
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['stock_id', 'date'])

    #最大・最小価格
    df['min_price'] = df.groupby('stock_id')['price'].transform('min')
    df['max_price'] = df.groupby('stock_id')['price'].transform('max')
    
    #値下げがあるもの印
    df['diff_price'] = df['max_price'] - df['min_price']
    
    #stockid_に車種の紐づけ
    # stock_optinos = get_data('sql/stock_cars_options.sql')
    # stockid_car_dict = stock_optinos.set_index('stock_id')['n_p_car_nm_n'].to_dict()
    # df['car_name'] = df['stock_id'].map(stockid_car_dict)
    
    df.reset_index(inplace=True, drop=True)
    
    # 乖離が大きものを消す
    df['display_end_date'] = df.groupby('stock_id').date.transform('max')
    df['end_day_diff'] = (df['end_day']-df['display_end_date']).astype('timedelta64[D]')

    print(df.shape)
    df = df[df.end_day_diff <= 14]
    print(df.shape)
    
    #掲載日時
    df.loc[:, 'keisaiday'] = (df['end_day']-df['start_day']).astype('timedelta64[D]').astype(int)
    
    #掲載の最大・最小日時
    df.loc[:, 'display_start_date'] = df.groupby('stock_id')['date'].transform(lambda x: min(x))
    df.loc[:, 'display_end_date'] = df.groupby('stock_id')['date'].transform(lambda x: max(x))
    
    df = df[['date', 'stock_id', 'price', 'end_day', 'display_end_date', 'start_day', \
         'display_start_date', 'min_price','max_price', 'diff_price', \
         'end_day_diff','keisaiday']]
    return df