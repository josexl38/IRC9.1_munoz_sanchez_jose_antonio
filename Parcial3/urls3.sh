#!/bin/bash

declare -a urls=("https://uvm.mx/" "https://upotosina.edu.mx/" "https://moodle.plataforma-utslp.net/")

file=ursl.csv
printf "%s$(date)\n" > "$file"

for url in "${urls[@]}"; do
        status=$(curl -m 10 -s -I $url | head -n 1 | awk '{print $2}')
        printf "$url,$status\n" >> "$file"

done
column -s, -t "$file"
