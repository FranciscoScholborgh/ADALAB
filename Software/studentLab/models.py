from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django import forms
from django.utils.translation import gettext_lazy as _

def validate_time(time):
    seconds = time.total_seconds()
    if seconds  < 0:
        raise ValidationError(
            ('No se admite una duracion negativa'),
        )
    elif seconds >= 3600:
        raise ValidationError(
            ('La duracion de la medida debe ser inferior a una hora'),
        )

# Create your models here.

class Docente(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    correo = models.EmailField()

    class Meta:
        ordering = ['-nombre']
    
    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('studentLab.views.docente', args=[self.codigo, self.nombre])

class Estudiante(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    correo = models.EmailField()
    semestre = models.IntegerField(default=1)

    class Meta:
        ordering = ['-nombre']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('studentLab.views.estudiante', args=[self.codigo, self.nombre])

class Curso(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    docente = models.ForeignKey(Docente, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-nombre']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('studentLab.views.curso', args=[self.codigo, self.nombre])

class MatriculaCurso(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    estado = models.CharField(default="Matriculado", max_length=15)

    class Meta:
        ordering = ['-curso']

    def __str__(self):
        return f"{self.curso.nombre}, estudiante: {self.estudiante.codigo}"

    def get_absolute_url(self):
        return reverse('studentLab.views.matriculacurso', args=[self.estudiante, self.curso])

class GrupoLaboratorio(models.Model):
    id_grupo = models.IntegerField(default=1, editable=False)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-curso', '-estudiante']
        unique_together = (( 'curso', 'estudiante'),)

    def __str__(self):
       return f'{self.curso.nombre}, grupo #{self.id_grupo}: {self.estudiante.nombre}'

    def get_absolute_url(self):
        return reverse('studentLab.views.grupoLaboratorio', args=[self.curso])
    
class Procedimiento(models.Model):
    id_proc = models.AutoField(primary_key=True)
    descripcion = models.TextField()
    medida = models.CharField(null=True, max_length=255)
    unidad = models.CharField(null=True, max_length=255)
    tiempo = models.DurationField(null=True, validators=[validate_time])

    class Meta:
        ordering = ['-medida']

    def __str__(self):
        return f'{self.medida}: {self.descripcion}'

    def get_absolute_url(self):
        return reverse('studentLab.views.procedimiento', args=[self.medida])

class PracticaLaboratorio(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    area = models.SlugField(null=True)
    objetivos = models.TextField(default='')
    materiales = models.TextField(default='')
    procedimientos = models.TextField(default='')
    preguntas = models.TextField(default='') 

    class Meta:
        ordering = ['-area', '-nombre']

    def __str__(self):
        return f'{self.nombre} +({self.area})'

    def get_absolute_url(self):
        return reverse('studentLab.views.practicaLaboratorio', args=[self.nombre])

class PracticaCurso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    practica = models.ForeignKey(PracticaLaboratorio, on_delete=models.CASCADE)

    def __str__(self):
       return f'{self.curso.nombre} - {self.practica.nombre}'

class DesarrolloPractica(models.Model):
    practica = models.ForeignKey(PracticaLaboratorio, on_delete=models.CASCADE)
    procedimiento = models.ForeignKey(Procedimiento, on_delete=models.CASCADE)
    paso = models.IntegerField(default=1, editable=False)

    class Meta:
        ordering = ['-practica', '-paso']

    def save(self, *args, **kwargs):
        registros = DesarrolloPractica.objects.filter(practica=self.practica)
        practica = registros.aggregate(models.Max('paso'))
        paso = practica['paso__max']
        if(paso is not None):
            self.paso = paso + 1
        return super(DesarrolloPractica, self).save( *args, **kwargs)

    def __str__(self):
       return f'{self.practica.nombre} {self.procedimiento.medida}'

    def get_absolute_url(self):
        return reverse('studentLab.views.desarrolloPractica', args=[self.practica])

class Device(models.Model):
    name = models.CharField(max_length=6, primary_key=True)
    estado = models.CharField(max_length=7)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return f'{self.name}: {self.estado}'

    def get_absolute_url(self):
        return reverse('studentLab.views.Device', args=[self.name])

class PracticasDevice(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    practica = models.ForeignKey(PracticaLaboratorio, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-practica', 'device']

    def __str__(self):
        return f'{self.practica}: {self.device}'

    def get_absolute_url(self):
        return reverse('studentLab.views.PracticasDevice', args=[self.practica])
