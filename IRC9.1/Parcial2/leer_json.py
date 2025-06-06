import json

file_name = "data.json"

with open(file_name) as data:
    datos = json.load(data)

print(datos["so"]+"\n"+datos["hostname"]+"\n"+datos["ip"]+"\n"+datos["version"][0])