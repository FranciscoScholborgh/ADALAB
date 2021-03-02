from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from studentLab.studentLabFacade import PracticaDataFacade as PracticaData
from studentLab.studentLabFacade import GrupoLabDataFacade as GrupoLabData
from studentLab.studentLabFacade import getPracticaCurso
from .documents import LabDocuments
from utils.email_utils import EmailUtils
from io import BytesIO
import json
from htmlmin.decorators import minified_response
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Create your views here.

class LaboratoryView():

    @login_required(login_url='/login/')
    @minified_response
    def laboratory(request):
        if request.method == 'POST':
            id_lab = request.POST.get('id_lab', '')
            id_dev = request.POST.get('id_dev', '')
            laboratorio = getPracticaCurso(id_lab)
            preguntas = PracticaData.getPreguntas_PracticaLab(laboratorio.practica)
            procedimientos = PracticaData.getProcedimientosPractica(laboratorio.practica)
            content = {'laboratorio':laboratorio, 'procedimientos':procedimientos,
                'preguntas':preguntas, 'device':id_dev, 'id_lab':id_lab}
            return render(request,'laboratorio.html', content)

    @login_required(login_url='/login/')
    def preinforme(request):
        if request.method == 'POST':
            try:
                raw_data = request.POST.get('data', '')
                method = request.POST.get('method', '')
                json_data = json.loads(raw_data)
                id_lab = json_data['id_lab']
                procs_data = json_data['procs']
                pregs_data = json_data['pregs']
                laboratorio = getPracticaCurso(id_lab)
                practica = laboratorio.practica
                curso = laboratorio.curso
                preguntas = PracticaData.getPreguntas_PracticaLab(practica)
                procedimientos = PracticaData.getProcedimientosPractica(practica)
                id_estudiante = request.user.username
                grupoLab = GrupoLabData.getGrupoLabotaroio(id_est=id_estudiante, curso=curso)
                id_grupo = grupoLab[0].id_grupo
                estudiantes = [registro.estudiante for registro in grupoLab]
                #estudiantes.pop()
                header = {'title':practica.nombre, 'curso':curso, 'estudiantes':estudiantes, 'id_grupo': id_grupo}
                data = {'procedimientos':procedimientos, 'proc_data':procs_data}
                preguntas = {'preguntas':preguntas, 'respuestas':pregs_data}
                document = LabDocuments.generate_preinforme(header, data, preguntas)
                filename = f"Práctica: {practica.nombre} - grupo {id_grupo}.docx"
                if method == 'local_info':
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename= "{filename}"'
                    document.save(response)
                    return response
                elif method == 'docente':
                    file = BytesIO()
                    document.save(file)
                    file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    attachments = [{"filename": filename, "to_attach": file, "file_type":file_type}]
                    email_subject = f'Preinforme generado {filename} por EL grupo {id_grupo}, curso: {curso.nombre}'
                    message = f'Hola estimado docente {curso.docente.nombre}.\n\nMediante este correo le hacemos entrega del preinforme generado por el grupo {id_grupo} de la práctica {practica.nombre} del curso {curso.nombre} realizada en ADASLAB.\nEl grupo está integrado por los estudiantes:\n'
                    for estudiante in estudiantes:
                        message += estudiante.nombre
                        message += '\n'
                    EmailUtils.send_email(email_subject, message,curso.docente.correo, attachments=attachments)
                    return HttpResponse("Enviado al docente con éxito xD")
                elif method =='estudiante':
                    file = BytesIO()
                    document.save(file)
                    file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    attachments = [{"filename": filename, "to_attach": file, "file_type":file_type}]
                    email_subject = f'Preinforme generado {filename} por el grupo {id_grupo}, curso: {curso.nombre}'
                    message = f'Hola estimados estudiantes.\n\nMediante este correo les hacemos entrega del preinforme generado por su grupo (#{id_grupo}) de la práctica {practica.nombre} del curso {curso.nombre} realizada en ADASLAB.\n'
                    recievers = []
                    for estudiante in estudiantes:
                        recievers.append(estudiante.correo)
                    EmailUtils.send_email(email_subject, message, recievers, attachments=attachments)
                    return HttpResponse("Enviado al grupo con éxito xD")

                #return HttpResponse(method)
            except json.decoder.JSONDecodeError:
                pass