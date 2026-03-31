DATA_FILES = {
    "Water Transport": "data/Water Transport.csv",
    "Air Transport": "data/Air Transport.csv",
    "Financial": "data/Financial.csv",
}

HIGH_FREQUENCY_SECTOR_INDICATORS = {
    "Water Transport": {
        "Daily Port Calls (Arrivals)": [
            "Port Calls: Arrivals",
            # "Port Calls: Departures",
        ],
        "Tanker Monthly Arrivals (No. of Vessels)": [
            "Tanker Arrivals: Unit: Above 75 Gross Tonnage: Oil Tanker",
            "Tanker Arrivals: Unit: Above 75 Gross Tonnage: Chemical Tanker",
            "Tanker Arrivals: Unit: Above 75 Gross Tonnage: LNG and LPG Tanker",
        ],
        "Tanker Monthly Arrivals (Tonnage)": [
            "Tanker Arrivals: GT: Above 75 Gross Tonnage: Oil Tanker",
            "Tanker Arrivals: GT: Above 75 Gross Tonnage: Chemical Tanker",
            "Tanker Arrivals: GT: Above 75 Gross Tonnage: LNG and LPG Tanker",
        ],
        "Monthly Sea Cargo Handled": [
            "Sea Cargo Handled",
        ],
    },
    "Air Transport": {
        "Monthly Flight Movements": [
            "Changi Airport: No. of Flight ",
        ],
        "Monthly Passenger Movements": [
            "Changi Airport: Passenger Movements"
        ],
        "Monthly Air Freight": [
            "Changi Airport: Air Freight Movements"
        ]
    },
    "Financial": {
        "SGX Daily Turnover": [
            "SGX: Turnover: Shares: Total"
        ],
        "Forex Monthly Turnover": [
            "Foreign Exchange Market: SGD: Total Turnover"
        ],
        "Daily Domestic Interest Rates": [
            "Domestic Interest Rates: SORA: 3 Month Compounded",
            "Treasury Bond: MAS: Yield: 2 Years",
            "Treasury Bond: MAS: Yield: 10 Years"
        ]
    },
}
