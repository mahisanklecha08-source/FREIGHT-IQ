# Antigravity Agent Execution Specification: FreightIQ Enterprise

---

## 1. Agent Operational Directives & Guardrails

You are an autonomous senior principal engineer inside the Antigravity IDE. Your mission is to implement, test, and package the complete **FreightIQ Enterprise** platform end-to-end.

### Critical Execution Rules
1. **Zero Truncation / No Placeholders**: Write complete, fully realized code in every file. Never write `# TODO: implement later`, `pass`, or mock stubs where domain logic belongs.
2. **Deterministic & Isolated Execution**: The system must run completely offline without external API keys or live network requests. Use pre-seeded data under `/data/`.
3. **Strict Client-Server Isolation**: The frontend (`frontend/`) and backend (`backend/`) must communicate strictly over HTTP REST using `requests` or `httpx`. Direct imports of backend models/functions into frontend files are strictly forbidden.
4. **Resilient Local Fallbacks**: If PostgreSQL is unavailable, the backend must seamlessly initialize and run against a local SQLite database (`freightiq.db`) when `USE_SQLITE=True`.
5. **Fast Inference Guarantee**: Machine learning models (SARIMA + XGBoost) must fit on the pre-generated seed dataset during startup/seeding in less than 5 seconds. Cache fitted model artifacts to disk or memory so `/api/v1/forecast` responds in under 150 ms.

---

## 2. Mathematical Formulations & Business Logic

### A. Total Landed Cost per Metric Ton ($/MT)
$$\text{Landed Cost (\$/MT)} = \frac{\text{Charter Hire} + \text{Bunker Cost} + \text{Port Dues (SOR)} + \text{Demurrage Risk} - \text{Despatch} + \text{Transshipment Surcharge}}{\text{Cargo Volume (MT)}} + \text{Inland Freight (\$/MT)}$$

Where:
* **Charter Hire**: $\text{Daily Rate (\$/day)} \times (\text{Voyage Days} + \text{Port Days})$
* **Bunker Cost**: $[(\text{Laden Days} \times \text{Laden Burn}) + (\text{Ballast Days} \times \text{Ballast Burn}) + (\text{Port Days} \times \text{Aux Burn})] \times \text{VLSFO Price (\$/MT)}$
* **Port Dues (SOR)**: Calculated per Indian Major Port Authority Schedule of Rates:
  $$\text{Port Dues} = (\text{Gross Tonnage} \times \text{Port Dues Rate}) + (\text{Gross Tonnage} \times \text{Berth Hire Rate/hr} \times \text{Berth Hours}) + \text{Pilotage} + \text{Tug Charges}$$
* **Demurrage Risk**: $\text{Daily Demurrage Rate} \times \max(0, \text{Congestion Waiting Days} + \text{Adverse Weather Days} - \text{Allowed Laytime})$

### B. IMO Carbon Intensity Indicator (CII) & $\text{CO}_2$ Emissions
$$\text{Total CO}_2 \text{ (MT)} = \text{Total Fuel Burn (MT)} \times 3.114$$
$$\text{Attained CII} = \frac{\text{Total CO}_2 \times 10^6}{\text{DWT} \times \text{Distance (Nautical Miles)}}$$
* **CII Rating Scale**: Compare Attained CII against IMO reference vectors to assign Grade **A**, **B**, **C**, **D**, or **E**.

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

### D. PM Gati Shakti Inland Evacuation Comparison
$$\text{Cost}_{\text{Rail}} = \text{Port Handling} + (\text{Distance}_{\text{Rail}} \times \text{Rail Tariff Rate}) + \text{Demurrage}_{\text{Rake}}$$
$$\text{Cost}_{\text{NW-1 Barge}} = \text{Barge Loading} + (\text{Distance}_{\text{River}} \times \text{Inland Waterway Tariff}) + \text{Plant Unloading}$$

---

## 3. Seed Dataset Schemas (`/data/`)

Write `scripts/generate_synthetic_data.py` to generate these 7 CSV files deterministically (seed=42):

1. **`freight_rates_history.csv`**:
   - Columns: `date,route_id,origin_port,destination_port,vessel_class,time_charter_rate_usd_day,voyage_rate_usd_ton,bunker_vlsfo_usd_ton,coal_index_usd_ton,congestion_index,monsoon_active_flag`
   - Span: 4 years of daily entries across standard trade lanes (e.g., Newcastle → Paradip, Taboneo → Vizag).
2. **`port_infrastructure.csv`**:
   - Columns: `port_id,port_name,country,max_draft_m,max_loa_m,max_beam_m,berth_count,cargo_handling_rate_tpd,channel_type,monsoon_risk_months,transshipment_hub_flag`
   - Exact Records: Paradip (14.5m), Vizag Outer (18.1m), Vizag Inner (14.5m), Gangavaram (18.5m), Gopalpur (12.5m), Dhamra (18.0m), Haldia (7.5m), Sagar/Sandheads (20.0m), Newcastle (15.2m), Hay Point (19.0m), Richards Bay (17.5m), Taboneo (12.0m), New Orleans (14.0m).
3. **`vessel_classes.csv`**:
   - Columns: `class_id,class_name,dwt_min,dwt_max,typical_draft_m,typical_loa_m,typical_beam_m,gross_tonnage,service_speed_knots,laden_fuel_burn_tpd,ballast_fuel_burn_tpd,port_fuel_burn_tpd,daily_opex_usd,daily_demurrage_usd`
   - Vessel Types: Handysize (35k DWT), Supramax (55k DWT), Ultramax (64k DWT), Panamax (75k DWT), Kamsarmax (82k DWT), Capesize (150k DWT).
4. **`port_tariffs_sor.csv`**:
   - Columns: `port_id,port_dues_per_gt_usd,pilotage_per_gt_usd,berth_hire_per_gt_hr_usd,tug_charge_fixed_usd,anchorage_per_gt_day_usd`
5. **`port_congestion_synthetic.csv`**:
   - Columns: `date,port_id,vessels_waiting,avg_wait_hours,yard_occupancy_pct,berth_utilization_pct`
6. **`bunker_prices_synthetic.csv`**:
   - Columns: `date,hub_name,vlsfo_usd_ton,ifo380_usd_ton,mgo_usd_ton`
   - Hubs: Singapore, Fujairah, Visakhapatnam.
7. **`landside_evacuation.csv`**:
   - Columns: `port_id,destination_plant,rail_distance_km,rail_freight_usd_ton,rail_rake_availability_idx,waterway_distance_km,barge_freight_usd_ton,barge_route_id`

---

## 4. Backend API Contract (`/api/v1/`)

All requests and responses must validate strictly through Pydantic v2 schemas:

### Endpoint Specifications
* `POST /api/v1/forecast`
  - **Body**: `ForecastRequest { vessel_class: str, origin_port: str, destination_port: str, horizon_days: int = 30 }`
  - **Response**: `ForecastResponse { historical_series: list[DataPoint], forecast_series: list[ForecastPoint], confidence_lower_80: list[float], confidence_upper_80: list[float], recommendation: str ("ENTER_NOW" | "WAIT" | "MONITOR"), confidence_score: float, top_drivers: list[FeatureDriver] }`
* `POST /api/v1/recommend-vessel`
  - **Body**: `VesselRecommendationRequest { cargo_volume_tons: float, origin_port: str, destination_port: str, target_laycan_start: str, target_laycan_end: str }`
  - **Response**: `VesselRecommendationResponse { feasible_options: list[FeasibleVesselCard], disqualified_options: list[DisqualifiedVesselCard], transshipment_advisory: TransshipmentAdvisory | None }`
* `POST /api/v1/multi-port-optimize`
  - **Body**: `MultiPortRequest { cargo_volume_tons: float, origin_port: str, discharge_port_1: str, discharge_port_2: str, split_ratio_p1: float = 0.6 }`
  - **Response**: `MultiPortResponse { split_discharge_total_cost: float, single_port_baseline_cost: float, net_arbitrage_savings: float, recommendation_notes: str }`
* `POST /api/v1/multimodal-evacuation`
  - **Body**: `MultimodalRequest { discharge_port: str, destination_plant: str, cargo_volume_tons: float }`
  - **Response**: `MultimodalResponse { rail_cost_total: float, rail_days: float, barge_cost_total: float, barge_days: float, cheapest_mode: str, carbon_savings_pct: float }`
* `POST /api/v1/simulate-scenario`
  - **Body**: `ScenarioSimulationRequest { base_forecast_id: str | None, bunker_price_delta_pct: float, congestion_delta_days: float, fx_rate_usd_inr: float, carbon_tax_usd_ton: float }`
  - **Response**: `ScenarioSimulationResponse { adjusted_landed_cost_per_ton_usd: float, adjusted_landed_cost_inr_crore: float, cost_delta_pct: float, sensitivity_matrix: dict }`
* `POST /api/v1/nlp-analyze-contract`
  - **Body**: `ContractAnalysisRequest { contract_text: str }`
  - **Response**: `ContractAnalysisResponse { risk_score_100: float, flagged_clauses: list[RiskClause], suggested_amendments: list[str] }`
* `GET /api/v1/risk-radar`
  - **Response**: `RiskRadarResponse { active_monsoon_ports: list[str], cyclone_warning_zones: list[str], port_congestion_rankings: list[PortCongestionSummary] }`
* `GET /api/v1/psu-benchmark`
  - **Response**: `PSUBenchmarkResponse { route: str, fair_fixture_rate_usd_ton: float, psu_reserve_ceiling_usd_ton: float, methodology_notes: str }`

---

## 5. Directory Structure & File Map

freightiq/
├── docker-compose.yml
├── run_local.py                         # Launches FastAPI on :8000 & Streamlit on :8501 concurrently
├── requirements.txt
├── README.md                            # High-impact documentation with ASCII architecture
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
│   ├── init.py
│   ├── main.py
│   ├── config.py
│   ├── database.py                      # SQLAlchemy engine with SQLite/Postgres switch
│   ├── models.py                        # DB tables matching the 7 CSV schemas
│   ├── schemas.py                       # Pydantic v2 schemas for all API payloads
│   ├── forecasting/
│   │   ├── init.py
│   │   ├── sarima_engine.py             # Statsmodels SARIMA wrapper with fallback
│   │   ├── ml_engine.py                 # XGBoost regressor with fast fit
│   │   ├── xai_explainer.py             # Feature attribution / SHAP surrogate
│   │   └── ensemble.py                  # Weighted ensemble & confidence band math
│   ├── decision_engine/
│   │   ├── init.py
│   │   ├── vessel_constraints.py        # Draft, LOA, beam filter & ranking logic
│   │   ├── transshipment.py             # Haldia/Sandheads lightening itinerary solver
│   │   ├── multi_port_solver.py         # Two-port split discharge optimizer
│   │   ├── port_tariffs.py              # SOR port dues calculator
│   │   ├── multimodal_evacuation.py     # PM Gati Shakti Rail vs. NW-1 barge calculator
│   │   ├── roi_calculator.py            # Spot vs. Laycan financial arbitrage
│   │   ├── esg_carbon_calc.py           # IMO CII & CO2 emission calculator
│   │   └── psu_benchmark.py             # PSU reserve price ceiling calculator
│   ├── nlp/
│   │   ├── init.py
│   │   └── contract_parser.py           # Rule-based/regex Charter Party risk scanner
│   └── routers/
│       ├── init.py
│       ├── forecast_router.py
│       ├── vessel_router.py
│       ├── multimodal_router.py
│       ├── simulation_router.py
│       └── risk_router.py
├── frontend/
│   ├── Home.py                          # Overview dashboard & Bhashini voice recorder
│   ├── components/
│   │   ├── init.py
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
├── init.py
├── test_forecasting.py
├── test_constraints.py
├── test_transshipment.py
├── test_roi_engine.py
└── test_multimodal.py