from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.apps import apps


def crear_roles(sender, **kwargs):
    # Define los grupos y los permisos asociados
    roles = {
        'empleado': ['add_miembro', 'change_miembro', 'view_miembro', 'add_historialmedico', 'change_historialmedico','view_historialmedico','add_historialdeportivo', 'change_historialdeportivo','view_historialdeportivo'],
        'miembro': ['view_miembro', 'view_historialmedico','view_historialdeportivo']
    }
    
    for rol_nombre, permisos_codenames in roles.items():
        rol, creado = Group.objects.get_or_create(name=rol_nombre)
        for codename in permisos_codenames:
            try:
                permiso = Permission.objects.get(codename=codename)
                rol.permissions.add(permiso)
            except Permission.DoesNotExist:
                print(f"Permiso {codename} no encontrado. Asegúrate de que los permisos existen.")

# Conectar la señal post_migrate para ejecutar la función después de cada migración
post_migrate.connect(crear_roles, sender=apps.get_app_config('login'))