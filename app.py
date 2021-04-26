import os
import sql_requete_function
import dash
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objs as go
from datetime import date,timedelta,datetime
import re


postgres_str='postgresql://postgres:admin@localhost:5432/diasporaDataBase'


app_name = 'dash-postgresqldataplot'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Scraping_controle'


def get_data1(data):
    return  [dash_table.DataTable(
				id='table_connexion_disponible',
				columns=[{"name": i, "id": i} for i in data.columns],
				data=data.to_dict('records'),
				style_header={'backgroundColor': 'blue','color': 'white','font-weight': 'bold','textAlign': 'center'},
				page_size=10,  # we have less data in this example, so setting to 20
				# fixed_rows={'headers': True},
    			style_table={'height': '350px','overflowX': 'auto'},
				style_cell={
					'backgroundColor': 'powderblue',
					'color': 'Black','font-weight': 'bold'
				},

				style_data_conditional=[
				   
				    {
				        'if': {'filter_query': '{is_using} = 0'},
				        'backgroundColor': 'rgb(153, 255, 102)'
					},
					{
				        'if': {'filter_query': '{is_using} = 1'},
				        'backgroundColor': 'rgb(255, 51, 0)'
					}
				]
			)]

def get_resum1(data):
    text1="Tolal des possiblités : {} "
    text2="Connexions en cours : {} "
    text3="Connexions disponibles : {} "
    if len(data):
        poss=len(data)
        en_cours=len(data[data['is_using']==1])
        text1=text1.format(poss)
        text2=text2.format(en_cours)
        text3=text3.format(poss-en_cours)
        # text="Tolal des possiblités :{} | Connexions en cours : {} | Connexions disponibles : {}".format(poss,en_cours,dispo)

    return  html.Div([text1,html.P(text2),text3])



def get_data2(data):
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
						'backgroundColor': 'powderblue',
						'color': 'Black','font-weight': 'bold',
						'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
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

def get_resum2(data):
    text=""
    if len(data):
        text1="Nombre total de recherches : {}".format(len(data))
        res_dict=data.groupby('location_search')['controle_scraping_id'].count().to_dict()
        text2='Pays : ' +' | '.join([str(ele)+' = '+str(res_dict[ele]) for ele in set(res_dict)])
        return html.Div([text1,html.P(text2)])
    return text


def get_data3(data):
    return [dash_table.DataTable(
					id='table_connexion_block',
					columns=[{"name": i, "id": i} for i in data.columns],
					data=data.to_dict('records'),
					style_header={'backgroundColor': 'blue','color': 'white','font-weight': 'bold','textAlign': 'center'},
					page_size=10,
					style_cell={
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
def get_resum3(data):
    text=""
    if len(data):
        text="Nombre total de connexions blocquées : {}".format(len(data))
    else:  
        text="Nombre total de connexions blocquées : {}".format(0)
    return text



style_all={
	'backgroundColor':'#caefff'
}


app.layout =html.Div([ 


	html.Div([
    	html.Div([
       		html.Button(id='submit-button', children='Submit',
       			style={'color': 'Black','backgroundColor':"#309ce7 ",'width':'300px'})

        ],className='six columns'),

        html.Div(id='total_load',className='six columns',style={'color': 'Black','font-weight': 'bold','textAlign': 'center'})

    ],className='row container'),

	html.Div([
		html.Div([
			html.Div([

				html.H2("Scraping Controle", style={'textAlign': 'center'}),
				html.Div([
				dcc.DatePickerRange(
					id='my-date-picker-range',
					min_date_allowed=date(2020,8,1),
					max_date_allowed=date.today()+timedelta(days=2),
					initial_visible_month=date.today(),
					end_date=date.today(),
					start_date=date.today()-timedelta(days=14)

				)],style={'backgroundColor':style_all['backgroundColor'],"marginLeft": "25px"}),

				html.Div(id='output-container-date-picker-range',style={'color': 'Black','font-weight': 'bold',"marginLeft": "25px"}),

				html.Div(dcc.Graph(id='example-graph')),

			],className='six columns'),
		]),

		html.Div([
            
			# table 1
			html.H2("Possibilité(s) de Connexions", style={'textAlign': 'center'}),
			html.Div(style={"height": 25}),
			html.Div(id='resum1', style={'color': 'Black','font-weight': 'bold',"marginLeft": "25px"}),
			html.Div(style={"height": 25}),
			html.Div(id='data1',className='container'),

			# html.Div([
			# 	html.Div([
			# 			daq.NumericInput(id='numeric_input_connexion',value=0,size=100)

			#         ],style={'width' : '33% ','display': 'inline-block'}),

			# 	html.Div([
			# 		html.Button(id='valid_update_connexion', children="fermer l'utilisation",
			# 			style={'color': 'Black','backgroundColor':"green",'width':'300px','font-weight': '900','color': 'Black'})

			# 	],style={'width' : '33% ','display': 'inline-block'}),

			# 	html.Div([
			# 		html.Div(id='numeric_output_connexion')
			# 	],className='row'),
	
			# ],className='row')

		],className='six columns'),

	],className='row'),

	# html.Div(style={"height": 100}),

	html.Div([

		html.Div([
			# table 2
			html.H2("Recherches en cours", style={'textAlign': 'center'}),
			html.Div(id='resum2', style={'color': 'Black','font-weight': 'bold',"marginLeft": "25px"}),

			html.Div(id='data2',className='container'),

			# html.Div([
			# 	html.Div([
			# 			daq.NumericInput(id='numeric_input_scraping',value=0,size=100)

			#         ],style={'width' : '33% ','display': 'inline-block'}),

			# 	html.Div([
			# 		html.Button(id='valid_update_scraping', children='Fermer la recherche en cours',
			# 			style={'color': 'Black','backgroundColor':"#309ce7 ",'font-weight': 'bold','width':'300px'})

			# 	],style={'width' : '33% ','display': 'inline-block'}),

			# 	html.Div([
			# 		html.Div(id='numeric_output_scraping')
			# 	],className='row'),
	
			# ],className='row')



		],className='six columns',
		# style={"marginLeft": "25px","marginRight": "25px"}
		),

		html.Div([

			# table 3
			html.H2("Connexions Blocquées", style={'textAlign': 'center'}),
			html.Div(id='resum3', style={'color': 'Black','font-weight': 'bold',"marginLeft": "25px"}),
			# html.Div(style={"height": 25}),

			html.Div(id='data3',className='container'),
			# html.Div([
			# 	html.Div([
			# 		html.Div([
			# 				daq.NumericInput(id='numeric_input_connexion_to_deblok',value=0,size=100)

			# 	        ],style={'width' : '33% ','display': 'inline-block'}),

			# 		html.Div([
			# 			html.Button(id='valid_update_connexion_to_deblok', children='Lancer la connexion',
			# 				style={'backgroundColor':"green",'width':'250px','font-weight': '900','color': 'Black'})

			# 		],style={'width' : '33% ','display': 'inline-block'}),

			# 		# html.Div([
			# 		# 	html.Div(id='numeric_output_connexion_to_deblok')
			# 		# ],className='row'),
		
			# 	],className='row'),

			# 	html.Div([
			# 		html.Div([
			# 				daq.NumericInput(id='numeric_input_connexion_deblok',value=0,size=100)

			# 	        ],style={'width' : '33% ','display': 'inline-block'}),

			# 		html.Div([
			# 			html.Button(id='valid_update_connexion_deblok', children='Débloquer la connexion',
			# 				style={'color': 'Black','backgroundColor':"#309ce7 ",'font-weight': 'bold','width':'250px'})

			# 		],style={'width' : '50% ','display': 'inline-block'}),

			# 		html.Div([
			# 			html.Div(id='numeric_output_connexion_deblok')
			# 		],className='row')
			# 	],className='row')

			#])
		],className='six columns',style={"marginLeft": "25px"}),



	],className='row'),



],
className='container',
style={"marginBottom": "50px","marginTop": "25px",'backgroundColor':style_all['backgroundColor']}

)


#----------------callback functions


@app.callback(dash.dependencies.Output('total_load','children'),
              dash.dependencies.Input('submit-button','n_clicks'))

def update_total_load(n_clicks):
	if n_clicks:
		sql='''SELECT username FROM profil_scraped'''
		data_scraped=sql_requete_function.get_pandas_table(sql,postgres_str)
		total_load_nb=len(data_scraped)
		return str(total_load_nb)+' Profils extrait'

	return None


@app.callback(
	[dash.dependencies.Output('output-container-date-picker-range', 'children'),
     dash.dependencies.Output('example-graph','figure')
	],
	[dash.dependencies.Input('my-date-picker-range', 'start_date'),
	 dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('submit-button','n_clicks')])

def update_activity_graph(start_date,end_date,n_clicks):
    from_date=[]
    string_prefix='Vue sur les activités'
    if n_clicks or start_date or end_date:
        if start_date is not None:
            start_date_object = date.fromisoformat(start_date)
            start_date_string = start_date_object.strftime('%Y-%m-%d')
            from_date.append(start_date_string)

            start_date_string = start_date_object.strftime('%d %B %Y')
            string_prefix = string_prefix + ' du ' + start_date_string


        if end_date is not None:
            end_date_object = date.fromisoformat(end_date)
            end_date_string = end_date_object.strftime('%Y-%m-%d')
            from_date.append(end_date_string)
            end_date_string = end_date_object.strftime('%d %B %Y')
            string_prefix = string_prefix + ' au ' + end_date_string

        result=sql_requete_function.show_exctraction_count_by_days(engine_text=postgres_str,
            from_date=from_date,color=style_all['backgroundColor'])

        list_date=[datetime.strptime(ele,'%Y-%m-%d') for ele in  from_date]
        delta=list_date[1]-list_date[0]

        string_prefix = string_prefix +' | Total durant {during} jours : {total}'.format(during=delta.days,total=result[0])


        return string_prefix,result[1]



@app.callback([dash.dependencies.Output('resum1','children'),
               dash.dependencies.Output('data1','children')],
              [dash.dependencies.Input('submit-button','n_clicks')])

def update_render_tab1(n_clicks):
    if n_clicks:
        sql1='''
        SELECT controle_connexion_id,scraper_mail,is_using,statut,notification 
        FROM controle_connexion
        WHERE statut=0 '''
        disp_connexion=sql_requete_function.get_pandas_table(sql1,postgres_str)
        output1=get_resum1(disp_connexion)
        output2=get_data1(disp_connexion)
        
        return [output1,output2]
    return [None,None]



@app.callback([dash.dependencies.Output('resum2','children'),
               dash.dependencies.Output('data2','children')],
              [dash.dependencies.Input('submit-button','n_clicks')])

def update_render_tab2(n_clicks):
    
    if n_clicks:
        sql2='''
        SELECT controle_scraping_id,location_search,name_search,connexion_using_id,total_search,error_in_page,date
        FROM controle_scraping
        WHERE is_using={is_using}
        '''.format(is_using=1)
        using_scraping=sql_requete_function.get_pandas_table(sql2,postgres_str)
        
        output1=get_resum2(using_scraping)
        output2=get_data2(using_scraping)
        
        return [output1,output2]
    return [None,None]


@app.callback([dash.dependencies.Output('resum3','children'),
               dash.dependencies.Output('data3','children')],
              [dash.dependencies.Input('submit-button','n_clicks')])

def update_render_tab3(n_clicks):
    
    if n_clicks:
        sql3='''
        SELECT controle_connexion_id,scraper_mail,is_using,statut,notification 
        FROM controle_connexion
        WHERE statut=1 '''
        connexion_block=sql_requete_function.get_pandas_table(sql3,postgres_str)
        
        output1=get_resum3(connexion_block)
        output2=get_data3(connexion_block)
        
        return [output1,output2]
    return [None,None]

# @app.callback(dash.dependencies.Output('numeric_output_connexion_to_deblok','children'),
#               dash.dependencies.Input('valid_update_connexion_to_deblok','n_clicks'),
#               dash.dependencies.Input('numeric_input_connexion_to_deblok','value'))

# def update_lancement_connexion(n_clicks,value):

# 	if n_clicks :
# 		if value!=0:
# 			return "la connexion {} est lancer".format(value)
# 		else:
# 			return "L'id {} de la connexion  est introuvable".format(value)

# 	return ""




if __name__ == '__main__':
    app.run_server(debug=True)