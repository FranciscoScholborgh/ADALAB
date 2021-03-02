from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db import models 
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from studentLab.studentLabFacade import CursoDataFacade as CursoData
from studentLab.studentLabFacade import EstudianteDataFacade as EstudianteData
from studentLab.studentLabFacade import GrupoLabDataFacade as GrupoLabData
from utils.email_utils import EmailUtils
import six

class ActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.username) + six.text_type(user.is_active)
        )

account_activation_token = ActivationTokenGenerator()

class UserSuscriber():

    def create_user(user_data, site_url):
        user = None
        student = None
        matricula = None
        grupo = None
        try:
            student_code = user_data.get('code')
            user_email = user_data.get('email')
            password = user_data.get('password')
            user = User.objects.create_user(username=student_code, email=user_email,
                                        password=password)
            user.is_active = False
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            user_name = user_data.get("name")
            url_message = f"https://{site_url}/activate/?uid={uid}&token={token}"
            email_subject = 'Activa tu cuenta en ADASLAB'
            message = f"Hola {user_name}, el usuario de tu cuenta ADASLAB es {student_code} \n\nPor favor accede al siguiente enlace para realizar la activación de tu cuenta :\n\n{url_message}"
            to_email = user_data.get('email')
            student_name = user_data.get('name')
            semester = user_data.get('semester')
            id_course= int(user_data.get('course'))
            student = EstudianteData.registrarEstudiante(codigo=student_code, nombre=student_name,
                                        correo=user_email, semestre=semester)
            course = CursoData.getCurso(id_course)
            matricula = CursoData.matricularEstudiante(estudiante=student, curso=course)
            grupo = GrupoLabData.crear_grupoLab(estudiante=student, curso=course)
            EmailUtils.send_email(email_subject, message, to_email)
            return True
        except:
            if user is not None:
                user.delete()
            if student is not None:
                student.delete()
            if matricula is not None:
                matricula.delete()
            if grupo is not None:
                grupo.delete()
            return False

    def edit_user( old_user,new_username=None, new_email=None):
        if new_email is not None:
            old_user.email = new_email
            old_user.save()
        if new_username is not None:
            new_user = User.objects.create()
            new_user.username = new_username
            new_user.password = old_user.password
            new_user.email = old_user.email
            new_user.is_active = old_user.is_active
            new_user.save()
            old_user.delete()
        
    def validate_user(uid, token):
        try:
            uidb64 = force_bytes(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uidb64)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return True
        else:
            return False
