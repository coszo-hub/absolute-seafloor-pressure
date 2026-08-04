#!/usr/bin/env python3
"""
Generate PREST parameter files (station + per-channel + run_metadata) in ../param/.

Single source of truth for the PREST (Tidal Seafloor Pressure / Tsunameter)
station, deployment, and channel metadata consumed by create_metadata.py,
OOI_metadata.py, and OOI_data_request_and_convert_mseed.py. Mirrors
make_vel3d_params.py in sea-water-velocity/VEL3D-data-collection.

Conventions (kept in lockstep with coszo-data-collection/param):
  net=OO, loc=10. r_value=1.0 — the StationXML response is flat unity because
  the pipeline converts the data to final units BEFORE writing MiniSEED.
  Pressure channels (UDO/LDO) carry conversion=0.0001450377: the pipeline
  divides raw PSI by it to get Pa (1 Pa = 0.0001450377 PSI), so the XML units
  are PA/pascal. Temperature channels (UK1/LK1) are already degC and carry
  conversion=1.0 so every channel can be divided by `conversion` uniformly.

Deployment epochs, sensor UIDs, and coordinates were transcribed from the
hand-maintained param files in coszo-data-collection/param (state of
2026-08-03), which themselves come from the OOI M2M deployment API.

Verified: every generated file parses (via read_param) to exactly the same
key->value dict as its hand-maintained counterpart, and create_metadata.py
builds identical StationXML from either set.

Usage: make_prest_params.py [out_dir]    (default: ../param)
"""
import os
import sys

PARAM_DIR = os.path.join(os.path.dirname(__file__), "..", "param")

LOC = "10"

# OOI M2M deployment-inventory base, consumed by OOI_metadata.py as `base_url`
BASE_URL = "https://ooinet.oceanobservatories.org/api/m2m/12587/events/deployment/inv"

# ── Channel kinds: NetCDF variable, description, response units ────────────────
# Pressure carries the PSI→Pa conversion; temperature is already degC.
PRESSURE = dict(
    var="absolute_pressure",
    desc="absolute_pressure, Seafloor Pressure",
    r_units="PA", r_desc="pascal",
    conversion="0.0001450377",
    conv_note="For OOI data, this value is used to convert data units preferred by EarthScope; 0.0001450377 PSI --> 1 Pa",
)
TEMP = dict(
    var="pressure_temp",
    desc="pressure_temp, Pressure Sensor Internal Temperature",
    r_units="C", r_desc="degrees Celsius",
    conversion="1.0",
    conv_note="Data already in output units; divide-by-1.0 keeps the pipeline uniform",
)

SENSOR_A = "Tidal Seafloor Pressure (Tsunameter 6,000 psia): PREST Series A"
SENSOR_B = "Tidal Seafloor Pressure (Tsunameter 2,000 psia): PREST Series B"

# ── Per-station metadata ───────────────────────────────────────────────────────
# deployments: {"1": [chan,...], "2": [...]} writes channels_1/channels_2 (+
#   data_types_1/_2); {"": [...]} writes uniform `channels` + `data_types`.
# Each channel: starts/ends/ids/rates are parallel per-epoch lists (end None =
#   open). `uncomment` reproduces keys that are live (not commented out) in the
#   hand-maintained file for that channel only.
STATIONS = [
    dict(
        refdes="RS01SLBS_MJ01A_06_PRESTA101", sta="HYSB1",
        comment="Oregon Slope Base", site="RSN Hydrate Slope Base",
        s_start="2014-09-13T00:00:01",
        s_lat="44.509772", s_lon="-125.405299", s_elev="-2909",
        c_lat="44.50977", c_lon="-125.4053", c_elev="-2909",
        sensor=SENSOR_A,
        deployments={"1": ["UDO", "UK1"], "2": ["LDO", "LK1"]},
        channels=[
            dict(cha="UDO", kind=PRESSURE, rates=["0.066667"],
                 starts=["2014-09-13T00:00:01"], ends=["2018-06-26T10:00:00"],
                 ids=["ATAPL-67639-00004"]),
            dict(cha="UK1", kind=TEMP, rates=["0.066667"],
                 starts=["2014-09-13T00:00:01"], ends=["2018-06-26T10:00:00"],
                 ids=["ATAPL-67639-00004"]),
            dict(cha="LDO", kind=PRESSURE, rates=["1.0"],
                 starts=["2018-06-26T10:00:00"], ends=[None],
                 ids=["ATAPL-67639-00005"]),
            dict(cha="LK1", kind=TEMP, rates=["1.0"],
                 starts=["2018-06-26T10:00:00"], ends=[None],
                 ids=["ATAPL-67639-00005"]),
        ],
    ),
    dict(
        refdes="RS01SUM1_LJ01B_09_PRESTB102", sta="HYS14",
        comment="Southern Hydrate Ridge (Summit 1)", site="RSN Hydrate Summit 1-4",
        s_start="2014-09-07T10:22:00",
        s_lat="44.569218", s_lon="-125.148115", s_elev="-773",
        c_lat="44.569218", c_lon="-125.148115", c_elev="-773",
        sensor=SENSOR_B,
        deployments={"1": ["UDO", "UK1"], "2": ["LDO", "LK1"]},
        channels=[
            dict(cha="UDO", kind=PRESSURE, rates=["0.066667"],
                 starts=["2014-09-07T10:22:00"], ends=["2017-08-11T00:30:00"],
                 ids=["ATAPL-69923-00001"]),
            dict(cha="UK1", kind=TEMP, rates=["0.066667"],
                 starts=["2014-09-07T10:22:00"], ends=["2017-08-11T00:30:00"],
                 ids=["ATAPL-69923-00001"]),
            dict(cha="LDO", kind=PRESSURE, rates=["1.0"],
                 starts=["2017-08-11T23:00:00"], ends=[None],
                 ids=["ATAPL-69923-00002"]),
            # NOTE: hand file lists TWO UIDs against ONE epoch; reproduced
            # verbatim (create_metadata.py only reads ids[0] per epoch).
            dict(cha="LK1", kind=TEMP, rates=["1.0"],
                 starts=["2017-08-11T23:00:00"], ends=[None],
                 ids=["ATAPL-69923-00001", "ATAPL-69923-00002"]),
        ],
    ),
    dict(
        refdes="RS03AXBS_MJ03A_06_PRESTA301", sta="AXBA1",
        comment="Axial Base Seafloor", site="RSN Axial Base 1",
        s_start="2014-08-08T16:39:00",
        s_lat="45.820222", s_lon="-129.736393", s_elev="-2610",
        c_lat="45.820222", c_lon="-129.736393", c_elev="-2610",
        sensor=SENSOR_A,
        deployments={"": ["UDO", "UK1"]},
        channels=[
            dict(cha="UDO", kind=PRESSURE, rates=["0.066667"] * 4,
                 starts=["2014-08-08T16:39:00", "2016-07-13T00:00:00",
                         "2020-08-06T05:40:00", "2022-08-30T01:37:00"],
                 ends=["2016-07-12T00:00:00", "2020-08-05T15:06:00",
                       "2022-08-29T02:19:00", None],
                 ids=["ATAPL-67639-00003", "ATAPL-67639-00006",
                      "ATAPL-67639-00003", "ATAPL-67639-00006"]),
            dict(cha="UK1", kind=TEMP, rates=["0.066667"] * 4,
                 starts=["2014-08-08T16:39:00", "2016-07-13T00:00:00",
                         "2020-08-06T05:40:00", "2022-08-30T01:37:00"],
                 ends=["2016-07-12T00:00:00", "2020-08-05T15:06:00",
                       "2022-08-29T02:19:00", None],
                 ids=["ATAPL-67639-00003", "ATAPL-67639-00006",
                      "ATAPL-67639-00003", "ATAPL-67639-00006"],
                 uncomment=("c_type", "c_clockdrift")),
        ],
    ),
]


def ln(key_val, comment):
    """One aligned `key = value    #comment` line."""
    return f"{key_val:<70}#{comment}\n"


def join(vals):
    return "; ".join("None" if v is None else v for v in vals)


def write_station_file(st, out_dir):
    chans_all = "[" + ",".join(f"{c['cha']}_{LOC}" for c in st["channels"]) + "]"
    path = os.path.join(out_dir, st["refdes"] + ".txt")
    with open(path, "w") as f:
        f.write("##parameter file##\n\n")
        f.write(f"# {st['comment']}\n\n")
        f.write(ln("net = OO", "Network Name"))
        f.write(ln("n_start = 2014-01-01T00:00:00", "Network_StartDate"))
        f.write(ln("n_end = None", "Network_EndDate"))
        f.write(ln("n_restatus = open", "Network_RestrictedStatus"))
        f.write(ln("descript = Ocean Observatories Initiative", "Description"))
        f.write(ln(f"sta = {st['sta']}", "Station Name"))
        f.write(ln(f"loc = {LOC}", "Station Location Code"))
        f.write(ln(f"s_start = {st['s_start']}",
                   "Station_StartDate --> First deployment date only, epochs are documented at the channel level"))
        f.write(ln("s_restatus = open", "Station_RestrictedStatus"))
        f.write(ln(f"s_lat = {st['s_lat']}", "Station_Latitude"))
        f.write(ln(f"s_lon = {st['s_lon']}", "Station_Longitude"))
        f.write(ln(f"s_elev = {st['s_elev']}", "Station_Elevation"))
        f.write(ln(f"s_site = {st['site']}", "Station_Site"))
        f.write(ln("s_end = None", "Station_endDate"))
        f.write(ln(f"metadata_channels = {chans_all}",
                   "Channel names --> Need channel names from all epochs"))
        by_cha = {c["cha"]: c for c in st["channels"]}
        for dep, chas in st["deployments"].items():
            suffix = f"_{dep}" if dep else ""
            chan_list = "[" + ",".join(f"{c}_{LOC}" for c in chas) + "]"
            data_types = "{" + ",".join(
                f"'{c}_{LOC}':'{by_cha[c]['kind']['var']}'" for c in chas) + "}"
            dep_note = f" --> deployment {dep}" if dep else ""
            f.write(ln(f"channels{suffix} = {chan_list}", f"Channel names{dep_note}"))
            f.write(ln(f"data_types{suffix} = {data_types}", "Data type from NetCDF header"))
    return path


def write_channel_file(st, c, out_dir):
    kind = c["kind"]
    live = c.get("uncomment", ())
    path = os.path.join(out_dir, f"{st['refdes']}_{c['cha']}_{LOC}.txt")
    with open(path, "w") as f:
        f.write("##parameter file##\n\n")
        f.write(f"# {st['comment']}\n")
        f.write(f"# Station Name: {st['sta']}\n\n")
        f.write("#Some parameters are commented out because they are optional "
                "in the stationxml and their values are unconfirmed.\n\n")
        f.write(ln(f"cha = {c['cha']}", "Channel Name"))
        f.write(ln(f"c_start = {join(c['starts'])}", "Channel_StartDate --> Deployment start dates"))
        f.write(ln(f"c_end = {join(c['ends'])}", "Channel_EndDate --> Deployment end dates"))
        f.write(ln(f"c_loc = {LOC}", "Channel_LocationCode"))
        f.write(ln(f"c_lat = {st['c_lat']}", "Channel_Latitude"))
        f.write(ln(f"c_lon = {st['c_lon']}", "Channel_Longitude"))
        f.write(ln(f"c_elev = {st['c_elev']}", "Channel_Elevation"))
        f.write(ln("c_dep = 0.0", "Channel_Depth"))
        f.write(ln("c_az = 0.0", "Channel_Azimuth"))
        f.write(ln("#c_dip = 0.0", "Channel_Dip"))
        pre = "" if "c_type" in live else "#"
        f.write(ln(f"{pre}c_type = GEOPHYSICAL", "Channel_type"))
        f.write(ln(f"c_sample_rate = {join(c['rates'])}", "Channel_SampleRate"))
        pre = "" if "c_clockdrift" in live else "#"
        f.write(ln(f"{pre}c_clockdrift = 0.0", "Channel_ClockDrift"))
        f.write(ln("#cal_unit = MICROSECOND", "Channel_CalibrationUnits"))
        f.write(ln("#cal_unit_descript = Period in microseconds", "Channel_Calibration_units_description"))
        f.write(ln(f"c_description = {kind['desc']}", "Channel_description"))
        f.write(ln(f"c_sensor = {st['sensor']}", "Channel_sensor_description"))
        f.write(ln(f"c_id = {join(c['ids'])}", "Sensor(UID) per deployment"))
        f.write(ln("r_value = 1.0", "Response_Sensitivity_Value"))
        f.write(ln(f"conversion = {kind['conversion']}", kind["conv_note"]))
        f.write(ln("r_frequency = 1.0", "Response_Sensitivity_Frequency"))
        f.write(ln(f"r_input_units = {kind['r_units']}", "Response_Sensitivity_Input_Units"))
        f.write(ln(f"r_input_description = {kind['r_desc']}", "Response_Sensitivity_Input_Units_description"))
        f.write(ln(f"r_output_units = {kind['r_units']}", "Response_Sensitivity_Output_Units"))
        f.write(ln(f"r_output_description = {kind['r_desc']}", "Response_Sensitivity_Output_Units_description"))
    return path


def write_run_metadata(out_dir):
    """Emit param/run_metadata.txt (reference_id roster + base_url) from STATIONS."""
    pairs, seen = [], set()
    for st in STATIONS:
        subsite, node = st["refdes"].split("_")[:2]
        if (subsite, node) not in seen:
            seen.add((subsite, node))
            pairs.append([subsite, node])
    ref_literal = "[" + ",".join(f'["{s}","{n}"]' for s, n in pairs) + "]"
    path = os.path.join(out_dir, "run_metadata.txt")
    with open(path, "w") as f:
        f.write("##parameter file##\n\n")
        f.write("# Generated by make_prest_params.py -- roster for OOI_metadata.py.\n")
        f.write("# Edit STATIONS in make_prest_params.py and re-run; do not hand-edit.\n\n")
        f.write(ln(f"reference_id = {ref_literal}", "[[subsite,node],...] tidal seafloor pressure"))
        f.write(ln(f"base_url = {BASE_URL}", "Base url for requesting deployment info"))
    return path


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else PARAM_DIR
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for st in STATIONS:
        written.append(write_station_file(st, out_dir))
        for c in st["channels"]:
            written.append(write_channel_file(st, c, out_dir))
    written.append(write_run_metadata(out_dir))
    for p in written:
        print("wrote", os.path.relpath(p))
    print(f"\n{len(written)} files written.")


if __name__ == "__main__":
    main()
