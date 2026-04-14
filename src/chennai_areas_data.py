"""
Chennai area and zone-level seed data.

Covers major areas across Chennai's zones based on CMDA (Chennai Metropolitan
Development Authority) zone classification. Data is based on publicly available
real estate market reports, CMDA planning documents, and infrastructure data.

Zones:
- North Chennai: Tondiarpet, Tiruvottiyur, Ennore, Madhavaram, Manali
- Central Chennai: T. Nagar, Mylapore, Anna Nagar, Egmore, Nungambakkam
- South Chennai: Adyar, Besant Nagar, Velachery, Tambaram, Medavakkam, Sholinganallur
- West Chennai: Porur, Ambattur, Avadi, Poonamallee, Mogappair
- IT Corridor (OMR): Perungudi, Thoraipakkam, Siruseri, Navalur, Kelambakkam
- ECR Belt: Thiruvanmiyur, Palavakkam, Neelankarai, Kovalam
"""

from src.area_models import AreaProfile, AreaLandPrice


def get_chennai_areas():
    """Return area-level profiles for Chennai."""
    areas = [
        # ==================== NORTH CHENNAI ====================
        AreaProfile(
            name="Tondiarpet", zone="North", city="Chennai",
            area_type="mixed", distance_from_center_km=5,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=True, flood_prone=True,
            green_cover_pct=4.0, current_aqi=135, water_supply_score=4.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3200, price_per_sqft_2020=4500,
                price_per_sqft_2025=6200, cagr_2015_2025=6.8,
                projected_2030=8500, projected_2040=14000,
                projected_2050=22000, projected_2070=42000,
            ),
            population_density_per_sqkm=42000,
        ),
        AreaProfile(
            name="Tiruvottiyur", zone="North", city="Chennai",
            area_type="industrial", distance_from_center_km=14,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=True, flood_prone=True,
            green_cover_pct=3.0, current_aqi=155, water_supply_score=3.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2200, price_per_sqft_2020=3000,
                price_per_sqft_2025=4200, cagr_2015_2025=6.7,
                projected_2030=5800, projected_2040=10000,
                projected_2050=16000, projected_2070=30000,
            ),
            population_density_per_sqkm=28000,
        ),
        AreaProfile(
            name="Ennore", zone="North", city="Chennai",
            area_type="industrial", distance_from_center_km=18,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=True, flood_prone=True,
            green_cover_pct=2.0, current_aqi=170, water_supply_score=3.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1500, price_per_sqft_2020=2200,
                price_per_sqft_2025=3200, cagr_2015_2025=7.9,
                projected_2030=4800, projected_2040=8500,
                projected_2050=14000, projected_2070=28000,
            ),
            population_density_per_sqkm=12000,
        ),
        AreaProfile(
            name="Madhavaram", zone="North", city="Chennai",
            area_type="residential", distance_from_center_km=12,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=8.0, current_aqi=120, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2800, price_per_sqft_2020=4000,
                price_per_sqft_2025=5800, cagr_2015_2025=7.6,
                projected_2030=8200, projected_2040=14500,
                projected_2050=24000, projected_2070=46000,
            ),
            population_density_per_sqkm=18000,
        ),
        AreaProfile(
            name="Manali", zone="North", city="Chennai",
            area_type="industrial", distance_from_center_km=16,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=2.0, current_aqi=185, water_supply_score=3.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1800, price_per_sqft_2020=2500,
                price_per_sqft_2025=3500, cagr_2015_2025=6.9,
                projected_2030=4800, projected_2040=8000,
                projected_2050=13000, projected_2070=25000,
            ),
            population_density_per_sqkm=9000,
        ),

        # ==================== CENTRAL CHENNAI ====================
        AreaProfile(
            name="T. Nagar", zone="Central", city="Chennai",
            area_type="commercial", distance_from_center_km=3,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=5.0, current_aqi=110, water_supply_score=7.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=10000, price_per_sqft_2020=14000,
                price_per_sqft_2025=18500, cagr_2015_2025=6.3,
                projected_2030=24000, projected_2040=38000,
                projected_2050=55000, projected_2070=95000,
            ),
            population_density_per_sqkm=45000,
        ),
        AreaProfile(
            name="Mylapore", zone="Central", city="Chennai",
            area_type="residential", distance_from_center_km=4,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=8.0, current_aqi=95, water_supply_score=7.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=9000, price_per_sqft_2020=12500,
                price_per_sqft_2025=17000, cagr_2015_2025=6.6,
                projected_2030=22500, projected_2040=36000,
                projected_2050=52000, projected_2070=90000,
            ),
            population_density_per_sqkm=35000,
        ),
        AreaProfile(
            name="Anna Nagar", zone="Central", city="Chennai",
            area_type="residential", distance_from_center_km=5,
            metro_connectivity=True, railway_station=False,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=12.0, current_aqi=100, water_supply_score=7.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=8500, price_per_sqft_2020=11500,
                price_per_sqft_2025=15500, cagr_2015_2025=6.2,
                projected_2030=20500, projected_2040=33000,
                projected_2050=48000, projected_2070=82000,
            ),
            population_density_per_sqkm=28000,
        ),
        AreaProfile(
            name="Egmore", zone="Central", city="Chennai",
            area_type="mixed", distance_from_center_km=2,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=6.0, current_aqi=115, water_supply_score=6.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=9500, price_per_sqft_2020=13000,
                price_per_sqft_2025=17500, cagr_2015_2025=6.3,
                projected_2030=23000, projected_2040=36000,
                projected_2050=52000, projected_2070=88000,
            ),
            population_density_per_sqkm=38000,
        ),
        AreaProfile(
            name="Nungambakkam", zone="Central", city="Chennai",
            area_type="commercial", distance_from_center_km=3,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=7.0, current_aqi=105, water_supply_score=7.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=12000, price_per_sqft_2020=16000,
                price_per_sqft_2025=22000, cagr_2015_2025=6.2,
                projected_2030=28000, projected_2040=44000,
                projected_2050=62000, projected_2070=105000,
            ),
            population_density_per_sqkm=32000,
        ),

        # ==================== SOUTH CHENNAI ====================
        AreaProfile(
            name="Adyar", zone="South", city="Chennai",
            area_type="residential", distance_from_center_km=8,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=True, flood_prone=True,
            green_cover_pct=15.0, current_aqi=80, water_supply_score=6.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=8000, price_per_sqft_2020=11000,
                price_per_sqft_2025=15000, cagr_2015_2025=6.5,
                projected_2030=20000, projected_2040=32000,
                projected_2050=48000, projected_2070=82000,
            ),
            population_density_per_sqkm=22000,
        ),
        AreaProfile(
            name="Besant Nagar", zone="South", city="Chennai",
            area_type="residential", distance_from_center_km=9,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=18.0, current_aqi=70, water_supply_score=7.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=9000, price_per_sqft_2020=12500,
                price_per_sqft_2025=17000, cagr_2015_2025=6.6,
                projected_2030=22000, projected_2040=35000,
                projected_2050=50000, projected_2070=85000,
            ),
            population_density_per_sqkm=18000,
        ),
        AreaProfile(
            name="Velachery", zone="South", city="Chennai",
            area_type="residential", distance_from_center_km=12,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=6.0, current_aqi=105, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=5500, price_per_sqft_2020=7500,
                price_per_sqft_2025=10500, cagr_2015_2025=6.7,
                projected_2030=14500, projected_2040=24000,
                projected_2050=36000, projected_2070=65000,
            ),
            population_density_per_sqkm=30000,
        ),
        AreaProfile(
            name="Tambaram", zone="South", city="Chennai",
            area_type="residential", distance_from_center_km=22,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=10.0, current_aqi=90, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3000, price_per_sqft_2020=4200,
                price_per_sqft_2025=6000, cagr_2015_2025=7.2,
                projected_2030=8500, projected_2040=15000,
                projected_2050=25000, projected_2070=48000,
            ),
            population_density_per_sqkm=14000,
        ),
        AreaProfile(
            name="Medavakkam", zone="South", city="Chennai",
            area_type="residential", distance_from_center_km=18,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=8.0, current_aqi=95, water_supply_score=4.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3200, price_per_sqft_2020=4500,
                price_per_sqft_2025=6500, cagr_2015_2025=7.4,
                projected_2030=9200, projected_2040=16000,
                projected_2050=27000, projected_2070=52000,
            ),
            population_density_per_sqkm=16000,
        ),
        AreaProfile(
            name="Sholinganallur", zone="South", city="Chennai",
            area_type="it_corridor", distance_from_center_km=20,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=True, flood_prone=True,
            green_cover_pct=7.0, current_aqi=85, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=4000, price_per_sqft_2020=6500,
                price_per_sqft_2025=10000, cagr_2015_2025=9.6,
                projected_2030=15500, projected_2040=30000,
                projected_2050=52000, projected_2070=100000,
            ),
            population_density_per_sqkm=12000,
        ),

        # ==================== WEST CHENNAI ====================
        AreaProfile(
            name="Porur", zone="West", city="Chennai",
            area_type="mixed", distance_from_center_km=14,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=6.0, current_aqi=100, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3800, price_per_sqft_2020=5500,
                price_per_sqft_2025=8000, cagr_2015_2025=7.7,
                projected_2030=11500, projected_2040=20000,
                projected_2050=34000, projected_2070=62000,
            ),
            population_density_per_sqkm=15000,
        ),
        AreaProfile(
            name="Ambattur", zone="West", city="Chennai",
            area_type="industrial", distance_from_center_km=13,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=5.0, current_aqi=120, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3500, price_per_sqft_2020=5000,
                price_per_sqft_2025=7200, cagr_2015_2025=7.5,
                projected_2030=10200, projected_2040=18000,
                projected_2050=30000, projected_2070=55000,
            ),
            population_density_per_sqkm=20000,
        ),
        AreaProfile(
            name="Avadi", zone="West", city="Chennai",
            area_type="residential", distance_from_center_km=21,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=10.0, current_aqi=105, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2200, price_per_sqft_2020=3200,
                price_per_sqft_2025=4800, cagr_2015_2025=8.1,
                projected_2030=7000, projected_2040=13000,
                projected_2050=22000, projected_2070=44000,
            ),
            population_density_per_sqkm=11000,
        ),
        AreaProfile(
            name="Poonamallee", zone="West", city="Chennai",
            area_type="residential", distance_from_center_km=24,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=14.0, current_aqi=90, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2000, price_per_sqft_2020=3000,
                price_per_sqft_2025=4500, cagr_2015_2025=8.4,
                projected_2030=6800, projected_2040=13000,
                projected_2050=23000, projected_2070=46000,
            ),
            population_density_per_sqkm=8000,
        ),
        AreaProfile(
            name="Mogappair", zone="West", city="Chennai",
            area_type="residential", distance_from_center_km=11,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=10.0, current_aqi=95, water_supply_score=6.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=4500, price_per_sqft_2020=6200,
                price_per_sqft_2025=8800, cagr_2015_2025=6.9,
                projected_2030=12000, projected_2040=20000,
                projected_2050=32000, projected_2070=58000,
            ),
            population_density_per_sqkm=22000,
        ),

        # ==================== IT CORRIDOR (OMR) ====================
        AreaProfile(
            name="Perungudi", zone="IT Corridor (OMR)", city="Chennai",
            area_type="it_corridor", distance_from_center_km=14,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=5.0, current_aqi=90, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=4200, price_per_sqft_2020=6500,
                price_per_sqft_2025=9800, cagr_2015_2025=8.8,
                projected_2030=15000, projected_2040=28000,
                projected_2050=48000, projected_2070=95000,
            ),
            population_density_per_sqkm=14000,
        ),
        AreaProfile(
            name="Thoraipakkam", zone="IT Corridor (OMR)", city="Chennai",
            area_type="it_corridor", distance_from_center_km=16,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=4.0, current_aqi=88, water_supply_score=4.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3800, price_per_sqft_2020=6000,
                price_per_sqft_2025=9200, cagr_2015_2025=9.2,
                projected_2030=14500, projected_2040=28000,
                projected_2050=48000, projected_2070=95000,
            ),
            population_density_per_sqkm=12000,
        ),
        AreaProfile(
            name="Siruseri", zone="IT Corridor (OMR)", city="Chennai",
            area_type="it_corridor", distance_from_center_km=25,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=False,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=12.0, current_aqi=65, water_supply_score=4.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2200, price_per_sqft_2020=3800,
                price_per_sqft_2025=6200, cagr_2015_2025=10.9,
                projected_2030=10500, projected_2040=22000,
                projected_2050=42000, projected_2070=90000,
            ),
            population_density_per_sqkm=5000,
        ),
        AreaProfile(
            name="Navalur", zone="IT Corridor (OMR)", city="Chennai",
            area_type="it_corridor", distance_from_center_km=28,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=False,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=15.0, current_aqi=60, water_supply_score=4.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1800, price_per_sqft_2020=3200,
                price_per_sqft_2025=5500, cagr_2015_2025=11.8,
                projected_2030=9500, projected_2040=22000,
                projected_2050=45000, projected_2070=100000,
            ),
            population_density_per_sqkm=3500,
        ),
        AreaProfile(
            name="Kelambakkam", zone="IT Corridor (OMR)", city="Chennai",
            area_type="it_corridor", distance_from_center_km=30,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=False,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=18.0, current_aqi=55, water_supply_score=3.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1500, price_per_sqft_2020=2800,
                price_per_sqft_2025=5000, cagr_2015_2025=12.8,
                projected_2030=9000, projected_2040=21000,
                projected_2050=44000, projected_2070=100000,
            ),
            population_density_per_sqkm=2800,
        ),

        # ==================== ECR BELT ====================
        AreaProfile(
            name="Thiruvanmiyur", zone="ECR Belt", city="Chennai",
            area_type="residential", distance_from_center_km=10,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=10.0, current_aqi=75, water_supply_score=6.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=7000, price_per_sqft_2020=9500,
                price_per_sqft_2025=13000, cagr_2015_2025=6.4,
                projected_2030=17500, projected_2040=28000,
                projected_2050=42000, projected_2070=75000,
            ),
            population_density_per_sqkm=20000,
        ),
        AreaProfile(
            name="Palavakkam", zone="ECR Belt", city="Chennai",
            area_type="residential", distance_from_center_km=13,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=12.0, current_aqi=65, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=5500, price_per_sqft_2020=7500,
                price_per_sqft_2025=10500, cagr_2015_2025=6.7,
                projected_2030=14500, projected_2040=24000,
                projected_2050=38000, projected_2070=68000,
            ),
            population_density_per_sqkm=15000,
        ),
        AreaProfile(
            name="Neelankarai", zone="ECR Belt", city="Chennai",
            area_type="residential", distance_from_center_km=16,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=False,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=16.0, current_aqi=55, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=4500, price_per_sqft_2020=6500,
                price_per_sqft_2025=9500, cagr_2015_2025=7.8,
                projected_2030=13500, projected_2040=24000,
                projected_2050=40000, projected_2070=72000,
            ),
            population_density_per_sqkm=8000,
        ),
        AreaProfile(
            name="Kovalam", zone="ECR Belt", city="Chennai",
            area_type="residential", distance_from_center_km=28,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=25.0, current_aqi=45, water_supply_score=4.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1800, price_per_sqft_2020=3000,
                price_per_sqft_2025=5200, cagr_2015_2025=11.2,
                projected_2030=9000, projected_2040=20000,
                projected_2050=40000, projected_2070=85000,
            ),
            population_density_per_sqkm=3000,
        ),

        # ── Additional Chennai Areas ──

        AreaProfile(
            name="Guindy", zone="Central", city="Chennai",
            area_type="mixed", distance_from_center_km=8,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=18.0, current_aqi=72, water_supply_score=7.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=6500, price_per_sqft_2020=8500,
                price_per_sqft_2025=11000, cagr_2015_2025=5.4,
                projected_2030=14000, projected_2040=22000,
                projected_2050=33000, projected_2070=55000,
            ),
            population_density_per_sqkm=14000,
        ),

        AreaProfile(
            name="Chromepet", zone="South", city="Chennai",
            area_type="residential", distance_from_center_km=18,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=10.0, current_aqi=80, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3200, price_per_sqft_2020=4200,
                price_per_sqft_2025=5800, cagr_2015_2025=6.1,
                projected_2030=8000, projected_2040=14000,
                projected_2050=25000, projected_2070=50000,
            ),
            population_density_per_sqkm=18000,
        ),

        AreaProfile(
            name="Pallavaram", zone="South", city="Chennai",
            area_type="mixed", distance_from_center_km=20,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=8.0, current_aqi=85, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2800, price_per_sqft_2020=3800,
                price_per_sqft_2025=5200, cagr_2015_2025=6.4,
                projected_2030=7500, projected_2040=13000,
                projected_2050=23000, projected_2070=45000,
            ),
            population_density_per_sqkm=15000,
        ),

        AreaProfile(
            name="Perambur", zone="North", city="Chennai",
            area_type="residential", distance_from_center_km=6,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=8.0, current_aqi=90, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=4000, price_per_sqft_2020=5200,
                price_per_sqft_2025=6800, cagr_2015_2025=5.4,
                projected_2030=9000, projected_2040=14000,
                projected_2050=22000, projected_2070=42000,
            ),
            population_density_per_sqkm=22000,
        ),

        AreaProfile(
            name="Thiruverkadu", zone="West", city="Chennai",
            area_type="residential", distance_from_center_km=16,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=15.0, current_aqi=70, water_supply_score=4.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1500, price_per_sqft_2020=2400,
                price_per_sqft_2025=3800, cagr_2015_2025=9.7,
                projected_2030=6000, projected_2040=13000,
                projected_2050=28000, projected_2070=65000,
            ),
            population_density_per_sqkm=8000,
        ),

        AreaProfile(
            name="Pallikaranai", zone="South", city="Chennai",
            area_type="mixed", distance_from_center_km=17,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=12.0, current_aqi=68, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2800, price_per_sqft_2020=4200,
                price_per_sqft_2025=6200, cagr_2015_2025=8.3,
                projected_2030=9000, projected_2040=17000,
                projected_2050=32000, projected_2070=68000,
            ),
            population_density_per_sqkm=12000,
        ),

        # ── Inner Chennai — Additional Areas ──

        AreaProfile(
            name="Ayanavaram", zone="North", city="Chennai",
            area_type="residential", distance_from_center_km=5,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=8.0, current_aqi=88, water_supply_score=6.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=4500, price_per_sqft_2020=5800,
                price_per_sqft_2025=7500, cagr_2015_2025=5.2,
                projected_2030=9500, projected_2040=15000,
                projected_2050=24000, projected_2070=45000,
            ),
            population_density_per_sqkm=25000,
        ),

        AreaProfile(
            name="Kolathur", zone="North", city="Chennai",
            area_type="residential", distance_from_center_km=10,
            metro_connectivity=True, railway_station=False,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=7.0, current_aqi=82, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3000, price_per_sqft_2020=4200,
                price_per_sqft_2025=6000, cagr_2015_2025=7.2,
                projected_2030=8500, projected_2040=15000,
                projected_2050=27000, projected_2070=55000,
            ),
            population_density_per_sqkm=18000,
        ),

        AreaProfile(
            name="Saligramam", zone="West", city="Chennai",
            area_type="mixed", distance_from_center_km=8,
            metro_connectivity=True, railway_station=True,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=10.0, current_aqi=75, water_supply_score=7.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=6000, price_per_sqft_2020=8000,
                price_per_sqft_2025=10500, cagr_2015_2025=5.8,
                projected_2030=13500, projected_2040=21000,
                projected_2050=32000, projected_2070=58000,
            ),
            population_density_per_sqkm=20000,
        ),

        AreaProfile(
            name="Arumbakkam", zone="Central", city="Chennai",
            area_type="residential", distance_from_center_km=7,
            metro_connectivity=True, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=9.0, current_aqi=78, water_supply_score=6.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=5500, price_per_sqft_2020=7200,
                price_per_sqft_2025=9500, cagr_2015_2025=5.6,
                projected_2030=12000, projected_2040=19000,
                projected_2050=30000, projected_2070=55000,
            ),
            population_density_per_sqkm=22000,
        ),

        AreaProfile(
            name="Gerukambakkam", zone="West", city="Chennai",
            area_type="residential", distance_from_center_km=15,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=False,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=18.0, current_aqi=62, water_supply_score=4.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1800, price_per_sqft_2020=2800,
                price_per_sqft_2025=4200, cagr_2015_2025=8.8,
                projected_2030=6500, projected_2040=13000,
                projected_2050=26000, projected_2070=62000,
            ),
            population_density_per_sqkm=6000,
        ),

        AreaProfile(
            name="Nolambur", zone="West", city="Chennai",
            area_type="residential", distance_from_center_km=12,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=12.0, current_aqi=68, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3200, price_per_sqft_2020=4500,
                price_per_sqft_2025=6500, cagr_2015_2025=7.3,
                projected_2030=9000, projected_2040=16000,
                projected_2050=28000, projected_2070=58000,
            ),
            population_density_per_sqkm=10000,
        ),

        # ── Chennai Outskirts ──

        AreaProfile(
            name="Oragadam", zone="Outskirts", city="Chennai",
            area_type="industrial", distance_from_center_km=45,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=True, hospital_proximity=False,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=25.0, current_aqi=50, water_supply_score=4.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=600, price_per_sqft_2020=1200,
                price_per_sqft_2025=2200, cagr_2015_2025=13.9,
                projected_2030=4000, projected_2040=10000,
                projected_2050=25000, projected_2070=70000,
            ),
            population_density_per_sqkm=1500,
        ),

        AreaProfile(
            name="Guduvanchery", zone="Outskirts", city="Chennai",
            area_type="residential", distance_from_center_km=35,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=20.0, current_aqi=55, water_supply_score=4.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=800, price_per_sqft_2020=1600,
                price_per_sqft_2025=2800, cagr_2015_2025=13.3,
                projected_2030=5000, projected_2040=12000,
                projected_2050=28000, projected_2070=72000,
            ),
            population_density_per_sqkm=3000,
        ),

        AreaProfile(
            name="Thirumazhisai", zone="Outskirts", city="Chennai",
            area_type="residential", distance_from_center_km=25,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=22.0, current_aqi=52, water_supply_score=4.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=700, price_per_sqft_2020=1400,
                price_per_sqft_2025=2500, cagr_2015_2025=13.6,
                projected_2030=4500, projected_2040=11000,
                projected_2050=26000, projected_2070=68000,
            ),
            population_density_per_sqkm=2500,
        ),

        AreaProfile(
            name="Red Hills", zone="Outskirts", city="Chennai",
            area_type="residential", distance_from_center_km=22,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=20.0, current_aqi=58, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=900, price_per_sqft_2020=1500,
                price_per_sqft_2025=2600, cagr_2015_2025=11.2,
                projected_2030=4200, projected_2040=10000,
                projected_2050=22000, projected_2070=55000,
            ),
            population_density_per_sqkm=4000,
        ),

        AreaProfile(
            name="Chengalpattu", zone="Outskirts", city="Chennai",
            area_type="mixed", distance_from_center_km=55,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=28.0, current_aqi=48, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=500, price_per_sqft_2020=1000,
                price_per_sqft_2025=1800, cagr_2015_2025=13.7,
                projected_2030=3200, projected_2040=8500,
                projected_2050=22000, projected_2070=65000,
            ),
            population_density_per_sqkm=2000,
        ),

        # ── Pondicherry Areas ──

        AreaProfile(
            name="White Town", zone="Central", city="Pondicherry",
            area_type="mixed", distance_from_center_km=0,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=25.0, current_aqi=35, water_supply_score=6.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=4500, price_per_sqft_2020=7000,
                price_per_sqft_2025=10000, cagr_2015_2025=8.3,
                projected_2030=14500, projected_2040=27000,
                projected_2050=48000, projected_2070=95000,
            ),
            population_density_per_sqkm=5000,
        ),

        AreaProfile(
            name="Auroville", zone="West", city="Pondicherry",
            area_type="residential", distance_from_center_km=10,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=False, flood_prone=False,
            green_cover_pct=55.0, current_aqi=28, water_supply_score=5.0,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1200, price_per_sqft_2020=2000,
                price_per_sqft_2025=3200, cagr_2015_2025=10.3,
                projected_2030=5200, projected_2040=12000,
                projected_2050=25000, projected_2070=60000,
            ),
            population_density_per_sqkm=500,
        ),

        AreaProfile(
            name="Lawspet", zone="North", city="Pondicherry",
            area_type="residential", distance_from_center_km=4,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=18.0, current_aqi=42, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=2000, price_per_sqft_2020=3000,
                price_per_sqft_2025=4500, cagr_2015_2025=8.4,
                projected_2030=6500, projected_2040=12000,
                projected_2050=22000, projected_2070=48000,
            ),
            population_density_per_sqkm=8000,
        ),

        AreaProfile(
            name="ECR Pondicherry", zone="South", city="Pondicherry",
            area_type="residential", distance_from_center_km=6,
            metro_connectivity=False, railway_station=False,
            it_park_proximity=False, hospital_proximity=False,
            coastal_proximity=True, flood_prone=False,
            green_cover_pct=30.0, current_aqi=32, water_supply_score=4.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=1800, price_per_sqft_2020=2800,
                price_per_sqft_2025=4200, cagr_2015_2025=8.8,
                projected_2030=6500, projected_2040=13000,
                projected_2050=26000, projected_2070=58000,
            ),
            population_density_per_sqkm=3500,
        ),

        AreaProfile(
            name="Mudaliarpet", zone="Central", city="Pondicherry",
            area_type="commercial", distance_from_center_km=2,
            metro_connectivity=False, railway_station=True,
            it_park_proximity=False, hospital_proximity=True,
            coastal_proximity=False, flood_prone=True,
            green_cover_pct=12.0, current_aqi=48, water_supply_score=5.5,
            land_price=AreaLandPrice(
                price_per_sqft_2015=3000, price_per_sqft_2020=4500,
                price_per_sqft_2025=6500, cagr_2015_2025=8.0,
                projected_2030=9500, projected_2040=18000,
                projected_2050=33000, projected_2070=70000,
            ),
            population_density_per_sqkm=12000,
        ),
    ]

    return areas
