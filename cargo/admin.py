from django.contrib import admin
# Aqui lo que necesito es crear una clase que me permita ver en el admin de Django a que Grupo (Drivers, Managers) pertenece cada usuario.
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    # Agregar 'groups_display' a la lista de columnas
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'groups_display')

    # Método para mostrar los grupos como string (ej: "Managers, Drivers")
    def groups_display(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    
    groups_display.short_description = 'Grupos'  # short_description personaliza el título de la columna.

# Desregistrar el UserAdmin por defecto y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

