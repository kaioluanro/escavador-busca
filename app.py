from datetime import date, timedelta
import pandas as pd
import numpy as np
import datetime
import time
from ultraabs import ultrabs, OrdDocs, isValidSpacy
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room
from uuid import uuid4

app = Flask(__name__)
import os
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy(app)
socketio = SocketIO(app,async_mode='gevent')
titleApp = 'Escavador RT'

class DataDom(db.Model):
    __tablename__ = 'data_dom'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=False, nullable=False)
    page = db.Column(db.Integer)
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    # Add new column
    ids = db.Column(db.Text)
    nums = db.Column(db.Text)
    secs = db.Column(db.Text)

    def __init__(self, title, page, text, date,ids,nums,secs):
        self.title = title
        self.page = page
        self.text = text
        self.date = date
        self.ids = ids  # Initialize ids column
        self.nums = nums
        self.secs = secs

class createDFtoSeach():
    def __init__(self,s_y,s_m,s_d,e_y,e_m,e_d):
        start = pd.Timestamp(int(s_y), int(s_m), int(s_d))
        end = pd.Timestamp(int(e_y), int(e_m), int(e_d))
        
        filtered_query = DataDom.query.filter(DataDom.date <= start, DataDom.date >= end)
        self.query = filtered_query
        results = filtered_query.all()
        self.df = pd.DataFrame([res.__dict__ for res in results])
        self.df = self.df.drop(columns='_sa_instance_state')
        

task_complete = False
task_complete1 = False

def convert_int64(obj):
    """
    Converte todos os valores np.int64 em int normais em um objeto json serializável.
    """
    if isinstance(obj, list):
        for idx, val in enumerate(obj):
            obj[idx] = convert_int64(val)
        return obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = convert_int64(value)
        return obj
    elif isinstance(obj, np.int64):
        return int(obj)
    else:
        return obj

clients = {}
@socketio.on('connect')
def handle_connect():
    #print('Client connected: ', clients)
    clients[request.sid] = request.sid
    socketio.emit('set_sid_cookie', {'sid': request.sid}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    #print('Client disconnected: ', request.sid)
    clients.pop(request.sid, None)

def emit_cust(namespace,data,client_sid):
    submissao_id = client_sid
    if submissao_id in clients:
        sid = clients[submissao_id]
        socketio.emit(namespace, data, room=sid)
    

@app.route('/', methods=['GET','POST'])
def principal():
    
    
    
    #socketio.emit('load_config',{'isValid': isValidSpacy},room=room)
    #socketio.emit('send_interno',{'listen_name':'load_config','data':{'isValid': isValidSpacy}})
    #while True:
    #    if isValidSpacy:
    #        #socketio.emit('load_config',{'isValid': isValidSpacy},room=room)
    #        socketio.emit('send_interno',{'listen_name':'load_config','data':{'isValid': isValidSpacy}})
    #        break  # Sair do loop quando a variável for True.   
    #    time.sleep(1)
    
    #========= Clear data json
    if 'data' in session:
        session.pop('data', None)
    #========= Create Year start 1986
    current_year = datetime.datetime.now().year
    years = list(range(1986, current_year + 1))
    
    #========= Get Date current
    current_day = datetime.datetime.now().day
    current_month = datetime.datetime.now().month
    
    #========= Get Filter Date
    start_day = request.form.get('start_day')
    start_month = request.form.get('start_month')
    start_year = request.form.get('start_year')
    end_day = request.form.get('end_day')
    end_month = request.form.get('end_month')
    end_year = request.form.get('end_year')
    
    #========= Get Text Search
    text_search = request.form.get('text_search')
    if text_search is not None:
        text_search = text_search.lower()
    
    #========= Get Client Sid
    client_sid = request.form.get('client_sid')
    
    search_data = ['']
    
    if request.method == 'POST':
        global task_complete
        global task_complete1
        #session['sid'] = client_sid
        ssnGet = client_sid#session.get('sid')
        #print(f"SID NA SESSION {session.get('sid')}")
        #emit_cust('alert-e',{'message':'OK'},session.get('sid'))
        #print('{}/{}/{} |>| {}/{}/{}'.format(start_year,start_month,start_day,end_year,end_month,end_day))
        #print('Texto da Barra: {}'.format(text_search))
        
        #===tratamentos search_data====:
                
        # 2.1. Verificador de palavras Genericas
        # 4. criar um Função para o texto na text area
        
        
        #================TEST CONTEXT SEACH AND MATCH
        #OUT == OK
        #text_search = "onde esta a LEI COMPLEMENTAR 5.910"
        #OUT == OK
        #text_search = "onde esta a portaria 77/2023 semf"
        #OUT WITH SEC == OK
        #text_search = "onde esta a portaria 77/2023 sec: semf"
        #OUT WITH DOM AND RESULT NULL == OK
        #text_search = "Em qual jornal esta a lei 1.875 dom: 3526 3516 3455 3325"
        #OUT WITH DOM AND RESULT VALID == OK
        #text_search = "Em qual jornal esta a lei 5.910 dom: 3526 3516 3455 3325"
        #================TEST COMMAND ESPECIFIC
        #OUT ID == OK
        #text_search = "id: 000480352600012023 000480352600022023 000420352600032023 000480352500062023 000480352500102023"
        #OUT SEC == OK
        #text_search = "sec: semf"
        #OUT SEC NUM == OK
        #text_search ="sec: poder num: 0001"
        #OUT DOM == OK
        #text_search = "dom: 3526 3516 3455 3325"
        #OUT DOM NUM == OK
        #text_search ="dom: 3439 3445 3469 num: 0002"
        #OUT DOM SEC NUM == OK
        #text_search ="dom: 3439 3445 3469 sec: poder num: 0010"
        #OUT DOM SEC  == OK
        #text_search ="dom: 3439 3445 3469 sec: sema"
                
        #============ Verify if Filter date correct!
        start1 = pd.Timestamp(int(start_year), int(start_month), int(start_day))
        end1 = pd.Timestamp(int(end_year), int(end_month), int(end_day))
        fix_compare_date = pd.Timestamp(2023,1,1)
        days = (start1 - end1).days + 1
        limit_date = 4*365
        
        if text_search != '':
            if days < limit_date:
                if start1 > end1:
                    #print(f"{start1} > {end1} = {start1 > end1}")
                    
                    if ("sec: " in text_search) or ("num: " in text_search) or ("id: " in text_search):
                        
                        if end1 < fix_compare_date:
                            #print(f"{end1} < {fix_compare_date} = {end1 < fix_compare_date}")
                            emit_cust('alert-e', {'message': 'Você não poder ajustar o limite final do filtro temporal com data inferior a 01/01/2023, pois o recurso de chaves "ID" não existe em data inferiores a 2023. Por favor, reajuste o limite final do filtro temporal para uma data aparte de 2023!'},ssnGet)
                        else:
                            df_f = createDFtoSeach(start_year,start_month,start_day,
                                                    end_year,end_month,end_day)
                    else:
                        if ("dom: " in text_search):
                            df_f = createDFtoSeach(1987,1,1,1986,1,1)
                        else:
                            df_f = createDFtoSeach(start_year,start_month,start_day,
                                                    end_year,end_month,end_day)
                
                    task_complete = True
                    #print(df_f.df)
                    #==== TEST PERFORM
                    emit_cust('inf_process_data',{},ssnGet)
                
                    search_data = ultrabs(text_search,df_f.df,df_f.query,DataDom)
                        
                    search_data_reord=OrdDocs(search_data.res)
                    #print(search_data_reord.organize_by_score())
                    search_data_reord = search_data_reord.organize_by_score()
                    convert_int64(search_data_reord)
                    
                    session.modified = False
                    
                    #========= Create Struct for Json session
                    if 'data' not in session:
                        session['data'] = {}
                    
                    if len(search_data.res['titles']) == 0:
                        session['data']['None'] = 'None'
                    
                    else:
                        session['data'][search_data.termoSearch] = search_data_reord
                    
                    data = session.get('data')
                    
                    emit_cust('result_end',{'data':data},ssnGet)
                                        
                    session.modified = True
                    task_complete1 = True
                else:
                    emit_cust('alert-e', {'message': 'Ter colocado o limite inicial do filtro temporal com data inferior ao limite final. Por favor, ajuste o filtro temporal para a data limite inicial seja superior à data limite final. Ex: 30/06/2023 até 12/05/2022.'},ssnGet)        
            else:
                emit_cust('alert-e', {'message': 'Intervalo de limite inicial e limite final do Filtro temporal é superior a 4 anos. Por favor, altere a data de início e fim do filtro temporal para o intervalo seja inferior a 4 anos.'},ssnGet)                                    
        else:
            emit_cust('alert-e', {'message': 'Barra de pesquisa essa vazia. Por favor, preencha a barra de pesquisa com os prompts apropriados para começar a buscar!'},ssnGet)                                    
        
    
    return render_template("timelinesearch.html", years=years, 
                           current_day=current_day,current_month=current_month,
                           current_year=current_year,titleApp=titleApp)

@app.route('/start_task', methods=['POST'])
def start_task():
    global task_complete
    task_complete = False

    return jsonify({'message': 'Task started.'})

@app.route('/task_status', methods=['GET'])
def task_status():
    global task_complete

    # Retorna o status da tarefa.
    return jsonify({'complete': task_complete})

@app.route('/info_db', methods=['GET'])
def info_db():
    total_pages = DataDom.query.count()
    unique_titles_count = db.session.query(DataDom.title).distinct().count()
    
    current_date = date.today()
    one_month_ago = current_date - timedelta(days=30)
    records = DataDom.query.filter(DataDom.date >= one_month_ago).all()
    closest_record = min(records, key=lambda record: abs(record.date - current_date))

    # Retorna o status da tarefa.
    return jsonify({'pages_all': total_pages,
                    'num_doms': unique_titles_count,
                    'current_dom':(closest_record.title).split('-')[0]})

@app.route('/tips')
def tip():
    return render_template("tips.html")

if __name__ == "__main__":
    socketio.run(app, host='127.0.0.1')

