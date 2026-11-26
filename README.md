# iron-macro-protocol (`nutri-personal`)

Skill de **nutrição esportiva, prescrição de treino de força/hipertrofia e avaliação biomecânica** baseada em evidências científicas, com integração bidirecional para o **Hevy Pro** (pull de treinos executados + push de rotinas via API).

## Funcionalidades

- **Múltiplos Perfis:** gere e isole perfis distintos com `python3 scripts/init.py --perfil <nome>` (ou `--listar`).
- **Nutrição baseada em evidência:** cálculo de TMB (Mifflin-St Jeor), TDEE e divisão de macros (`scripts/macros.py`), respeitando gramagem **crua** e lista de mercado semanal (`scripts/lista_mercado.py`).
- **Prescrição de treino baseada em evidência:** volume fracionário (10–20 séries/músculo/semana), proximidade da falha (`1–3 RIR`), descanso entre séries, *double progression*, *deload* e ênfase em **posição alongada**.
- **Integração bidirecional com Hevy Pro:**
  - `scripts/hevy_sync.py`: importa treinos executados (`GET /v1/workouts`) para o SQLite local (`~/.nutri-personal/progress.sqlite`).
  - `scripts/hevy_push.py`: cria e envia rotinas montadas diretamente para o app Hevy (`POST /v1/routines`), com resolução automática de `exercise_template_id` e modo `--dry-run`.

## Uso Rápido (Hevy)

```bash
# 1. Puxar treinos executados do Hevy para o SQLite local
python3 scripts/hevy_sync.py --paginas 3

# 2. Buscar exercise_template_id no Hevy
python3 scripts/hevy_push.py --search "Incline Dumbbell"

# 3. Enviar uma rotina JSON direto para o app Hevy (teste antes com --dry-run)
python3 scripts/hevy_push.py --file rotina.json --dry-run
python3 scripts/hevy_push.py --file rotina.json
```

## Referências Científicas Principais

### Treino e Hipertrofia
- **Volume semanal:** Pelland JC et al. (2025). *The Resistance Training Dose-Response: Meta-Regressions Exploring the Effects of Weekly Volume and Frequency on Muscle Hypertrophy and Strength Gain.* *Sports Medicine*.
- **Proximidade da falha (RIR):** Robinson ZP et al. (2024). *Exploring the Dose–Response Relationship Between Estimated Resistance Training Proximity to Failure, Strength Gain, and Muscle Hypertrophy: A Series of Meta-Regressions.* *Sports Medicine*.
- **Descanso entre séries:** Schoenfeld BJ et al. (2016). *Longer Interset Rest Periods Enhance Muscle Strength and Hypertrophy in Resistance-Trained Men.* *J Strength Cond Res*. [DOI:10.1519/JSC.0000000000001272](https://doi.org/10.1519/JSC.0000000000001272)
- **Faixa de repetições:** Schoenfeld BJ et al. (2017). *Strength and Hypertrophy Adaptations Between Low- vs. High-Load Resistance Training.* *J Strength Cond Res*. [DOI:10.1519/JSC.0000000000002200](https://doi.org/10.1519/JSC.0000000000002200)
- **Amplitude e posição alongada:** Wolf M et al. (2023, *IJSC* [DOI:10.47206/ijsc.v3i1.182](https://doi.org/10.47206/ijsc.v3i1.182); 2025, *PeerJ* [DOI:10.7717/peerj.18904](https://doi.org/10.7717/peerj.18904)).

### Nutrição Esportiva
- **Proteína diária:** Morton RW et al. (2018). *Br J Sports Med*. [DOI:10.1136/bjsports-2017-097608](https://doi.org/10.1136/bjsports-2017-097608)
- **Proteína em déficit:** Helms AR et al. (2014). *Int J Sport Nutr Exerc Metab*. [DOI:10.1123/ijsnem.2013-0054](https://doi.org/10.1123/ijsnem.2013-0054)
- **Resposta anabólica sem teto rígido por refeição:** Trommelen J et al. (2023). *Cell Reports Medicine*, 4(12):101324. [DOI:10.1016/j.xcrm.2023.101324](https://doi.org/10.1016/j.xcrm.2023.101324)
- **Timing de nutrientes (ISSN):** Kerksick CM et al. (2018). *J Int Soc Sports Nutr*. [DOI:10.1186/s12970-018-0242-y](https://doi.org/10.1186/s12970-018-0242-y)
- **Terapia incretínica (GLP-1) + treino resistido:** Eisa AF et al. (2026). *Diabetes Obes Metab*. [DOI:10.1111/dom.70666](https://doi.org/10.1111/dom.70666)
