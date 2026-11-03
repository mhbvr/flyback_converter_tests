# Board 0.2 – waveform analysis and ngspice simulation

## 1. What the measurements say

| Quantity | Value |
|---|---|
| Input power | 4.8 V × 0.274 A = **1.315 W** |
| Output power | 172² / 31 160 Ω = **0.949 W** |
| Efficiency | **72.2 %** (0.366 W lost) |

From the scope captures (`pwm-*.csv`, plotted in `sim/img/measured.png`):

* **Operating point.** The converter runs at 100 kHz. PWM is high for 3.39 µs (D = 0.34), and the gate follows the PWM edge about 100 ns later.
* **Operating mode.** The converter runs in discontinuous mode (DCM). After turn-off the secondary conducts for about 1.2 µs. Then the drain rings freely for about 5 µs at **565 kHz**, with a decay time constant τ ≈ 16 µs.
* **Hard turn-on.** The MOSFET always turns on near a *peak* of that ring, at Vds ≈ 9–10 V (about 2·Vin). The node capacitance is discharged hard through the FET every cycle.
* **Ring capacitance.** The ring capacitance referred to the primary is about **8 nF** (565 kHz with 10 µH). With the probe moved to the secondary, the ring drops to 525 kHz. That is consistent with about 65 pF on the secondary side (winding self-capacitance, 76 pF interwinding capacitance, diode Cj) reflected ×100.
* **Turn-off spike.** The drain peaks at 27.6 V, well below the 60 V rating. The leakage ring is about 22 MHz and is strongly damped.
* **The 5 V rail sags on every pulse.** The gate voltage equals the MCP1407 supply. It falls from 4.8 V to 4.05 V during the on-time. The reflected primary voltage, read from the secondary on-state, falls from 48.7 V to 41.8 V on the secondary, i.e. 0.7 V on the primary. The 1.6 A peak primary current is drawn through a high-impedance supply path.
* **Scope caveat.** The secondary plateau reads 186–190 V although Vout is 172 V. The demagnetisation *time* does not depend on scope gain: 1.20 µs measured, 1.195 µs simulated at Vout = 172 V. That timing confirms 172 V. So the absolute CH3 reading at 100 V/div with a −204 V offset is off by roughly 7 % (offset and gain error). Do not use the absolute secondary voltage from these captures.

## 2. Simulation model (`sim/`)

| Part | Model used |
|---|---|
| CSD18533KCS | **TI vendor PSpice model** (SLPM047), downloaded and patched for ngspice by `get_models.sh` |
| DA2033-AL | Coupled inductors with Coilcraft datasheet values (doc 510): Lp 10 µH ±10 %, 1:10, leakage 0.144 µH, DCR 15 mΩ / 1.1 Ω. Coilcraft has no SPICE model for this part. |
| QH05TZ600 | Power Integrations does not publish SPICE models. Diode `.model` fitted to the datasheet: VF 2.6 V @ 5 A, CJ 17 pF @ 10 V, Qrr ≈ 6.5 nC |
| MCP1407 | Microchip's model download was blocked (HTTP 403) from the simulation environment. Behavioural driver from the datasheet instead: R_OH 2.1 Ω, R_OL 1.5 Ω, delay, quiescent current, powered from the same 5 V rail. |
| Board | Bench leads 0.15 Ω / 1.5 µH, 10 µF electrolytic (ESR fitted), 100 nF ceramic, perfboard 30 mΩ / 40 nH, 10 MΩ ‖ 15 pF probe |

Fitted parameters (everything else is datasheet):

| Parameter | Fitted value | Matched to |
|---|---|---|
| Lp | 9.5 µH | within the ±10 % tolerance |
| Electrolytic ESR | 0.45 Ω | rail droop |
| Secondary capacitance | 63 pF | 565 kHz ring |
| R_core | 1 kΩ across the primary | ring decay τ |
| Leakage damping | 150 Ω | turn-off ring |

Validation of the fitted model against the measurements:

| | measured | ngspice |
|---|---|---|
| Pin | 1.315 W | 1.314 W |
| Iin | 0.274 A | 0.274 A |
| Ring frequency / decay τ | 565 kHz / 15.9 µs | 564 kHz / 15.6 µs |
| Vds at turn-on | ≈ 9.5 V | 8.9 V |
| Gate (= VDD): 0.6 µs after turn-on / at turn-off | 4.80 / 4.06 V | 4.69 / 4.22 V |
| Secondary on-state: start / end | −48.7 / −41.8 V | −46.7 / −41.2 V |
| **Vout** | **172 V** | **180.5 V** |
| **Efficiency** | **72.2 %** | **79.6 %** |

![overlay](sim/img/ov_g1.png)

### Loss budget (fitted model)

![loss budget](sim/img/loss_budget.png)

### What-if runs

![what-if](sim/img/whatif.png)

| Case | Efficiency |
|---|---|
| Datasheet-nominal parasitics (ESR 0.3 Ω, Lp 10 µH) | 82.0 % |
| Fitted model | 79.6 % |
| Fitted + valley turn-on (period 9.18 µs ≈ 109 kHz, ton 3.26 µs for the same power) | 81.4 % |
| Fitted + low-ESR input capacitor (20 mΩ) | 86.8 % (output power also rises to 1.23 W, because the primary sees more volts) |
| Both | 88.4 % |

## 3. Likely reasons for the low efficiency

1. **No proper input capacitor for the power stage. This is the largest single loss, about 0.13–0.15 W (10–11 % of Pin).**
   * The primary draws a triangular current of 1.6 A peak and 0.62 A rms. The only local storage is the 10 µF electrolytic placed for the MCP1407, plus the bench leads.
   * The simulated ripple current in that capacitor is about **0.5 A rms**, which is probably above the rating of a small 10 µF can. It dissipates about 0.12 W in its ESR. The leads and perfboard wiring add about 0.03 W.
   * The evidence in the data is the 0.7 V sag on both the gate and the reflected primary voltage during every pulse.
   * Fix: put low-ESR ceramics right at the primary/MOSFET loop (for example 2–3 × 22 µF X5R, plus a polymer bulk capacitor). Keep that loop area small and decouple the driver separately. In simulation this alone gives +7 points.
2. **Hard capacitive turn-on at the ring peak, plus leakage ringing, about 0.05 W (4 %).**
   * The transformer is a photoflash/capacitor-charger part (designed for LT3750, which runs in boundary mode). At fixed 100 kHz it idles half of each period ringing. The 8 nF node is then dumped through the FET from about 2·Vin.
   * The leakage energy (½·Llk·Ipk² ≈ 0.19 µJ per cycle) is dissipated in the ringing.
   * Fix: turn on at a valley (adjust the frequency, or use quasi-resonant / boundary-mode control). Worth about +2 points in simulation.
3. **Core loss, ≥ 0.05 W (4 %).** This is fitted from the small-signal ring decay, so it is probably an underestimate at the real flux swing (see point 4).
4. **About 0.1 W (7 %) the model does not explain.** The real output settles at 172 V instead of 180 V. Likely candidates:
   * large-signal core loss and AC winding loss (gap fringing, proximity effect), which the linear R_core cannot capture;
   * measurement error in the bench-supply readings: 1 % error in Iin is 0.7 % in efficiency;
   * only one of the two DA2033 primary windings connected. The datasheet requires both in parallel; please check the wiring.

   Suggested checks:
   * Measure Iin with a DMM in series, and Vin at the board.
   * After a few minutes of running, compare the temperature rise of the transformer and of the 10 µF capacitor.
   * Measure Vout with the same meter.

**Not the problem:**
* MOSFET: about 21 mW including switching. 4–5 V gate drive is fine; R_DS(on) is about 6 mΩ at 4.5 V.
* Gate drive power: about 8 mW.
* QH05TZ600 diode: about 8 mW.
* Winding DCRs: below 10 mW.

## 4. Re-running

```bash
cd board_0.2/sim
./get_models.sh   # downloads the TI CSD18533KCS model and patches it for ngspice
./run_all.sh      # runs all cases (~10 min), prints loss tables, regenerates img/
```

The netlist is `sim/flyback.cir`, and `.spiceinit` selects PSpice compatibility mode.
