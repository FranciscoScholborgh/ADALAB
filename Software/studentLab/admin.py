from django.contrib import admin
from .models import Curso, DesarrolloPractica, Docente, Estudiante, GrupoLaboratorio, MatriculaCurso, PracticaCurso, PracticaLaboratorio, Procedimiento, Device, PracticasDevice

# Register your models here.

admin.site.register(Device)
admin.site.register(Docente)
admin.site.register(Estudiante)
admin.site.register(Curso)
admin.site.register(MatriculaCurso)
admin.site.register(GrupoLaboratorio)
admin.site.register(Procedimiento)
admin.site.register(PracticasDevice)
admin.site.register(PracticaLaboratorio)
admin.site.register(PracticaCurso)
admin.site.register(DesarrolloPractica)
