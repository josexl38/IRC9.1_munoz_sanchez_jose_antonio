#!/bin/bash 

# Archivo de log
LOG_FILE="/var/log/ssh_commands.log"

# Obtener usuario y fecha de inicio de sesión
USER_SESSION=$(whoami)
SESSION_START=$(date "+%Y-%m-%d %H:%M:%S")

# Escribir inicio de sesión en el log
echo "=== Nueva sesión SSH de $USER_SESSION iniciada en $SESSION_START ===" >> "$LOG_FILE"

# Registrar comandos ejecutados
HISTFILE=~/.bash_history
touch "$HISTFILE"
tail -f "$HISTFILE" | while read CMD; do
    # Filtrar líneas vacías y repeticiones
    if [[ ! -z "$CMD" ]]; then
        TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
        echo "$TIMESTAMP - $USER_SESSION ejecutó: $CMD" >> "$LOG_FILE"
    fi
done &

# Al cerrar sesión, escribir mensaje en el log
trap "echo '=== Sesión SSH de $USER_SESSION finalizada en $(date "+%Y-%m-%d %H:%M:%S") ===' >> $LOG_FILE" EXIT