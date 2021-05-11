import pandas as pd 
from sqlalchemy import create_engine
import plotly.graph_objs as go #https://www.tutorialspoint.com/plotly/
from plotly.offline import iplot #https://www.tutorialspoint.com/plotly/
from datetime import datetime




def show_exctraction_count_by_days(engine_text,from_date=[],color='#c9c9c9'):
    sql=''
    data=[]
    if not from_date:
        sql='''
            SELECT TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') as foday, count(username)
            FROM scraping_linkedin_scraped_profiles 
            WHERE date!=''
            group by foday
            order by foday'''
    else:
        from_date_sorted=sorted(from_date)
        if len(from_date_sorted)==1:
            from_date=from_date_sorted[0]
            sql='''
            SELECT TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') as foday, count(username)
            FROM scraping_linkedin_scraped_profiles 
            WHERE TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF')>={}
            group by foday
            order by foday'''.format(repr(from_date))
            
        if len(from_date_sorted)==2: 
            from_date_min=from_date_sorted[0]
            from_date_max=from_date_sorted[1]
            sql='''
            SELECT TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') as foday, count(username)
            FROM scraping_linkedin_scraped_profiles 
            WHERE TO_DATE(date,'YYYY-MM-DDTHH:MI:SS.FF') BETWEEN {} AND {}
            group by foday
            order by foday'''.format(repr(from_date_min),repr(from_date_max))
    try:
        connexion = create_engine(engine_text)
        data=pd.read_sql_query(sql,con=connexion)
    except:
        print(e)
        print('Eroor in import data\nSQL_request={}\nConnexion_engine{}'.format(sql,engine_text))

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




def get_pandas_table(sql,engine_text):
   
    data=[]
    try:
        connexion = create_engine(engine_text)
        data=pd.read_sql_query(sql,con=connexion)
    except Exception as e:
        print(e)
        print('Error in import data\nSQL_request={}\nConnexion_engine{}'.format(sql,engine_text))
    return data