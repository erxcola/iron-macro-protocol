# Evidência — Nutrição

Material de pesquisa para os números que a skill coloca no plano. Cada seção cita o estudo, resume o achado útil, e marca força da evidência (**forte** / **moderada** / **fraca**) com base em desenho (ECR, meta-análise, revisão narrativa) e consistência.

Convenção interna: quando a skill escreve "proteína 1.8–2.4 g/kg", a faixa vem **daqui**, não de palpite. Se o cálculo em `scripts/macros.py` divergir, este arquivo é fonte da verdade — ajustar script.

---

## 1. Proteína — ingestão para hipertrofia

### 1.1 Teto para ganho de massa magra (Morton et al., 2018 — base clássica)
- **Força:** forte. Meta-análise sistemática com 49 estudos, 1863 participantes, publicada em *British Journal of Sports Medicine*.
- **Achado:** breakpoint de ~**1.62 g/kg/dia** (IC 95%: 1.03–2.2) acima do qual o ganho adicional de massa magra via proteína é marginal em adultos treinando resistido.
- **Uso na skill:** piso prático é 1.6 g/kg/dia para hipertrofia em superávit; teto superior fica em 2.2 g/kg/dia salvo cenário específico (cutting agressivo — ver 1.3).
- **Ref:** Morton RW, Murphy KT, McKellar SR, et al. A systematic review, meta-analysis and meta-regression of the effect of protein supplementation on resistance training-induced gains in muscle mass and strength in healthy adults. *Br J Sports Med*. 2018;52(6):376-384. [DOI:10.1136/bjsports-2017-097608](https://doi.org/10.1136/bjsports-2017-097608)

### 1.2 Dose-resposta abaixo de 1.3 g/kg (Nunes et al., 2025 — reforço recente)
- **Força:** moderada–forte. Dose-resposta pooled.
- **Achado:** ganho de ~**0.39 kg de massa magra por cada 0.1 g/kg/dia adicional** até ~1.3 g/kg; acima disso a inclinação cai para ~0.12 kg por 0.1 g/kg/dia. Confirma que o retorno marginal despenca próximo do breakpoint de Morton.
- **Uso na skill:** se o usuário está abaixo de 1.3 g/kg (comum em dieta ocidental típica), priorizar correção dessa faixa antes de brigar por decimais acima de 2.
- **Ref:** veja [Maximizing Muscle Retention With Protein — Biolayne (Nunes 2025 cover)](https://biolayne.com/reps/issue-34/maximizing-muscle-retention-with-protein/) e checar o artigo primário Nunes et al. 2025 em *Advances in Nutrition* antes de citar como autoritativo.

### 1.3 Proteína em déficit agressivo
- **Força:** moderada. Revisão narrativa 2025 sintetizando ECRs anteriores (Longland 2016, Helms 2014, Mettler 2010).
- **Achado:** em déficit >25% com treino resistido, faixas de **2.2–3.1 g/kg/dia** (sobre FFM ou peso corporal, dependendo da fonte) protegem massa magra melhor do que 1.6–2.0 g/kg. Debate aberto: artigo em *Journal of Cachexia* 2025 argumenta que a disponibilidade energética total pode importar mais do que a proteína isoladamente — i.e., se o déficit é muito grande, nenhuma dose de proteína "salva" sem RT presente.
- **Uso na skill:** para cutting agressivo (>20% déficit) por janela curta, subir proteína para **2.4–2.8 g/kg/dia** de peso corporal e **nunca sem treino resistido em paralelo**. Acima de 3.0 g/kg sem benefício documentado — mais custo culinário do que ganho mecânico.
- **Refs:** [Preserving Fat-Free Mass During Weight Loss — drdidwal.com (síntese 2025)](https://drdidwal.com/preserving-fat-free-mass-during-weight-loss-the-synergistic-role-of-resistance-exercise-and-nutrition); checar primária Helms AR et al. *Int J Sport Nutr Exerc Metab*. 2014;24(2):127-138 [DOI:10.1123/ijsnem.2013-0054](https://doi.org/10.1123/ijsnem.2013-0054).

### 1.4 Distribuição de proteína em refeições e "teto por refeição"
- **Força:** moderada–forte. Dose-resposta Schoenfeld & Aragon (2018) + ensaio isotópico com 100g de proteína de Trommelen et al. (2023).
- **Achado:**
  - Repartir proteína em **3–4 refeições de ~0.4 g/kg** facilita aderência, saciedade e cobertura do limiar de leucina.
  - **Atualização importante (Trommelen et al., 2023):** doses grandes em uma única refeição (até 100g) **não são "desperdiçadas"** — produzem resposta anabólica sustentada por >12 horas *in vivo*. Portanto, refeições maiores (ex.: 2 refeições/dia ou jantar reforçado) funcionam bem se baterem o total diário.
- **Uso na skill:** preferir 3–4 refeições para conforto digestivo e saciedade, sem neurose caso o usuário prefira 2 refeições maiores ou precise concentrar proteína em uma janela menor.
- **Refs:**
  - Schoenfeld BJ, Aragon AA. *J Int Soc Sports Nutr*. 2018;15:10. [DOI:10.1186/s12970-018-0215-1](https://doi.org/10.1186/s12970-018-0215-1)
  - Trommelen J et al. The anabolic response to protein ingestion during recovery from exercise has no upper limit in magnitude and duration in vivo in humans. *Cell Reports Medicine*. 2023;4(12):101324. [DOI:10.1016/j.xcrm.2023.101324](https://doi.org/10.1016/j.xcrm.2023.101324)

---

## 2. Déficit calórico — taxa segura para preservar massa magra

### 2.1 Taxa recomendada (Refalo et al., meta-regressão de resistidos)
- **Força:** moderada. Meta-regressão de populações treinando resistido em déficit.
- **Achado:** déficits maiores produzem **maior perda de FFM**; recomendação derivada é **≤0.5% do peso corporal por semana** para minimizar essa perda em quem quer manter massa magra. Déficit >500 kcal/dia correlaciona com perda significativa de FFM mesmo com RT.
- **Uso na skill:** padrão de cutting = **15–20% abaixo do TDEE** (equivale a ~0.4–0.6% do peso/semana para a maioria). Acima de 25% só com justificativa (prazo, competição) e por janela ≤4 semanas com re-feeds semanais.
- **Ref:** síntese em [Rapid Weight Loss, Minimal Muscle Loss? — Biolayne](https://biolayne.com/reps/issue-44/rapid-weight-loss-minimal-muscle-loss-putting-exercise-to-the-test/). Buscar o paper primário Refalo MC et al. 2024/2025 em *Sports Medicine* antes de citar como autoritativo definitivo.

### 2.2 Exercício resistido em déficit profundo (Xie et al. 2025, network MA)
- **Força:** forte. Network meta-análise de 62 ECRs, publicada 2025.
- **Achado:** restrição calórica **sem** treino perde em média **-1.66 kg (IC 95%: -3.12 a -0.19) de massa magra**; adicionar RT reduz essa perda significativamente. Em VLED (≤800 kcal/dia), adicionar exercício preserva **~0.83 kg** de FFM vs. dieta sozinha.
- **Uso na skill:** nenhum protocolo de cutting sem treino resistido 3× semana no mínimo. Déficit sem RT é regressão nas métricas que importam.
- **Ref:** [Xie et al., Frontiers in Endocrinology 2025](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2025.1725500/full); VLED meta em [Frontiers in Nutrition 2025](https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2025.1579024/pdf).

### 2.3 Terapia incretínica (GLP-1) e massa magra — contexto moderno
- **Força:** moderada. Meta-análise 2026 (publicação antecipada), 2026 em *Diabetes, Obesity and Metabolism*.
- **Achado:** usuários de GLP-1 perdem ~**26%** do peso total como massa magra sem RT; com **RT + estilo de vida**, cai para **17.5% (IC 95%: 14.2–20.8)** — perfil composicional mais favorável.
- **Uso na skill:** se o usuário está em semaglutida/tirzepatida, **proteína acima de 2.0 g/kg + RT 3–4× semana + 30–45 min pé/dia** são não-negociáveis. Sem isso, o emagrecimento vem roubando pernas e braços.
- **Ref:** Eisa AF et al. Lean Mass Changes With Incretin Therapy Versus Lifestyle Intervention. *Diabetes Obes Metab*. 2026. [DOI:10.1111/dom.70666](https://doi.org/10.1111/dom.70666)

---

## 3. Gordura dietética — piso

### 3.1 Piso funcional (consistente em múltiplas revisões)
- **Força:** moderada. Base é integração de ECRs sobre testosterona, saciedade, lipossolúveis.
- **Achado:** **≥0.8 g/kg/dia** de gordura preserva perfil hormonal em homens treinando resistido; abaixo de 20% das calorias totais, risco de queda de T livre e saciedade degradada. Em mulheres, piso similar, com atenção extra em déficit (amenorreia hipotalâmica abaixo de disponibilidade energética ~30 kcal/kg FFM/dia).
- **Uso na skill:** piso de gordura = **max(0.8 g/kg, 20% kcal alvo)**. Carbo é o resto.

---

## 4. Carboidrato — timing e distribuição

### 4.1 Timing peri-treino
- **Força:** moderada. ISSN position stand on nutrient timing (Kerksick 2017, atualizado).
- **Achado:** em quem treina ≥2× dia ou tem ≤8h entre sessões, consumo pós-treino de carbo (0.8–1.2 g/kg) acelera reposição de glicogênio. Em treino único diário com dieta balanceada, o "janela anabólica" é marginal.
- **Uso na skill:** para treino único diário, não forçar refeição pós-treino específica. Para múltiplas sessões ou atleta em cutting, concentrar carbo pré/pós-treino.
- **Ref:** Kerksick CM et al. ISSN exercise & sports nutrition review update: research & recommendations. *J Int Soc Sports Nutr*. 2018;15:38. [DOI:10.1186/s12970-018-0242-y](https://doi.org/10.1186/s12970-018-0242-y)

---

## 5. Hidratação

### 5.1 Baseline
- **Força:** moderada. ACSM position stand + EFSA.
- **Achado:** **30–35 ml/kg/dia** como baseline; adicionar **500–750 ml por hora de treino** em clima quente ou sessão intensa. Urina amarelo-pálido é indicador prático suficiente.
- **Uso na skill:** meta diária = peso × 35 ml como padrão; peso × 40–45 ml em dias de treino ou calor.

---

## 6. Lacunas conhecidas / pendências

- Checar o paper primário Refalo 2024/2025 em *Sports Medicine* para confirmar o número ≤0.5% peso/semana.
- Checar Nunes 2025 em *Advances in Nutrition* para confirmar as inclinações 0.39 vs 0.12 kg LBM/0.1 g/kg/dia.
- Revisão específica de proteína em usuários de GLP-1 — literatura muito nova, ainda dominada por 2026.
- Ritmo circadiano e composição macros: evidência insuficiente para prescrição além de "não dormir com fome extrema".

---

## Como usar este arquivo

1. Antes de escrever um número no plano do usuário, achar a seção aqui que o cobre.
2. Se o número da skill divergir do número daqui, **este arquivo manda**.
3. Se o usuário perguntar "de onde vem esse 1.8 g/kg", responder com a referência direta (Morton 2018 §1.1) e o DOI. Nada de "a literatura diz".
4. Quando chegar um estudo mais recente que mova um número, **atualizar aqui primeiro, depois a skill**.
