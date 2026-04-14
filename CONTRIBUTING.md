# Contributing

Thank you for your interest in contributing to the India Cities Dashboard project.

## How to Contribute

### Reporting Issues
- Open a GitHub issue describing the bug or feature request
- Include steps to reproduce for bugs
- For data corrections, cite the source of the correct data

### Adding a New City
1. Open `src/seed_data.py`
2. Add a new `CityProfile` object with all required fields:
   - `GeographicalProfile` — coordinates, elevation, coastal, seismic zone, flood risk, terrain
   - `ClimateData` — current and projected temp, rainfall, AQI, heat days, cyclone risk
   - `LandPriceData` — historical prices (2015, 2020, 2025), CAGR, projected prices
   - `PopulationData` — census 2011, estimates, growth rate, projections, density
   - `InfrastructureScore` — metro, airport, IT hub, healthcare/education/transport/water scores, green cover
3. Use publicly available and citable data sources
4. Run `python3 main.py` to verify the new city appears in all reports

### Updating Data
- All data values should be backed by a public source (census, IMD, IPCC, NAREDCO, etc.)
- Add a comment or note referencing the source when updating values
- Update projections using the methodology described in the README

### Adding a New Report or Scoring Dimension
1. Create or update the relevant module in `src/`
2. Add a report generation function returning a `pd.DataFrame`
3. Wire it into `main.py` with a `--report` option
4. Update `ReadME.md` with the new report description

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test locally: `python3 main.py` (ensure all reports run without errors)
5. Submit a pull request with a clear description

## Code Style

- Python 3.10+
- Use type hints for function signatures
- Follow existing patterns in the codebase (dataclasses for models, pandas DataFrames for reports)
- Keep modules focused: one module per analysis domain

## Data Quality Guidelines

- Use the most recent census data available
- Climate projections should reference IPCC scenario (currently RCP 4.5)
- Land prices should use area-average values, not peak locality prices
- Population figures should use metropolitan area estimates, not just municipal limits
- Clearly distinguish between census data, estimates, and projections

## Questions?

Open a GitHub issue with the label `question`.
