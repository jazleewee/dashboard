DATA_FILES = {
    "Water Transport": "data/Water Transport.csv",
    "Air Transport": "data/Air Transport.csv",
    "Financial": "data/Financial.csv",
}

HIGH_FREQUENCY_SECTOR_INDICATORS = {
    "Water Transport": {
        "Tanker Arrivals": [
            "Tanker Arrivals: Unit: Above 75 Gross Tonnage: Oil Tanker",
            "Tanker Arrivals: Unit: Above 75 Gross Tonnage: Chemical Tanker",
            "Tanker Arrivals: Unit: Above 75 Gross Tonnage: LNG and LPG Tanker",
        ],
        "Tanker Arrivals GT": [
            "Tanker Arrivals: GT: Above 75 Gross Tonnage: Oil Tanker",
            "Tanker Arrivals: GT: Above 75 Gross Tonnage: Chemical Tanker",
            "Tanker Arrivals: GT: Above 75 Gross Tonnage: LNG and LPG Tanker",
        ],
        "Sea Cargo Handled": [
            "Sea Cargo Handled",
        ],
        "Port Calls": [
            "Port Calls: Arrivals",
            # "Port Calls: Departures",
        ],
    },
    "Air Transport": {
        "Flight Movements": [
            "Changi Airport: No. of Flight ",
        ],
        "Passenger Movements": [
            "Changi Airport: Passenger Movements"
        ],
        "Air Freight": [
            "Changi Airport: Air Freight Movements"
        ]
    },
    "Financial": {
        "SGX Turnover": [
            "SGX: Turnover: Shares: Total"
        ],
        "Forex Turnover": [
            "Foreign Exchange Market: SGD: Total Turnover"
        ],
        "Domestic Interest Rates": [
            "Domestic Interest Rates: SORA: 3 Month Compounded",
            "Treasury Bond: MAS: Yield: 2 Years",
            "Treasury Bond: MAS: Yield: 10 Years"
        ]
    },
}
