from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django import forms
from .models import TruckDriver, Truck, TruckTrip
from django.utils import timezone
from django.core.exceptions import ValidationError


# Formulario GENERAL de registro de usuario, en el principio.
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False, label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Correo Electróncio'}))
    
    first_name = forms.CharField(max_length=30, required=False, label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nombre'}))
    
    last_name = forms.CharField(max_length=30, required=True, label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Apellido'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>No sea bobo: elija una clave diferente de cualquiera de sus otros datos personales.</li><li>Debe tener al menos 8 caracteres.</li><li>No puede ser una clave común o facil de acceder, por ejemplo, no use la palabra -password- </li><li>La clave no puede ser completamente numerica</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmar Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Repita la password que escribió antes, a modo de verificación.</small></span>'


# formulario usado por el manager para registrar conductores.
class DriverRegistrationForm(forms.ModelForm):
    # Campos personalizados (solo los que NO están en User)
    address = forms.CharField(
        max_length=255, 
        required=False, 
        label="Dirección",
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Av. Lavalleja 742'})
    )
    license_number = forms.CharField(
        max_length=20, 
        label="No. Documento (Cédula de Identidad)",
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 12345678'})
    )
    cell_number = forms.CharField(
        max_length=15, 
        required=False, 
        label="Número de Celular",
        widget=forms.TextInput(attrs={'placeholder': 'Ej: +598 12 345678'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name') # quitamos password1 y password2 porque la password inicial va a ser 'holamaquina' para todos los conductores.

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)  # ¡Extrae el usuario aquí!
        super().__init__(*args, **kwargs)
        # Aplicar estilos Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # Placeholders personalizados
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Ej: juanperez'
            elif field_name == 'email':
                field.widget.attrs['placeholder'] = 'Ej: juan@example.com'
            elif field_name == 'first_name':
                field.widget.attrs['placeholder'] = 'Ej: Juan'
            elif field_name == 'last_name':
                field.widget.attrs['placeholder'] = 'Ej: Pérez'
    # --- Validaciones personalizadas ---
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if license_number and TruckDriver.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("Ya existe un conductor con este número de documento.")
        return license_number

    def clean_cell_number(self):
        cell_number = self.cleaned_data.get('cell_number')
        if cell_number and TruckDriver.objects.filter(cell_number=cell_number).exists():
            raise forms.ValidationError("Ya existe un conductor con este número de celular.")
        return cell_number

    # aque vamos con la contraseña fija 'holamaquina'
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password('holamaquina')  # Contraseña fija
        if commit:
            user.save()
            # Asignar al grupo 'Drivers'
            drivers_group = Group.objects.get(name='Drivers')
            user.groups.add(drivers_group)
            # Crear el perfil TruckDriver
            TruckDriver.objects.create(
                user=user,
                created_by=self.current_user,  # pasamos el Manager al form
                address=self.cleaned_data.get('address'),
                license_number=self.cleaned_data['license_number'],
                cell_number=self.cleaned_data.get('cell_number')
            )
        return user


# formulario usado por el manager para cargar vehiculos (trucks).
class TruckForm(forms.ModelForm):
    driver = forms.ModelChoiceField(
        queryset=TruckDriver.objects.none(),
        required=False,
        label="Conductor (opcional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Truck
        fields = ['plate_number', 'driver', 'brand', 'moddel', 'year', 'mileage'] 
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ABC-1234'}),
            'moddel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Modelo XYZ'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Volvo'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2030'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Kilometraje'}),
        }

    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        
        if self.manager:
            self.fields['driver'].queryset = TruckDriver.objects.filter(
                created_by=self.manager
            ).select_related('user')
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        print(f"Usuario asignado: {self.manager}") # debugging
        truck = super().save(commit=False)
        truck.registration_date = timezone.now().date()  # Fecha actual automática
        truck.is_available = True  # Siempre disponible al crearse
        # asigna el manager actual al camión que se está creando.
        truck.created_by = self.manager  # acá NO usamos self.current_user para ser consistentes.
        print(f"Truck antes de guardar - created_by: {truck.created_by}") # debugging
        if commit:
            truck.save()
        return truck

    def clean_plate_number(self):
        plate = self.cleaned_data['plate_number']
        if Truck.objects.filter(plate_number__iexact=plate).exists():
            raise ValidationError("¡Esta matrícula ya está registrada!")
        return plate.upper()


# formulario usado por el conductor o driver para registrar el inicio de un viaje.
class TruckDutyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Buscar el TruckDriver asociado al user
            try:
                driver = TruckDriver.objects.get(user=user)
                manager = driver.created_by  # El manager que lo creó

                # Mostrar solo los camiones creados por ese manager
                self.fields['truck'].queryset = Truck.objects.filter(
                    is_available=True,
                    created_by=manager
                )
            except TruckDriver.DoesNotExist:
                self.fields['truck'].queryset = Truck.objects.none()  # Nada si no es driver

    class Meta:
        model = TruckTrip
        fields = ['truck', 'mileage', 'load_type', 'load_location']

    truck = forms.ModelChoiceField(
        queryset=Truck.objects.none(),
        label='Vehículo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    mileage = forms.IntegerField(
        label='Kilometraje',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Ingrese el kilometraje actual del vehículo.'
    )

    load_type = forms.ChoiceField(
        choices=TruckTrip.LOAD_TYPES,
        label='Tipo de Carga',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    load_location = forms.ChoiceField(
        choices=TruckTrip.LOAD_LOCATIONS,
        label='Lugar de Carga',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Setea fecha y hora del inicio del viaje
        instance.date = timezone.now().date()
        instance.end_load_time = timezone.now().time()

        if commit:
            instance.save()

            # Actualiza el kilometraje actual del camión si es diferente del que ya tiene.
            truck = instance.truck
            if instance.mileage > truck.mileage:
                truck.mileage = instance.mileage
                truck.save()

        return instance


# La vista fuel_register es un formulario que permite kilometraje (mileage), litros (en el modelo, va al campo fuel_loaded_liters) e importe (fuel_loaded_amount en el modelo).
class FuelRegisterForm(forms.ModelForm):
    class Meta:
        model = TruckTrip
        fields = ['mileage', 'fuel_loaded_liters', 'fuel_loaded_amount']
        widgets = {
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_loaded_liters': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_loaded_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'mileage': 'Kilometraje actual',
            'fuel_loaded_liters': 'Litros cargados',
            'fuel_loaded_amount': 'Importe total ($)',
        }


# parte final: descarga, con la vista unload_register. Aqui, el driver eligirá el lugar de descarga entre las opciones que tenía en el modelo. También, tomará el último kilometraje que haya guardado. Si cargó combustible en el camino, tomará el kilometraje que registró en esa carga. Si no cargó combustible, tomará el kilometraje que registró cuando inició el viaje.
class UnloadRegisterForm(forms.ModelForm):
    class Meta:
        model = TruckTrip
        fields = ['mileage', 'unload_location']
        widgets = {
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'unload_location': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'mileage': 'Kilometraje Final',
            'unload_location': 'Lugar de Descarga',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
