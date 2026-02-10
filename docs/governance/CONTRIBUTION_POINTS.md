# Contribution Points (CP) Specification

**Version:** 0.1.0 (Draft)
**Status:** Under Discussion

---

## Purpose

Contribution Points (CP) track the value each participant brings to ACCU. CP determines:
- Share of project revenue
- Voting weight in governance
- Access to Pro-Community benefits

---

## Core Principles

1. **All value counts** — code, docs, research, capital, community work
2. **Quality over quantity** — reviewed contributions worth more
3. **Recency matters** — recent work weighted higher (decay model)
4. **Transparent tracking** — all CP visible to community
5. **Non-transferable** — you can't sell or buy CP

---

## Contribution Types

### Code Contributions
| Action | Base CP | Multiplier |
|--------|---------|------------|
| PR merged (small) | 5 | 1x |
| PR merged (medium) | 15 | 1x |
| PR merged (large) | 50 | 1x |
| Critical bug fix | 30 | 1.5x |
| Security fix | 50 | 2x |
| Core feature | 100 | 1x |

### Documentation
| Action | Base CP |
|--------|---------|
| README improvement | 5 |
| Tutorial created | 20 |
| Architecture doc | 30 |
| Translation | 10 |

### Community
| Action | Base CP |
|--------|---------|
| Issue triaged | 2 |
| Community support (per week active) | 5 |
| Onboarding new contributor | 15 |
| Event organization | 25 |

### Capital & Resources
| Action | CP Formula |
|--------|------------|
| Financial contribution | $100 = 10 CP (capped at 500 CP/month) |
| Compute resources | $50/mo equivalent = 5 CP/mo |
| Infrastructure sponsorship | Custom |

### Special Contributions
| Action | Base CP |
|--------|---------|
| Project nomination (accepted) | 50 |
| Original author participation | 100 (one-time) |
| Steward service (per month) | 30 |

---

## Decay Model

CP decay over time to favor active participation:

```
Effective CP = Base CP × Decay Factor

Decay Factor:
- 0-6 months: 100%
- 6-12 months: 80%
- 12-24 months: 50%
- 24+ months: 25%
```

---

## Project-Specific CP

Each resurrected project has its own CP pool:
- Contributors earn Project CP for work on that project
- Project CP determines share of that project's revenue
- Project CP is separate from Platform CP

---

## Revenue Distribution

### Per-Project Model
```
Project Revenue (after costs)
├── 30-40% → Original Author (fixed agreement)
├── 40-50% → Project Contributors (by Project CP)
└── 15-25% → ACCU Core Pool
    ├── Infrastructure
    ├── Agent maintenance
    └── Treasury
```

### Platform Incentives
- Top 10% CP holders: Pro-Community benefits
- Top 1% CP holders: Steward nomination eligibility

---

## Tracking & Transparency

### Public Dashboard
- Total CP per contributor (pseudonymous option)
- CP breakdown by category
- Historical CP with decay applied
- Project-specific CP

### Audit Trail
- All CP awards logged with justification
- Disputes trackable
- Quarterly reconciliation

---

## Anti-Gaming Measures

1. **Peer review required** — contributions need approval
2. **Quality gates** — automated checks before CP award
3. **Dispute process** — challenges allowed within 14 days
4. **Cap on capital CP** — prevents money from dominating

---

## MVP Implementation

For MVP phase:
- Manual tracking in spreadsheet
- Weekly CP reconciliation
- Simplified categories (code, docs, other)
- No decay during MVP

---

## Open Questions

- [ ] Exact multipliers for different contribution types
- [ ] Decay curve steepness
- [ ] Capital contribution cap amount
- [ ] Anonymity vs transparency balance
