---
agent: agent
description: 'Revisão completa do projeto Django antes da apresentação para a banca. Valida arquitetura, segurança, qualidade de código, testes e documentação.'
tools: ['read_file', 'file_search', 'grep_search', 'get_errors', 'run_in_terminal']
---

Você é um arquiteto de software sênior revisando o projeto antes da apresentação para a banca avaliadora. Faça uma revisão completa e sistemática seguindo as etapas abaixo. Seja direto e objetivo — aponte problemas concretos com localização exata (arquivo e linha quando possível) e sugira a correção.

## Etapa 1 — Estrutura do Projeto

Explore o workspace e verifique:
- Os apps estão organizados por domínio de negócio?
- Existe separação de responsabilidades: `models.py`, `views.py`, `forms.py`, `services.py`, `urls.py`, `templates/`?
- O `settings.py` está configurado corretamente (INSTALLED_APPS, DATABASES, TEMPLATES, STATIC_FILES)?
- Existe um `requirements.txt` atualizado?

Reporte qualquer desvio da estrutura esperada.

## Etapa 2 — Modelos e Banco de Dados

Leia todos os `models.py` e verifique:
- [ ] Todos os modelos têm `__str__` definido?
- [ ] Campos monetários usam `DecimalField` (não `FloatField`)?
- [ ] Relacionamentos (`ForeignKey`, `ManyToManyField`, `OneToOneField`) estão com `on_delete` correto?
- [ ] Campos usados em filtros frequentes têm `db_index=True` ou índices compostos no `Meta`?
- [ ] Existe pasta `migrations/` com migrações geradas?

Liste qualquer modelo que viola estas práticas.

## Etapa 3 — Segurança

Leia as views, forms e settings e verifique:
- [ ] Todas as views com dados do usuário têm `LoginRequiredMixin`?
- [ ] Os dados são filtrados por `request.user` em todas as queries relevantes?
- [ ] `get_object_or_404` é usado com filtro por `usuario=request.user` ao buscar objetos individuais?
- [ ] Todos os formulários POST têm `{% csrf_token %}` no template?
- [ ] Não há SQL concatenado com f-strings ou % format (vulnerabilidade de injeção)?
- [ ] `SECRET_KEY` não está hardcoded sem uso de variável de ambiente?

Classifique cada problema encontrado como: **CRÍTICO**, **ALTO** ou **MÉDIO**.

## Etapa 4 — Performance e Queries

Leia as views e verifique:
- [ ] Há uso de `select_related()` em acessos a ForeignKey no template?
- [ ] Há uso de `prefetch_related()` em acessos a M2M ou reverse FK?
- [ ] Listagens grandes têm paginação (`Paginator` ou `paginate_by` em ListView)?
- [ ] Cálculos de total/soma usam `aggregate()`/`annotate()` no banco (não em Python)?
- [ ] Nenhuma query dentro de loop em template ou view?

Indique os arquivos e views com problemas de N+1 ou falta de paginação.

## Etapa 5 — Testes

Verifique a existência e cobertura de testes:
- [ ] Existe pasta `tests/` ou arquivo `tests.py` em cada app?
- [ ] Há testes de models (validações, `__str__`, métodos)?
- [ ] Há testes de views (status HTTP, controle de acesso, contexto)?
- [ ] Há teste de isolamento de dados (usuário A não acessa dados do usuário B)?
- [ ] Há testes de forms?

Execute os testes e reporte falhas:
```
python manage.py test --verbosity=2
```

## Etapa 6 — Qualidade de Código

Verifique:
- [ ] Não há lógica de negócio em views (deve estar em `services.py` ou methods do model)?
- [ ] URLs têm `name=` definido em todos os endpoints?
- [ ] Templates usam `{% url 'nome' %}` (não URLs hardcoded)?
- [ ] Não há código comentado ou `print()` de debug esquecido?
- [ ] `requirements.txt` está presente e atualizado?

## Etapa 7 — Execução Local

Verifique se é possível rodar o projeto do zero:
- [ ] `requirements.txt` existe?
- [ ] Migrações existem e são aplicáveis?
- [ ] Existe instrução de como criar o superusuário?
- [ ] O README descreve os passos de execução?

## Etapa 8 — Relatório Final

Ao final, gere um relatório estruturado com:

### ✅ Pontos Fortes
Liste o que está bem implementado.

### ⚠️ Problemas Encontrados
Para cada problema:
- **Localização**: arquivo e linha
- **Severidade**: CRÍTICO / ALTO / MÉDIO / BAIXO
- **Descrição**: o que está errado
- **Correção sugerida**: como resolver

### 📋 Checklist de Prontidão para a Banca
| Item | Status |
|------|--------|
| Estrutura de projeto organizada | ✅ / ❌ |
| Modelos com boas práticas | ✅ / ❌ |
| Segurança implementada | ✅ / ❌ |
| Sem N+1 queries críticos | ✅ / ❌ |
| Testes passando | ✅ / ❌ |
| README com instruções de execução | ✅ / ❌ |
| Aplicação rodando localmente | ✅ / ❌ |

### 🎯 Prioridade de Correções
Liste os 3 itens mais críticos a corrigir antes da apresentação, em ordem de prioridade.
