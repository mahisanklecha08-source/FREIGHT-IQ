# ⚓ FreightIQ Enterprise Platform
### AI-Powered Maritime Intelligence, Constraint Solver, Multimodal Logistics & Charter Tender Arbitrage

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/pytest-13%20passed-brightgreen.svg)](https://pytest.org)
[![License](https://img.shields.io/badge/license-Enterprise-blue.svg)]()

---

## 🏛️ System Architecture

```text
                               +-------------------------------------------------------+
                               |              FREIGHTIQ ENTERPRISE PLATFORM           |
                               +-------------------------------------------------------+
                                                           |
               +-------------------------------------------+-------------------------------------------+
               |                                                                                       |
               v                                                                                       v
+-----------------------------+                                                         +-----------------------------+
|    FRONTEND (STREAMLIT)     | <================ HTTP REST API (:8000) ==============> |      BACKEND (FASTAPI)      |
|         Port :8501          |                                                         |         Port :8000          |
+-----------------------------+                                                         +-----------------------------+
| • Executive Home & Bhashini |                                                         | • SARIMA & XGBoost Ensemble |
| • Rate Forecast & XAI       |                                                         | • Physical Constraint Check |
| • Vessel & Transshipment    |                                                         | • Haldia Lightening Solver  |
| • Scenario Simulator (ROI)  |                                                         | • PM Gati Shakti Engine     |
| • PM Gati Shakti Multimodal |                                                         | • Landed Cost & SOR Tariffs |
| • Geospatial AIS & Weather  |                                                         | • Charter Party NLP Scanner |
| • PSU Tender Benchmark Memo |                                                         | • CVC Reserve Ceiling Model |
+-----------------------------+                                                         +-----------------------------+
                                                                                                       |
                                                                                        +--------------v--------------+
                                                                                        |    SQLAlchemy + SQLite/DB   |
                                                                                        |       (freightiq.db)        |
                                                                                        +-----------------------------+
                                                                                        | • freight_rates_history     |
                                                                                        | • port_infrastructure       |
                                                                                        | • vessel_classes            |
                                                                                        | • port_tariffs_sor          |
                                                                                        | • port_congestion_synthetic |
                                                                                        | • bunker_prices_synthetic   |
                                                                                        | • landside_evacuation       |
                                                                                        +-----------------------------+
```

---

## 📐 Mathematical Formulations & Business Logic

### A. Total Landed Cost per Metric Ton ($/MT)
$$\text{Landed Cost (\$/MT)} = \frac{\text{Charter Hire} + \text{Bunker Cost} + \text{Port Dues (SOR)} + \text{Demurrage Risk} - \text{Despatch} + \text{Transshipment Surcharge}}{\text{Cargo Volume (MT)}} + \text{Inland Freight (\$/MT)}$$

Where:
* **Charter Hire**: $\text{Daily Rate (\$/day)} \times (\text{Voyage Days} + \text{Port Days})$
* **Bunker Cost**: $[(\text{Laden Days} \times \text{Laden Burn}) + (\text{Ballast Days} \times \text{Ballast Burn}) + (\text{Port Days} \times \text{Aux Burn})] \times \text{VLSFO Price (\$/MT)}$
* **Port Dues (SOR)**: Calculated per Indian Major Port Authority Schedule of Rates:
  $$\text{Port Dues} = (\text{Gross Tonnage} \times \text{Port Dues Rate}) + (\text{Gross Tonnage} \times \text{Berth Hire Rate/hr} \times \text{Berth Hours}) + \text{Pilotage} + \text{Tug Charges}$$
* **Demurrage Risk**: $\text{Daily Demurrage Rate} \times \max(0, \text{Congestion Waiting Days} + \text{Adverse Weather Days} - \text{Allowed Laytime})$

---

### B. IMO Carbon Intensity Indicator (CII) & $\text{CO}_2$ Emissions
$$\text{Total CO}_2 \text{ (MT)} = \text{Total Fuel Burn (MT)} \times 3.114$$
$$\text{Attained CII} = \frac{\text{Total CO}_2 \times 10^6}{\text{DWT} \times \text{Distance (Nautical Miles)}}$$
* **CII Rating Scale**: Compare Attained CII against IMO reference vectors to assign Grade **A**, **B**, **C**, **D**, or **E**.

---

### C. Physical Constraint & Transshipment Validation Rules
1. **Draft Check**: Disqualify any vessel where $\text{Operating Draft} > \text{Port Max Draft} - 0.5\text{m (Under Keel Clearance)}$.
2. **LOA / Beam Check**: Disqualify any vessel where $\text{LOA} > \text{Max LOA}$ or $\text{Beam} > \text{Max Beam}$.
3. **Haldia Riverine Rule**:
   - If `destination == "Haldia"` and `cargo_volume > 25,000 MT`:
     - Disqualify direct discharge for Panamax and Capesize.
     - Automatically construct a **Transshipment / Lightening Schedule**:
       - Mother vessel (Capesize/Panamax) discharges parcel at **Sandheads Anchorage** or **Dhamra Port**.
       - Daughter shallow-draft barges (Mini Bulk Carriers / 5,000 MT capacity) shuttle remaining cargo to Haldia Dock Complex.
       - Apply transshipment handling surcharge: $\$5.50/\text{MT}$.

---

### D. PM Gati Shakti Inland Evacuation Comparison
$$\text{Cost}_{\text{Rail}} = \text{Port Handling} + (\text{Distance}_{\text{Rail}} \times \text{Rail Tariff Rate}) + \text{Demurrage}_{\text{Rake}}$$
$$\text{Cost}_{\text{NW-1 Barge}} = \text{Barge Loading} + (\text{Distance}_{\text{River}} \times \text{Inland Waterway Tariff}) + \text{Plant Unloading}$$

---

## 🚀 Quickstart & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Seed Data (Deterministic, seed=42)
```bash
python scripts/generate_synthetic_data.py
```

### 3. Run Automated Tests
```bash
pytest tests/ -v
```

### 4. Launch Full Platform Concurrently
```bash
python run_local.py
```
* **Backend REST API**: [http://localhost:8000](http://localhost:8000) (Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs))
* **Frontend Command Center**: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

---

## 📡 REST API Reference (`/api/v1/`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/forecast` | SARIMA + XGBoost ensemble forecast with 80% confidence bands and XAI top drivers |
| `POST` | `/api/v1/recommend-vessel` | Physical constraint validation (UKC 0.5m), landed cost ranking, and Haldia lightening |
| `POST` | `/api/v1/multi-port-optimize` | Two-port split discharge co-loading arbitrage optimizer |
| `POST` | `/api/v1/multimodal-evacuation`| PM Gati Shakti Indian Railways vs. NW-1 barge cost & carbon evaluation |
| `POST` | `/api/v1/simulate-scenario` | Macro shock stress testing (Bunker %, Delay days, FX, Carbon tax) in INR Crores |
| `POST` | `/api/v1/nlp-analyze-contract` | Charter party agreement scanner with 0-100 risk score and PSU amendment suggestions |
| `GET`  | `/api/v1/risk-radar` | Geospatial port congestion queues, active monsoon zones, and cyclone warnings |
| `GET`  | `/api/v1/psu-benchmark` | CVC-compliant fair fixture market benchmark and PSU tender reserve ceiling |

---

## 📂 Directory Structure

```text
freightiq/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── run_local.py                         # Launches FastAPI (:8000) & Streamlit (:8501) concurrently
├── requirements.txt
├── README.md                            # Complete technical documentation
├── .env.example
├── data/                                # Deterministic CSV seeds
│   ├── freight_rates_history.csv
│   ├── port_infrastructure.csv
│   ├── vessel_classes.csv
│   ├── port_tariffs_sor.csv
│   ├── port_congestion_synthetic.csv
│   ├── bunker_prices_synthetic.csv
│   └── landside_evacuation.csv
├── scripts/
│   └── generate_synthetic_data.py
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py                      # SQLAlchemy engine with SQLite/Postgres switch
│   ├── models.py                        # DB tables matching the 7 CSV schemas
│   ├── schemas.py                       # Pydantic v2 schemas for all API payloads
│   ├── forecasting/
│   │   ├── __init__.py
│   │   ├── sarima_engine.py             # Statsmodels SARIMA wrapper with fallback
│   │   ├── ml_engine.py                 # XGBoost regressor with fast fit & cache
│   │   ├── xai_explainer.py             # Feature attribution / SHAP surrogate
│   │   └── ensemble.py                  # Weighted ensemble & confidence band math
│   ├── decision_engine/
│   │   ├── __init__.py
│   │   ├── vessel_constraints.py        # Draft, LOA, beam filter & ranking logic
│   │   ├── transshipment.py             # Haldia/Sandheads lightening itinerary solver
│   │   ├── multi_port_solver.py         # Two-port split discharge optimizer
│   │   ├── port_tariffs.py              # SOR port dues calculator
│   │   ├── multimodal_evacuation.py     # PM Gati Shakti Rail vs. NW-1 barge calculator
│   │   ├── roi_calculator.py            # Spot vs. Laycan financial arbitrage
│   │   ├── esg_carbon_calc.py           # IMO CII & CO2 emission calculator
│   │   └── psu_benchmark.py             # PSU reserve price ceiling calculator
│   ├── nlp/
│   │   ├── __init__.py
│   │   └── contract_parser.py           # Rule-based/regex Charter Party risk scanner
│   └── routers/
│       ├── __init__.py
│       ├── forecast_router.py
│       ├── vessel_router.py
│       ├── multimodal_router.py
│       ├── simulation_router.py
│       └── risk_router.py
├── frontend/
│   ├── Home.py                          # Overview dashboard & Bhashini voice recorder
│   ├── components/
│   │   ├── __init__.py
│   │   ├── voice_input.py               # Audio input helper
│   │   └── memo_generator.py            # Printable Executive Briefing Memo generator
│   └── pages/
│       ├── 1_📈Rate_Forecast&XAI.py
│       ├── 2🚢Vessel_Selector&Transshipment.py
│       ├── 3⚡Scenario_Simulator&ROI.py
│       ├── 4🚂Multi_Modal&Gati_Shakti.py
│       ├── 5🗺️_Geospatial_AIS_&Weather.py
│       └── 6📄Tender_Benchmark&_Memo.py
└── tests/
    ├── __init__.py
    ├── test_forecasting.py
    ├── test_constraints.py
    ├── test_transshipment.py
    ├── test_roi_engine.py
    └── test_multimodal.py
```
