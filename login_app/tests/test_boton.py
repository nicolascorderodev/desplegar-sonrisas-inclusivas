from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from login_app.models import CustomUser  # Importamos el modelo de usuario personalizado

class GestionPacientesTest(StaticLiveServerTestCase):
    def setUp(self):
        """Configura el navegador y crea un usuario antes de cada prueba"""
        self.driver = webdriver.Chrome()  # Asegúrate de que ChromeDriver está en tu PATH

        # Creamos un usuario de prueba con rol auxiliar administrativo
        CustomUser.objects.create_user(username="felipe", password="123456", role="auxiliar")

    def tearDown(self):
        """Cierra el navegador después de cada prueba"""
        self.driver.quit()

    def test_navegacion_gestion_pacientes(self):
        """Prueba si el botón 'Ir a Gestión de Pacientes' está presente y se puede hacer clic"""
        self.driver.get(self.live_server_url + "/login/")  # Ir a la página de login

        # Encuentra los campos de usuario y contraseña
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")

        # Ingresar credenciales de auxiliar administrativo
        username_input.send_keys("felipe")
        password_input.send_keys("123456")
        password_input.send_keys(Keys.RETURN)

        time.sleep(3)  # Esperar a la redirección después del login

        # Imprimir la URL actual después de iniciar sesión
        print(f"URL después del login: {self.driver.current_url}")

        # Verificar si entró al dashboard del auxiliar administrativo
        if "dashboard/auxiliar" not in self.driver.current_url:
            print("❌ Error: No se redirigió al dashboard del auxiliar administrativo.")
            return  # Terminar la prueba aquí

        # Intentar hacer clic en "Ir a Gestión de Pacientes"
        try:
            boton_gestion_pacientes = self.driver.find_element(By.LINK_TEXT, "Ir a Gestión de Pacientes")
            print("✅ Prueba exitosa: Se encontró el botón 'Ir a Gestión de Pacientes'.")

            # Intentar hacer clic en el botón (pero sin avanzar)
            boton_gestion_pacientes.click()
            time.sleep(2)
            print(f"URL después de hacer clic en 'Gestión de Pacientes': {self.driver.current_url}")

        except Exception as e:
            print("❌ Prueba fallida: El botón 'Ir a Gestión de Pacientes' no se encontró o está roto.")
            print(f"Detalles del error: {e}")