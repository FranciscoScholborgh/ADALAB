from django import forms
from studentLab.studentLabFacade import EstudianteDataFacade as EstudianteData

class StudentForm(forms.Form):
    code = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    semester = forms.IntegerField(required=True)

    def getCleanedData(self):
        return self.cleaned_data

class StudentRegisterForm(StudentForm):

    def clean(self):
        cleaned_data = super().clean()
        student_code = cleaned_data.get("code")
        student_email = cleaned_data.get("email").lower()
        estudiante = EstudianteData.getEstudiante(cod_est=student_code)
        if estudiante is not None:
            msg = f"Ya se encuentra un estudiante registrado con el código {student_code}"
            self.add_error('code', msg)

        if not student_email.endswith("@unicartagena.edu.co"):
            msg = "Debe registrarse con su correo institucional"
            self.add_error('email', msg)
        else:
            estudiante = EstudianteData.getEstudiante(email_est=student_email)
            if estudiante is not None:
                msg = f'Ya existe un usuario con el correo institucional {student_email}'
                self.add_error('email', msg)
                
class StudentEditForm(StudentForm):

    def clean(self):
        cleaned_data = super().clean()
        student_email = cleaned_data.get("email").lower()
        if not student_email.endswith("@unicartagena.edu.co"):
            msg = "Debe registrarse con su correo institucional"
            self.add_error('email', msg)