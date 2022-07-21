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

def get_preprocessing_data(sql_path: str='sql/first_pub.sql', col: str= 'min_date'):
    df = get_data(sql_path=sql_path)
    
    df = to_datetime(df, col=col)
    df = extract_yyyy(df,datetime_col=col)
    df = extract_mm(df,datetime_col=col)
    df = extract_dd(df,datetime_col=col)
    df = extract_dayofweek(df,datetime_col=col)
    return df