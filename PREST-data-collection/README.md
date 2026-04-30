# COSZO Data Collection Package

## Overview

The COSZO Data Collection Package automates retrieval, validation, conversion, and staging of Ocean Observatories Initiative (OOI) RCA Tier‑3 geophysical data and metadata. The pipeline converts:

- **Waveform data** → **MiniSEED** (ObsPy‑compliant, archive‑ready)
- **Metadata** → **StationXML** (and dataless SEED via ObsPy)

Tier‑3 data are data from cabled offshore instruments sampled at **8 Hz or less** and **not diverted by the U.S. Navy**.

This package is derived from the original *ooi‑data‑collection* system provided to COSZO by EarthScope Data Services (formerly IRIS DMC). That legacy system targeted direct BUD/BATS ingestion, which is no longer used. The current pipeline stages data locally for downstream transfer via **SeedLink** (near‑real‑time) or **miniseed2dmc** (historical backfill).

---

## Runtime Environment

### Requirements

- miniconda
- **Python ≥ 3.10**
- numpy
- netCDF4
- ObsPy
- requests

Create the runtime environment using the provided conda specification:

```bash
conda env create --file bin/environment.yml
```

### Terminology

- **Sample period (Δt)**: Time spacing between consecutive samples
- **Sample rate**: Reciprocal of the sample period (1/Δt)

The pipeline derives timing from data timestamps; configured sample rates are advisory only.

---

## OOI API Credentials (Required)

Each execution environment must supply OOI credentials via environment variables.

### Credential File

Create the following file in the repository root:

```bash
.ooi_env
```

Contents:

```bash
export OOI_USERNAME=<your_ooi_api_username>
export OOI_TOKEN=<your_ooi_api_token>
```

- Do **not** quote values
- Do **not** commit this file

### Permissions

```bash
chmod 600 .ooi_env
```

This is required for cron execution and security.

### Failure Mode

If credentials are missing or not loaded correctly, scripts exit immediately with:

```
Missing OOI credentials. Set OOI_USERNAME and OOI_TOKEN in the environment.
```

---

## Execution Model

All operations are launched via wrapper scripts in `bin/`. These wrappers:

- Activate the conda environment
- Load credentials from `.ooi_env`
- Resolve repository paths (cron‑safe)
- Prevent concurrent duplicate executions

**Python scripts must never be called directly from cron.**

---

## Directory Structure

### `bin/`

Pipeline executables and utilities.

- **run_ooi_requests.sh** – Secure wrapper (required entry point)
- **run_data_collection.sh** – Pipeline dispatcher (metadata vs waveform)
- **OOI_metadata.py** – Metadata retrieval and validation
- **create_metadata.py** – StationXML construction
- **OOI_data_request_and_convert_mseed.py** – Core waveform pipeline
- **detect.py** – Pipeline health monitoring
- **mail.py** – Email notification utility
- **read_param.py** – Parameter file loader
- **diagnose_timing.py** – Offline timing-diagnostics tool (per‑day and summary figures, calendar heatmap, CSV metrics). Shares OOI‑fetch infrastructure with the pipeline.
- **temporal_anomaly_investigator.py** – Timestamp‑variability assessment. Fits an OLS sample clock per day, separates real gaps from jitter spikes via a wall‑clock sample‑count cross‑check, and writes per‑day 4‑panel figures plus a cross‑day CSV.

---

### `run/`

Persistent pipeline state:

- `endtime_<reference>_<run>.txt`

---

### Output and Log Directories

| Transfer method | MiniSEED output | Logs and gap files |
|-----------------|------------------|-------------------|
| seedlink        | output/mseed/    | log/              |
| miniseed2dmc    | output/mseed2dmc/<YEAR>/ | log_mseed2dmc/ |

Gap files (`gap_<reference>_<run>.txt`, when enabled) are written to the **same log directory** as the corresponding run.

Additional outputs:

- `output/xml/` – StationXML
- `output/netcdf/` – Optional raw NetCDF copies (audit trail)
- `output/diagnostics/` – `diagnose_timing.py` per‑day and summary figures, CSV metrics
- `output/temporal_anomaly/` – `temporal_anomaly_investigator.py` output:
    - `metrics/<STATION>_variability.csv` — one row per (station × day), with both raw and wall‑clock‑corrected gap counts, OLS‑fit sample interval, jitter stats in ms and as fraction of Δt_true
    - `figures/per_day/<station>_<date>/` — 4‑panel figure + `variability_stats.txt`
    - `figures/summary/` — cross‑day plots (`--mode plot`)
    - `netcdf/` — raw `.nc` files when run with `--save-nc`

---

## Gap Detection (Summary)

Gap detection is fully **data‑driven** and adaptive:

- Sample period derived from robust median inter‑sample spacing
- Expected sample counts compared to actual counts per window
- Thresholds adapt to sampling regime and window completeness
- Failure modes advance state to prevent pipeline stalls

Gap records are written to the active **log directory**, not the `run/` directory.

The pipeline's gap detection uses an **absolute Δt threshold** (multiplier × median sample period), scaled by sampling regime and window completeness — tuned to split MiniSEED files cleanly around real dropouts while tolerating jitter.

The offline `temporal_anomaly_investigator.py` applies a **different, stricter criterion** designed for data‑quality characterisation (not file splitting):

- Integer‑step test: `Δi = round(Δt' / median(Δt'))`; any `Δi > 1` is a raw gap candidate.
- Wall‑clock correction: if the observed sample count already accounts for the window duration at the nominal sample period, raw Δi>1 events are reclassified as **jitter**, not gaps.
- Both the raw and corrected gap counts are stored in the CSV (`n_gaps_raw` vs `n_gaps`).

This is strictly more sensitive than the pipeline on long‑period data (a single missing 15 s sample is below the pipeline's 45–60 s threshold but the investigator flags it), with jitter‑vs‑gap discrimination on top.

---

## Offline Diagnostic Tools

Two tools share the pipeline's OOI fetch infrastructure but run **offline** from the real‑time path — they do not advance pipeline state or produce MiniSEED.

### `diagnose_timing.py`

Per‑station timing diagnostics across arbitrary date ranges. Three modes:

- `single` — one (station, date): 3‑panel figure + stats
- `collect` — batch over a date range, appending to per‑station CSVs
- `plot` — cross‑day summary figures (calendar heatmap, sample‑rate deviation, gap counts, day‑boundary offsets)

Output: `output/diagnostics/`

### `temporal_anomaly_investigator.py`

Per‑day timestamp‑variability assessment implementing the 10‑step procedure in
`Obsidian Vault/COSZO/timestamp variability assessment plan.md`. Three modes:

- `single --station <ref> --date YYYY-MM-DD`
- `collect --start YYYY-MM-DD --end YYYY-MM-DD [--station …]`
- `plot` — cross‑day summary figures (Δt_true, jitter σ and max, gap count per day)

Flags:

- `--save-nc` — also download the raw `.nc` for each fetched day to `output/temporal_anomaly/netcdf/`. Default **off**.
- `--only-gaps` — only write the per‑day 4‑panel figure when the **post‑correction** `n_gaps > 0` (skips days whose raw Δi>1 events were reclassified as jitter). CSV row is written either way. Default **off**.
- `--force` — overwrite an existing CSV row in `single` mode.

Example:

```bash
python bin/temporal_anomaly_investigator.py --mode collect \
    --start 2019-01-01 --end 2019-03-31 --save-nc --only-gaps
```

---

## Assumptions and Guarantees

- OOI timestamps are authoritative
- Sample period is derived from data
- State always advances to avoid stalling
- No MiniSEED file spans a detected data gap
- Scripts must be executed via wrappers

