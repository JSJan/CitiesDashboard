# Local Setup & Running Guide

## Prerequisites

- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **pip** (comes with Python) or **pip3** on macOS
- **Git** — [Download Git](https://git-scm.com/downloads)

### Verify Prerequisites

```bash
python3 --version   # Should be 3.10 or higher
pip3 --version      # Should be available
git --version       # Should be available
```

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/<your-username>/CitiesDashboard.git
cd CitiesDashboard
```

---

## Step 2: Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate    # macOS / Linux
# venv\Scripts\activate     # Windows
```

---

## Step 3: Install Dependencies

```bash
pip3 install -r requirements.txt
```

This installs:
| Package | Purpose |
|---------|---------|
| pandas | Data manipulation and report generation |
| numpy | Numerical computations (logistic growth, projections) |
| matplotlib | Plotting (reserved for future dashboard) |
| seaborn | Statistical visualizations (reserved for future dashboard) |
| tabulate | Pretty-printing tables in the terminal |

---

## Step 4: Run the Dashboard

### Full Dashboard (All Reports)
```bash
python3 main.py
```

### Individual Reports
```bash
python3 main.py --report climate      # Climate change analysis
python3 main.py --report land         # Land price analysis & ROI
python3 main.py --report population   # Population projections
python3 main.py --report ranking      # Master city ranking
python3 main.py --report buy          # Top cities to buy land
```

### City Deep Dive
```bash
python3 main.py --city Chennai
python3 main.py --city Bengaluru
python3 main.py --city Mysuru
```

Available cities: Mumbai, Delhi, Bengaluru, Chennai, Hyderabad, Kolkata, Pune, Ahmedabad, Coimbatore, Jaipur, Lucknow, Chandigarh, Kochi, Indore, Thiruvananthapuram, Visakhapatnam, Mysuru, Vadodara, Bhubaneswar

---

## Project Structure

```
CitiesDashboard/
├── main.py                     # CLI entry point
├── requirements.txt            # Python dependencies
├── ReadME.md                   # Project overview & methodology
├── ProblemStatement.md         # Original vision & requirements
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── LocalSetup.md               # This file
├── src/
│   ├── __init__.py             # Package init
│   ├── models.py               # Data models (dataclasses)
│   ├── seed_data.py            # City data for 20 Indian cities
│   ├── climate_analysis.py     # Climate risk scoring & projections
│   ├── land_price_analysis.py  # Land price CAGR & ROI analysis
│   ├── population_analysis.py  # Logistic growth modeling
│   └── scoring_engine.py       # Composite scoring & ranking
├── Prompts/
│   └── prompt1.md              # Initial project prompt
└── PromptEngineering/
    └── Learnings.md            # AI/prompt engineering notes
```

---

## Troubleshooting

### `pip: command not found`
Use `pip3` instead of `pip` on macOS.

### `ModuleNotFoundError: No module named 'src'`
Make sure you are running from the project root directory (`CitiesDashboard/`), not from inside `src/`.

### `python: command not found`
Use `python3` on macOS/Linux. On Windows, ensure Python is added to your PATH.

### Tables look misaligned in terminal
Use a monospace font and ensure your terminal width is at least 120 characters. You can resize or use:
```bash
python3 main.py --report ranking 2>&1 | less -S
```

---

## Deactivate Virtual Environment

When done:
```bash
deactivate
```
