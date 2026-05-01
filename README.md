# ⛽ IISE-Challenge — Fuel Optimization for Transport Fleets

> **IISE 2026 · Orta Transport (Orta Group)**
> Applying Monte Carlo simulation to intelligent fuel planning in commercial logistics.

---

## Table of Contents

1. [Problematic Context](#1-problematic-context)
2. [Solution Path](#2-solution-path)
3. [Data Research](#3-data-research)
4. [Data Augmentation](#4-data-augmentation)
5. [AI Model](#5-ai-model)
6. [Results](#6-results)
7. [Team — Les Huntrix](#7-team--les-huntrix)

---

## 1. Problematic Context

Commercial transport fleets face a persistent operational challenge: determining the right amount of fuel to load for each trip. Overfueling increases vehicle weight, raises costs, and wastes resources. Underfueling risks route interruptions, driver safety incidents, and costly emergency stops.

For **Orta Transport**, this problem is compounded by the variability of real-world conditions — changing weather, road safety levels, and the individual driving behavior of each driver — making fixed or rule-of-thumb fuel estimates unreliable and inefficient.

---

## 2. Solution Path

We approached this as a stochastic optimization problem. Rather than predicting a single deterministic fuel quantity, we model the inherent uncertainty in trip conditions using **Monte Carlo methods**, sampling across the distribution of possible outcomes (weather variability, traffic, driving style) to produce a statistically robust fuel recommendation.

The pipeline covers:

- Probabilistic modeling of trip variables (destination distance, weather, safety conditions, driver profile)
- Monte Carlo simulation over thousands of sampled scenarios per trip
- Output: an optimal fuel load that minimizes cost while satisfying a safety margin constraint

---

## 3. Data Research

We identified and collected the key variables governing fuel consumption in a fleet context:

- **Route data** — distance, road type, elevation profile
- **Weather conditions** — temperature, wind speed, precipitation probability
- **Road safety conditions** — risk level per corridor (incident history, road quality)
- **Driver profiles** — historical fuel consumption patterns, acceleration/braking behavior, average speed

Data sources included Orta Transport's internal fleet records, public meteorological APIs, and road safety databases.

---

## 4. Data Augmentation

Real-world fleet data is often sparse, inconsistent, or incomplete — particularly for edge-case weather events and rarely driven routes. To address this, we applied data augmentation strategies:

- **Synthetic trip generation** using learned distributions from historical records
- **Weather scenario sampling** from regional climate models
- **Driver style interpolation** to fill gaps in short-tenure driver histories

This ensured that our Monte Carlo simulations could explore the full space of plausible trip conditions, not just those already observed.

---

## 5. AI Model

The core of our system is a **Monte Carlo simulation engine** coupled with a predictive fuel consumption model:

1. **Fuel consumption predictor** — a regression model trained on historical trip data, taking route, weather, safety level, and driver style as inputs, and outputting expected fuel consumption (L/100km or equivalent).

2. **Monte Carlo optimizer** — for a given trip, we sample $N$ scenarios from the joint distribution of uncertain variables, run the predictor on each, and derive the distribution of total fuel needed.

3. **Optimal fuel recommendation** — the recommended fuel load is set at a chosen percentile of the simulated distribution (e.g., 95th percentile), ensuring the driver reaches the destination safely across the vast majority of plausible scenarios while avoiding systematic overfueling.

```
Trip parameters → Monte Carlo sampling → Fuel consumption model (×N runs)
→ Distribution of total fuel needed → Optimal load recommendation
```

---

## 6. Results

The model was validated against held-out historical trips from Orta Transport's fleet. Key outcomes:

- **Fuel estimation accuracy** improved compared to fixed company benchmarks
- **Overfueling reduced** on average per trip, with measurable cost savings projected at scale
- **Safety constraint satisfied** — no simulated trip fell short of fuel under the chosen confidence level
- The model successfully differentiated recommendations by driver profile, rewarding efficient driving styles with leaner fuel loads

> Detailed metrics and figures are available in the project report / presentation.

---

## 7. Team — Les Huntrix

Developed for the **IISE 2026 Challenge** by:

| Name | Role |
|---|---|
| **Maximilien Tragarz Quintana** | |
| **Paris Joshua Reyes Pineda** | |
| **Karla Yvette Aleman Pastrana** | |
| **Adolfo Naverrete Najera** | |
| **Agatha Adaluz Liewald Suárez** | |

---

*IISE 2026 · Les Huntrix · Orta Transport / Orta Group*
