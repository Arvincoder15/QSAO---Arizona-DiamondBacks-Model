# 📊 QSAO Case Competition 2026  
## Analytics-Based Team Building — Arizona Diamondbacks

### Repository Description
An analytics-driven roster construction project for the 2026 QSAO Case Competition, applying machine learning, Statcast metrics, and archetype-based player evaluation to optimize the Arizona Diamondbacks’ roster through trades, extensions, and player development decisions.

---

## Overview
This project was developed for the **QSAO Case Competition 2026**, where teams act as analytics consultants for an assigned MLB franchise.  
Our group analyzed the **Arizona Diamondbacks**, building a data-driven player evaluation framework to support roster-optimization decisions during a **contending competitive window**.

The project combines **machine-learned WAR projections**, **Statcast-based performance indicators**, **archetype classification**, **positional context**, and **role-based analysis** to inform:
- Trade proposals  
- Contract extension strategies  
- Internal player development decisions  

---

## Objectives
- Evaluate the Diamondbacks’ roster using traditional and advanced metrics  
- Identify roster strengths, weaknesses, and surplus value  
- Build interpretable machine learning models to project player value  
- Classify players by functional archetype and roster role  
- Propose realistic, analytics-backed trades aligned with team needs  

---

## Data Sources
- **Baseball-Reference** — Traditional statistics, WAR, positional data  
- **MLB Statcast (Baseball Savant)** — Expected metrics and contact quality  
- Seasons analyzed: **2021–2025**

---

## Methodology

### 1. Data Integration & Feature Engineering
- Merged Baseball-Reference and Statcast data at the player-season level  
- Engineered features capturing:
  - Offensive production and quality of contact  
  - Pitching run prevention and swing-and-miss ability  
  - Usage and workload context (starter vs bullpen, everyday vs bench)  

---

### 2. Quantitative Player Evaluation (Machine Learning)
- Built **regularized regression (Ridge)** models to project near-term player value  
- Target metrics:
  - **Batters:** `WAR_per_600 = WAR / PA × 600`  
  - **Pitchers:** `WAR_per_180 = WAR / IP × 180`  
- Recent seasons weighted more heavily to reflect aging curves and current performance  
- Emphasis on interpretability and stability over black-box prediction  

---

### 3. Archetype & Role Classification
Players were grouped into functional categories based on percentile thresholds across key metrics.

**Hitting Archetypes**
- Power Bat  
- High-OBP / Table Setter  
- Power–Contact Hybrid  
- Replacement-Level / Depth  

**Pitching Archetypes**
- Frontline Starter  
- Mid-Rotation Starter  
- Back-End / Contact Starter  
- Bullpen / Depth Arm  

Roles were further classified as:
- Starter vs Bullpen (pitchers)  
- Everyday Player, Platoon / Regular, Bench / Utility (batters)

---

### 4. Positional & Defensive Adjustment
- WAR values adjusted for positional scarcity to reflect roster construction realities  
- Prevented overvaluing offence at low-impact defensive positions  
- Enabled fair cross-position comparisons when identifying surplus and core players  

---

### 5. Roster Optimization Logic
- Defined **core players** based on age (≤32), projected WAR, and role stability  
- Identified **surplus players** with replaceable skill sets  
- Preserved core contributors while targeting marginal upgrades  

---

## Key Outputs
- Projected 2025 WAR for all Diamondbacks batters and pitchers  
- Player archetype and role classifications  
- Core vs surplus player segmentation  
- Realistic trade target shortlists aligned with team needs  

---

## Strategic Takeaways
- The Diamondbacks are positioned to **contend**, led by a young offensive core and rotation  
- Bullpen reliability represents the primary performance gap  
- Surplus offensive depth can be converted into high-leverage pitching upgrades  
- Long-term risk minimized by limiting commitments to high-variance roles  

---

## Technologies Used
- **Python**
- **pandas / NumPy** — Data processing  
- **scikit-learn** — Machine learning  
- **matplotlib** — Visualization  

---

## Project Context
This repository was created for the **QSAO Case Competition 2026** and reflects an analytics consulting approach rather than an official MLB affiliation.
