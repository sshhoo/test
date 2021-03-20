# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from PIL import Image
import imghdr
import base64
from io import BytesIO

import dash
from dash.dependencies import Input,Output,State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate

# ~ print('data/')
# ~ print('rank.npy')

file_list = []
label_list = []
character_list = []
current_label=None
font_type_dict={}
font_type_list=[]
font_type_list_count_dict={}
only_font_name_list=[]
single_font_name_list=[]

for (dir,subs,files) in os.walk('data/'):
	for file in files:
		target=os.path.join(dir,file)
		if os.path.isfile(target):
			if imghdr.what(target)!=None:
				file_list.append(target)
				if os.path.basename(os.path.dirname(target))!=current_label:
					current_label=os.path.basename(os.path.dirname(target))
					label_list.append(os.path.basename(os.path.dirname(target)))
				if len(label_list)<2:
					character_list.append(os.path.splitext(os.path.basename(target))[0].split('_')[1])
				
file_list.sort()
label_list.sort()
character_list.sort()

for i in range(len(label_list)):
	if current_label!=label_list[i].split('-')[0]:
		c=0
		current_label=label_list[i].split('-')[0]
		font_type_list_count_dict[current_label]=0
	font_type_list_count_dict[current_label]+=1
	if len(label_list[i].split('-'))>1:
		if c==0:
			font_type_dict[current_label]=[label_list[i].split('-')[1]]
			c=1
		else:
			font_type_dict[current_label].append(label_list[i].split('-')[1])
		if not label_list[i].split('-')[1] in font_type_list:
			font_type_list.append(label_list[i].split('-')[1])
	else:
		single_font_name_list.append(label_list[i])

only_font_name_list=list(font_type_list_count_dict.keys())


# ~ print(len(only_font_name_list))
# ~ print(len(single_font_name_list))

# ~ print('single check')
for i in range(len(single_font_name_list)):
	if not single_font_name_list[i] in only_font_name_list:
		print(i)
		print(single_font_name_list[i])
# ~ print('check over')

current_result_nd=np.load('rank.npy')
# ~ print(current_result_nd)
current_result_df=pd.DataFrame(current_result_nd).rank()
# ~ print(current_result_df)

def numpy_to_b64(array):
	im_pil = Image.fromarray(array)
	buff = BytesIO()
	im_pil.save(buff, format="png")
	im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
	return im_b64

app = dash.Dash(__name__)

server=app.server

app.layout = html.Div([
	html.A(html.Div('What fonts are similar?',style={'fontSize':30}),href='https://fontcomparisonsystem.herokuapp.com/'),
	html.Br(),
	html.Div('Select Font',style={'fontSize':20}),
	dcc.Dropdown(
		id='labels',
		options=[
			{ 'label': x,'value': x} for x in label_list
		],multi=True,value=[]
	),
	html.Div(id='output-labels',children='labels'),
	html.Br(),
	html.Div('Input Character 0〜9',style={'fontSize':20}),
	html.Div(dcc.Input(id='input-box',type='text')),
	html.Br(),
	html.Div('Display Number',style={'fontSize':20}),
	html.Div(dcc.Input(id='display-box',type='number',value='10')),
	html.Button('Generate Images',id='images-button'),
	html.Div(id='output-container-images'),
])

#labels_number
@app.callback(
	Output('output-labels', 'children'),
	[Input('labels', 'value')])
def update_output_methods(value):
	now_labels=value
	labels_number=len(now_labels)
	return f'Labels:{labels_number}'

#image_generate
generate_count=0
@app.callback(
	Output('output-container-images', 'children'),
	[Input('labels','value'),
	Input('input-box', 'value'),
	Input('display-box','value'),
	Input('images-button', 'n_clicks')])
def path_to_images(compare_labels,input_text,display_number,n_clicks):
	global generate_count
	global current_result_df
	global label_list
	global character_list
	if n_clicks==None:
		raise PreventUpdate
	if generate_count<n_clicks:
		generate_count+=1
		# ~ print(compare_labels)
		# ~ print(input_text)
		# ~ print(display_number)
		# ~ print(n_clicks)
		# ~ print(generate_count)
		temp_df=[]
		ret_list=[]
		flag=''
		display_number=int(display_number)
		if input_text==None:
			return html.Div('Input text, please.',style={'fontSize':20}),
		elif len(list(input_text))==0:
			return html.Div('Input text, please.',style={'fontSize':20}),
		else:
			input_char=list(input_text)
			# ~ print(input_char)
			for h in range(len(input_char)):
				if not input_char[h] in character_list:
					flag='ex_char'
			if flag=='ex_char':
				return html.Div('Input 0〜9, please.',style={'fontSize':20}),
			if len(compare_labels)==0:
				return html.Div('Select font, please.',style={'fontSize':20}),
			else:
				for i in range(len(compare_labels)):
					for j in range(len(input_char)):
						image_temp=Image.open('data/'+f'{compare_labels[i]}/{compare_labels[i]}_{input_char[j]}.png')
						if image_temp.mode!="L":
							image=image_temp.convert("L")
						else:
							image=image_temp
						img=np.array(image)
						if j==0:
							con_img=img
						else:
							con_img=np.hstack((con_img,img))
					ret_list.append(html.Div(f'target{i+1}\'s name :',style={'fontSize':20}),)
					font_name_char_list=list(compare_labels[i].split('-')[0])
					for k in range(len(font_name_char_list)):
						if k==0:
							temp_name=font_name_char_list[k]
							continue
						else:
							if font_name_char_list[k].isupper():
								if not font_name_char_list[k-1].isupper():
									temp_name+='+'
							temp_name+=font_name_char_list[k]
					ret_list.append(html.A(html.Div(f'{compare_labels[i]}',style={'fontSize':20}),href=f'https://fonts.google.com/specimen/{temp_name}'),)
					# ~ print(f'target{i+1}\'s name : {compare_labels[i]} ok')
					ret_list.append(html.Img(src='data:image/png;base64, ' + numpy_to_b64(con_img),style={'height': 'auto','display': 'block','margin': 'auto'}),)
					if i==0:
						temp_df=pd.DataFrame(current_result_df.iloc[:,label_list.index(compare_labels[i])])
					else:
						temp_df+=pd.DataFrame(current_result_df.iloc[:,label_list.index(compare_labels[i])]).values
				temp_df/=len(compare_labels)
				temp_df=temp_df.rank()
				# ~ print(temp_df)
				temp_df.sort_values(temp_df.columns.values[0],inplace=True)
				# ~ print(temp_df)
				font_index_list=temp_df.index.values
				# ~ print(font_index_list)
								
				count=0
				font_count=0
				for i in range(display_number):
					for j in range(len(input_char)):
						image_temp=Image.open('data/'+f'{label_list[font_index_list[i]]}/{label_list[font_index_list[i]]}_{input_char[j]}.png')
						if image_temp.mode!="L":
							image=image_temp.convert("L")
						else:
							image=image_temp
						img=np.array(image)
						if j==0:
							con_img=img
						else:
							con_img=np.hstack((con_img,img))
					ret_list.append(html.Div('Font\'s name :',style={'fontSize':20}),)
					font_name_char_list=list(label_list[font_index_list[i]].split('-')[0])
					for k in range(len(font_name_char_list)):
						if k==0:
							temp_name=font_name_char_list[k]
							continue
						else:
							if font_name_char_list[k].isupper():
								if not font_name_char_list[k-1].isupper():
									temp_name+='+'
							temp_name+=font_name_char_list[k]
					ret_list.append(html.A(html.Div(f'{label_list[font_index_list[i]]}',style={'fontSize':20}),href=f'https://fonts.google.com/specimen/{temp_name}'),)
					# ~ print(f'Font\'s name : {label_list[font_index_list[i]]} ok')
					ret_list.append(html.Img(src='data:image/png;base64, ' + numpy_to_b64(con_img),style={'height': 'auto','display': 'block','margin': 'auto'}),)
				ret_div=html.Div(ret_list),
				return ret_div
	elif n_clicks==1:
		generate_count=n_clicks-1

if __name__ == '__main__':
	app.run_server(debug=True)
