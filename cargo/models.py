from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Definición de los modelos para la aplicación de gestión de camiones
# 3 modelos: TruckDriver (conductores), Trucks (vehículos) y TruckTrips (viajes).

class TruckDriver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='truck_driver', verbose_name='Condcutor')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_drivers')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección')
    license_number = models.CharField(max_length=20, unique=True, verbose_name='Cédula de Identidad')
    cell_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Número de Celular (formato: 09XXXXXXX)')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Conductor de Camión'
        verbose_name_plural = 'Conductores de Camión'

    def __str__(self):
        return self.user.username

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def email(self):
        return self.user.email  # Acceso directo al email del User


class Truck(models.Model):
    plate_number = models.CharField(max_length=15, unique=True, verbose_name='Número de Matrícula')
    driver = models.ForeignKey(
        TruckDriver, 
        on_delete=models.SET_NULL, 
        related_name='trucks', 
        null=True,
        blank=True, 
        verbose_name='Conductor'
        )
    moddel = models.CharField(max_length=50, verbose_name='Modelo')
    brand = models.CharField(max_length=50, verbose_name='Marca')
    year = models.PositiveIntegerField(verbose_name='Año de Fabricación')
    capacity = models.CharField(max_length=50, blank=True, null=True, verbose_name='Capacidad de Carga')
    registration_date = models.DateField(verbose_name='Fecha de Inicio de Actividades')
    last_maintenance = models.DateField(blank=True, null=True, verbose_name='Último Mantenimiento')
    # Este campo (total_fuel_consumption) se actualizará con la suma de las cargas de combustible que se vayan reportando en los sucesivos viajes, en TruckTrips.
    total_fuel_consumption = models.FloatField(default=0.0, verbose_name='Consumo Total de Combustible (Litros)') 
    # is_available indica si el camión está disponible para ser asignado a un viaje. La idea es que si dejo de usar un camión, por el motivo que sea, los viajes asociados a ese camión no se eliminen.
    is_available = models.BooleanField(default=True, verbose_name='Disponible')
    # Este campo es para saber que usuario (manager) agregó el camión al sistema.
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Agregado por",
        related_name='truck_added_by'
    )
    mileage = models.PositiveIntegerField(verbose_name='Kilometraje')

    class Meta:
        verbose_name = 'Camión'
        verbose_name_plural = 'Camiones'
        ordering = ['plate_number']  # Ordeno la lista de camiones por el número de matrícula.

    def __str__(self):
        return f"{self.brand} {self.moddel} ({self.plate_number})"


class TruckTrip(models.Model):
    date = models.DateField(default=timezone.now, verbose_name='Fecha del Viaje')
    end_load_time = models.TimeField(default=timezone.now, verbose_name='Hora de Finalización de Carga')
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='trips', verbose_name='Camión')

    driver = models.ForeignKey(
    TruckDriver,
    on_delete=models.SET_NULL, # si algún día se un conductor, los viajes no se borran.
    null=True,
    blank=False,
    related_name='trips',
    verbose_name='Conductor'
)

    # Lista de los tipos de carga
    LOAD_TYPES = [
        ('A', 'Carga A'),
        ('B', 'Carga B'),
        ('C', 'Carga C'),
    ]
    load_type = models.CharField(max_length=1, choices=LOAD_TYPES, verbose_name='Tipo de Carga')

    # Lista de los lugares de carga
    LOAD_LOCATIONS = [
        ('LA', 'Lugar A'),
        ('LB', 'Lugar B'),
        ('LC', 'Lugar C'),
    ]
    load_location = models.CharField(max_length=2, choices=LOAD_LOCATIONS, verbose_name='Lugar de Carga')
    
    # Lista de los lugares de descarga
    UNLOAD_LOCATIONS = [
        ('D1', 'Descarga 1'),
        ('D2', 'Descarga 2'),
        ('D3', 'Descarga 3'),
    ]
    unload_location = models.CharField(max_length=2, choices=UNLOAD_LOCATIONS, verbose_name='Lugar de Descarga')
    unload_time = models.DateTimeField(default=timezone.now, verbose_name='Hora de Descarga')
    initial_mileage = models.PositiveIntegerField(default=0, verbose_name='Kilometraje al Iniciar Viaje')
    mileage = models.PositiveIntegerField(verbose_name='Kilometraje al Cargar Combustible')
    fuel_loaded_liters = models.FloatField(null=True, blank=True, verbose_name='Carga Combustible (Litros)')
    fuel_loaded_amount = models.FloatField(null=True, blank=True, verbose_name='Carga Combustible (Importe)')

    class Meta:
        verbose_name = 'Viaje de Camión'
        verbose_name_plural = 'Viajes de Camiones'
        ordering = ['-date', '-end_load_time']  # Orden predeterminado por fecha y hora descendente

    def __str__(self):
        return f"Viaje de {self.truck.brand} {self.truck.model} el {self.date}"