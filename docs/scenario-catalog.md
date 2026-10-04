# Scenario Catalog — Data Pipeline Arena

Auto-generated from `config/scenarios.yaml` (the single source of truth).
Regenerate with: `python -c "import generate_scenarios as gs; ..."` or manually.

**47 scenarios** — 23 optimization (training) / 24 heldout (testing).

> ⚠️ **Lab-side document.** The descriptive names below are registry labels;
> the model-facing workspace `data/eval/` uses opaque `sc-<6hex>` ids instead.
> The name↔id mapping lives in `data/truth/id_map.csv` (scorer-only) and must
> never be copied into an agent workspace or prompt.

| ID | Family | Split | Injected controls |
|---|---|---|---|
| `baseline` | none | optimization | — |
| `noop_neutral_controls` | none | heldout | all-neutral (exact no-op) |
| `drift_death_up_2018_2024` | drift | optimization | drift Death 2018-2024 +0.15/yr |
| `drift_ci_down_2016_2019` | drift | optimization | drift CI 2016-2019 -0.10/yr |
| `drift_tpd_up_2019_2021` | drift | optimization | drift TPD 2019-2021 +0.08/yr |
| `drift_death_up_2015_2017` | drift | heldout | drift Death 2015-2017 +0.15/yr |
| `drift_ip_down_2020_2024` | drift | heldout | drift IP 2020-2024 -0.10/yr |
| `drift_ci_up_2021_2023` | drift | heldout | drift CI 2021-2023 +0.05/yr |
| `shock_covid_2020_2022` | shock | optimization | shock 2020-2022 Death x1.5 |
| `shock_ci_2021_2022` | shock | optimization | shock 2021-2022 CI x1.4 |
| `shock_tpd_ip_2023` | shock | optimization | shock 2023-2023 TPD x1.3, IP x1.2 |
| `shock_death_2016` | shock | heldout | shock 2016-2016 Death x1.3 |
| `shock_ip_2018_2019` | shock | heldout | shock 2018-2019 IP x1.5 |
| `shock_ci_tpd_2015_2016` | shock | heldout | shock 2015-2016 CI x1.2, TPD x1.4 |
| `volatility_ip_sigma_03` | volatility | optimization | vol IP 2015-2024 sigma=0.3 |
| `volatility_death_sigma_02` | volatility | optimization | vol Death 2015-2024 sigma=0.2 |
| `volatility_ci_sigma_015` | volatility | heldout | vol CI 2015-2024 sigma=0.15 |
| `volatility_tpd_sigma_04` | volatility | heldout | vol TPD 2015-2024 sigma=0.4 |
| `trap_noise_drift_lookalike` | noise_trap | optimization | vol Death 2016-2020 sigma=0.35 |
| `trap_noise_spike_lookalike` | noise_trap | optimization | vol all 2020-2022 sigma=0.4 |
| `trap_noise_drift_lookalike_b` | noise_trap | heldout | vol CI 2017-2023 sigma=0.3 |
| `trap_noise_spike_lookalike_b` | noise_trap | heldout | vol IP 2018-2019 sigma=0.45 |
| `ip_recovery_mental_health_x2` | recovery | optimization | recovery 2015-2024 Mental Health x2.0 |
| `ip_recovery_cancer_x05` | recovery | optimization | recovery 2015-2024 Cancer x0.5 |
| `ip_recovery_injury_x15` | recovery | heldout | recovery 2015-2024 Injury/Accident x1.5 |
| `ip_recovery_cardio_x04` | recovery | heldout | recovery 2015-2024 Cardiovascular x0.4 |
| `ip_recovery_mh_msk` | recovery | heldout | recovery 2015-2024 Mental Health x2.5, Musculoskeletal x1.5 |
| `mixed_drift_death_shock_ci` | mixed | optimization | drift Death 2019-2024 +0.08/yr; shock 2021-2021 CI x1.4 |
| `mixed_drift_ip_vol_death` | mixed | optimization | drift IP 2018-2022 +0.07/yr; vol Death 2019-2022 sigma=0.25 |
| `mixed_shock_tpd_drift_death` | mixed | heldout | shock 2020-2021 TPD x1.3; drift Death 2016-2019 +0.06/yr |
| `mixed_triple_ci_ip_mh` | mixed | heldout | drift CI 2020-2024 +0.05/yr; vol IP 2015-2024 sigma=0.15; recovery 2015-2024 Mental Health x1.5 |
| `sys_shock_crisis_2020_2022` | systemic | optimization | shock 2020-2022 Death x1.5, CI x1.3, TPD x1.2, IP x1.1 |
| `sys_drift_aging_2018_2024` | systemic | optimization | drift Death 2018-2024 +0.06/yr; drift CI 2018-2024 +0.04/yr; drift TPD 2018-2024 +0.03/yr; drift IP 2018-2024 +0.02/yr |
| `sys_vol_macro_2019_2021` | systemic | optimization | vol all 2019-2021 sigma=0.25 |
| `sys_cascade_shock_drift_2020` | systemic | optimization | shock 2020-2020 Death x1.4, CI x1.2; drift Death 2021-2024 +0.05/yr; drift CI 2021-2024 +0.04/yr |
| `sys_shock_inverse_2021_2022` | systemic | optimization | shock 2021-2022 Death x1.4, CI x0.6 |
| `sys_drift_diverge_2018_2024` | systemic | optimization | drift Death 2018-2024 +0.06/yr; drift CI 2018-2024 -0.04/yr |
| `sys_shock_crisis_2015_2016` | systemic | heldout | shock 2015-2016 Death x1.4, CI x1.2, IP x1.1 |
| `sys_drift_aging_2016_2019` | systemic | heldout | drift Death 2016-2019 +0.05/yr; drift CI 2016-2019 +0.03/yr; drift IP 2016-2019 +0.02/yr |
| `sys_vol_macro_2020_2024` | systemic | heldout | vol all 2020-2024 sigma=0.15 |
| `sys_cascade_drift_shock_2018` | systemic | heldout | drift Death 2016-2019 +0.05/yr; drift IP 2016-2019 +0.03/yr; shock 2020-2020 Death x1.3, IP x1.2 |
| `sys_shock_inverse_2017_2019` | systemic | heldout | shock 2017-2019 Death x1.3, IP x0.7 |
| `sys_drift_diverge_2020_2023` | systemic | heldout | drift TPD 2020-2023 +0.05/yr; drift IP 2020-2023 -0.03/yr |
| `sys_trend_tpd_ip_2019_2023` | systemic | optimization | drift TPD 2019-2023 +0.05/yr; drift IP 2019-2023 +0.04/yr |
| `sys_shock_tpd_ip_2021_2022` | systemic | optimization | shock 2021-2022 TPD x1.4, IP x1.3 |
| `sys_trend_tpd_ip_2015_2018` | systemic | heldout | drift TPD 2015-2018 +0.04/yr; drift IP 2015-2018 +0.03/yr |
| `sys_shock_tpd_ip_2022` | systemic | heldout | shock 2022-2022 TPD x1.3, IP x1.2 |

See [dataset-usage.md](dataset-usage.md) for how to add scenarios and regenerate.
