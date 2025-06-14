from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import SignUpForm
from .forms import DriverRegistrationForm


# Create your views here.
def index(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Acceso Exitoso')
                if user.groups.filter(name='Managers').exists():
                    return redirect('report')  # si es manager redirecciona a report.html
                elif user.groups.filter(name='Drivers').exists():
                    return redirect('landing')    # si es un conductor redirecciona a landing.html
            else:
                # si no es ninguno me manda a index. 
                return redirect('index')
        else:
            # Manejar el caso de credenciales incorrectas
            return render(request, 'index.html')
        return render(request, 'index.html')

@login_required
def report(request):
    return render(request, 'report.html')

@login_required
def landing(request):
    return render(request, 'truckduties/landing.html')

def login_user(request):
    pass

def logout_user(request):
    # Limpiar mensajes previos para que no aparezcan en la siguiente página
    storage = messages.get_messages(request)
    for message in storage:
        pass  # Esto vacía la lista de mensajes
    logout(request)
    messages.success(request, 'Adios!')
    return redirect('index')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # authenticate y login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password) # Necesitas pasar 'request' como primer argumento
            if user is not None:
                login(request, user)
                # Asignar el grupo según el tipo de usuario
                user_type = form.cleaned_data['user_type']
                try:
                    if user_type == 'Conductores':
                        group = Group.objects.get(name='Drivers')
                    elif user_type == 'Administrador':
                        group = Group.objects.get(name='Managers')
                    if group:
                        user.groups.add(group)
                except Group.DoesNotExist:
                    messages.error(request, f'El grupo "{user_type}" no existe.')
                    return render(request, 'register.html', {'form': form}) # Re-renderizar con el formulario y el error
                messages.success(request, 'Usuario creado exitosamente!')
                return redirect('index')
            else:
                messages.error(request, 'Error al iniciar sesión después del registro.')
                return render(request, 'register.html', {'form': form}) # Re-renderizar con el formulario y el error
        else:
            return render(request, 'register.html', {'form': form}) # Re-renderizar el formulario con errores
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form}) # Pasar el formulario al template en la petición GET 

def add_driver(request):
    if request.method == 'POST':

        # --- MUY IMPORTANTE: Imprime los datos POST ---
        print("--- Datos POST recibidos ---")
        for key, value in request.POST.items():
            if "password" in key: # Para no imprimir contraseñas en texto plano en la consola
                print(f"{key}: {'*****'}")
            else:
                print(f"{key}: {value}")
        print("----------------------------")
        # --- Fin de la impresión POST ---

        form = DriverRegistrationForm(request.POST)
        if form.is_valid():
            form.save() # El método save del formulario se encarga de crear el User y el TruckDriver
            messages.success(request, '¡Conductor agregado exitosamente!')
            # Redirige a la página principal o a una lista de conductores
            return redirect('index') # O 'drivers_list' si la tienes
        else:
            print("Errores del formulario:", form.errors)
            # Si el formulario no es válido, vuelve a renderizar con los errores
            messages.error(request, 'Por favor, revisa el formulario.')
            return render(request, 'truckduties/add_driver.html', {'form': form})
    else:
        form = DriverRegistrationForm() # Crea un formulario vacío para la petición GET
    return render(request, 'truckduties/add_driver.html', {'form': form})