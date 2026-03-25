# Peixada Financas

Aplicacao web de gestao financeira pessoal para cadastro e analise de receitas e despesas, com dashboard interativo e controle por usuario autenticado.

## 1. Estrutura do README

### 1.1. Titulo do Projeto

Nome: Peixada Financas

Descricao breve:
Sistema para organizar movimentacoes financeiras pessoais, com categorizacao, filtros avancados, recorrencia e visualizacao grafica dos dados.

### 1.2. Tecnologias Utilizadas

- Python 3.13
- Django 5.1
- SQLite (banco padrao do projeto)
- Bootstrap 5.3.3
- Bootstrap Icons 1.11.3
- Chart.js 4.4.4
- python-dotenv 1.0.1
- Pillow 11.1.0

Dependencias Python atuais em requirements.txt:

- Django==5.1
- python-dotenv==1.0.1
- Pillow==11.1.0
- asgiref==3.11.1
- sqlparse==0.5.5
- tzdata==2025.3

### 1.3. Instalacao

1. Clone o repositorio:

	git clone https://github.com/usuario/nome-do-repositorio.git
	cd nome-do-repositorio

2. Crie e ative o ambiente virtual:

	Windows:
	python -m venv venv
	venv\Scripts\activate

	Mac/Linux:
	python3 -m venv venv
	source venv/bin/activate

3. Instale as dependencias:

	pip install -r requirements.txt

4. Configure variaveis de ambiente (arquivo .env na raiz):

	SECRET_KEY=sua_chave_secreta
	DEBUG=True
	ALLOWED_HOSTS=127.0.0.1,localhost

5. Execute as migracoes do banco:

	python manage.py migrate

6. (Opcional) Crie um superusuario:

	python manage.py createsuperuser

7. Rode o servidor:

	python manage.py runserver

8. Acesse no navegador:

	http://127.0.0.1:8000

### 1.4. Uso

Depois de iniciar o servidor:

1. Crie sua conta em /usuarios/cadastro/ ou faca login.
2. Cadastre categorias de receitas e despesas.
3. Registre movimentacoes na tela de Dashboard ou Lancamentos.
4. Use recorrencia diaria, semanal ou mensal quando necessario.
5. Acompanhe saldo, receitas e despesas no dashboard com graficos.
6. Filtre a tabela de lancamentos por periodo, categoria, tipo e descricao.

Funcionalidades principais:

- Cadastro de categorias por usuario
- Cadastro e edicao de movimentacoes financeiras
- Suporte a recorrencia com geracao automatica de ocorrencias
- Dashboard com comparativos e distribuicao por categoria
- Tabela de lancamentos com filtros e paginacao
- Exclusao com confirmacao e mensagens de feedback

### 1.5. Exemplos de Uso

Exemplo A: cadastrar despesa pontual

1. Acesse Lancamentos.
2. Clique em Nova Movimentacao.
3. Selecione tipo Despesa.
4. Informe categoria, valor e data.
5. Salve.

Exemplo B: cadastrar receita recorrente mensal

1. Abra o modal Nova Movimentacao.
2. Selecione tipo Receita.
3. Marque recorrente.
4. Escolha frequencia mensal e dia do mes.
5. Salve. O sistema criara novas ocorrencias apenas ate a data atual.

Exemplo C: analisar dados no dashboard

1. Acesse Dashboard.
2. Troque o filtro para semanal, mensal, anual ou personalizado.
3. Veja os graficos de comparacao e distribuicao por categoria.

### 1.6. Testes

Este projeto utiliza a estrutura de testes nativa do Django (unittest/TestCase).

Executar todos os testes:

python manage.py test

Executar com verbosidade:

python manage.py test -v 2

Executar somente um app:

python manage.py test financas
python manage.py test usuarios

Observacao sobre pytest:

- O fluxo oficial atual do projeto e com unittest via Django.
- Se desejar usar pytest, e necessario adicionar pytest e pytest-django ao projeto.

### 1.7. Contribuicao

1. Faca fork do repositorio.
2. Crie uma branch para sua alteracao:

	git checkout -b feature/nome-da-feature

3. Faça commit:

	git commit -am "Adiciona nova feature"

4. Envie para seu remoto:

	git push origin feature/nome-da-feature

5. Abra um Pull Request com:

- contexto da alteracao
- problema resolvido
- impacto esperado
- evidencias (prints, videos, logs ou testes)

### 1.8. Licenca

No momento, nao existe arquivo LICENSE no repositorio.

Recomendacao: adicionar uma licenca explicita (exemplo: MIT) para definir claramente regras de uso, distribuicao e contribuicao.

## 2. Documentacao Tecnica

### 2.1. Arquitetura do Sistema

Arquitetura monolitica Django com renderizacao server-side:

- Backend: Django (apps financas e usuarios)
- Frontend: templates Django + Bootstrap + JavaScript vanilla
- Banco: SQLite
- Graficos: Chart.js consumindo dados preparados no backend

Separacao por responsabilidades:

- models.py: entidades e estrutura de dados
- forms.py: validacao de entrada
- services.py: regras de negocio e agregacoes
- views.py: orquestracao de requisicoes e respostas
- templates: renderizacao HTML

### 2.2. Fluxo de Dados

Fluxo principal:

1. Usuario envia formulario (ex: criar movimentacao).
2. View recebe request autenticada.
3. Form valida os dados.
4. View salva dados via ORM.
5. Services processam regras (ex: recorrencia e agregacoes).
6. Dados sao consultados para dashboard/tabela.
7. View serializa dados de graficos em JSON para template.
8. Frontend (Chart.js) renderiza visualizacoes.

### 2.3. Estrutura do Banco de Dados

Modelo Categoria:

- usuario (FK para User)
- nome
- cor
- icone
- restricao de unicidade por usuario e nome

Modelo Movimentacao:

- usuario (FK para User)
- categoria (FK para Categoria)
- descricao (opcional)
- valor (DecimalField)
- tipo (receita ou despesa)
- data
- recorrente (boolean)
- frequencia (diaria, semanal, mensal)
- dias_semana (para recorrencia semanal)
- dia_mes (para recorrencia mensal)
- data_limite
- movimentacao_origem (auto relacionamento para ocorrencias)
- criado_em

Indices e ordenacao:

- indice composto: usuario, data, tipo
- ordenacao padrao: data desc e criado_em desc

### 2.4. Descricao das Funcionalidades

- Cadastro, edicao e exclusao de categorias
- Bloqueio de exclusao de categoria com movimentacoes vinculadas
- Cadastro de receitas e despesas pontuais
- Cadastro de receitas e despesas recorrentes
- Geracao automatica de ocorrencias recorrentes ate a data atual
- Dashboard com:
  - saldo
  - totais de receitas e despesas
  - comparacao mensal receita x despesa
  - distribuicao por categoria
- Tabela de lancamentos com filtros:
  - data inicial/final
  - categoria
  - tipo
  - descricao
- Autenticacao, perfil e alteracao de senha
- Pagina 404 personalizada

### 2.5. Fluxo de Execucao

Fluxo de uma requisicao tipica autenticada:

1. LoginRequiredMixin ou login_required valida autenticacao.
2. View filtra dados por request.user para isolamento entre usuarios.
3. Services realizam calculos no banco usando aggregate/annotate.
4. Template renderiza resultados.
5. JavaScript da pagina ativa componentes visuais (modais, graficos, mascara monetaria).

Fluxo de recorrencia:

1. Movimentacao recorrente e salva.
2. Services calculam datas validas conforme frequencia.
3. Ocorrencias sao criadas apenas se ainda nao existirem.
4. Nao sao geradas ocorrencias futuras alem da data atual.

## 3. Detalhamento de Recursos

### Estrutura de pastas relevante

.
|- core/                  Configuracoes globais do Django (settings, urls, wsgi, asgi)
|- financas/              App principal de dominio financeiro
|  |- management/commands Comandos utilitarios (seed, limpar_seed, processar_recorrencias)
|  |- models.py           Entidades Categoria e Movimentacao
|  |- services.py         Regras de negocio e consultas agregadas
|  |- views.py            Dashboard, lancamentos e categorias
|- usuarios/              App de autenticacao e perfil
|- templates/             Base, paginas e parciais
|- static/                CSS e JavaScript globais/paginas
|- manage.py              Entrypoint administrativo do Django
|- requirements.txt       Dependencias Python

### Comandos uteis de desenvolvimento

- python manage.py runserver
- python manage.py makemigrations
- python manage.py migrate
- python manage.py seed --usuario admin
- python manage.py limpar_seed --usuario admin
- python manage.py processar_recorrencias
- python manage.py test

### Boas praticas adotadas no projeto

- ORM Django em vez de SQL concatenado
- validacoes centralizadas em forms
- logica de negocio centralizada em services
- isolamento de dados por usuario autenticado
- protecoes de seguranca basicas no settings (X-Frame-Options, no sniff)

---

Se este README estiver sendo usado como guia para onboarding da equipe, recomenda-se manter esta documentacao atualizada sempre que houver mudancas em modelos, rotas, comandos ou regras de negocio.
