# Absolute Seafloor Pressure

Monorepo for the **PREST** instrument family (OOI Regional Cabled Array tidal seafloor pressure sensors) under the COSZO project.

## Stations

`DO` channels carry absolute pressure; paired `K1` channels carry the sensor's internal pressure-temperature reading. `_10` is the SEED location code.

| Reference | Site | OO Net.Sta | Channels |
|---|---|---|---|
| `RS01SLBS-MJ01A-06-PRESTA101` | Slope Base, Hydrate Ridge | `OO.HYSB1` | `UDO_10`, `UK1_10`, `LDO_10`, `LK1_10` |
| `RS01SUM1-LJ01B-09-PRESTB102` | Southern Hydrate Summit 1 | `OO.HYS14` | `UDO_10`, `UK1_10`, `LDO_10`, `LK1_10` |
| `RS03AXBS-MJ03A-06-PRESTA301` | Axial Base | `OO.AXBA1` | `UDO_10`, `UK1_10` |

## Deployments

Deployment history per station, with the channels active during each deployment and their nominal sample rate. Sourced from each channel's `c_start` / `c_end` in `PREST-data-collection/param/*_DO_10.txt`.

| Station | Dep | Start | End | Channels | Sample rate |
|---|---|---|---|---|---|
| `OO.HYSB1` | 1 | 2014-09-13 | 2018-06-26 | `UDO_10`, `UK1_10` | 15 s (0.0667 Hz) |
| `OO.HYSB1` | 2 | 2018-06-26 | ongoing | `LDO_10`, `LK1_10` | 1 s (1 Hz) |
| `OO.HYS14` | 1 | 2014-09-07 | 2017-08-11 | `UDO_10`, `UK1_10` | 15 s (0.0667 Hz) |
| `OO.HYS14` | 2 | 2017-08-11 | ongoing | `LDO_10`, `LK1_10` | 1 s (1 Hz) |
| `OO.AXBA1` | 1 | 2014-08-08 | 2016-07-12 | `UDO_10`, `UK1_10` | 15 s (0.0667 Hz) |
| `OO.AXBA1` | 2 | 2016-07-13 | 2020-08-05 | `UDO_10`, `UK1_10` | 15 s (0.0667 Hz) |
| `OO.AXBA1` | 3 | 2020-08-06 | 2022-08-29 | `UDO_10`, `UK1_10` | 15 s (0.0667 Hz) |
| `OO.AXBA1` | 4 | 2022-08-30 | ongoing | `UDO_10`, `UK1_10` | 15 s (0.0667 Hz) |

## Layout

```
absolute-seafloor-pressure/
├── README.md
├── .gitignore
└── PREST-data-collection/        ← pipeline code
    ├── bin/                       ← *.py + *.sh (cron pipeline, investigator,
    │                                 backfill, gap_algorithms, sync_metrics, etc.)
    ├── param/                     ← run_prest.txt, station + per-channel params
    ├── run/                       ← endtime_*.txt state (also marks where the
    │                                 historical local backfill should start)
    ├── crons_prest_seedlink_and_mseed2dmc.txt
    ├── save_results_to_test       ← operator helper
    ├── test/, testk/              ← tests / smoke-test scripts
    └── output/                    ← runtime working tree
        ├── mseed/                  ← seedlink MiniSEEDs (contents NOT tracked)
        ├── mseed2dmc/              ← backfill MiniSEEDs (contents NOT tracked)
        ├── metrics/                ← per-day stats CSVs (TRACKED — pushed daily)
        └── diagnostics/            ← per-event log .txt files (TRACKED — pushed daily)
```

## Workflows

### Live data — VM seedlink path

The COSZO VM clones this repo and runs `crons_prest_seedlink_and_mseed2dmc.txt`:

| Time (UTC) | Job |
|---|---|
| 18:01 / 18:06 / 18:11 | Seedlink fetch for SLBS / SUM1 / AXBS |
| 18:16 | Metadata refresh |
| 18:21 | Latency check |
| 18:35 | `bin/sync_metrics.sh` — git push of `output/metrics/` and `output/diagnostics/` |

Miniseed2dmc cron entries are commented out — historical backfill is local-only, see below.

### Historical — local backfill

`bin/backfill_mseed_from_nc.py` walks NetCDFs the investigator has saved (via `--save-nc`) and produces MiniSEEDs in `PREST-data-collection/output/mseed2dmc/<YEAR>/`, byte-compatible with what the cron pipeline produces. Default algorithm: `anomaly` (OLS Δt_true + true_missing).

```bash
python bin/backfill_mseed_from_nc.py \
    --start 2014-09-14 --end <wherever investigator collect has reached>
```

### Daily metrics sync

`bin/sync_metrics.sh` runs once per day on the VM:

```
git pull --rebase --autostash
git add PREST-data-collection/output/metrics/ PREST-data-collection/output/diagnostics/
git commit -m "metrics: sync <date>"
git push origin main
```

`output/metrics/<station>_<run>_pipeline_stats.csv` and `output/diagnostics/<event>_<station>_<run>.txt` are tracked directly — no copy step, no top-level mirror.

## Algorithm

`gap_algo` in `param/run_prest.txt` selects between `legacy` (median Δt + adaptive multiplier × sp threshold) and `anomaly` (OLS Δt_true + integer-step + `true_missing > 0` splitting). **Default: `anomaly`** as of 2026-04-29.

Both algorithms live in `bin/gap_algorithms.py` behind a single `detect_gaps()` dispatcher used by the cron pipeline, the local backfill, the testk smoke-tests, and `bin/plot_from_netcdf.py`.

Built-in safety fallbacks (both apply only when `gap_algo = anomaly`):

- **Short-window guard:** `n < 100` falls back to legacy automatically.
- **Deployment-boundary guard:** if a deployment's `c_end` falls inside the requested 24 h window, falls back to legacy for that day. Affects ~2 historical days (SLBS 2018-06-26, SUM1 2017-08-11).

The actual algorithm used per row is recorded in `pipeline_stats.csv` columns `algorithm` (what ran) and `algorithm_requested` (what `gap_algo` asked for).

## Other instrument repos

This monorepo covers PREST. Sibling instrument repos in the `coszo-hub` organization will follow the same internal layout:

- `coszo-hub/absolute-seafloor-pressure/PREST-data-collection/` (this repo)
- future: `coszo-hub/<current-meter>/...`
- future: `coszo-hub/<scpr>/...`
- future: `coszo-hub/<botpt>/...`
