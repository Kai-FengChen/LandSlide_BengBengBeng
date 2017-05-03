from flask import Flask, render_template, url_for, json, redirect, jsonify, request
import os
from bs4 import BeautifulSoup
import datetime
import time
import requests
from subprocess import call
app = Flask(__name__)

@app.route("/")
def main():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    
    json_url = os.path.join(SITE_ROOT, "static/data", "today.json")
    predict = json.load(open(json_url))

    json_url = os.path.join(SITE_ROOT, "static/data", "point.json")        
    history = json.load(open(json_url))
    history = {"features":history,"type":'FeatureCollection'}
    
    user_upload = requests.get('http://nasa.rails.nctu.me/catalogs/index.json').json()
    user_upload = {"features":user_upload,"type":'FeatureCollection'}
    
    json_url = os.path.join(SITE_ROOT, "static/data", "taiwan.json")
    taiwan = json.load(open(json_url))
    
    json_url = os.path.join(SITE_ROOT, "static/data", "rain.json")
    rain = json.load(open(json_url))

    return render_template('sample.html', history=history, predict=predict, taiwan=taiwan, rain=rain, user_upload=user_upload)

@app.route("/update")
def update():
    today = datetime.date.today().strftime("%Y-%m-%d")
    precip_req = "https://pmmpublisher.pps.eosdis.nasa.gov/opensearch?q=global_landslide_nowcast_30mn&limit=1&startTime=%s&endTime=%s" %(today,today)
    p = requests.get(precip_req)
    r = requests.get(p.json()['items'][0]['action'][0]['using'][0]['url'])
    soup = BeautifulSoup(r.content, 'html.parser')
    topjson = requests.get(soup.find_all('a')[1].get('href')).json()
    
    with open('top.json', 'w') as f:
        json.dump(topjson, f)
    
    geojson = os.popen("./node_modules/topojson-client/bin/topo2geo -l < top.json").read()[:-1]
    os.popen("./node_modules/topojson-client/bin/topo2geo %s.json < top.json" %geojson)
    os.popen("mv %s.json static/data/today.json" %geojson)

    with open('static/data/today.json') as f:
        data = json.load(f)

    for i in range(len(data['features'])):
        data['features'][i]['nowcast'] = data['features'][i]['properties']['nowcast']

    with open('static/data/today.json', 'w') as f:
        json.dump(data, f)
    
    return redirect('/')

@app.route("/rain")
def rain():
    feature = []
    for i in range(5):
        today = datetime.date.fromordinal(datetime.date.today().toordinal()-i-2).strftime("%Y-%m-%d")
        precip_req = "https://pmmpublisher.pps.eosdis.nasa.gov/opensearch?q=precip_1d&limit=1&startTime=%s&endTime=%s" %(today,today)
        p = requests.get(precip_req)
        topjson = requests.get(p.json()['items'][0]['action'][1]['using'][0]['url']).json()
        
        with open('top.json', 'w') as f:
            json.dump(topjson, f)
        
        geojson = os.popen("./node_modules/topojson-client/bin/topo2geo -l < top.json").read()[:-1]
        os.popen("./node_modules/topojson-client/bin/topo2geo %s.json < top.json" %geojson)
        time.sleep(2)
        print(i)
        with open('%s.json' %geojson) as f:
            data = json.load(f)
        for j in range(len(data['features'])):
            data['features'][j]['properties']['day_id'] = i
        feature = feature+data['features']
    #os.popen("mv %s.json static/data/today.json" %geojson)
    with open('static/data/rain.json', 'w') as f:
        json.dump({"features":feature,"type":'FeatureCollection'}, f)
    
    return redirect('/')

@app.route("/update_points")
def update_points():
    r = requests.get('http://nasa.rails.nctu.me/catalogs/all')
    point_list = []
    for i in range(len(r.json())):
        country = r.json()[i]['countryname']
        date = r.json()[i]['date']
        if r.json()[i]['trigger']:
            trigger = r.json()[i]['trigger']
        else:
            trigger = "Unkown"
        if r.json()[i]['injuries']:
            injur = r.json()[i]['injuries']
        else:
            injur = "Unknown"
        if r.json()[i]['landslide_size']:
            size = r.json()[i]['landslide_size']
        else:
            size = "Unknown"            
        if r.json()[i]['longitude'] and r.json()[i]['latitude']:
            point = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [r.json()[i]['longitude'], r.json()[i]['latitude']]
                },
                "properties": {
                        "description": "<center><h3>%s:%s</strong></h3></center><hr><ul><li>Triggered By: %s</li><li>Injuries: %s</li><li>Landslide Size: %s</li></ul><center><img src=\"http://www.weatherwizkids.com/wp-content/uploads/2015/04/landslide5.jpg\" align=\"middle\" height=\"300\" width=\"300\"></center>" %(country, date, trigger, injur, size)
                },
            }
            point_list.append(point)
    with open('static/data/point.json', 'w') as f:
        json.dump(point_list, f)
    return redirect('/')

@app.route("/taiwan")
def update_taiwan():
    r = requests.get("http://od.moi.gov.tw/api/v1/rest/datastore/301000000A-001029-006")
    j = r.json()
    d = {}
    for i in j['result']['records']:
        d[i['County'] + i['Town'] + i['Village']] = (i['X'], i['Y'])

    taiwan = requests.get('http://opendata.epa.gov.tw/ws/Data/SOIL00062/?$skip=0&$top=1000&format=json')
    taiwan_data = []
    for i in taiwan.json():
        name = i['County']+i['Town']+i['Vill']
        dd={}
        if name in d.keys():
            loc = d[name]
            dd['lon'] = float(loc[0])
            dd['lat'] = float(loc[1])
            dd['name'] = name
            dd['triger'] = i['DisasterName']
            dd['time'] = i['DisasterTime']
            taiwan_data.append(dd)
    with open('static/data/taiwan.json', 'w') as f:
        json.dump(taiwan_data, f)
    return redirect('/')

@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        r = request.get_json()
        with open('static/data/point.json') as f:
            data = json.load(f)
        country = r['countryname']
        date = r['date']
        photo = r['photos_link']
        print(photo)
        if r['trigger']:
            trigger = r['trigger']
        else:
            trigger = "Unkown"
        if r['injuries']:
            injur = r['injuries']
        else:
            injur = "Unknown"
        if r['landslide_size']:
            size = r['landslide_size']
        else:
            size = "Unknown"  
        if r['longitude'] and r['latitude']:
            image_url = url_for('static', filename='landslide_victory/public/uploads/%s' %photo)
            print(image_url)
            point = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [r['longitude'], r['latitude']]
                },
                "properties": {
                        "description": "<center><h3>%s:%s</strong></h3></center><hr><ul><li>Triggered By: %s</li><li>Injuries: %s</li><li>Landslide Size: %s</li></ul><center><img src=\"%s\" align=\"middle\" height=\"300\" width=\"300\"></center>" %(country, date, trigger, injur, size, image_url)
                },
            }
            data.append(point)
        with open('static/data/point.json', 'w') as f:
            json.dump(data, f)
        return jsonify({})

if __name__ == "__main__":
    app.run('0.0.0.0')
