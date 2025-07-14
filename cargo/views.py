from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import SignUpForm, DriverRegistrationForm, TruckForm, TruckDutyForm, FuelRegisterForm, UnloadRegisterForm
from django.core.paginator import Paginator
from .models import TruckDriver, Truck, TruckTrip
from django.http import JsonResponse
#from .models import TruckDuty



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
                    return redirect('register_trip')    # si es un conductor redirecciona a register_trip para comenzar un viaje.
            else:
                # si no es ninguno me manda a index. 
                return redirect('index')
        else:
            # Manejar el caso de credenciales incorrectas
            return render(request, 'index.html')
        return render(request, 'index.html')


@login_required
def report(request):
    # Obtener conductores y vehículos del manager actual
    drivers = TruckDriver.objects.filter(
        created_by=request.user
    ).select_related('user')
    
    trucks = Truck.objects.filter(
        created_by=request.user
    ).select_related('driver__user')  # Optimiza la consulta del conductor
    
    context = {
        'drivers': drivers,
        'trucks': trucks,
        'total_trucks': trucks.count()
    }
    return render(request, 'report.html', context)


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

        # --- Imprime los datos POST ---
        print("--- Datos POST recibidos ---")
        for key, value in request.POST.items():
            if "password" in key: # Para no imprimir contraseñas en texto plano en la consola
                print(f"{key}: {'*****'}")
            else:
                print(f"{key}: {value}")
        print("----------------------------")
        # --- Fin de la impresión POST ---

        # pasamos el usuario actual al formulario.
        form = DriverRegistrationForm(request.POST, current_user=request.user)  
        if form.is_valid():
            form.save() # El método save del formulario se encarga de crear el User y el TruckDriver
            messages.success(request, '¡Conductor agregado exitosamente!')
            # Redirige a la página principal o a una lista de conductores
            return redirect('report')
        else:
            print("Errores del formulario:", form.errors)
            # Si el formulario no es válido, vuelve a renderizar con los errores
            messages.error(request, 'Por favor, revisa el formulario.')
            return render(request, 'truckduties/add_driver.html', {'form': form})
    else:
        form = DriverRegistrationForm() # Crea un formulario vacío para la petición GET
    return render(request, 'truckduties/add_driver.html', {'form': form})


@login_required
def list_drivers(request):
    # Filtrar solo los Drivers creados por el Manager actual
    drivers = TruckDriver.objects.filter(
        user__groups__name='Drivers',  # Asegura que son Drivers
        created_by=request.user  # Asume que hay un campo 'created_by' en TruckDriver
    ).select_related('user')  # Optimiza la consulta
    
        # Asegúrate de pasar 'drivers' al contexto
    return render(request, 'report.html', {
        'drivers': drivers
    })


@login_required
def add_truck(request):
    if request.method == 'POST':
        form = TruckForm(request.POST, manager=request.user)
        if form.is_valid():
            form.save()
            return redirect('report')
    else:
        form = TruckForm(manager=request.user)
    
    return render(request, 'truckduties/add_truck.html', {'form': form})


@login_required
def list_trucks(request):
    # Filtra vehículos del manager actual, en base al campo created_by del modelo Truck
    trucks = Truck.objects.filter(
        created_by=request.user
    ).select_related('driver__user')  # Optimiza consultas a conductor
    
    # Filtros adicionales (opcionales)
    is_available = request.GET.get('is_available')
    if is_available == 'true':
        trucks = trucks.filter(is_available=True)
    elif is_available == 'false':
        trucks = trucks.filter(is_available=False)
    
    context = {
        'trucks': trucks,
        'total_trucks': trucks.count(),
    }
    return render(request, 'report.html', context)


# esta es la vista que inicia un viaje. 
# el usuario (driver) completa el formulario y en el momento que lo confirma, se crea un nuevo track_id y un nuevo viaje.
def register_trip(request):
    if request.method == 'POST':
        form = TruckDutyForm(request.POST)
        if form.is_valid():
            trip = form.save()
            # Si el formulario está ok, redirigimos travel.html.
            return redirect('travel_actions', trip_id=trip.id)  # Este es travel.html, donde voy a poder 'descargar la carga' o 'cargar combustible'
    else:
        form = TruckDutyForm()

    # si el formulario no es válido, volvemos a renderizar con los errores.
    return render(request, 'truckduties/register_trip.html', {'form': form})


# travel_actions es la vista donde tengo la opción de descargar la carga o cargar combustible.
def travel_actions(request, trip_id):
    trip = get_object_or_404(TruckTrip, id=trip_id)
    return render(request, 'travel.html', {'trip': trip})


# Necesito que cada vez que cargo un camión, traiga también el kilometraje del mismo.
# para eso, voy a usar JavaScript y una vista de Django.
# Entonces, creamos una vista AJAX (Asynchronous JavaScript and XML) que recibe el ID del camión
# y devuelve su kilometraje en formato JSON:
def get_truck_mileage(request):
    truck_id = request.GET.get('truck_id')
    try:
        truck = Truck.objects.get(pk=truck_id)
        return JsonResponse({'mileage': truck.mileage})
    except Truck.DoesNotExist:
        return JsonResponse({'error': 'Camión no encontrado'}, status=404)


# estamos en la vista travel_actions. Hasta ahora, se seleccionó el vehículo, el tipo y 
# lugar de carga. Ahora, con esta vista, pasamos a la parte donde el conductor podrá
# cargar combustible (fuel_register, si es requerido) o sinó proceder a la descarga (unload_register)
# y completar el viaje.
# las URL para estas vistas, ya van a tener asociado un <int:trip_id>, que va a ser el ID del viaje.


def travel_actions(request, trip_id):
    trip = get_object_or_404(TruckTrip, id=trip_id)
    return render(request, 'truckduties/travel-actions.html', {'trip': trip})


# vista para la carga de combustible.
def fuel_register(request, trip_id):
    trip = get_object_or_404(TruckTrip, id=trip_id)

    if request.method == 'POST':
        form = FuelRegisterForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            # Si el form es válido, redireccionamos al paso siguiente, que es descarga
            return redirect('unload_register', trip_id=trip.id)
    else:
        # muestra el formulario vacío, pero cargado con la instancia actual
        form = FuelRegisterForm(instance=trip)

    return render(request, 'truckduties/fuel_register.html', {'form': form, 'trip': trip})


# vista para la descarga de la carga.
def unload_register(request, trip_id):
    trip = get_object_or_404(TruckTrip, id=trip_id)

    if request.method == 'POST':
        form = UnloadRegisterForm(request.POST, instance=trip)
        if form.is_valid():
            updated_trip = form.save(commit=False)

            # Distancia: por ahora solo mostramos los valores, después veré que hago.
            initial_mileage = trip.mileage or 0
            final_mileage = form.cleaned_data.get('mileage') or 0
            distance = max(final_mileage - initial_mileage, 0)
            updated_trip.save()

            messages.success(request, f"Descarga registrada. Distancia recorrida: {distance} km.")
            return redirect('travel_summary', trip_id=trip.id)
    else:
        form = UnloadRegisterForm(instance=trip)

    return render(request, 'truckduties/unload_register.html', {
        'form': form,
        'trip': trip,
    })

# vista para el resumen del viaje.
def travel_summary(request, trip_id):
    trip = get_object_or_404(TruckTrip, id=trip_id)

    # Distancia recorrida: final - inicial
    distance = max((trip.mileage or 0) - trip.truck.mileage, 0)

    return render(request, 'truckduties/travel_summary.html', {
        'trip': trip,
        'distance': distance
    })

