from collections import defaultdict
from flask import Flask, render_template, request, redirect
from flask import Flask

from flask_cors  import CORS
from numpy import add

import requests

import pandas as pd
import geopandas as gpd

from io import StringIO
from keplergl import KeplerGl

from shapely.geometry import shape
from random import randint


from functools import lru_cache
import json
import geocoder
import mercantile
from dataclasses import dataclass


############################
# import for folium

import folium
import json

import numpy as np
import vincent


##############################

from utils import MapData, load_new_appeal_by_df

regions = [['Алтайский край', 52.129671, 82.530022],
 ['Амурская область', 53.413346, 127.728073],
 ['Архангельская область', 63.637521, 43.33667],
 ['Астраханская область', 46.851463, 47.466198],
 ['Белгородская область', 50.872237, 37.303207],
 ['Брянская область', 52.909198, 33.422206],
 ['Владимирская область', 55.9042, 40.898894],
 ['Волгоградская область', 49.615821, 44.151415],
 ['Вологодская область', 60.138993, 44.049627],
 ['Воронежская область', 50.970903, 40.233395],
 ['Еврейская автономная область', 48.522908, 132.257621],
 ['Забайкальский край', 52.847263, 116.200433],
 ['Ивановская область', 56.967841, 41.966406],
 ['Иркутская область', 57.100298, 106.363314],
 ['Калининградская область', 54.560096, 21.218944],
 ['Калужская область', 54.371805, 35.445194],
 ['Камчатский край', 61.350179, 169.782981],
 ['Кемеровская область', 54.897945, 86.990391],
 ['Кировская область', 58.344112, 49.695439],
 ['Костромская область', 58.456007, 43.788504],
 ['Краснодарский край', 45.54491, 39.610422],
 ['Красноярский край', 67.236783, 95.968486],
 ['Курганская область', 55.448352, 64.809405],
 ['Курская область', 51.535008, 36.121356],
 ['Ленинградская область', 59.337017, 29.608975],
 ['Липецкая область', 52.864473, 39.147637],
 ['Магаданская область', 62.575815, 154.036835],
 ['Москва', 55.75322, 37.622513],
 ['Московская область', 55.531132, 38.874756],
 ['Мурманская область', 68.004158, 35.01006],
 ['Ненецкий автономный округ', 67.714212, 54.365071],
 ['Нижегородская область', 56.595648, 44.279559],
 ['Новгородская область', 58.307715, 32.490222],
 ['Новосибирская область', 55.582396, 79.26487],
 ['Омская область', 56.103477, 73.344425],
 ['Оренбургская область', 52.743533, 53.498691],
 ['Орловская область', 52.78146, 36.481042],
 ['Пензенская область', 53.240932, 43.946823],
 ['Пермский край', 59.117698, 56.225679],
 ['Приморский край', 45.04198, 134.709375],
 ['Псковская область', 57.236486, 29.23692],
 ['Республика Башкортостан', 54.271505, 56.525537],
 ['Республика Бурятия', 54.544222, 112.348699],
 ['Республика Дагестан', 42.259793, 47.095751],
 ['Республика Ингушетия', 43.10359, 45.05459],
 ['Республика Калмыкия', 46.41403, 45.325701],
 ['Республика Карелия', 63.621328, 33.232608],
 ['Республика Коми', 64.125467, 54.789669],
 ['Республика Крым', 45.3892, 33.993751],
 ['Республика Марий Эл', 56.485739, 48.197867],
 ['Республика Мордовия', 54.205758, 44.319678],
 ['Республика Саха (Якутия)', 65.061073, 119.845661],
 ['Республика Тыва', 51.584332, 94.793085],
 ['Республика Хакасия', 53.386363, 89.897078],
 ['Ростовская область', 47.728738, 41.268137],
 ['Рязанская область', 54.55973, 40.950331],
 ['Самарская область', 53.452932, 50.34431],
 ['Санкт-Петербург', 59.938955, 30.315644],
 ['Саратовская область', 51.578529, 46.797223],
 ['Сахалинская область', 50.150926, 142.750806],
 ['Свердловская область', 58.58676, 61.530761],
 ['Севастополь', 44.556972, 33.526402],
 ['Смоленская область', 54.956198, 32.998552],
 ['Ставропольский край', 44.953551, 43.344521],
 ['Тамбовская область', 52.474699, 41.592258],
 ['Тверская область', 57.093033, 34.706204],
 ['Томская область', 58.740293, 81.950869],
 ['Тульская область', 53.888069, 37.575702],
 ['Тюменская область', 57.541821, 68.096053],
 ['Ульяновская область', 53.891062, 47.606533],
 ['Хабаровский край', 51.695886, 136.637043],
 ['Челябинская область', 54.446204, 60.39565],
 ['Чукотский автономный округ', 65.982613, 174.43232],
 ['Ямало-Ненецкий автономный округ', 67.808603, 75.199571],
 ['Ярославская область', 57.817361, 39.105138]]


imgs = pd.read_csv('img_id.csv')

import copy

dict_by_region = dict()

for key in imgs['region'].unique():

    t = imgs[imgs['region'] == key]
    
    dict_by_mnn = dict()
    
    for i in range(len(t)):
        dict_by_mnn[t.iloc[i]['mnn']] = t.iloc[i]['img_id']
    
    dict_by_region[key] = copy.deepcopy(dict_by_mnn)


regs = list(dict_by_region.keys())

mnns = sorted(list(imgs['mnn'].unique()))

print(mnns)

print("!!!!!!!!!!!!!!!!")


map_data = MapData()

ZOOM_LEVEL = 1

app = Flask(__name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)
cors = CORS(app)

def load_config():
    with open('map_config.json', 'r') as fd:
        return json.load(fd)

@app.get('/test')
def get_test_page():    
    return render_template('test_map.html')

@app.get('/regs')
def get_regs_page():    
    return render_template('with-regions.html')

@app.get('/dis')
def get_dis_page():    
    return render_template('with-districts.html')

@app.get('/map1')
def get_main_page():    
    return render_template('page.html')

@app.get('/reg')
def get_reg_page():    
    return render_template('regions.html')



@app.get('/')
def get_inter_page():

    map_data = f""
    
    for i in range(len(regions)):
        u = regions[i]
        
        x = str(u[1])
        y = str(u[2])
        
        if i % 10 == 0:
            map_data += f"DG.marker([{x},{y}]," + "{icon: redIcon, title : 'Красный маркер'})" + ".on('click', function() {clickedElement.innerHTML = '" + f"<b>{u[0]} - дефицит! 800 единиц </b><br>Cоседние регионы:<br>Новосибирская область - профицит 1000 единиц<br>Томская область - профицит 3300 единиц<br>Кемеровская область - профицит 6300<br>Республика Хакассия - профицит 2160" + "';}).addTo(map).bindLabel(" + f"'{u[0]}'," + " {static: false});"        
        else:
            map_data += f"DG.marker([{x},{y}]," + "{icon: greenIcon, title : 'Зелёный маркер'})" + ".on('click', function() {clickedElement.innerHTML = '" + f"инфа по  {u[0]}" + "';}).addTo(map).bindLabel(" + f"'{u[0]}'," + " {static: false});"          

    #print(map_data)
        
    return render_template('interactive.html', map_data=map_data, regs=regs)


@app.get('/region')
def get_region77_page():
    
    result = None
    
    reg = request.args.get('reg')  
    mnn = request.args.get('mnn')
    
    print(reg)
    print(mnn)
    
    if reg is not None:
        if reg in dict_by_region:
            t = dict_by_region[reg]
            if mnn in t:
                result = "<img style='width: 100%' src='/storage/" + t[mnn] + "' />"
            else:
                result = "Недостаточно данных для прогнозирования"
        else:
            result = "Недостаточно данных для прогнозирования"
     

    x = None
    y = None
    
    if reg is not None:
        for u in regions:
            if u[0] == reg:
                x = u[1]
                y = u[2]               
                       
            
    map_data = None
    
    
    if x is not None:
        map_data = "DG.marker(["+str(x)+","+str(y)+"]).on('click', function() {clickedElement.innerHTML = 'маркер';}).addTo(map);"
    
    for i in range(len(regions)):
        u = regions[i]
        
        x = str(u[1])
        y = str(u[2])
        
    #print(map_data)
    
    
    return render_template('interactive2.html', map_data=map_data, regs = regs, mnn = mnns, result = result, reg=reg)


@app.get('/fol')
def get_fol_page():
    scatter_points = {
        "x": np.random.uniform(size=(100,)),
        "y": np.random.uniform(size=(100,)),
    }
    
    # Let's create the vincent chart.
    scatter_chart = vincent.Scatter(scatter_points, iter_idx="x", width=600, height=300)
    
    # Let's convert it to JSON.
    scatter_json = scatter_chart.to_json()

    # Let's convert it to dict.
    scatter_dict = json.loads(scatter_json)
    m = folium.Map([43, -100], zoom_start=4)
    
    popup = folium.Popup()
    
    folium.Vega(scatter_chart, height=350, width=650).add_to(popup)
    folium.Marker([30, -120], popup=popup).add_to(m)
    
    # Let's create a Vega popup based on scatter_json.
    popup = folium.Popup(max_width=0)
    folium.Vega(scatter_json, height=350, width=650).add_to(popup)
    folium.Marker([30, -100], popup=popup).add_to(m)
    
    # Let's create a Vega popup based on scatter_dict.
    popup = folium.Popup(max_width=650)
    folium.Vega(scatter_dict, height=350, width=650).add_to(popup)
    folium.Marker([30, -80], popup=popup).add_to(m)
    
    return m._repr_html_()
    
@app.get('/fol1')
def get_fol_page1():
    url = ("https://raw.githubusercontent.com/python-visualization/folium/master/examples/data")
    vis1 = json.loads(requests.get(f"{url}/vis1.json").text)
    vis2 = json.loads(requests.get(f"{url}/vis2.json").text)
    vis3 = json.loads(requests.get(f"{url}/vis3.json").text)
        
    m = folium.Map(location=[46.3014, -123.7390], zoom_start=7, tiles="Stamen Terrain")
        
    folium.Marker(location=[47.3489, -124.708],popup=folium.Popup(max_width=450).add_child(folium.Vega(vis1, width=450,height=250)),).add_to(m)

    folium.Marker(
        location=[44.639, -124.5339],
        popup=folium.Popup(max_width=450).add_child(
            folium.Vega(vis2, width=450, height=250)
        ),
    ).add_to(m)

    folium.Marker(
        location=[46.216, -124.1280],
        popup=folium.Popup(max_width=450).add_child(
            folium.Vega(vis3, width=450, height=250)
        ),
    ).add_to(m)
    
    return m._repr_html_()    


@app.get('/fol2')
def get_fol2_page():
    m = folium.Map(location=[63.391522, 96.328125], zoom_start=3)
    
    rel_ = folium.Choropleth(
    geo_data = './admin_level_4.geojson', 
    name = 'Отношение числа филиалов с ЕБС ко всем',
    key_on='id',
    bins = 5,
    fill_color='YlGn',
    nan_fill_color='white',
    nan_fill_opacity=0.5,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name= 'Отношение числа филиалов с ЕБС ко всем',
    highlight = True,
    show = False
    )
    
    rel_.add_to(m)
    
    return m._repr_html_() 
    
@app.get('/map')
def get_map_data():
    gdf_by_quads = gpd.GeoDataFrame([
        {
            'id': f['id'],
            'title': f['properties']['title'],
            'geometry': shape(f['geometry']),
            **f['properties']
        }
        for f in map_data.get_tile_features()
    ])
    # gdf.set_crs(epsg=4326, inplace=True)

    geo = KeplerGl(height=1000, data={}, show_docs=False, config=load_config())

    if len(gdf_by_quads) > 0:
        geo.add_data(data=gdf_by_quads, name="appeals")

    if map_data.custom_geometry:
        geo.add_data(data=map_data.custom_geometry, name='custom')

    return geo._repr_html_(center_map=True)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
