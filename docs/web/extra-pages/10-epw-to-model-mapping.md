---
title: EPW mapping
---

# EnergyPlus Weather (EPW / TMY) -> Climate Information data model

A companion to the Climate Information specification (`ClimateInformation`) and the worked
examples in `examples/`. The specification describes the data model itself: its
structure, unit system, conventions, and rules. This document maps the EnergyPlus Weather
format onto that model. `tools/epw_to_json.py` and `tools/json_to_epw.py` implement the
mapping in both directions, and the test suite checks the round-trip.

This is the section-level map. Companions:

- [EPW data dictionary](40-epw-data-dictionary.md): the EPW format itself, field by field.
- [Gap analysis](30-ashrae-design-day-gap-analysis.md) (Part 2): the record of the
  converter's validation against the EnergyPlus data dictionary.
- [ASHRAE and DDY mapping](20-ashrae-to-ddy-and-model-mapping.md): the ASHRAE design
  conditions, which are what the EPW `DESIGN CONDITIONS` header carries. Its
  [abbreviations table](20-ashrae-to-ddy-and-model-mapping.md#abbreviations) expands the
  terms used on these pages.

An EPW file (`.epw`) is a time-series format with an optional design-conditions header.
Typical Meteorological Year (TMY) files carry similar hourly data in a different layout.
Design-day (DDY) files carry design conditions only and are covered in
[ASHRAE and DDY mapping](20-ashrae-to-ddy-and-model-mapping.md). The original EPW
documentation is at
https://climate.onebuilding.org/papers/EnergyPlus_Weather_File_Format.pdf.

## `LOCATION` line -> `location`

`LOCATION, City, State, Country, Source, WMO, Lat, Lon, TZ, Elevation`

| EPW field | Model |
|---|---|
| City / State / Country | `name` / `subdivision` / `country_code` |
| WMO | `wmo_station_id` |
| Lat / Lon / TZ / Elevation | `latitude` / `longitude` / `time_zone_offset` / `elevation` |
| *(none)* | `iana_time_zone_code`: EPW has no IANA code, so it is inferred as `Etc/GMT+/-N` from the offset |
| *(none)* | `anemometer_height` (10 m) / `station_height` (1.8 m), assumed |

## `DESIGN CONDITIONS` line -> `summary_data`

The EPW `DESIGN CONDITIONS` header is the ASHRAE spreadsheet columns P-CL laid end to end
in three labeled sections (`Heating` = P-AE, `Cooling` = AF-BK, `Extremes` = BL-CL). It
maps to the annual design conditions exactly as set out in
[ASHRAE and DDY mapping](20-ashrae-to-ddy-and-model-mapping.md). It is the only summary an
EPW carries. Everything from spreadsheet column CM onward (average daily temperature,
degree days, average and monthly wind speed, precipitation, monthly design DB/WB, mean
daily ranges, and clear-sky and all-sky solar) lives in the `.stat` file, so those
`ClimateSummaryData` variables are absent from an EPW-derived summary. The header is
optional, and the converter reads it only on request (`--epw-header-design`, off by
default) because the DDY is the preferred design source.

## Hourly records (35 fields) -> `time_series`

| EPW field (index) | Model `ClimateTimeSeries` variable | Conversion to base SI |
|---|---|---|
| Dry-bulb temperature (6) | `dry_bulb_temperature` | degC -> K |
| Dew-point temperature (7) | `dew_point_temperature` | degC -> K |
| Relative humidity (8) | `relative_humidity` | % -> fraction |
| Atmospheric pressure (9) | `atmospheric_pressure` | Pa (as-is) |
| Horizontal IR sky (12) | `horizontal_infrared_sky_irradiance` | Wh/m2-h ~= W/m2 |
| Global horizontal radiation (13) | `global_horizontal_irradiation` (SUM) | Wh/m2 -> J/m2 (x3600) |
| Direct normal radiation (14) | `direct_normal_irradiation` (SUM) | Wh/m2 -> J/m2 |
| Diffuse horizontal radiation (15) | `diffuse_horizontal_irradiation` (SUM) | Wh/m2 -> J/m2 |
| Global/Direct/Diffuse illuminance (16/17/18) | `*_illuminance` | lux (as-is) |
| Wind direction (20) | `wind_direction` | degrees -> radians |
| Wind speed (21) | `wind_speed` | m/s (as-is) |
| Total / Opaque sky cover (22/23) | `total_sky_cover` / `opaque_sky_cover` | tenths -> fraction |
| Precipitable water (28) | `precipitable_water` | mm -> m |
| Aerosol optical depth (29) | `aerosol_optical_depth` | unitless |
| Snow depth (30) | `snow_depth` | cm -> m |
| Albedo (32) | `ground_albedo` | unitless |
| Liquid precipitation depth (33) | `liquid_precipitation_depth` (SUM) | mm -> m |

EPW reports radiation as energy received over the hour (Wh/m2), so it maps to the model's
irradiation variables (`J/m2`, `value_type = SUM`) rather than the instantaneous
irradiance variables (`W/m2`). The date and time columns are encoded in the
`TimeInterval` rather than stored as variables.

## Exclusions and missing values

### EPW fields with no model home

Year/Month/Day/Hour/Minute (encoded in the `TimeInterval` instead), the
data-source/uncertainty flag string, extraterrestrial horizontal and direct-normal
radiation (10/11), zenith luminance (19), visibility (24), ceiling height (25),
present-weather observation and codes (26/27), days since last snowfall (31), and
liquid-precipitation quantity/hours (34).

### Model time-series variables not present in an EPW

`wet_bulb_temperature`, `humidity_ratio`, the instantaneous irradiance forms
(`global/direct/diffuse_*_irradiance`), `sky_type`, and the whole air-quality and
pollutant set (`particulate_matter_*`, `carbon_dioxide`, `nitrogen_dioxide`,
`nitrogen_oxide`, `sulphur_dioxide`, `ozone`, `ammonia`, `carbon_monoxide`,
`formaldehyde`, `benzene`, `voc`, `turbidity`, `lead`, `mercury`).

### Missing values: EPW sentinels and model null

EPW has no blank or missing-value concept. Every field carries a numeric sentinel instead
(99.9 degC for temperature, 999 for %/direction/speed, 9999 for Wh/m2, 999999 for
pressure and illuminance, and so on). The model supports an explicit `null`, so on import
(`epw_to_json.py`) each sentinel becomes `null`, and on export (`json_to_epw.py`) each
`null` returns to the sentinel. `tools/test_climate_helpers.py::test_null_roundtrip_epw_json`
checks this round-trip. One illuminance edge case is recorded in the
[Gap analysis](30-ashrae-design-day-gap-analysis.md) (Part 2).

On reverse conversion, quantities the model omits (humidity ratio, wind shelter factor,
n-year return periods) come back blank in the generated `DESIGN CONDITIONS` line, and the
EPW fields listed under "EPW fields with no model home" come back as their sentinels. The
data the model carries round-trips exactly.
