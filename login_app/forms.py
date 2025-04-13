from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, Cita
from django.contrib.auth import get_user_model

User = get_user_model()
class CustomAuthenticationForm(AuthenticationForm):
    pass  # Usamos el formulario de Django sin cambios

class UsuarioForm(UserCreationForm):
    nombre_completo = forms.CharField(max_length=255, required=True, label="Nombre Completo")
    numero_documento = forms.CharField(max_length=20, required=True, label="Número de Documento")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True, label="Rol")

    class Meta:
        model = CustomUser
        fields = ["nombre_completo", "username", "numero_documento", "email", "password1", "password2", "role"]

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ["dentista", "fecha", "hora", "motivo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "dentista": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(CitaForm, self).__init__(*args, **kwargs)
        self.fields["dentista"].queryset = User.objects.filter(role="dentista")  # Filtra solo los dentistas