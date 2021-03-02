from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from studentLab.studentLabFacade import EstudianteDataFacade as EstudianteData

class LoginForm(forms.Form):
    user = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    def getCleanedData(self):
        return self.cleaned_data

class RegisterForm(forms.Form):
    code = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    semester = forms.IntegerField(required=True)
    course = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput, validators=[validate_password])
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput)

    def getCleanedData(self):
        return self.cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        student_code = cleaned_data.get("code")
        user_email = cleaned_data.get("email").lower()
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("confirm_password")

        estudiante = EstudianteData.getEstudiante(cod_est=student_code)
        if estudiante is not None:
            msg = f"Ya se encuentra un estudiante registrado con el código {student_code}"
            self.add_error('code', msg)

        #if not user_email.endswith("@unicartagena.edu.co"):
        #    msg = "Debe registrarse con su correo institucional"
        #    self.add_error('email', msg)
        #else:
        try:
            User.objects.get(email=user_email)
            msg = f'Ya existe un usuario registrado con el correo electrónico {user_email}'
            self.add_error('email', msg)
        except User.DoesNotExist:
            pass
        
        if password1 != password2:
            msg = "La contraseña no coincide con la confirmación"
            self.add_error('confirm_password', msg)