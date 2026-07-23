from app.models import SatelliteLaunchSite, SatelliteObjectType, SatelliteOwner

SATCAT_OBJECT_TYPES: dict[str, SatelliteObjectType] = {
    "PAY": SatelliteObjectType.PAYLOAD,
    "R/B": SatelliteObjectType.ROCKET_BODY,
    "DEB": SatelliteObjectType.DEBRIS,
    "UNK": SatelliteObjectType.UNKNOWN,
}

SATCAT_OWNER_NAMES: dict[str, str] = {
    "AB": "Arab Satellite Communications Organization",
    "ABS": "Asia Broadcast Satellite",
    "AC": "AsiaSat",
    "ALG": "Algeria",
    "ARGN": "Argentina",
    "AUS": "Australia",
    "AZER": "Azerbaijan",
    "BEL": "Belgium",
    "BRAZ": "Brazil",
    "CA": "Canada",
    "CHBZ": "China/Brazil",
    "CHLE": "Chile",
    "CIS": "Commonwealth of Independent States",
    "CZCH": "Czech Republic",
    "DEN": "Denmark",
    "ECU": "Ecuador",
    "EGYP": "Egypt",
    "ESA": "European Space Agency",
    "ESRO": "European Space Research Organization",
    "EUME": "EUMETSAT",
    "EUTE": "Eutelsat",
    "FGER": "France/Germany",
    "FR": "France",
    "GER": "Germany",
    "GLOB": "Globalstar",
    "GREC": "Greece",
    "IM": "Inmarsat",
    "IND": "India",
    "INDO": "Indonesia",
    "IRAN": "Iran",
    "IRAQ": "Iraq",
    "ISRA": "Israel",
    "ISS": "International Space Station",
    "IT": "Italy",
    "ITSO": "Intelsat",
    "JPN": "Japan",
    "KAZ": "Kazakhstan",
    "LAOS": "Laos",
    "LUXE": "Luxembourg",
    "MALA": "Malaysia",
    "MEX": "Mexico",
    "NATO": "NATO",
    "NETH": "Netherlands",
    "NICO": "New ICO",
    "NIG": "Nigeria",
    "NKOR": "North Korea",
    "NOR": "Norway",
    "O3B": "O3b Networks",
    "ORB": "Orbcomm",
    "PAKI": "Pakistan",
    "PERU": "Peru",
    "POL": "Poland",
    "PRC": "China",
    "ROC": "Taiwan",
    "ROM": "Romania",
    "RP": "Philippines",
    "SAFR": "South Africa",
    "SAUD": "Saudi Arabia",
    "SEAL": "Sea Launch",
    "SES": "SES",
    "SING": "Singapore",
    "SKOR": "South Korea",
    "SPN": "Spain",
    "STCT": "Singapore/Taiwan",
    "SWED": "Sweden",
    "SWTZ": "Switzerland",
    "THAI": "Thailand",
    "TMMC": "Turkmenistan/Monaco",
    "TURK": "Turkey",
    "UAE": "United Arab Emirates",
    "UK": "United Kingdom",
    "UKR": "Ukraine",
    "URY": "Uruguay",
    "US": "United States",
    "USBZ": "United States/Brazil",
    "VENZ": "Venezuela",
    "VTNM": "Vietnam",
}

SATCAT_LAUNCH_SITE_NAMES: dict[str, str] = {
    "AFETR": "Cape Canaveral Space Force Station",
    "AFWTR": "Vandenberg Space Force Base",
    "CAS": "Canary Islands Airspace",
    "DLS": "Dombarovsky Launch Site",
    "ERAS": "Eastern Range Airspace",
    "FRGUI": "Guiana Space Centre",
    "HGSTR": "Hammaguir Space Track Range",
    "JSC": "Jiuquan Satellite Launch Center",
    "KODAK": "Kodiak Launch Complex",
    "KSCUT": "Uchinoura Space Center",
    "KWAJ": "Kwajalein Atoll",
    "KYMSC": "Kanye Space and Missile Complex",
    "NSC": "Naro Space Center",
    "PLMSC": "Plesetsk Cosmodrome",
    "SEAL": "Sea Launch Platform",
    "SEM": "Semnan Space Center",
    "SNMLP": "San Marco Launch Platform",
    "SRI": "Satish Dhawan Space Centre",
    "SVOB": "Svobodny Cosmodrome",
    "TANSC": "Tanegashima Space Center",
    "TSC": "Taiyuan Satellite Launch Center",
    "TTMTR": "Baikonur Cosmodrome",
    "TYMSC": "Taiyuan Satellite Launch Center",
    "VOSTO": "Vostochny Cosmodrome",
    "WLPIS": "Wallops Flight Facility",
    "WOMRA": "Woomera Test Range",
    "WSC": "Wenchang Space Launch Site",
    "XICLF": "Xichang Satellite Launch Center",
    "YAVNE": "Yavne Launch Facility",
}


def map_satcat_owner(owner_code: str | None) -> SatelliteOwner | None:
    if not owner_code:
        return None

    return SatelliteOwner(
        code=owner_code,
        name=SATCAT_OWNER_NAMES.get(owner_code, owner_code),
    )


def map_satcat_object_type(object_type_code: str | None) -> SatelliteObjectType | None:
    if not object_type_code:
        return None

    return SATCAT_OBJECT_TYPES.get(object_type_code)


def map_satcat_launch_site(launch_site_code: str | None) -> SatelliteLaunchSite | None:
    if not launch_site_code:
        return None

    return SatelliteLaunchSite(
        code=launch_site_code,
        name=SATCAT_LAUNCH_SITE_NAMES.get(launch_site_code, launch_site_code),
    )
