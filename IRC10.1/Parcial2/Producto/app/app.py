from flask import Flask, render_template, request, redirect, session, url_for, flash
from app.database import init_db, get_user, create_user, log_action, get_logs
from app.ansible_runner import run_playbook, test_ssh_connection
import os, json, logging

# ------------------------
# 🔧 Configuración Logging
# ------------------------
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# ------------------------
# 🚀 Configuración Flask
# ------------------------
app = Flask(__name__)
app.secret_key = 'supersecretkey'

init_db()

# ------------------------
# 🔧 Directorios
# ------------------------
BASE_DIR = os.getcwd()
PLAYBOOKS_DIR = os.path.join(BASE_DIR, 'playbooks')
SERVERS_FILE = os.path.join(BASE_DIR, 'servers.json')
KEYS_DIR = os.path.join(BASE_DIR, 'ssh_keys')
os.makedirs(KEYS_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# ------------------------
# 📦 Funciones Auxiliares
# ------------------------
def load_servers():
    if not os.path.exists(SERVERS_FILE):
        with open(SERVERS_FILE, 'w') as f:
            json.dump({}, f, indent=4)
    with open(SERVERS_FILE, 'r') as f:
        return json.load(f)

def save_servers(servers):
    with open(SERVERS_FILE, 'w') as f:
        json.dump(servers, f, indent=4)

# ------------------------
# 🔐 Rutas de Autenticación
# ------------------------
@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = get_user(request.form['username'])
        if user and user['password'] == request.form['password']:
            session['username'] = user['username']
            log_action(user['username'], 'Login')
            return redirect('/dashboard')
        error = 'Credenciales inválidas'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        try:
            create_user(request.form['username'], request.form['password'])
            log_action(request.form['username'], 'Registro')
            return redirect('/login')
        except:
            error = 'Usuario ya existe'
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    u = session.get('username')
    log_action(u, 'Logout')
    session.clear()
    return redirect('/login')

# ------------------------
# 🏠 Dashboard (Playbook Runner)
# ------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    servers = load_servers()
    playbooks = [f for f in os.listdir(PLAYBOOKS_DIR) if f.endswith(('.yml', '.yaml'))]
    output = ""

    if request.method == 'POST':
        selected_playbooks = request.form.getlist('playbooks')
        selected_servers = request.form.getlist('servers')

        if not selected_playbooks or not selected_servers:
            flash("⚠️ Debes seleccionar al menos un playbook y un servidor.")
        else:
            targets = servers.keys() if "all" in selected_servers else selected_servers
            for srv in targets:
                for pb in selected_playbooks:
                    logging.info(f'Run playbook {pb} on {srv}')
                    out = run_playbook(pb, srv)
                    output += f"\n▶️ Playbook: {pb} en servidor: {srv}\n{out}\n"
                    log_action(session['username'], f'Ejecutó {pb} en {srv}')

    return render_template('dashboard.html',
                           username=session['username'],
                           playbooks=playbooks,
                           servers=servers,
                           output=output)

# ------------------------
# 📜 CRUD Playbooks
# ------------------------
@app.route('/playbooks')
def playbooks_list():
    if 'username' not in session:
        return redirect('/login')
    pbs = [f for f in os.listdir(PLAYBOOKS_DIR) if f.endswith(('.yml', '.yaml'))]
    return render_template('playbooks.html', playbooks=pbs)

@app.route('/playbooks/create', methods=['GET', 'POST'])
def create_playbook():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        filename = request.form['filename']
        content = request.form['content']
        if not filename.endswith('.yml'):
            filename += '.yml'
        path = os.path.join(PLAYBOOKS_DIR, filename)
        with open(path, 'w') as f:
            f.write(content)
        log_action(session['username'], f'Creó playbook {filename}')
        return redirect('/playbooks')
    return render_template('create_playbook.html')

@app.route('/playbooks/edit/<name>', methods=['GET', 'POST'])
def edit_playbook(name):
    if 'username' not in session:
        return redirect('/login')
    path = os.path.join(PLAYBOOKS_DIR, name)
    if request.method == 'POST':
        content = request.form['content']
        with open(path, 'w') as f:
            f.write(content)
        log_action(session['username'], f'Editó playbook {name}')
        return redirect('/playbooks')
    with open(path, 'r') as f:
        content = f.read()
    return render_template('edit_playbook.html', name=name, content=content)

@app.route('/playbooks/delete/<name>', methods=['POST'])
def delete_playbook(name):
    if 'username' not in session:
        return redirect('/login')
    path = os.path.join(PLAYBOOKS_DIR, name)
    if os.path.exists(path):
        os.remove(path)
        log_action(session['username'], f'Eliminó playbook {name}')
    return redirect('/playbooks')

# ------------------------
# 🖥️ CRUD Servers + SSH Test
# ------------------------
@app.route('/servers')
def servers_list():
    if 'username' not in session:
        return redirect('/login')
    return render_template('servers.html', servers=load_servers())

@app.route('/servers/create', methods=['GET', 'POST'])
def create_server():
    if 'username' not in session:
        return redirect('/login')
    servers = load_servers()
    if request.method == 'POST':
        alias = request.form['alias']
        ip = request.form['ip']
        user = request.form['user']
        ssh_key = request.form.get('ssh_key', '').strip()
        password = request.form.get('password', '').strip()

        ok, msg = test_ssh_connection(ip, user, ssh_key or None, password or None)
        if not ok:
            flash(f"❌ Falló conexión a {alias}: {msg}")
        else:
            flash(f"✅ Conexión SSH exitosa con {alias}.")
            servers[alias] = {
                "ip": ip,
                "user": user,
                "ssh_key": ssh_key,
                "password": password
            }
            save_servers(servers)
            log_action(session['username'], f'Creó servidor {alias} ({ip})')
            return redirect('/servers')

    return render_template('create_server.html')

@app.route('/servers/edit/<alias>', methods=['GET', 'POST'])
def edit_server(alias):
    if 'username' not in session:
        return redirect('/login')

    servers = load_servers()
    if alias not in servers:
        flash("Servidor no existe")
        return redirect('/servers')

    srv = servers[alias]

    if request.method == 'POST':
        new_alias = request.form['alias']
        ip = request.form['ip']
        user = request.form['user']
        ssh_key = request.form.get('ssh_key', '').strip() or srv.get('ssh_key', '')
        password = request.form.get('password', '').strip() or srv.get('password', '')

        ok, msg = test_ssh_connection(ip, user, ssh_key or None, password or None)
        if not ok:
            flash(f"❌ Falló conexión a {new_alias}: {msg}")
        else:
            flash(f"✅ Conexión SSH exitosa con {new_alias}.")
            if new_alias != alias:
                servers.pop(alias)

            servers[new_alias] = {
                "ip": ip,
                "user": user,
                "ssh_key": ssh_key,
                "password": password
            }

            save_servers(servers)
            log_action(session['username'], f'Editó servidor {alias} -> {new_alias}')
            return redirect('/servers')

    return render_template('edit_server.html', alias=alias, server=srv)

@app.route('/servers/delete/<alias>', methods=['POST'])
def delete_server(alias):
    if 'username' not in session:
        return redirect('/login')
    servers = load_servers()
    if alias in servers:
        ip = servers.pop(alias).get('ip', 'desconocida')
        save_servers(servers)
        log_action(session['username'], f'Eliminó servidor {alias} ({ip})')
    return redirect('/servers')

# ------------------------
# 📜 Logs
# ------------------------
@app.route('/logs')
def logs():
    if 'username' not in session:
        return redirect('/login')
    return render_template('logs.html', logs=get_logs())

# ------------------------
# 🚀 Run App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
