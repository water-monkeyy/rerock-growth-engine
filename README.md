# ReRock Growth Engine

Production Python system for weekly retail sales analysis and campaign planning.

Built as a real operating tool — not a demo. Turns weekly sales data into clear decisions with minimal manual work.

## Results
- **$16,906** total sales in 4 weeks
- Week 4: **$6,172** (+53.7% WoW / +72.5% vs prior 3-week average)
- Converted seasonal spike into a structured 14-day campaign system

## What it does
- Ingests weekly sales CSV data
- Calculates week-over-week dollar and percent change
- Computes prior-baseline lifts and forward scenarios
- Generates text reports, JSON output, and charts
- Supports a repeatable Monday–Wednesday–Friday operating rhythm

## Quick Start

```bash
pip install -r requirements.txt
python analyze_sales.py
