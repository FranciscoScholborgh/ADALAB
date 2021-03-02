from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm
from .accounts_utils import UserSuscriber
from studentLab.studentLabFacade import CursoDataFacade as CursoData
from htmlmin.decorators import minified_response

# Create your views here.

class AccountsView():

    @minified_response
    def user_login(request):
        if request.method == 'GET':
            if request.user.is_authenticated:
                if request.user.is_staff:
                    return redirect('/ADASLAB/')
                else:
                    return redirect('/')
            else: 
                return render(request, 'login.html', {})
        elif request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                user_data = form.getCleanedData()
                username = user_data["user"]
                password = user_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    if user.is_staff:
                        return redirect('/ADASLAB/')
                    else:
                        return redirect('/')
                else:
                    try:
                        user = User.objects.get(username=username)
                        if user.is_active:
                            msg = {"title" : "Usuario o contraseña incorrecta",
                                "content" : "Contraseña incorrecta, por favor inténtelo nuevamente"}
                            content = {"msg" : msg, "showModal" : True}
                            return render(request, 'login.html', content)
                        else:
                            msg = {"title" : "Su cuenta NO está verificada",
                                "content" : f"Su cuenta no está verificada, por favor revise la bandeja de entrada de su correo.\nEn caso de no haber recibido un correo, comuníquese con nosotros a través de adaslaboratory@gmail.com"}
                            content = {"msg" : msg, "showModal" : True}
                            return render(request, 'login.html', content)
                    except User.DoesNotExist:
                        msg = {"title" : "Su cuenta NO está registrada",
                            "content" : f"La cuenta {username}  no se encuentra registrada. Debe de registrarse si desea utilizar ADASLAB"}
                        content = {"msg" : msg, "showModal" : True}
                        return render(request, 'login.html', content)
            else:
                msg = {"title" : "Usuario o contraseña incorrecta"}
                content = {'form':form, "msg" : msg}
                return render(request, 'login.html', content)

    @minified_response
    def user_logout(request):
        logout(request)
        return redirect(AccountsView.user_login)

    @minified_response
    def register(request):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            cursos = CursoData.getCursos()
            if request.method == 'GET':
                form_values = {"code" : '', "name" : '', "email" : '', "semester" : None}  
                return render(request, 'register.html', {'cursos' : cursos, 'form_values' : form_values})
            else:
                form = RegisterForm(request.POST)
                if form.is_valid():
                    showModal = True
                    user_data = form.getCleanedData()
                    current_site = get_current_site(request)
                    created = UserSuscriber.create_user(user_data, current_site)
                    if created:
                        msg = {"title" : "Registro realizado con éxito",
                            "content" : "Solo queda uno paso para poder acceder a ADASLAB, por favor revisa tu correo para activar tu cuenta de usaurio"} 
                    else:
                        msg = {"title" : "No se pudo enviar correo de validación", 
                            "content" : False}
                    content = {'msg' : msg, 'showModal' : showModal, 'form_values' : user_data}
                    return render(request, 'register.html', content) 
                else:
                    msg = {"title" : "Error en el registro", "content" : None}
                    showModal = True
                    user_data = form.getCleanedData()
                    id_curso = user_data.get("course")
                    user_data["course"] = CursoData.getCurso(id_curso)
                    content = {'form':form, 'msg' : msg ,'showModal' : showModal, 'cursos' : cursos, 'form_values' : user_data}
                    return render(request, 'register.html', content)
    
    @minified_response    
    def activate_account(request):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            if request.method == 'GET':
                uid = request.GET.get('uid', '')
                token = request.GET.get('token', '')
                if UserSuscriber.validate_user(uid, token):
                    title = "Cuenta activada"
                    content = "Tu cuenta ha sido activada, ahora puedes iniciar sesión en ADASLAB"
                    success = True
                else:
                    title = "Error al activar la cuenta"
                    content = "Algo salio mal al momento de la activación, por favor verifica que tenga conexión a internet o que el enlace de activación sea el correcto. En caso de no poder activar la cuenta mediante al enlace enviado a su correo escríbenos a adaslaboratory@gmail.com y lo solucionaremos lo más pronto posible"
                    success = False
                msg = {"title" : title, "content" : content, "success" : success}
                return render(request, 'activate.html', msg)
