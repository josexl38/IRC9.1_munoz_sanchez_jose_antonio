#!/bin/bash

# Definir las URLs a comprobar
declare -a urls=("https://uvm.mx/" "https://upotosina.edu.mx/" "https://moodle.plataforma-utslp.net/")

# Definir nombres de archivos
csv_file="urls.csv"
json_file="urls.json"
yml_file="urls.yml"
xml_file="urls.xml"

# Limpiar los archivos antes de escribir
echo "URL,STATUS" > "$csv_file"
echo "[" > "$json_file"
echo "" > "$yml_file"
echo "<urls>" > "$xml_file"

# Iterar sobre cada URL
for url in "${urls[@]}"; do
    status=$(curl -m 10 -s -o /dev/null -w "%{http_code}" "$url")

    # CSV
    echo "$url,$status" >> "$csv_file"

    # JSON
    echo "  {\"url\": \"$url\", \"status\": \"$status\"}," >> "$json_file"

    # YAML
    echo "- url: $url" >> "$yml_file"
    echo "  status: $status" >> "$yml_file"

    # XML
    echo "  <url>" >> "$xml_file"
    echo "    <link>$url</link>" >> "$xml_file"
    echo "    <status>$status</status>" >> "$xml_file"
    echo "  </url>" >> "$xml_file"
done

# Cerrar JSON correctamente (quitando la última coma)
sed -i '$ s/,$//' "$json_file"
echo "]" >> "$json_file"

# Cerrar XML
echo "</urls>" >> "$xml_file"

# Mostrar archivos generados
echo "Archivos generados:"
ls -l urls.*
