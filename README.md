# 📈 Interactive VWAP (HLC) Chart UI

This project provides a **deployable interactive trading chart UI** using **Streamlit + Plotly**.

Users can upload **CSV or Excel files** and instantly visualize:
- Candlestick chart
- VWAP (HLC based)
- Volume panel
- 5-minute time ticks
- Interactive hover tooltips (OHLC, Volume, OI)

---

## 🚀 Features

✔ Candlestick price chart  
✔ VWAP calculated using **(High + Low + Close) / 3**  
✔ Volume panel with correct scaling  
✔ 5-minute x-axis ticks  
✔ Hover shows:
- Time
- Open, High, Low, Close
- Volume
- Open Interest (if available)

✔ Works locally or on Streamlit Cloud  

---

## 📂 Supported File Formats
- `.csv`
- `.xlsx`

---

## 📊 Required Columns (case-insensitive)

| Column | Required |
|------|---------|
| datetime / time / timestamp | ✅ |
| open | ✅ |
| high | ✅ |
| low | ✅ |
| close | ✅ |
| volume | ✅ |
| oi | Optional |

---

## 🛠 Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv interactive_vwap_env