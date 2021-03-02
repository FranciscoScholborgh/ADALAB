from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from datetime import timedelta
from .models import Docente, Curso, Estudiante, GrupoLaboratorio, MatriculaCurso, PracticaLaboratorio, PracticaCurso, Device, PracticasDevice, DesarrolloPractica, Procedimiento

#En Construcción

class DocenteDataFacade():
    
    def getDocente(cod_doc=None, email_doc=None):
        try:
            if cod_doc is not None and email_doc is not None:
                return Docente.objects.get(codigo=cod_doc, correo=email_doc)
            elif cod_doc is not None:
                return Docente.objects.get(codigo=cod_doc)
            elif email_doc is not None:
                return Docente.objects.get(correo=email_doc)
            else:
                return None
        except ObjectDoesNotExist:
            return None

    def getDocentes():
        return Docente.objects.all()

    def createDocente(codigo, nombre, correo):
        return Docente.objects.create(codigo=codigo, nombre=nombre,
                                correo=correo)


class CursoDataFacade():

    def getCurso(id_curso):
        try:
            return Curso.objects.get(codigo=id_curso)
        except ObjectDoesNotExist:
            return None

    def getCursosinADAS():
        return Curso.objects.all()    
        
    def getCursos():
        cursos_quarySet = Curso.objects.all()
        cursos = []
        for curso in cursos_quarySet:
            curso_id = curso.codigo
            curso_name = curso.nombre
            cursos.append({"id" : curso_id, "name" : curso_name})
        return cursos

    def getMTCursos(estudiante):
        grupos = MatriculaCurso.objects.filter(estudiante=estudiante, estado="Matriculado")
        cursos = []
        for grupo in grupos:
            cursos.append(grupo.curso)
        return cursos

    def getNoMTCursos(estudiante):
        cursos = CursoDataFacade.getMTCursos(estudiante)
        cod_cursos = [curso.codigo for curso in cursos]
        noMTCursos = Curso.objects.all()
        for cod_curso in cod_cursos:
            noMTCursos = noMTCursos.exclude(codigo=cod_curso)
        return noMTCursos

    def createCurso(codigo, nombre, cod_docente):
        docente = DocenteDataFacade.getDocente(cod_doc=cod_docente)
        return Curso.objects.create(codigo=codigo, nombre=nombre,
                                docente=docente)

    def matricularEstudiante(estudiante, curso):
        try:
            matricula = MatriculaCurso.objects.get(estudiante=estudiante, curso=curso)
            matricula.estado = "Matriculado"
            matricula.save()
        except MatriculaCurso.DoesNotExist:
            return MatriculaCurso.objects.create(estudiante=estudiante, curso=curso)

    def retirarMatriculaEstudiante(estudiante, curso):
        matricula = MatriculaCurso.objects.get(estudiante=estudiante, curso=curso)
        matricula.estado = "Retirado"
        matricula.save()
        return True

    def getMatriculaEstudiante(estudiante):
        return MatriculaCurso.objects.filter(estudiante=estudiante)

    def getCurso_frompractica(practica):
        try:
            prac_curso = PracticaCurso.objects.get(practica=practica)
            curso = prac_curso.curso
            return curso
        except ObjectDoesNotExist:
            return None

class EstudianteDataFacade():

    def registrarEstudiante(codigo, nombre, correo, semestre):
        return Estudiante.objects.create(codigo=codigo, nombre=nombre,
                                        correo=correo, semestre=semestre)
        
    def getEstudiante(cod_est=None, email_est=None):
        try:
            if cod_est is not None and email_est is not None:
                return Estudiante.objects.get(codigo=cod_est, correo=email_est)
            elif cod_est is not None:
                return Estudiante.objects.get(codigo=cod_est)
            elif email_est is not None:
                return Estudiante.objects.get(correo=email_est)
            else:
                return None
        except ObjectDoesNotExist:
            return None

    def getEstudiantes():
        return Estudiante.objects.all()

class PracticaDataFacade():

    def getPracticaLaboratorio(codigo):
        try:
            return PracticaLaboratorio.objects.get(codigo=codigo)
        except ObjectDoesNotExist:
            return None

    def getPracticasLaboratorio():
        return PracticaLaboratorio.objects.all() 

    def create_practicaLaboratorio(pralab_data):
        code = pralab_data["código"]
        pralab = PracticaDataFacade.getPracticaLaboratorio(code)
        if pralab is None:
            name = pralab_data["nombre"]
            area = pralab_data["área"]
            list_objs = pralab_data["objetivos"]
            objs = ''
            for obj in list_objs:
                objs += f'{obj}/*/'
            objs = objs[:-3]
            list_mats = pralab_data["materiales"]
            mats = ''
            for mat in list_mats:
                mats += f'{mat}/*/'
            mats = mats[:-3]
            list_procs = pralab_data["procedimientos"]
            proc_text = ''
            procs = []
            for proc in list_procs:
                proc_text += f'{proc["descripción"]}/*/'
                desc = proc["descripción"]
                list_measu= proc["medidas"]
                measures = ''
                for measure in list_measu:
                    measures += f'{measure},'
                measures = measures[:-1]
                list_units = proc["unidades"]
                units = ''
                for unit in list_units:
                    units += f'{unit},'
                units = units[:-1]
                vect_t = proc["tiempo"]
                t = int(vect_t[0])*3600 + int(vect_t[1])*60 + int(vect_t[2])
                t_delta = timedelta
                procedimiento = Procedimiento.objects.create(descripcion=desc, medida=measures,
                    unidad=units, tiempo=timedelta(seconds=t))
                procs.append(procedimiento)  
            proc_text = proc_text[:-3]
            list_pregs = pralab_data["preguntas"]
            pregs = ''
            for preg in list_pregs:
                pregs += f'{preg}/*/'
            pregs = pregs[:-3]
            practica = PracticaLaboratorio.objects.create(codigo=code, nombre=name, 
                area=area, objetivos=objs, materiales=mats, procedimientos=proc_text, 
                preguntas=pregs)
            curso_code = pralab_data["curso"]
            curso = CursoDataFacade.getCurso(curso_code)
            dev_name = pralab_data["device"]
            device = DeviceDataFacade.getDevice(dev_name)
            if curso is None or device is None:
                return False
            PracticaCurso.objects.create(curso=curso, practica=practica)
            PracticasDevice.objects.create(device=device, practica=practica)
            for proc in procs:
                DesarrolloPractica.objects.create(practica=practica, procedimiento=proc)
            return True    
        else:
            return False    

    def getPracticasDisponibles(estudiante):
        cursos = CursoDataFacade.getMTCursos(estudiante=estudiante)
        devices = Device.objects.filter(estado="ONLINE")
        practicas_online = []
        for device in devices:
            prac_indev = PracticasDevice.objects.filter(device=device)
            for pradev in prac_indev:
                practicas_online.append(pradev.practica)
        practicas = []
        for curso in cursos:
            practicas_cursos = PracticaCurso.objects.filter(curso=curso)
            for practica_curso in practicas_cursos:
                if practica_curso.practica in practicas_online:
                    for praDev in PracticasDevice.objects.filter(practica=practica_curso.practica):
                        add = {'practica':practica_curso.practica, 'curso':practica_curso.curso,
                            'device': praDev.device.name, 'id':practica_curso.id}
                        practicas.append(add)
        return practicas

    def getProcedimientosPractica(practica):
        pasosPractica = DesarrolloPractica.objects.filter(practica=practica)
        procedimientos = []
        for pasoPractica in pasosPractica:
            desPrac = {'procedimiento': pasoPractica.procedimiento, 'paso': pasoPractica.paso}
            procedimientos.append(desPrac)
        procedimientos.reverse()
        return procedimientos

    def getPreguntas_PracticaLab(practica):
        preguntas = []
        id = 1
        for pregunta in practica.preguntas.split('/*/'):
            preguntas.append({'id':id,'text':pregunta})
            id+=1
        return preguntas

class GrupoLabDataFacade():

    def crear_grupoLab(estudiante, curso):
        grupos = GrupoLaboratorio.objects.filter(curso=curso)
        group_index = []
        for grupo in grupos:
            group_index.append(grupo.id_grupo)
        id_grupo = 1
        while True:
            if id_grupo not in group_index:
                break
            id_grupo += 1
        grupo = GrupoLaboratorio.objects.create(estudiante=estudiante,curso=curso)
        grupo.id_grupo = id_grupo
        grupo.save()
        return grupo

    def registrarEstudiante_grupoLab(estudiante, curso, id_grupo):
        CursoDataFacade.matricularEstudiante(estudiante=estudiante, curso=curso)
        return GrupoLaboratorio.objects.create(id_grupo=id_grupo, estudiante=estudiante, 
                                            curso=curso)

    def retirarEstudiante_grupoLab(estudiante, curso, id_grupo):
        grupoLab = GrupoLaboratorio.objects.get(estudiante=estudiante, curso=curso, id_grupo=id_grupo)
        grupoLab.delete()
        CursoDataFacade.retirarMatriculaEstudiante(estudiante=estudiante, curso=curso)
        return True

    def getGrupoLabotaroio(id_est, curso):
        usuario_est = EstudianteDataFacade.getEstudiante(cod_est=id_est)
        grupo = GrupoLaboratorio.objects.get(estudiante=usuario_est, curso=curso)
        id_grupo = grupo.id_grupo
        return GrupoLaboratorio.objects.filter(id_grupo=id_grupo)

    def getGruposLab_estudiante(estudiante):
        return GrupoLaboratorio.objects.filter(estudiante=estudiante)

    def getGrupoLaboratorio(id_grupo, curso):
        return GrupoLaboratorio.objects.filter(id_grupo=id_grupo, curso=curso)

    def getGrupoEstudiante(estudiante, curso):
        try:
            return GrupoLaboratorio.objects.get(estudiante=estudiante, curso=curso)
        except ObjectDoesNotExist:
            return None

class DeviceDataFacade():

    def setDeviceStatus(device, estado):
        device = Device.objects.get(name=device)
        device.estado = estado
        device.save()

    def getDevice(dev_name):
        try:
            return Device.objects.get(name=dev_name)
        except ObjectDoesNotExist:
            return None

    def getDevice_fromPractica(practica):
        try:
            prac_dev = PracticasDevice.objects.get(practica=practica)
            device = prac_dev.device
            return device
        except ObjectDoesNotExist:
            return None

    def getDevices():
        return Device.objects.all()

    def createDevice(dev_name):
        return Device.objects.create(name=dev_name, estado='OFFLINE')

def getPracticaCurso(id):
    return PracticaCurso.objects.get(id=id)