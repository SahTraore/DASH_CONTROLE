import os
import sql_requete_function
import dash
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from datetime import date,timedelta,datetime
import re
from app_config import is_localhost,local_conn_params,remote_conn_params


#
conn_params=None
if is_localhost==True:
	conn_params=local_conn_params
else:
	conn_params=remote_conn_params





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
					# # 	'filter_query': '{is_being_used}=True',
				 # #        },
				 # #        'backgroundColor': 'rgb(255, 51, 0)'
					# # }
				]
			)]

def get_resum1(data):
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
        res_dict=data.groupby('residence_name')['controle_scraping_id'].count().to_dict()
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

#------------------------------------------------------------------------------
app.layout =html.Div([ 


	html.Div([
    	html.Div([
       		html.Button(id='submit-button', children='Submit',
       			style={'color': 'Black','backgroundColor':"#309ce7 ",'width':'300px'})

        ],className='six columns'),

        html.Div(id='total_load',className='six columns',style={'color': 'Black','font-weight': 'bold','textAlign': 'center'}),
        html.Div(id='total_load_company',className='six columns',style={'color': 'Black','font-weight': 'bold','textAlign': 'center'}),
        html.Div([
        	dcc.ConfirmDialog(
        		id='confirm-new-launch',
        		message='Voulez-vous lancer une nouvelle instance?',
			    ),
        	html.Button(id='launch_new_scraping',children='Nouvelle instance',n_clicks=0)

        	],className='six columns')


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
			html.Div(id='data1',className='container')

		],className='six columns'),

	],className='row'),

	# html.Div(style={"height": 100}),

	html.Div([

		html.Div([
			# table 2
			html.H2("Recherches en cours", style={'textAlign': 'center'}),
			html.Div(id='resum2', style={'color': 'Black','font-weight': 'bold',"marginLeft": "25px"}),

			html.Div(id='data2',className='container'),


		],className='six columns',
		# style={"marginLeft": "25px","marginRight": "25px"}
		),

		html.Div([

			# table 3
			html.H2("Connexions Blocquées", style={'textAlign': 'center'}),
			html.Div(id='resum3', style={'color': 'Black','font-weight': 'bold',"marginLeft": "25px"}),
			# html.Div(style={"height": 25}),

			html.Div(id='data3',className='container'),
		
		],className='six columns',style={"marginLeft": "25px"}),



	],className='row'),



],
className='container',
style={"marginBottom": "50px","marginTop": "25px",'backgroundColor':style_all['backgroundColor']}

)


#----------------callback functions

@app.callback(dash.dependencies.Output('confirm-new-launch', 'displayed'),
              dash.dependencies.Input('launch_new_scraping', 'n_clicks'))

def display_confirmation(n_clicks):
	if n_clicks:
		return True
	return False




@app.callback([dash.dependencies.Output('total_load','children'),
	dash.dependencies.Output('total_load_company','children')],
              dash.dependencies.Input('submit-button','n_clicks'))

def update_total_load(n_clicks):
	if n_clicks:
		sql='''SELECT username FROM scraping_linkedin_scraped_profiles'''
		data_scraped=sql_requete_function.get_pandas_table(sql,**conn_params)
		total_load_nb=len(data_scraped)
		sql='''SELECT * FROM scraping_linkedin_company'''
		company_scraped=sql_requete_function.get_pandas_table(sql,**conn_params)
		total_load_comp=len(company_scraped)

		return [str(total_load_nb)+' profils extraits',str(total_load_comp)+' compagnies extraites']

	return [None,None]


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

        # result=sql_requete_function.show_exctraction_count_by_days(engine_text=postgres_str,
        #     from_date=from_date,color=style_all['backgroundColor'],**conn_params)
        result=sql_requete_function.show_exctraction_count_by_days(from_date=from_date,color=style_all['backgroundColor'],**conn_params)
 

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
        SELECT controle_connexion_id,scraper_mail,is_being_used,status,notification,ip_adress,port
        FROM scraping_linkedin_bot
        WHERE status='usable' '''
        disp_connexion=sql_requete_function.get_pandas_table(sql1,**conn_params)
        disp_connexion.is_being_used=disp_connexion.is_being_used.replace({True:'true',False:'false'})
        # print(disp_connexion.is_being_used.dtypes)
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
        SELECT res1.controle_scraping_id,res1.bot_being_used_id,res1.name_fr as residence_name ,surnames.origine_name,res1.total_search
        From ( SELECT *
         From (SELECT * FROM scraping_linkedin_scraping) scraping 
         left join scraping_linkedin_country country
         on scraping.residence_search_id=country.controle_country_id) res1 left join scraping_linkedin_names surnames
         on res1.name_search_id=surnames.controle_name_id
        WHERE res1.is_being_used={is_being_used}
        '''.format(is_being_used=True)
        using_scraping=sql_requete_function.get_pandas_table(sql2,**conn_params)
        
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
        SELECT controle_connexion_id,scraper_mail,is_being_used,status,notification 
        FROM scraping_linkedin_bot
        WHERE status='blocked' '''
        connexion_block=sql_requete_function.get_pandas_table(sql3,**conn_params)
        
        output1=get_resum3(connexion_block)
        output2=get_data3(connexion_block)
        
        return [output1,output2]
    return [None,None]





if __name__ == '__main__':
    app.run_server(debug=True)