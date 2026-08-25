# What I checked, and what the agent got wrong

## What the agent got wrong

Three bugs in the original code, and one in the verify run itself.

1. **`wear_percent` always returned 0.** The formula used `//` (integer floor-division). For any car
   that had not yet completed a full service interval, `km_since // interval` evaluates to `0`,
   so `wear_percent` returned `0 * 100 = 0` regardless of how close to the limit the car was.
   A car at 14,900 km out of 15,000 reported 0 % wear instead of ~99 %.

2. **`needs_service` wrongly flagged cars with no service record.** The original code defaulted
   `last_service_km` to `0` when the key was missing, which made the full odometer reading count
   as kilometres since service. A car with 92,000 km and no record was treated as 92,000 km
   overdue — obviously wrong. The fix is to return `False` (skip) when the key is absent.

3. **`km_to_miles` used the wrong constant.** `MILES_PER_KM = 1.609` is actually kilometres per
   mile, not miles per kilometre. The correct value is 0.621371. This made every distance reading
   about 2.6× too large.

4. **`fleet_report.fleet_summary` floored the average.** Same `//` issue: integer division dropped
   the fractional part of the wear average, giving `0.00` instead of `~59.67`.

## What I checked before I accepted the work

- Ran `python verify.py` before and after each fix to confirm each FAIL flipped to PASS.
- Ran `py -3.12 analyze.py` to verify the data analysis executed without errors and produced a
  ranked output.
- Ran `py -3.12 -m pytest test_km_wachter.py test_fleet_report.py` to confirm the test suite
  still passed after the fixes.

## What the data actually said

The group-comparison table showed:

| Column            | Broke down (mean) | Did not (mean) | Ratio |
|-------------------|-------------------|----------------|-------|
| odometer_km       | 53,448            | 53,302         | 1.00  |
| km_since_service  | 11,678            | 7,261          | 1.61  |
| avg_daily_km      | 160               | 131            | 1.22  |
| load_factor       | 0.60              | 0.51           | 1.19  |
| age_years         | 5.88              | 5.89           | 1.00  |

**Total odometer and age are not useful predictors** — the means are virtually identical between
groups. The factors that actually separate the two groups are `km_since_service` (1.61×),
`avg_daily_km` (1.22×), and `load_factor` (1.19×). Cars break down because they are being driven
hard and are overdue for service, not simply because they are old or have high total mileage.
