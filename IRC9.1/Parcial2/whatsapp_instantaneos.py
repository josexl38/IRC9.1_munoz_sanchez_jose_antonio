import pywhatkit
import time

numero = "+524441698269"  
mensaje = "Este es un mensaje automático"

while True:
    try:
        pywhatkit.sendwhatmsg_instantly(numero, mensaje)
        print(f"Mensaje enviado a {numero}")
        
        time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
        break  

