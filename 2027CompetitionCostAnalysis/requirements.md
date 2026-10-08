# Requirements: Diagnostic Cost and Effectiveness Comparison Script

## 1. Purpose

Build a Python script that compares four diagnostic approaches for the VIM/CDH1 question, at two scales (1,000 and 50,000 tests), and answers:

1. **Which option is cheapest** at each scale (total cost and cost per test)?
2. **Which option is most effective** (accuracy, turnaround, feasibility)?
3. **Which option is best overall** when cost and effectiveness are weighed together, and how sensitive that answer is to uncertain inputs?

Diagnostics compared: **Gel** (toehold strand-displacement RNA assay read on a gel), **Protein** (immunoassay), **Sequencing** (targeted sequencing, modeled two ways: **Sequencing-Outsourced** and **Sequencing-InHouse**), **SNP** (genotyping assay). That is five rows per scale. The targeted RNA homogeneous assay from the source table is an optional sixth row (see section 9).

All money is in **USD, 2026 prices**. Any older vendor quote or published price is converted to 2026 USD with a CPI adjustment factor stored in `config.yaml`.

## 2. Model Structure

Every diagnostic at every scale is described by the same table layout:

| Field | Fixed | Variable |
|---|---|---|
| Time to get sample | Collection setup, training, logistics (days) | Draw plus processing per patient (minutes) |
| Time to read diagnostic | Development, validation, setup (days) | Hands-on and instrument time per test (minutes) |
| Cost to get sample | Centrifuge, freezer, regulatory, courier contracts | Tube, needle, labor, shipping per sample |
| Cost to read diagnostic | Development, instruments, automation, validation | Reagents, consumables, labor, QC per test |

Core formulas:

- `total_cost(N) = fixed_sample + fixed_read + N * (var_sample + var_read) * (1 + qc_overhead)`
- `cost_per_test(N) = total_cost(N) / N`
- `total_time(N) = fixed_time + (N * var_time) / parallel_capacity`
- `cost_per_correct_result = cost_per_test / accuracy`, where `accuracy = (sens * prev + spec * (1 - prev))`
- `break_even_N(A, B) = (fixed_A - fixed_B) / (var_B - var_A)`, reported only when a positive crossover exists

## 3. Inputs

### 3.1 `inputs/cost_assumptions.csv` (one row per diagnostic and scale)

Columns: `diagnostic, method, scale, sample_type, sample_time_fixed_days, sample_time_var_min, read_time_fixed_days, read_time_var_min, sample_cost_fixed, sample_cost_var, prep_cost_fixed, prep_cost_var, prep_time_var_min, read_cost_fixed, read_cost_var, qc_overhead_pct, parallel_capacity, price_year, source, confidence`

- `method` distinguishes variants of one diagnostic (for Sequencing: `outsourced` or `in_house`; otherwise `standard`).
- `sample_type` is `whole_blood`, `plasma`, or `serum`. Whole blood skips the centrifuge step, which lowers sample-collection cost and time.
- `prep_*` columns hold sample preparation between collection and read. For the Gel assay this is the **amplification step** (section 4A), not RNA extraction.
- `price_year` is converted to 2026 USD on load.

- Each numeric field accepts `low`, `base`, `high` values (either as three columns per field or a long-format file with a `case` column).
- `source` must record where the number came from (vendor quote, core facility price list, paper). Rows with source `placeholder` must be flagged in the output.
- `confidence` is one of `low`, `medium`, `high`.

### 3.2 `inputs/performance_assumptions.csv` (one row per diagnostic)

Columns: `diagnostic, sensitivity, specificity, sample_type, invasiveness_score, technical_feasibility_score, readiness_level, regulatory_burden_score, feasibility_gate, notes`

- `feasibility_gate` is pass/fail/unknown. Example: Protein fails or is unknown until VIM/CDH1 is shown to be detectable in plasma or serum. Options that fail the gate are excluded from "best overall" and shown separately.
- Disease `prevalence` is a global parameter in the config file.

### 3.3 `config.yaml`

- Scales to evaluate (default `[1000, 50000]`, any list allowed)
- Currency `USD`, target price year `2026`, and a CPI table for converting older prices
- Prevalence, and discount or amortization period for fixed costs (optional)
- Sequencing in-house vs. outsourced: both always run and are reported side by side, plus the break-even N between them
- Assay chemistry parameters from section 4A
- Scoring weights for effectiveness: accuracy, turnaround, feasibility, invasiveness, regulatory burden (must sum to 1; validated)
- Monte Carlo settings: number of draws (default 10,000), random seed, distribution type (triangular on low/base/high)
- Flag for whether 50,000 is a one-time batch or an annual volume (affects amortization)

## 4A. Gel Assay Chemistry Constraints (from the team's literature review)

These findings change what the Gel row costs, so the script must model them explicitly instead of assuming a standard extract-then-detect workflow.

**Findings to encode as parameters:**

| Parameter | Value | Note |
|---|---|---|
| Required target RNA concentration | 10-100 nM (literature range) | Toehold-mediated strand displacement detected synthetic RNA at 50 nM in a 10 µL reaction (0.5 pmol). Coupled to an amplification cascade, detection reached about 1 fM for miRNA |
| Lowest absolute quantity proven on our device | 100 pmol per well | Much higher than the literature figure; keep both as separate inputs and flag the gap |
| Background RNA tolerance | Functional at 25 ng/µL total RNA from whole blood | Dose-response matched pure buffer in the TB mRNA example |
| RNA purification | Not required | Remove the RNA extraction kit from Gel fixed and variable costs |
| Probe purity | Critical (pure VIM and CDH1 locks) | Add a probe purification and QC cost line |
| Concentration | Amplification reaction needed | Add an amplification step (RT plus isothermal or PCR amplification) with its own cost, time, and failure rate |

**Model implications:**

1. **Workflow for Gel:** whole blood or plasma → (no extraction) → amplification → add probes → run gel. The Protein, Sequencing, and SNP workflows keep their own extraction or prep steps.
2. **Amplification feasibility check (gate):** `required_fold = target_conc_needed / expected_input_conc`. Inputs are the expected VIM/CDH1 concentration in the sample (a required user input, with low/base/high), the amplification efficiency, and the maximum realistic fold gain of the chosen amplification chemistry. If `required_fold` exceeds the achievable gain, the Gel row is flagged `feasibility_gate = fail` and excluded from "best overall" rather than silently scored.
3. **Amplification cost** is its own line: reagents and enzymes per reaction, thermocycler or heat block as a fixed cost, hands-on and run time, and added QC for contamination control (amplification increases carryover risk, so add a no-template control rate).
4. **Direct whole blood use** should make Gel sampling cheaper and faster than plasma-based options (no centrifuge, no separation), and the script should show this in the sample-collection columns.
5. **Concentration units** must be handled in code (nM, pmol, ng/µL, fM) with explicit conversions, and the report must show which unit each assumption was entered in.

## 4. Calculations the Script Must Perform

1. **Cost model:** Fixed, variable, total, and per-test cost for sample collection, diagnostic read, and combined, for every diagnostic and scale.
2. **Time model:** Fixed time (setup) and variable time (per sample), plus total elapsed time at each scale given `parallel_capacity`.
3. **Pairwise break-even:** Break-even test count between every pair of diagnostics, with a note when one option dominates at all N.
4. **Cost-effectiveness:** Cost per correct result and cost per true positive detected.
5. **Multi-criteria score:** Normalize each criterion to 0-1, apply user weights, and rank. Show the ranking at each scale.
6. **Scenario analysis:** Run low, base, and high cases for all inputs.
7. **Uncertainty analysis:** Monte Carlo over input ranges, reporting the probability that each diagnostic is cheapest and best overall, with 5th/50th/95th percentile cost per test.
8. **Sensitivity analysis:** One-at-a-time sensitivity (tornado data) showing which input moves the winner most.

## 5. Outputs

Written to `outputs/`:

| File | Contents |
|---|---|
| `cost_table.csv` / `cost_table.xlsx` | The fill-in table: type, scale, fixed and variable time and cost for sampling and reading, plus totals |
| `comparison_summary.csv` | Cost per test, total cost, total time, cost per correct result, score, and rank for each option and scale |
| `breakeven.csv` | Pairwise break-even test counts |
| `monte_carlo_results.csv` | Percentiles and win probabilities |
| `report.md` | Plain-language recommendation: cheapest, most effective, best overall at each scale, with caveats and flagged placeholder inputs |
| `figures/*.png` | Cost vs. N lines, stacked fixed/variable bars, cost per test by scale, tornado chart, cost vs. effectiveness scatter, Monte Carlo win-probability bars |

The report must state clearly when a conclusion depends on a placeholder or low-confidence input.

## 6. Command-Line Interface

```
python compare_diagnostics.py \
    --costs inputs/cost_assumptions.csv \
    --performance inputs/performance_assumptions.csv \
    --config config.yaml \
    --scenario base|low|high|all \
    --output outputs/
```

Optional flags: `--scales 1000 50000`, `--no-montecarlo`, `--export-xlsx`, `--exclude Sequencing`.

## 7. Suggested Repository Layout

Mirrors the example repo (small scripts, input CSVs, and a cost analysis folder):

```
diagnostic-cost-analysis/
├── compare_diagnostics.py      # CLI entry point
├── cost_model.py               # fixed/variable/total/break-even math
├── scoring.py                  # effectiveness scoring and ranking
├── uncertainty.py              # Monte Carlo and sensitivity
├── plots.py                    # figures
├── report.py                   # report.md generation
├── config.yaml
├── inputs/
│   ├── cost_assumptions.csv
│   └── performance_assumptions.csv
├── Cost Analysis/              # working notes, vendor quotes, source documents
├── outputs/
├── tests/
└── requirements.txt
```

## 8. Dependencies (`requirements.txt`)

```
python>=3.10
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
pyyaml>=6.0
openpyxl>=3.1      # xlsx export
pydantic>=2.0      # input validation
pytest>=7.0        # tests
scipy>=1.10        # optional: distributions
seaborn>=0.13      # optional: nicer plots
```

## 9. Optional and Future Extensions

- Add the **targeted RNA homogeneous assay** from the source table as a fifth diagnostic.
- Split the gel row into manual and automated variants at 50,000 to model the automation decision.
- Model a shared blood draw if multiple assays are run on the same patient.
- Add staged capital cost (depreciation) and regulatory costs (CLIA, CE) as separate lines.

## 10. Validation and Acceptance Criteria

- Input validation fails loudly on missing columns, negative values, weights not summing to 1, or low > base > high ordering errors.
- Unit tests cover: total cost formula, break-even with a hand-computed example, weight normalization, and a case where one option dominates at all N.
- With the same seed, Monte Carlo output is reproducible.
- Running the script on the bundled placeholder inputs produces every file in section 5 without errors.
- The cost table output matches the layout of the table the user wants to fill in (Type, Scale, Time/Cost to get sample, Time/Cost to read, each split into Fixed and Variable).
- Every placeholder input is listed in the report with a "replace with vendor quote" warning.

## 11. Open Questions to Confirm Before Building

Resolved: currency is USD 2026, and sequencing is modeled both outsourced and in-house.

1. Is 50,000 tests a one-time batch or annual volume (affects fixed-cost amortization)?
2. What sensitivity, specificity, and prevalence values should be used? These drive "most effective" and are not in the current table.
3. What weights matter most to industry: cost, speed, accuracy, or regulatory ease?
4. Should the protein option be blocked until detectability of VIM/CDH1 in blood is confirmed?
5. What VIM/CDH1 concentration is expected in whole blood or plasma? The amplification gate in section 4A depends on this.
6. Which amplification chemistry is planned (RT-PCR, isothermal such as RPA or NASBA, or a toehold-coupled cascade)? Each has different cost, speed, and achievable fold gain.
7. Your device's proven 100 pmol per well is far above the literature 0.5 pmol per 10 µL reaction. Which should the base case use?
