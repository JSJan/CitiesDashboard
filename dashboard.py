"""
India Cities Dashboard — Interactive Web App (Streamlit + Plotly)

Run with:
    streamlit run dashboard.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.seed_data import get_all_cities
from src.chennai_areas_data import get_chennai_areas
from src.world_cities_data import get_world_cities, USD_TO_INR
from src.climate_analysis import generate_climate_report, climate_risk_score
from src.land_price_analysis import generate_land_report, generate_price_timeline, monte_carlo_price_simulation
from src.population_analysis import generate_population_report, generate_population_timeline, estimate_carrying_capacity
from src.scoring_engine import generate_master_ranking, get_top_cities_to_buy, compute_all_scores
from src.chennai_area_analysis import generate_area_ranking, generate_zone_summary, get_top_areas_to_buy
from src.llm.query_engine import QueryEngine
from src.scrapers.pipeline import run_weather_pipeline, run_real_estate_pipeline, get_pipeline_status


# ────────────────────────── PAGE CONFIG ──────────────────────────

st.set_page_config(
    page_title="India Cities Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────── LOAD DATA ──────────────────────────

@st.cache_data
def load_cities():
    cities = get_all_cities()
    compute_all_scores(cities)
    return cities

@st.cache_data
def load_chennai_areas():
    return get_chennai_areas()

@st.cache_data
def load_world_cities():
    return get_world_cities()

cities = load_cities()
areas = load_chennai_areas()
world_cities = load_world_cities()

# ────────────────────────── SIDEBAR ──────────────────────────

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select View",
    [
        "Master Ranking",
        "City Comparison",
        "Climate Analysis",
        "Land Price Analysis",
        "Population Analysis",
        "Chennai Areas",
        "Pondicherry Areas",
        "Investment Calculator",
        "🤖 AI Query",
        "🌍 World Cities",
        "📈 Price Timeline",
        "⛰️ Hill Stations",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")

# Tier filter
tier_filter = st.sidebar.multiselect(
    "City Tier", [1, 2, 3], default=[1, 2, 3]
)
filtered_cities = [c for c in cities if c.tier in tier_filter]

# State filter
all_states = sorted(set(c.state for c in cities))
state_filter = st.sidebar.multiselect(
    "State", all_states, default=all_states
)
filtered_cities = [c for c in filtered_cities if c.state in state_filter]

# Price range filter
all_prices = [c.land_price.avg_price_per_sqft_2025 for c in cities]
price_min, price_max = int(min(all_prices)), int(max(all_prices))
price_range = st.sidebar.slider(
    "Price Range (₹/sqft)", price_min, price_max, (price_min, price_max), step=500
)
filtered_cities = [
    c for c in filtered_cities
    if price_range[0] <= c.land_price.avg_price_per_sqft_2025 <= price_range[1]
]

# Minimum overall score filter
min_score = st.sidebar.slider("Min Overall Score", 0, 100, 0, step=5)

# Apply min score filter (only for pages that use scored cities)
if min_score > 0:
    filtered_cities = [
        c for c in filtered_cities
        if hasattr(c, 'overall_score') and (c.overall_score or 0) >= min_score
    ]

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: Census 2011, IMD, IPCC AR6, NAREDCO estimates. "
    "Projections through 2050/2070. Not financial advice."
)

# ── Refresh Data ──
st.sidebar.markdown("---")
st.sidebar.markdown("**Live Data**")

_status = get_pipeline_status()
_last_run = _status.get("last_run")
if _last_run:
    from datetime import datetime as _dt
    try:
        _last_dt = _dt.fromisoformat(_last_run)
        _age = _dt.now() - _last_dt
        _age_str = f"{_age.days}d ago" if _age.days > 0 else f"{_age.seconds // 3600}h ago"
    except Exception:
        _age_str = "unknown"
    st.sidebar.caption(f"Last refresh: {_age_str}")
else:
    st.sidebar.caption("Never refreshed")

_refresh_scope = st.sidebar.selectbox(
    "Refresh scope",
    ["Weather (free, no key)", "Real Estate (scrape)", "All"],
    label_visibility="collapsed",
)

if st.sidebar.button("🔄 Refresh Live Data", use_container_width=True):
    with st.sidebar.status("Fetching live data...", expanded=True) as _status_ui:
        try:
            if _refresh_scope in ("Weather (free, no key)", "All"):
                st.sidebar.write("Fetching weather...")
                _w = run_weather_pipeline(cities)
                st.sidebar.write(f"Weather: {_w['details']}")
            if _refresh_scope in ("Real Estate (scrape)", "All"):
                st.sidebar.write("Scraping real estate...")
                _r = run_real_estate_pipeline(cities, areas)
                st.sidebar.write(f"Real estate: {_r['details']}")
            _status_ui.update(label="Refresh complete!", state="complete")
        except Exception as _e:
            _status_ui.update(label=f"Error: {_e}", state="error")
    st.cache_data.clear()
    st.rerun()

# ────────────────────────── HEADER ──────────────────────────

st.title("🏙️ India Cities Dashboard")
st.caption("Sustainability • Liveability • Climate • Land Investment • Population — Projections 2025 → 2050 → 2070")

# ────────────────────────── PAGES ──────────────────────────

if page == "Master Ranking":
    st.header("Master City Ranking")
    st.markdown("**Overall = Liveability (35%) + Sustainability (35%) + Investment (30%)**")

    df = generate_master_ranking(filtered_cities)

    # Highlight metrics
    col1, col2, col3, col4 = st.columns(4)
    if not df.empty:
        top = df.iloc[0]
        col1.metric("Top City", top["City"])
        col2.metric("Overall Score", top["Overall Score"])
        col3.metric("Liveability", top["Liveability"])
        col4.metric("Sustainability", top["Sustainability"])

    # Color-coded table
    st.dataframe(
        df.style.background_gradient(subset=["Overall Score"], cmap="RdYlGn")
              .background_gradient(subset=["Climate Risk"], cmap="RdYlGn_r"),
        width="stretch",
        hide_index=True,
    )

    # Bar chart
    fig = px.bar(
        df, x="City", y=["Liveability", "Sustainability", "Investment"],
        barmode="group", title="Score Breakdown by City",
        color_discrete_sequence=["#2ecc71", "#3498db", "#e74c3c"],
    )
    fig.update_layout(yaxis_title="Score (0-100)", xaxis_tickangle=-45)
    st.plotly_chart(fig, width="stretch")


elif page == "City Comparison":
    st.header("City Comparison")

    city_names = [c.name for c in filtered_cities]
    selected = st.multiselect("Select cities to compare (2-4)", city_names, default=city_names[:3])

    if len(selected) < 2:
        st.warning("Select at least 2 cities to compare.")
    else:
        sel_cities = [c for c in filtered_cities if c.name in selected]

        # Radar chart
        categories = ["Liveability", "Sustainability", "Investment",
                       "Climate Safety", "Infrastructure", "Green Cover"]

        fig = go.Figure()
        for city in sel_cities:
            infra_avg = (city.infrastructure.healthcare_score +
                         city.infrastructure.education_score +
                         city.infrastructure.transport_score +
                         city.infrastructure.water_supply_score) / 4 * 10
            climate_safety = max(0, 100 - climate_risk_score(city))
            values = [
                city.liveability_score, city.sustainability_score,
                city.investment_score, climate_safety,
                infra_avg, min(100, city.infrastructure.green_cover_pct * 3),
            ]
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself", name=city.name,
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="City Comparison Radar",
        )
        st.plotly_chart(fig, width="stretch")

        # Side-by-side metrics
        cols = st.columns(len(sel_cities))
        for col, city in zip(cols, sel_cities):
            with col:
                st.subheader(city.name)
                st.metric("Tier", city.tier)
                st.metric("Price ₹/sqft", f"₹{city.land_price.avg_price_per_sqft_2025:,.0f}")
                st.metric("Price 2050", f"₹{city.land_price.projected_price_2050:,.0f}")
                st.metric("Population", f"{city.population.population_2025:,}")
                st.metric("AQI", city.climate.air_quality_index)
                st.metric("Flood Risk", city.geo.flood_risk.title())


elif page == "Climate Analysis":
    st.header("Climate Change Analysis & Risk Assessment")

    df = generate_climate_report(filtered_cities)
    st.dataframe(
        df.style.background_gradient(subset=["Climate Risk Score"], cmap="RdYlGn_r"),
        width="stretch", hide_index=True,
    )

    # Temperature projection chart
    fig = go.Figure()
    for city in filtered_cities:
        fig.add_trace(go.Scatter(
            x=["2025", "2050", "2070"],
            y=[
                city.climate.avg_temp_c,
                city.climate.avg_temp_c + city.climate.projected_temp_rise_2050,
                city.climate.avg_temp_c + city.climate.projected_temp_rise_2070,
            ],
            mode="lines+markers", name=city.name,
        ))
    fig.update_layout(
        title="Temperature Projection by City",
        xaxis_title="Year", yaxis_title="Avg Temperature (°C)",
    )
    st.plotly_chart(fig, width="stretch")

    # AQI comparison
    aqi_data = pd.DataFrame([{
        "City": c.name,
        "Current AQI": c.climate.air_quality_index,
        "AQI 2050": c.climate.projected_aqi_2050,
        "AQI 2070": c.climate.projected_aqi_2070,
    } for c in filtered_cities])
    fig = px.bar(
        aqi_data, x="City", y=["Current AQI", "AQI 2050", "AQI 2070"],
        barmode="group", title="Air Quality Index Trajectory",
        color_discrete_sequence=["#27ae60", "#f39c12", "#e74c3c"],
    )
    st.plotly_chart(fig, width="stretch")


elif page == "Land Price Analysis":
    st.header("Land Price Analysis & Investment Potential")

    df = generate_land_report(filtered_cities)
    st.dataframe(
        df.style.background_gradient(subset=["Investment Score"], cmap="RdYlGn"),
        width="stretch", hide_index=True,
    )

    # Price timeline chart
    timelines = []
    for city in filtered_cities:
        timelines.append(generate_price_timeline(city))
    all_timelines = pd.concat(timelines, ignore_index=True)

    fig = px.line(
        all_timelines, x="Year", y="Price_per_sqft_INR", color="City",
        title="Land Price Projection (₹/sqft) — 2015 to 2070",
    )
    fig.add_vline(x=2025, line_dash="dash", line_color="gray",
                  annotation_text="Today")
    st.plotly_chart(fig, width="stretch")

    # Buy recommendations
    st.subheader("Top Cities to Buy Land Today")
    buy_df = get_top_cities_to_buy(filtered_cities, top_n=10)
    st.dataframe(buy_df, width="stretch", hide_index=True)

    # Monte Carlo uncertainty bands
    st.subheader("Price Uncertainty — Monte Carlo Simulation")
    mc_city_name = st.selectbox(
        "Select city for uncertainty analysis",
        [c.name for c in filtered_cities],
        key="mc_city",
    )
    mc_city = next(c for c in filtered_cities if c.name == mc_city_name)
    mc_df = monte_carlo_price_simulation(mc_city)

    fig_mc = go.Figure()
    # P10-P90 band (light)
    fig_mc.add_trace(go.Scatter(
        x=list(mc_df["Year"]) + list(mc_df["Year"][::-1]),
        y=list(mc_df["P90"]) + list(mc_df["P10"][::-1]),
        fill="toself", fillcolor="rgba(46,204,113,0.1)",
        line=dict(color="rgba(0,0,0,0)"), name="P10–P90 range",
    ))
    # P25-P75 band (darker)
    fig_mc.add_trace(go.Scatter(
        x=list(mc_df["Year"]) + list(mc_df["Year"][::-1]),
        y=list(mc_df["P75"]) + list(mc_df["P25"][::-1]),
        fill="toself", fillcolor="rgba(46,204,113,0.25)",
        line=dict(color="rgba(0,0,0,0)"), name="P25–P75 range",
    ))
    # Median line
    fig_mc.add_trace(go.Scatter(
        x=mc_df["Year"], y=mc_df["P50"],
        mode="lines", name="Median (P50)",
        line=dict(color="#2ecc71", width=3),
    ))
    fig_mc.update_layout(
        title=f"Land Price Uncertainty — {mc_city_name} (1,000 simulations)",
        xaxis_title="Year", yaxis_title="Price (₹/sqft)",
    )
    st.plotly_chart(fig_mc, width="stretch")
    st.caption("Bands show 10th–90th and 25th–75th percentile ranges from Monte Carlo simulation varying annual CAGR.")


elif page == "Population Analysis":
    st.header("Population Analysis & Projections")

    df = generate_population_report(filtered_cities)
    st.dataframe(df, width="stretch", hide_index=True)

    # Population timeline
    timelines = []
    for city in filtered_cities:
        timelines.append(generate_population_timeline(city))
    all_timelines = pd.concat(timelines, ignore_index=True)

    fig = px.line(
        all_timelines, x="Year", y="Population", color="City",
        title="Population Projection — 2011 to 2070 (dashed lines = carrying capacity)",
    )
    fig.add_vline(x=2025, line_dash="dash", line_color="gray",
                  annotation_text="Today")
    # Add carrying capacity lines for each city
    for city in filtered_cities:
        cap = estimate_carrying_capacity(city)
        fig.add_hline(
            y=cap, line_dash="dot", line_color="rgba(150,150,150,0.4)",
            annotation_text=f"{city.name} cap",
            annotation_font_size=9,
            annotation_font_color="gray",
        )
    st.plotly_chart(fig, width="stretch")

    # Growth rate comparison
    growth_data = pd.DataFrame([{
        "City": c.name, "Growth Rate (%/yr)": c.population.growth_rate_pct,
        "Density (/km²)": c.population.density_per_sqkm,
    } for c in filtered_cities])
    fig = px.scatter(
        growth_data, x="Density (/km²)", y="Growth Rate (%/yr)",
        text="City", title="Population Growth vs Density",
        size="Growth Rate (%/yr)", color="Growth Rate (%/yr)",
        color_continuous_scale="RdYlGn",
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, width="stretch")


elif page == "Chennai Areas":
    st.header("Chennai — Zone & Area-Level Analysis")

    chennai_areas = [a for a in areas if a.city == "Chennai"]

    tab1, tab2, tab3 = st.tabs(["Zone Summary", "Area Ranking", "Buy Recommendations"])

    with tab1:
        zone_df = generate_zone_summary(chennai_areas)
        st.dataframe(zone_df, width="stretch", hide_index=True)

        # Zone price comparison
        fig = px.bar(
            zone_df, x="Zone", y=["Avg Liveability", "Avg Investment"],
            barmode="group", title="Zone-wise Scores",
            color_discrete_sequence=["#2ecc71", "#e74c3c"],
        )
        st.plotly_chart(fig, width="stretch")

    with tab2:
        # Zone filter for areas
        zone_names = sorted(set(a.zone for a in chennai_areas))
        zone_filter = st.multiselect("Filter by Zone", zone_names, default=zone_names)
        filtered_areas = [a for a in chennai_areas if a.zone in zone_filter]

        rank_df = generate_area_ranking(filtered_areas)
        st.dataframe(
            rank_df.style.background_gradient(subset=["Overall"], cmap="RdYlGn"),
            width="stretch", hide_index=True,
        )

        # Price scatter
        scatter_data = pd.DataFrame([{
            "Area": a.name, "Zone": a.zone,
            "Price 2025": a.land_price.price_per_sqft_2025,
            "CAGR %": a.land_price.cagr_2015_2025,
            "Flood Prone": a.flood_prone,
        } for a in filtered_areas])
        fig = px.scatter(
            scatter_data, x="Price 2025", y="CAGR %",
            color="Zone", symbol="Flood Prone", text="Area",
            title="Price vs Growth Rate by Area",
            size="CAGR %",
        )
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, width="stretch")

    with tab3:
        buy_df = get_top_areas_to_buy(chennai_areas, top_n=15)
        st.dataframe(buy_df, width="stretch", hide_index=True)


elif page == "Investment Calculator":
    st.header("Investment Calculator")
    st.markdown("Estimate your returns if you invest today in a specific city or Chennai area.")

    calc_type = st.radio("Invest in:", ["City", "Chennai Area"])

    if calc_type == "City":
        city_name = st.selectbox("Select City", [c.name for c in cities])
        city = next(c for c in cities if c.name == city_name)
        current_price = city.land_price.avg_price_per_sqft_2025
        price_2050 = city.land_price.projected_price_2050
        price_2070 = city.land_price.projected_price_2070
    else:
        area_name = st.selectbox("Select Area", [a.name for a in areas])
        area = next(a for a in areas if a.name == area_name)
        current_price = area.land_price.price_per_sqft_2025
        price_2050 = area.land_price.projected_2050
        price_2070 = area.land_price.projected_2070

    col1, col2 = st.columns(2)
    with col1:
        investment_sqft = st.number_input("Area (sq ft)", min_value=100, value=1000, step=100)
    with col2:
        investment_amt = current_price * investment_sqft
        st.metric("Investment Today", f"₹{investment_amt:,.0f}")

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    value_2050 = price_2050 * investment_sqft
    value_2070 = price_2070 * investment_sqft
    roi_2050 = ((value_2050 - investment_amt) / investment_amt) * 100
    roi_2070 = ((value_2070 - investment_amt) / investment_amt) * 100

    col1.metric("Current Price", f"₹{current_price:,.0f}/sqft")
    col2.metric("Value in 2050", f"₹{value_2050:,.0f}", f"+{roi_2050:.0f}% ROI")
    col3.metric("Value in 2070", f"₹{value_2070:,.0f}", f"+{roi_2070:.0f}% ROI")

    # Timeline chart
    years = [2025, 2030, 2040, 2050, 2060, 2070]
    if calc_type == "City":
        prices = [
            current_price,
            city.land_price.projected_price_2030,
            city.land_price.projected_price_2040,
            price_2050,
            (price_2050 + price_2070) / 2,
            price_2070,
        ]
    else:
        prices = [
            current_price,
            area.land_price.projected_2030,
            area.land_price.projected_2040,
            price_2050,
            (price_2050 + price_2070) / 2,
            price_2070,
        ]
    values = [p * investment_sqft for p in prices]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=values, mode="lines+markers+text",
        text=[f"₹{v:,.0f}" for v in values],
        textposition="top center",
        fill="tozeroy", fillcolor="rgba(46,204,113,0.1)",
        line=dict(color="#2ecc71", width=3),
    ))
    fig.add_hline(y=investment_amt, line_dash="dash", line_color="red",
                  annotation_text=f"Initial: ₹{investment_amt:,.0f}")
    loc_name = city_name if calc_type == "City" else area_name
    fig.update_layout(
        title=f"Investment Value Over Time — {loc_name} ({investment_sqft} sqft)",
        xaxis_title="Year", yaxis_title="Portfolio Value (₹)",
    )
    st.plotly_chart(fig, width="stretch")

    st.info(
        "**Disclaimer:** Projections are based on historical CAGR trends and are estimates only. "
        "Actual returns may vary significantly. This is not financial advice."
    )

elif page == "Pondicherry Areas":
    st.header("Pondicherry — Area-Level Analysis")

    pondy_areas = [a for a in areas if a.city == "Pondicherry"]
    if not pondy_areas:
        st.warning("No Pondicherry area data available.")
    else:
        tab1, tab2 = st.tabs(["Area Ranking", "Price Comparison"])

        with tab1:
            rank_df = generate_area_ranking(pondy_areas)
            st.dataframe(
                rank_df.style.background_gradient(subset=["Overall"], cmap="RdYlGn"),
                width="stretch", hide_index=True,
            )

        with tab2:
            scatter_data = pd.DataFrame([{
                "Area": a.name, "Zone": a.zone,
                "Price 2025": a.land_price.price_per_sqft_2025,
                "CAGR %": a.land_price.cagr_2015_2025,
                "Coastal": a.coastal_proximity,
            } for a in pondy_areas])
            fig = px.scatter(
                scatter_data, x="Price 2025", y="CAGR %",
                color="Zone", text="Area",
                title="Pondicherry — Price vs Growth Rate",
                size="CAGR %", symbol="Coastal",
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, width="stretch")

            # Bar chart of projected prices
            proj_data = pd.DataFrame([{
                "Area": a.name,
                "2025": a.land_price.price_per_sqft_2025,
                "2030": a.land_price.projected_2030,
                "2050": a.land_price.projected_2050,
                "2070": a.land_price.projected_2070,
            } for a in pondy_areas])
            proj_melt = proj_data.melt(id_vars="Area", var_name="Year", value_name="Price (₹/sqft)")
            fig2 = px.bar(
                proj_melt, x="Area", y="Price (₹/sqft)", color="Year",
                barmode="group", title="Projected Land Prices by Area",
            )
            st.plotly_chart(fig2, width="stretch")


elif page == "🤖 AI Query":
    st.header("🤖 AI-Powered Query Interface")
    st.markdown(
        "Ask questions in plain English about cities, land prices, climate, "
        "and investment potential. Uses LLM when available, otherwise rule-based parsing."
    )

    engine = QueryEngine(cities=cities, areas=areas)
    method_label = "LLM (GPT-4o-mini)" if engine.openai_client else "Rule-based"
    st.caption(f"Engine: **{method_label}**")

    question = st.text_input(
        "Ask a question",
        placeholder="e.g., Compare Mumbai vs Pune for investment",
    )

    # Example questions
    with st.expander("Example questions"):
        examples = [
            "Top 5 cities for investment",
            "Compare Bengaluru vs Chennai vs Hyderabad",
            "Cities with AQI below 60",
            "Best area in Chennai to buy land",
            "Which tier 2 cities have best liveability?",
            "Cities with price under 5000 per sqft",
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}"):
                question = ex

    if question:
        with st.spinner("Thinking..."):
            result = engine.query(question)

        answer = result.get("answer")
        data = result.get("data")
        intent = result.get("intent", "")

        # Generate summary when rule-based engine returns None answer
        if answer is None and data is not None:
            if isinstance(data, list) and len(data) > 0:
                answer = f"Found **{len(data)}** results for your query ({intent}):"
            elif isinstance(data, dict):
                answer = f"Here are the details ({intent}):"
            else:
                answer = "Here are the results:"

        st.subheader("Answer")
        st.markdown(answer or "No answer generated.")

        # Show data if present
        if data is not None:
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                st.dataframe(pd.DataFrame(data), width="stretch", hide_index=True)
            elif isinstance(data, dict):
                st.json(data)
            elif isinstance(data, pd.DataFrame):
                st.dataframe(data, width="stretch", hide_index=True)

        st.caption(f"Method: {result.get('method', 'unknown')} | Intent: {result.get('intent', 'N/A')}")


elif page == "🌍 World Cities":
    st.header("🌍 Global City Benchmarks")
    st.markdown("Compare Indian cities with global counterparts across key metrics.")

    # Build comparison dataframe
    def _infra_avg(city):
        i = city.infrastructure
        return round((i.healthcare_score + i.education_score + i.transport_score + i.water_supply_score) / 4, 1)

    world_data = []
    for wc in world_cities:
        usd_price = wc.land_price.avg_price_per_sqft_2025
        world_data.append({
            "City": wc.name,
            "Country": wc.state,
            "Population (M)": round(wc.population.population_2025 / 1e6, 1),
            "Price (USD/sqft)": usd_price,
            "Price (₹/sqft)": int(usd_price * USD_TO_INR),
            "AQI": wc.climate.air_quality_index,
            "Green Cover %": wc.infrastructure.green_cover_pct,
            "Infra Score": _infra_avg(wc),
        })

    india_data = []
    for c in cities:
        inr_price = c.land_price.avg_price_per_sqft_2025
        india_data.append({
            "City": c.name,
            "Country": "India",
            "Population (M)": round(c.population.population_2025 / 1e6, 1),
            "Price (USD/sqft)": int(inr_price / USD_TO_INR),
            "Price (₹/sqft)": inr_price,
            "AQI": c.climate.air_quality_index,
            "Green Cover %": c.infrastructure.green_cover_pct,
            "Infra Score": _infra_avg(c),
        })

    combined_df = pd.DataFrame(world_data + india_data)

    tab1, tab2, tab3 = st.tabs(["Comparison Table", "Price Comparison", "Liveability Scatter"])

    with tab1:
        st.dataframe(
            combined_df.sort_values("Price (USD/sqft)", ascending=False),
            width="stretch", hide_index=True,
        )

    with tab2:
        fig = px.bar(
            combined_df.sort_values("Price (USD/sqft)", ascending=False),
            x="City", y="Price (USD/sqft)", color="Country",
            title="Land Price Comparison — Global vs India (USD/sqft)",
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, width="stretch")

    with tab3:
        fig = px.scatter(
            combined_df, x="AQI", y="Infra Score",
            color="Country", size="Population (M)", text="City",
            title="Air Quality vs Infrastructure — Global Benchmark",
        )
        fig.update_traces(textposition="top center")
        fig.update_xaxes(title="AQI (lower is better)")
        st.plotly_chart(fig, width="stretch")


elif page == "📈 Price Timeline":
    st.header("📈 Land Price Increase Over the Years")
    st.markdown("Track how land prices have grown and are projected to grow across cities and areas.")

    tab1, tab2, tab3 = st.tabs(["City Price Timeline", "Chennai Area Timeline", "Outskirts Growth"])

    # ── Tab 1: City-level price timelines ──
    with tab1:
        city_names = [c.name for c in filtered_cities]
        selected_cities = st.multiselect(
            "Select cities to compare", city_names,
            default=city_names[:5] if len(city_names) >= 5 else city_names,
            key="pt_cities",
        )

        timeline_rows = []
        for c in filtered_cities:
            if c.name not in selected_cities:
                continue
            lp = c.land_price
            for year, price in [
                (2015, lp.avg_price_per_sqft_2015),
                (2020, lp.avg_price_per_sqft_2020),
                (2025, lp.avg_price_per_sqft_2025),
                (2030, lp.projected_price_2030),
                (2040, lp.projected_price_2040),
                (2050, lp.projected_price_2050),
                (2070, lp.projected_price_2070),
            ]:
                timeline_rows.append({"City": c.name, "Year": year, "Price (₹/sqft)": price})

        if timeline_rows:
            tl_df = pd.DataFrame(timeline_rows)
            fig = px.line(
                tl_df, x="Year", y="Price (₹/sqft)", color="City",
                markers=True, title="Land Price Timeline — Cities (₹/sqft)",
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, width="stretch")

            # Growth multiplier table
            growth_rows = []
            for c in filtered_cities:
                if c.name not in selected_cities:
                    continue
                lp = c.land_price
                growth_rows.append({
                    "City": c.name,
                    "2015 (₹)": f"{lp.avg_price_per_sqft_2015:,.0f}",
                    "2025 (₹)": f"{lp.avg_price_per_sqft_2025:,.0f}",
                    "2050 (₹)": f"{lp.projected_price_2050:,.0f}",
                    "2070 (₹)": f"{lp.projected_price_2070:,.0f}",
                    "CAGR %": f"{lp.cagr_2015_2025:.1f}",
                    "10yr Growth": f"{lp.avg_price_per_sqft_2025 / lp.avg_price_per_sqft_2015:.1f}x",
                    "2025→2050": f"{lp.projected_price_2050 / lp.avg_price_per_sqft_2025:.1f}x",
                    "2025→2070": f"{lp.projected_price_2070 / lp.avg_price_per_sqft_2025:.1f}x",
                })
            st.dataframe(pd.DataFrame(growth_rows), width="stretch", hide_index=True)
        else:
            st.info("Select at least one city.")

    # ── Tab 2: Chennai area price timeline ──
    with tab2:
        chennai_areas_all = [a for a in areas if a.city == "Chennai" and a.zone != "Outskirts"]
        area_names = [a.name for a in chennai_areas_all]
        selected_areas = st.multiselect(
            "Select Chennai areas", area_names,
            default=area_names[:6] if len(area_names) >= 6 else area_names,
            key="pt_areas",
        )

        area_rows = []
        for a in chennai_areas_all:
            if a.name not in selected_areas:
                continue
            lp = a.land_price
            for year, price in [
                (2015, lp.price_per_sqft_2015),
                (2020, lp.price_per_sqft_2020),
                (2025, lp.price_per_sqft_2025),
                (2030, lp.projected_2030),
                (2040, lp.projected_2040),
                (2050, lp.projected_2050),
                (2070, lp.projected_2070),
            ]:
                area_rows.append({"Area": a.name, "Zone": a.zone, "Year": year, "Price (₹/sqft)": price})

        if area_rows:
            area_df = pd.DataFrame(area_rows)
            fig = px.line(
                area_df, x="Year", y="Price (₹/sqft)", color="Area",
                markers=True, title="Chennai Area Price Timeline (₹/sqft)",
                line_dash="Zone",
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, width="stretch")

            # Growth table for areas
            agrowth = []
            for a in chennai_areas_all:
                if a.name not in selected_areas:
                    continue
                lp = a.land_price
                agrowth.append({
                    "Area": a.name, "Zone": a.zone,
                    "2015": f"₹{lp.price_per_sqft_2015:,}",
                    "2025": f"₹{lp.price_per_sqft_2025:,}",
                    "2050": f"₹{lp.projected_2050:,}",
                    "2070": f"₹{lp.projected_2070:,}",
                    "CAGR %": f"{lp.cagr_2015_2025:.1f}",
                    "25yr Growth": f"{lp.projected_2050 / lp.price_per_sqft_2025:.1f}x",
                })
            st.dataframe(pd.DataFrame(agrowth), width="stretch", hide_index=True)
        else:
            st.info("Select at least one area.")

    # ── Tab 3: Outskirts high-growth areas ──
    with tab3:
        st.markdown(
            "**Outskirts and emerging areas** typically show the highest CAGR "
            "due to lower base prices and rapid infrastructure development."
        )
        outskirts = [a for a in areas if a.city == "Chennai" and a.zone == "Outskirts"]
        if not outskirts:
            st.warning("No outskirts data available.")
        else:
            out_rows = []
            for a in outskirts:
                lp = a.land_price
                for year, price in [
                    (2015, lp.price_per_sqft_2015),
                    (2020, lp.price_per_sqft_2020),
                    (2025, lp.price_per_sqft_2025),
                    (2030, lp.projected_2030),
                    (2040, lp.projected_2040),
                    (2050, lp.projected_2050),
                    (2070, lp.projected_2070),
                ]:
                    out_rows.append({"Area": a.name, "Year": year, "Price (₹/sqft)": price})

            out_df = pd.DataFrame(out_rows)
            fig = px.line(
                out_df, x="Year", y="Price (₹/sqft)", color="Area",
                markers=True, title="Outskirts Price Timeline — Highest Growth Potential",
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, width="stretch")

            # Summary metrics
            cols = st.columns(len(outskirts))
            for col, a in zip(cols, outskirts):
                lp = a.land_price
                growth = lp.projected_2050 / lp.price_per_sqft_2025
                col.metric(
                    a.name,
                    f"₹{lp.price_per_sqft_2025:,}/sqft",
                    f"{lp.cagr_2015_2025:.1f}% CAGR · {growth:.0f}x by 2050",
                )


elif page == "⛰️ Hill Stations":
    st.header("⛰️ Hill Stations — Investment & Liveability Analysis")
    st.markdown(
        "Compare hill stations across South and North India for retirement living, "
        "vacation homes, and long-term land investment."
    )

    # Identify hill stations by terrain + elevation
    hill_stations = [
        c for c in cities
        if c.geo.terrain_type == "hilly" and c.geo.elevation_m >= 800
    ]
    south_hills = [c for c in hill_stations if c.geo.latitude < 20]
    north_hills = [c for c in hill_stations if c.geo.latitude >= 20]

    # Region selector
    region = st.radio("Region", ["All", "South India", "North India"], horizontal=True)
    if region == "South India":
        display_hills = south_hills
    elif region == "North India":
        display_hills = north_hills
    else:
        display_hills = hill_stations

    if not display_hills:
        st.warning("No hill stations found for this filter.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "Overview", "Investment ROI", "Price Timeline", "Climate Advantage",
        ])

        with tab1:
            overview_rows = []
            for c in display_hills:
                lp = c.land_price
                region_label = "South" if c.geo.latitude < 20 else "North"
                overview_rows.append({
                    "Hill Station": c.name,
                    "State": c.state,
                    "Region": region_label,
                    "Elevation (m)": c.geo.elevation_m,
                    "Avg Temp (°C)": c.climate.avg_temp_c,
                    "AQI": c.climate.air_quality_index,
                    "Green Cover %": c.infrastructure.green_cover_pct,
                    "Price 2025 (₹/sqft)": f"{lp.avg_price_per_sqft_2025:,}",
                    "CAGR %": lp.cagr_2015_2025,
                    "Flood Risk": c.geo.flood_risk,
                })
            st.dataframe(
                pd.DataFrame(overview_rows),
                width="stretch", hide_index=True,
            )

            # Key metrics
            cheapest = min(display_hills, key=lambda c: c.land_price.avg_price_per_sqft_2025)
            best_cagr = max(display_hills, key=lambda c: c.land_price.cagr_2015_2025)
            cleanest = min(display_hills, key=lambda c: c.climate.air_quality_index)
            coolest = min(display_hills, key=lambda c: c.climate.avg_temp_c)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Cheapest", cheapest.name, f"₹{cheapest.land_price.avg_price_per_sqft_2025:,}/sqft")
            col2.metric("Highest Growth", best_cagr.name, f"{best_cagr.land_price.cagr_2015_2025}% CAGR")
            col3.metric("Cleanest Air", cleanest.name, f"AQI {cleanest.climate.air_quality_index}")
            col4.metric("Coolest", coolest.name, f"{coolest.climate.avg_temp_c}°C")

        with tab2:
            st.subheader("Return on Investment Analysis")
            st.markdown("Assuming ₹50 lakh investment today — how much land and what returns?")

            investment = 5000000  # ₹50 lakh

            roi_rows = []
            for c in display_hills:
                lp = c.land_price
                sqft_bought = investment / lp.avg_price_per_sqft_2025
                value_2030 = sqft_bought * lp.projected_price_2030
                value_2050 = sqft_bought * lp.projected_price_2050
                value_2070 = sqft_bought * lp.projected_price_2070
                roi_2050 = ((value_2050 - investment) / investment) * 100
                roi_2070 = ((value_2070 - investment) / investment) * 100
                region_label = "South" if c.geo.latitude < 20 else "North"
                roi_rows.append({
                    "Hill Station": c.name,
                    "Region": region_label,
                    "Sqft Bought": f"{sqft_bought:,.0f}",
                    "Value 2030 (₹)": f"{value_2030:,.0f}",
                    "Value 2050 (₹)": f"{value_2050:,.0f}",
                    "Value 2070 (₹)": f"{value_2070:,.0f}",
                    "ROI 2050 %": f"{roi_2050:,.0f}%",
                    "ROI 2070 %": f"{roi_2070:,.0f}%",
                    "Growth 25yr": f"{lp.projected_price_2050 / lp.avg_price_per_sqft_2025:.1f}x",
                })
            roi_df = pd.DataFrame(roi_rows)
            st.dataframe(roi_df, width="stretch", hide_index=True)

            # ROI bar chart
            chart_data = pd.DataFrame([{
                "Hill Station": c.name,
                "ROI 2050 %": ((c.land_price.projected_price_2050 / c.land_price.avg_price_per_sqft_2025) - 1) * 100,
                "ROI 2070 %": ((c.land_price.projected_price_2070 / c.land_price.avg_price_per_sqft_2025) - 1) * 100,
            } for c in display_hills])
            chart_melt = chart_data.melt(id_vars="Hill Station", var_name="Horizon", value_name="ROI %")
            fig = px.bar(
                chart_melt, x="Hill Station", y="ROI %", color="Horizon",
                barmode="group", title="Return on Investment — Hill Stations (₹50L invested today)",
                color_discrete_sequence=["#2ecc71", "#3498db"],
            )
            st.plotly_chart(fig, width="stretch")

        with tab3:
            st.subheader("Land Price Timeline — 2015 to 2070")
            tl_rows = []
            for c in display_hills:
                lp = c.land_price
                region_label = "South" if c.geo.latitude < 20 else "North"
                for year, price in [
                    (2015, lp.avg_price_per_sqft_2015),
                    (2020, lp.avg_price_per_sqft_2020),
                    (2025, lp.avg_price_per_sqft_2025),
                    (2030, lp.projected_price_2030),
                    (2040, lp.projected_price_2040),
                    (2050, lp.projected_price_2050),
                    (2070, lp.projected_price_2070),
                ]:
                    tl_rows.append({
                        "Hill Station": c.name, "Region": region_label,
                        "Year": year, "Price (₹/sqft)": price,
                    })

            tl_df = pd.DataFrame(tl_rows)
            fig = px.line(
                tl_df, x="Year", y="Price (₹/sqft)", color="Hill Station",
                markers=True, line_dash="Region",
                title="Hill Station Land Prices — Historical & Projected",
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, width="stretch")

            # Growth multiplier table
            growth_rows = []
            for c in display_hills:
                lp = c.land_price
                growth_rows.append({
                    "Hill Station": c.name,
                    "2015 (₹)": f"{lp.avg_price_per_sqft_2015:,}",
                    "2025 (₹)": f"{lp.avg_price_per_sqft_2025:,}",
                    "2050 (₹)": f"{lp.projected_price_2050:,}",
                    "2070 (₹)": f"{lp.projected_price_2070:,}",
                    "10yr": f"{lp.avg_price_per_sqft_2025 / lp.avg_price_per_sqft_2015:.1f}x",
                    "25yr": f"{lp.projected_price_2050 / lp.avg_price_per_sqft_2025:.1f}x",
                    "45yr": f"{lp.projected_price_2070 / lp.avg_price_per_sqft_2025:.1f}x",
                })
            st.dataframe(pd.DataFrame(growth_rows), width="stretch", hide_index=True)

        with tab4:
            st.subheader("Climate Advantage — Why Hill Stations?")
            st.markdown(
                "Hill stations offer **cooler temperatures**, **cleaner air**, and **higher green cover** "
                "compared to plains cities. As climate change worsens urban heat, these advantages will drive demand."
            )

            # Compare hill stations vs metro averages
            metros = [c for c in cities if c.tier == 1]
            avg_metro_temp = sum(c.climate.avg_temp_c for c in metros) / len(metros)
            avg_metro_aqi = sum(c.climate.air_quality_index for c in metros) / len(metros)
            avg_hill_temp = sum(c.climate.avg_temp_c for c in display_hills) / len(display_hills)
            avg_hill_aqi = sum(c.climate.air_quality_index for c in display_hills) / len(display_hills)

            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Avg Temperature",
                f"{avg_hill_temp:.1f}°C (Hills)",
                f"{avg_hill_temp - avg_metro_temp:.1f}°C vs Metros",
            )
            col2.metric(
                "Avg AQI",
                f"{avg_hill_aqi:.0f} (Hills)",
                f"{avg_hill_aqi - avg_metro_aqi:.0f} vs Metros",
            )
            avg_hill_green = sum(c.infrastructure.green_cover_pct for c in display_hills) / len(display_hills)
            avg_metro_green = sum(c.infrastructure.green_cover_pct for c in metros) / len(metros)
            col3.metric(
                "Avg Green Cover",
                f"{avg_hill_green:.0f}% (Hills)",
                f"+{avg_hill_green - avg_metro_green:.0f}% vs Metros",
            )

            # Scatter: Temp vs AQI colored by elevation
            climate_data = pd.DataFrame([{
                "Hill Station": c.name,
                "Avg Temp (°C)": c.climate.avg_temp_c,
                "AQI": c.climate.air_quality_index,
                "Elevation (m)": c.geo.elevation_m,
                "Green Cover %": c.infrastructure.green_cover_pct,
            } for c in display_hills])
            fig = px.scatter(
                climate_data, x="Avg Temp (°C)", y="AQI",
                size="Green Cover %", color="Elevation (m)",
                text="Hill Station",
                title="Temperature vs Air Quality — Higher Elevation = Better Living",
                color_continuous_scale="Viridis",
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, width="stretch")
