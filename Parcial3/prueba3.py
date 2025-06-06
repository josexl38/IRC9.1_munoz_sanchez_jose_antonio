import requests

# URL base de la API
base_url = "http://127.0.0.1:8000"

# 1️⃣ LOGIN para obtener el token
login_url = f"{base_url}/api/login"
credentials = {"username": "usuario1", "password": "password123"}
login_response = requests.post(login_url, json=credentials)

if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    print("✅ Login exitoso. Token obtenido.")

    # 2️⃣ OBTENER PERFIL usando el token
    profile_url = f"{base_url}/api/profile"
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_response = requests.get(profile_url, headers=headers)
    
    if profile_response.status_code == 200:
        print("✅ Perfil obtenido correctamente:", profile_response.json())
    else:
        print("❌ Error al obtener el perfil:", profile_response.text)
else:
    print("❌ Error en el login:", login_response.text)
