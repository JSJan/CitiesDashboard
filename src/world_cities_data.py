"""
World Cities — Global benchmark dataset for cross-country comparison.
Covers 10 major world cities across different climate zones and economies.

Currency: All prices in USD/sqft for comparability.
"""

from src.models import (
    CityProfile, GeographicalProfile, ClimateData,
    LandPriceData, PopulationData, InfrastructureScore,
)


# USD to INR conversion rate (approximate, April 2026)
USD_TO_INR = 84.0


def get_world_cities():
    """Return world city profiles. Prices are in USD/sqft."""
    cities = [

        # ── Asia-Pacific ──

        CityProfile(
            name="Singapore", state="Singapore", tier=1,
            geo=GeographicalProfile(
                latitude=1.352, longitude=103.820, elevation_m=15,
                coastal=True, river_proximity=True, seismic_zone=1,
                flood_risk="low", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=27.5, avg_rainfall_mm=2340, humidity_pct=84,
                air_quality_index=25, extreme_heat_days=0,
                cyclone_risk="none",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.3,
                projected_rainfall_change_2050_pct=5.0,
                projected_rainfall_change_2070_pct=8.0,
                projected_aqi_2050=30, projected_aqi_2070=35,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1200, avg_price_per_sqft_2020=1500,
                avg_price_per_sqft_2025=1800, cagr_2015_2025=4.1,
                projected_price_2030=2200, projected_price_2040=3000,
                projected_price_2050=4000, projected_price_2070=6500,
            ),
            population=PopulationData(
                population_2011=5184000, population_2020=5686000,
                population_2025=5920000, growth_rate_pct=0.8,
                projected_2030=6100000, projected_2040=6400000,
                projected_2050=6600000, projected_2070=6800000,
                density_per_sqkm=8358,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=9.5, education_score=9.5,
                transport_score=9.5, water_supply_score=9.0,
                green_cover_pct=30.0,
            ),
        ),

        CityProfile(
            name="Dubai", state="UAE", tier=1,
            geo=GeographicalProfile(
                latitude=25.276, longitude=55.296, elevation_m=5,
                coastal=True, river_proximity=False, seismic_zone=1,
                flood_risk="low", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=27.2, avg_rainfall_mm=94, humidity_pct=56,
                air_quality_index=55, extreme_heat_days=90,
                cyclone_risk="none",
                projected_temp_rise_2050=1.8, projected_temp_rise_2070=2.8,
                projected_rainfall_change_2050_pct=-10.0,
                projected_rainfall_change_2070_pct=-15.0,
                projected_aqi_2050=65, projected_aqi_2070=80,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=450, avg_price_per_sqft_2020=380,
                avg_price_per_sqft_2025=550, cagr_2015_2025=2.0,
                projected_price_2030=650, projected_price_2040=850,
                projected_price_2050=1100, projected_price_2070=1800,
            ),
            population=PopulationData(
                population_2011=1800000, population_2020=3400000,
                population_2025=3800000, growth_rate_pct=3.5,
                projected_2030=4300000, projected_2040=5200000,
                projected_2050=6000000, projected_2070=7500000,
                density_per_sqkm=762,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.5, education_score=7.5,
                transport_score=9.0, water_supply_score=7.0,
                green_cover_pct=5.0,
            ),
        ),

        CityProfile(
            name="Tokyo", state="Japan", tier=1,
            geo=GeographicalProfile(
                latitude=35.682, longitude=139.759, elevation_m=40,
                coastal=True, river_proximity=True, seismic_zone=5,
                flood_risk="medium", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=16.3, avg_rainfall_mm=1530, humidity_pct=63,
                air_quality_index=30, extreme_heat_days=5,
                cyclone_risk="medium",
                projected_temp_rise_2050=1.3, projected_temp_rise_2070=2.0,
                projected_rainfall_change_2050_pct=3.0,
                projected_rainfall_change_2070_pct=5.0,
                projected_aqi_2050=35, projected_aqi_2070=38,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=950, avg_price_per_sqft_2020=1100,
                avg_price_per_sqft_2025=1250, cagr_2015_2025=2.8,
                projected_price_2030=1450, projected_price_2040=1900,
                projected_price_2050=2500, projected_price_2070=4000,
            ),
            population=PopulationData(
                population_2011=13185000, population_2020=13960000,
                population_2025=14000000, growth_rate_pct=0.1,
                projected_2030=13900000, projected_2040=13500000,
                projected_2050=13000000, projected_2070=12000000,
                density_per_sqkm=6363,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=9.5, education_score=9.5,
                transport_score=10.0, water_supply_score=9.5,
                green_cover_pct=20.0,
            ),
        ),

        # ── Europe ──

        CityProfile(
            name="London", state="UK", tier=1,
            geo=GeographicalProfile(
                latitude=51.507, longitude=-0.128, elevation_m=11,
                coastal=False, river_proximity=True, seismic_zone=1,
                flood_risk="medium", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=11.3, avg_rainfall_mm=602, humidity_pct=79,
                air_quality_index=40, extreme_heat_days=2,
                cyclone_risk="none",
                projected_temp_rise_2050=1.2, projected_temp_rise_2070=1.9,
                projected_rainfall_change_2050_pct=2.0,
                projected_rainfall_change_2070_pct=4.0,
                projected_aqi_2050=35, projected_aqi_2070=30,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1400, avg_price_per_sqft_2020=1300,
                avg_price_per_sqft_2025=1500, cagr_2015_2025=0.7,
                projected_price_2030=1650, projected_price_2040=2000,
                projected_price_2050=2500, projected_price_2070=3800,
            ),
            population=PopulationData(
                population_2011=8204000, population_2020=8982000,
                population_2025=9400000, growth_rate_pct=0.9,
                projected_2030=9800000, projected_2040=10300000,
                projected_2050=10700000, projected_2070=11200000,
                density_per_sqkm=5700,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.5, education_score=9.5,
                transport_score=9.0, water_supply_score=8.5,
                green_cover_pct=33.0,
            ),
        ),

        CityProfile(
            name="Berlin", state="Germany", tier=1,
            geo=GeographicalProfile(
                latitude=52.520, longitude=13.405, elevation_m=34,
                coastal=False, river_proximity=True, seismic_zone=1,
                flood_risk="low", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=10.4, avg_rainfall_mm=570, humidity_pct=72,
                air_quality_index=28, extreme_heat_days=3,
                cyclone_risk="none",
                projected_temp_rise_2050=1.4, projected_temp_rise_2070=2.2,
                projected_rainfall_change_2050_pct=-2.0,
                projected_rainfall_change_2070_pct=-4.0,
                projected_aqi_2050=25, projected_aqi_2070=22,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=350, avg_price_per_sqft_2020=550,
                avg_price_per_sqft_2025=650, cagr_2015_2025=6.4,
                projected_price_2030=850, projected_price_2040=1200,
                projected_price_2050=1700, projected_price_2070=3000,
            ),
            population=PopulationData(
                population_2011=3501872, population_2020=3664000,
                population_2025=3850000, growth_rate_pct=0.5,
                projected_2030=3950000, projected_2040=4050000,
                projected_2050=4100000, projected_2070=4100000,
                density_per_sqkm=4100,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=9.0, education_score=9.0,
                transport_score=9.5, water_supply_score=9.0,
                green_cover_pct=30.0,
            ),
        ),

        # ── Americas ──

        CityProfile(
            name="New York", state="USA", tier=1,
            geo=GeographicalProfile(
                latitude=40.713, longitude=-74.006, elevation_m=10,
                coastal=True, river_proximity=True, seismic_zone=2,
                flood_risk="medium", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=12.9, avg_rainfall_mm=1268, humidity_pct=63,
                air_quality_index=42, extreme_heat_days=10,
                cyclone_risk="medium",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.4,
                projected_rainfall_change_2050_pct=5.0,
                projected_rainfall_change_2070_pct=8.0,
                projected_aqi_2050=38, projected_aqi_2070=35,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1600, avg_price_per_sqft_2020=1400,
                avg_price_per_sqft_2025=1700, cagr_2015_2025=0.6,
                projected_price_2030=1900, projected_price_2040=2400,
                projected_price_2050=3000, projected_price_2070=4500,
            ),
            population=PopulationData(
                population_2011=8175000, population_2020=8336000,
                population_2025=8500000, growth_rate_pct=0.3,
                projected_2030=8600000, projected_2040=8700000,
                projected_2050=8700000, projected_2070=8600000,
                density_per_sqkm=10947,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.5, education_score=9.5,
                transport_score=8.5, water_supply_score=8.0,
                green_cover_pct=14.0,
            ),
        ),

        CityProfile(
            name="São Paulo", state="Brazil", tier=1,
            geo=GeographicalProfile(
                latitude=-23.550, longitude=-46.633, elevation_m=760,
                coastal=False, river_proximity=True, seismic_zone=1,
                flood_risk="high", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=19.3, avg_rainfall_mm=1454, humidity_pct=78,
                air_quality_index=50, extreme_heat_days=5,
                cyclone_risk="none",
                projected_temp_rise_2050=1.6, projected_temp_rise_2070=2.5,
                projected_rainfall_change_2050_pct=-5.0,
                projected_rainfall_change_2070_pct=-8.0,
                projected_aqi_2050=60, projected_aqi_2070=70,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=250, avg_price_per_sqft_2020=200,
                avg_price_per_sqft_2025=280, cagr_2015_2025=1.1,
                projected_price_2030=330, projected_price_2040=450,
                projected_price_2050=600, projected_price_2070=1000,
            ),
            population=PopulationData(
                population_2011=11253000, population_2020=12330000,
                population_2025=12800000, growth_rate_pct=0.6,
                projected_2030=13200000, projected_2040=13800000,
                projected_2050=14200000, projected_2070=14500000,
                density_per_sqkm=7398,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=7.0, education_score=7.5,
                transport_score=6.0, water_supply_score=6.5,
                green_cover_pct=18.0,
            ),
        ),

        # ── Africa & Middle East ──

        CityProfile(
            name="Cape Town", state="South Africa", tier=2,
            geo=GeographicalProfile(
                latitude=-33.925, longitude=18.424, elevation_m=0,
                coastal=True, river_proximity=False, seismic_zone=1,
                flood_risk="low", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=17.0, avg_rainfall_mm=515, humidity_pct=71,
                air_quality_index=30, extreme_heat_days=8,
                cyclone_risk="none",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.5,
                projected_rainfall_change_2050_pct=-12.0,
                projected_rainfall_change_2070_pct=-18.0,
                projected_aqi_2050=35, projected_aqi_2070=40,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=150, avg_price_per_sqft_2020=180,
                avg_price_per_sqft_2025=220, cagr_2015_2025=3.9,
                projected_price_2030=280, projected_price_2040=400,
                projected_price_2050=550, projected_price_2070=900,
            ),
            population=PopulationData(
                population_2011=3740000, population_2020=4618000,
                population_2025=5000000, growth_rate_pct=1.5,
                projected_2030=5400000, projected_2040=6100000,
                projected_2050=6700000, projected_2070=7500000,
                density_per_sqkm=1530,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=True, it_hub=True,
                healthcare_score=6.5, education_score=7.0,
                transport_score=5.5, water_supply_score=4.0,
                green_cover_pct=28.0,
            ),
        ),

        # ── Australia ──

        CityProfile(
            name="Sydney", state="Australia", tier=1,
            geo=GeographicalProfile(
                latitude=-33.869, longitude=151.209, elevation_m=58,
                coastal=True, river_proximity=True, seismic_zone=1,
                flood_risk="medium", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=18.4, avg_rainfall_mm=1215, humidity_pct=65,
                air_quality_index=22, extreme_heat_days=8,
                cyclone_risk="low",
                projected_temp_rise_2050=1.3, projected_temp_rise_2070=2.1,
                projected_rainfall_change_2050_pct=-5.0,
                projected_rainfall_change_2070_pct=-10.0,
                projected_aqi_2050=28, projected_aqi_2070=32,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=700, avg_price_per_sqft_2020=800,
                avg_price_per_sqft_2025=950, cagr_2015_2025=3.1,
                projected_price_2030=1100, projected_price_2040=1450,
                projected_price_2050=1900, projected_price_2070=3000,
            ),
            population=PopulationData(
                population_2011=4391000, population_2020=5312000,
                population_2025=5700000, growth_rate_pct=1.5,
                projected_2030=6100000, projected_2040=6800000,
                projected_2050=7400000, projected_2070=8200000,
                density_per_sqkm=430,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=9.0, education_score=9.0,
                transport_score=8.0, water_supply_score=7.5,
                green_cover_pct=25.0,
            ),
        ),

        CityProfile(
            name="Nairobi", state="Kenya", tier=2,
            geo=GeographicalProfile(
                latitude=-1.286, longitude=36.817, elevation_m=1795,
                coastal=False, river_proximity=True, seismic_zone=2,
                flood_risk="medium", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=19.0, avg_rainfall_mm=869, humidity_pct=60,
                air_quality_index=55, extreme_heat_days=0,
                cyclone_risk="none",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.4,
                projected_rainfall_change_2050_pct=5.0,
                projected_rainfall_change_2070_pct=8.0,
                projected_aqi_2050=70, projected_aqi_2070=85,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=80, avg_price_per_sqft_2020=110,
                avg_price_per_sqft_2025=150, cagr_2015_2025=6.5,
                projected_price_2030=210, projected_price_2040=350,
                projected_price_2050=550, projected_price_2070=1000,
            ),
            population=PopulationData(
                population_2011=3138000, population_2020=4397000,
                population_2025=5100000, growth_rate_pct=3.5,
                projected_2030=6000000, projected_2040=7800000,
                projected_2050=9500000, projected_2070=13000000,
                density_per_sqkm=6300,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=True, it_hub=True,
                healthcare_score=5.0, education_score=5.5,
                transport_score=4.0, water_supply_score=4.0,
                green_cover_pct=15.0,
            ),
        ),
    ]

    return cities
