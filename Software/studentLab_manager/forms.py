from django import forms
from django.db import models
from studentLab.studentLabFacade import CursoDataFacade as CursoData
from studentLab.studentLabFacade import DocenteDataFacade as DocenteData
from studentLab.studentLabFacade import DeviceDataFacade as DeviceData

# Create your models here.

class DocenteForm(forms.Form):
    code = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    def getCleanedData(self):
        return self.cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        doc_code = cleaned_data.get("code")
        doc_email = cleaned_data.get("email").lower()

        doc_bycode = DocenteData.getDocente(cod_doc=doc_code)
        if doc_bycode is not None:
            msg = f"Ya se encuentra un docente registrado con el código {doc_code}"
            self.add_error('code', msg)

        doc_byemail = DocenteData.getDocente(email_doc=doc_email)
        if doc_byemail is not None:
            msg = f'Ya existe un docente con el correo {doc_email}'
            self.add_error('email', msg)

class CursoForm(forms.Form):
    code_curso = forms.IntegerField(required=True)
    name_curso = forms.CharField(required=True)
    docente = forms.IntegerField(required=True)

    def getCleanedData(self):
        return self.cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        curso_code = cleaned_data.get("code_curso") 
        curso = CursoData.getCurso(curso_code)
        if curso is not None:
            msg = f'Ya existe un curso con el código {curso_code}'
            self.add_error('code_curso', msg)

class DeviceForm(forms.Form):
    dev_name = forms.CharField(required=True)

    def getCleanedData(self):
        return self.cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        dev_name = cleaned_data.get("dev_name") 
        device = DeviceData.getDevice(dev_name)
        if device is not None:
            msg = f'Ya existe un dispositivo de medición con el nombre {dev_name}'
            self.add_error('dev_name', msg)

class PracticaForm(forms.Form):
    doc_practica = forms.FileField(required=True)
    curso_id = forms.IntegerField(required=True)
    dev_id = forms.IntegerField(required=True)

    def getCleanedData(self):
        return self.cleaned_data

    def clean(self):
        cleaned_data = super().clean()