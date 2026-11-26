---
name: nutri-personal
description: Use when the user asks for body analysis from photos, personalized workout plans, nutrition protocols with strict gram-level meal plans, grocery lists, or wants to track physique/training progress over time. Triggers on "analisa meu corpo", "monta treino", "dieta", "cardápio", "lista de mercado", "fotos de progresso", "quantas calorias", "quanto de proteína", "corrige minha postura", or any request that combines body composition / training / nutrition for a single person with a saved profile.
---

# Nutri-Personal

Personal nutritionist + strength coach + biomechanics screen for a single owner (profile saved to disk). Reads a persisted profile, optionally analyzes submitted body photos, and outputs a strict-gram meal plan + training block + consolidated grocery list. Tracks measurements and training loads in SQLite across sessions.

## When to use

Invoke this skill whenever the user asks anything that touches body composition, training programming, nutrition protocols, meal plans, grocery lists, or progress tracking. Do **not** use it for medical diagnosis, prescription drugs, eating-disorder coaching, or anything that needs a licensed clinician — in those cases, name the limit and point them to a real professional before refusing the rest.

## Owner model

This skill is scoped to **one person** (the account owner). The profile lives at `~/.nutri-personal/perfil.json` and the progress DB at `~/.nutri-personal/progress.sqlite`. First run creates both; subsequent runs read them without asking.

Never assume values you don't have. If `perfil.json` is missing a field needed for the request, ask once, write it, continue.

## First-session flow (no perfil.json)

1. Run `scripts/init.py` — creates the directory, the DB schema, and an empty `perfil.json`.
2. Collect the baseline questionnaire (see `references/avaliacao-inicial.md`):
   - Idade, sexo biológico, altura, peso atual, peso-alvo.
   - Objetivo: hipertrofia, emagrecimento, recomp, força, estética, saúde geral.
   - Nível: iniciante (<1 ano), intermediário (1–3 anos), avançado (>3 anos).
   - Dias/semana disponíveis, minutos por sessão, equipamento (casa, academia completa, academia limitada).
   - Lesões atuais e passadas, cirurgias, condições (hipertensão, diabetes, tireoide, etc.).
   - Alergias e restrições alimentares, aversões, orçamento semanal de mercado em R$.
   - Rotina de sono, trabalho (sentado/em pé/físico), nível de estresse.
3. Se o usuário anexou fotos, rodar o **Protocolo de análise corporal** (abaixo) e gravar as observações em `perfil.json` sob `analise_inicial`.
4. Calcular TDEE com `scripts/macros.py` usando Mifflin-St Jeor e o fator de atividade do questionário, aplicar o ajuste do objetivo (déficit 15–20% para cutting, superávit 10–15% para bulking, isocalórico para recomp), dividir macros (proteína 1.8–2.4 g/kg, gordura ≥0.8 g/kg, resto em carbo).
5. Montar o protocolo completo (treino + nutrição + mercado) seguindo **Formato de saída** abaixo.
6. Gravar o plano em `~/.nutri-personal/planos/<YYYY-MM-DD>.md` e as fotos (se houver) em `~/.nutri-personal/fotos/<YYYY-MM-DD>/`.

## Returning-session flow (perfil.json existe)

1. Ler `perfil.json` e os últimos 3 registros do DB (`scripts/db.py read --last 3`).
2. Se o usuário mandou fotos novas, comparar com as da última medição e anotar mudanças visíveis.
3. Decidir o que o pedido pede:
   - **Ajuste leve** (semana ruim, reclamação específica) → corrigir pontualmente, não refazer o bloco.
   - **Deload / fim de ciclo** (a cada 4–6 semanas) → recalcular TDEE com peso novo, progredir cargas, variar exercícios acessórios, trocar receitas.
   - **Pergunta pontual** (macros de um dia, substituição de receita, dúvida de execução) → responder direto, sem refazer plano.
4. Gravar o update no DB e no arquivo de plano.

## Protocolo de análise corporal (fotos)

**O que dá para ver em foto bem feita (frontal, lateral, dorsal, luz uniforme):**
- Distribuição de gordura por região (abdômen, flancos, glúteos, membros).
- Estimativa visual de %BF com **margem explícita de ±3–4%**.
- Desvios posturais grossos: anteversão/retroversão pélvica, hiperlordose/cifose, ombro protraído, cabeça anteriorizada, valgo/varo de joelho, pés pronados/supinados.
- Assimetrias visíveis (um lado mais desenvolvido, escápula alada unilateral).
- Proporções: largura de ombro vs quadril, V-taper, desenvolvimento proporcional de grupos musculares.

**O que NÃO dá para ver e precisa ser dito de cara:**
- Gordura visceral (precisa bioimpedância/DEXA).
- Força real, mobilidade real (precisa teste).
- Lesões internas, hérnias, impingimento.
- Nada que precise de palpação ou amplitude ativa.

**Protocolo padrão de output da análise:**
- Uma linha por desvio postural visível, com o grupo muscular que compensa.
- Uma estimativa de %BF com faixa (ex: "~18–22%").
- Uma lista curta de pontos fortes visíveis e pontos a desenvolver.
- Se a foto for ruim (ângulo, roupa larga, luz), dizer o que precisa ser refotografado antes de gastar palpite.

Detalhe completo em `references/analise-corporal.md`.

## Formato de saída (plano completo)

Sempre nessa ordem, sem omitir seções:

### 1. Análise
- Resumo do questionário / mudanças desde o último plano.
- Análise corporal (se há fotos).
- Problemas mecânicos e o que o treino vai endereçar.

### 2. Treino
Para cada dia da semana que treina:
- Nome do dia (ex: "Segunda — Push").
- Lista de exercícios na ordem: `Exercício — séries x reps @ RPE/carga — descanso`.
- Observações de execução quando há problema mecânico (ex: "Agachamento box por hora, joelho valgo").
- Aquecimento específico se há lesão.
- Tempo total estimado.

Referências: `references/treinos/*.md`, `references/biomecanica-comum.md`.

### 3. Nutrição (gramagem rígida)
- TDEE calculado, calorias alvo, split de macros (P/C/G em g e kcal).
- Cardápio de 7 dias OU 1 dia base + 6 variações, cada refeição com:
  - Horário aproximado.
  - Ingredientes em gramas CRUS (ex: "Arroz branco 80g cru, frango peito 180g cru").
  - Modo de preparo em 1–2 linhas.
  - Macros da refeição (P/C/G/kcal).
- Hidratação alvo em litros/dia.
- Suplementação se fizer sentido (creatina, whey, ômega-3, vitamina D se dosagem baixa) — nada sem evidência.

Referências: `references/nutricao/*.md`, `references/receitas/*.md`.

### 4. Lista de mercado (semanal)
Gerada por `scripts/lista_mercado.py` a partir das receitas da semana:
- Agrupada por setor do mercado (hortifruti, açougue, laticínios, grãos/secos, limpeza/outros).
- Quantidade total da semana por item (ex: "Peito de frango — 1.6 kg").
- Custo estimado se o usuário tiver preenchido `precos.json`.
- Substituições por preço/disponibilidade (`references/mercado/substituicoes.md`).

### 5. Métricas a acompanhar
- O que medir na próxima avaliação (peso, circunferências, fotos, cargas-chave).
- Quando revisitar o plano (default: 4 semanas).

## Princípios inegociáveis

- **Gramagem crua, sempre.** "80g de arroz" = cru, não cozido. Sempre explicitar.
- **Honestidade sobre o que foto não mostra.** Nunca cravar %BF sem margem.
- **Progressão registrada.** Cargas e repetições do plano anterior são lidas do DB antes de montar o próximo.
- **Nada de dieta da moda.** Macros vêm de Mifflin-St Jeor + ajuste conhecido, não de "método X".
- **Se tem lesão séria ou dor persistente, falar para procurar fisio/médico antes do treino.** A skill continua montando o plano para o resto, mas marca a região em espera.
- **Sem romantizar déficit extremo.** Déficit >25% só com justificativa (prazo específico) e por janela curta (≤4 semanas) com re-feeds.

## Arquivos de referência (criados em sessões futuras)

Essa SKILL.md é a orquestração. Os conteúdos abaixo são preenchidos conforme a skill for usada — na primeira sessão real, criar o que o pedido exige; não tentar preencher tudo antecipadamente.

- `references/avaliacao-inicial.md` — questionário completo e como pontuar.
- `references/analise-corporal.md` — protocolo detalhado, exemplos de desvios, limites.
- `references/biomecanica-comum.md` — mapa desvio → músculo encurtado/fraco → correção.
- `references/treinos/{hipertrofia,emagrecimento,forca,mobilidade-corretivo}.md` — templates por objetivo.
- `references/treinos/progressao.md` — regras de progressão de carga (double progression, RPE, deload).
- `references/nutricao/calculo-macros.md` — Mifflin-St Jeor, fatores de atividade, ajustes.
- `references/nutricao/estrategias.md` — cutting/bulking/recomp, quando trocar.
- `references/nutricao/suplementacao.md` — só com evidência.
- `references/receitas/{cafe,almoco,jantar,lanches}.md` — receitas com macros calculados.
- `references/receitas/por-objetivo/{alta-proteina,low-carb,bulk}.md`.
- `references/mercado/template-semanal.md` — formato da lista.
- `references/mercado/substituicoes.md` — trocas por preço/disponibilidade.

## Scripts (criados em sessões futuras)

- `scripts/init.py` — cria `~/.nutri-personal/`, schema SQLite, perfil.json vazio.
- `scripts/macros.py` — TMB (Mifflin-St Jeor) + TDEE + split de macros por objetivo.
- `scripts/db.py` — read/write no SQLite (medidas, cargas, fotos indexadas).
- `scripts/hevy_sync.py` — puxa treinos executados do Hevy Pro (`GET /v1/workouts`) para o SQLite local.
- `scripts/hevy_push.py` — envia rotinas geradas direto para o app Hevy (`POST /v1/routines`) resolvendo `exercise_template_id`.
- `scripts/lista_mercado.py` — consolida receitas de um plano em lista agrupada.

Schema SQLite proposto:

```sql
CREATE TABLE medicoes (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  peso_kg REAL,
  bf_estimado_min REAL,
  bf_estimado_max REAL,
  circ_cintura_cm REAL,
  circ_quadril_cm REAL,
  circ_braco_cm REAL,
  circ_coxa_cm REAL,
  circ_peitoral_cm REAL,
  notas TEXT
);

CREATE TABLE treinos_executados (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  exercicio TEXT NOT NULL,
  series INTEGER,
  reps INTEGER,
  carga_kg REAL,
  rpe REAL,
  notas TEXT
);

CREATE TABLE fotos (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  angulo TEXT CHECK(angulo IN ('frontal','lateral','dorsal','outro')),
  caminho TEXT NOT NULL,
  observacoes TEXT
);

CREATE TABLE planos (
  id INTEGER PRIMARY KEY,
  data_inicio DATE NOT NULL,
  data_fim DATE,
  objetivo TEXT,
  caminho_md TEXT NOT NULL,
  tdee_kcal INTEGER,
  calorias_alvo INTEGER,
  proteina_g INTEGER,
  carbo_g INTEGER,
  gordura_g INTEGER
);
```

## Roadmap (quando a skill crescer)

- **MCP opcional** se quisermos: (a) pegar preços reais de supermercado (scraping ou API), (b) integrar com Apple Health / Google Fit, (c) exportar planos para Notion/Obsidian. Por enquanto, nada disso é necessário.
- **Reconhecimento de refeição** via foto do prato (modelo de visão) — depois, se valer o esforço.
- **Comparação temporal de fotos** com grid lado-a-lado — gerar HTML estático que a skill abre no browser.
