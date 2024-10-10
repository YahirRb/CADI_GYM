import firebase_admin
from firebase_admin import credentials, storage
"""
cred = credentials.Certificate("credentials.json")
# Inicializa la aplicación con las credenciales y el bucket
firebase_admin.initialize_app(cred, {
    'storageBucket': 'cadi-minatitlan.appspot.com'  # Especifica tu bucket aquí
})

# Obtiene el bucket
bucket = storage.bucket()  # Ya no necesitas pasar el nombre aquí
"""