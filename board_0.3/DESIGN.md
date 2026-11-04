# Board 0.3 – 5 V → 170 V flyback with TL5001 control

Board 0.2 was driven open-loop from a lab PWM generator. Board 0.3 closes the loop with a **TI TL5001** voltage-mode PWM controller. The power stage keeps what we learned in board 0.2 (see `../board_0.2/ANALYSIS.md`):
* DA2033 transformer;
* discontinuous conduction mode (DCM) at 100 kHz;
* ceramic input capacitors right at the transformer;
* a 600 V ultrafast diode.

The goal of this document is to explain every component value step by step. Nothing here has been simulated yet. The numbers come from hand calculations; `calc.py` in this folder reproduces them.

---

## 1. Specification

| Parameter | Value |
|---|---|
| Input voltage | 5 V nominal (4.5–5.5 V) |
| Output voltage | 170 V |
| Output current | 0–15 mA (2.55 W max); 5.5 mA is the board 0.2 test load (31.16 kΩ) |
| Switching frequency | 100 kHz, fixed |
| Operating mode | DCM at all loads (guaranteed by the maximum-duty clamp) |
| Expected efficiency | ~85 % (a planning number, used only to size the input power) |

---

## 2. Block diagram and signal polarity

```
 +5V ──┬──────────────────────────────┬───────────────┐
       │                              │               │
   [TL5001]                        PNP Q1         DA2033 primary
   VCC  OUT ──R_B 4.7k── base       emitter=+5V       │  (P1/P2 in parallel)
   FB   COMP               │  collector──┬── MCP1407 IN   │
   RT   DTC   SCP          │             R_PD 10k     OUT ─── gate  Q2 (CSD18534KCS)
   GND             R_BE 10k (base–emitter)   │            source ─ GND
                                            GND
 secondary: DA2033 S → D1 (STTH1R06) → Cout 2.2 µF film ‖ load ‖ divider R1/R2 → FB
```

### 2.1 Why not MCP1406 (inverting)?

The TL5001 output is an **open-collector NPN that conducts during the switch on-time**. The datasheet says the output transistor is turned on while the oscillator triangle is below both the DTC and COMP voltages. With a pull-up resistor, the OUT node is therefore **low while the MOSFET should be on**. So an inverting driver has the right *polarity*, and the MCP1406 guess is logical.

The problem is the *logic levels*:

| | Value |
|---|---|
| TL5001 output saturation voltage (low level) | 1.5 V typ, **2.0 V max** at 10 mA |
| MCP1406/07 input low threshold V_IL | **0.8 V max** (1.3 V typ) |
| MCP1406/07 input high threshold V_IH | 2.4 V min |

A 1.5–2.0 V "low" is not a valid logic low for the MCP140x input. The driver may never see a low, or may switch erratically. A resistor divider cannot fix it either. The ratio between the high level (5 V) and the worst-case low level (2 V) is only 2.5, while the input needs at least 2.4 V / 0.8 V = 3 between them.

**Choice:** one small PNP transistor (MMBT3906 / 2N3906 / BC857) as a level shifter, followed by the **non-inverting MCP1407** (the same driver as board 0.2).

* **On-time.** TL5001 OUT pulls the base down through R_B, so Q1 turns on and its collector goes to about 5 V. MCP1407 IN is high and the gate is high.
* **Off-time.** OUT releases, R_BE pulls the base to 5 V, and Q1 turns off. R_PD pulls MCP1407 IN to 0 V and the gate goes low.
* **UVLO, SCP latch, or no controller supply.** OUT is off, so the gate stays low. This is the safe default.

Base current with the worst-case OUT low of 2 V: (5 − 0.7 − 2) V / 4.7 kΩ − 0.7 V / 10 kΩ ≈ **0.42 mA**. The collector only has to supply 0.5 mA into R_PD and the MCP1407 input, so Q1 is well saturated even at a gain of 10. The TL5001 sinks well under 1 mA (its limit is 20 mA).

PNP storage time (~0.2–0.3 µs) slightly stretches the on-time. It sits inside the feedback loop, so it does not matter for regulation. If the edge looks slow on the scope, a 100 pF capacitor across R_B speeds it up.

---

## 3. Power stage

### 3.1 DCM energy balance

In DCM the transformer starts every cycle with zero current. During the on-time t_on, the primary current rises linearly to

$$ I_{pk} = \frac{V_{in}\, t_{on}}{L_p} $$

and the stored energy $E = \tfrac12 L_p I_{pk}^2$ is completely transferred to the output during the off-time. The input power is therefore

$$ P_{in} = \tfrac12 L_p I_{pk}^2 f = \frac{V_{in}^2 D^2}{2 L_p f}, \qquad D = t_{on} f . $$

Setting $P_{in}\cdot\eta = V_o^2/R$ gives the DCM flyback output voltage. Note that it does not depend on the turns ratio:

$$ V_o = V_{in}\, D \sqrt{\frac{R}{2 L_p f}} \quad (\eta = 1). $$

### 3.2 Peak current and duty at full load

Full load: $P_o = 170\ \text{V} \times 15\ \text{mA} = 2.55$ W, so $P_{in} = P_o/0.85 = 3.0$ W. The energy per cycle is $E = P_{in}/f = 30\ \mu$J.

| L_p (datasheet ±10 %) | I_pk = √(2E/L_p) | t_on = L_p·I_pk / V_in,min | D | t_demag | t_on + t_demag |
|---|---|---|---|---|---|
| 9 µH | 2.58 A | 5.16 µs | 0.52 | 1.36 µs | 6.5 µs |
| 10 µH | 2.45 A | 5.44 µs | 0.54 | 1.43 µs | 6.9 µs |
| 11 µH | 2.34 A | 5.71 µs | 0.57 | 1.50 µs | 7.2 µs |

The demagnetisation time follows from the secondary inductance $n^2 L_p$, the secondary peak current $I_{pk}/n$, and the secondary voltage $V_o + V_F$:

$$ t_{demag} = \frac{n^2 L_p \cdot I_{pk}/n}{V_o + V_F} = \frac{n L_p I_{pk}}{V_o + V_F}. $$

In every row t_on + t_demag is well below the 10 µs period, so the converter is safely in DCM. The 2.6 A peak current is far below the 5 A rating of the DA2033.

### 3.3 Reflected voltage and the DCM limit

The reflected voltage during demagnetisation is $V_{OR} = (V_o + V_F)/n = 171/10 = 17.1$ V. The volt-second balance of the primary, $V_{in} t_{on} = V_{OR} t_{demag}$, gives the largest duty cycle that still stays in DCM:

$$ D_{crit} = \frac{V_{OR}}{V_{in} + V_{OR}} = 0.79 \text{ at } 4.5\text{ V}, \quad 0.76 \text{ at } 5.5\text{ V}. $$

### 3.4 Maximum-duty clamp D_max = 0.70

We clamp the duty with the TL5001 dead-time control at **D_max = 0.70**, which is below D_crit. This one choice does three jobs:

1. **The converter can never enter CCM.** That keeps the small-signal model of section 6 valid and stops the core from "walking" up in current.
2. **It is a crude current limit.** The worst case is I_pk = 5.5 V · 0.70 · 10 µs / 9 µH = **4.3 A**, still below the 5 A rating.
3. **It leaves enough headroom.** At the worst case (4.5 V input, 11 µH), the maximum input power is still 4.5 W, against the 3 W we need.

The TL5001 frequency tolerance is wide (±15 % spread). At +15 % (8.7 µs period) the worst case is t_on = 6.1 µs plus t_demag = 2.0 µs = 8.1 µs, which is still DCM.

### 3.5 Component stresses and choices

| Part | Choice | Reason |
|---|---|---|
| Transformer | DA2033-AL, **both primaries in parallel** | 10 µH, 1:10, 5 A; proven on board 0.2 |
| MOSFET Q2 | CSD18534KCS (TO-220, 60 V, logic level). CSD18533KCS from board 0.2 also works. | Peak drain voltage ≈ V_in + V_OR + leakage spike. Board 0.2 measured +5 V spike at 1.6 A; scaled to 2.6 A that is ≈ 5.5 + 17.1 + 8 ≈ 31 V, and ≈ 36 V at the 4.3 A clamp. Comfortably inside 60 V. Lower gate charge than CSD18533. |
| Diode D1 | STTH1R06 (DO-41) or MUR160, 600 V ultrafast | Peak reverse voltage ≈ 170 V + ring ≈ 255 V measured; 600 V gives margin; trr ≤ 35 ns |
| Gate driver | MCP1407 (non-inverting), 100 nF + 1 µF at VDD | Same as board 0.2; see section 2.1 |
| Input capacitors | **3 × 22 µF X7R 25 V 1210** at the transformer primary / MOSFET source | Board 0.2's biggest loss was the input path. Input AC ripple current is ≈ 0.9 A rms at 3 W; each 1210 ceramic handles several amperes at milliohm ESR. 25 V parts keep the DC-bias capacitance loss small. |
| Output capacitor | 2.2 µF / 250 V film (as board 0.2) | Ripple ≈ I_o·(T − t_demag)/C = 15 mA · 8.5 µs / 2.2 µF ≈ **58 mV p-p** (0.03 %) |

---

## 4. TL5001 configuration

### 4.1 Frequency: R_T = 100 kΩ

The datasheet characterises the TL5001 at R_T = 100 kΩ, which gives f = 100 kHz (typical). That is exactly our design frequency.

### 4.2 Dead time (maximum duty): R_DT = 113 kΩ

The datasheet gives

$$ R_{DT} = (R_T + 1250\,\Omega)\,\big[D_{max}(V_{osc,max} - V_{osc,min}) + V_{osc,min}\big] $$

with the triangle wave running from about 0.7 V to 1.3 V:

$$ R_{DT} = 101.25\ \text{k}\Omega \times (0.70 \times 0.6 + 0.7) = 113.4\ \text{k}\Omega \;\rightarrow\; \textbf{113 kΩ (E96)}, \; D_{max} = 0.69. $$

If only E24 values are at hand, 110 kΩ gives D_max = 0.64. That is still enough: 0.57 is needed at full load and minimum input.

### 4.3 Soft start: C_DT = 22 nF

A capacitor in parallel with R_DT makes the duty limit rise slowly after power-up. The time constant is

$$ \tau_{ss} = R_{DT} C_{DT} = 113\ \text{k}\Omega \times 22\ \text{nF} = 2.5\ \text{ms}. $$

The duty clamp reaches its final value in about 3–5 τ ≈ 10 ms. This limits inrush current and transformer peak current while Cout charges.

### 4.4 Short-circuit protection: C_SCP = 3.3 µF

When the output is shorted, the secondary voltage collapses. The core can then no longer reset, so DCM is lost and the current ratchets up. The SCP latch therefore must stay enabled; do not ground SCP.

The SCP timer starts whenever COMP > 1.5 V. That also happens during a normal start-up, while the loop is still out of regulation. The timeout must therefore be about 10–15 × longer than the start-up time.

**Start-up time estimate.** Cout must store $\tfrac12 C V^2 = \tfrac12 \cdot 2.2\,\mu\text{F} \cdot 170^2 = 32$ mJ. With about 3–4 W available beyond the load, plus the soft start, that takes roughly 15–20 ms.

**Timeout.** Choose t_SCP ≈ 250 ms. The datasheet gives $C_{SCP}[\mu F] = 12.46 \cdot t_{SCP}[s]$, so C_SCP = 3.1 µF → **3.3 µF** (t_SCP ≈ 265 ms).

After an SCP trip, the controller stays off until its supply is cycled.

### 4.5 Supply decoupling

The TL5001 VCC is fed through **10 Ω + 1 µF** (an RC filter, corner frequency ≈ 16 kHz) from the 5 V rail. This keeps the switching noise of the power stage away from the controller. The TL5001 draws only 1.4 mA, so the filter drops just 14 mV.

---

## 5. Output-voltage divider

The error amplifier regulates FB to the internal 1 V reference:

$$ V_o = \left(1 + \frac{R_1}{R_2}\right)\cdot 1\ \text{V}. $$

* **Divider current.** Choose about 100 µA. That is large compared with the 0.5 µA maximum error-amp bias current (0.5 % error), and small in power: 17 mW.
* **R_1 = 3 × 562 kΩ in series (1206).** Three resistors keep each one at 57 V and 6 mW, well within its voltage rating.
* **R_2 = 10.0 kΩ.** Then V_o = (1 + 1.686 MΩ / 10 kΩ) × 1 V = **169.6 V**.
* **Tolerance.** The TL5001 reference is ±5 % (TL5001A: ±3 %), so V_o can be 161–178 V. For an exact value, use R_2 = 8.2 kΩ + a 5 kΩ trimmer.
* **Bleeder.** The divider also discharges Cout after switch-off: τ = 1.7 MΩ × 2.2 µF ≈ 3.7 s. Wait about 20 s before touching the output.

---

## 6. Small-signal model of the power stage (control → output)

### 6.1 Modulator

The PWM comparator compares COMP with a 0.6 V peak-to-peak triangle (0.7–1.3 V). The duty cycle is therefore

$$ D = \frac{V_{COMP} - 0.7\ \text{V}}{V_m}, \qquad \frac{\hat d}{\hat v_c} = \frac{1}{V_m} = \frac{1}{0.6\ \text{V}}. $$

### 6.2 DCM flyback as a power source

In DCM the transformer delivers a fixed energy per cycle. Seen from the output capacitor, the power stage is a **controlled power source**: the average current it delivers into the output node is

$$ i_{src} = \frac{P_{in}}{V_o} = \frac{V_{in}^2 D^2}{2 L_p f\, V_o}. $$

The node equation at the output is $C\, dv_o/dt = i_{src} - v_o/R$. Linearising around the operating point uses two partial derivatives:

* $\partial i_{src}/\partial D = 2 I_o / D$;
* $\partial i_{src}/\partial v_o = -I_o/V_o = -1/R$. A constant-power source looks like a *negative* resistance −R.

This gives

$$ sC\,\hat v_o = \frac{2 I_o}{D}\hat d - \frac{\hat v_o}{R} - \frac{\hat v_o}{R} \quad\Rightarrow\quad \frac{\hat v_o}{\hat d} = \frac{V_o/D}{1 + s/\omega_p}, \qquad \omega_p = \frac{2}{RC}. $$

**The DCM flyback is a first-order system:** one pole at $f_p = 1/(\pi R C)$. That is why a very simple compensator is enough.

We neglect three higher-frequency terms, all far above the crossover frequency (~1 kHz) chosen below:
* the film capacitor's ESR zero (megahertz);
* the second DCM pole (near f_sw/π ≈ 30 kHz);
* the right-half-plane zero, which in DCM lies near the switching frequency.

### 6.3 Numbers

The full control-to-output transfer function is

$$ G_{vc}(s) = \frac{1}{V_m}\cdot\frac{V_o/D}{1 + s/\omega_p}. $$

| Load | R | D (5 V) | DC gain V_o/(D·V_m) | f_p | \|G_vc\| at 1 kHz |
|---|---|---|---|---|---|
| 15 mA | 11.3 kΩ | 0.45 | 627 (55.9 dB) | 12.8 Hz | 8.0 (18 dB) |
| 5.5 mA | 31.2 kΩ | 0.27 | 1040 (60.3 dB) | 4.6 Hz | 4.8 (14 dB) |
| 1 mA | 170 kΩ | 0.12 | 2430 (67.7 dB) | 0.85 Hz | 2.1 (6 dB) |
| divider only | 1.7 MΩ | 0.04 | 7670 (77.7 dB) | 0.09 Hz | 0.65 (−4 dB) |

Above the pole, the plant behaves like an integrator, $|G_{vc}| \approx K/\omega$, with

$$ K = \frac{V_o}{D V_m}\cdot\frac{2}{RC} = \frac{2 V_{in}}{V_m\, C \sqrt{2 L_p f R}} \;\propto\; \frac{V_{in}}{\sqrt{R}}. $$

So the high-frequency gain is **largest at full load and maximum input voltage**. That is the worst case for the crossover frequency and the case we design for. At lighter load the gain falls as 1/√R.

---

## 7. Compensation: one series R–C (the simplest network)

### 7.1 Network and transfer function

Put one resistor R_f and one capacitor C_f **in series from COMP to FB**. The top divider resistor R_1 is the input resistor of the inverting error amplifier. FB is a virtual ground for AC, so R_2 does not enter the AC gain. The compensator is

$$ G_c(s) = \frac{Z_f}{R_1} = \frac{R_f + \frac{1}{sC_f}}{R_1} = \frac{1 + s R_f C_f}{s\, C_f R_1}. $$

It is an **integrator** (infinite DC gain, so zero steady-state error) with a **zero** at $f_z = 1/(2\pi R_f C_f)$. Above f_z it is a flat gain $K_c = R_f/R_1$. This is the classic PI controller, or a "type II without the high-frequency pole".

The sign works out naturally. If V_o rises, FB rises, COMP falls, the duty falls and V_o falls again: negative feedback.

### 7.2 Why this works for a DCM flyback

Above its pole the plant is an integrator: −20 dB/decade, −90°. Above f_z the PI is a constant gain: 0°. The loop gain therefore crosses 0 dB with a −20 dB/decade slope and about −90° of phase, i.e. close to 90° of phase margin. A pure integrator compensator (C_f alone) would add another −90° and leave almost no margin. That is why the resistor R_f is needed.

### 7.3 Step 1 – choose the crossover frequency

* **Target f_c ≈ 1 kHz at full load and 5.5 V input** (the worst case from section 6.3).
* This is f_sw/100. The loop gain at 100 kHz is then tiny, so the output ripple does not disturb the modulator. The neglected DCM pole and RHP zero (tens of kHz and above) are also far away.
* A nixie load changes slowly, so ~1 kHz bandwidth is plenty.

### 7.4 Step 2 – the flat gain K_c sets the crossover

At crossover $|G_c \cdot G_{vc}| = 1$, and above f_z $|G_c| = K_c$:

$$ K_c = \frac{\omega_c}{K} = \frac{2\pi \cdot 1\ \text{kHz}}{50\,300\ \text{s}^{-1}\times 1.1} = 0.114. $$

Here 50 300 s⁻¹ is K at 15 mA and 5 V, and the factor 1.1 scales it to 5.5 V. Then

$$ R_f = K_c R_1 = 0.114 \times 1.686\ \text{M}\Omega = 192\ \text{k}\Omega \;\rightarrow\; \textbf{200 kΩ}\;(K_c = 0.119). $$

### 7.5 Step 3 – place the zero well below the lowest crossover

The crossover frequency falls with load (section 6.3). The phase margin is

$$ PM \approx 180^\circ - 90^\circ_{plant} - (90^\circ - \arctan(f_c/f_z)) = \arctan(f_c/f_z). $$

The lowest realistic crossover is about 90 Hz, with only the feedback divider as load. To keep about 60° there, f_z must be at or below roughly 90/1.7 ≈ 50 Hz:

$$ C_f = \frac{1}{2\pi R_f f_z} = \frac{1}{2\pi \cdot 200\ \text{k}\Omega \cdot 50\ \text{Hz}} = 15.9\ \text{nF} \;\rightarrow\; \textbf{15 nF}\;(f_z = 53\ \text{Hz}). $$

### 7.6 Step 4 – check the whole operating range

These figures come from calculating the formulas above (section 6 plant × section 7 compensator) with `calc.py`. It is not a circuit simulation.

| Load | V_in | Crossover f_c | Phase margin |
|---|---|---|---|
| 15 mA | 4.5 / 5.0 / 5.5 V | 857 / 951 / 1046 Hz | 87–88° |
| 5.5 mA | 4.5 / 5.0 / 5.5 V | 518 / 575 / 632 Hz | 85–86° |
| 1 mA | 4.5 / 5.0 / 5.5 V | 227 / 251 / 275 Hz | 77–79° |
| divider only (no load) | 4.5 / 5.0 / 5.5 V | 83 / 90 / 97 Hz | 58–61° |

The loop is stable with large margins everywhere, including no load. The gain margin is large because the plant has no other poles near the crossover.

### 7.7 Practical checks

* **COMP drive.** The TL5001 error amplifier can only source 45 µA and wants ≥ 100 kΩ DC load. The series R–C has no DC path, and its AC current is microamps, so this is fine.
* **Ripple on COMP.** 58 mV of output ripple × K_c = **7 mV p-p** on COMP, against a 600 mV ramp, so about 1 % duty jitter. If the leakage spike couples noise into FB, the standard fix is a small capacitor C_HF from COMP to FB. 47 pF puts a pole at 1/(2π·200 kΩ·47 pF) ≈ 17 kHz and costs only about 3° of phase margin at 1 kHz; do not go much larger, because 220 pF would already put the pole at 3.6 kHz, too close to the crossover. Leave its footprint empty at first.
* **Start-up overshoot (integrator wind-up).** During start-up COMP sits at its upper limit (2.3 V), and the duty is limited by the DTC soft start. Once V_o reaches 170 V, the proportional path pulls COMP down by K_c·ΔV_o. Getting from 2.3 V to the clamp level (~1.12 V) needs ΔV_o ≈ 1.2 V / 0.119 ≈ **10 V**. Expect up to about 6 % overshoot at start-up, which then decays through the load. This is acceptable for nixies; confirm it in simulation.
* **Minimum on-time.** With only the divider as load, D ≈ 0.04, so t_on ≈ 0.4 µs. The PNP storage time (~0.2–0.3 µs) is of the same order. The converter may then skip pulses or run in bursts at no load. That is harmless for a nixie supply.

---

## 8. Bill of materials (control and power path)

| Ref | Value | Notes |
|---|---|---|
| U1 | TL5001ACD (or TL5001CP for perfboard) | the "A" version has a ±3 % reference |
| R_T | 100 kΩ 1 % | f ≈ 100 kHz |
| R_DT ‖ C_DT | 113 kΩ 1 % ‖ 22 nF | D_max ≈ 0.69, soft start τ = 2.5 ms |
| C_SCP | 3.3 µF X7R | SCP timeout ≈ 265 ms |
| R_1 | 3 × 562 kΩ 1 % (1206) | high-voltage feedback |
| R_2 | 10.0 kΩ 1 % (optionally 8.2 kΩ + 5 kΩ trimmer) | V_o = 169.6 V |
| R_f, C_f | 200 kΩ, 15 nF (C0G or film) | compensation, COMP → FB in series |
| C_HF | DNP (footprint for 47 pF) | optional noise filter, COMP → FB |
| VCC filter | 10 Ω + 1 µF | TL5001 supply |
| Q1 | MMBT3906 / 2N3906 / BC857 | level shifter |
| R_B, R_BE, R_PD | 4.7 kΩ, 10 kΩ, 10 kΩ | Q1 base, base–emitter, collector pull-down |
| U2 | MCP1407 + 1 µF ‖ 100 nF at VDD | non-inverting gate driver |
| Q2 | CSD18534KCS (or CSD18533KCS) | 60 V logic-level MOSFET |
| T1 | DA2033-AL | both primaries in parallel |
| D1 | STTH1R06 or MUR160 | 600 V ultrafast |
| C_in | 3 × 22 µF X7R 25 V 1210 | directly at the primary / MOSFET source loop |
| C_out | 2.2 µF 250 V film | output |

---

## 9. Next steps (not done yet)

1. **Simulate** with the board 0.2 ngspice setup: replace the PWM source with a TL5001 behavioural model (1 V reference, 0.7–1.3 V ramp, D_max clamp). Check start-up overshoot, load steps (1 → 15 mA) and the loop gain (injection at FB).
2. **Build it** with the input ceramics and the MOSFET source return on one short, wide loop.
3. **Measure the loop gain** on the bench (injection resistor in series with R_1) and compare it with section 7.6.
