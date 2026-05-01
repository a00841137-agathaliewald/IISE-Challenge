"""
Monte Carlo — Simulador de escenarios de viaje
Calibrado con base.xlsx (75 viajes reales, ruta Puebla–Cuautitlán EDOMEX)

Lógica Monte Carlo real:
    En cada iteración se samplea UN valor de CADA variable simultáneamente,
    se calcula el outcome (litros) para ESE escenario específico,
    y se acumula la distribución de 10,000 outcomes por ruta.

Variables simuladas:
    1. Rendimiento  km/L    Normal(2.457, 0.186)
    2. Distancia    km      Normal(163/172/181, σ) según ruta
    3. Peso/carga   ton     Normal(34.82, 0.39)
    4. Temperatura  °F      Normal(64.96, 7.65)
    5. Viento       mph     Exponencial(5.04)
    6. Humedad      %       Normal(37.12, 13.84)

Crimen: parámetro λ fijo por ruta (promediado SESNSP, agregado en IA).
Output: 1,500 filas (500/ruta) listas para entrenar la NN.
"""

import numpy as np
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIG
# ─────────────────────────────────────────────────────────────────────────────
SEED   = 42
N_ITER = 10_000   # iteraciones Monte Carlo por ruta
N_OUT  = 500      # filas finales por ruta (sample representativo)
np.random.seed(SEED)

# ─────────────────────────────────────────────────────────────────────────────
# 1. PARÁMETROS CALIBRADOS DESDE base.xlsx
# ─────────────────────────────────────────────────────────────────────────────
REND_MEAN,  REND_STD  = 2.457,  0.186   # km/L
PESO_MEAN,  PESO_STD  = 34.82,  0.392   # ton
TEMP_MEAN,  TEMP_STD  = 64.96,  7.650   # °F
HUM_MEAN,   HUM_STD   = 37.12,  13.84   # %
VIENTO_ESC             = 5.04            # escala Exponencial

# ─────────────────────────────────────────────────────────────────────────────
# 2. RUTAS — 3 caminos reales Puebla → Cuautitlán Izcalli EDOMEX
# ─────────────────────────────────────────────────────────────────────────────
RUTAS = {
    'A_rapida': {
        'nombre':        'Ruta A — México-Puebla + Arco Norte',
        'km_mean':       163, 'km_std': 4,
        'dur_offset':    0.0,
    },
    'B_alterna1': {
        'nombre':        'Ruta B — Circuito Exterior Mexiquense',
        'km_mean':       172, 'km_std': 5,
        'dur_offset':    1.2,
    },
    'C_alterna2': {
        'nombre':        'Ruta C — Vía Texcoco / Peñón-Texcoco',
        'km_mean':       181, 'km_std': 6,
        'dur_offset':    2.5,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────
def monte_carlo_ruta(ruta_key, n_iter=N_ITER):
    """
    Ejecuta n_iter iteraciones Monte Carlo para una ruta.

    Cada iteración:
      1. Samplea 1 valor de CADA variable simultáneamente
      2. Calcula litros para ESE escenario
      3. Registra el escenario completo

    Retorna DataFrame con n_iter filas.
    """
    r = RUTAS[ruta_key]
    escenarios = []

    for _ in range(n_iter):

        # ── 1. SAMPLEO SIMULTÁNEO ──────────────────────────────────────────

        # Rendimiento — Normal truncada (mín físico 1.5 km/L)
        rend = np.random.normal(REND_MEAN, REND_STD)
        while rend < 1.5:
            rend = np.random.normal(REND_MEAN, REND_STD)

        # Distancia — varía por condición de la ruta
        km = np.clip(
            np.random.normal(r['km_mean'], r['km_std']),
            r['km_mean'] - 25, r['km_mean'] + 25
        )

        # Peso — Normal truncada
        peso = np.random.normal(PESO_MEAN, PESO_STD)
        while peso < 30 or peso > 38:
            peso = np.random.normal(PESO_MEAN, PESO_STD)

        # Temperatura — Normal
        temp = np.clip(np.random.normal(TEMP_MEAN, TEMP_STD), 30, 100)

        # Viento — Exponencial (mayoría días sin viento, pocos con viento fuerte)
        viento = np.clip(np.random.exponential(scale=VIENTO_ESC), 0, 55)

        # Humedad — Normal truncada
        humedad = np.clip(np.random.normal(HUM_MEAN, HUM_STD), 0, 100)

        # ── 2. CALCULAR OUTCOME PARA ESTE ESCENARIO ───────────────────────

        # Cada variable afecta el rendimiento del escenario específico
        factor_peso   = 1 + (peso   - PESO_MEAN) * 0.003   # +0.3% por ton extra
        factor_viento = 1 - min(viento / 250, 0.08)         # hasta -8% con viento
        factor_temp   = 1 - max((50 - temp) / 1000, 0)      # -3% si temp < 50°F
        factor_lluvia = 0.98 if humedad > 70 else 1.0        # -2% si humedad alta

        # Rendimiento real de ESTE escenario (interacción de todos los factores)
        rend_escenario = rend * factor_viento * factor_temp * factor_lluvia

        # Duración en este escenario
        vel_promedio = rend_escenario * 35
        duracion = (km / max(vel_promedio, 1)) + r['dur_offset']
        duracion = np.clip(duracion, 4, 40)

        # Litros en este escenario — física directa
        litros = (km / rend_escenario) * factor_peso
        litros = np.clip(litros, 30, 300)

        # ── 3. REGISTRAR ESCENARIO ─────────────────────────────────────────
        escenarios.append({
            'ruta':          ruta_key,
            'ruta_nombre':   r['nombre'],
            'km':            round(km, 1),
            'duracion_h':    round(duracion, 2),
            'peso_ton':      round(peso, 3),
            'temp_f':        round(temp, 1),
            'wind_mph':      round(viento, 1),
            'humedad_pct':   round(humedad, 1),
            'crimen_lambda': r['crimen_lambda'],
            'litros':        round(litros, 2),   # TARGET para la NN
        })

    return pd.DataFrame(escenarios)


# ─────────────────────────────────────────────────────────────────────────────
# 4. DATASET FINAL — 1,500 filas
# ─────────────────────────────────────────────────────────────────────────────
def generar_dataset():
    frames = []
    for key in RUTAS:
        print(f"  Simulando {N_ITER:,} escenarios: {key}...", end=' ', flush=True)
        df_ruta = monte_carlo_ruta(key)
        df_out  = df_ruta.sample(n=N_OUT, random_state=SEED)
        frames.append(df_out)
        p50 = df_ruta['litros'].median()
        print(f"OK — P50 litros = {p50:.1f}")
    df = pd.concat(frames, ignore_index=True)
    return df.sample(frac=1, random_state=SEED).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':

    print("=" * 62)
    print("Monte Carlo — Puebla → Cuautitlán Izcalli EDOMEX")
    print(f"{N_ITER:,} iteraciones por ruta  |  {N_OUT} filas de output por ruta")
    print("=" * 62)

    df = generar_dataset()

    print(f"\nDataset: {len(df)} filas × {len(df.columns)} columnas")

    print("\nP10 / P50 / P95 de litros por ruta:")
    print("-" * 50)
    for key in RUTAS:
        s = df[df['ruta'] == key]['litros']
        print(f"  {key:15s}  "
              f"P10={s.quantile(.10):.1f}L  "
              f"P50={s.quantile(.50):.1f}L  "
              f"P95={s.quantile(.95):.1f}L")

    print("\nMedia de variables por ruta:")
    print(df.groupby('ruta')[['km','duracion_h','peso_ton',
                               'wind_mph','litros']].mean().round(2))

    features = ['km','duracion_h','peso_ton','temp_f',
                'wind_mph','humedad_pct','crimen_lambda']
    cols_nn = ['ruta'] + features + ['litros']
    df[cols_nn].to_csv('dataset_mc_1500.csv', index=False)

    print(f"\nGuardado: dataset_mc_1500.csv")
    print(f"Features (X): {features}")
    print(f"Target   (y): litros")