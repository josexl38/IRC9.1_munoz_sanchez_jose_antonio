import subprocess
import os
import json
import tempfile
import shutil


# Rutas absolutas para binarios
SSHPASS = shutil.which('sshpass') or '/usr/bin/sshpass'
SSH = shutil.which('ssh') or '/usr/bin/ssh'
ANSIBLE_PLAYBOOK = shutil.which('ansible-playbook') or '/usr/local/bin/ansible-playbook'


def load_servers():
    servers_file = os.path.join(os.getcwd(), 'servers.json')
    if not os.path.exists(servers_file):
        raise FileNotFoundError("❌ El archivo servers.json no existe.")
    with open(servers_file, 'r') as f:
        return json.load(f)


def generate_inventory(servers):
    inventory = "[all]\n"
    for name, data in servers.items():
        ip = data['ip']
        user = data.get('user', 'root')
        ssh_key = data.get('ssh_key', '').strip()
        password = data.get('password', '').strip()

        line = (
            f"{name} ansible_host={ip} ansible_user={user} "
            f"ansible_become=true ansible_become_method=sudo"
        )

        if ssh_key:
            ssh_key = os.path.expanduser(ssh_key)
            line += f" ansible_ssh_private_key_file={ssh_key}"
        if password:
            line += (
                f" ansible_ssh_pass={password} "
                f"ansible_become_pass={password} "
                f"ansible_connection=ssh "
                f"ansible_ssh_common_args='-o StrictHostKeyChecking=no' "
            )

        inventory += line + "\n"

    inventory += "\n[all:vars]\n"
    inventory += "ansible_host_key_checking=False\n"
    return inventory


def run_playbook(playbook, server):
    playbook_path = os.path.join('playbooks', playbook)
    if not os.path.exists(playbook_path):
        return f"❌ Playbook {playbook} no encontrado."

    servers = load_servers()
    if server != "all" and server not in servers:
        return f"❌ El servidor {server} no está en la lista."

    inventory_content = generate_inventory(servers)

    with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
        tmp.write(inventory_content)
        inventory_path = tmp.name

    cmd = [
        ANSIBLE_PLAYBOOK,
        playbook_path,
        "-i", inventory_path,
        "-l", server if server != "all" else "all"
    ]

    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        output = result.stdout + "\n" + result.stderr

    except FileNotFoundError as e:
        output = f"❌ Error ejecutando ansible-playbook: {str(e)}"

    finally:
        if os.path.exists(inventory_path):
            os.remove(inventory_path)

    return output


def test_ssh_connection(ip, user, ssh_key=None, password=None):
    """Verifica la conexión SSH. Devuelve (True, mensaje) o (False, error)."""
    if ssh_key:
        ssh_key = os.path.expanduser(ssh_key)
        cmd = [
            SSH,
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=5",
            "-i", ssh_key,
            f"{user}@{ip}",
            "echo OK"
        ]
    elif password:
        if not SSHPASS or not os.path.exists(SSHPASS):
            return False, "❌ sshpass no está instalado y es necesario para conexiones por contraseña."

        cmd = [
            SSHPASS, "-p", password,
            SSH,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            f"{user}@{ip}",
            "echo OK"
        ]
    else:
        return False, "❌ Debes proporcionar llave SSH o contraseña."

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if proc.returncode == 0 and "OK" in proc.stdout:
            return True, "✅ Conexión SSH exitosa."
        else:
            return False, proc.stderr.strip()

    except FileNotFoundError as e:
        return False, f"❌ Error ejecutando comando: {str(e)}"
