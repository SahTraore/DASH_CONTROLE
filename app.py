from app_config import is_localhost,local_conn_params,remote_conn_params
from  sql_requete_function import  *

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

				html.Div(dcc.Graph(id='profile_scraped_graph')),

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



	html.Div([
		html.Div([
			# figure resum
			html.H2("Résumer de l'extraction", style={'textAlign': 'center'}),

			html.Div(dcc.Graph(id='by_origine_graph')),


		]
		),

	],className='row')




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
		sql='''SELECT username FROM scraping_linkedin_scraped_profiles where is_scraped=True'''
		data_scraped=get_pandas_table(sql,**conn_params)
		total_load_nb=len(data_scraped)
		sql='''SELECT * FROM scraping_linkedin_company'''
		company_scraped=get_pandas_table(sql,**conn_params)
		total_load_comp=len(company_scraped)

		return ['{} profils extraits'.format(repr(total_load_nb)),'{} compagnies extraites'.format(repr(total_load_comp))]

	return ['{} profils extraits'.format('...'),'{} compagnies extraites'.format('...')]



@app.callback(
    dash.dependencies.Output('my-date-picker-range', 'end_date'), # This updates the field end_date in the DatePicker
    dash.dependencies.Input('submit-button','n_clicks'),
)
def update_endate(n_clicks):
	return date.today()



@app.callback(
	[dash.dependencies.Output('output-container-date-picker-range', 'children'),
     dash.dependencies.Output('profile_scraped_graph','figure')
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

        # result=show_exctraction_count_by_days(engine_text=postgres_str,
        #     from_date=from_date,color=style_all['backgroundColor'],**conn_params)
        result=show_exctraction_count_by_days(from_date=from_date,color=style_all['backgroundColor'],**conn_params)
 

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
        disp_connexion=get_pandas_table(sql1,**conn_params)
        disp_connexion.is_being_used=disp_connexion.is_being_used.replace({True:'true',False:'false'})
        # print(disp_connexion.is_being_used.dtypes)
        output1=get_available_connexion_text(disp_connexion)
        output2=get_available_connexion_data(disp_connexion)
        
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
        using_scraping=get_pandas_table(sql2,**conn_params)
        
        output1=get_scraping_being_used_text(using_scraping)
        output2=get_scraping_being_used_data(using_scraping)
        
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
        connexion_block=get_pandas_table(sql3,**conn_params)
        
        output1=get_blocked_connexion_text(connexion_block)
        output2=get_blocked_connexion_data(connexion_block)
        
        return [output1,output2]
    return [None,None]


@app.callback(dash.dependencies.Output('by_origine_graph','figure'),
              [dash.dependencies.Input('submit-button','n_clicks')])

def update_render_by_country(n_clicks):
    figure={}
    if n_clicks:
    	figure=show_exctraction_count_by_country(color=style_all['backgroundColor'],**conn_params)
        
    return figure


if __name__ == '__main__':
 	app.run_server(debug=True)