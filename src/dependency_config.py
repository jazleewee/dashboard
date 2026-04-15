"""
Dependency node configuration for the dashboard.

Preferred mapping approach:
- Put CEIC series ids directly in `series_ids`
- Put exact Google Sheets row-2 names in `google_sheet_series`

Keyword fields remain available as a fallback, but explicit mappings are preferred.
"""


def node(
    *,
    label: str,
    description: str,
    children: list[str] | None = None,
    series_ids: list[str] | None = None,
    google_sheet_series: list[str] | None = None,
    sheet_keywords: list[str] | None = None,
) -> dict:
    return {
        "label": label,
        "description": description,
        "children": children or [],
        "series_ids": series_ids or [],
        "google_sheet_series": google_sheet_series or [],
        "sheet_keywords": sheet_keywords or [],
    }


DEPENDENCY_NODES = {
    "crude_oil": node(
        label="Crude Oil",
        description="Primary oil price indicators and oil-linked product chains.",
        children=[
            "marine_fuel",
            "jet_fuel",
            "diesel_petrol",
            "lpg",
            "naphtha",
        ],
        series_ids=[
            "global_crude_oil",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "crude",
        ],
    ),
    "gas": node(
        label="Gas",
        description="Gas benchmarks and downstream gas-sensitive product chains.",
        children=[
            "ethane",
            "methane",
            "helium",
        ],
        series_ids=[
            "global_us_natural_gas",
            "global_germany_natural_gas",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "gas",
            "lng",
            "natural gas",
        ],
    ),
    "marine_fuel": node(
        label="Marine Fuel",
        description="Fuel inputs that feed shipping and bunkering activity.",
        children=[
            "water_transport",
            "wholesale_bunkering",
        ],
        google_sheet_series=["ClearLynx VLSFO Bunker Fuel Spot Price/Singapore",
        "Asia Fuel Oil 380cst FOB Singapore Cargo Spot"],
        sheet_keywords=[
            "marine fuel",
            "bunker",
            "fuel oil",
        ],
    ),
    "jet_fuel": node(
        label="Jet Fuel",
        description="Aviation fuel indicators and their transmission into air transport.",
        children=[
            "air_transport",
        ],
        google_sheet_series=["Jet Fuel Singapore FOB Cargoes vs Crude Oil Dated Brent FOB NWE",
        "Jet Fuel NWE FOB Barges",
        "PADD I Average Jet Fuel Spot Market Price Prompt"],
        sheet_keywords=[
            "jet fuel",
            "jet",
            "aviation fuel",
        ],
    ),
    "diesel_petrol": node(
        label="Diesel/Petrol",
        description="Road fuel indicators linked to land transport and mobility-sensitive sectors.",
        children=[
            "land_transport",
        ],
        google_sheet_series=["Gasoline Singapore 92 RON FOB Cargoes",
        "Gasoline Singapore 95 RON FOB Cargoes",
        "RBOB Regular Gasoline NY Buckeye Continuous MKTMID"],
        sheet_keywords=[
            "diesel",
            "gasoil",
            "petrol",
            "gasoline",
        ],
    ),
    "lpg": node(
        label="LPG",
        description="Liquefied petroleum gas indicators and related feedstock pressures.",
        children=[
            "olefins_aromatics",
        ],
        google_sheet_series=["North American Spot LPGs/NGLs Propane Price/Mont Belvieu LST",
        "North American Spot LPGs/NGLs Normal Butane Price/Mont Belvieu LST",
        "North American Spot LPGs/NGLs Purity Ethane Price/Mont Belvieu non-LST",
        "Bloomberg Arab Gulf LPG Propane Monthly Posted Price",
        "Bloomberg Arab Gulf LPG Butane Monthly Posted Price"],
        sheet_keywords=[
            "lpg",
            "propane",
            "butane",
        ],
    ),
    "naphtha": node(
        label="Naphtha",
        description="Naphtha benchmarks feeding petrochemicals and broader chemical production.",
        children=[
            "olefins_aromatics",
            "petrochemicals",
            "basic_chemicals",
        ],
        series_ids=[
            "global_japan_naphtha",
            "global_france_naphtha",
        ],
        google_sheet_series=["Naphtha Japan CIF Cargoes",
        "Naphtha Singapore FOB Cargoes",
        "GX Naphtha NWE CIF Cargoes Prompt",
        ""],
        sheet_keywords=[
            "naphtha",
            "naptha",
        ],
    ),
    "ethane": node(
        label="Ethane",
        description="Gas-derived feedstock linked to basic chemicals and petrochemicals.",
        children=[
            "olefins_aromatics",
            "basic_chemicals",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "ethane",
        ],
    ),
    "methane": node(
        label="Methane",
        description="Gas-related indicators with transmission into fertilisers and utilities.",
        children=[
            "fertilisers",
            "gas_electricity",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "methane",
        ],
    ),
    "helium": node(
        label="Helium",
        description="Specialty gas indicators relevant for semiconductor supply chains.",
        children=[
            "semiconductors",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "helium",
        ],
    ),
    "olefins_aromatics": node(
        label="Olefins & Aromatics",
        description="Intermediate petrochemical products such as propylene and ethylene.",
        children=[
            "other_derivatives",
            "petrochemicals",
            "basic_chemicals",
        ],
        google_sheet_series=["SE Asia Ethylene (Olefins) CFR Spot Price Weekly",
        "US Gulf Ethylene (Olefins) FD Spot Price Weekly",
        "NWE Ethylene CIF Price USD/MT Weekly",
        "NE Asia Ethylene (Olefins) CFR Spot Price Weekly",
        "China Chemicals SunSirs LLDPE Linear Low-Density Polyethylene",
        "China Chemicals SunSirs HDPE High Density Polyethylene",
        "China Chemicals SunSirs PET Polyethylene Terephthalate",
        "SE Asia Film-Grade Polyethylene (HDPE Polymers) CFR Spot Price Weekly",
        "SE Asia Film-Grade Polyethylene (LLDPE Polymers) CFR Spot Price Weekly"],
        sheet_keywords=[
            "olefin",
            "aromatic",
            "ethylene",
            "propylene",
        ],
    ),
    "other_derivatives": node(
        label="Derivative Products",
        description="Derived industrial products such as plastics, paints, and pharmaceuticals.",
        children=[
            "water_waste",
            "construction",
            "real_estate",
            "food_beverage",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "plastic",
            "paint",
            "pharma",
            "chemical",
        ],
    ),
    "fertilisers": node(
        label="Fertilisers",
        description="Fertiliser-related products and their downstream economic effects.",
        children=[],
        google_sheet_series=[],
        sheet_keywords=[
            "fertiliser",
            "fertilizer",
            "urea",
            "ammonia",
        ],
    ),
    "water_transport": node(
        label="Water Transport",
        description="Shipping activity and port-related indicators.",
        series_ids=[
            "sea_cargo_handled",
            "container_throughput",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "shipping",
            "container",
            "cargo",
            "bunker",
        ],
    ),
    "air_transport": node(
        label="Air Transport",
        description="Aviation activity indicators including flights, passengers, and freight.",
        series_ids=[
            "air_flight_movements",
            "air_passenger_movements",
            "air_freight_movements",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "air freight",
            "aviation",
            "jet",
            "passenger",
        ],
    ),
    "land_transport": node(
        label="Land Transport",
        description="Land mobility indicators and fuel-sensitive transport demand.",
        series_ids=[
            "visitor_arrival_land",
        ],
        google_sheet_series=[],
        sheet_keywords=[
            "diesel",
            "petrol",
            "vehicle",
            "land transport",
        ],
    ),
    "petrochemicals": node(
        label="Petrochemicals",
        description="Chemical feedstock-intensive sectors and associated prices.",
        google_sheet_series=[],
        sheet_keywords=[
            "petrochemical",
            "ethylene",
            "propylene",
            "polymer",
        ],
    ),
    "basic_chemicals": node(
        label="Basic Chemicals",
        description="Broad basic chemical production and input cost pressures.",
        google_sheet_series=[],
        sheet_keywords=[
            "chemical",
            "methanol",
            "ammonia",
            "caustic",
        ],
    ),
    "water_waste": node(
        label="Water & Waste",
        description="Utilities and waste-related sectors exposed to input cost changes.",
        google_sheet_series=[],
        sheet_keywords=[
            "water",
            "waste",
            "utility",
        ],
    ),
    "petroleum": node(
        label="Petroleum",
        description="Petroleum sector indicators and refining-related activity.",
        google_sheet_series=[],
        sheet_keywords=[
            "petroleum",
            "refinery",
            "refining",
        ],
    ),
    "gas_electricity": node(
        label="Gas & Electricity",
        description="Utility-facing gas and power indicators.",
        google_sheet_series=[],
        sheet_keywords=[
            "power",
            "electricity",
            "gas",
        ],
    ),
    "wholesale_bunkering": node(
        label="Wholesale: Bunkering",
        description="Wholesale activity directly tied to marine bunkering demand.",
        google_sheet_series=[],
        sheet_keywords=[
            "bunker",
            "marine fuel",
        ],
    ),
    "wholesale_ex_bunkering": node(
        label="Wholesale: ex Bunkering",
        description="Non-bunkering wholesale sectors indirectly exposed to disruptions.",
        google_sheet_series=[],
        sheet_keywords=[
            "wholesale",
        ],
    ),
    "construction": node(
        label="Construction",
        description="Construction sectors exposed to chemicals and derived products.",
        google_sheet_series=[],
        sheet_keywords=[
            "construction",
            "cement",
            "building",
        ],
    ),
    "real_estate": node(
        label="Real Estate",
        description="Indirect exposure through construction and utilities-related channels.",
        google_sheet_series=[],
        sheet_keywords=[
            "property",
            "real estate",
        ],
    ),
    "food_beverage": node(
        label="Food & Beverage",
        description="Food-related sectors affected through fertilisers and packaging chains.",
        google_sheet_series=[],
        series_ids=[
            "food_and_beverage_sales"
        ],
        sheet_keywords=[
            "food",
            "beverage",
            "packaging",
        ],
    ),
    "semiconductors": node(
        label="Semiconductors",
        description="Semiconductor exposure through specialty gases and industrial inputs.",
        google_sheet_series=[],
        sheet_keywords=[
            "semiconductor",
            "chip",
            "helium",
        ],
    ),
}


ROOT_NODES = [
    "crude_oil",
    "gas",
]
