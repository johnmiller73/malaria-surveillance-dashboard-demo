# Malaria surveillance dashboard demo: routine reporting vs WHO estimates

A demonstration dashboard showing how routinely reported malaria cases and deaths compare with modelled (WHO World Malaria Report–style) estimates. It breaks the gap down by reporting system, so programmes can see which systems and which areas are missing the most data and where support should go.

> **All data in this repository are synthetic.** They were generated for demonstration with a fixed random seed. They are not real surveillance data or WHO estimates, and the country is labelled "Country X".

## What it shows

- **Headline figures**: estimated cases or deaths, how many were routinely reported, the share captured, and the reporting system with the largest gap.
- **From estimate to reported**: a waterfall that starts with the estimate and removes, in turn:
  - cases or deaths with no formal care (not reportable);
  - the unreported share in each reporting system.
- **Expected vs reported**: the estimate split by the system each case is expected to pass through, next to what each system actually reported.
- **Reporting system scorecard**: for each system, expected, reported, gap, % captured, change since 2021, reporting completeness, recording accuracy and a suggested focus.
- **Progress since 2021**: % of expected captured by each system over time.
- **Where are the largest gaps?**: a ranking table and heatmap. You can filter by system and rank by:
  - absolute gap;
  - % captured;
  - reporting completeness;
  - slowest improvement.

  Click any row to drill down.

The four reporting systems are:

- public facilities (HMIS);
- private facilities (HMIS);
- the EMR exchange;
- community HMIS.

The data drill down from national level to state, then to district. District detail is included for 9 states. All place names are anonymised ("State 01", "District 01-03").

## Run it

- **Locally:** open `index.html` in a browser. The data are embedded in `data/data.js`, so no server is needed. D3 loads from a CDN, so you need an internet connection.
- **GitHub Pages:** go to *Settings → Pages*, then deploy from the default branch, root folder.

The current selection is kept in the URL. For example, `index.html#state=CX-S02&metric=deaths` opens on one state's deaths, so you can share a link to a specific view.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The dashboard page (charts drawn with D3 v7) |
| `dash-shim.js` | Small runtime that loads the data and handles filters and redraws |
| `data/geo_2025.csv` | 2025 expected vs reported, by location × reporting system × measure (cases/deaths) |
| `data/trend_2021_2025.csv` | Yearly expected vs reported by system, national and state level |
| `data/data.js` | The two CSVs embedded as JavaScript so the page works when opened from disk |
| `scripts/make_sample_data.py` | Regenerates all of the files in `data/` |

### Key columns in `geo_2025.csv`

| Column | Meaning |
| --- | --- |
| `level`, `geo_id`, `parent_id`, `name`, `state` | Location hierarchy (National → State → District) |
| `system` | `public`, `private`, `emr`, `community`, `nocare`, `reportable` (sum of the four systems) or `total` (the WHO estimate) |
| `metric` | `cases` or `deaths` |
| `est`, `rep`, `gap` | Expected, reported, and expected − reported |
| `cap`, `cap_2021`, `cap_change` | % captured in 2025 and 2021, and the change in percentage points |
| `units_expected`, `units_reporting`, `completeness` | Reporting units (facilities or CHWs) expected to report, units that reported, and the % |
| `accuracy` | Reported ÷ (expected × completeness): how fully reporting units record what they see |
| `action` | Rule-based suggested focus |

## Using real data

To replace the sample data, produce CSVs with the same columns. Possible sources:

- **Reported counts:** an HMIS/DHIS2 export.
- **Estimates:** WHO or subnational modelled estimates.
- **Split by system:** care-seeking surveys (DHS/MIS) and facility listings.

After that, regenerate `data/data.js`, or delete it so the page reads the CSVs directly. The page then needs to be served over HTTP, for example with `python -m http.server`.

## Definitions

- **Expected per system:** the estimate multiplied by the share of care expected through that channel.
- **No formal care:** cases and deaths not expected to reach any reporting system. This is a modelling gap rather than a reporting gap, so it is excluded from the gap ranking.
- **Suggested focus**, applied in this order:
  1. EMR exchange not live → roll it out.
  2. Completeness < 70% → raise reporting completeness.
  3. Recording accuracy < 70% → improve recording and data quality.
  4. Otherwise → maintain and verify through data quality audits.
