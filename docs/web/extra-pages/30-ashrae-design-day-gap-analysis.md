---
title: Gap analysis
---

# Gap analysis: ASHRAE HOF 2025 and EPW <-> Climate Information data model

This page is the column-level cross-check behind the
[ASHRAE and DDY mapping](20-ashrae-to-ddy-and-model-mapping.md) and
[EPW mapping](10-epw-to-model-mapping.md) notes. It checks the ASHRAE *Handbook of
Fundamentals 2025* design-conditions spreadsheet
(`HOF_2025_Climate_Design_Conditions_SI.xlsx`, single `Stations` sheet, 588 columns,
header rows 1-4) and the EnergyPlus Weather (`.epw`) format against
`schema/ClimateInformation.schema.yaml` and the worked examples in `examples/`.
Abbreviations are expanded in the
[ASHRAE and DDY mapping](20-ashrae-to-ddy-and-model-mapping.md#abbreviations).

Status as of the 2026-07-03 revision:

- **The YAML and the curated JSON example define the same set of summary variables**
  (verified programmatically; see Part 1.3).
- The curated examples match the YAML shapes. JSON Schema generation and example
  validation both run clean against the `lattice` build pinned in `pyproject.toml`.
- The EPW converter matches the EnergyPlus data dictionary field by field (Part 2).

The [revision history](#revision-history) at the end of this page records how the model
reached this state.

## Part 1: ASHRAE design data <-> model

### 1.1 Station information (cols A-O) -> `location`

| ASHRAE (col) | Model | Note |
|---|---|---|
| Region (A) | `wmo_region` (1-6) | |
| Country / Prov State / Station Name (B/C/D) | `country_code` / `subdivision` / `name` | |
| WMO (E) / WBAN (F) | `wmo_station_id` / `wban_station_id` | every Chicago artifact uses the ASHRAE 6-digit WMO `725300`. The `wigos_station_id` keeps the 5-digit traditional WMO number, which is the correct WIGOS form. |
| Lat / Lon / Elev (G/H/I) | `latitude` / `longitude` / `elevation` | the onebuilding EPW/DDY report Chicago's elevation as 201.8 m; the generators apply the ASHRAE **205 m** as a canonical override so every Chicago artifact agrees. |
| TZ Offset (K) | `time_zone_offset` | |
| Period / Climate Zone / Grade (M/N/O) | `SourceDataPeriod` / `climate_zones` / `SourceDataPeriod.ashrae_grade` | |
| StdP (J) | -- | *excluded: derived from elevation (HOF Ch. 1)* |
| TZ Code (L) | `iana_time_zone_code` instead | the IANA code is stored in place of the ASHRAE `NAC`/`EUW` code |

### 1.2 Design conditions and climate normals -> `summary_data`

Every ASHRAE design-conditions block has a model home or a recorded exclusion. The
mapping below is the authoritative column-range cross-check (the variable names are the
`ClimateSummaryData` members).

| ASHRAE section (cols) | Model variable(s) |
|---|---|
| Coldest / Hottest Month (P / AF) | `coldest_month` / `hottest_month` |
| Heating DB 99.6/99 (Q/R) + Cooling DB 0.4/1/2 (AH/AJ/AL) | `dry_bulb_temperature.annual.percent_exceedance` |
| Cooling MCWB (AI/AK/AM) | `dry_bulb_temperature_coincident_mean_wet_bulb_temperature` |
| Humidification DP 99.6/99 (S/V) + Dehumidification DP 0.4/1/2 (AV/AY/BB) | `dew_point_temperature.annual.percent_exceedance` |
| Humidification/Dehumidification MCDB (U/X, AX/BA/BD) | `dew_point_temperature_coincident_mean_dry_bulb_temperature` |
| Humidification/Dehumidification HR (T/W, AW/AZ/BC) | -- *excluded: derivable from DP and station pressure* |
| Coldest-Month WS 0.4/1 (Y/AA) | -- *not stored; only its MCDB is* |
| Coldest-Month WS MCDB (Z/AB) | `wind_speed_coincident_mean_dry_bulb_temperature` |
| MCWS to 99.6%/0.4% DB (AC/AT) | `dry_bulb_temperature_coincident_mean_wind_speed` |
| PCWD to 99.6%/0.4% DB (AD/AU) | `dry_bulb_temperature_coincident_prevailing_wind_direction` (radians) |
| Wind Shelter Factor (AE) | -- *excluded: obsolete* |
| Hottest Month DB Range (AG) | = `daily_dry_bulb_temperature_range` at the hottest month (not stored separately) |
| Evaporation WB 0.4/1/2 (AN/AP/AR) | `wet_bulb_temperature.annual.percent_exceedance` |
| Evaporation MCDB (AO/AQ/AS) | `wet_bulb_temperature_coincident_mean_dry_bulb_temperature` |
| Enthalpy 0.4/1/2 (BE/BG/BI) | `enthalpy.annual.percent_exceedance` |
| Enthalpy MCDB (BF/BH/BJ) | `enthalpy_coincident_mean_dry_bulb_temperature` |
| Extreme Max WB (BK) | `wet_bulb_temperature.annual.maximum` |
| Extreme Annual WS 1/2.5/5 (BL-BN) | `wind_speed.annual.percent_exceedance` |
| Extreme Annual DB mean/std min&max (BO-BR) | `dry_bulb_temperature.annual.{mean,standard_deviation}_{minimum,maximum}` |
| Extreme Annual WB mean/std min&max (CA-CD) | `wet_bulb_temperature.annual.{mean,standard_deviation}_{minimum,maximum}` |
| n-Year Return Period Extreme DB / WB (BS-BZ, CE-CL) | -- *excluded: derivable from extreme-annual mean/std* |
| Average Daily Temperature + its Std (CM-DL) | `daily_average_dry_bulb_temperature` (annual + monthly mean/std) |
| HDD/CDD 10 degC & 18.3 degC (DM-FL) | `heating_degree_days` / `cooling_degree_days` (two base temperatures) |
| Average Wind Speed annual+monthly (FM-FY) | `wind_speed.{annual,monthly}.mean` |
| Average / Max / Min / Std Precipitation (FZ-HY) | `liquid_precipitation_depth.{mean, maximum, minimum, standard_deviation}` |
| Monthly Design DB 0.4/2/5/10 + MCWB (HZ-LQ) | `dry_bulb_temperature.monthly` / `..._coincident_mean_wet_bulb_temperature.monthly` |
| Monthly Design WB 0.4/2/5/10 + MCDB (LR-PI) | `wet_bulb_temperature.monthly` / `..._coincident_mean_dry_bulb_temperature.monthly` |
| Mean Daily DB Range (PJ-PU) | `daily_dry_bulb_temperature_range` |
| Mean Daily DB/WB Range @ 5% design DB/WB (PV-RQ) | `daily_{dry,wet}_bulb_temperature_range_at_design_{dry,wet}_bulb_temperature` |
| Clear-Sky taub / taud (RR-SO) | `clear_sky_beam_optical_depth` / `clear_sky_diffuse_optical_depth` |
| Clear-Sky Noon Beam / Diffuse Irradiance, 21st (SP-TM) | -- *excluded: derivable from taub/taud (HOF Ch. 14)* |
| All-Sky Avg + Std Monthly GHI (TN-UK) | `daily_all_sky_solar_irradiation` (mean + standard_deviation) |
| Historical Trends / Variability / Neighbors (UL-VP) | -- *excluded: out of scope for the base model* |

### 1.3 YAML <-> JSON variable parity

Comparing the YAML `ClimateSummaryData` data elements against the curated
`examples/curated/USA_IL_Chicago-v2.1-draft.json` `summary_data`:

- **In JSON but not YAML:** *(none)*.
- **In YAML but not JSON:** `relative_humidity` only. It is defined as a summary variable
  but unused, because the ASHRAE design data has no summary relative-humidity column. This is
  intentional and harmless (a provider *may* publish it).

The two match: the YAML defines exactly the variables the example uses, plus
`relative_humidity` in reserve.

---

## Part 2: EPW <-> model

The section-level EPW mapping (the `LOCATION` line, the `DESIGN CONDITIONS` header, the
35-field hourly record, the fields with no model home, and sentinel <-> `null` handling)
is in [EPW mapping](10-epw-to-model-mapping.md). This part records how the converter was
validated against the EnergyPlus format.

### 2.1 Validation against the EnergyPlus data dictionary (2026-07-03)

The converter's EPW field table (`EPW_FIELDS` in `tools/epw_to_json.py`) was
cross-checked field by field against the EnergyPlus EPW data dictionary
([Big Ladder Software copy](https://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/energyplus-weather-file-epw-data-dictionary.html);
a local copy is kept at [EPW data dictionary](40-epw-data-dictionary.md)).

- All 20 mapped hourly fields agree with the dictionary on **position, unit, and
  missing-value sentinel**.
- The 9 unmapped numeric fields (10, 11, 19, 24-27, 31, 34) are exactly the ones listed
  under "EPW fields with no model home" in [EPW mapping](10-epw-to-model-mapping.md). The
  reverse converter re-emits them with their correct sentinels.
- A generated EPW (`examples/generated/USA_IL_Chicago-from-json.epw`) parses to 8760
  records of exactly 35 fields, with the expected header blocks.
- The sentinel <-> `null` round-trip and the EPW -> JSON -> EPW round-trip pass
  (`tools/test_climate_helpers.py`: `test_null_roundtrip_epw_json`,
  `test_roundtrip_json_epw`).

### 2.2 Design-conditions header

The EPW-derived `percent_exceedance` grids and extreme-annual statistics reproduce the
curated draft's annual blocks value for value. The annual `mean` and
`standard_deviation` are not in the header; they come from columns CM onward, which live
in the `.stat` file.

### 2.3 Known deviation: illuminance sentinel

The data dictionary flags the three illuminance fields (16/17/18) as missing when a value
is `>= 999900`, but the converter tests `>= 999999` (the printed sentinel). Every real EPW
writer emits exactly `999999` for a missing illuminance, so this has no practical effect
on the round-trip. It is recorded for completeness.

---

## Revision history

- **2026-07-03.** Revised for the expanded schema. The earlier draft listed many ASHRAE
  quantities as *missing* from the YAML; almost all of those were added in the 2026-06-12
  schema update. The structural YAML <-> JSON inconsistencies tracked in earlier drafts
  were resolved, and the curated examples were brought into line with the YAML shapes.
  The `lattice` build pinned in `pyproject.toml` parses the `ashrae_grade` constraint
  (`'["A", "B", "C", "D", "E"]'`), which an earlier build could not. Chicago's WMO
  identifier changed from the 5-digit `72530` in the curated draft to the ASHRAE 6-digit
  `725300` across all artifacts. The EPW converter was validated against the EnergyPlus
  data dictionary (Part 2).
