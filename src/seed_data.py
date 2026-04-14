"""
Seed data for 20 major Indian cities.

Data is based on publicly available estimates from census records,
IPCC climate projections, real estate market reports, and
government infrastructure data. Values are approximate and
intended for analytical modeling, not precise investment decisions.

Sources referenced:
- Census of India 2011
- India Meteorological Department (IMD)
- IPCC AR6 South Asia regional data
- National Real Estate Development Council (NAREDCO)
- Smart Cities Mission data
"""

from src.models import (
    CityProfile, GeographicalProfile, ClimateData,
    LandPriceData, PopulationData, InfrastructureScore,
)


def get_all_cities():
    """Return a list of CityProfile objects for 20 major Indian cities."""
    cities = [
        # --- TIER 1 METROS ---
        CityProfile(
            name="Mumbai",
            state="Maharashtra",
            tier=1,
            geo=GeographicalProfile(
                latitude=19.076, longitude=72.877, elevation_m=14,
                coastal=True, river_proximity=False, seismic_zone=3,
                flood_risk="high", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=27.2, avg_rainfall_mm=2167, humidity_pct=75,
                air_quality_index=155, extreme_heat_days=5,
                cyclone_risk="medium",
                projected_temp_rise_2050=1.6, projected_temp_rise_2070=2.4,
                projected_rainfall_change_2050_pct=8.0,
                projected_rainfall_change_2070_pct=14.0,
                projected_aqi_2050=175, projected_aqi_2070=190,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=12000, avg_price_per_sqft_2020=18000,
                avg_price_per_sqft_2025=25000, cagr_2015_2025=7.6,
                projected_price_2030=35000, projected_price_2040=55000,
                projected_price_2050=80000, projected_price_2070=140000,
            ),
            population=PopulationData(
                population_2011=12442373, population_2020=20670000,
                population_2025=22100000, growth_rate_pct=1.1,
                projected_2030=23300000, projected_2040=25200000,
                projected_2050=26800000, projected_2070=28500000,
                density_per_sqkm=20634,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.5, education_score=8.0,
                transport_score=7.5, water_supply_score=5.5,
                green_cover_pct=13.0,
            ),
        ),

        CityProfile(
            name="Delhi",
            state="Delhi",
            tier=1,
            geo=GeographicalProfile(
                latitude=28.644, longitude=77.216, elevation_m=216,
                coastal=False, river_proximity=True, seismic_zone=4,
                flood_risk="medium", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=25.0, avg_rainfall_mm=797, humidity_pct=56,
                air_quality_index=260, extreme_heat_days=30,
                cyclone_risk="none",
                projected_temp_rise_2050=2.0, projected_temp_rise_2070=3.1,
                projected_rainfall_change_2050_pct=-5.0,
                projected_rainfall_change_2070_pct=-8.0,
                projected_aqi_2050=290, projected_aqi_2070=310,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=10000, avg_price_per_sqft_2020=14000,
                avg_price_per_sqft_2025=20000, cagr_2015_2025=7.2,
                projected_price_2030=27000, projected_price_2040=45000,
                projected_price_2050=68000, projected_price_2070=120000,
            ),
            population=PopulationData(
                population_2011=11034555, population_2020=20000000,
                population_2025=22000000, growth_rate_pct=1.4,
                projected_2030=24000000, projected_2040=27500000,
                projected_2050=30000000, projected_2070=33000000,
                density_per_sqkm=11320,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.0, education_score=8.5,
                transport_score=8.0, water_supply_score=5.0,
                green_cover_pct=11.0,
            ),
        ),

        CityProfile(
            name="Bengaluru",
            state="Karnataka",
            tier=1,
            geo=GeographicalProfile(
                latitude=12.971, longitude=77.594, elevation_m=920,
                coastal=False, river_proximity=False, seismic_zone=2,
                flood_risk="medium", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=24.0, avg_rainfall_mm=970, humidity_pct=65,
                air_quality_index=95, extreme_heat_days=3,
                cyclone_risk="none",
                projected_temp_rise_2050=1.3, projected_temp_rise_2070=2.0,
                projected_rainfall_change_2050_pct=-3.0,
                projected_rainfall_change_2070_pct=-6.0,
                projected_aqi_2050=125, projected_aqi_2070=150,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=5000, avg_price_per_sqft_2020=7500,
                avg_price_per_sqft_2025=11000, cagr_2015_2025=8.2,
                projected_price_2030=16000, projected_price_2040=30000,
                projected_price_2050=52000, projected_price_2070=95000,
            ),
            population=PopulationData(
                population_2011=8425970, population_2020=12700000,
                population_2025=14200000, growth_rate_pct=2.5,
                projected_2030=16200000, projected_2040=20000000,
                projected_2050=23500000, projected_2070=27000000,
                density_per_sqkm=4381,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.0, education_score=8.5,
                transport_score=6.0, water_supply_score=4.5,
                green_cover_pct=18.0,
            ),
        ),

        CityProfile(
            name="Chennai",
            state="Tamil Nadu",
            tier=1,
            geo=GeographicalProfile(
                latitude=13.083, longitude=80.270, elevation_m=6,
                coastal=True, river_proximity=True, seismic_zone=3,
                flood_risk="high", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=28.6, avg_rainfall_mm=1400, humidity_pct=72,
                air_quality_index=110, extreme_heat_days=15,
                cyclone_risk="high",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.3,
                projected_rainfall_change_2050_pct=10.0,
                projected_rainfall_change_2070_pct=18.0,
                projected_aqi_2050=140, projected_aqi_2070=165,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=4500, avg_price_per_sqft_2020=6500,
                avg_price_per_sqft_2025=9500, cagr_2015_2025=7.8,
                projected_price_2030=13500, projected_price_2040=24000,
                projected_price_2050=40000, projected_price_2070=75000,
            ),
            population=PopulationData(
                population_2011=4681087, population_2020=10900000,
                population_2025=12000000, growth_rate_pct=1.8,
                projected_2030=13200000, projected_2040=15500000,
                projected_2050=17500000, projected_2070=20000000,
                density_per_sqkm=26903,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.5, education_score=8.0,
                transport_score=6.5, water_supply_score=4.0,
                green_cover_pct=9.0,
            ),
        ),

        CityProfile(
            name="Hyderabad",
            state="Telangana",
            tier=1,
            geo=GeographicalProfile(
                latitude=17.385, longitude=78.486, elevation_m=542,
                coastal=False, river_proximity=True, seismic_zone=2,
                flood_risk="medium", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=26.7, avg_rainfall_mm=812, humidity_pct=58,
                air_quality_index=105, extreme_heat_days=20,
                cyclone_risk="low",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.2,
                projected_rainfall_change_2050_pct=-2.0,
                projected_rainfall_change_2070_pct=-5.0,
                projected_aqi_2050=135, projected_aqi_2070=160,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=3800, avg_price_per_sqft_2020=5800,
                avg_price_per_sqft_2025=9000, cagr_2015_2025=9.0,
                projected_price_2030=14000, projected_price_2040=28000,
                projected_price_2050=50000, projected_price_2070=100000,
            ),
            population=PopulationData(
                population_2011=6809970, population_2020=10000000,
                population_2025=11500000, growth_rate_pct=2.8,
                projected_2030=13500000, projected_2040=17000000,
                projected_2050=20500000, projected_2070=24000000,
                density_per_sqkm=18480,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=7.5, education_score=7.5,
                transport_score=7.0, water_supply_score=5.5,
                green_cover_pct=15.0,
            ),
        ),

        CityProfile(
            name="Kolkata",
            state="West Bengal",
            tier=1,
            geo=GeographicalProfile(
                latitude=22.572, longitude=88.363, elevation_m=11,
                coastal=False, river_proximity=True, seismic_zone=3,
                flood_risk="high", terrain_type="delta",
            ),
            climate=ClimateData(
                avg_temp_c=26.8, avg_rainfall_mm=1582, humidity_pct=78,
                air_quality_index=170, extreme_heat_days=12,
                cyclone_risk="high",
                projected_temp_rise_2050=1.6, projected_temp_rise_2070=2.5,
                projected_rainfall_change_2050_pct=7.0,
                projected_rainfall_change_2070_pct=12.0,
                projected_aqi_2050=200, projected_aqi_2070=225,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=3500, avg_price_per_sqft_2020=4800,
                avg_price_per_sqft_2025=6500, cagr_2015_2025=6.4,
                projected_price_2030=8800, projected_price_2040=14000,
                projected_price_2050=22000, projected_price_2070=40000,
            ),
            population=PopulationData(
                population_2011=4486679, population_2020=14800000,
                population_2025=15500000, growth_rate_pct=0.8,
                projected_2030=16000000, projected_2040=16800000,
                projected_2050=17200000, projected_2070=17500000,
                density_per_sqkm=24252,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=False,
                healthcare_score=7.0, education_score=7.5,
                transport_score=6.5, water_supply_score=5.0,
                green_cover_pct=8.0,
            ),
        ),

        CityProfile(
            name="Pune",
            state="Maharashtra",
            tier=1,
            geo=GeographicalProfile(
                latitude=18.520, longitude=73.856, elevation_m=560,
                coastal=False, river_proximity=True, seismic_zone=3,
                flood_risk="medium", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=25.0, avg_rainfall_mm=722, humidity_pct=55,
                air_quality_index=90, extreme_heat_days=8,
                cyclone_risk="none",
                projected_temp_rise_2050=1.2, projected_temp_rise_2070=1.8,
                projected_rainfall_change_2050_pct=-2.0,
                projected_rainfall_change_2070_pct=-4.0,
                projected_aqi_2050=115, projected_aqi_2070=135,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=4200, avg_price_per_sqft_2020=6200,
                avg_price_per_sqft_2025=8500, cagr_2015_2025=7.3,
                projected_price_2030=12000, projected_price_2040=21000,
                projected_price_2050=35000, projected_price_2070=65000,
            ),
            population=PopulationData(
                population_2011=3124458, population_2020=7400000,
                population_2025=8500000, growth_rate_pct=2.2,
                projected_2030=9600000, projected_2040=11500000,
                projected_2050=13500000, projected_2070=16000000,
                density_per_sqkm=5600,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.0, education_score=8.5,
                transport_score=6.5, water_supply_score=6.0,
                green_cover_pct=22.0,
            ),
        ),

        CityProfile(
            name="Ahmedabad",
            state="Gujarat",
            tier=1,
            geo=GeographicalProfile(
                latitude=23.022, longitude=72.571, elevation_m=53,
                coastal=False, river_proximity=True, seismic_zone=3,
                flood_risk="medium", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=27.0, avg_rainfall_mm=782, humidity_pct=52,
                air_quality_index=145, extreme_heat_days=35,
                cyclone_risk="low",
                projected_temp_rise_2050=1.8, projected_temp_rise_2070=2.8,
                projected_rainfall_change_2050_pct=-4.0,
                projected_rainfall_change_2070_pct=-7.0,
                projected_aqi_2050=170, projected_aqi_2070=195,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=2800, avg_price_per_sqft_2020=4000,
                avg_price_per_sqft_2025=5800, cagr_2015_2025=7.6,
                projected_price_2030=8200, projected_price_2040=15000,
                projected_price_2050=26000, projected_price_2070=50000,
            ),
            population=PopulationData(
                population_2011=5570585, population_2020=8000000,
                population_2025=8800000, growth_rate_pct=1.5,
                projected_2030=9500000, projected_2040=11000000,
                projected_2050=12500000, projected_2070=14000000,
                density_per_sqkm=12000,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=False,
                healthcare_score=7.0, education_score=7.0,
                transport_score=7.0, water_supply_score=5.5,
                green_cover_pct=10.0,
            ),
        ),

        # --- TIER 2 CITIES ---

        CityProfile(
            name="Coimbatore",
            state="Tamil Nadu",
            tier=2,
            geo=GeographicalProfile(
                latitude=11.016, longitude=76.955, elevation_m=411,
                coastal=False, river_proximity=True, seismic_zone=2,
                flood_risk="low", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=25.1, avg_rainfall_mm=640, humidity_pct=58,
                air_quality_index=65, extreme_heat_days=5,
                cyclone_risk="none",
                projected_temp_rise_2050=1.1, projected_temp_rise_2070=1.7,
                projected_rainfall_change_2050_pct=-2.0,
                projected_rainfall_change_2070_pct=-4.0,
                projected_aqi_2050=80, projected_aqi_2070=95,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=2200, avg_price_per_sqft_2020=3200,
                avg_price_per_sqft_2025=4800, cagr_2015_2025=8.1,
                projected_price_2030=7200, projected_price_2040=14500,
                projected_price_2050=28000, projected_price_2070=60000,
            ),
            population=PopulationData(
                population_2011=1061447, population_2020=2200000,
                population_2025=2600000, growth_rate_pct=2.1,
                projected_2030=2900000, projected_2040=3500000,
                projected_2050=4100000, projected_2070=5000000,
                density_per_sqkm=2400,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=True, it_hub=True,
                healthcare_score=7.5, education_score=7.5,
                transport_score=5.5, water_supply_score=6.5,
                green_cover_pct=25.0,
            ),
        ),

        CityProfile(
            name="Jaipur",
            state="Rajasthan",
            tier=2,
            geo=GeographicalProfile(
                latitude=26.912, longitude=75.787, elevation_m=431,
                coastal=False, river_proximity=False, seismic_zone=2,
                flood_risk="low", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=25.8, avg_rainfall_mm=600, humidity_pct=42,
                air_quality_index=135, extreme_heat_days=40,
                cyclone_risk="none",
                projected_temp_rise_2050=2.0, projected_temp_rise_2070=3.0,
                projected_rainfall_change_2050_pct=-6.0,
                projected_rainfall_change_2070_pct=-10.0,
                projected_aqi_2050=165, projected_aqi_2070=190,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=2500, avg_price_per_sqft_2020=3500,
                avg_price_per_sqft_2025=5000, cagr_2015_2025=7.2,
                projected_price_2030=7200, projected_price_2040=13000,
                projected_price_2050=24000, projected_price_2070=48000,
            ),
            population=PopulationData(
                population_2011=3073350, population_2020=4100000,
                population_2025=4600000, growth_rate_pct=1.8,
                projected_2030=5100000, projected_2040=6000000,
                projected_2050=7000000, projected_2070=8500000,
                density_per_sqkm=6300,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=False,
                healthcare_score=6.5, education_score=6.5,
                transport_score=6.0, water_supply_score=4.0,
                green_cover_pct=8.0,
            ),
        ),

        CityProfile(
            name="Lucknow",
            state="Uttar Pradesh",
            tier=2,
            geo=GeographicalProfile(
                latitude=26.846, longitude=80.946, elevation_m=123,
                coastal=False, river_proximity=True, seismic_zone=3,
                flood_risk="medium", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=25.5, avg_rainfall_mm=960, humidity_pct=60,
                air_quality_index=190, extreme_heat_days=28,
                cyclone_risk="none",
                projected_temp_rise_2050=1.8, projected_temp_rise_2070=2.7,
                projected_rainfall_change_2050_pct=-3.0,
                projected_rainfall_change_2070_pct=-6.0,
                projected_aqi_2050=220, projected_aqi_2070=250,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=2000, avg_price_per_sqft_2020=3000,
                avg_price_per_sqft_2025=4500, cagr_2015_2025=8.4,
                projected_price_2030=6800, projected_price_2040=14000,
                projected_price_2050=27000, projected_price_2070=55000,
            ),
            population=PopulationData(
                population_2011=2817105, population_2020=3800000,
                population_2025=4200000, growth_rate_pct=1.6,
                projected_2030=4700000, projected_2040=5600000,
                projected_2050=6500000, projected_2070=8000000,
                density_per_sqkm=4100,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=False, it_hub=False,
                healthcare_score=6.5, education_score=7.0,
                transport_score=5.5, water_supply_score=5.0,
                green_cover_pct=12.0,
            ),
        ),

        CityProfile(
            name="Chandigarh",
            state="Chandigarh",
            tier=2,
            geo=GeographicalProfile(
                latitude=30.733, longitude=76.779, elevation_m=321,
                coastal=False, river_proximity=False, seismic_zone=4,
                flood_risk="low", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=23.5, avg_rainfall_mm=1100, humidity_pct=55,
                air_quality_index=105, extreme_heat_days=15,
                cyclone_risk="none",
                projected_temp_rise_2050=1.4, projected_temp_rise_2070=2.1,
                projected_rainfall_change_2050_pct=-2.0,
                projected_rainfall_change_2070_pct=-4.0,
                projected_aqi_2050=130, projected_aqi_2070=155,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=5500, avg_price_per_sqft_2020=7500,
                avg_price_per_sqft_2025=10000, cagr_2015_2025=6.2,
                projected_price_2030=13500, projected_price_2040=22000,
                projected_price_2050=35000, projected_price_2070=60000,
            ),
            population=PopulationData(
                population_2011=1055450, population_2020=1200000,
                population_2025=1350000, growth_rate_pct=1.2,
                projected_2030=1440000, projected_2040=1600000,
                projected_2050=1750000, projected_2070=2000000,
                density_per_sqkm=9258,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=True, it_hub=True,
                healthcare_score=8.0, education_score=8.5,
                transport_score=7.5, water_supply_score=7.0,
                green_cover_pct=35.0,
            ),
        ),

        CityProfile(
            name="Kochi",
            state="Kerala",
            tier=2,
            geo=GeographicalProfile(
                latitude=9.931, longitude=76.267, elevation_m=0,
                coastal=True, river_proximity=True, seismic_zone=3,
                flood_risk="high", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=27.0, avg_rainfall_mm=3005, humidity_pct=80,
                air_quality_index=55, extreme_heat_days=2,
                cyclone_risk="low",
                projected_temp_rise_2050=1.2, projected_temp_rise_2070=1.8,
                projected_rainfall_change_2050_pct=8.0,
                projected_rainfall_change_2070_pct=14.0,
                projected_aqi_2050=70, projected_aqi_2070=85,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=3500, avg_price_per_sqft_2020=4800,
                avg_price_per_sqft_2025=6500, cagr_2015_2025=6.4,
                projected_price_2030=9000, projected_price_2040=15000,
                projected_price_2050=24000, projected_price_2070=45000,
            ),
            population=PopulationData(
                population_2011=601574, population_2020=2100000,
                population_2025=2400000, growth_rate_pct=1.5,
                projected_2030=2600000, projected_2040=3000000,
                projected_2050=3400000, projected_2070=4000000,
                density_per_sqkm=6300,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=True,
                healthcare_score=8.0, education_score=7.5,
                transport_score=6.0, water_supply_score=6.5,
                green_cover_pct=30.0,
            ),
        ),

        CityProfile(
            name="Indore",
            state="Madhya Pradesh",
            tier=2,
            geo=GeographicalProfile(
                latitude=22.719, longitude=75.857, elevation_m=553,
                coastal=False, river_proximity=True, seismic_zone=2,
                flood_risk="low", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=24.5, avg_rainfall_mm=940, humidity_pct=50,
                air_quality_index=80, extreme_heat_days=18,
                cyclone_risk="none",
                projected_temp_rise_2050=1.3, projected_temp_rise_2070=2.0,
                projected_rainfall_change_2050_pct=-2.0,
                projected_rainfall_change_2070_pct=-4.0,
                projected_aqi_2050=100, projected_aqi_2070=120,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1800, avg_price_per_sqft_2020=2800,
                avg_price_per_sqft_2025=4200, cagr_2015_2025=8.8,
                projected_price_2030=6500, projected_price_2040=14000,
                projected_price_2050=28000, projected_price_2070=62000,
            ),
            population=PopulationData(
                population_2011=1964086, population_2020=2800000,
                population_2025=3200000, growth_rate_pct=2.0,
                projected_2030=3600000, projected_2040=4300000,
                projected_2050=5100000, projected_2070=6500000,
                density_per_sqkm=3500,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=False, it_hub=False,
                healthcare_score=7.0, education_score=7.0,
                transport_score=6.5, water_supply_score=6.0,
                green_cover_pct=14.0,
            ),
        ),

        CityProfile(
            name="Thiruvananthapuram",
            state="Kerala",
            tier=2,
            geo=GeographicalProfile(
                latitude=8.524, longitude=76.936, elevation_m=10,
                coastal=True, river_proximity=False, seismic_zone=3,
                flood_risk="medium", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=27.0, avg_rainfall_mm=1827, humidity_pct=78,
                air_quality_index=45, extreme_heat_days=2,
                cyclone_risk="low",
                projected_temp_rise_2050=1.1, projected_temp_rise_2070=1.7,
                projected_rainfall_change_2050_pct=6.0,
                projected_rainfall_change_2070_pct=10.0,
                projected_aqi_2050=55, projected_aqi_2070=65,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=3000, avg_price_per_sqft_2020=4200,
                avg_price_per_sqft_2025=5800, cagr_2015_2025=6.8,
                projected_price_2030=8000, projected_price_2040=14000,
                projected_price_2050=23000, projected_price_2070=42000,
            ),
            population=PopulationData(
                population_2011=752490, population_2020=1670000,
                population_2025=1850000, growth_rate_pct=1.0,
                projected_2030=1960000, projected_2040=2100000,
                projected_2050=2250000, projected_2070=2500000,
                density_per_sqkm=5100,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=True, it_hub=True,
                healthcare_score=8.5, education_score=8.5,
                transport_score=5.5, water_supply_score=7.0,
                green_cover_pct=40.0,
            ),
        ),

        CityProfile(
            name="Visakhapatnam",
            state="Andhra Pradesh",
            tier=2,
            geo=GeographicalProfile(
                latitude=17.686, longitude=83.218, elevation_m=14,
                coastal=True, river_proximity=False, seismic_zone=2,
                flood_risk="medium", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=27.5, avg_rainfall_mm=1118, humidity_pct=72,
                air_quality_index=75, extreme_heat_days=10,
                cyclone_risk="high",
                projected_temp_rise_2050=1.4, projected_temp_rise_2070=2.1,
                projected_rainfall_change_2050_pct=7.0,
                projected_rainfall_change_2070_pct=12.0,
                projected_aqi_2050=95, projected_aqi_2070=115,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=2200, avg_price_per_sqft_2020=3200,
                avg_price_per_sqft_2025=5000, cagr_2015_2025=8.6,
                projected_price_2030=7500, projected_price_2040=15000,
                projected_price_2050=30000, projected_price_2070=65000,
            ),
            population=PopulationData(
                population_2011=1730320, population_2020=2200000,
                population_2025=2500000, growth_rate_pct=2.0,
                projected_2030=2800000, projected_2040=3400000,
                projected_2050=4000000, projected_2070=5200000,
                density_per_sqkm=3100,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=True, it_hub=True,
                healthcare_score=6.5, education_score=6.5,
                transport_score=5.5, water_supply_score=5.5,
                green_cover_pct=20.0,
            ),
        ),

        # --- TIER 3 EMERGING CITIES ---

        CityProfile(
            name="Mysuru",
            state="Karnataka",
            tier=3,
            geo=GeographicalProfile(
                latitude=12.295, longitude=76.639, elevation_m=770,
                coastal=False, river_proximity=True, seismic_zone=2,
                flood_risk="low", terrain_type="plateau",
            ),
            climate=ClimateData(
                avg_temp_c=23.8, avg_rainfall_mm=785, humidity_pct=60,
                air_quality_index=50, extreme_heat_days=2,
                cyclone_risk="none",
                projected_temp_rise_2050=1.0, projected_temp_rise_2070=1.6,
                projected_rainfall_change_2050_pct=-1.5,
                projected_rainfall_change_2070_pct=-3.0,
                projected_aqi_2050=60, projected_aqi_2070=72,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1500, avg_price_per_sqft_2020=2200,
                avg_price_per_sqft_2025=3500, cagr_2015_2025=8.8,
                projected_price_2030=5500, projected_price_2040=12000,
                projected_price_2050=25000, projected_price_2070=58000,
            ),
            population=PopulationData(
                population_2011=920550, population_2020=1200000,
                population_2025=1350000, growth_rate_pct=1.8,
                projected_2030=1500000, projected_2040=1800000,
                projected_2050=2100000, projected_2070=2700000,
                density_per_sqkm=2100,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=False, it_hub=True,
                healthcare_score=7.0, education_score=7.5,
                transport_score=5.0, water_supply_score=7.0,
                green_cover_pct=32.0,
            ),
        ),

        CityProfile(
            name="Vadodara",
            state="Gujarat",
            tier=3,
            geo=GeographicalProfile(
                latitude=22.307, longitude=73.181, elevation_m=39,
                coastal=False, river_proximity=True, seismic_zone=3,
                flood_risk="medium", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=27.0, avg_rainfall_mm=920, humidity_pct=55,
                air_quality_index=100, extreme_heat_days=22,
                cyclone_risk="low",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.3,
                projected_rainfall_change_2050_pct=-3.0,
                projected_rainfall_change_2070_pct=-5.0,
                projected_aqi_2050=125, projected_aqi_2070=148,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1600, avg_price_per_sqft_2020=2400,
                avg_price_per_sqft_2025=3800, cagr_2015_2025=9.0,
                projected_price_2030=6000, projected_price_2040=13000,
                projected_price_2050=27000, projected_price_2070=60000,
            ),
            population=PopulationData(
                population_2011=1670806, population_2020=2200000,
                population_2025=2500000, growth_rate_pct=1.6,
                projected_2030=2800000, projected_2040=3300000,
                projected_2050=3800000, projected_2070=4600000,
                density_per_sqkm=3200,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=False, it_hub=False,
                healthcare_score=6.5, education_score=7.0,
                transport_score=5.5, water_supply_score=5.5,
                green_cover_pct=15.0,
            ),
        ),

        CityProfile(
            name="Bhubaneswar",
            state="Odisha",
            tier=3,
            geo=GeographicalProfile(
                latitude=20.296, longitude=85.824, elevation_m=45,
                coastal=False, river_proximity=False, seismic_zone=3,
                flood_risk="medium", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=27.4, avg_rainfall_mm=1502, humidity_pct=72,
                air_quality_index=85, extreme_heat_days=15,
                cyclone_risk="high",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.2,
                projected_rainfall_change_2050_pct=5.0,
                projected_rainfall_change_2070_pct=9.0,
                projected_aqi_2050=105, projected_aqi_2070=125,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1500, avg_price_per_sqft_2020=2300,
                avg_price_per_sqft_2025=3800, cagr_2015_2025=9.7,
                projected_price_2030=6200, projected_price_2040=14000,
                projected_price_2050=30000, projected_price_2070=70000,
            ),
            population=PopulationData(
                population_2011=837737, population_2020=1100000,
                population_2025=1300000, growth_rate_pct=2.5,
                projected_2030=1500000, projected_2040=1900000,
                projected_2050=2400000, projected_2070=3200000,
                density_per_sqkm=2800,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=False, it_hub=True,
                healthcare_score=6.5, education_score=6.5,
                transport_score=5.0, water_supply_score=5.5,
                green_cover_pct=18.0,
            ),
        ),

        CityProfile(
            name="Surat",
            state="Gujarat",
            tier=2,
            geo=GeographicalProfile(
                latitude=21.170, longitude=72.831, elevation_m=13,
                coastal=True, river_proximity=True, seismic_zone=3,
                flood_risk="high", terrain_type="plain",
            ),
            climate=ClimateData(
                avg_temp_c=27.3, avg_rainfall_mm=1143, humidity_pct=68,
                air_quality_index=95, extreme_heat_days=18,
                cyclone_risk="medium",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.3,
                projected_rainfall_change_2050_pct=6.0,
                projected_rainfall_change_2070_pct=10.0,
                projected_aqi_2050=120, projected_aqi_2070=145,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=1800, avg_price_per_sqft_2020=2800,
                avg_price_per_sqft_2025=4500, cagr_2015_2025=9.6,
                projected_price_2030=7200, projected_price_2040=16000,
                projected_price_2050=35000, projected_price_2070=85000,
            ),
            population=PopulationData(
                population_2011=4467000, population_2020=5800000,
                population_2025=6700000, growth_rate_pct=3.2,
                projected_2030=7800000, projected_2040=9500000,
                projected_2050=11000000, projected_2070=13500000,
                density_per_sqkm=5600,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=True, airport_international=True, it_hub=False,
                healthcare_score=6.0, education_score=5.5,
                transport_score=6.5, water_supply_score=5.0,
                green_cover_pct=8.0,
            ),
        ),

        # ── Union Territories & Additional Cities ──

        # Pondicherry (Puducherry) — coastal UT, French Quarter, tourism-driven
        CityProfile(
            name="Pondicherry", state="Puducherry", tier=3,
            geo=GeographicalProfile(
                latitude=11.934, longitude=79.830, elevation_m=4,
                coastal=True, river_proximity=False, seismic_zone=2,
                flood_risk="medium", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=28.5, avg_rainfall_mm=1280, humidity_pct=72,
                air_quality_index=45, extreme_heat_days=15,
                cyclone_risk="medium",
                projected_temp_rise_2050=1.6, projected_temp_rise_2070=2.5,
                projected_rainfall_change_2050_pct=5.0,
                projected_rainfall_change_2070_pct=8.0,
                projected_aqi_2050=60, projected_aqi_2070=75,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=2500, avg_price_per_sqft_2020=3800,
                avg_price_per_sqft_2025=5500, cagr_2015_2025=8.2,
                projected_price_2030=8200, projected_price_2040=16000,
                projected_price_2050=30000, projected_price_2070=65000,
            ),
            population=PopulationData(
                population_2011=244377, population_2020=310000,
                population_2025=350000, growth_rate_pct=1.5,
                projected_2030=380000, projected_2040=430000,
                projected_2050=480000, projected_2070=550000,
                density_per_sqkm=3400,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=False, it_hub=False,
                healthcare_score=6.5, education_score=7.0,
                transport_score=4.5, water_supply_score=5.5,
                green_cover_pct=22.0,
            ),
        ),

        # Goa (Panaji) — coastal state, tourism + IT emerging
        CityProfile(
            name="Panaji", state="Goa", tier=3,
            geo=GeographicalProfile(
                latitude=15.498, longitude=73.827, elevation_m=7,
                coastal=True, river_proximity=True, seismic_zone=3,
                flood_risk="medium", terrain_type="coastal",
            ),
            climate=ClimateData(
                avg_temp_c=27.5, avg_rainfall_mm=2932, humidity_pct=75,
                air_quality_index=38, extreme_heat_days=8,
                cyclone_risk="low",
                projected_temp_rise_2050=1.4, projected_temp_rise_2070=2.2,
                projected_rainfall_change_2050_pct=6.0,
                projected_rainfall_change_2070_pct=10.0,
                projected_aqi_2050=52, projected_aqi_2070=65,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=4000, avg_price_per_sqft_2020=6500,
                avg_price_per_sqft_2025=9500, cagr_2015_2025=9.0,
                projected_price_2030=14500, projected_price_2040=28000,
                projected_price_2050=52000, projected_price_2070=110000,
            ),
            population=PopulationData(
                population_2011=114405, population_2020=130000,
                population_2025=145000, growth_rate_pct=1.2,
                projected_2030=155000, projected_2040=170000,
                projected_2050=185000, projected_2070=200000,
                density_per_sqkm=2800,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=True, it_hub=False,
                healthcare_score=6.0, education_score=5.5,
                transport_score=5.0, water_supply_score=6.0,
                green_cover_pct=35.0,
            ),
        ),

        # Dehradun — hill capital of Uttarakhand, education hub
        CityProfile(
            name="Dehradun", state="Uttarakhand", tier=3,
            geo=GeographicalProfile(
                latitude=30.317, longitude=78.032, elevation_m=640,
                coastal=False, river_proximity=True, seismic_zone=4,
                flood_risk="medium", terrain_type="hilly",
            ),
            climate=ClimateData(
                avg_temp_c=21.5, avg_rainfall_mm=2073, humidity_pct=62,
                air_quality_index=72, extreme_heat_days=5,
                cyclone_risk="none",
                projected_temp_rise_2050=1.5, projected_temp_rise_2070=2.4,
                projected_rainfall_change_2050_pct=-3.0,
                projected_rainfall_change_2070_pct=-5.0,
                projected_aqi_2050=90, projected_aqi_2070=110,
            ),
            land_price=LandPriceData(
                avg_price_per_sqft_2015=2200, avg_price_per_sqft_2020=3500,
                avg_price_per_sqft_2025=5000, cagr_2015_2025=8.6,
                projected_price_2030=7500, projected_price_2040=15000,
                projected_price_2050=28000, projected_price_2070=58000,
            ),
            population=PopulationData(
                population_2011=578420, population_2020=720000,
                population_2025=820000, growth_rate_pct=2.0,
                projected_2030=920000, projected_2040=1100000,
                projected_2050=1300000, projected_2070=1600000,
                density_per_sqkm=3100,
            ),
            infrastructure=InfrastructureScore(
                metro_rail=False, airport_international=False, it_hub=False,
                healthcare_score=6.5, education_score=8.0,
                transport_score=4.0, water_supply_score=7.0,
                green_cover_pct=32.0,
            ),
        ),
    ]

    return cities
