from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from login_app.models import CustomUser  # Importamos el modelo de usuario personalizado

class LoginTest(StaticLiveServerTestCase):
    def setUp(self):
        """Configura el navegador y crea un usuario antes de cada prueba"""
        self.driver = webdriver.Chrome()  # Asegúrate de que ChromeDriver está en tu PATH

        # Creamos un usuario de prueba con el modelo CustomUser
        CustomUser.objects.create_user(username="cristina", password="123456", role="admin")

    def tearDown(self):
        """Cierra el navegador después de cada prueba"""
        self.driver.quit()

    def test_login(self):
        """Prueba si un usuario puede iniciar sesión correctamente"""
        self.driver.get(self.live_server_url + "/login/")  # Ajusta la URL según tu proyecto

        # Encuentra los campos de usuario y contraseña
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")

        # Ingresa credenciales de prueba
        username_input.send_keys("cristina")
        password_input.send_keys("123456")
        password_input.send_keys(Keys.RETURN)

        time.sleep(5)  # Espera para la redirección (puedes reducirlo)
        
        # Imprimir la URL actual después del login
        print(f"URL después del login: {self.driver.current_url}")

        # Verifica que el usuario llegó al dashboard del administrador
        self.assertIn("/dashboard/admin/", self.driver.current_url)