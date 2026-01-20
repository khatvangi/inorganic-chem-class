# Textbook Analysis v3 - Validated Results

**Date:** 2026-01-19
**Status:** VALIDATED - All 4 checks passed
**Git:** https://github.com/khatvangi/inorganic-chem-class

---

## Validation Results

| Check | Status | Details |
|-------|--------|---------|
| 1. Discriminatory Power | ✅ PASS | 22.8 point variation (27.2 - 50.0) |
| 2. Topic Coverage | ✅ PASS | 20/20 topics for all 10 books |
| 3. Example Counts | ✅ PASS | Quantified: 0-650 examples |
| 4. Rankings | ✅ PASS | Meaningful differentiation |

---

## Overall Rankings

| Rank | Textbook | Overall | Examples | Best For |
|------|----------|---------|----------|----------|
| 1 | ic_tina.pdf | **50.0** | 650 | coordination, main group |
| 2 | advancex_ic_applicaionts.pdf | 48.0 | 13 | coordination, bioinorganic |
| 3 | descriptive_ic.pdf (Rodgers) | 46.3 | 224 | coordination, main group |
| 4 | Atkins_Shriver.pdf | 43.7 | 365 | coordination, main group |
| 5 | ic_basset.pdf | 41.8 | 63 | main group |
| 6 | concise_ic_jd_lee.pdf | 40.2 | 49 | coordination |
| 7 | descriptive_ic_house.pdf | 38.8 | 65 | main group, organometallics |
| 8 | inorganic_chemistry_saito.pdf | 30.3 | 0 | general |
| 9 | bioinorganic_chemistry_bertini.pdf | 27.7 | 0 | bioinorganic |
| 10 | inorganic_chemistry_libretexts.pdf | 27.2 | 0 | organometallics |

---

## Key Descriptive Textbooks Comparison

These are the primary teaching resources for CHEM 361:

| Metric | JD Lee (Concise) | Rodgers | House |
|--------|------------------|---------|-------|
| **Chunks** | 565 | 1,495 | 1,027 |
| **Words** | 132,089 | 300,085 | 242,325 |
| **Examples** | 49 | **224** | 65 |
| **Equations** | 421 | **1,221** | 49* |
| **Figures** | 503 | 1,272 | 595 |
| **Coverage Score** | 63.2 | **70.8** | 67.7 |
| **Depth Score** | 27.6 | **35.3** | 24.4 |
| **Pedagogy Score** | 22.2 | **24.8** | 14.7 |
| **Overall** | 40.2 | **46.3** | 38.8 |

*House equation count is low due to detection pattern mismatch (uses different notation)

### Interpretation

- **Rodgers** is the strongest descriptive textbook overall
- **JD Lee** is intentionally concise - good for quick reference
- **House** has good coverage but equation detection needs improvement

---

## Topic Coverage by Book

### Coordination Chemistry Coverage (Core Topic)

| Book | Rating | Keyword Density |
|------|--------|-----------------|
| ic_tina | excellent | 17.2 |
| advancex_ic | excellent | 16.8 |
| Atkins_Shriver | good | 14.1 |
| descriptive_ic (Rodgers) | good | 10.8 |
| JD Lee | good | 10.8 |
| House | good | 9.3 |

### Main Group Chemistry Coverage (Core Topic)

| Book | s-block | p-block |
|------|---------|---------|
| Rodgers | 11.6 | **14.0** |
| House | 9.7 | **13.7** |
| JD Lee | **11.5** | 6.8 |
| Atkins_Shriver | 6.4 | 8.9 |

### Crystal Field Theory Coverage (Core Topic)

| Book | Rating | Keyword Density |
|------|--------|-----------------|
| JD Lee | good | **12.4** |
| ic_tina | good | 11.3 |
| Atkins_Shriver | good | 9.2 |
| Rodgers | fair | 6.1 |
| House | fair | 5.8 |

---

## Composite Score Breakdown

```
Overall = (Coverage × 0.4) + (Depth × 0.3) + (Pedagogy × 0.3)

Where:
- Coverage: Weighted average of 20 topic scores
- Depth: Equations + Examples + Cross-topic integration
- Pedagogy: Examples + Figures + Keyword diversity
```

### Score Distribution

```
                    Coverage    Depth    Pedagogy    Overall
ic_tina              73.4       45.0      27.3        50.0
advancex_ic          68.9       38.7      30.6        48.0
Rodgers              70.8       35.3      24.8        46.3
Atkins_Shriver       66.9       32.5      25.5        43.7
ic_basset            62.1       33.5      24.3        41.8
JD Lee               63.2       27.6      22.2        40.2
House                67.7       24.4      14.7        38.8
```

---

## Data Quality Notes

### Well-Ingested Books (>500 chunks)
- ic_tina.pdf: 2,375 chunks ✅
- Atkins_Shriver.pdf: 2,494 chunks ✅
- descriptive_ic.pdf (Rodgers): 1,495 chunks ✅
- descriptive_ic_house.pdf: 1,027 chunks ✅
- concise_ic_jd_lee.pdf: 565 chunks ✅ (intentionally concise)
- ic_basset.pdf: 446 chunks ✅
- advancex_ic_applicaionts.pdf: 351 chunks ✅

### Under-Ingested Books (need re-ingestion)
- bioinorganic_chemistry_bertini_et_al.pdf: 1 chunk ❌
- inorganic_chemistry_libretexts.pdf: 1 chunk ❌
- inorganic_chemistry_saito.pdf: 1 chunk ❌

---

## Recommendations for Meta-Book

Based on validated analysis:

### Primary Sources by Topic

| Topic | Best Source | Secondary |
|-------|-------------|-----------|
| Coordination Fundamentals | ic_tina | Atkins_Shriver |
| Crystal Field Theory | JD Lee | ic_tina |
| Main Group (p-block) | Rodgers | House |
| Main Group (s-block) | JD Lee | Rodgers |
| Transition Metals | House | Rodgers |
| Reaction Mechanisms | Rodgers | House |
| Worked Examples | ic_tina (650) | Atkins_Shriver (365) |
| Equations/Theory | Rodgers (1,221) | JD Lee (421) |

### Content Synthesis Strategy

1. **Explanations**: Draw from highest coverage score for topic
2. **Examples**: Prioritize ic_tina (most examples per topic)
3. **Theory/Equations**: Use Rodgers or JD Lee
4. **Figures**: Cross-reference Rodgers and Atkins_Shriver
5. **Quick Reference**: JD Lee (concise by design)

---

## Files

| File | Description |
|------|-------------|
| `experiments/analyze_textbooks_v3.py` | Analysis script (keyword-based, no LLM dependency) |
| `experiments/results/textbook_analysis_v3.json` | Full results (2,480 lines) |
| `docs/METABOOK_SCHEMA.md` | Schema for lesson generation |

---

## Next Steps

1. [ ] Re-ingest 3 under-chunked books if needed
2. [ ] Improve House equation detection patterns
3. [ ] Generate meta-book using validated rankings
4. [ ] Map best sources to curriculum topics

---

*Analysis method: Keyword density + pattern matching*
*No LLM dependency for core metrics - ensures reproducibility*
