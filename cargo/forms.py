from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django import forms
from .models import TruckDriver # Importamos el modelo TruckDriver

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
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Repita la password que escribió antes, a modo de verificación.</small></span>'

'''
class DriverRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label="Nombre", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nombre'}))
    last_name = forms.CharField(max_length=30, label="Apellido", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Apellido'}))
    email = forms.EmailField(max_length=254, label="Correo Electrónico", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Correo Electrónico'}))
    address = forms.CharField(max_length=255, required=False, label="Dirección", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Dirección'}))
    license_number = forms.CharField(max_length=20, label="No. Documento (Cédula de Identidad)", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Cédula de Identidad'}))
    cell_number = forms.CharField(max_length=15, required=False, label="Número de Celular", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Número de Celular'}))

    class Meta(UserCreationForm.Meta):
        model = User
        # Solo los campos del User necesarios para el registro de la cuenta
        fields = ('username', 'password', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilos y placeholders a los campos de UserCreationForm
        self.fields['username'].label = "Usuario"
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de Usuario'
        self.fields['username'].help_text = '' # Limpiamos el help_text por defecto si no lo queremos

        self.fields['password'].label = "Contraseña"
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Contraseña'
        self.fields['password'].help_text = '' # Puedes personalizarlo si quieres

        self.fields['password2'].label = "Confirmar Contraseña"
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Repetir Contraseña'
        self.fields['password2'].help_text = '' # Puedes personalizarlo si quieres

    # valido el número de documento y el número de celular solamente
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if license_number and TruckDriver.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("Ya existe un conductor con este número de documento.")
        return license_number

    def clean_cell_number(self):
        cell_number = self.cleaned_data.get('cell_number')
        # Solo validar unicidad si el campo no es nulo o vacío
        if cell_number and TruckDriver.objects.filter(cell_number=cell_number).exists():
            raise forms.ValidationError("Ya existe un conductor con este número de celular.")
        return cell_number

    def save(self, commit=True):
        # 1. Crear el usuario de Django (User)
        user = super().save(commit=False)
        if commit:
            user.save()

            # Asignar el usuario al grupo 'Drivers' directamente
            # Eliminamos el try-except porque el grupo siempre existe
            drivers_group = Group.objects.get(name='Drivers')
            user.groups.add(drivers_group)

            # 2. Crear y guardar el objeto TruckDriver
            truck_driver_profile = TruckDriver.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                address=self.cleaned_data.get('address'),
                license_number=self.cleaned_data['license_number'],
                cell_number=self.cleaned_data.get('cell_number')
            )
            return user
        return user
'''

class DriverRegistrationForm(forms.ModelForm): # antes heredado de UserCreationForm.
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
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 1.234.567-8'})
    )
    cell_number = forms.CharField(
        max_length=15, 
        required=False, 
        label="Número de Celular",
        widget=forms.TextInput(attrs={'placeholder': 'Ej: +598 12 345678'})
    )

    #class Meta(UserCreationForm.Meta):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name') # quitamos password1 y password2 porque la password inicial va a ser 'holamaquina' para todos los conductores.
        
        '''
        labels = {
            'username': 'Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }
        help_texts = {
            'username': '',
            'password1': '',
            'password2': '',
        }
        '''
        
# (Eliminado bloque comentado que causaba error de indentación)

    def __init__(self, *args, **kwargs):
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
        #user.email = self.cleaned_data['email']  # Asegurar que el email se guarde
        user.set_password('holamaquina')  # Contraseña fija (ver si está encriptada)
        if commit:
            user.save()
            # Asignar al grupo 'Drivers'
            drivers_group = Group.objects.get(name='Drivers')
            user.groups.add(drivers_group)
            # Crear el perfil TruckDriver (sin campos redundantes)
            TruckDriver.objects.create(
                user=user,
                address=self.cleaned_data.get('address'),
                license_number=self.cleaned_data['license_number'],
                cell_number=self.cleaned_data.get('cell_number')
            )
        return user