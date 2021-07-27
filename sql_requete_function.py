from app_config import style_all
import dash
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html

import psycopg2
from sshtunnel import SSHTunnelForwarder

import plotly.graph_objs as go #https://www.tutorialspoint.com/plotly/
from plotly.offline import iplot #https://www.tutorialspoint.com/plotly/

from datetime import date,timedelta,datetime
import pandas as pd 
import os
import re



def get_available_connexion_data(data):
    return  [dash_table.DataTable(
                id='table_connexion_disponible',
                columns=[{"name": i, "id": i} for i in data.columns],
                data=data.to_dict('records'),
                style_header={'backgroundColor': 'blue','color': 'white','font-weight': 'bold','textAlign': 'center'},
                page_size=10,  # we have less data in this example, so setting to 20
                # fixed_rows={'headers': True},
                style_table={'height': '350px','overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'backgroundColor': 'powderblue',
                    'color': 'Black','font-weight': 'bold',
                                    },

                style_data_conditional=[
                   
                    {
                    'if': {
                        'filter_query': '{is_being_used}="false"',
                        },
                        'backgroundColor': 'rgb(153, 255, 102)'
                    },
                    {
                    'if': {
                        'filter_query': '{is_being_used}="true"',
                        },
                        'backgroundColor': 'rgb(255, 51, 0)'
                    }
                    # {
                    # # 'if': {
                    # #     'filter_query': '{is_being_used}=True',
                 # #        },
                 # #        'backgroundColor': 'rgb(255, 51, 0)'
                    # # }
                ]
            )]

def get_available_connexion_text(data):
    text1="Tolal des possiblités : {} "
    text2="Connexions en cours : {} "
    text3="Connexions disponibles : {} "
    if len(data):
        poss=len(data)
        en_cours=len(data[data['is_being_used']=="true"])
        text1=text1.format(poss)
        text2=text2.format(en_cours)
        text3=text3.format(poss-en_cours)
        # text="Tolal des possiblités :{} | Connexions en cours : {} | Connexions disponibles : {}".format(poss,en_cours,dispo)

    return  html.Div([text1,html.P(text2),text3])



def get_scraping_being_used_data(data):
    return [dash_table.DataTable(
                    id='table_scraping_being_used',
                    columns=[{"name": i, "id": i} for i in data.columns],
                    data=data.to_dict('records'),

                    style_header={

                        'backgroundColor': 'blue',
                        'color': 'white','font-weight':'bold',
                        'textAlign': 'center','overflow': 'hidden',
                    },
                    page_size=10,  # we have less data in this example, so setting to 20
                    # fixed_rows={'headers': True},
                    style_cell={
                        'textAlign': 'left',
                        'backgroundColor': 'powderblue',
                        'color': 'Black','font-weight': 'bold',
                        'whiteSpace': 'normal',
                        #'minWidth': '180px', 'width': '180px', 
                        #'maxWidth': '180px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': style_all['backgroundColor']
                        },
                    ],
                    style_table={'height': '350px','overflowX': 'auto'},

                )]

def get_scraping_being_used_text(data):
    text=""
    if len(data):
        text1="Nombre total de recherches : {}".format(len(data))
        res_dict=data.groupby('residence_name')['controle_scraping_id'].count().to_dict()
        text2='Pays : ' +' | '.join([str(ele)+' = '+str(res_dict[ele]) for ele in set(res_dict)])
        return html.Div([text1,html.P(text2)])
    return text


def get_blocked_connexion_data(data):
    return [dash_table.DataTable(
                    id='table_connexion_block',
                    columns=[{"name": i, "id": i} for i in data.columns],
                    data=data.to_dict('records'),
                    style_header={'backgroundColor': 'blue','color': 'white','font-weight': 'bold','textAlign': 'center'},
                    page_size=10,
                    style_cell={
                        'textAlign': 'left',
                        'backgroundColor': 'grey',
                        'color': 'white',
                        'font-weight': 'bold','height': 'auto',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'color': 'black',
                            'backgroundColor': style_all['backgroundColor'],
                        },
                    ],
                    style_table={'height': '350px','overflowX': 'auto'},

                )]

def get_blocked_connexion_text(data):
    text=""
    if len(data):
        text="Nombre total de connexions blocquées : {}".format(len(data))
    else:  
        text="Nombre total de connexions blocquées : {}".format(0)
    return text


def show_exctraction_count_by_days(ipaddress,db_name,db_user,db_port,db_password,ssh_port,remote_server_host,
    ssh_username,ssh_user_password,from_date=[],color='#c9c9c9'):
    sql=''
    data=[]
    if not from_date:
        sql='''
            SELECT TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') as foday, count(username)
            FROM scraping_linkedin_scraped_profiles 
            WHERE date!='' AND is_scraped=True
            group by foday
            order by foday'''
    else:
        from_date_sorted=sorted(from_date)
        if len(from_date_sorted)==1:
            from_date=from_date_sorted[0]
            sql='''
            SELECT TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') as foday, count(username)
            FROM scraping_linkedin_scraped_profiles 
            WHERE TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF')>={}  AND is_scraped=True
            group by foday
            order by foday'''.format(repr(from_date))
            
        if len(from_date_sorted)==2: 
            from_date_min=from_date_sorted[0]
            from_date_max=from_date_sorted[1]
            sql='''
            SELECT TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') as foday, count(username)
            FROM scraping_linkedin_scraped_profiles 
            WHERE TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') BETWEEN {} AND {}  AND is_scraped=True
            group by foday
            order by foday'''.format(repr(from_date_min),repr(from_date_max))
    try:
        data=get_pandas_table(sql,ipaddress,db_name,db_user,db_port,db_password,ssh_port,remote_server_host,ssh_username,ssh_user_password)
    except Exception as e:
        print(e)
        # print('Error in import data\nSQL_request={}\nConnexion_engine{}'.format(sql,engine_text))

    names=data['foday']
    valeurs=data['count']
    total=sum(valeurs)

    data = [go.Bar(
       x = names,
       y = valeurs
    )]

    layout = go.Layout(
        title = "Représentation de l'activité d'extraction des Profils ", 
        xaxis ={'title': "Date d'extraction"} , 
        yaxis ={'title':"Nombre d'url extrait"},
        paper_bgcolor= color)

    fig=go.Figure(data = data, layout = layout)
    
    return total,fig




def show_exctraction_count_by_country(ipaddress,db_name,db_user,db_port,db_password,ssh_port,remote_server_host,
    ssh_username,ssh_user_password,color='#c9c9c9'):

    sql="""select country_origine_name  as country_origine_name ,count(username) as nombre from profiles_search_view 
    group by country_origine_name"""
    data_res=pd.DataFrame({})

    try:
        data_res=get_pandas_table(sql,ipaddress,db_name,
                                  db_user,db_port,db_password,ssh_port,
                                  remote_server_host,ssh_username,ssh_user_password)
        if list(data_res.columns):
            data_res.country_origine_name.fillna('tunisie',inplace=True)
            data_res=data_res.groupby(['country_origine_name']).sum()
     
    except Exception as e:
        print('Error in data_res')
        print(e)
    

    names=data_res.index
    valeurs=data_res['nombre']
    total=sum(valeurs)

    data = [go.Bar(
       x = names,
       y = valeurs
    )]

    layout = go.Layout(
        title = "Représentation Par pays d'origine ", 
        xaxis ={'title': "Pays d'origine"} , 
        yaxis ={'title':"Nombre de profils extrait"},
        paper_bgcolor= color)

    fig=go.Figure(data = data, layout = layout)

    return fig




def get_pandas_table(sql,ipaddress,db_name,db_user,
                     db_port,db_password,ssh_port,remote_server_host,
                     ssh_username,ssh_user_password):
   
    data=[]
    if  remote_server_host!=None:
        try:
            with SSHTunnelForwarder((remote_server_host, ssh_port), ssh_password=ssh_user_password,
                                    ssh_username=ssh_username,
                                    remote_bind_address=(ipaddress, db_port)) as server:
                connexion = psycopg2.connect(dbname=db_name, user=db_user, 
                                             password=db_password, port=server.local_bind_port)
                data=pd.read_sql_query(sql,con=connexion)
        except Exception as e:
            print(e)
            print('Error in import data\nSQL_request={}'.format(sql))
    else:

        # engine_text = 'postgresql://{db_user}:{db_password}@{ipaddress}:{db_port}/{db_name}'.format(db_user=db_user,
        #     db_password=db_password,
        #     ipaddress=ipaddress,
        #     db_port=db_port,
        
        #     db_name=db_name)

        try:
            # connexion = create_engine(engine_text)
            connexion = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, port=db_port)
            data=pd.read_sql_query(sql,con=connexion)
        except Exception as e:
            print(e)
            rint('Error in import data\nSQL_request={}'.format(sql))



    return data