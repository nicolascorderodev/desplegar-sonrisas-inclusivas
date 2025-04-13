from django.db import models

class Contactanos(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=15)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)