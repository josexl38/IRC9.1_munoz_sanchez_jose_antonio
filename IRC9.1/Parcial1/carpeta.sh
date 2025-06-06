#!/bin/bash

read -p "Introduce el nombre de la carpeta que deseas buscar: " NOMBRE_CARPETA

ARCHIVO="archivo.txt"
FECHA=$(date +%Y-%m-%d)

echo "Buscando la carpeta '$NOMBRE_CARPETA' en el sistema..."
CARPETA=$(find / -type d -name "$NOMBRE_CARPETA" 2>/dev/null)

if [ -z "$CARPETA" ]; then
  echo "La carpeta '$NOMBRE_CARPETA' no existe. Creándola en el directorio home..."
  CARPETA="$NOMBRE_CARPETA"
  mkdir -p "$CARPETA"
  echo "Carpeta creada en: $CARPETA"
else
  echo "La carpeta '$NOMBRE_CARPETA' ya existe en: $CARPETA"
fi

ARCHIVO_COMPLETO="$CARPETA/$ARCHIVO"
BACKUP="$CARPETA/${ARCHIVO%.txt}_$FECHA.txt"

if [ ! -f "$ARCHIVO_COMPLETO" ]; then
  echo "El archivo '$ARCHIVO' no existe. Creándolo..."
  echo "Este es un archivo de prueba" > "$ARCHIVO_COMPLETO"
  echo "Archivo creado en: $ARCHIVO_COMPLETO"
else
  echo "El archivo '$ARCHIVO' ya existe."

  echo "Creando backup del archivo existente..."
  cp "$ARCHIVO_COMPLETO" "$BACKUP"
  echo "Backup creado con el nombre: $BACKUP"
fi

echo "Script finalizado."

