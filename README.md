# Trade Analytics Dashboard

An interactive Streamlit dashboard for visualizing and analyzing trade history exported from MetaTrader 5 (MT5).

## Features

- **Account Details** — displays account metadata parsed from the MT5 report header
- **Overview** — key metrics (account balance, days traded, total volume) and an interactive equity curve chart
- **Metrics** *(in progress)* — planned tab for deeper performance analytics
- **Position History** — full table of all closed trades with reformatted columns and cumulative balance

## Requirements

Install dependencies with:

```bash
pip install streamlit pandas plotly matplotlib openpyxl
```

## Usage

```bash
streamlit run streamlit_test_v1.py
```

Then open the local URL shown in your terminal, and upload your MT5 trade history file when prompted.

## Input File

The app expects an `.xlsx` export of your **Trade History Report** from MetaTrader 5. To export this from MT5:

1. Open the **History** tab in the Terminal panel
2. Right-click → **Save as Report**
3. Choose **Excel (.xlsx)** format

The file should contain account details in the first few rows followed by a table of closed positions.

## Data Processing

On upload, the app:

1. Extracts account details from the report header rows
2. Isolates the closed positions table and drops summary rows
3. Renames and reformats columns (dates, prices, PnL, swap, commission, volume)
4. Computes cumulative balance per trade and per day
5. Derives summary statistics: total PnL, net PnL (after swap), profit %, and calendar days traded

### Output Columns

| Column | Description |
|---|---|
| Date Open / Time Open | Entry date and time |
| Position | MT5 position ID |
| Symbol | Traded instrument |
| Type | Buy or Sell |
| Volume | Lot size |
| Open Price / Close Price | Entry and exit prices |
| S/L Price / T/P Price | Stop-loss and take-profit levels |
| Date Close / Time Close | Exit date and time |
| Commission | Broker commission |
| Swap | Overnight swap charges |
| PnL | Realised profit or loss |
| Current Balance | Running account balance after each trade |

## Notes

- The equity curve y-axis is automatically scaled with a small buffer around the min/max balance for readability
- Error handling is minimal at this stage — the app silently catches exceptions during file parsing
