# -*- coding: utf-8 -*-

from typing import List, Optional

COMMON_LOCATION_MAP = {

    "North America": {
    "AWS": [
      "US East (N. Virginia)",
      "US East (Ohio)",
      "US West (Oregon)",
      "US West (N. California)",
      "Canada (Central)"
    ],
    "GCP": [
      "Iowa",
      "Northern Virginia",
      "South Carolina",
      "Las Vegas",
      "Toronto",
      "Salt Lake City",
      "Columbus",
      "Los Angeles",
      "Montréal",
      "Dallas",
      "Mexico",
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
      "US West Central",
      "CA Central",
      "CA East",
      "MX Central"
    ]
  },

  "South America": {
    "AWS": [
      "South America (São Paulo)"
    ],
    "GCP": [
      "São Paulo",
      "Santiago"
    ],
    "Azure": [
      "BR South",
      "BR Southeast",
      "CL Central"
    ]
  },

  "Europe": {
    "AWS": [
      "EU (Stockholm)",
      "EU (Paris)",
      "EU (Frankfurt)",
      "EU (Ireland)",
      "EU (London)"
    ],
    "GCP": [
      "Netherlands",
      "Belgium",
      "Finland",
      "Zurich",
      "Madrid",
      "Warsaw",
      "Milan",
      "Berlin",
      "Turin",
      "Frankfurt",
      "London",
      "Paris",
      "Stockholm"
    ],
    "Azure": [
      "EU North",
      "EU West",
      "FR Central",
      "FR South",
      "DE North",
      "DE West Central",
      "AT East",
      "ES Central",
      "IT North",
      "PL Central",
      "SE Central",
      "SE South",
      "UK South",
      "UK West",
      "CH North",
      "CH West"
    ]
  },

  "Asia Pacific": {
    "AWS": [
      "Asia Pacific (Tokyo)",
      "Asia Pacific (Sydney)",
      "Asia Pacific (Singapore)",
      "Asia Pacific (Mumbai)",
      "Asia Pacific (Osaka)",
      "Asia Pacific (Seoul)"
    ],
    "GCP": [
      "Taiwan",
      "Melbourne",
      "Delhi",
      "Hong Kong",
      "Jakarta",
      "Mumbai",
      "Mumbai",
      "Sydney",
      "Seoul",
      "Osaka",
    ],
    "Azure": [
      "AP East",
      "AP Southeast",
      "AU East",
      "AU Southeast",
      "ID Central",
      "IN Central",
      "IN Central Jio",
      "IN South",
      "IN West",
      "IN West Jio",
      "JA East",
      "JA West",
      "KR Central",
      "KR South",
      "MY West",
      "NZ North"
    ]
  },

  "Middle East & Africa": {
    "AWS": [],
    "GCP": [
      "Dammam",
      "Tel Aviv",
      "Doha",
      "Johannesburg"
    ],
    "Azure": [
      "AE Central",
      "AE North",
      "QA Central",
      "IL Central",
      "ZA North",
      "ZA West"
    ]
  },

  #add more locations as needed
}

def expand_common_locations(
    requested: List[str],
    clouds: Optional[List[str]]
) -> List[str]:
    expanded: List[str] = []
    # lowercase→canonical lookup
    canonical = {k.lower(): k for k in COMMON_LOCATION_MAP}
    for loc in requested:
        key = loc.strip().lower()
        if key in canonical:
            per_cloud = COMMON_LOCATION_MAP[canonical[key]]
            targets = clouds or per_cloud.keys()
            for c in targets:
                expanded += per_cloud.get(c, [])
        else:
            expanded.append(loc)
    return expanded
