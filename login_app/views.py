from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from login_app.models import CustomUser
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Cita, EvolucionClinica
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.http import JsonResponse
from .models import CustomUser, HistoriaClinica
from .models import CustomUser
from django.contrib import messages
from .models import Cita, HistoriaClinica, EvolucionClinica
from django.core.exceptions import PermissionDenied


User = get_user_model()


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")  # Usa .get() para evitar errores
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"Usuario autenticado: {user.username}, Rol: {getattr(user, 'role', 'No definido')}")  # Debug seguro

            # Redirigir según el rol
            role = getattr(user, "role", None)  # Evita errores si el atributo no existe
            if role == "admin":
                return redirect("admin_dashboard")
            elif role == "auxiliar":
                return redirect("auxiliar_dashboard")
            elif role == "dentista":
                return redirect("dentista_dashboard")
            elif role == "paciente":
                return redirect("paciente_dashboard")
            else:
                print("No tiene rol asignado, volviendo al home")
                return redirect("home")

        else:
            print("Credenciales incorrectas")
            return redirect("login")

    # Si es GET, renderizar la plantilla del login
    return render(request, "login.html")  # Asegúrate de que el template exista

@login_required
def admin_dashboard(request):
    return render(request, 'login/admin_dashboard.html', {'usuario': request.user})

@login_required
def auxiliar_dashboard(request):
    return render(request, 'login/auxiliar_dashboard.html', {'usuario': request.user})

@login_required
def gestion_pacientes(request):
    pacientes = CustomUser.objects.filter(role="paciente")  # Solo pacientes
    return render(request, "funcionalidades/gestion_pacientes.html", {"pacientes": pacientes})


@login_required
def dentista_dashboard(request):
    return render(request, 'login/dentista_dashboard.html', {'usuario': request.user})  

@login_required
def paciente_dashboard(request):
    paciente = request.user

    citas = Cita.objects.filter(paciente=paciente).order_by('fecha', 'hora')

    historia_clinica = HistoriaClinica.objects.filter(paciente=paciente).order_by('-fecha_inicio').first()

    evoluciones = EvolucionClinica.objects.filter(historia__paciente=paciente).order_by('-fecha_consulta')[:5]

    return render(request, 'login/paciente_dashboard.html', {
        'usuario': paciente,
        'citas': citas,
        'historia_clinica': historia_clinica,
        'evoluciones': evoluciones,
    })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def gestion_usuarios(request):
    role = request.GET.get('role')  # Ahora sí coincide con el modelo
    if role:
        usuarios = CustomUser.objects.filter(role=role)
    else:
        usuarios = CustomUser.objects.all()
    return render(request, 'funcionalidades/gestion_usuarios.html', {'usuarios': usuarios})

@login_required
def crear_usuario(request):
    usuario_creado = False
    error_message = None  # Para almacenar el mensaje de error

    if request.method == "POST":
        nombre_completo = request.POST.get("nombre_completo")
        username = request.POST.get("username")
        numero_documento = request.POST.get("numero_documento")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")

        # Verificar si las contraseñas coinciden
        if password1 != password2:
            error_message = "Las contraseñas no coinciden."
        # Verificar si el número de documento ya existe
        elif CustomUser.objects.filter(numero_documento=numero_documento).exists():
            error_message = "El número de documento ya está registrado."
        # Verificar si el correo ya existe
        elif CustomUser.objects.filter(email=email).exists():
            error_message = "El correo electrónico ya está registrado."
        else:
            try:
                usuario = CustomUser(
                    nombre_completo=nombre_completo,
                    username=username,
                    numero_documento=numero_documento,
                    email=email,
                    role=role,
                    password=make_password(password1),  # Encriptar contraseña
                )
                usuario.save()
                usuario_creado = True
            except IntegrityError:
                error_message = "Ha ocurrido un error al registrar el usuario."

    return render(request, "funcionalidades/crear_usuario.html", {"usuario_creado": usuario_creado, "error_message": error_message})

@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    error_message = None
    usuario_actualizado = False

    if request.method == "POST":
        nombre_completo = request.POST.get("nombre_completo")
        username = request.POST.get("username")
        email = request.POST.get("email")
        numero_documento = request.POST.get("numero_documento")
        nueva_contraseña = request.POST.get("password")
        role = request.POST.get("role")

        # Validaciones de duplicados en otros usuarios
        if CustomUser.objects.filter(numero_documento=numero_documento).exclude(id=user_id).exists():
            error_message = "El número de documento ya está registrado en otro usuario."
        elif CustomUser.objects.filter(username=username).exclude(id=user_id).exists():
            error_message = "El nombre de usuario ya está registrado."
        elif CustomUser.objects.filter(email=email).exclude(id=user_id).exists():
            error_message = "El correo electrónico ya está registrado en otro usuario."
        else:
            try:
                usuario.nombre_completo = nombre_completo
                usuario.username = username
                usuario.email = email
                usuario.numero_documento = numero_documento
                usuario.role = role

                # Si el usuario ingresa una nueva contraseña, la actualiza
                if nueva_contraseña:
                    usuario.password = make_password(nueva_contraseña)

                usuario.save()
                usuario_actualizado = True
            except IntegrityError:
                error_message = "Ha ocurrido un error al actualizar el usuario."

    return render(request, "funcionalidades/editar_usuario.html", {
        "usuario": usuario, 
        "usuario_actualizado": usuario_actualizado, 
        "error_message": error_message
    })

@login_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    usuario.delete()
    return redirect("gestion_usuarios")


#gestion citas
@login_required
def gestion_citas(request):
    pacientes = CustomUser.objects.filter(role="paciente")
    citas_pendientes = {paciente.id: Cita.objects.filter(paciente=paciente, estado="pendiente") for paciente in pacientes}

    return render(request, 'funcionalidades/gestion_citas.html', {
        'pacientes': pacientes,
        'citas_pendientes': citas_pendientes
    })
    
 #agenda de citas
@login_required
def agenda_citas(request):
    usuario_id = request.user.nombre_completo  # Obtiene el ID del usuario autenticado
    print(f"ID del usuario autenticado: {usuario_id}")
    dentista = CustomUser.objects.filter(nombre_completo=usuario_id).first()
   
    citas_pendientes_dentista = Cita.objects.filter(dentista=dentista, estado="pendiente")
 
    for cita in citas_pendientes_dentista:  # Itera directamente sobre el QuerySet
        print(f"{cita.paciente.nombre_completo} - {cita.fecha} {cita.hora} - {cita.motivo}")
 
            
    return render(request, 'funcionalidades/agenda_citas.html', {
       # 'pacientes': pacientes,
        # 'citas_pendientes': citas_pendientes,
        'citas_pendientes_dentista': citas_pendientes_dentista
    })
             
       

@login_required
def crear_cita(request, paciente_id):
    paciente = get_object_or_404(CustomUser, id=paciente_id)
    dentistas = CustomUser.objects.filter(role="dentista")

    # Generar los horarios desde 08:00 hasta 19:00 con intervalos de 30 min
    horarios_disponibles = [
        (datetime.strptime("08:00", "%H:%M") + timedelta(minutes=30 * i)).strftime("%H:%M")
        for i in range(((19 - 8) * 60) // 30 + 1)
    ]

    if request.method == "POST":
        dentista_id = request.POST.get("dentista")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        motivo = request.POST.get("motivo")

        if not (dentista_id and fecha and hora and motivo):
            return JsonResponse({"status": "error", "message": "Todos los campos son obligatorios."})

        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora, "%H:%M").time()

        if fecha_obj < datetime.today().date():
            return JsonResponse({"status": "error", "message": "No puedes agendar citas en fechas pasadas."})

        dentista = get_object_or_404(CustomUser, id=dentista_id)

        # Verificar si el dentista ya tiene una cita en ese horario
        cita_existente = Cita.objects.filter(dentista=dentista, fecha=fecha, hora=hora).exists()

        if cita_existente:
            return JsonResponse({"status": "error", "message": "El dentista ya tiene una cita en esta hora."})

        # Crear la cita
        Cita.objects.create(
            paciente=paciente,
            dentista=dentista,
            fecha=fecha,
            hora=hora,
            motivo=motivo,
            estado="pendiente"
        )
        return JsonResponse({"status": "success", "message": "Cita creada con éxito."})

    return render(request, "funcionalidades/crear_cita.html", {
        "paciente": paciente,
        "dentistas": dentistas,
        "horarios_disponibles": horarios_disponibles
    })

@login_required
def ver_citas_pendientes(request, paciente_id):
    paciente = get_object_or_404(CustomUser, id=paciente_id)  # Obtener el paciente por ID
    citas = Cita.objects.filter(paciente=paciente).order_by("fecha", "hora")  # Obtener citas pendientes

    return render(request, "funcionalidades/ver_citas.html", {"paciente": paciente, "citas": citas})

@login_required
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    dentistas = CustomUser.objects.filter(role="dentista")

    # Lista de horarios en intervalos de 30 minutos
    horarios = [
        "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00"
    ]

    if request.method == "POST":
        dentista_id = request.POST.get("dentista")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        motivo = request.POST.get("motivo")

        if not (dentista_id and fecha and hora and motivo):
            return JsonResponse({"error": "Todos los campos son obligatorios."}, status=400)

        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora, "%H:%M").time()

        if fecha_obj < datetime.today().date():
            return JsonResponse({"error": "No puedes agendar citas en fechas pasadas."}, status=400)

        if hora not in horarios:
            return JsonResponse({"error": "La hora seleccionada no es válida."}, status=400)

        dentista = get_object_or_404(CustomUser, id=dentista_id)

        cita.dentista = dentista
        cita.fecha = fecha_obj
        cita.hora = hora_obj
        cita.motivo = motivo
        cita.save()

        return JsonResponse({"success": "Cita editada con éxito."})

    return render(request, "funcionalidades/editar_cita.html", {
        "cita": cita,
        "dentistas": dentistas,
        "horarios": horarios
    })

@login_required
def eliminar_cita(request, cita_id):
    if request.method == "POST":
        cita = get_object_or_404(Cita, id=cita_id)
        cita.delete()
        return JsonResponse({"success": "Cita eliminada con éxito."})
    
    return JsonResponse({"error": "Método no permitido."}, status=405)



#MODULO GESTION HISTORIA CLINICA

@login_required
def gestion_historia_clinica(request):
    User = get_user_model()
    
    # Obtener pacientes (CustomUser con role='paciente')
    pacientes = User.objects.filter(role='paciente').order_by('last_name', 'first_name')
    
    # Obtener historias clínicas existentes
    historias = HistoriaClinica.objects.select_related('paciente').all()
    
    return render(request, 'funcionalidades/gestion_historia_clinica.html', {
        'pacientes': pacientes,
        'historias': historias
    })

@login_required
def crear_historia_clinica(request, customuser_id):
    paciente = get_object_or_404(CustomUser, id=customuser_id)
    
    if request.method == "POST":
        try:
            # Crear la historia clínica
            historia = HistoriaClinica.objects.create(
                paciente=paciente,
                fecha_inicio=request.POST.get('fecha'),
                tratamiento=request.POST.get('tratamiento'),
                duracion_tratamiento=request.POST.get('duracion')
            )               
            
            messages.success(request, "¡Historia clínica creada con éxito!")
            # Pasamos el ID de la historia creada al template
            return render(request, 'funcionalidades/crear_historia_clinica.html', {
                'paciente': paciente,
                'historia_id': historia.id  # <-- Aquí pasamos el ID
            })
            
        except Exception as e:
            messages.error(request, f"Error al crear historia clínica: {str(e)}")
            return redirect('crear_historia_clinica', customuser_id=customuser_id)
    
    return render(request, 'funcionalidades/crear_historia_clinica.html', {
        'paciente': paciente
    })
    
@login_required
def modificar_historia_clinica(request, historia_id):
    historia = get_object_or_404(HistoriaClinica, id=historia_id)

    if request.method == "POST":
        # Obtener los datos del formulario
        historia.fecha_inicio = request.POST.get('fecha_inicio')
        historia.tratamiento = request.POST.get('tratamiento')
        historia.duracion_tratamiento = request.POST.get('duracion_tratamiento')

        # Solo capturar datos adicionales si los usas en otro modelo (esto es opcional)
        avance = request.POST.get('avance_tratamiento')
        medicamentos = request.POST.get('medicamentos')
        fecha_consulta = request.POST.get('fecha_consulta')

        # Guardar cambios en la historia clínica
        historia.save()

        # Opcional: guardar evolución en otro modelo si lo tienes (a futuro)

        messages.success(request, "Historia clínica actualizada correctamente.")
        return redirect('gestion_historia_clinica')

    return render(request, 'funcionalidades/modificar_historia_clinica.html', {
        'historia': historia
    })

@login_required
def modificar_historia_clinica(request, historia_id):
    historia = get_object_or_404(HistoriaClinica, id=historia_id)

    if request.method == "POST":
        # Actualizar historia base
        historia.fecha_inicio = request.POST.get('fecha_inicio')
        historia.tratamiento = request.POST.get('tratamiento')
        historia.duracion_tratamiento = request.POST.get('duracion_tratamiento')
        historia.save()

        # Guardar evolución solo si hay datos
        fecha_consulta = request.POST.get('fecha_consulta')
        avance = request.POST.get('avance_tratamiento')
        medicamentos = request.POST.get('medicamentos')

        if fecha_consulta and avance:
            EvolucionClinica.objects.create(
                historia=historia,
                fecha_consulta=fecha_consulta,
                avance_tratamiento=avance,
                medicamentos=medicamentos
            )

        messages.success(request, "Historia clínica actualizada correctamente.")
        return redirect('gestion_historia_clinica')

    # Obtener todas las evoluciones relacionadas
    evoluciones = historia.evoluciones.order_by('-fecha_consulta')

    return render(request, 'funcionalidades/modificar_historia_clinica.html', {
        'historia': historia,
        'evoluciones': evoluciones
    })


# MODULO PARA PACIENTES
@login_required
def gestion_modulo_paciente(request):
    """
    Vista principal del módulo de paciente (reemplaza a paciente_dashboard)
    """
    if not hasattr(request.user, 'role') or request.user.role != 'paciente':
        logout(request)
        return redirect('login')
    
    try:
        # Obtener próxima cita (la primera futura)
        proxima_cita = Cita.objects.filter(
            paciente=request.user,
            fecha__gte=date.today()
        ).select_related('dentista').order_by('fecha', 'hora').first()
        
        # Obtener la historia clínica con sus evoluciones
        historia_clinica = HistoriaClinica.objects.filter(
            paciente=request.user
        ).prefetch_related('evoluciones').first()
        
        # Obtener citas recientes para el resumen (últimas 3)
        citas_recientes = Cita.objects.filter(
            paciente=request.user
        ).select_related('dentista').order_by('-fecha', '-hora')[:3]
        
        return render(request, 'funcionalidades/gestion_modulo_paciente.html', {
            'usuario': request.user,
            'proxima_cita': proxima_cita,
            'historia_clinica': historia_clinica,
            'citas_recientes': citas_recientes
        })
        
    except Exception as e:
        # Loggear el error en producción
        messages.error(request, "Error al cargar tu información")
        return render(request, 'funcionalidades/gestion_modulo_paciente.html', {
            'usuario': request.user
        })

@login_required
def paciente_mis_citas(request):
    """
    Vista que muestra todas las citas del paciente
    Redirige siempre al módulo principal al volver
    """
    if not hasattr(request.user, 'role') or request.user.role != 'paciente':
        logout(request)
        return redirect('login')
    
    try:
        citas = Cita.objects.filter(
            paciente=request.user
        ).select_related('dentista').order_by('-fecha', '-hora')
        
        return render(request, 'funcionalidades/paciente_mis_citas.html', {
            'usuario': request.user,
            'citas': citas,
            'total_citas': citas.count()
        })
        
    except Exception as e:
        messages.error(request, "Error al cargar tus citas")
        return redirect('gestion_modulo_paciente')

@login_required
def paciente_mi_historia(request):
    """
    Vista que muestra la historia clínica completa del paciente
    Redirige siempre al módulo principal al volver
    """
    if not hasattr(request.user, 'role') or request.user.role != 'paciente':
        logout(request)
        return redirect('login')
    
    try:
        historia_clinica = HistoriaClinica.objects.filter(
            paciente=request.user
        ).prefetch_related('evoluciones').first()
        
        evoluciones = None
        if historia_clinica:
            evoluciones = historia_clinica.evoluciones.order_by('-fecha_consulta')
        
        return render(request, 'funcionalidades/paciente_mi_historia.html', {
            'usuario': request.user,
            'historia_clinica': historia_clinica,
            'evoluciones': evoluciones,
            'total_evoluciones': evoluciones.count() if evoluciones else 0
        })
        
    except Exception as e:
        messages.error(request, "Error al cargar tu historia clínica")
        return redirect('gestion_modulo_paciente')
    
          