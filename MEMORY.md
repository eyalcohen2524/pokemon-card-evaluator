# MEMORY.md - Long-Term Memory

## Projects

### Climate Alpha Engine (2026-02-11)
AI platform predicting stock/bond movements after hurricanes.
- **Insurance stocks:** 60% accuracy, filter to >15% exposure, 7-day window
- **Muni bonds:** 76.7% accuracy (IG 30-day) or 71.4% (HY 7-day)
- **Counterintuitive:** National IG ETFs (MUB/VTEB) beat state-specific funds
- Location: `climate-alpha-enhanced/`
- Reports: `REPORT.md` (stocks), `MUNI_BOND_REPORT.md` (bonds)
- Real backtested on 18 hurricanes (2004-2022)

## Technical Lessons

### OpenClaw Context Management
- Gateway restarts don't clear session token counts
- Must manually delete `.jsonl` files in `~/.openclaw/agents/main/sessions/`
- Monitor sessions >60k tokens, take action >150k

### Model Aliases
- `opus` = anthropic/claude-opus-4-5 (valid)
- opus-4.6 does NOT exist yet

## Eyal's Preferences
- Likes real data over synthetic
- Wants honest accuracy metrics, not inflated numbers
- Prefers comprehensive reports with methodology
