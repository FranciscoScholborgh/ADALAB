from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from studentLab.studentLabFacade import CursoDataFacade as CursoData
from studentLab.studentLabFacade import DocenteDataFacade as DocenteData
from studentLab.studentLabFacade import PracticaDataFacade as PracticaData
from studentLab.studentLabFacade import DeviceDataFacade as DeviceData
from .forms import DocenteForm, CursoForm, DeviceForm, PracticaForm
from json import loads as load_json
from .documents import ManagerDocuments
from htmlmin.decorators import minified_response

# Create your views here.

def add_docente(docForm):
    form = DocenteForm(docForm)
    if form.is_valid():
        showModal = True
        doc_data = form.getCleanedData()
        doc_code = doc_data.get("code")
        doc_name = doc_data.get("name")
        doc_email = doc_data.get("email")
        DocenteData.createDocente(codigo=doc_code, nombre=doc_name, correo=doc_email)
        msg = {'title':'Docente agregado', 'content':f'El docente {doc_name} ha sido agregado con éxito'}
        content = {'showModal':True, 'msg':msg, 'view':0}
        return content
    else:
        doc_data = form.getCleanedData()
        msg = {'title':'Error al registrar el docente', 'content':None}
        errors = [form.errors[error] for error in form.errors]
        content = {'showModal':True, 'form':form, 'docform_values': doc_data, 'msg':msg,
                'errors':errors, 'view':0}
        return content

def edit_docente(docForm):
    form = DocenteForm(docForm)
    form.is_valid()
    form_values = form.getCleanedData()
    old_values = load_json(docForm['olddoc'])
    old_code = old_values['code']
    try:
        code = form_values['code']
    except KeyError:
        code = None
    try:
        name = form_values['name'] if form_values['name'] is not None else old_values['name']
    except KeyError:
        name = old_values['name']
    try:
        email = form_values['email'] if form_values['email'] is not None else old_values['email']
    except KeyError:
        email = old_values['email']
    old_docente = DocenteData.getDocente(old_code)
    if old_code != code and code is not None:
        old_docente.delete()
        DocenteData.createDocente(codigo=code, nombre=name, correo=email)    
    else:
        old_docente.nombre = name
        old_docente.correo = email
        old_docente.save()
    msg = {'title':'Información modificada', 'content':f'La información del docente ha sido modificada con éxito'}
    content = {'showModal':True, 'msg':msg, 'view':0}
    return content

def remove_docente(docForm):
    doc_code = docForm.get('info', None)
    doc_code = int(doc_code)
    docente = DocenteData.getDocente(doc_code)
    msg = {'title':'Registro eliminado exitosamente', 'content':f'El registro del docente {docente.nombre} ha sido eliminado con éxito'}
    docente.delete()
    content = {'showModal':True, 'msg':msg, 'view':0}
    return content

def add_curso(curForm):
    form = CursoForm(curForm)
    if form.is_valid():
        showModal = True
        cur_data = form.getCleanedData()
        curso_code = cur_data.get("code_curso")
        curso_name = cur_data.get("name_curso")
        doc_code = cur_data.get("docente")
        CursoData.createCurso(codigo=curso_code, nombre=curso_name, cod_docente=doc_code)
        msg = {'title':'Curso agregado', 'content':f'El curso {curso_name} ha sido agregado con éxito'}
        content = {'showModal':True, 'msg':msg, 'view':1}
        return content
    else:
        doc_data = form.getCleanedData()
        msg = {'title':'Error al registrar el curso', 'content':None}
        errors = [form.errors[error] for error in form.errors]
        content = {'showModal':True, 'form':form, 'form_values': doc_data, 'msg':msg,
                'errors':errors, 'view':1}
        return content

def edit_curso(curForm):
    form = CursoForm(curForm)
    form.is_valid()
    form_values = form.getCleanedData()
    old_values = load_json(curForm['oldcur'])
    old_code = old_values['code_curso']
    try:
        code = form_values['code_curso']
    except KeyError:
        code = None
    try:
        name = form_values['name_curso'] if form_values['name_curso'] is not None else old_values['name_curso']
    except KeyError:
        name = old_values['name_curso']
    try:
        cod_docente = form_values['docente'] if form_values['docente'] is not None else old_values['docente']
    except KeyError:
        cod_docente = old_values['docente']
    old_curso = CursoData.getCurso(old_code)
    if old_code != code and code is not None:
        old_curso.delete()
        CursoData.createCurso(codigo=code, nombre=name, cod_docente=cod_docente)
    else:
        old_curso.nombre = name
        docente = DocenteData.getDocente(cod_docente)
        old_curso.docente = docente
        old_curso.save()
    msg = {'title':'Curso modificado', 'content':f'La información del curso ha sido modificada con éxito'}
    content = {'showModal':True, 'msg':msg, 'view':1}
    return content

def remove_curso(curForm):
    cur_code = curForm.get('info', None)
    cur_code = int(cur_code)
    curso = CursoData.getCurso(cur_code)
    msg = {'title':'Registro eliminado exitosamente', 'content':f'El registro del curso {curso.nombre} ha sido eliminado con éxito'}
    curso.delete()
    content = {'showModal':True, 'msg':msg, 'view':1}
    return content

def add_dispositivo(devForm):
    form = DeviceForm(devForm)
    if form.is_valid():
        showModal = True
        dev_data = form.getCleanedData()
        dev_name = dev_data.get("dev_name")
        DeviceData.createDevice(dev_name)
        msg = {'title':'Dispositivo agregado', 'content':f'El dispositivo {dev_name} ha sido agregado con éxito'}
        content = {'showModal':True, 'msg':msg, 'view':2}
        return content
    else:
        doc_data = form.getCleanedData()
        msg = {'title':'Error al registrar el dispositivo', 'content':None}
        errors = [form.errors[error] for error in form.errors]
        content = {'showModal':True, 'form':form, 'form_values': doc_data, 'msg':msg,
                'errors':errors, 'view':2}
        return content

def edit_dispositivo(devForm):
    form = DeviceForm(devForm)
    if form.is_valid():
        old_name = devForm['olddev']
        old_device = DeviceData.getDevice(old_name)
        old_device.delete()
        dev_data = form.getCleanedData()
        dev_name = dev_data.get("dev_name")
        DeviceData.createDevice(dev_name)
        msg = {'title':'Dispositivo modificado', 'content':f'El dispositivo ha sido modificado con éxito'}
        content = {'showModal':True, 'msg':msg, 'view':2}
        return content
    else:
        doc_data = form.getCleanedData()
        msg = {'title':'Error al modificar el dispositivo', 'content':None}
        errors = [form.errors[error] for error in form.errors]
        content = {'showModal':True, 'form':form, 'form_values': doc_data, 'msg':msg,
                'errors':errors, 'view':2}
        return content

def remove_dispositivo(devForm):
    dev_code = devForm.get('info', None)
    device = DeviceData.getDevice(dev_code)
    msg = {'title':'Registro eliminado exitosamente', 'content':f'El registro del dispositivo {device.name} ha sido eliminado con éxito'}
    device.delete()
    content = {'showModal':True, 'msg':msg, 'view':2}
    return content

def proccess_document(request, filename):
    doc = request.FILES[filename]
    pralab_data = ManagerDocuments.load_pralabtemplate(doc)
    return pralab_data

def add_practica(request, data=None):
    created = False
    content = {}
    if data is None:   
        pralab_data = proccess_document(request, 'doc_practica')
        created = True
        content['view'] = 4
    else:
        pralab_data = data
        content['view'] = 3
    
    if pralab_data is None:
        msg = {'title':'Error al cargar el documento', 'content': 'No se puedo cargar el documento, revise que este no este dañado e inténtelo nuevamente'} 
    elif pralab_data == 1:
        msg = {'title':'Error al cargar el documento', 'content': 'El documento no tiene el formato correcto, por favor verifíquelo e inténtelo nuevamente'}
    elif pralab_data == 2:
        msg = {'title':'Contenido faltante en el formato', 'content': 'Debe llenar toda la información solicitada en el documento para crear la práctica, ingrese la información faltante e inténtelo nuevamente'}
    elif pralab_data == 3:
        msg = {'title':'Formato de procedimientos incorrecto', 'content': 'El formato utilizado en el registro de los procedimientos no es correcto, por favor corríjalo e inténtelo nuevamente'}
    elif pralab_data == 4:
        msg = {'title':'Formato de medidas incorrecto', 'content': 'Debe ingresar el mismo número de medidas y unidades en los procedimientos'}
    elif pralab_data == 5:
        msg = {'title':'Formato de tiempo incorrecto', 'content': 'El formato de tiempo no es el correcto en los procedimientos'}
    elif pralab_data == 6:
        msg = {'title':'Código de práctica invalido', 'content': 'El código de la práctica debe ser numérico'}
    else:
        try:
            hello = pralab_data['curso']
        except KeyError:
            curso =  request.POST.get('curso_id', None)
            pralab_data['curso'] = curso

        try:    
            hello = pralab_data['device']
        except KeyError:
            dev = request.POST.get('dev_id', None)
            pralab_data['device'] = dev
            
        created = PracticaData.create_practicaLaboratorio(pralab_data)   
        if created is True:   
            status = 'creada' if content['view'] == 4 else 'modificada'         
            msg = {'title':f'Práctica {status}', 'content': f'La práctica ha sido {status} con éxito'}
        else:
            status = 'crear' if content['view'] == 4 else 'modificar'
            msg = {'title':f'Error al {status} la práctica', 'content': f'No se puedo {status} la práctica de laboratorio, por favor verifique su conexión a internet e inténtelo nuevamente, si el problema persiste escribenos a adaslaboratory@gmail.com explicando la situación'}
    content['showModal'] = True
    content['msg'] = msg
    return content

def edit_practica(request):
    oldcode =  int(request.POST.get('oldpracode', ''))
    pralab_data = proccess_document(request, 'editdoc_practica')
    curso =  request.POST.get('newcurso_id', None)
    dev = request.POST.get('newdev_id', None)
    pralab_data['curso'] = curso
    pralab_data['device'] = dev
    old_pralab = PracticaData.getPracticaLaboratorio(oldcode)
    old_pralab.delete()
    return add_practica(request, pralab_data)

def remove_practica(praForm):
    pra_code = praForm.get('info', None)
    pra_code = int(pra_code)
    practica = PracticaData.getPracticaLaboratorio(pra_code)
    msg = {'title':'Registro eliminado exitosamente', 'content':f'El registro de la práctica {practica.nombre} ha sido eliminado con éxito'}
    practica.delete()
    content = {'showModal':True, 'msg':msg, 'view':3}
    return content

functions = {
    'adddoc': add_docente,
    'editdoc' : edit_docente,
    'remove_docente' : remove_docente,
    'addcur' : add_curso,
    'editcur' : edit_curso,
    'remove_curso' : remove_curso,
    'adddev' : add_dispositivo,
    'editdev' : edit_dispositivo,
    'remove_dispositivo' : remove_dispositivo,
    'adddocpra' : add_practica,
    'editpralab': edit_practica,
    'remove_practica' : remove_practica
}

class MangerView():

    @login_required(login_url='/login/')
    @minified_response
    def index(request):
        user = request.user
        if user.is_staff is False:
            return redirect('/')
        content = {}
        if request.method == 'POST':
            ops = request.POST.get('ops', '')
            execute = functions.get(ops)
            if ops != 'adddocpra' and ops != 'editpralab':
                content = execute(request.POST)
            else:
                content = execute(request)
        elif request.method == 'GET':
            content['view'] = 0
        docentes = DocenteData.getDocentes()
        cursos = CursoData.getCursosinADAS()
        devices = DeviceData.getDevices()
        practicas = PracticaData.getPracticasLaboratorio()
        practicas_ngp = []
        for practica in practicas:
            new_pra = {}
            new_pra['codigo'] = practica.codigo
            new_pra['nombre'] = practica.nombre
            new_pra['area'] = practica.area
            new_pra['objetivos'] = practica.objetivos
            new_pra['materiales'] = practica.materiales
            new_pra['procedimientos'] = practica.procedimientos
            new_pra['preguntas'] = practica.preguntas
            new_pra['curso'] = CursoData.getCurso_frompractica(practica)
            new_pra['device'] = DeviceData.getDevice_fromPractica(practica)
            practicas_ngp.append(new_pra)
        content['docentes'] = docentes
        content['cursos'] = cursos
        content['devices'] = devices
        content['practicas'] = practicas_ngp
        return render(request, 'adaslab_manager.html', content)
