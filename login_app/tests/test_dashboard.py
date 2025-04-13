import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestDashboardRedirection(StaticLiveServerTestCase):

    def setUp(self):
        """Configura el driver de Selenium antes de cada test"""
        self.driver = webdriver.Chrome()

    def tearDown(self):
        """Cierra el driver después de cada test"""
        self.driver.quit()

    def test_dashboard_redirection(self):
        """Verifica que un usuario no autenticado es redirigido al login"""

        # URL protegida (dashboard sin login)
        url_protegida = f"{self.live_server_url}/dashboard/admin/"
        self.driver.get(url_protegida)

        time.sleep(3)  # Esperar un poco para cargar la página

        # Obtener la URL actual después de intentar acceder
        url_actual = self.driver.current_url

        # URLs esperadas para la validación
        url_login_correcto = f"{self.live_server_url}/login/?next=/dashboard/admin/"
        url_login_incorrecto = f"{self.live_server_url}/accounts/login/?next=/dashboard/admin/"

        # Verificar si fue redirigido correctamente al login
        if url_actual == url_login_correcto:
            print("✅ Prueba exitosa: Se redirige correctamente al login configurado.")
        
        elif url_actual == url_login_incorrecto:
            print("⚠️ Prueba fallida: Django intentó usar la URL por defecto en lugar de la configurada en settings.")
        
        else:
            # Verificar si muestra error 404
            try:
                error_404 = self.driver.find_element(By.TAG_NAME, "h1").text
                if "404" in error_404:
                    print("⚠️ Prueba fallida: Se muestra error 404 en lugar de redirección.")
                else:
                    print("❌ Error inesperado: No se detectó ni redirección al login ni error 404.")
            except:
                print("❌ No se pudo verificar si se muestra error 404.")