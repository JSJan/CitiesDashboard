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
from src.climate_analysis import generate_climate_report, climate_risk_score
from src.land_price_analysis import generate_land_report, generate_price_timeline, monte_carlo_price_simulation
from src.population_analysis import generate_population_report, generate_population_timeline, estimate_carrying_capacity
from src.scoring_engine import generate_master_ranking, get_top_cities_to_buy, compute_all_scores
from src.chennai_area_analysis import generate_area_ranking, generate_zone_summary, get_top_areas_to_buy


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

cities = load_cities()
areas = load_chennai_areas()

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
        "Investment Calculator",
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

    tab1, tab2, tab3 = st.tabs(["Zone Summary", "Area Ranking", "Buy Recommendations"])

    with tab1:
        zone_df = generate_zone_summary(areas)
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
        zone_names = sorted(set(a.zone for a in areas))
        zone_filter = st.multiselect("Filter by Zone", zone_names, default=zone_names)
        filtered_areas = [a for a in areas if a.zone in zone_filter]

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
        buy_df = get_top_areas_to_buy(areas, top_n=15)
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
