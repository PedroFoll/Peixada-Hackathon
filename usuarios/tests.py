from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class CadastroViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('usuarios:cadastro')
        self.dados_validos = {
            'first_name': 'João',
            'last_name': 'Silva',
            'username': 'joaosilva',
            'email': 'joao@teste.com',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
        }

    def test_cadastro_get_exibe_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/cadastro.html')

    def test_cadastro_post_valido_cria_usuario_e_redireciona(self):
        response = self.client.post(self.url, self.dados_validos)
        self.assertRedirects(response, reverse('financas:dashboard'), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username='joaosilva').exists())

    def test_senha_e_armazenada_com_hash(self):
        self.client.post(self.url, self.dados_validos)
        usuario = User.objects.get(username='joaosilva')
        self.assertTrue(usuario.password.startswith('pbkdf2_'))
        self.assertNotEqual(usuario.password, self.dados_validos['password1'])

    def test_cadastro_post_valido_loga_usuario_automaticamente(self):
        self.client.post(self.url, self.dados_validos)
        response = self.client.get(reverse('financas:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_cadastro_post_email_duplicado_exibe_erro(self):
        User.objects.create_user(username='outro', email='joao@teste.com', password='qualquer')
        response = self.client.post(self.url, self.dados_validos)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'Já existe uma conta com este e-mail.')

    def test_cadastro_post_senhas_divergentes_exibe_erro(self):
        dados = {**self.dados_validos, 'password2': 'SenhaDiferente!99'}
        response = self.client.post(self.url, dados)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='joaosilva').exists())

    def test_cadastro_post_campos_obrigatorios_ausentes_exibe_erro(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='joaosilva').exists())

    def test_cadastro_usuario_autenticado_redireciona_para_dashboard(self):
        User.objects.create_user(username='logado', password='Senha@123')
        self.client.login(username='logado', password='Senha@123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('financas:dashboard'), fetch_redirect_response=False)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('usuarios:login')
        self.usuario = User.objects.create_user(
            username='testeuser',
            password='Senha@Forte123',
            email='teste@teste.com',
        )

    def test_login_get_exibe_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')

    def test_login_post_credenciais_validas_redireciona(self):
        response = self.client.post(self.url, {
            'username': 'testeuser',
            'password': 'Senha@Forte123',
        })
        self.assertRedirects(response, reverse('financas:dashboard'), fetch_redirect_response=False)

    def test_login_post_credenciais_invalidas_exibe_erro(self):
        response = self.client.post(self.url, {
            'username': 'testeuser',
            'password': 'senhaerrada',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_usuario_autenticado_redireciona_para_dashboard(self):
        self.client.login(username='testeuser', password='Senha@Forte123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('financas:dashboard'), fetch_redirect_response=False)

    def test_login_post_username_ausente_nao_autentica(self):
        response = self.client.post(self.url, {'username': '', 'password': 'Senha@Forte123'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('usuarios:logout')
        self.usuario = User.objects.create_user(
            username='testeuser',
            password='Senha@Forte123',
        )

    def test_logout_post_encerra_sessao_e_redireciona(self):
        self.client.login(username='testeuser', password='Senha@Forte123')
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('usuarios:login'))
        # Após logout, acesso ao perfil deve redirecionar para login
        perfil_response = self.client.get(reverse('usuarios:perfil'))
        self.assertRedirects(
            perfil_response,
            f"{reverse('usuarios:login')}?next={reverse('usuarios:perfil')}",
        )

    def test_logout_get_nao_encerra_sessao(self):
        self.client.login(username='testeuser', password='Senha@Forte123')
        response = self.client.get(self.url)
        # GET no logout deve retornar 405 (método não permitido) ou redirecionar sem encerrar
        self.assertIn(response.status_code, [302, 405])

    def test_logout_sem_autenticacao_redireciona(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('usuarios:login'))

