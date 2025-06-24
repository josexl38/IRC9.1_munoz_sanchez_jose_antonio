from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ""
    if request.method == 'POST':
        try:
            cmd = ["ansible-playbook", "-i", "inventory.ini", "app/playbooks/ejemplo.yml"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout + result.stderr
        except Exception as e:
            output = f"ERROR: {e}"
    return render_template("index.html", output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
