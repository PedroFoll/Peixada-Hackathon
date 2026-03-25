# Referência Chart.js — Exemplos e Templates

## Inclusão via CDN (padrão do projeto)

```html
<!-- Incluir ANTES do script principal, no <head> ou fim do <body> -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
```

---

## Estrutura base de um gráfico

```javascript
const ctx = document.getElementById('meuGrafico').getContext('2d');

const meuGrafico = new Chart(ctx, {
  type: 'bar',          // 'bar' | 'line' | 'pie' | 'doughnut' | 'radar' | 'polarArea' | 'scatter'
  data: {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
    datasets: [{
      label: 'Rótulo do Dataset',
      data: [10, 20, 30, 40, 50],
      backgroundColor: 'rgba(59, 130, 246, 0.6)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 1,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
  }
});
```

---

## Paleta de Cores Padrão do Projeto

```javascript
// Use estas cores para consistência visual com o design system
const CORES = {
  receita:     { bg: 'rgba(34, 197, 94, 0.6)',   border: 'rgb(34, 197, 94)'   },
  despesa:     { bg: 'rgba(239, 68, 68, 0.6)',    border: 'rgb(239, 68, 68)'   },
  neutro:      { bg: 'rgba(107, 114, 128, 0.6)',  border: 'rgb(107, 114, 128)' },
  primario:    { bg: 'rgba(59, 130, 246, 0.6)',   border: 'rgb(59, 130, 246)'  },
  aviso:       { bg: 'rgba(245, 158, 11, 0.6)',   border: 'rgb(245, 158, 11)'  },
  categorias: [
    'rgba(59, 130, 246, 0.7)',
    'rgba(34, 197, 94, 0.7)',
    'rgba(239, 68, 68, 0.7)',
    'rgba(245, 158, 11, 0.7)',
    'rgba(168, 85, 247, 0.7)',
    'rgba(20, 184, 166, 0.7)',
    'rgba(249, 115, 22, 0.7)',
  ]
};
```

---

## Gráfico de Barras — Comparação por Categoria

```javascript
new Chart(document.getElementById('graficoBarras').getContext('2d'), {
  type: 'bar',
  data: {
    labels: labels,   // ex: ['Alimentação', 'Transporte', 'Lazer']
    datasets: [{
      label: 'Despesas por Categoria (R$)',
      data: valores,
      backgroundColor: CORES.categorias,
      borderColor: CORES.categorias.map(c => c.replace('0.7', '1')),
      borderWidth: 1,
      borderRadius: 6,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (item) => ` R$ ${item.raw.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (v) => 'R$ ' + v.toLocaleString('pt-BR')
        }
      }
    }
  }
});
```

---

## Gráfico de Linhas — Tendência ao Longo do Tempo

```javascript
new Chart(document.getElementById('graficoLinha').getContext('2d'), {
  type: 'line',
  data: {
    labels: meses,    // ex: ['Jan', 'Fev', 'Mar', ...]
    datasets: [
      {
        label: 'Receitas',
        data: receitas,
        borderColor: CORES.receita.border,
        backgroundColor: CORES.receita.bg,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 8,
      },
      {
        label: 'Despesas',
        data: despesas,
        borderColor: CORES.despesa.border,
        backgroundColor: CORES.despesa.bg,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 8,
      }
    ]
  },
  options: {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (item) => ` ${item.dataset.label}: R$ ${item.raw.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { callback: (v) => 'R$ ' + v.toLocaleString('pt-BR') }
      }
    }
  }
});
```

---

## Gráfico de Pizza / Doughnut — Distribuição Percentual

```javascript
new Chart(document.getElementById('graficoPizza').getContext('2d'), {
  type: 'doughnut',   // ou 'pie'
  data: {
    labels: categorias,
    datasets: [{
      data: valores,
      backgroundColor: CORES.categorias,
      borderWidth: 2,
      hoverOffset: 8,
    }]
  },
  options: {
    responsive: true,
    cutout: '60%',    // remova para gráfico de pizza sólida
    plugins: {
      legend: { position: 'bottom' },
      tooltip: {
        callbacks: {
          label: (item) => {
            const total = item.dataset.data.reduce((a, b) => a + b, 0);
            const pct = ((item.raw / total) * 100).toFixed(1);
            return ` ${item.label}: R$ ${item.raw.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} (${pct}%)`;
          }
        }
      }
    }
  }
});
```

---

## Gráfico de Radar — Comparação Multivariável

```javascript
new Chart(document.getElementById('graficoRadar').getContext('2d'), {
  type: 'radar',
  data: {
    labels: ['Alimentação', 'Transporte', 'Saúde', 'Lazer', 'Educação'],
    datasets: [
      {
        label: 'Este mês',
        data: [400, 200, 150, 300, 100],
        backgroundColor: 'rgba(59, 130, 246, 0.3)',
        borderColor: 'rgb(59, 130, 246)',
        pointBackgroundColor: 'rgb(59, 130, 246)',
      },
      {
        label: 'Mês anterior',
        data: [350, 180, 200, 250, 120],
        backgroundColor: 'rgba(107, 114, 128, 0.2)',
        borderColor: 'rgb(107, 114, 128)',
        pointBackgroundColor: 'rgb(107, 114, 128)',
      }
    ]
  },
  options: {
    responsive: true,
    scales: {
      r: {
        beginAtZero: true,
        ticks: { callback: (v) => 'R$ ' + v }
      }
    }
  }
});
```

---

## Integração com Django — Dados via data-* (padrão obrigatório)

No template Django:
```html
<canvas id="graficoSaldo"
        data-labels='{{ labels_json|escapejs }}'
        data-receitas='{{ receitas_json|escapejs }}'
        data-despesas='{{ despesas_json|escapejs }}'
        height="300">
</canvas>
```

Na view Django:
```python
import json
from django.db.models import Sum, Q

def dashboard(request):
    dados = (
        Transacao.objects
        .filter(usuario=request.user)
        .values('data__month')
        .annotate(
            receitas=Sum('valor', filter=Q(tipo='receita')),
            despesas=Sum('valor', filter=Q(tipo='despesa')),
        )
        .order_by('data__month')
    )
    meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

    context = {
        'labels_json':   json.dumps([meses[d['data__month'] - 1] for d in dados]),
        'receitas_json': json.dumps([float(d['receitas'] or 0) for d in dados]),
        'despesas_json': json.dumps([float(d['despesas'] or 0) for d in dados]),
    }
    return render(request, 'financas/dashboard.html', context)
```

No script do template:
```javascript
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('graficoSaldo');
  // Lê dados dos data-* attributes — NUNCA interpolar variáveis Django diretamente no JS
  const labels   = JSON.parse(canvas.dataset.labels);
  const receitas = JSON.parse(canvas.dataset.receitas);
  const despesas = JSON.parse(canvas.dataset.despesas);

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: { labels, datasets: [
      { label: 'Receitas', data: receitas, ...CORES.receita },
      { label: 'Despesas', data: despesas, ...CORES.despesa },
    ]},
    options: { responsive: true }
  });
});
```

---

## Atualização Dinâmica do Gráfico (sem recarregar a página)

```javascript
// Referência ao gráfico criado
const grafico = new Chart(ctx, config);

// Atualizar dados via fetch (endpoint Django que retorna JSON)
async function atualizarGrafico(periodo) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const response = await fetch(`/financas/dados-grafico/?periodo=${periodo}`, {
    headers: { 'X-CSRFToken': csrfToken }
  });
  if (!response.ok) return;
  const dados = await response.json();

  grafico.data.labels               = dados.labels;
  grafico.data.datasets[0].data     = dados.receitas;
  grafico.data.datasets[1].data     = dados.despesas;
  grafico.update('active');  // anima a transição
}

// Vincular a seletor de período
document.querySelectorAll('[data-periodo]').forEach(btn => {
  btn.addEventListener('click', () => atualizarGrafico(btn.dataset.periodo));
});
```

---

## Opções Globais Recomendadas

```javascript
// Aplicar antes de criar qualquer gráfico (no início do script)
Chart.defaults.font.family    = "'Inter', sans-serif";
Chart.defaults.font.size      = 13;
Chart.defaults.color          = '#6b7280';   // --color-text-muted
Chart.defaults.animation.duration = 600;
```

---

## Wrapper HTML Responsivo para Canvas

```html
<!-- Sempre envolva o canvas em um container com altura controlada -->
<div class="card shadow-sm">
  <div class="card-header d-flex justify-content-between align-items-center">
    <h6 class="mb-0 fw-semibold">Receitas vs Despesas</h6>
    <div class="btn-group btn-group-sm" role="group">
      <button class="btn btn-outline-secondary active" data-periodo="mensal">Mensal</button>
      <button class="btn btn-outline-secondary" data-periodo="anual">Anual</button>
    </div>
  </div>
  <div class="card-body" style="position: relative; height: 300px;">
    <canvas id="graficoSaldo"></canvas>
  </div>
</div>
```

> **Atenção**: defina `height` no elemento pai, não no `<canvas>` diretamente. Isso respeita o `responsive: true` do Chart.js e evita distorções.

---

## Checklist de Qualidade — Chart.js

- [ ] `responsive: true` e `maintainAspectRatio: false` (quando o container tem altura fixa)
- [ ] Tooltips formatados em R$ com `toLocaleString('pt-BR')`
- [ ] Dados passados via `data-*` attributes (nunca interpolação JS direta com Django)
- [ ] Cores do projeto usadas (`CORES` object) — sem cores aleatórias hardcoded
- [ ] Gráfico destruído/recriado se o elemento pode ser rerenderizado (`chart.destroy()`)
- [ ] Opções globais de fonte e cor aplicadas antes da criação dos gráficos
- [ ] Canvas envolto em container com `position: relative` e altura definida
