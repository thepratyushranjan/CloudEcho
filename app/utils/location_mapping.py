# -*- coding: utf-8 -*-

from typing import List, Optional



COMMON_COUNTRY_MAP = {
    "India": {
        "AWS": [
            "Mumbai",
            "Hyderabad"
        ],
        "GCP": [
            "Mumbai",
            "Delhi"
        ],
        "Azure": [
            "Central India",
            "South India",
            "West India "
        ]
    },

     "USA": {
        "AWS": [
            "N.Virginia",
            "Ohio",
            "Oregon",
            "N.California"
        ],
        "GCP": [
            "Council Bluffs",
            "Iowa",
            "Moncks Corner",
            "South Carolina"
            "Ashburn",
            "Northern Virginia",
            "Columbus",
            "Ohio",
            "Dallas",
            "Texas",
            "The Dalles",
            "Oregon",
            "Los Angeles",
            "California",
            "Salt Lake City",
            "Utah",
            "Las Vegas",
            "Nevada",

        ],
        "Azure": [
            "West US ",
            "East US 2",
            "East US ",
            "West US 2",
            "West Central US",
            "West US 3",
            "Central US",
            "South Central US",
            "North Central US",
            
        ]
    },

    "Australia": {
        "AWS": [
            "Sydney",
            "Melbourne",
        ],
        "GCP": [
            "Melbourne",
            "Sydney"
        ],
        "Azure": [
            "Australia Central",
            "Australia East",
            "Australia Southeast"
        ]
    },

    "Norway": {
        "AWS": [],
        "GCP": [],
        "Azure": [
            "Norway East"
        ]
    },


    "Belgium": {
        "AWS": [],
        "GCP": [
            "Belgium",
            "St. Ghislain"
        ],
        "Azure": []
    },

    "Brazil": {
        "AWS": [
            "Sao Paulo"
        ],
        "GCP": [
            "Osasco (São Paulo)"
        ],
        "Azure": [
            "Brazil South"
        ]
    },

    "Canada": {
        "AWS": [
            "Central",
            "Calgary"
        ],
        "GCP": [
            "Toronto",
            "Montréal",
            "Québec",
            "Ontario"
        ],
        "Azure": [
            "Canada East",
            "Canada Central"
        ]
    },

    "Chile": {
        "AWS": [],
        "GCP": [
            "Santiago"
        ],
        "Azure": []
    },

    "Finland": {
        "AWS": [],
        "GCP": [
            "Finland",
            "Hamina"
        ],
        "Azure": []
    },

     "France": {
        "AWS": [
            "Paris"
        ],
        "GCP": [
            "Paris"
        ],
        "Azure": [
            "France Central"
        ]
    },

    "Germany": {
        "AWS": [
            "Frankfurt"
        ],
        "GCP": [
            "Berlin",
            "Frankfurt",
            "Germany"
        ],
        "Azure": [
            "Germany West Central"
        ]
    },

    "Hong Kong": {
        "AWS": [],
        "GCP": [
            "Hong Kong"
        ],
        "Azure": [
            "East Asia"
        ]
    },

    "Indonesia": {
        "AWS": [
            "Jakarta"
        ],
        "GCP": [
            "Jakarta"
        ],
        "Azure": [
            "ID Central"
        ]
    },

     "Ireland": {
        "AWS": [
            "Ireland"
        ],
        "GCP": [],
        "Azure": [
            "North Europe"
        ]
    },

    "Israel": {
        "AWS": [
            "Tel Aviv"
        ],
        "GCP": [
            "Tel Aviv"
        ],
        "Azure": [
            "Tel Aviv"
        ]
    },

    "Italy": {
        "AWS": [
            "Milan"
        ],
        "GCP": [
            "Milan",
            "Turin",
            "Italy"
        ],
        "Azure": [
            "IT North"
        ]
    },

    "Japan": {
        "AWS": [
            "Tokyo",
            "Osaka"
        ],
        "GCP": [
            "Osaka",
            "Tokyo"
        ],
        "Azure": [
            "Japan East",
            "Japan West"
        ]
    },

     "Malaysia": {
        "AWS": [],
        "GCP": [],
        "Azure": [
            "MY West"
        ]
    },

    "Mexico": {
        "AWS": [],
        "GCP": [
            "Mexico",
            "Queretaro"
        ],
        "Azure": []
    },

    "Netherlands": {
        "AWS": [],
        "GCP": [
            "Eemshaven"
        ],
        "Azure": [
            "West Europe"
        ]
    },

    "New Zealand": {
        "AWS": [],
        "GCP": [],
        "Azure": [
            "NZ North"
        ]
    },

    "Poland": {
        "AWS": [],
        "GCP": [
            "Warsaw"
        ],
        "Azure": [
            "Poland Central"
        ]
    },

    "Qatar": {
        "AWS": [],
        "GCP": [
            "Doha"
        ],
        "Azure": [
            "Qatar Central"
        ]
    },

    "Saudi Arabia": {
        "AWS": [],
        "GCP": [
            "Dammam","Saudi Arabia"
        ],
        "Azure": []
    },

    "Singapore": {
        "AWS": [
            "Singapore"
        ],
        "GCP": [
            "Jurong West"
        ], 
        "Azure": [
            "Southeast Asia"
        ]
    },

    "South Africa": {
        "AWS": [
            "Cape Town"
        ],
        "GCP": [
            "Johannesburg"
        ],
        "Azure": [
            "South Africa North"
        ]
    },

    "South Korea": {
        "AWS": [
            "Seoul"
        ],
        "GCP": [
            "Seoul"
        ],
        "Azure": [
            "Korea South ",
            "Korea Central"
        ]
    },

    "Spain": {
        "AWS": [
            "Spain"
        ],
        "GCP": [
            "Madrid"
        ],
        "Azure": [
            "ES Central"
        ]
    },

    "Sweden": {
        "AWS": [
            "Stockholm"
        ],
        "GCP": [
            "Stockholm"
        ],
        "Azure": [
            "Sweden Central"
        ]
    },

     "Switzerland": {
        "AWS": [
            "Zurich"
        ],
        "GCP": [
            "Zurich"
        ],
        "Azure": [
            "Switzerland North"
        ]
    },

    "Taiwan": {
        "AWS": [],
        "GCP": [
            "Taiwan",
            "Changhua County"
        ],
        "Azure": []
    },

    "United Arab Emirates": {
        "AWS": [
            "UAE",
            "Bahrain"
        ],
        "GCP": [],
        "Azure": [
            "UAE North"
        ]
    },

    "United Kingdom": {
        "AWS": [
            "London"
        ],
        "GCP": [
            "London","England"
        ],
        "Azure": [
            "UK West",
            "UK South"
        ]
    },
}




def expand_common_locations(
    requested: List[str],
    clouds: Optional[List[str]]
) -> List[str]:
    expanded: List[str] = []
    canonical = {country.lower(): country for country in COMMON_COUNTRY_MAP}

    for loc in requested:
        key = loc.strip().lower()
        if key in canonical:
            per_cloud = COMMON_COUNTRY_MAP[canonical[key]]
            targets = clouds if clouds else per_cloud.keys()
            for provider in targets:
                expanded.extend(per_cloud.get(provider, []))
        else:
            expanded.append(loc)

    return expanded 

# AWS Region With Country
AWS_REGION_TO_COUNTRY = {
    "us-east-1": "USA",
    "us-east-2": "USA",
    "us-west-1": "USA",
    "us-west-2": "USA",
    "af-south-1": "South Africa",
    "ap-east-1": "Hong Kong",
    "ap-south-2": "India",
    "ap-southeast-3": "Indonesia",
    "ap-southeast-5": "Malaysia",
    "ap-southeast-4": "Australia",
    "ap-south-1": "India",
    "ap-northeast-3": "Japan",
    "ap-northeast-2": "South Korea",
    "ap-southeast-1": "Singapore",
    "ap-southeast-2": "Australia",
    "ap-east-2": "Taiwan",
    "ap-southeast-7": "Thailand",
    "ap-northeast-1": "Japan",
    "ca-central-1": "Canada",
    "ca-west-1": "Canada",
    "eu-central-1": "Germany",
    "eu-west-1": "Ireland",
    "eu-west-2": "United Kingdom",
    "eu-south-1": "Italy",
    "eu-west-3": "France",
    "eu-south-2": "Spain",
    "eu-north-1": "Sweden",
    "eu-central-2": "Switzerland",
    "il-central-1": "Israel",
    "mx-central-1": "Mexico",
    "me-south-1": "Bahrain",
    "me-central-1": "United Arab Emirates",
    "sa-east-1": "Brazil",
    "us-gov-east-1": "USA",
    "us-gov-west-1": "USA"
}


def get_country_from_aws_region_code(region_code: str) -> Optional[str]:
    return AWS_REGION_TO_COUNTRY.get(region_code)