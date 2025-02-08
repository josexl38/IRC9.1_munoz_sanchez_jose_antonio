import platform
import sys
import subprocess
from threading import local

sistemaop = sys.platform
sistema = platform.system()
version = platform.win32_ver()

print("Estamos en {}".format(sistema), "en version: {}".format(version))
if sistema == 'Windows':
    local = subprocess.getoutput("""for /f "tokens=2 delims=[]" %a in ('ping -n 1 -4 "%computername%"') do @echo %a""")
else:
    local = subprocess.getoutput("ifconfig | grep 'inet' | grep -Fv 127.0.0.1 | awk '{print $2}'")
print(local)
print(platform.node())
print(platform.machine())
print(platform.processor())