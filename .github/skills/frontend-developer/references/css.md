# Referência CSS — Exemplos e Templates

## Variáveis CSS (design tokens)

```css
:root {
  /* Cores */
  --color-primary: #3b82f6;
  --color-primary-dark: #1e40af;
  --color-accent: #f59e0b;
  --color-success: #22c55e;
  --color-error: #ef4444;
  --color-warning: #f97316;
  --color-text: #1f2937;
  --color-text-muted: #6b7280;
  --color-bg: #ffffff;
  --color-bg-alt: #f3f4f6;
  --color-border: #e5e7eb;

  /* Tipografia */
  --font-sans: 'Inter', sans-serif;
  --font-display: 'Plus Jakarta Sans', sans-serif;
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  1.875rem;  /* 30px */
  --text-4xl:  2.25rem;   /* 36px */

  /* Espaçamentos (sistema 8pt) */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-6:  24px;
  --space-8:  32px;
  --space-12: 48px;
  --space-16: 64px;

  /* Bordas e sombras */
  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:   16px;
  --radius-full: 9999px;
  --shadow-sm:  0 1px 3px rgba(0,0,0,.1);
  --shadow-md:  0 4px 12px rgba(0,0,0,.1);
  --shadow-lg:  0 8px 24px rgba(0,0,0,.12);

  /* Transições */
  --transition-fast:   0.15s ease;
  --transition-normal: 0.2s ease;
  --transition-slow:   0.4s ease;
}
```

## Reset / Base

```css
/* === BASE === */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { font-size: 16px; scroll-behavior: smooth; }

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--color-text);
  background-color: var(--color-bg);
  line-height: 1.6;
}

img, video { max-width: 100%; display: block; }

a { color: var(--color-primary); text-decoration: none; }
a:hover { text-decoration: underline; }

button { cursor: pointer; font-family: inherit; }
```

## Layout com Flexbox

```css
/* === FLEXBOX UTILITÁRIOS === */
.flex         { display: flex; }
.flex-center  { display: flex; align-items: center; justify-content: center; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }
.flex-col     { display: flex; flex-direction: column; }
.flex-wrap    { flex-wrap: wrap; }
.gap-4        { gap: var(--space-4); }
.gap-6        { gap: var(--space-6); }
```

## Layout com CSS Grid

```css
/* === GRID === */

/* Grid responsivo automático (sem breakpoints) */
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
}

/* Grid de 12 colunas base */
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-4);
}

/* Layout de 2 colunas: conteúdo + sidebar */
.layout-sidebar {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-8);
}

@media (max-width: 768px) {
  .layout-sidebar { grid-template-columns: 1fr; }
}
```

## Responsividade Mobile-first

```css
/* === RESPONSIVIDADE === */

/* Container padrão */
.container {
  width: 100%;
  padding: 0 var(--space-4);
}

@media (min-width: 768px) {
  .container { padding: 0 var(--space-8); }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-12);
  }
}

/* Ocultar/mostrar por breakpoint */
.apenas-mobile  { display: block; }
.apenas-desktop { display: none; }

@media (min-width: 768px) {
  .apenas-mobile  { display: none; }
  .apenas-desktop { display: block; }
}
```

## Animações e Transições

```css
/* === ANIMAÇÕES === */

/* Transição hover padrão */
.btn {
  transition: transform var(--transition-normal),
              box-shadow var(--transition-normal),
              background-color var(--transition-normal);
}
.btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.4s ease forwards; }

/* Pulse (loading/skeleton) */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}
.skeleton {
  background-color: var(--color-border);
  border-radius: var(--radius-md);
  animation: pulse 1.5s ease-in-out infinite;
}

/* Slide In da esquerda */
@keyframes slideInLeft {
  from { transform: translateX(-100%); opacity: 0; }
  to   { transform: translateX(0); opacity: 1; }
}
```

## Componentes comuns

```css
/* === BOTÕES === */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-primary {
  background-color: var(--color-primary);
  color: #fff;
}
.btn-primary:hover { background-color: var(--color-primary-dark); }

/* === CARD === */
.card {
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-normal);
}
.card:hover { box-shadow: var(--shadow-md); }

/* === BADGE === */
.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 600;
}
.badge-primary { background-color: var(--color-primary); color: #fff; }
```