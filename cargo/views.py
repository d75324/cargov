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
import csv
from django.http import HttpResponse


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

    # Obtener todos los viajes que pertenecen a los camiones del manager
    trips = TruckTrip.objects.filter(
        truck__created_by=request.user,
        mileage__isnull=False  # Solo viajes completados
    ).select_related('truck', 'truck__driver', 'truck__driver__user')\
     .order_by('-date')

    # Calcular distancia recorrida y agregarla dinámicamente
    for trip in trips:
        trip.distance = (trip.mileage or 0) - (trip.initial_mileage or 0)

    context = {
        'drivers': drivers,
        'trucks': trucks,
        'trips': trips,
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
            user = form.save()  # Guarda el usuario y lo retorna
            # Autenticar y loguear al usuario
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # lo asignamos automáticamente al grupo "Managers"
                try:
                    group = Group.objects.get(name='Managers')  # para estar seguros que existe
                    user.groups.add(group)
                except Group.DoesNotExist:
                    messages.error(request, 'El grupo "Managers" no existe.')
                    return render(request, 'register.html', {'form': form})
                
                messages.success(request, '¡Usuario registrado correctamente!')
                return redirect('index')
            else:
                messages.error(request, 'Error al autenticar después del registro.')
                return render(request, 'register.html', {'form': form})
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

# formulario usado por el manager para agregar un nuevo conductor.
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
@login_required
def register_trip(request):
    if request.method == 'POST':
        form = TruckDutyForm(request.POST, user=request.user)
        if form.is_valid():
            trip = form.save(commit=False)
            truck = trip.truck
            trip.initial_mileage = truck.mileage  # Guardamos el kilometraje inicial del camión al momento de iniciar el viaje.

            # Asignamos el conductor al viaje
            try:
                trip.driver = TruckDriver.objects.get(user=request.user)
            except TruckDriver.DoesNotExist:
                trip.driver = None  # podría acá colocar un mensaje de error

            trip.save()
            return redirect('travel_actions', trip_id=trip.id)
    else:
        form = TruckDutyForm(user=request.user)

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

    # Guardar el valor de kilometraje del camión ANTES de modificarlo
    initial_mileage = trip.initial_mileage  # Este sí es fijo, lo guardé al crear el viaje
    final_mileage = trip.mileage
    if final_mileage:
        distance = final_mileage - initial_mileage
    else:
        distance = 0

    context = {
        'trip': trip,
        'initial_mileage': initial_mileage,
        'final_mileage': final_mileage,
        'distance': distance
    }

    if final_mileage and final_mileage > trip.truck.mileage:
        trip.truck.mileage = final_mileage
        trip.truck.save()

    return render(request, 'truckduties/travel_summary.html', context)


# creamos la vista para exportar los viajes a CSV.
@login_required
def download_report(request):
    # Obtener los viajes del manager
    trips = TruckTrip.objects.filter(
        truck__created_by=request.user,
        mileage__isnull=False
    ).select_related('truck', 'truck__driver', 'truck__driver__user').order_by('-date')

    # Creamos la respuesta HTTP con cabeceras para descargar CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_viajes.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Fecha',
        'Vehículo',
        'Conductor',
        'Tipo de Carga',
        'Lugar de Carga',
        'Fecha Descarga',
        'Lugar de Descarga',
        'Kilometraje Final',
        'Distancia Recorrida',
        'Litros Cargados',
        'Importe',
        'Extra'
    ])

    for trip in trips:
        writer.writerow([
            trip.date.strftime('%Y-%m-%d'),
            trip.truck.plate_number,
            trip.driver.user.get_full_name() if trip.driver else '',
            trip.get_load_type_display(),
            trip.get_load_location_display(),
            trip.unload_time.strftime('%Y-%m-%d %H:%M') if trip.unload_time else '',
            trip.get_unload_location_display() if trip.unload_location else '',
            trip.mileage or '',
            (trip.mileage or 0) - (trip.initial_mileage or 0),
            trip.fuel_loaded_liters if hasattr(trip, 'fuel_loaded_liters') else '',
            trip.fuel_loaded_amount if hasattr(trip, 'fuel_loaded_amount') else '',
            trip.extra if hasattr(trip, 'extra') else '',
        ])

    return response


