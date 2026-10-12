# Report — `20261012-pump-fit-response-b`

Every number below is read from a file in this `results/` directory. `teax.era_pin` is null, so reproducing these numbers needs no teax revision beyond the environment's. The run used teax revision `8d877460ac4f6f264561d916e40c1708adb13397` (see the snapshot).

## Question

How does the pump-fit constraint (`PumpStation__station__pump_fit__aa8dd6c31b6b238a`, `capacity >= demand_flow`) respond to basin area and installed pump capacity? Does energy price matter to it?

## Pump-fit verdict over the swept grid (`grid_cases.json`)

Energy price is held at 0.10, and the other inputs at their design values. Each cell gives the verdict, then the required flow (the `demand_flow` operand).

| basin_area \ installed_capacity | 0.20 | 0.25 | 0.30 |
|---|---|---|---|
| 4.0 | violated (0.28) | violated (0.28) | satisfied (0.28) |
| 8.0 | violated (0.26) | violated (0.26) | satisfied (0.26) |
| 12.0 | violated (0.24) | satisfied (0.24) | satisfied (0.24) |
| 16.0 | violated (0.22) | satisfied (0.22) | satisfied (0.22) |

- 7 of 12 points are satisfied and 5 are violated. All 12 cases completed under the sealed fingerprint.
- **Basin area:** required flow falls as area rises on the grid: 0.28, 0.26, 0.24, 0.22 at areas 4, 8, 12, 16. The verdict at capacity 0.25 flips from violated to satisfied between area 8 and area 12. At capacity 0.20 every area is violated, and at 0.30 every area is satisfied.
- **Installed capacity:** capacity does not change required flow, and it is the constraint's other operand. At every area the verdict moves from violated to satisfied as capacity rises across the grid. The flip lies between 0.25 and 0.30 at areas 4 and 8, and between 0.20 and 0.25 at areas 12 and 16.
- Annual cost (`grid_cases.json`) depends on area alone across the grid: 224.0, 208.0, 192.0, 176.0 at areas 4, 8, 12, 16. Capacity does not change it.

These are statements about 12 grid points. No point sits on the boundary (the smallest |margin| in `oracle_scan.json` is 0.01). The boundary is located only to within a grid cell, and nothing is claimed between grid points or outside the grid.

## Energy price

Energy price was not swept, by the operator's ruling. Its answer is structural (`../indicators.json`): `no_constraint_response`. No path in the module graph reaches either pump-fit operand from `PumpStation__station__energy_price`; it reaches only `annual_pumping_cost`. In this model, energy price cannot change the pump-fit verdict.

## Verification (`verification_summary.json`)

All 12 cases were sampled across both verdict strata. Both channels agree with the independent oracle at relative deviation 0.0 (tolerance 1e-9). The pump-fit verdict was re-derived from the oracle's operands with no mismatches.
