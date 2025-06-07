# Usar imagen base de nginx (ligero y rápido)
FROM nginx:alpine

# Información del mantenedor (puedes personalizar)
LABEL maintainer="tu-nombre <jmunoz18709@plataforma-utslp.net>"

# Copiar el archivo index.html a la ruta donde nginx sirve el contenido
COPY index.html /usr/share/nginx/html/

# Exponer el puerto 80 para HTTP
EXPOSE 80

# Ejecutar nginx en primer plano (modo daemon off)
CMD ["nginx", "-g", "daemon off;"]
