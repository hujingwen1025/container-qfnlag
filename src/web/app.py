from flask import Flask, request, render_template, jsonify
from logger import log
from sqlalchemy import text
from db import get_db, close_db
import sqlalchemy
import socket
import random
import linecache
import datetime

#hostname = socket.gethostname()
#IPAddr = socket.gethostbyname(hostname)

app = Flask(__name__)
app.teardown_appcontext(close_db)

debug = 0

signinhandlejs = ''

credfilepath = "assets/creds/cred.txt"

sessionidpath = "assets/creds/sessionid.txt"

randcharpath = "assets/security/randchar.txt"
randchar = []

devemail = 'jingwenhu1025@gmail.com'

signouthtmlpath = 'assets/html/signout.html'

dashboardhtmlpath = 'assets/html/dashboard.html'

addretlogscript = """

"""

signinhandlepath = 'assets/js/signinhandle.js'

addretlogtextpath = 'assets/html/signin.html'

homehtmlpath = 'assets/html/suc.html'

def dprint(text):
    if debug == 1:
        print(text)
        
def genranstring(length, data):
    try:
        string = ''
        for i in range(length):
            string += data[random.randint(0, len(data) - 1)]
        return string
    except:
        return 'Error'

def matchcred(filepath, username, password):
    try:
        with open(filepath) as credfile:
            for item in credfile:
                if ord(item[-1]) == 10:
                    pitem = item[:-1]
                else:
                    pitem = item
                usern = pitem.split('*')[0]
                passd = pitem.split('*')[1]
                if username == usern and password == passd:
                    return True
        return False
    except:
        return 'Error'
    
def postlogin(username, data, expday):
    try:
        while True:
            sessionid = genranstring(8192, data)
            with open(sessionidpath) as sessionidfile:
                for item in sessionidfile:
                    if ord(item[-1]) == 10:
                        pitem = item[:-1]
                    else:
                        pitem = item
                    spitem = pitem.split('*')
                    cursession = spitem[1]
                    if sessionid == cursession:
                        continue
            break
        curdate = datetime.date.today()
        expdate = curdate + datetime.timedelta(days = expday)
        writeinfo = str(expdate) + '*' + str(sessionid) + '*' + str(username) + '*' + str(curdate)
        with open(sessionidpath, 'a') as sessionidfile:
            sessionidfile.write(writeinfo + '\n')
        retinfo = signinhandlejs.replace('%sessionid%', sessionid)
        return  str(addretlogtext) + '<script>' + retinfo +  addretlogscript + '</script>'
    except AssertionError as error:
        return render_template('regmatcherr.html')

def matchsession(filepath, sessionid):
    with open(filepath) as sessionidfile:
        for item in sessionidfile:
            if ord(item[-1]) == 10:
                pitem = item[:-1]
            else:
                pitem = item
            spitem = pitem.split('*')
            curexp = spitem[0].split('-')
            cursession = spitem[1]
            curuser = spitem[2]
            curdate = str(datetime.date.today()).split('-')
            if cursession == sessionid:
                print(datetime.datetime(int(curexp[0]), int(curexp[1]), int(curexp[2])))
                print(datetime.datetime(int(curdate[0]), int(curdate[1]), int(curdate[2])))
                if datetime.datetime(int(curexp[0]), int(curexp[1]), int(curexp[2])) > datetime.datetime(int(curdate[0]), int(curdate[1]), int(curdate[2])):
                    print('valid exp')
                    return curuser
                else:
                    return False
    return False
                
with open(randcharpath) as randcharfile:
    for curitem in randcharfile:
        if ord(curitem[-1]) == 10:
            randchar += curitem[:-1]
        else:
            randchar += curitem
            
with open(addretlogtextpath, 'r') as file:
    addretlogtext = file.read()
    
with open(homehtmlpath, 'r') as file:
    homehtml = file.read()
    
with open(dashboardhtmlpath, 'r') as file:
    dashboardhtml = file.read()
    
with open(signinhandlepath, 'r') as file:
    signinhandlejs = file.read()
    
with open(signouthtmlpath, 'r') as file:
    signouthtml = file.read()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/noresponse')
def noresponse():
    return render_template('nores.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    mcred = matchcred(credfilepath, username, password)
    
    if mcred == True:
        return postlogin(username, randchar, 2)
    elif mcred == False:
        return render_template('incpass.html')
    elif mcred == 'Error':
        render_template('regmatcherr.html')
    render_template('regmatcherr.html')

@app.route('/reg', methods=['POST'])
def reg():
    username = request.form['username']
    password = request.form['password']
    veripass = request.form['veripassword']
    
    if password != veripass:
        return render_template('regmatcherr.html')
    
    with open(credfilepath) as credfile:
        for item in credfile:
            if ord(item[-1]) == 10:
                pitem = item[:-1]
            else:
                pitem = item
            spitem = pitem.split('*')
            usern = pitem.split('*')[0]
            if username == usern:
                return render_template('regusernameerr.html')
    
    for char in username:
        if ord(char) < 32 or ord(char) > 122 or ord(char) == 42:
            return render_template('regusercharerr.html')
    
    for char in password:
        if ord(char) < 32 or ord(char) > 122 or ord(char) == 42:
            return render_template('regpasscharerr.html')
        
    writeinfo = '\n' + str(username) + '*' + str(password)
        
    with open(credfilepath, 'a') as credfile:
        credfile.write(writeinfo)
        
    return render_template('regsuc.html')

@app.route('/home', methods=['POST'])
def home():
    print('Client Request Home')
    sessionid = request.json.get('sessionid')
    print('sessionid is - ' + str(sessionid))
    username = matchsession(sessionidpath, sessionid)
    print('username is - ' + str(username))
    if username != False:
        retinfo = {
            "html": homehtml,
        }
        print(jsonify(retinfo))
        return jsonify(retinfo)
    else:
        retinfo = {
            "html": signouthtml,
        }
        print(jsonify(retinfo))
        return jsonify(retinfo)
    
@app.route('/dashboard', methods=['POST'])
def dashboard():
    print('Client Request Dashboard')
    sessionid = request.json.get('sessionid')
    print('sessionid is - ' + str(sessionid))
    username = matchsession(sessionidpath, sessionid)
    print('username is - ' + str(username))
    if username != False:
        retinfo = {
            "html": dashboardhtml,
        }
        print(jsonify(retinfo))
        return jsonify(retinfo)
    else:
        retinfo = {
            "html": signouthtml,
        }
        print(jsonify(retinfo))
        return jsonify(retinfo)
    
@app.route('/developerlogin')
def developerlogin():
    return render_template('devlogin.html')

@app.route('/devlogin', methods=['POST'])
def devlogin():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'admin' and password == 'password':
        return 'Login Success'
    else:
        return 'Invalid Credentials'
    
