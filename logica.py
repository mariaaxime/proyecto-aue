from flask import Flask, request, session, g, render_template, json, redirect, url_for, send_from_directory, flash
from django.utils.safestring import mark_safe
import statistics
import numpy as np
import sqlite3
import Simulate as si
import Entrada as en
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(__name__)


UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['json'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.update(dict(
    DATABASE=os.path.join(app.static_folder, 'aue.db'),
    SECRET_KEY='RrLYMdLdbwU3ghN',
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.secret_key = 'RrLYMdLdbwU3ghN'

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.before_first_request
def initdb_command():
    """Initializes the database."""
    init_db()
    print ('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/", methods=['GET'])
def index():
    if session.get('usuario'):
        return render_template('index.html', activar=session['ya_simule'])
    else:
        return render_template('login.html')

@app.route("/index", methods=['GET', 'POST'])
def login():
    db = get_db()
    username = request.form['username']
    password = request.form['pwd']
    curusuario = db.execute('select * from USUARIO where username="' + username + '" and password="' + password + '"')
    usuario = curusuario.fetchone()
    if usuario is not None:
        session['usuario'] = username
        session['inversion'] = 4
        session['reposicion'] = 1.5
        session['baterias'] = 3.5
        session['mantenimiento'] = 0.3
        session['ya_simule'] = 0
        return render_template('index.html', activar=session['ya_simule'])
    else:
        return render_template('login.html')

@app.route("/costs")
def entrada_costos():
    return render_template('cost_parameters.html', activar=session['ya_simule'], inversion=session['inversion']
                           , reposicion=session['reposicion'], baterias=session['baterias'], mantenimiento=session['mantenimiento'])

@app.route("/input", methods=['POST'])
def entrada_parametros_costos():
    session['inversion'] = float(request.form['inversion'])
    session['reposicion'] = float(request.form['reposicion'])
    session['baterias'] = float(request.form['baterias'])
    session['mantenimiento'] = float(request.form['mantenimiento'])
    if (session['ya_simule'] == 1):
        return render_template('simulation.html', simulacion=session['simulacion'],
                           dias=session['numDias'], periodos=session['periodos'], aparatos=session['aparatos'], activar=session['ya_simule'])
    return render_template('index.html', activar=session['ya_simule'])

@app.route("/probabilities", methods=['POST'])
def leer_parametros():
    aparatos = []
    periodos = int(request.form['periodos'])
    session['periodos'] = periodos
    for i in range(10):
        nom = 'aparato' + str(i + 1)
        if (request.form[nom] != ""):
            aparatos.append(request.form[nom])
        session['aparatos'] = aparatos
    return render_template('appliance_profile.html', aparatos=session['aparatos'], periodos=session['periodos'], activar=session['ya_simule'])

@app.route("/probs", methods=['GET'])
def ir_probabilidades():
    return render_template('appliance_profile.html', aparatos=session['aparatos'], periodos=session['periodos'], probabilidades=session['probabilidades'], activar=session['ya_simule'])

@app.route("/profs", methods=['GET'])
def ir_perfiles():
    return render_template('customer_profile.html', aparatos=session['aparatos'], perfiles=session['perfiles'], activar=session['ya_simule'])

@app.route("/params", methods=['GET'])
def ir_parametros():
    return render_template('simulation_parameters.html', dias=session['numDias'], activar=session['ya_simule'])

@app.route("/table", methods=['POST'])
def mostrar_probabilidades():
    probabilidades = []
    aparatos = session['aparatos']
    periodos = session['periodos']
    for apa in aparatos:
        prob = {}
        prob['aparato'] = apa
        inicio = []
        duracion = []
        for p in range(periodos+1):
            ini = 'pi_' + apa + str(p)
            dur = 'pd_' + apa + str(p)
            inicio.append(float(request.form[ini]))
            duracion.append(float(request.form[dur]))
        prob['inicio'] = inicio
        prob['duracion'] = duracion
        probabilidades.append(prob)
    session['probabilidades'] = probabilidades
    return render_template('probabilities.html', probabilidades=session['probabilidades'], activar=session['ya_simule'])

@app.route("/profiles", methods=['POST'])
def leer_perfiles():
    return render_template('customer_profile.html', aparatos=session['aparatos'], activar=session['ya_simule'])

@app.route("/parameters", methods=['POST'])
def guardar_perfiles():
    nombres = session['aparatos']
    perfiles = []
    suma = 0
    for p in [1, 2]:
        per = 'perfil' + str(p)
        suma += int(request.form[per])
        session['numUsuarios'] = suma
    for p in [1,2]:
        perfil = {}
        per = 'perfil' + str(p)
        perfil['id'] = p
        perfil['cantidad'] = int(request.form[per])
        perfil['proporcion'] = (int(request.form[per])/suma) * 100
        aparatos = []
        for apa in nombres:
            if (request.form.get(str(p) + "_" + apa)):
                aparato = {}
                aparato['nombre'] = apa
                cant = 'cantidad' + str(p) + '_' + apa
                pot = 'potencia' + str(p) + '_' + apa
                aparato['cantidad'] = int(request.form[cant])
                aparato['potencia'] = int(request.form[pot])
                aparatos.append(aparato)
        perfil['aparatos'] = aparatos
        perfiles.append(perfil)
    session['perfiles'] = perfiles
    en.getProfiles(session['perfiles'])
    return render_template('simulation_parameters.html', perfiles = session['perfiles'], activar=session['ya_simule'])

@app.route("/simulation", methods=['GET', 'POST'])
def simular():
    session['numDias'] = int(request.form['numDias'])
    simu = si.simular(session['numUsuarios'], session['numDias'], session['periodos'])
    session['simulacion'] = simu
    write_file('simulacion.json', session['simulacion'])
    write_file('dias.json', session['numDias'])
    session['ya_simule'] = 1
    return render_template('simulation.html', simulacion=session['simulacion'],
                           dias=session['numDias'], periodos=session['periodos'], aparatos=session['aparatos'], activar=session['ya_simule'])

@app.route("/simulation_results", methods=['GET', 'POST'])
def mostrar_simulacion():
    session['simulacion'] = read_file('simulacion.json')
    return render_template('simulation.html', simulacion=session['simulacion'],
                           dias=session['numDias'], periodos=session['periodos'], aparatos=session['aparatos'], activar=session['ya_simule'])


@app.route("/total_graph", methods=['GET', 'POST'])
def graficar_total():
    consumo_total = []
    session['simulacion'] = read_file('simulacion.json')
    session['numDias'] = read_file('dias.json')
    for s in session['simulacion']:
        consumo_total.append(s['total'])
    session['consumo_total'] = consumo_total
    write_file('totales.json', session['consumo_total'])
    return render_template('total_graph.html', consumo=session['consumo_total'],
                           dias=session['numDias'], periodos=session['periodos'], activar=session['ya_simule'])

@app.route("/app_graph", methods=['GET', 'POST'])
def graficar_aparatos():
    consumo_aparatos = []
    session['simulacion'] = read_file('simulacion.json')
    session['numDias'] = read_file('dias.json')
    for a in session['aparatos']:
        consumo_aparatos.append(a + "")
        for s in session['simulacion']:
            consumo_aparatos.append(s[a])
    session['consumo_aparatos'] = consumo_aparatos
    return render_template('appliance_graph.html', consumo=mark_safe(session['consumo_aparatos']),
                           dias=session['numDias'], periodos=session['periodos'], activar=session['ya_simule'])


@app.route("/cost_graph", methods=['GET', 'POST'])
def graficar_costos():
    session['consumo_total'] = read_file('totales.json')
    totales = session['consumo_total']
    dolar = 2746.47
    anios = 21

    # wp: Pico maximo de la curva de consumo
    wp = max(totales)

    # CAPEX
    capex = []
    cis = session['inversion'] * dolar  # (Costo de inversion solar para wp)
    rem = session['reposicion'] * dolar  # Rem (Costo de reposicion del sistema fotovoltaico para wp)
    cl = session['numUsuarios']  # cl: Nivel de dispersion (tamaño de la población)

    capex.append('capex')
    for i in range(anios):
        c = ((cis * wp) + (rem * wp * int(i / 10)))/1000000
        capex.append(c)

    session['capex'] = capex

    # OPEX
    opex = []
    cb = session['baterias'] * dolar / 1000 # (costo del uso de las baterías por Wh)
    aom = session['mantenimiento'] * dolar  # costo de mantenimiento por mes por cliente
    b = sum(totales) / len(totales)  # Bcl (Promedio diario del uso de las baterias)

    opex.append('opex')
    for i in range(anios):
        o = ((cb * b * 365 * i) + (aom * cl * 12 * i))/1000000
        opex.append(o)

    session['opex'] = opex

    return render_template('cost_graph.html', anios=anios, capex=mark_safe(session['capex']), opex=mark_safe(session['opex']), activar=session['ya_simule'])

@app.route("/statistics", methods=['GET', 'POST'])
def generar_estadisticas():
    opex = session['opex']
    capex = session['capex']
    total = read_file('totales.json')
    periodos = session['periodos']
    dias = session['numDias']
    usuarios = session['numUsuarios']
    t = np.array(total)
    total_dia = []
    factor_dia = []
    promedio_dia = []
    session['costo_promedio'] = round(((sum(opex[1:])+sum(capex[1:]))/len(opex))/12, 3)
    session['variacion'] = round(np.std(t)/np.mean(t)*100,3)
    session['consumo_promedio'] = round(sum(total)/len(total),3)
    session['daily_peak'] = np.percentile(t, 95)
    for i in range(0,dias):
        total_dia.append(sum(total[i*periodos:(i+1)*periodos]))
        promedio_dia.append(total_dia[i]/periodos)
        factor_dia.append(promedio_dia[i]/max(total[i*periodos:(i+1)*periodos]))
    session['total_dia'] = total_dia
    session['monthly_average'] = ((sum(total_dia)/len(total_dia))*30)/usuarios
    session['load_factor'] = round((sum(factor_dia)/len(factor_dia))*100,3)
    return render_template('statistics.html', costo=session['costo_promedio'], variacion=session['variacion'],
                           consumo=session['consumo_promedio'], peak=session['daily_peak'],
                           month=session['monthly_average'], factor=session['load_factor'], activar=session['ya_simule'])

@app.route("/curve_graph", methods=['GET', 'POST'])
def graficar_curva():
    total = read_file('totales.json')
    total = sorted(total, reverse=True)
    total.insert(0, 'Consumo por período')
    return render_template('loadcurve_graph.html', consumo=total, activar=session['ya_simule'])

@app.route("/box_graph", methods=['GET', 'POST'])
def graficar_cajas():
    total = read_file('totales.json')
    periodos = session['periodos']
    total_periodos = []
    eje_periodos = []

    for i in range(periodos):
        total_periodos.append([])
        eje_periodos.append(i+1)

    for i in range(len(total)):
        pos = i%periodos
        total_periodos[pos].append(total[i])
    return render_template('totalbox_graph.html', consumo=total_periodos, eje=eje_periodos, activar=session['ya_simule'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_data', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            aparatos = []
            probabilidades = read_file(filename)
            session['probabilidades'] = probabilidades
            for p in probabilidades:
                aparatos.append(p['aparato'])
                session['periodos'] = len(p['inicio']) -1
            session['aparatos'] = aparatos
            en.getprobas(probabilidades, session['aparatos'], session['periodos'])
            return render_template('probabilities.html', probabilidades=session['probabilidades'], activar=session['ya_simule'])

def read_file(file):
    with open(file) as json_data:
        d = json.load(json_data)
        return d

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

def read_file(file):
    with open(file) as json_data:
        d = json.load(json_data)
        return d

def write_file(file, data):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #app.run(debug=True)