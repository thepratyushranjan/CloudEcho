# -*- coding: utf-8 -*-

from typing import List, Optional

# COMMON_LOCATION_MAP = {

#     "North America": {
#     "AWS": [
#       "US East (N. Virginia)",
#       "US East (Ohio)",
#       "US West (Oregon)",
#       "US West (N. California)",
#       "Canada (Central)"
#     ],
#     "GCP": [
#       "Iowa",
#       "Northern Virginia",
#       "South Carolina",
#       "Las Vegas",
#       "Toronto",
#       "Salt Lake City",
#       "Columbus",
#       "Los Angeles",
#       "Montréal",
#       "Dallas",
#       "Mexico",
#       "Oregon"
#     ],
#     "Azure": [
#       "US East",
#       "US East 2",
#       "US Central",
#       "US North Central",
#       "US South Central",
#       "US South Central 2",
#       "US West",
#       "US West 2",
#       "US West 3",
#       "US West Central",
#       "CA Central",
#       "CA East",
#       "MX Central"
#     ]
#   },

#   "South America": {
#     "AWS": [
#       "South America (São Paulo)"
#     ],
#     "GCP": [
#       "São Paulo",
#       "Santiago"
#     ],
#     "Azure": [
#       "BR South",
#       "BR Southeast",
#       "CL Central"
#     ]
#   },

#   "Europe": {
#     "AWS": [
#       "EU (Stockholm)",
#       "EU (Paris)",
#       "EU (Frankfurt)",
#       "EU (Ireland)",
#       "EU (London)"
#     ],
#     "GCP": [
#       "Netherlands",
#       "Belgium",
#       "Finland",
#       "Zurich",
#       "Madrid",
#       "Warsaw",
#       "Milan",
#       "Berlin",
#       "Turin",
#       "Frankfurt",
#       "London",
#       "Paris",
#       "Stockholm"
#     ],
#     "Azure": [
#       "EU North",
#       "EU West",
#       "FR Central",
#       "FR South",
#       "DE North",
#       "DE West Central",
#       "AT East",
#       "ES Central",
#       "IT North",
#       "PL Central",
#       "SE Central",
#       "SE South",
#       "UK South",
#       "UK West",
#       "CH North",
#       "CH West"
#     ]
#   },

#   "Asia Pacific": {
#     "AWS": [
#       "Asia Pacific (Tokyo)",
#       "Asia Pacific (Sydney)",
#       "Asia Pacific (Singapore)",
#       "Asia Pacific (Mumbai)",
#       "Asia Pacific (Osaka)",
#       "Asia Pacific (Seoul)"
#     ],
#     "GCP": [
#       "Taiwan",
#       "Melbourne",
#       "Delhi",
#       "Hong Kong",
#       "Jakarta",
#       "Mumbai",
#       "Mumbai",
#       "Sydney",
#       "Seoul",
#       "Osaka",
#     ],
#     "Azure": [
#       "AP East",
#       "AP Southeast",
#       "AU East",
#       "AU Southeast",
#       "ID Central",
#       "IN Central",
#       "IN Central Jio",
#       "IN South",
#       "IN West",
#       "IN West Jio",
#       "JA East",
#       "JA West",
#       "KR Central",
#       "KR South",
#       "MY West",
#       "NZ North"
#     ]
#   },

#   "Middle East & Africa": {
#     "AWS": [],
#     "GCP": [
#       "Dammam",
#       "Tel Aviv",
#       "Doha",
#       "Johannesburg"
#     ],
#     "Azure": [
#       "AE Central",
#       "AE North",
#       "QA Central",
#       "IL Central",
#       "ZA North",
#       "ZA West"
#     ]
#   },

#   #add more locations as needed
# }

COMMON_COUNTRY_MAP = {
    "India": {
        "AWS": [
            "Asia Pacific (Mumbai)",
            "Asia Pacific (Hyderabad)"
        ],
        "GCP": [
            "Mumbai",
            "Delhi"
        ],
        "Azure": [
            "IN Central",
            "IN Central Jio",
            "IN South",
            "IN West",
            "IN West Jio"
        ]
    },

     "USA": {
        "AWS": [
            "US East (N. Virginia)",
            "US East (Ohio)",
            "US West (Oregon)",
            "US West (N. California)"
        ],
        "GCP": [
            "Iowa",
            "Northern Virginia",
            "South Carolina",
            "Las Vegas",
            "Salt Lake City",
            "Columbus",
            "Los Angeles",
            "Dallas",
            "Oregon"
        ],
        "Azure": [
            "US East",
            "US East 2",
            "US Central",
            "US North Central",
            "US South Central",
            "US South Central 2",
            "US West",
            "US West 2",
            "US West 3",
            "US West Central"
        ]
    },

    "Australia": {
        "AWS": [
            "Asia Pacific (Sydney)"
        ],
        "GCP": [
            "Melbourne",
            "Sydney"
        ],
        "Azure": [
            "AU East",
            "AU Southeast"
        ]
    },

    "Austria": {
        "AWS": [],
        "GCP": [],
        "Azure": [
            "AT East"
        ]
    },

    "Belgium": {
        "AWS": [],
        "GCP": [
            "Belgium"
        ],
        "Azure": []
    },

    "Brazil": {
        "AWS": [
            "South America (São Paulo)"
        ],
        "GCP": [
            "São Paulo"
        ],
        "Azure": [
            "BR South",
            "BR Southeast"
        ]
    },

    "Canada": {
        "AWS": [
            "Canada (Central)"
        ],
        "GCP": [
            "Toronto",
            "Montréal"
        ],
        "Azure": [
            "CA Central",
            "CA East"
        ]
    },

    "Chile": {
        "AWS": [],
        "GCP": [
            "Santiago"
        ],
        "Azure": [
            "CL Central"
        ]
    },

    "Finland": {
        "AWS": [],
        "GCP": [
            "Finland"
        ],
        "Azure": []
    },

     "France": {
        "AWS": [
            "EU (Paris)"
        ],
        "GCP": [
            "Paris"
        ],
        "Azure": [
            "FR Central",
            "FR South"
        ]
    },

    "Germany": {
        "AWS": [
            "EU (Frankfurt)"
        ],
        "GCP": [
            "Berlin",
            "Frankfurt"
        ],
        "Azure": [
            "DE North",
            "DE West Central"
        ]
    },

    "Hong Kong": {
        "AWS": [],
        "GCP": [
            "Hong Kong"
        ],
        "Azure": []
    },

    "Indonesia": {
        "AWS": [],
        "GCP": [
            "Jakarta"
        ],
        "Azure": [
            "ID Central"
        ]
    },

     "Ireland": {
        "AWS": [
            "EU (Ireland)"
        ],
        "GCP": [],
        "Azure": [
            "EU North"
        ]
    },

    "Israel": {
        "AWS": [],
        "GCP": [
            "Tel Aviv"
        ],
        "Azure": [
            "IL Central"
        ]
    },

    "Italy": {
        "AWS": [],
        "GCP": [
            "Milan",
            "Turin"
        ],
        "Azure": [
            "IT North"
        ]
    },

    "Japan": {
        "AWS": [
            "Asia Pacific (Tokyo)",
            "Asia Pacific (Osaka)"
        ],
        "GCP": [
            "Osaka"
        ],
        "Azure": [
            "JA East",
            "JA West"
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
            "Mexico"
        ],
        "Azure": [
            "MX Central"
        ]
    },

    "Netherlands": {
        "AWS": [],
        "GCP": [
            "Netherlands"
        ],
        "Azure": [
            "EU West"
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
            "PL Central"
        ]
    },

    "Qatar": {
        "AWS": [],
        "GCP": [
            "Doha"
        ],
        "Azure": [
            "QA Central"
        ]
    },

    "Saudi Arabia": {
        "AWS": [],
        "GCP": [
            "Dammam"
        ],
        "Azure": []
    },

    "Singapore": {
        "AWS": [
            "Asia Pacific (Singapore)"
        ],
        "GCP": [], 
        "Azure": []
    },

    "South Africa": {
        "AWS": [],
        "GCP": [
            "Johannesburg"
        ],
        "Azure": [
            "ZA North",
            "ZA West"
        ]
    },

    "South Korea": {
        "AWS": [
            "Asia Pacific (Seoul)"
        ],
        "GCP": [
            "Seoul"
        ],
        "Azure": [
            "KR Central",
            "KR South"
        ]
    },

    "Spain": {
        "AWS": [],
        "GCP": [
            "Madrid"
        ],
        "Azure": [
            "ES Central"
        ]
    },

    "Sweden": {
        "AWS": [
            "EU (Stockholm)"
        ],
        "GCP": [
            "Stockholm"
        ],
        "Azure": [
            "SE Central",
            "SE South"
        ]
    },

     "Switzerland": {
        "AWS": [],
        "GCP": [
            "Zurich"
        ],
        "Azure": [
            "CH North",
            "CH West"
        ]
    },

    "Taiwan": {
        "AWS": [],
        "GCP": [
            "Taiwan"
        ],
        "Azure": []
    },

    "United Arab Emirates": {
        "AWS": [],
        "GCP": [],
        "Azure": [
            "AE Central",
            "AE North"
        ]
    },

    "United Kingdom": {
        "AWS": [
            "EU (London)"
        ],
        "GCP": [
            "London"
        ],
        "Azure": [
            "UK South",
            "UK West"
        ]
    },
}

# def expand_common_locations(
#     requested: List[str],
#     clouds: Optional[List[str]]
# ) -> List[str]:
#     expanded: List[str] = []
#     # lowercase→canonical lookup
#     canonical = {k.lower(): k for k in COMMON_LOCATION_MAP}
#     for loc in requested:
#         key = loc.strip().lower()
#         if key in canonical:
#             per_cloud = COMMON_LOCATION_MAP[canonical[key]]
#             targets = clouds or per_cloud.keys()
#             for c in targets:
#                 expanded += per_cloud.get(c, [])
#         else:
#             expanded.append(loc)
#     return expanded


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