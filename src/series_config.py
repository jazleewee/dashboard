SERIES_REGISTRY = {
    "global_crude_oil": {
        "series_id": "global_crude_oil",
        "source": "ceic",
        "source_key": "42651501",
        "label": "Crude Oil",
        "unit": "USD/Barrel",
        "frequency": "",
    },
    "global_us_natural_gas": {
        "series_id": "global_us_natural_gas",
        "source": "ceic",
        "source_key": "40780401",
        "label": "US Natural Gas",
        "unit": "USD/MM BTU",
        "frequency": "",
    },
    "global_germany_natural_gas": {
        "series_id": "global_germany_natural_gas",
        "source": "ceic",
        "source_key": "449519797",
        "label": "Germany Natural Gas",
        "unit": "USD/MM BTU",
        "frequency": "",
    },
    "global_japan_naphtha": {
        "series_id": "global_japan_naphtha",
        "source": "ceic",
        "source_key": "161345001",
        "label": "Japan Naphtha",
        "unit": "USD/Barrel",
        "frequency": "",
    },
    "global_france_naphtha": {
        "series_id": "global_france_naphtha",
        "source": "ceic",
        "source_key": "352664901",
        "label": "France Naphtha",
        "unit": "USD/Ton",
        "frequency": "",
    },
    "sea_cargo_handled": {
        "series_id": "sea_cargo_handled",
        "source": "ceic",
        "source_key": "36680501",
        "label": "Sea Cargo Handled",
        "unit": "",
        "frequency": "",
    },
    "container_throughput": {
        "series_id": "container_throughput",
        "source": "ceic",
        "source_key": "36681201",
        "label": "Container Throughput",
        "unit": "",
        "frequency": "",
    },
    "air_flight_movements": {
        "series_id": "air_flight_movements",
        "source": "ceic",
        "source_key": "36670301",
        "label": "Flight Movements",
        "unit": "",
        "frequency": "",
    },
    "air_passenger_movements": {
        "series_id": "air_passenger_movements",
        "source": "ceic",
        "source_key": "241774802",
        "label": "Passenger Movements",
        "unit": "",
        "frequency": "",
    },
    "air_freight_movements": {
        "series_id": "air_freight_movements",
        "source": "ceic",
        "source_key": "241774902",
        "label": "Air Freight Movements",
        "unit": "",
        "frequency": "",
    },
    "financial_sgx_turnover": {
        "series_id": "financial_sgx_turnover",
        "source": "ceic",
        "source_key": "35960701",
        "label": "SGX Daily Turnover",
        "unit": "",
        "frequency": "",
    },
    "financial_forex_turnover": {
        "series_id": "financial_forex_turnover",
        "source": "ceic",
        "source_key": "471805317",
        "label": "Forex Monthly Turnover",
        "unit": "",
        "frequency": "",
    },
    "financial_sora_3m": {
        "series_id": "financial_sora_3m",
        "source": "ceic",
        "source_key": "468026967",
        "label": "SORA 3M Compounded",
        "unit": "",
        "frequency": "",
    },
    "financial_yield_2y": {
        "series_id": "financial_yield_2y",
        "source": "ceic",
        "source_key": "35945301",
        "label": "MAS Yield 2Y",
        "unit": "",
        "frequency": "",
    },
    "financial_yield_10y": {
        "series_id": "financial_yield_10y",
        "source": "ceic",
        "source_key": "35945601",
        "label": "MAS Yield 10Y",
        "unit": "",
        "frequency": "",
    },
    "visitor_arrival_land": {
        "series_id": "visitor_arrival_land",
        "source": "ceic",
        "source_key": "36588001",
        "label": "Visitor Arrivals by Land",
        "unit": "",
        "frequency": "",
    },
}


GLOBAL_PRICES = {
    "Upstream": {
        "Crude Oil": {
            "series_ids": ["global_crude_oil"],
        },
        "Natural Gas": {
            "series_ids": [
                "global_us_natural_gas",
                "global_germany_natural_gas",
            ],
        },
        "Naphtha": {
            "left_series_ids": ["global_japan_naphtha"],
            "right_series_ids": ["global_france_naphtha"],
        },
    },
}


SECTOR_SPECIFIC_INDICATORS = {
    "Water Transport": {
        "Monthly Sea Cargo Handled": [
            "sea_cargo_handled",
        ],
        "Monthly Container Throughput": [
            "container_throughput",
        ],
    },
    "Air Transport": {
        "Monthly Flight Movements": [
            "air_flight_movements",
        ],
        "Monthly Passenger Movements": [
            "air_passenger_movements",
        ],
        "Monthly Air Freight": [
            "air_freight_movements",
        ],
    },
    "Land Transport": {
        "Monthly Visitor Arrivals by Land": [
            "visitor_arrival_land",
        ],
    },
    "Financial": {
        "SGX Daily Turnover": [
            "financial_sgx_turnover",
        ],
        "Forex Monthly Turnover": [
            "financial_forex_turnover",
        ],
        "Daily Domestic Interest Rates": [
            "financial_sora_3m",
            "financial_yield_2y",
            "financial_yield_10y",
        ],
    },
}
