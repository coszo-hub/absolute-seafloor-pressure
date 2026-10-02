# Session resume / handoff — PREST (updated 2026-10-02)

Read this first in a new session on this repo. Shared context (machines, conventions,
VEL3D sibling, SeedLink design) is in
`sea-water-velocity/VEL3D-data-collection/CLAUDE_RESUME.md` and Obsidian
`COSZO/10-02-26 Notes.md`.

## Conventions
- Git author Maleen Kidiwela; **no Claude/AI co-author trailers**. Short answers.
- **PREST data through 2026-05-01 was already processed and SENT with the old code —
  do NOT reprocess or "correct" it.** New code applies from 2026-05-02 on.

## Stations
| SEED | OOI refdes | Rate | Channels (loc 10) |
|---|---|---|---|
| HYSB1 | RS01SLBS-MJ01A-06-PRESTA101 | 15 s → 1 Hz from dep 2 (2018-06) | UDO/UK1 → LDO/LK1 |
| HYS14 | RS01SUM1-LJ01B-09-PRESTB102 | 15 s → 1 Hz from dep 2 (2017-08) | UDO/UK1 → LDO/LK1 |
| AXBA1 | RS03AXBS-MJ03A-06-PRESTA301 | 15 s (14.999925 s in metadata) | UDO/UK1 |
Stream `prest_real_time` (in the OOI gold copy). Deployments current as of 2026-10-01
(HYSB1 2, HYS14 2, AXBA1 4). Same station codes as VEL3D but loc 10 (VEL3D uses 20/21).

## Done (2026-10-01/02)
- Ported the VEL3D fixes (commit e2c34f3 + later): `--source goldcopy` (stream defaults to
  `prest_real_time`), timing segmenting, excess-record cleanup, `--min-piece-seconds 60`,
  deployment-start-day fallback, OOI no-data / deployment-mask handling, retry semantics,
  CSV trailing-newline guard, backfill handles `channels_N` station params.
- Processed **2026-05-02 → 2026-09-30** (152 days × 3 stations, no failures):
  MiniSEED `/Volumes/COSZO/PREST/mseed2dmc/2026/` (914 files, 492 MB); rows appended to
  `output/temporal_anomaly/metrics/RS0*_variability.csv` (565aa38). Recomputing 2026-05-01
  reproduced the original row (float rounding only).
- Fixed the 2026-05-01/05-02 rows that got glued together (CSV had no trailing newline).
- Summary figures regenerated (titles `HYSB1 - PREST` …), force-tracked despite the `*.png`
  ignore rule (73c53a5, 2e8343f); plain fig1 dropped, `fig1_dt_true_outliers.png` kept.
  README "Timing summary" embeds fig1_dt_true_outliers / fig2_jitter / fig3_gap_count.
- Outliers: same 57 flagged days as before (HYS14 2015-08..10 broken timing + 3 AXBA1),
  none in 2026-05 → 09.
- SeedLink repo side (f0b3983): `bin/run_daily_seedlink.sh <REFDES> - goldcopy`,
  `bin/daily_alerts.py`, `bin/cleanup_seedlink.sh`, repo-agnostic `bin/sync_metrics.sh`,
  `crons_prest_seedlink.txt` (replaces the old M2M seedlink cron; install TOGETHER with the
  VEL3D block), cursors `run/endtime_<REFDES>_prest.txt` seeded to **2026-10-01**, retired
  miniseed2dmc cursors removed. VM steps: `sea-water-velocity/VM_SEEDLINK_SETUP.md`.

## To do
1. **Upload 2026-05-02 → 09-30 MiniSEED** to EarthScope once Dropoff is authorized
   (account seismic@uw.edu; emailed data-submission@earthscope.org 2026-10-01). This repo
   has no Dropoff script — copy `sea-water-velocity/VEL3D-data-collection/bin/dropoff_earthscope.sh`
   (set MSEED_DIR to `/Volumes/COSZO/PREST/mseed2dmc`, `DROPOFF_PREFIX=prest`). PREST
   StationXML was already sent — don't resend unless metadata changes.
2. **VM**: the VM agent installs the SeedLink setup (ring.conf MSeedScan for this repo's
   `output/mseed/`, combined crontab, `.ooi_env`, deploy key). The old PREST clone on the
   VM may still be named `Tidal-Seafloor-Pressure` — set `PREST=` in the cron block.
3. Optional: split the old merged **2020-02-15** line in the 3 variability CSVs (two rows
   on one line, 51 fields) — user hasn't decided.
4. This Mac's PREST folder has no `.ooi_env` (only needed to run M2M here; the VM has one).
