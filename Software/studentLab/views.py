from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from json import loads as load_json
from json import dumps as generate_json
from re import search as regex_search
from accounts.accounts_utils import UserSuscriber
from .forms import StudentRegisterForm, StudentEditForm
from studentLab.studentLabFacade import CursoDataFacade as CursoData
from studentLab.studentLabFacade import EstudianteDataFacade as EstudianteData
from studentLab.studentLabFacade import PracticaDataFacade as PracticaData
from studentLab.studentLabFacade import GrupoLabDataFacade as GrupoLabData
from studentLab.studentLabFacade import DeviceDataFacade as DeviceData
from django.http import HttpResponse
from utils.str_utils import reduce_str
from htmlmin.decorators import minified_response
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

class StudentLabView():
    
    @login_required(login_url='login/')
    @minified_response
    def index(request):

        def get_group(grupos_ins):
            grupos = []
            for grupo in grupos_ins:
                curso = grupo.curso
                group_students = GrupoLabData.getGrupoLaboratorio(id_grupo=grupo.id_grupo, curso=curso)
                estudiantes = []
                for group_student in group_students:
                    if user_student.codigo != group_student.estudiante.codigo:
                        is_user = None
                        try:
                            std_code =  group_student.estudiante.codigo
                            User.objects.get(username=std_code)
                            is_user = True
                        except ObjectDoesNotExist:
                            is_user = False
                        info = {'datos':group_student.estudiante, 'is_user':is_user}
                        estudiantes.append(info)  
                grupos.append({'curso':{'codigo':curso.codigo, 'nombre':curso.nombre}, 'numero':grupo.id_grupo,
                                'user_student':user_student,'estudiantes':estudiantes})
            return grupos

        def create_group(request_json, estudiante):
            cod_curso = request_json.get("curso")
            curso = CursoData.getCurso(cod_curso)
            id_grupo = request_json.get("id_grupo")
            GrupoLabData.registrarEstudiante_grupoLab(estudiante=estudiante, curso=curso, id_grupo=id_grupo)
        
        username = request.user.username
        user_student = None
        try:
            user_student = EstudianteData.getEstudiante(cod_est=username)
        except ValueError:
            return redirect('/ADASLAB/')
        user_sdtname = reduce_str(user_student.nombre, ' ', 26)
        grupos_ins = GrupoLabData.getGruposLab_estudiante(user_student)
        cursos_nomt = CursoData.getNoMTCursos(user_student)

        practicas = PracticaData.getPracticasDisponibles(user_student)
       
        if request.method == "GET":
            grupos = get_group(grupos_ins)
            content = {'username' : user_sdtname, 'user_student':user_student, 'view':0,
                'grupos': grupos,'cursos_nomt':cursos_nomt, 'practicas':practicas}
            return render(request,'index.html', content)
        elif request.method == "POST":
            request_json = load_json(request.POST['ops'])    
            command = request_json.get("command")
            if command == "add":
                form = StudentRegisterForm(request.POST)
                if form.is_valid():
                    form_values = form.getCleanedData()
                    student_code = form_values.get("code")
                    student_name = form_values.get("name")
                    student_email = form_values.get("email")
                    student_semester = form_values.get("semester")
                    estudiante = EstudianteData.registrarEstudiante(codigo=student_code, nombre=student_name,
                                                    correo=student_email, semestre=student_semester)
                    create_group(request_json, estudiante)
                    grupos = get_group(grupos_ins)
                    msg= {'title':"Estudiante agregado al grupo", 
                        'content':f"{student_name} se ha agregado al grupo con éxito"}
                    content = {'msg':msg, 'form_values':None, 'username' : user_sdtname, 
                            'user_student':user_student, 'grupos': grupos, 'cursos_nomt':cursos_nomt,
                            'showModal':True, 'view' : 1, 'practicas':practicas}
                    return render(request,'index.html', content)
                else:
                    form_values = form.getCleanedData()
                    msg = {'title':"Error en registro de estudiante", 'content':None}
                    grupos = get_group(grupos_ins)
                    content = {'username' : user_sdtname, 'form':form, 'form_values':form_values, 
                            'view' : 1, 'showModal':True, 'msg':msg, 'user_student':user_student, 
                            'grupos': grupos, 'cursos_nomt':cursos_nomt, 'practicas':practicas}
                    return render(request,'index.html', content)
            elif command == "add_est":
                code = request_json.get("code")
                group_data = request_json.get("group_data")
                id_curso = group_data["course"]
                id_group = group_data["id_group"]

                estudiante = EstudianteData.getEstudiante(cod_est=code)
                curso = CursoData.getCurso(id_curso)
                group = GrupoLabData.getGrupoEstudiante(estudiante=estudiante, curso=curso)

                if group is None:
                    GrupoLabData.registrarEstudiante_grupoLab(estudiante=estudiante, curso=curso, id_grupo=id_group)
                    msg= {'title':"Estudiante agregado al grupo", 
                        'content':f"{estudiante.nombre} se ha agregado al grupo con éxito"}
                else:
                    msg = {'title':"Error al agregar al estudiante", 'content':f'El estudiante {estudiante.nombre} ya se encuentra registrado en un grupo de láboratorio en el curso {curso.nombre}'}
                grupos = get_group(grupos_ins)
                content = {'username' : user_sdtname, 'view' : 1, 'showModal':True, 
                    'msg':msg, 'user_student':user_student, 'grupos': grupos, 
                    'cursos_nomt':cursos_nomt, 'practicas':practicas}
                return render(request,'index.html', content)

            elif command == "edit":
                ops = request_json.get("code")
                form = StudentEditForm(request.POST)
                estudiante = EstudianteData.getEstudiante(cod_est=ops)
                form.is_valid()
                form_values = form.getCleanedData()
                errors = str(form.errors)
                is_valid = False if "Debe registrarse con su correo institucional" in errors else True
                if is_valid:
                    validate = True
                    duplicated = False
                    student_code = form_values.get("code")
                    student_email = form_values.get("email")
                    student_name = form_values.get("name")
                    student_semester = form_values.get("semester")
                    context = None
                    if student_code != estudiante.codigo:
                        verify_student = EstudianteData.getEstudiante(cod_est=student_code)
                        if verify_student is not None:
                            context = f"Ya se encuentra un estudiante registrado con el código {student_code} "
                            validate = False
                        else:
                            estudiante.codigo = student_code
                            duplicated = True
                    if student_email != estudiante.correo:
                        verify_student = EstudianteData.getEstudiante(email_est=student_email)
                        if verify_student is not None:
                            if context is None:
                                context = f"Ya se encuentra un estudiante registrado con el correo {student_email} \n"
                            else:
                                context += f"y con el correo {student_email}"
                            validate = False
                        else:
                            estudiante.correo = student_email
                    if validate:
                        estudiante.nombre = student_name
                        estudiante.semestre = student_semester
                        estudiante.save()
                        if duplicated:
                            to_delete = EstudianteData.getEstudiante(cod_est=ops)
                            to_delete.delete()
                            create_group(request_json, estudiante)
                        form_values = None
                        msg= {'title':"Información de estudiante modificada", 
                        'content':f"Se ha modificado la información de {student_name} con éxito"}
                    else:
                        msg= {'title':"Error en la moficación de datos del estudiante", 
                        'content':context}
                else:
                    msg = {'title':"Error en la moficación de datos del estudiante", 
                        'content':"Debe registrar al estudiante con un correo institucional"}
                grupos = get_group(grupos_ins)
                content = {'username' : user_sdtname, 'msg':msg, 'form_values':form_values, 
                        'user_student':user_student, 'grupos': grupos, 'cursos_nomt':cursos_nomt,
                        'showModal':True, 'view' : 1, 'practicas':practicas}
                return render(request,'index.html', content)
            elif command == "delete":
                code = request_json.get("code")
                curso_code = request_json.get("course")
                id_grupo = request_json.get("id_group")
                try:
                    estudiante = EstudianteData.getEstudiante(cod_est=code)
                    try:
                        User.objects.get(username=estudiante.codigo)
                        curso = CursoData.getCurso(curso_code)
                        GrupoLabData.retirarEstudiante_grupoLab(estudiante=estudiante, curso=curso, id_grupo=id_grupo)
                    except ObjectDoesNotExist:
                        estudiante.delete()
                    msg = {'title':"Estudiante retirado del grupo", 
                        'content':"El estudiante fue retirado del grupo con éxito"}
                except:
                    msg = {'title':"Error al retirar al estudiante del grupo", 
                        'content':"Algo salio mal al momento de retirar al estudiante del grupo, por favor verifique su conexión a internet e inténtelo nuevamente"}
                grupos = get_group(grupos_ins)
                content = {'username' : user_sdtname, 'msg':msg, 'form_values':None, 
                        'user_student': user_student, 'grupos': grupos, 'cursos_nomt':cursos_nomt,
                        'showModal':True, 'view' : 1, 'practicas':practicas}
                return render(request,'index.html', content)
            elif command == "user_edit":
                data = {"code":request.POST["user_code"], "name":request.POST["user_name"],
                        "email":request.POST["user_email"], "semester":request.POST["user_semester"]}
                form = StudentEditForm(data)
                grupos = get_group(grupos_ins)
                if form.is_valid():
                    form_values = form.getCleanedData()
                    student_code = form_values.get("code")
                    student_email = form_values.get("email")
                    student_name = form_values.get("name")
                    student_semester = form_values.get("semester")
                    if student_code == user_student.codigo:
                        user_student.nombre = student_name
                        user_student.correo = student_email
                        user_student.semestre = student_semester
                        user_student.save()
                        request.user.email = student_email
                        request.user.save()
                        msg = {'title':"Datos de usuario editados", 
                        'content':"Los datos del usuario han sido editados con éxito"}
                        content = {'username' : user_sdtname, 'msg':msg, 'form_values':None, 
                        'user_student': user_student, 'grupos': grupos, 'cursos_nomt':cursos_nomt,
                        'showModal':True, 'view' : 3, 'practicas':practicas}
                        return render(request,'index.html', content)
                    else:
                        old_code = user_student.codigo
                        user_student.codigo = student_code
                        user_student.nombre = student_name
                        user_student.correo = student_email
                        user_student.semestre = student_semester
                        user_student.save()
                        to_delete = EstudianteData.getEstudiante(cod_est=old_code)
                        lab_groups = GrupoLabData.getGruposLab_estudiante(to_delete)
                        for group in lab_groups:
                            id_group = group.id_grupo
                            curso = group.curso
                            CursoData.matricularEstudiante(estudiante=user_student, curso=curso)
                            GrupoLabData.registrarEstudiante_grupoLab(id_grupo=id_group, estudiante=user_student, 
                                                        curso=curso)
                        to_delete.delete()
                        UserSuscriber.edit_user(new_username=student_code, new_email=student_email, old_user=request.user)
                        return redirect('/login/')
                else:
                    msg = {'title':"Error al retirar al estudiante del grupo", 
                        'content':""}
                    content = {'username' : user_sdtname, 'msg':msg, 'form_values':None, 
                        'user_student': user_student, 'grupos': grupos, 'cursos_nomt':cursos_nomt,
                        'showModal':True, 'view' : 3, 'practicas':practicas}
                    return render(request,'index.html', content)
            elif command == "mat_course":
                id_curso = request.POST['mt_course']
                curso = CursoData.getCurso(id_curso)
                CursoData.matricularEstudiante(estudiante=user_student, curso=curso)
                GrupoLabData.crear_grupoLab(estudiante=user_student, curso=curso)
                msg = {'title':"Inscripción realizada", 
                        'content':f"Se he registrado en el curso {curso.nombre} con éxito"}
                grupos = get_group(grupos_ins)
                cursos_nomt = CursoData.getNoMTCursos(user_student)
                practicas = PracticaData.getPracticasDisponibles(user_student)
                content = {'username' : user_sdtname, 'msg':msg, 'form_values':None, 
                        'user_student': user_student, 'grupos': grupos, 'cursos_nomt':cursos_nomt,
                        'showModal':True, 'view' : 3, 'practicas':practicas}
                return render(request,'index.html', content)
            elif command == "del_course":
                id_curso = request.POST['ret_course']
                curso = CursoData.getCurso(id_curso)
                grupo = GrupoLabData.getGrupoEstudiante(estudiante=user_student, curso=curso)
                grupolab_info = get_group([grupo])
                for grupo_info in grupolab_info:
                    for estudiante in grupo_info.get("estudiantes"):
                        try:
                            User.objects.get(username=estudiante["datos"].codigo)
                        except ObjectDoesNotExist:
                            estudiante["datos"].delete()
                GrupoLabData.retirarEstudiante_grupoLab(estudiante=user_student, curso=curso,
                                    id_grupo= grupolab_info[0].get("numero"))
                CursoData.retirarMatriculaEstudiante(estudiante=user_student, curso=curso)
                practicas = PracticaData.getPracticasDisponibles(user_student)
                msg = {'title':"Asignatra retirada", 
                        'content':f"Se he retirado el curso {curso.nombre} en el curso con éxito"}
                grupos = get_group(grupos_ins)
                cursos_nomt = CursoData.getNoMTCursos(user_student)
                content = {'username' : user_sdtname, 'msg':msg, 'form_values':None, 
                        'user_student': user_student, 'grupos': grupos, 'cursos_nomt':cursos_nomt,
                        'showModal':True, 'view' : 3, 'practicas':practicas}
                return render(request,'index.html', content)

    def deviceStatus(request):
        device_id = request.GET.get("id")
        device_status = request.GET.get("status")
        DeviceData.setDeviceStatus(device_id, device_status)
        return HttpResponse(f"Done")

    @login_required(login_url='login/')
    def sdtConsult(request):
        code = str(request.GET['code'])
        all_students = EstudianteData.getEstudiantes()
        user_code = request.user.username
        all_students = all_students.exclude(codigo=user_code)
        estudiantes = []
        for estudiante in all_students:
            student_code = str(estudiante.codigo)
            if code == student_code or code in student_code:
                data = {'code' : estudiante.codigo, 'name' : estudiante.nombre}
                estudiantes.append(data)
        data = {'students':estudiantes}
        json_data = generate_json(data)
        return HttpResponse(json_data, content_type="application/json")