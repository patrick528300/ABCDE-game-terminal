"""First pygame map screen for ABCDE.

This phase renders the world board, ports, sea routes, and a player status UI.
Currency-control rules are intentionally omitted.
"""

from __future__ import annotations

import math
import random
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from Colony_dataBase import colonies
from trade_route_dataBase import routes as TRADE_ROUTE_DATA


SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 860
SIDE_PANEL_WIDTH = 360
MAP_MARGIN = 40
FPS = 60
FULLSCREEN_START = True
DEFAULT_MAX_ROUNDS = 50
MIN_MAX_ROUNDS = 40
LONDON_MERIDIAN = -0.1276
MIN_LATITUDE = -60.0
MAX_LATITUDE = 75.0
MAP_RECT = pygame.Rect(MAP_MARGIN, MAP_MARGIN + 34, SCREEN_WIDTH - SIDE_PANEL_WIDTH - MAP_MARGIN * 2, SCREEN_HEIGHT - MAP_MARGIN * 2 - 72)
BACKGROUND_IMAGE_PATH = Path("world_map_background.png")
USE_BACKGROUND_IMAGE = True
BACKGROUND_MIN_LATITUDE = -85.0
BACKGROUND_MAX_LATITUDE = 85.0
MAP_SCROLL_SPEED = 90
MAP_OVERLAY_X_OFFSET = -45
MAP_OVERLAY_Y_OFFSET = 28

ROBINSON_TABLE = [
    (0, 1.0000, 0.0000),
    (5, 0.9986, 0.0620),
    (10, 0.9954, 0.1240),
    (15, 0.9900, 0.1860),
    (20, 0.9822, 0.2480),
    (25, 0.9730, 0.3100),
    (30, 0.9600, 0.3720),
    (35, 0.9427, 0.4340),
    (40, 0.9216, 0.4958),
    (45, 0.8962, 0.5571),
    (50, 0.8679, 0.6176),
    (55, 0.8350, 0.6769),
    (60, 0.7986, 0.7346),
    (65, 0.7597, 0.7903),
    (70, 0.7186, 0.8435),
    (75, 0.6732, 0.8936),
    (80, 0.6213, 0.9394),
    (85, 0.5722, 0.9761),
    (90, 0.5322, 1.0000),
]

OCEAN = (189, 224, 241)
OCEAN_DEEP = (169, 211, 233)
LAND = (244, 229, 156)
LAND_DARK = (202, 184, 112)
COAST = (194, 170, 90)
TEXT = (238, 242, 244)
TEXT_MUTED = (177, 190, 199)
PANEL = (26, 34, 43)
PANEL_ALT = (35, 46, 57)
ROUTE = (8, 55, 112)
ROUTE_FAINT = ROUTE
LAND_GOODS_ROUTE = (122, 78, 42)
PORT = (70, 153, 232)
CAPITAL = (82, 196, 114)
STRAIT = (230, 79, 79)
HOVER = (255, 255, 255)
BLACK = (0, 0, 0)

OWNER_COLORS = {
    "United Kingdom": (230, 209, 67),
    "Russia": (210, 71, 73),
    "China": (72, 180, 95),
    "Japan": (222, 143, 57),
    "Pirates": (130, 89, 188),
    "United States": (67, 132, 221),
    None: (165, 170, 176),
}

OWNER_ICONS = {
    "United Kingdom": "🇬🇧",
    "Russia": "🇷🇺",
    "China": "🐲",
    "Japan": "🇯🇵",
    "Pirates": "🏴‍☠️",
    "United States": "🇺🇸",
}

OWNER_LEGEND_LABELS = {
    "United Kingdom": "UK",
    "Russia": "Russia",
    "China": "China",
    "Japan": "Japan",
    "Pirates": "Pirates",
    "United States": "USA",
}

RESOURCE_ORDER = ["wood", "metal", "gold", "sugar", "fertilizer", "oil"]
RESOURCE_COLORS = {
    "wood": (127, 92, 50),
    "metal": (142, 154, 164),
    "gold": (224, 180, 57),
    "sugar": (239, 238, 225),
    "fertilizer": (89, 151, 84),
    "oil": (35, 37, 42),
}
RESOURCE_LABELS = {
    "wood": "WOOD",
    "metal": "METAL",
    "gold": "GOLD",
    "sugar": "SUGAR",
    "fertilizer": "FERT",
    "oil": "OIL",
}
RESOURCE_PRICES = {
    "wood": {"buy": 15, "sell": 5},
    "metal": {"buy": 25, "sell": 10},
    "gold": {"buy": 70, "sell": 70},
    "sugar": {"buy": 30, "sell": 15},
    "fertilizer": {"buy": 40, "sell": 15},
    "oil": {"buy": 50, "sell": 30},
}
FACTORY_COSTS = {
    "green": {"base_money": 50, "wood": 2, "metal": 1},
    "red": {"base_money": 80, "wood": 3, "metal": 2},
    "upgrade": {"base_money": 30, "wood": 1, "metal": 1},
}
SHIP_COSTS = {
    "Merchant": {"base_money": 30, "wood": 2, "metal": 1},
    "Warship": {"base_money": 60, "wood": 3, "metal": 2},
    "Pirate": {"base_money": 60, "wood": 3, "metal": 2},
}
SHIP_COST = SHIP_COSTS["Merchant"]
RUSSIA_SHIP_COST = {"money": 20, "wood_or_metal": 1}
LICENSES = {
    "smuggler": {"label": "Smuggler's License", "price": 500, "renewal": 200},
    "pirate": {"label": "Pirate's License", "price": 800, "renewal": 300},
}
LICENSE_DURATION_ROUNDS = 10
LICENSE_RENEW_WINDOW = 3
INITIAL_RESOURCES = {
    "wood": 5,
    "metal": 5,
    "gold": 0,
    "sugar": 0,
    "fertilizer": 0,
    "oil": 0,
}

EMPIRE_ORDER = [
    "United Kingdom",
    "Russia",
    "China",
    "Japan",
    "Pirates",
    "United States",
]

CAPITALS = {
    "United Kingdom": "London",
    "Russia": "Murmansk",
    "China": "Shanghai",
    "Japan": "Tokyo",
    "Pirates": "Timor",
    "United States": "New_York",
}

SKILLS = {
    "United Kingdom": "+$10 tax for each port/choking",
    "Russia": "Ship building fee and materials are halved",
    "China": "Pays reduced foreign fees; earns higher fees from foreign entry",
    "Japan": "All ports allow entry, fees still apply",
    "Pirates": "Can rob; cannot invest trade cards",
    "United States": "Factory building fee is halved; material use is unchanged",
}

GAME_RULES = [
    "Objective",
    "Play until the configured final round. The final evaluation compares money, ports, factories, resources, completed trade, and war winrate.",
    "Turn Order",
    "Turns advance United Kingdom, Russia, China, Japan, Pirates, United States. When the United States ends its turn, the round increases by one.",
    "Ports And Ownership",
    "Each country starts with the same number of ports. Capitals cannot be captured. Ports may collect tax every 5 rounds. If a port is captured in war, its factory and stored goods transfer to the winner.",
    "Ships",
    "Merchant speed is 3, warship speed is 2, pirate speed is 4. Ships may stay, sail to a connected port, continue a voyage, return, join another ship, or attack when allowed.",
    "Sail Limit",
    "A ship that has not entered a port within the last 4 rounds sinks. Unfinished voyage distance is not charged when sunk.",
    "Fees",
    "Foreign ships pay the destination port fee unless an entry rule or license waives it. Pirate ports are open and free. Japan may enter all ports but still pays fees.",
    "China Skill",
    "China pays $10 less at foreign ports and $15 less at foreign choking ports, with a minimum fee of $5. Foreigners entering Chinese ports pay $10 extra, or $15 extra at Chinese choking ports.",
    "Trade Investment",
    "Invest costs the current trade-card price and offers three trade cards. Pirates cannot invest. A merchant declares a route at either endpoint and earns profit by selling at the destination.",
    "Cargo Storage",
    "Loaded merchants may store goods at ports with space. Stored goods can be picked up by eligible ships. Goods may move through land routes where available.",
    "Market",
    "Resources can be bought and sold at current market prices. Prices react to wars, news, and cooling periods.",
    "Letter Of Marque",
    "Smuggler's License costs $500 and renewal costs $200. It allows entry into any non-plague port without fees. Pirate's License costs $800 and renewal costs $300. It lets merchant ships rob enemy merchants as privateers. Licenses last 10 rounds and can be renewed in the last 3 rounds.",
    "Factories",
    "Green and red factories produce resources every 5 rounds. Shipyard factories build ships. United States pays half factory building fee but normal materials. Pirates cannot build shipyard factories.",
    "Ship Building",
    "Merchant ships cost $30 plus 2 wood and 1 metal. Warships cost $60 plus 3 wood and 2 metal. Russia pays half ship building fee and half materials rounded up, with 1 staying 1.",
    "Combat",
    "Merchant power is 2 empty or 1 loaded. Pirate power is 2. Warship power is 3. Normal port power is 4 and pirate port power is 3. Combat is one entity vs one entity using dice times power.",
    "War And Non-War Actions",
    "Attacking ports and national warships is war. Pirate rob against merchants is not war. Warships enforcing against pirates is not war. War changes prices; rob and enforce do not.",
    "Port Protection",
    "If an enemy ship is inside a foreign non-pirate port, attackers must defeat the port before attacking ships inside. Pirate ports do not protect ships inside unless the port itself is attacked.",
    "Resources",
    "Oil can boost combat or factory output. Sugar can boost one enroute ship until it reaches the next port. Fertilizer is auto-used for wood or sugar factory bonuses.",
    "News",
    "Every 5 rounds, maritime and economic news may affect ports, ship speed, trade card cost, or resource prices for a limited duration.",
]

# Route network copied from map.ipynb. Trade-route cards are not used for map lines.
NOTEBOOK_NAME_ALIASES = {
    "Acapulco": "Acapulco_De_Juarez",
    "Bering": "Strait_of_Bering",
    "Bombay": "Mumbai",
    "Cabo_Verde": "Cape_Verde",
    "Columbo": "Colombo",
    "Galapagos": "Galapagos_Islands",
    "Hormuz": "Strait_of_Hormuz",
    "Singapore": "Strait_of_Malacca",
    "Mandab": "Strait_of_Mandeb",
    "Mozambique": "Strait_of_Mozambique",
    "Rekjavik": "Reykjavik",
    "St_Pertersburg": "Saint_Petersburg",
}

NOTEBOOK_COURSES = [
    ("Honolulu", "Bering", 3),
    ("Papeete", "Honolulu", 3),
    ("Papeete", "Tierra_del_Fuego", 8),
    ("Bering", "Anchorage", 4),
    ("Anchorage", "Vancouver", 2),
    ("Vancouver", "Honolulu", 3),
    ("Vancouver", "San_Francisco", 1),
    ("San_Francisco", "Honolulu", 3),
    ("San_Francisco", "Acapulco", 2),
    ("San_Francisco", "Galapagos", 5),
    ("Acapulco", "Honolulu", 4),
    ("Acapulco", "Galapagos", 2),
    ("Papeete", "Galapagos", 4),
    ("Galapagos", "Lima", 1),
    ("Lima", "Papeete", 5),
    ("Antofagasta", "Lima", 2),
    ("Lima", "Valparaiso", 4),
    ("Antofagasta", "Valparaiso", 3),
    ("Tierra_del_Fuego", "Valparaiso", 2),
    ("Tierra_del_Fuego", "Lima", 4),
    ("Churchill", "Nuuk", 3),
    ("Nuuk", "Newfoundland", 1),
    ("Nuuk", "Rekjavik", 2),
    ("Rekjavik", "Murmansk", 4),
    ("Rekjavik", "London", 2),
    ("Rekjavik", "Gibraltar", 2),
    ("Murmansk", "London", 3),
    ("London", "Amsterdam", 1),
    ("London", "Gibraltar", 3),
    ("London", "Cabo_Verde", 3),
    ("Gibraltar", "Tunis", 1),
    ("Tunis", "Istanbul", 1),
    ("Amsterdam", "St_Pertersburg", 2),
    ("Newfoundland", "Rekjavik", 3),
    ("Newfoundland", "London", 3),
    ("Newfoundland", "New_York", 1),
    ("Newfoundland", "Santo_Domingo", 2),
    ("New_York", "Gibraltar", 4),
    ("New_York", "Cabo_Verde", 5),
    ("New_York", "Recife", 4),
    ("New_York", "Jacksonville", 1),
    ("London", "New_York", 3),
    ("London", "Jacksonville", 6),
    ("Jacksonville", "Gibraltar", 4),
    ("Jacksonville", "Santo_Domingo", 2),
    ("Jacksonville", "Havana", 1),
    ("New_York", "Santo_Domingo", 2),
    ("Cabo_Verde", "Santo_Domingo", 4),
    ("Veracruz", "Havana", 1),
    ("Santo_Domingo", "Havana", 1),
    ("Santo_Domingo", "Maracaibo", 1),
    ("Santo_Domingo", "Gibraltar", 5),
    ("Santo_Domingo", "Freetown", 4),
    ("Santo_Domingo", "Benguela", 5),
    ("Maracaibo", "Cabo_Verde", 4),
    ("Freetown", "Cabo_Verde", 2),
    ("Maracaibo", "Recife", 3),
    ("Maracaibo", "Benguela", 4),
    ("Cabo_Verde", "Recife", 3),
    ("Freetown", "Recife", 3),
    ("Cabo_Verde", "Gibraltar", 2),
    ("Cabo_Verde", "Freetown", 1),
    ("Cabo_Verde", "Cape_of_Good_Hope", 7),
    ("Benguela", "Recife", 3),
    ("Rio_de_Janeiro", "Recife", 1),
    ("Cape_of_Good_Hope", "Recife", 5),
    ("Cape_of_Good_Hope", "Rio_de_Janeiro", 4),
    ("Buenos_Aires", "Rio_de_Janeiro", 1),
    ("Tierra_del_Fuego", "Rio_de_Janeiro", 4),
    ("Tierra_del_Fuego", "Buenos_Aires", 2),
    ("Freetown", "Lagos", 1),
    ("Freetown", "Walvis_Bay", 3),
    ("Rio_de_Janeiro", "Walvis_Bay", 3),
    ("Lagos", "Walvis_Bay", 2),
    ("Benguela", "Walvis_Bay", 1),
    ("Cape_of_Good_Hope", "Walvis_Bay", 2),
    ("Cape_of_Good_Hope", "Tierra_del_Fuego", 6),
    ("Cape_of_Good_Hope", "Mozambique", 2),
    ("Cape_of_Good_Hope", "Port_Louis", 3),
    ("Cape_of_Good_Hope", "Perth", 6),
    ("Mozambique", "Mombassa", 1),
    ("Mozambique", "Port_Louis", 2),
    ("Mozambique", "Male", 3),
    ("Port_Louis", "Mombassa", 2),
    ("Port_Louis", "Mogadishu", 2),
    ("Port_Louis", "Bombay", 3),
    ("Port_Louis", "Male", 3),
    ("Port_Louis", "Jakarta", 4),
    ("Port_Louis", "Perth", 5),
    ("Mombassa", "Mogadishu", 1),
    ("Mombassa", "Male", 3),
    ("Mogadishu", "Mandab", 1),
    ("Mogadishu", "Hormuz", 3),
    ("Mogadishu", "Male", 1),
    ("Hormuz", "Mandab", 2),
    ("Hormuz", "Male", 2),
    ("Bombay", "Hormuz", 1),
    ("Bombay", "Male", 1),
    ("Bombay", "Mandab", 1),
    ("Male", "Colombo", 1),
    ("Male", "Perth", 5),
    ("Colombo", "Calcutta", 1),
    ("Colombo", "Singapore", 1),
    ("Colombo", "Jakarta", 3),
    ("Calcutta", "Yangon", 1),
    ("Singapore", "Yangon", 1),
    ("Singapore", "Calcutta", 2),
    ("Singapore", "Male", 2),
    ("Singapore", "Manila", 2),
    ("Singapore", "Jakarta", 2),
    ("Singapore", "Timor", 3),
    ("Jakarta", "Timor", 1),
    ("Jakarta", "Perth", 2),
    ("Jakarta", "Manila", 2),
    ("Manila", "Tokyo", 2),
    ("Manila", "Timor", 1),
    ("Manila", "Yaren", 3),
    ("Manila", "Honolulu", 5),
    ("Tokyo", "Honolulu", 6),
    ("Tokyo", "Port_Moresby", 3),
    ("Tokyo", "Vladivostok", 3),
    ("Vladivostok", "Vancouver", 6),
    ("Vladivostok", "Bering", 3),
    ("Port_Moresby", "Timor", 1),
    ("Port_Moresby", "Yaren", 2),
    ("Port_Moresby", "Suva", 2),
    ("Port_Moresby", "Sydney", 3),
    ("Wellington", "Port_Moresby", 4),
    ("Yaren", "Honolulu", 5),
    ("Yaren", "Papeete", 5),
    ("Yaren", "Suva", 2),
    ("Suva", "Papeete", 5),
    ("Perth", "Cape_of_Good_Hope", 6),
    ("Perth", "Sydney", 3),
    ("Wellington", "Sydney", 1),
    ("Wellington", "Yaren", 3),
    ("Wellington", "Suva", 2),
    ("Wellington", "Papeete", 5),
    ("Wellington", "Tierra_del_Fuego", 9),
    ("Maracaibo", "Freetown", 4),
    ("Tierra_del_Fuego", "Freetown", 5),
    ("Tierra_del_Fuego", "Walvis_Bay", 5),
    ("Rio_de_Janeiro", "Freetown", 5),
    ("San_Diego", "San_Francisco", 1),
    ("San_Diego", "Honolulu", 3),
    ("San_Diego", "Galapagos", 3),
    ("Tierra_del_Fuego", "Galapagos", 4),
    ("Honolulu", "Galapagos", 4),
    ("Papeete", "Acapulco", 4),
    ("Panama_City", "Acapulco", 2),
    ("Panama_City", "Galapagos", 1),
    ("Panama_City", "Lima", 1),
    ("Colon", "Santo_Domingo", 1),
    ("Colon", "Maracaibo", 1),
    ("Colon", "Havana", 1),
    ("Colon", "Veracruz", 1),
    ("Istanbul", "Port_Said", 1),
    ("Port_Said", "Tunis", 1),
    ("Suez_City", "Mandab", 2),
    ("Hormuz", "Suez_City", 2),
    ("Shanghai", "Tokyo", 1),
    ("Shanghai", "Hong_Kong", 2),
    ("Shanghai", "Manila", 2),
    ("Shanghai", "Honolulu", 6),
    ("Hong_Kong", "Tokyo", 2),
    ("Hong_Kong", "Vladivostok", 3),
    ("Hong_Kong", "Manila", 1),
    ("Hong_Kong", "Singapore", 2),
    ("Hong_Kong", "Jakarta", 3),
    ("Singapore", "Port_Louis", 4),
    ("Manila", "Acapulco", 12),
    ("Amsterdam", "Gibraltar", 3),
    ("Amsterdam", "Rekjavik", 2),
    ("Colombo", "Perth", 4),
    ("Manaus", "Belem", 2),
    ("New_Orleans", "Havana", 1),
    ("New_Orleans", "Veracruz", 1),
    ("Belem", "Recife", 2),
    ("Belem", "Maracaibo", 3),
    ("Belem", "Cabo_Verde", 4),
    ("Belem", "Freetown", 4),
    ("Oslo", "London", 1),
    ("Oslo", "Amsterdam", 1),
    ("Oslo", "Rekjavik", 1),
    ("Oslo", "Murmansk", 2),
    ("Oslo", "Newfoundland", 5),
    ("Rekjavik", "New_York", 5),
    ("Oslo", "St_Pertersburg", 3),
]

NOTEBOOK_PORT_ORDER = [
    "Bering",
    "Honolulu",
    "Papeete",
    "Anchorage",
    "Vancouver",
    "San_Francisco",
    "Acapulco",
    "Galapagos",
    "Lima",
    "Antofagasta",
    "Valparaiso",
    "Tierra_del_Fuego",
    "Churchill",
    "Nuuk",
    "Rekjavik",
    "Murmansk",
    "Newfoundland",
    "London",
    "Amsterdam",
    "St_Pertersburg",
    "New_York",
    "Jacksonville",
    "Gibraltar",
    "Tunis",
    "Istanbul",
    "Veracruz",
    "Havana",
    "Santo_Domingo",
    "Cabo_Verde",
    "Maracaibo",
    "Freetown",
    "Lagos",
    "Recife",
    "Benguela",
    "Rio_de_Janeiro",
    "Walvis_Bay",
    "Buenos_Aires",
    "Cape_of_Good_Hope",
    "Mandab",
    "Mombassa",
    "Mozambique",
    "Mogadishu",
    "Hormuz",
    "Port_Louis",
    "Bombay",
    "Male",
    "Colombo",
    "Calcutta",
    "Yangon",
    "Singapore",
    "Jakarta",
    "Perth",
    "Timor",
    "Port_Moresby",
    "Sydney",
    "Wellington",
    "Manila",
    "Tokyo",
    "Shanghai",
    "Hong_Kong",
    "Vladivostok",
    "Yaren",
    "Suva",
    "San_Diego",
    "Panama_City",
    "Colon",
    "Suez_City",
    "Port_Said",
    "Belem",
    "Manaus",
    "New_Orleans",
    "Oslo",
]

PORT_GEO_COORDS = {
    "Bering": (62.51, 178.24),
    "Honolulu": (21.31, -157.86),
    "Papeete": (-17.55, -149.56),
    "Anchorage": (61.22, -170.90),
    "Vancouver": (49.28, -150.12),
    "San_Francisco": (38.03, -146.27),
    "Acapulco": (13.82, -125.42),
    "Galapagos": (-10.39, -111.20),
    "Lima": (-22.49, -99.37),
    "Antofagasta": (-48.29, -100.42),
    "Valparaiso": (-63.32, -110.07),
    "Tierra_del_Fuego": (-75.61, -113.77),
    "Churchill": (55.44, -107.24),
    "Nuuk": (68.29, -73.10),
    "Rekjavik": (64.15, -21.94),
    "Murmansk": (71.09, 30.35),
    "Newfoundland": (48.10, -73.88),
    "London": (51.84, -18.01),
    "Amsterdam": (55.05, -8.11),
    "St_Pertersburg": (61.71, 16.15),
    "New_York": (40.21, -92.62),
    "Jacksonville": (29.71, -99.61),
    "Gibraltar": (34.41, -22.61),
    "Tunis": (34.41, -4.32),
    "Istanbul": (38.39, 14.03),
    "Veracruz": (15.26, -116.36),
    "Havana": (18.69, -101.44),
    "Santo_Domingo": (14.00, -88.94),
    "Cabo_Verde": (11.65, -40.16),
    "Maracaibo": (5.15, -90.08),
    "Freetown": (-1.54, -26.96),
    "Lagos": (-2.44, -9.31),
    "Recife": (-22.85, -55.95),
    "Benguela": (-22.58, 0.41),
    "Rio_de_Janeiro": (-37.30, -66.88),
    "Walvis_Bay": (-34.95, 0.51),
    "Buenos_Aires": (-49.03, -82.98),
    "Cape_of_Good_Hope": (-50.00, 10.18),
    "Mandab": (4.97, 31.24),
    "Mombassa": (-10.93, 28.47),
    "Mozambique": (-31.16, 29.43),
    "Mogadishu": (-1.35, 36.79),
    "Hormuz": (22.13, 45.69),
    "Port_Louis": (-32.96, 47.63),
    "Bombay": (14.72, 62.40),
    "Male": (-3.52, 62.57),
    "Colombo": (1.35, 72.98),
    "Calcutta": (16.17, 76.56),
    "Yangon": (10.75, 86.92),
    "Singapore": (-8.22, 95.60),
    "Jakarta": (-18.33, 103.14),
    "Perth": (-46.07, 116.34),
    "Timor": (-25.02, 128.08),
    "Port_Moresby": (-17.61, 143.01),
    "Sydney": (-50.33, 157.47),
    "Wellington": (-52.22, 178.12),
    "Manila": (4.61, 116.30),
    "Tokyo": (32.60, 133.88),
    "Shanghai": (26.82, 112.34),
    "Hong_Kong": (17.79, 106.34),
    "Vladivostok": (43.49, 128.12),
    "Yaren": (0.63, 169.28),
    "Suva": (-27.91, 178.67),
    "San_Diego": (30.43, -139.09),
    "Panama_City": (0.27, -101.48),
    "Colon": (4.06, -97.80),
    "Suez_City": (23.93, 22.40),
    "Port_Said": (29.53, 18.97),
    "Belem": (-8.25, -62.00),
    "Manaus": (-13.50, -72.00),
    "New_Orleans": (24.60, -106.50),
    "Oslo": (64.00, 2.20),
}

PORT_DATA_OVERRIDES = {
    "Gibraltar": {
        "owner": "Pirates",
        "tax": 30,
        "fee": 20,
        "resource": "shipyard",
        "kind": "choking",
    },
    "San_Diego": {
        "owner": "United States",
        "tax": 20,
        "fee": 10,
        "resource": "shipyard",
        "kind": "port",
    },
    "Singapore": {
        "tax": 30,
        "storage_capacity": 6,
        "kind": "port",
    },
    "Acapulco": {"fee": 20},
    "Veracruz": {"fee": 20},
    "Panama_City": {"tax": 30, "fee": 20, "storage_capacity": 6, "kind": "port"},
    "Colon": {"tax": 30, "fee": 20, "storage_capacity": 6, "kind": "port"},
    "Suez_City": {"tax": 30, "fee": 20, "storage_capacity": 6, "kind": "port"},
    "Port_Said": {"tax": 30, "fee": 20, "storage_capacity": 6, "kind": "port"},
    "Belem": {"tax": 20, "fee": 10, "resource": "sugar", "kind": "port"},
    "Manaus": {"tax": 20, "fee": 10, "resource": "gold", "kind": "port"},
    "New_Orleans": {"tax": 20, "fee": 15, "resource": "oil", "kind": "port"},
    "Oslo": {"tax": 20, "fee": 15, "resource": "oil", "kind": "port"},
    "Hong_Kong": {"resource": "metal"},
    "Valparaiso": {"resource": "metal"},
}

NOTEBOOK_CHOKING_POINTS = {
    "Bering",
    "Gibraltar",
    "Cape_of_Good_Hope",
    "Hormuz",
    "Singapore",
    "Mandab",
    "Mozambique",
    "Newfoundland",
    "Tierra_del_Fuego",
}

PORT_OUTLINE_GROUPS = [
    ["Bering", "Anchorage", "Vancouver", "San_Francisco", "San_Diego", "Acapulco", "Panama_City"],
    ["Churchill", "Newfoundland", "New_York", "Jacksonville", "Havana", "Santo_Domingo", "Colon"],
    ["Colon", "Maracaibo", "Galapagos", "Lima", "Antofagasta", "Valparaiso", "Tierra_del_Fuego", "Buenos_Aires", "Rio_de_Janeiro", "Recife", "Maracaibo"],
    ["Rekjavik", "London", "Amsterdam", "St_Pertersburg", "Murmansk", "Rekjavik"],
    ["Gibraltar", "Tunis", "Istanbul", "Port_Said", "Suez_City", "Mandab", "Mogadishu", "Mombassa", "Mozambique", "Cape_of_Good_Hope", "Walvis_Bay", "Benguela", "Lagos", "Freetown", "Cabo_Verde", "Gibraltar"],
    ["Hormuz", "Bombay", "Colombo", "Calcutta", "Yangon", "Singapore", "Jakarta", "Hong_Kong", "Shanghai", "Tokyo", "Vladivostok", "Hormuz"],
    ["Jakarta", "Timor", "Port_Moresby", "Sydney", "Perth", "Jakarta"],
    ["Wellington", "Sydney", "Suva", "Yaren", "Papeete", "Wellington"],
    ["Honolulu", "Bering", "Vladivostok", "Tokyo", "Manila", "Yaren", "Papeete", "Honolulu"],
]

SEA_ROUTE_WAYPOINTS = {
    ("Amsterdam", "St_Pertersburg"): [(56.0, 6.5), (56.0, 12.5), (58.5, 20.0)],
    ("Murmansk", "London"): [(70.0, 20.0), (63.0, 2.0), (55.0, -2.0)],
    ("London", "Cabo_Verde"): [(48.0, -8.0), (32.0, -15.0)],
    ("London", "Gibraltar"): [(48.0, -7.0), (42.0, -10.0)],
    ("London", "New_York"): [(50.0, -20.0), (45.0, -40.0), (41.0, -62.0)],
    ("London", "Jacksonville"): [(48.0, -18.0), (38.0, -40.0), (30.0, -68.0)],
    ("Jacksonville", "Gibraltar"): [(30.0, -65.0), (33.0, -40.0), (35.0, -15.0)],
    ("Colon", "Veracruz"): [(12.0, -82.0), (18.0, -90.0)],
    ("Port_Said", "Tunis"): [(32.0, 25.0), (34.0, 18.0)],
    ("Suez_City", "Mandab"): [(22.0, 36.0), (16.0, 40.0)],
    ("New_York", "Jacksonville"): [(35.5, -74.5)],
    ("Churchill", "Nuuk"): [(60.0, -88.0), (62.0, -70.0), (63.0, -58.0)],
    ("Newfoundland", "Santo_Domingo"): [(37.0, -58.0), (25.0, -66.0)],
    ("Vladivostok", "Vancouver"): [(48.0, 160.0), (51.0, -170.0), (52.0, -145.0)],
    ("Vladivostok", "Bering"): [(50.0, 150.0), (57.0, 170.0)],
    ("Tokyo", "Honolulu"): [(31.0, 160.0), (26.0, -175.0)],
    ("Shanghai", "Honolulu"): [(28.0, 150.0), (25.0, 175.0)],
    ("Manila", "Acapulco"): [(18.0, 145.0), (18.0, 175.0), (16.0, -160.0), (15.0, -135.0)],
    ("Manila", "Tokyo"): [(21.0, 128.0), (29.0, 136.0)],
    ("Shanghai", "Tokyo"): [(31.0, 127.0), (33.5, 134.0)],
    ("Hong_Kong", "Tokyo"): [(23.0, 122.0), (29.0, 131.0)],
    ("Hong_Kong", "Vladivostok"): [(25.0, 123.0), (34.0, 129.0), (41.0, 132.0)],
    ("Hong_Kong", "Manila"): [(18.0, 117.0)],
    ("Hong_Kong", "Singapore"): [(14.0, 112.0), (4.0, 106.0)],
    ("Hong_Kong", "Jakarta"): [(10.0, 112.0), (-3.0, 109.0)],
    ("Colombo", "Calcutta"): [(10.0, 85.0), (17.0, 88.0)],
    ("Calcutta", "Yangon"): [(17.0, 91.0)],
    ("Singapore", "Yangon"): [(3.0, 96.0), (9.0, 94.0)],
    ("Singapore", "Calcutta"): [(5.0, 92.0), (13.0, 88.0)],
    ("Singapore", "Male"): [(-3.0, 88.0), (-4.0, 76.0)],
    ("Singapore", "Timor"): [(-10.0, 108.0), (-15.0, 120.0)],
    ("Hormuz", "Mandab"): [(20.0, 58.0), (14.0, 50.0), (12.0, 43.0)],
    ("Hormuz", "Male"): [(18.0, 60.0), (8.0, 66.0)],
    ("Bombay", "Mandab"): [(16.0, 65.0), (13.0, 55.0)],
    ("Bombay", "Hormuz"): [(20.0, 65.0), (24.0, 58.0)],
    ("Port_Louis", "Bombay"): [(-10.0, 62.0), (8.0, 66.0)],
    ("Singapore", "Port_Louis"): [(-8.0, 90.0), (-15.0, 72.0), (-20.0, 58.0)],
    ("Port_Louis", "Jakarta"): [(-18.0, 75.0), (-12.0, 92.0)],
    ("Port_Louis", "Perth"): [(-25.0, 78.0), (-30.0, 100.0)],
    ("Jakarta", "Perth"): [(-13.0, 110.0), (-24.0, 111.0)],
    ("Perth", "Sydney"): [(-38.0, 124.0), (-40.0, 140.0)],
    ("Wellington", "Sydney"): [(-39.0, 165.0)],
    ("Wellington", "Port_Moresby"): [(-35.0, 170.0), (-25.0, 160.0), (-15.0, 151.0)],
    ("Wellington", "Yaren"): [(-35.0, 175.0), (-12.0, 176.0)],
    ("Wellington", "Suva"): [(-35.0, 178.0), (-25.0, 178.0)],
    ("Wellington", "Papeete"): [(-32.0, -175.0), (-23.0, -162.0)],
    ("Wellington", "Tierra_del_Fuego"): [(-52.0, -170.0), (-55.0, -120.0)],
    ("Lima", "Papeete"): [(-14.0, -110.0), (-16.0, -130.0)],
    ("Lima", "Valparaiso"): [(-20.0, -78.0), (-28.0, -75.0), (-34.0, -73.0)],
    ("Cape_of_Good_Hope", "Perth"): [(-42.0, 50.0), (-40.0, 90.0)],
    ("Cape_of_Good_Hope", "Tierra_del_Fuego"): [(-50.0, -5.0), (-55.0, -40.0)],
    ("Tierra_del_Fuego", "Rio_de_Janeiro"): [(-53.0, -55.0), (-35.0, -45.0)],
    ("Tierra_del_Fuego", "Buenos_Aires"): [(-52.0, -58.0), (-42.0, -57.0)],
    ("Buenos_Aires", "Rio_de_Janeiro"): [(-31.0, -48.0)],
    ("Rio_de_Janeiro", "Recife"): [(-17.0, -34.0)],
    ("Maracaibo", "Recife"): [(5.0, -55.0), (-2.0, -42.0)],
    ("Belem", "Recife"): [(-6.0, -38.0)],
    ("Belem", "Maracaibo"): [(4.0, -55.0)],
    ("Belem", "Cabo_Verde"): [(4.0, -38.0), (9.0, -30.0)],
    ("Belem", "Freetown"): [(2.0, -35.0), (5.0, -20.0)],
    ("New_Orleans", "Havana"): [(25.0, -88.0)],
    ("New_Orleans", "Veracruz"): [(24.0, -92.0), (20.0, -94.0)],
    ("Oslo", "Rekjavik"): [(62.0, -5.0), (64.0, -14.0)],
    ("Oslo", "Murmansk"): [(70.0, 15.0), (71.0, 25.0)],
    ("Oslo", "Newfoundland"): [(62.0, -10.0), (58.0, -35.0), (52.0, -55.0)],
    ("Rekjavik", "New_York"): [(58.0, -35.0), (48.0, -55.0), (42.0, -70.0)],
    ("Oslo", "St_Pertersburg"): [(60.0, 10.0), (60.0, 18.0)],
    ("Santo_Domingo", "Freetown"): [(12.0, -60.0), (8.0, -35.0), (5.0, -18.0)],
    ("Maracaibo", "Freetown"): [(7.0, -55.0), (5.0, -32.0), (4.0, -18.0)],
    ("Santo_Domingo", "Benguela"): [(8.0, -55.0), (0.0, -30.0), (-12.0, -10.0)],
    ("Maracaibo", "Benguela"): [(3.0, -55.0), (-5.0, -30.0), (-14.0, -10.0)],
    ("Benguela", "Recife"): [(-18.0, 0.0), (-12.0, -20.0)],
    ("Freetown", "Recife"): [(3.0, -20.0), (-3.0, -30.0)],
    ("Cabo_Verde", "Recife"): [(5.0, -25.0), (-3.0, -30.0)],
    ("Cabo_Verde", "Cape_of_Good_Hope"): [(0.0, -20.0), (-25.0, 5.0)],
    ("Freetown", "Lagos"): [(5.0, -6.0)],
    ("Freetown", "Walvis_Bay"): [(-5.0, 0.0), (-17.0, 8.0)],
    ("Lagos", "Walvis_Bay"): [(-6.0, 4.0), (-18.0, 8.0)],
    ("Benguela", "Walvis_Bay"): [(-18.0, 10.0)],
    ("Cape_of_Good_Hope", "Walvis_Bay"): [(-29.0, 12.0)],
    ("Cape_of_Good_Hope", "Mozambique"): [(-34.0, 31.0), (-25.0, 36.0)],
    ("Mozambique", "Mombassa"): [(-12.0, 43.0)],
    ("Mozambique", "Port_Louis"): [(-22.0, 44.0), (-20.0, 52.0)],
    ("Mozambique", "Male"): [(-15.0, 48.0), (-8.0, 58.0), (-4.0, 66.0)],
    ("Port_Louis", "Mombassa"): [(-12.0, 47.0)],
    ("Mombassa", "Mogadishu"): [(-1.0, 43.5)],
}


@dataclass
class Ship:
    name: str
    owner: str
    location: str
    kind: str
    destination: str | None = None
    progress: int = 0
    course_distance: int = 0
    attack_on_arrival: bool = False
    trade_card: TradeCard | None = None
    trade_destination: str | None = None
    distance_since_upkeep: int = 0
    last_port_round: int = 1
    sugar_speed_active: bool = False


@dataclass
class TradeCard:
    start: str
    end: str
    profit: int
    status: str = "undeclared"
    stolen_from: str | None = None


@dataclass
class StoredGood:
    owner: str
    trade_card: TradeCard
    trade_destination: str


@dataclass
class Treaty:
    text: str
    countries: list[str]
    effective_round: int
    expire_round: int


@dataclass
class AttackPrompt:
    attacker: Ship
    defender: object
    trigger: str
    location: str | None = None
    attacker_uses_oil: bool = False


@dataclass
class HistoryEvent:
    round_number: int
    kind: str
    title: str
    details: list[str]


@dataclass
class NewsEvent:
    category: str
    kind: str
    title: str
    details: list[str]
    ports: set[str] = field(default_factory=set)
    expires_round: int = 0
    resource: str | None = None
    price_delta: int = 0
    trade_card_cost: int | None = None


@dataclass
class PendingShipBuild:
    owner: str
    location: str
    kind: str
    ready_round: int


@dataclass
class PendingGoodsTransfer:
    owner: str
    good: StoredGood
    from_port: str
    to_port: str
    turns_remaining: int
    waiting_ship_id: int | None
    arrival_fee_paid: bool = False


@dataclass
class PlayerState:
    country: str
    money: int
    resources: dict[str, int]
    ports: list
    ships: list[Ship]
    trade_cards: list[TradeCard]
    licenses: dict[str, int]
    transactions: list[str] = field(default_factory=list)
    oil_power_until: int = 0


@dataclass
class MapNode:
    name: str
    lat: float
    lon: float
    owner: str | None
    tax: int | None
    fee: int | None
    resource: str | None
    kind: str
    factory_level: str | None = None
    factory_owner: str | None = None
    entry_mode: str = "default"
    entry_countries: set[str] = field(default_factory=set)
    free_entry_countries: set[str] = field(default_factory=set)
    storage_capacity: int = 3


def canonical_notebook_name(name: str) -> str:
    return NOTEBOOK_NAME_ALIASES.get(name, name)


def colony_for_notebook_name(name: str):
    canonical = canonical_notebook_name(name)
    normalized = canonical.lower()
    for port in colonies:
        if port.name.lower() == normalized:
            return port
    return None


def node_kind(name: str, colony) -> str:
    if colony and colony.resource == "capital":
        return "capital"
    if name in NOTEBOOK_CHOKING_POINTS or (colony and colony.tax == 30):
        return "choking"
    return "port"


def build_map_nodes() -> dict[str, MapNode]:
    nodes = {}
    for name in NOTEBOOK_PORT_ORDER:
        lat, lon = PORT_GEO_COORDS[name]
        colony = colony_for_notebook_name(name)
        override = PORT_DATA_OVERRIDES.get(name, {})
        owner = override.get("owner", colony.owner if colony else None)
        tax = override.get("tax", colony.tax if colony else None)
        fee = override.get("fee", colony.fee if colony else None)
        if tax is None:
            tax = 20
        if fee is None:
            fee = 10
        resource = override.get("resource", colony.resource if colony else None)
        if resource == "arm":
            resource = "shipyard"
        nodes[name] = MapNode(
            name=name,
            lat=lat,
            lon=lon,
            owner=owner,
            tax=tax,
            fee=fee,
            resource=resource,
            kind=override.get("kind", node_kind(name, colony)),
            storage_capacity=override.get("storage_capacity", 3),
        )
    return nodes


MAP_NODES = build_map_nodes()
BACKGROUND_SURFACE: pygame.Surface | None = None
BACKGROUND_RECT = MAP_RECT.copy()
MAP_SCROLL_X = 0
MAP_SCROLL_Y = 0


def display_place_name(name: str) -> str:
    return name.replace("_", " ")


def adjusted_trade_profit(profit: int) -> int:
    if profit >= 550:
        return profit + 200
    if profit >= 450:
        return profit + 100
    if profit >= 350:
        return profit + 50
    return profit


def trade_card_from_route(route) -> TradeCard:
    start = display_place_name(route[0].name)
    end = display_place_name(route[1].name)
    if start in ("Dares Salaam", "Dare es Salaam"):
        start = "Monbasa"
    if end in ("Dares Salaam", "Dare es Salaam"):
        end = "Monbasa"
    return TradeCard(
        start=start,
        end=end,
        profit=adjusted_trade_profit(route[2]),
    )


MANUAL_TRADE_CARDS = [
    TradeCard("Amsterdam", "Manaus", 450),
    TradeCard("Rio de Janeiro", "Manaus", 290),
    TradeCard("Walvis Bay", "Manaus", 320),
    TradeCard("Amsterdam", "New Orleans", 400),
    TradeCard("New Orleans", "Tokyo", 650),
    TradeCard("New Orleans", "Hong Kong", 650),
    TradeCard("Hong Kong", "Vladivostok", 275),
]

TRADE_CARDS = [trade_card_from_route(route) for route in TRADE_ROUTE_DATA] + MANUAL_TRADE_CARDS

TRADE_CARD_NODE_ALIASES = {
    "Acapulco_De_Juarez": "Acapulco",
    "Dares_Salaam": "Mombassa",
    "Dare_es_Salaam": "Mombassa",
    "Monbasa": "Mombassa",
    "Mumbai": "Bombay",
    "New_Orleans": "New_Orleans",
    "Reykjavik": "Rekjavik",
    "Rio_De_Janeiro": "Rio_de_Janeiro",
}


def trade_label_to_node(label: str) -> str | None:
    key = label.replace(" ", "_")
    key = TRADE_CARD_NODE_ALIASES.get(key, key)
    if key in MAP_NODES:
        return key
    for name in MAP_NODES:
        if display_place_name(name).lower() == label.lower():
            return name
    return None


def trade_card_endpoint_nodes(card: TradeCard) -> tuple[str, str] | None:
    start = trade_label_to_node(card.start)
    end = trade_label_to_node(card.end)
    if not start or not end:
        return None
    return start, end


def trade_card_other_endpoint(card: TradeCard, port_name: str) -> str | None:
    endpoints = trade_card_endpoint_nodes(card)
    if not endpoints:
        return None
    start, end = endpoints
    if port_name == start:
        return end
    if port_name == end:
        return start
    return None


def normalized_delta_lon(lon: float) -> float:
    return ((lon - LONDON_MERIDIAN + 180) % 360) - 180


def mercator_y(lat: float) -> float:
    lat = max(MIN_LATITUDE, min(MAX_LATITUDE, lat))
    radians = math.radians(lat)
    return math.log(math.tan(math.pi / 4 + radians / 2))


def robinson_lookup(lat: float) -> tuple[float, float]:
    abs_lat = min(90.0, abs(lat))
    lower_index = int(abs_lat // 5)
    if lower_index >= len(ROBINSON_TABLE) - 1:
        x_coeff = ROBINSON_TABLE[-1][1]
        y_coeff = ROBINSON_TABLE[-1][2]
    else:
        lower_lat, lower_x, lower_y = ROBINSON_TABLE[lower_index]
        upper_lat, upper_x, upper_y = ROBINSON_TABLE[lower_index + 1]
        t = (abs_lat - lower_lat) / (upper_lat - lower_lat)
        x_coeff = lower_x + (upper_x - lower_x) * t
        y_coeff = lower_y + (upper_y - lower_y) * t
    return x_coeff, y_coeff if lat >= 0 else -y_coeff


def robinson_normalized(lat: float, lon: float) -> tuple[float, float]:
    delta_lon = normalized_delta_lon(lon)
    x_coeff, y_coeff = robinson_lookup(lat)
    x = (delta_lon / 180.0) * x_coeff
    y = y_coeff
    return x, y


def map_projection_rect() -> pygame.Rect:
    return BACKGROUND_RECT if BACKGROUND_SURFACE else MAP_RECT


def fit_rect_to_map_area(size: tuple[int, int]) -> pygame.Rect:
    width, height = size
    aspect = width / height
    fitted_w = MAP_RECT.width * 2
    fitted_h = round(fitted_w / aspect)
    return pygame.Rect(
        MAP_RECT.left,
        MAP_RECT.top,
        fitted_w,
        fitted_h,
    )


def max_map_scroll_x() -> int:
    return max(0, BACKGROUND_RECT.width - MAP_RECT.width)


def max_map_scroll_y() -> int:
    return max(0, BACKGROUND_RECT.height - MAP_RECT.height)


def clamp_map_scroll() -> None:
    global MAP_SCROLL_X, MAP_SCROLL_Y
    MAP_SCROLL_X = max(0, min(MAP_SCROLL_X, max_map_scroll_x()))
    MAP_SCROLL_Y = max(0, min(MAP_SCROLL_Y, max_map_scroll_y()))


def pan_map(delta_x: int = 0, delta_y: int = 0) -> None:
    global MAP_SCROLL_X, MAP_SCROLL_Y
    MAP_SCROLL_X += delta_x
    MAP_SCROLL_Y += delta_y
    clamp_map_scroll()


def load_background_image() -> None:
    global BACKGROUND_RECT, BACKGROUND_SURFACE, MAP_SCROLL_X, MAP_SCROLL_Y
    if not USE_BACKGROUND_IMAGE or not BACKGROUND_IMAGE_PATH.exists():
        BACKGROUND_SURFACE = None
        BACKGROUND_RECT = MAP_RECT.copy()
        MAP_SCROLL_X = 0
        MAP_SCROLL_Y = 0
        return
    raw = pygame.image.load(str(BACKGROUND_IMAGE_PATH)).convert()
    BACKGROUND_RECT = fit_rect_to_map_area(raw.get_size())
    BACKGROUND_SURFACE = pygame.transform.smoothscale(raw, BACKGROUND_RECT.size)
    MAP_SCROLL_X = min(max_map_scroll_x() // 2, max_map_scroll_x())
    MAP_SCROLL_Y = 0


def geo_to_screen(lat: float, lon: float) -> tuple[int, int]:
    rect = map_projection_rect()
    map_w = rect.width
    map_h = rect.height
    scroll_x = MAP_SCROLL_X if BACKGROUND_SURFACE else 0
    scroll_y = MAP_SCROLL_Y if BACKGROUND_SURFACE else 0
    if BACKGROUND_SURFACE:
        x_norm, y_norm = robinson_normalized(lat, lon)
        x = rect.left + ((x_norm + 1) / 2) * map_w - scroll_x + MAP_OVERLAY_X_OFFSET
        y = rect.top + ((1 - y_norm) / 2) * map_h - scroll_y + MAP_OVERLAY_Y_OFFSET
        return round(x), round(y)
    x = rect.left + ((normalized_delta_lon(lon) + 180) / 360) * map_w - scroll_x + MAP_OVERLAY_X_OFFSET
    max_y = mercator_y(MAX_LATITUDE)
    min_y = mercator_y(MIN_LATITUDE)
    y = rect.top + ((max_y - mercator_y(lat)) / (max_y - min_y)) * map_h
    return round(x), round(y)


def node_to_screen(name: str) -> tuple[int, int]:
    node = MAP_NODES[name]
    return geo_to_screen(node.lat, node.lon)


def port_at_position(mouse_pos: tuple[int, int], radius: int = 18) -> str | None:
    closest_name = None
    closest_distance = radius + 1
    for name in MAP_NODES:
        distance = math.dist(mouse_pos, node_to_screen(name))
        if distance <= radius and distance < closest_distance:
            closest_name = name
            closest_distance = distance
    return closest_name


def robinson_y_to_lat(y_norm: float) -> float:
    sign = 1 if y_norm >= 0 else -1
    target = abs(y_norm)
    for idx in range(len(ROBINSON_TABLE) - 1):
        lower_lat, _, lower_y = ROBINSON_TABLE[idx]
        upper_lat, _, upper_y = ROBINSON_TABLE[idx + 1]
        if lower_y <= target <= upper_y:
            t = 0 if upper_y == lower_y else (target - lower_y) / (upper_y - lower_y)
            return sign * (lower_lat + (upper_lat - lower_lat) * t)
    return sign * 90.0


def screen_to_geo(pos: tuple[int, int]) -> tuple[float, float]:
    rect = map_projection_rect()
    scroll_x = MAP_SCROLL_X if BACKGROUND_SURFACE else 0
    scroll_y = MAP_SCROLL_Y if BACKGROUND_SURFACE else 0
    x = pos[0] - rect.left + scroll_x - MAP_OVERLAY_X_OFFSET
    y = pos[1] - rect.top + scroll_y - MAP_OVERLAY_Y_OFFSET
    if BACKGROUND_SURFACE:
        x_norm = (x / rect.width) * 2 - 1
        y_norm = 1 - (y / rect.height) * 2
        lat = robinson_y_to_lat(y_norm)
        x_coeff, _ = robinson_lookup(lat)
        delta_lon = 0 if x_coeff == 0 else (x_norm / x_coeff) * 180
        lon = ((delta_lon + LONDON_MERIDIAN + 180) % 360) - 180
        return round(lat, 2), round(lon, 2)
    lon = ((x / rect.width) * 360 - 180 + LONDON_MERIDIAN + 180) % 360 - 180
    max_y = mercator_y(MAX_LATITUDE)
    min_y = mercator_y(MIN_LATITUDE)
    merc_y = max_y - (y / rect.height) * (max_y - min_y)
    lat = math.degrees(2 * math.atan(math.exp(merc_y)) - math.pi / 2)
    return round(lat, 2), round(lon, 2)


def move_port_to_screen(name: str, pos: tuple[int, int]) -> None:
    lat, lon = screen_to_geo(pos)
    node = MAP_NODES[name]
    node.lat = max(-89.0, min(89.0, lat))
    node.lon = lon


def port_geo_coords_source() -> str:
    lines = ["PORT_GEO_COORDS = {"]
    for name in NOTEBOOK_PORT_ORDER:
        node = MAP_NODES[name]
        lines.append(f'    "{name}": ({node.lat:.2f}, {node.lon:.2f}),')
    lines.append("}")
    return "\n".join(lines)


def write_back_port_geo_coords() -> None:
    source_path = Path(__file__)
    source = source_path.read_text(encoding="utf-8")
    replacement = port_geo_coords_source()
    updated, count = re.subn(
        r"PORT_GEO_COORDS = \{.*?\n\}",
        replacement,
        source,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Could not find PORT_GEO_COORDS block to update")
    source_path.write_text(updated, encoding="utf-8")


def export_port_geo_coords(path: Path = Path("port_geo_coords_edited.py"), write_back: bool = False) -> None:
    lines = [
        "# Generated by ABCDE port edit mode.",
        port_geo_coords_source(),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if write_back:
        write_back_port_geo_coords()


def make_players() -> list[PlayerState]:
    players = []
    for country in EMPIRE_ORDER:
        owned_ports = [port for port in colonies if port.owner == country]
        owned_port_names = {port.name for port in owned_ports}
        for node in MAP_NODES.values():
            if node.owner == country and canonical_notebook_name(node.name) not in owned_port_names:
                owned_ports.append(node)
        capital = CAPITALS[country]
        ships = [
            Ship("pirate" if country == "Pirates" else f"{country} merchant 1", country, capital, "Pirate" if country == "Pirates" else "Merchant"),
            Ship("pirate" if country == "Pirates" else f"{country} warship 1", country, capital, "Pirate" if country == "Pirates" else "Warship"),
            Ship("pirate" if country == "Pirates" else f"{country} warship 2", country, capital, "Pirate" if country == "Pirates" else "Warship"),
            Ship("pirate" if country == "Pirates" else f"{country} merchant 2", country, capital, "Pirate" if country == "Pirates" else "Merchant"),
        ]
        players.append(
            PlayerState(
                country=country,
                money=450,
                resources=initial_resources(),
                ports=owned_ports,
                ships=ships,
                trade_cards=[],
                licenses={},
            )
        )
    return players


def initial_resources() -> dict[str, int]:
    return dict(INITIAL_RESOURCES)


def refresh_player_ports(players: list[PlayerState]) -> None:
    for player in players:
        player.ports = []
        seen = set()
        for node in MAP_NODES.values():
            if node.owner == player.country and node.name not in seen:
                player.ports.append(node)
                seen.add(node.name)


def randomize_game() -> list[PlayerState]:
    target_port_counts = {country: len(NOTEBOOK_PORT_ORDER) // len(EMPIRE_ORDER) for country in EMPIRE_ORDER}
    for node in MAP_NODES.values():
        node.entry_mode = "default"
        node.entry_countries.clear()
        node.free_entry_countries.clear()
        if node.kind == "capital":
            node.owner = next(country for country, capital in CAPITALS.items() if capital == node.name)
            continue
        node.owner = None

    assignable_nodes = [node for node in MAP_NODES.values() if node.kind != "capital"]
    random.shuffle(assignable_nodes)
    owner_pool: list[str] = []
    for country in EMPIRE_ORDER:
        already_owned = sum(1 for node in MAP_NODES.values() if node.owner == country)
        owner_pool.extend([country] * max(0, target_port_counts[country] - already_owned))
    while len(owner_pool) < len(assignable_nodes):
        owner_pool.append(EMPIRE_ORDER[len(owner_pool) % len(EMPIRE_ORDER)])
    if len(owner_pool) > len(assignable_nodes):
        owner_pool = owner_pool[: len(assignable_nodes)]
    for node, owner in zip(assignable_nodes, owner_pool):
        node.owner = owner

    players = [
        PlayerState(country=country, money=450, resources=initial_resources(), ports=[], ships=[], trade_cards=[], licenses={})
        for country in EMPIRE_ORDER
    ]
    refresh_player_ports(players)
    for player in players:
        possible_locations = [port.name for port in player.ports] or [CAPITALS[player.country]]
        for index in range(4):
            kind = "Pirate" if player.country == "Pirates" else ("Merchant" if index in (0, 3) else "Warship")
            name = "pirate" if player.country == "Pirates" else f"{player.country} {kind.lower()} {index + 1}"
            player.ships.append(
                Ship(
                    name=name,
                    owner=player.country,
                    location=random.choice(possible_locations),
                    kind=kind,
                )
            )
    return players


def player_by_country(players: list[PlayerState], country: str | None) -> PlayerState | None:
    if not country:
        return None
    for player in players:
        if player.country == country:
            return player
    return None


def tax_income_for_player(player: PlayerState) -> int:
    base_tax = sum(port.tax or 0 for port in player.ports)
    if player.country == "United Kingdom":
        base_tax += 10 * sum(1 for port in player.ports if port.kind in ("port", "choking"))
    return base_tax


def collect_taxes(players: list[PlayerState], round_number: int) -> dict[str, int]:
    income_by_country = {}
    for player in players:
        income = tax_income_for_player(player)
        player.money += income
        income_by_country[player.country] = income
        if income:
            record_transaction(player, round_number, income, "tax income")
    return income_by_country


def record_transaction(player: PlayerState | None, round_number: int, amount: int, detail: str) -> None:
    if not player:
        return
    sign = "+" if amount > 0 else ""
    player.transactions.append(f"R{round_number} {sign}${amount}: {detail}")
    if len(player.transactions) > 120:
        del player.transactions[: len(player.transactions) - 120]


def ship_upkeep_due(ship: Ship) -> int:
    if ship.kind == "Warship":
        return ship.distance_since_upkeep * 3
    if ship.kind == "Pirate":
        return ship.distance_since_upkeep
    return ship.distance_since_upkeep


def charge_ship_arrival_upkeep(
    ship: Ship,
    players: list[PlayerState],
    round_number: int,
    history_events: list[HistoryEvent] | None = None,
) -> int:
    cost = ship_upkeep_due(ship)
    player = player_by_country(players, ship.owner)
    distance = ship.distance_since_upkeep
    if player and cost:
        player.money -= cost
        record_transaction(player, round_number, -cost, f"voyage upkeep {distance} distance to {display_place_name(ship.location)}")
    if history_events and distance:
        history_events.append(
            HistoryEvent(
                round_number=round_number,
                kind="maintenance",
                title=f"{ship.owner} paid voyage upkeep",
                details=[f"{ship.name}: {distance} distance, cost ${cost}", f"Arrived at {display_place_name(ship.location)}"],
            )
        )
    ship.distance_since_upkeep = 0
    ship.last_port_round = round_number
    return cost


def collect_ship_maintenance(players: list[PlayerState], round_number: int) -> dict[str, int]:
    costs = {}
    for player in players:
        cost = sum(5 for ship in player.ships if ship.kind != "Merchant")
        player.money -= cost
        costs[player.country] = cost
        if cost:
            record_transaction(player, round_number, -cost, "non-merchant upkeep")
    return costs


def clamp_non_gold_resources(player: PlayerState) -> None:
    non_gold = [resource for resource in RESOURCE_ORDER if resource != "gold"]
    total = sum(player.resources.get(resource, 0) for resource in non_gold)
    if total <= 10:
        return
    for resource in non_gold:
        while player.resources.get(resource, 0) > 0 and total > 10:
            player.resources[resource] -= 1
            total -= 1


def collect_factory_resources(players: list[PlayerState]) -> dict[str, dict[str, int]]:
    gains_by_country = {player.country: {resource: 0 for resource in RESOURCE_ORDER} for player in players}
    factory_nodes_by_owner: dict[str, list[MapNode]] = defaultdict(list)
    for node in MAP_NODES.values():
        if node.factory_owner and node.factory_level:
            factory_nodes_by_owner[node.factory_owner].append(node)
    oil_bonus_owners: set[str] = set()
    fertilizer_bonus_owners: set[str] = set()
    for player in players:
        owned_factories = factory_nodes_by_owner.get(player.country, [])
        if player.resources.get("oil", 0) > 0 and any(node.resource in ("metal", "gold") for node in owned_factories):
            player.resources["oil"] -= 1
            oil_bonus_owners.add(player.country)
        if player.resources.get("fertilizer", 0) > 0 and any(node.resource in ("wood", "sugar") for node in owned_factories):
            player.resources["fertilizer"] -= 1
            fertilizer_bonus_owners.add(player.country)
    for node in MAP_NODES.values():
        if not node.factory_owner or not node.factory_level:
            continue
        if node.resource not in RESOURCE_ORDER or node.resource == "shipyard":
            continue
        player = player_by_country(players, node.factory_owner)
        if not player:
            continue
        amount = 2 if node.factory_level == "red" else 1
        if player.country in fertilizer_bonus_owners and node.resource in ("wood", "sugar"):
            amount += 2
        player.resources[node.resource] = player.resources.get(node.resource, 0) + amount
        gains_by_country[player.country][node.resource] += amount
        if player.country in oil_bonus_owners and node.resource in ("metal", "gold"):
            player.resources["metal"] = player.resources.get("metal", 0) + 1
            gains_by_country[player.country]["metal"] += 1
    for player in players:
        clamp_non_gold_resources(player)
    return gains_by_country


def resource_gain_lines(gains: dict[str, dict[str, int]], country: str) -> list[str]:
    country_gains = gains.get(country, {})
    lines = [
        f"{RESOURCE_LABELS[resource]} +{amount}"
        for resource, amount in country_gains.items()
        if amount
    ]
    return lines or ["No factory resource gain"]


def player_for_ship(players: list[PlayerState], ship: Ship) -> PlayerState | None:
    for player in players:
        if ship in player.ships:
            return player
    return None


def distance_point_to_segment(
    point: tuple[int, int],
    start: tuple[int, int],
    end: tuple[int, int],
) -> float:
    px, py = point
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    if dx == 0 and dy == 0:
        return math.dist(point, start)
    t = max(0.0, min(1.0, ((px - sx) * dx + (py - sy) * dy) / (dx * dx + dy * dy)))
    closest = (sx + t * dx, sy + t * dy)
    return math.dist(point, closest)


def find_attack_prompt(
    moved_ship: Ship,
    players: list[PlayerState],
    old_pos: tuple[int, int],
    new_pos: tuple[int, int],
) -> AttackPrompt | None:
    if not ship_is_enroute(moved_ship):
        port = MAP_NODES.get(moved_ship.location)
        if port and port.owner and port.owner != moved_ship.owner:
            if not can_attack_defender(moved_ship, port):
                return None
            return AttackPrompt(moved_ship, port, "entered enemy port", moved_ship.location)
    for player in players:
        if player.country == moved_ship.owner:
            continue
        for enemy_ship in player.ships:
            if enemy_ship is moved_ship:
                continue
            if not ships_can_fight(moved_ship, enemy_ship, players):
                continue
            if not ship_is_enroute(moved_ship) and not ship_is_enroute(enemy_ship) and moved_ship.location == enemy_ship.location:
                defender = attack_defender_for_target(moved_ship, enemy_ship)
                if not can_attack_defender(moved_ship, defender):
                    continue
                location = defender.name if isinstance(defender, MapNode) else moved_ship.location
                return AttackPrompt(moved_ship, defender, "same position", location)
            enemy_pos = ship_screen_position(enemy_ship)
            if distance_point_to_segment(enemy_pos, old_pos, new_pos) <= 18:
                defender = attack_defender_for_target(moved_ship, enemy_ship)
                if not can_attack_defender(moved_ship, defender):
                    continue
                location = defender.name if isinstance(defender, MapNode) else (moved_ship.location if not ship_is_enroute(moved_ship) else None)
                return AttackPrompt(moved_ship, defender, "passed enemy ship", location)
    return None


def ships_at_location(players: list[PlayerState], location: str, owner: str | None = None) -> list[Ship]:
    ships = []
    for player in players:
        if owner is not None and player.country != owner:
            continue
        for ship in player.ships:
            if not ship_is_enroute(ship) and ship.location == location:
                ships.append(ship)
    return ships


def attack_side_entities(prompt: AttackPrompt, players: list[PlayerState]) -> tuple[list[object], list[object]]:
    return [prompt.attacker], [prompt.defender]


def base_entity_power(entity: object) -> int:
    if isinstance(entity, MapNode):
        return 3 if entity.owner == "Pirates" else 4
    if isinstance(entity, Ship):
        if entity.kind == "Merchant":
            return 1 if entity.trade_card else 2
        if entity.kind == "Pirate":
            return 2
        if entity.kind == "Warship":
            return 3
    return 1


def entity_power(
    entity: object,
    power_penalties: dict[int, int] | None = None,
    players: list[PlayerState] | None = None,
    round_number: int | None = None,
) -> int:
    penalty = (power_penalties or {}).get(id(entity), 0)
    bonus = 0
    owner = entity_owner(entity)
    if players is not None and round_number is not None:
        player = player_by_country(players, owner)
        if player and player.oil_power_until >= round_number:
            bonus = 1
    return max(1, base_entity_power(entity) + bonus - penalty)


def entity_owner(entity: object) -> str | None:
    if isinstance(entity, Ship):
        return entity.owner
    if isinstance(entity, MapNode):
        return entity.owner
    return None


def entity_label(entity: object) -> str:
    if isinstance(entity, Ship):
        return f"{ship_kind_label(entity)} ({entity.owner})"
    if isinstance(entity, MapNode):
        return f"Port {display_place_name(entity.name)} ({entity.owner})"
    return str(entity)


def remove_battle_entity(entity: object, players: list[PlayerState]) -> None:
    if isinstance(entity, Ship):
        owner = player_for_ship(players, entity)
        if owner and entity in owner.ships:
            owner.ships.remove(entity)


def transfer_stolen_trade_card(ship: Ship, old_owner: PlayerState, pirate_player: PlayerState) -> str | None:
    card = ship.trade_card
    if not card:
        return None
    if card in old_owner.trade_cards:
        old_owner.trade_cards.remove(card)
    if card not in pirate_player.trade_cards:
        pirate_player.trade_cards.append(card)
    card.stolen_from = old_owner.country
    card.status = "robbed"
    return f"Stolen trade: {card.start} -> {card.end} ${card.profit}"


def convert_robbed_merchant_to_pirate(ship: Ship, players: list[PlayerState]) -> str | None:
    old_owner = player_for_ship(players, ship)
    pirate_player = player_by_country(players, "Pirates")
    if not old_owner or not pirate_player:
        return None
    stolen_detail = transfer_stolen_trade_card(ship, old_owner, pirate_player)
    if ship in old_owner.ships:
        old_owner.ships.remove(ship)
    ship.owner = "Pirates"
    ship.kind = "Pirate"
    ship.name = "pirate"
    pirate_player.ships.append(ship)
    return stolen_detail or "Empty merchant converted to pirate"


def transfer_robbed_goods_to_privateer(defender: Ship, attacker: Ship, players: list[PlayerState]) -> str | None:
    old_owner = player_for_ship(players, defender)
    attacker_player = player_for_ship(players, attacker)
    if not old_owner or not attacker_player:
        return None
    card = defender.trade_card
    if not card:
        return "Empty merchant robbed"
    if attacker.trade_card:
        return "Robbed merchant had cargo, but attacker is already loaded"
    if card in old_owner.trade_cards:
        old_owner.trade_cards.remove(card)
    if card not in attacker_player.trade_cards:
        attacker_player.trade_cards.append(card)
    card.stolen_from = old_owner.country
    card.status = "declared"
    attacker.trade_card = card
    attacker.trade_destination = defender.trade_destination
    defender.trade_card = None
    defender.trade_destination = None
    return f"Stolen goods: {card.start} -> {card.end} ${card.profit}"


def prompt_has_defenders(prompt: AttackPrompt, players: list[PlayerState]) -> bool:
    if isinstance(prompt.defender, MapNode):
        if prompt.defender.owner == prompt.attacker.owner:
            return False
        if prompt.defender.owner:
            return True
    if isinstance(prompt.defender, Ship):
        return player_for_ship(players, prompt.defender) is not None
    return False


def prompt_attacker_alive(prompt: AttackPrompt, players: list[PlayerState]) -> bool:
    return player_for_ship(players, prompt.attacker) is not None


def can_continue_attack(prompt: AttackPrompt, players: list[PlayerState]) -> bool:
    if combat_action(prompt)[0] == "rob" and prompt.attacker.kind == "Merchant":
        return False
    return prompt_attacker_alive(prompt, players) and prompt_has_defenders(prompt, players)


def combat_action(prompt: AttackPrompt) -> tuple[str, str, bool]:
    defender_owner = entity_owner(prompt.defender)
    if isinstance(prompt.defender, MapNode):
        return "war", "Attack", True
    if (
        isinstance(prompt.defender, Ship)
        and prompt.defender.kind == "Merchant"
        and (prompt.attacker.owner == "Pirates" or prompt.attacker.kind in ("Pirate", "Merchant"))
    ):
        return "rob", "Rob", False
    if prompt.attacker.kind == "Warship" and defender_owner == "Pirates":
        return "enforce", "Enforce", False
    return "war", "Attack", True


def attack_action_label(attacker: Ship, defender: object) -> str:
    return combat_action(AttackPrompt(attacker, defender, "preview"))[1]


def port_guard_for_target(attacker: Ship, target: Ship) -> MapNode | None:
    if ship_is_enroute(target):
        return None
    port = MAP_NODES.get(target.location)
    if port and port.owner == "Pirates":
        return None
    if port and port.owner and port.owner != attacker.owner:
        return port
    return None


def attack_defender_for_target(attacker: Ship, target: Ship) -> object:
    return port_guard_for_target(attacker, target) or target


def can_attack_defender(attacker: Ship, defender: object) -> bool:
    if isinstance(defender, MapNode) and defender.kind == "capital" and defender.owner != attacker.owner:
        return False
    return True


def defender_survived_same_side(defender: object, original_owner: str | None, players: list[PlayerState]) -> bool:
    if isinstance(defender, MapNode):
        return defender.owner == original_owner
    if isinstance(defender, Ship):
        return player_for_ship(players, defender) is not None and defender.owner == original_owner
    return False


def resolve_attack(
    prompt: AttackPrompt,
    players: list[PlayerState],
    power_penalties: dict[int, int] | None = None,
    round_number: int | None = None,
) -> dict[str, int | str | bool]:
    attacker_roll = defender_roll = 0
    attacker_power = defender_power = 0
    action_kind, action_label, is_war = combat_action(prompt)
    attacker_entities, defender_entities = attack_side_entities(prompt, players)
    defender_entity = defender_entities[0]
    defender_original_owner = entity_owner(defender_entity)
    if round_number is not None:
        attacker_player = player_by_country(players, prompt.attacker.owner)
        if prompt.attacker_uses_oil and attacker_player and attacker_player.resources.get("oil", 0) > 0:
            attacker_player.resources["oil"] -= 1
            attacker_player.oil_power_until = max(attacker_player.oil_power_until, round_number)
        defender_player = player_by_country(players, entity_owner(defender_entity))
        if defender_player and defender_player.resources.get("oil", 0) > 0 and defender_player.oil_power_until < round_number:
            defender_player.resources["oil"] -= 1
            defender_player.oil_power_until = round_number
    while attacker_power == defender_power:
        attacker_roll = random.randint(1, 6)
        defender_roll = random.randint(1, 6)
        attacker_entity_power = entity_power(attacker_entities[0], power_penalties, players, round_number)
        if action_kind == "rob" and prompt.attacker.kind == "Merchant":
            attacker_entity_power = 1
        attacker_power = attacker_roll * attacker_entity_power
        defender_power = defender_roll * entity_power(defender_entity, power_penalties, players, round_number)
    attacker_wins = attacker_power > defender_power
    loser = defender_entities[-1] if attacker_wins else attacker_entities[-1]
    defender_owner = entity_owner(prompt.defender) or "Unknown"
    attacker_entities_label = ", ".join(entity_label(entity) for entity in attacker_entities)
    defender_entities_label = ", ".join(entity_label(entity) for entity in defender_entities)
    loser_label = entity_label(loser)
    stolen_detail = None
    converted_ship = False
    if action_kind == "rob" and attacker_wins and isinstance(loser, Ship) and loser is prompt.defender:
        if prompt.attacker.owner == "Pirates" or prompt.attacker.kind == "Pirate":
            stolen_detail = convert_robbed_merchant_to_pirate(loser, players)
            converted_ship = True
            loser_label = "Merchant converted to Pirates"
        else:
            stolen_detail = transfer_robbed_goods_to_privateer(loser, prompt.attacker, players)
            loser_label = "Goods seized by privateer"
    else:
        remove_battle_entity(loser, players)
    if attacker_wins and isinstance(loser, MapNode):
        loser.owner = prompt.attacker.owner
        if loser.factory_level:
            loser.factory_owner = prompt.attacker.owner
        refresh_player_ports(players)
    defender_weakened = False
    if (
        not attacker_wins
        and power_penalties is not None
        and defender_survived_same_side(defender_entity, defender_original_owner, players)
    ):
        current_penalty = power_penalties.get(id(defender_entity), 0)
        max_penalty = max(0, base_entity_power(defender_entity) - 1)
        new_penalty = min(max_penalty, current_penalty + 1)
        power_penalties[id(defender_entity)] = new_penalty
        defender_weakened = new_penalty > current_penalty
    return {
        "action_kind": action_kind,
        "action_label": action_label,
        "is_war": is_war,
        "attacker": prompt.attacker.owner,
        "defender": defender_owner,
        "attacker_roll": attacker_roll,
        "defender_roll": defender_roll,
        "attacker_power": attacker_power,
        "defender_power": defender_power,
        "winner": prompt.attacker.owner if attacker_wins else entity_owner(prompt.defender) or "Unknown",
        "lost_entity": loser_label,
        "attacker_entities": attacker_entities_label,
        "defender_entities": defender_entities_label,
        "can_continue": bool(isinstance(prompt.defender, MapNode) and prompt.defender.owner != prompt.attacker.owner),
        "converted_ship": converted_ship,
        "stolen_trade": stolen_detail or "",
        "defender_weakened": defender_weakened,
        "defender_effective_power": entity_power(defender_entity, power_penalties, players, round_number),
        "captured_port": loser.name if attacker_wins and isinstance(loser, MapNode) else "",
    }


def draw_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    pos: tuple[int, int],
    color: tuple[int, int, int] = TEXT,
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(topleft=pos)
    surface.blit(rendered, rect)
    return rect


def draw_wrapped_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    rect: pygame.Rect,
    color: tuple[int, int, int] = TEXT_MUTED,
    line_gap: int = 4,
) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= rect.width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = rect.top
    for line in lines:
        draw_text(surface, font, line, (rect.left, y), color)
        y += font.get_height() + line_gap
        if y > rect.bottom:
            break
    return y


def draw_world(surface: pygame.Surface) -> None:
    surface.fill(OCEAN)
    if BACKGROUND_SURFACE:
        previous_clip = surface.get_clip()
        surface.set_clip(MAP_RECT)
        surface.blit(BACKGROUND_SURFACE, (BACKGROUND_RECT.left - MAP_SCROLL_X, BACKGROUND_RECT.top - MAP_SCROLL_Y))
        pygame.draw.line(
            surface,
            (87, 138, 171),
            (BACKGROUND_RECT.left + BACKGROUND_RECT.width // 2 - MAP_SCROLL_X, BACKGROUND_RECT.top - MAP_SCROLL_Y),
            (BACKGROUND_RECT.left + BACKGROUND_RECT.width // 2 - MAP_SCROLL_X, BACKGROUND_RECT.bottom - MAP_SCROLL_Y),
            1,
        )
        surface.set_clip(previous_clip)
        pygame.draw.rect(surface, (114, 172, 203), MAP_RECT, 1)
        return

    for y in range(MAP_RECT.top, MAP_RECT.bottom, 18):
        shade = OCEAN if y % 36 else OCEAN_DEEP
        pygame.draw.line(surface, shade, (MAP_RECT.left, y), (MAP_RECT.right, y), 1)

    pygame.draw.rect(surface, (114, 172, 203), MAP_RECT, 1)
    for lon in range(-180, 181, 30):
        x, _ = geo_to_screen(0, lon)
        pygame.draw.line(surface, (173, 213, 233), (x, MAP_RECT.top), (x, MAP_RECT.bottom), 1)
    for lat in range(-60, 76, 15):
        _, y = geo_to_screen(lat, LONDON_MERIDIAN)
        pygame.draw.line(surface, (173, 213, 233), (MAP_RECT.left, y), (MAP_RECT.right, y), 1)

    pygame.draw.line(
        surface,
        (87, 138, 171),
        (MAP_RECT.left + MAP_RECT.width // 2, MAP_RECT.top),
        (MAP_RECT.left + MAP_RECT.width // 2, MAP_RECT.bottom),
        1,
    )

    continents_lonlat = [
        [
            (-170, 68), (-162, 60), (-153, 58), (-160, 55), (-170, 54), (-158, 58), (-150, 62),
            (-137, 58), (-126, 50), (-124, 42), (-117, 33), (-108, 25),
            (-97, 18), (-90, 18), (-84, 10), (-77, 8), (-76, 18), (-81, 26), (-72, 42),
            (-57, 50), (-60, 57), (-77, 63), (-95, 70), (-125, 72), (-150, 72),
        ],
        [(-74, 12), (-67, 5), (-78, -8), (-76, -18), (-72, -33), (-70, -52), (-59, -55), (-51, -40), (-45, -22), (-35, -8), (-48, 5), (-60, 10)],
        [(-53, 83), (-28, 78), (-20, 70), (-34, 61), (-48, 60), (-61, 66)],
        [
            (-11, 36), (-5, 43), (8, 58), (25, 61), (38, 52), (31, 41), (25, 35), (10, 36),
            (5, 43), (-5, 43), (-10, 39),
        ],
        [
            (-17, 32), (-5, 37), (8, 36), (18, 31), (31, 31), (40, 18), (51, 11), (43, -12),
            (35, -24), (23, -35), (17, -35), (10, -19), (2, -5), (-10, 5), (-17, 18),
        ],
        [
            (32, 72), (58, 72), (82, 66), (105, 58), (133, 50), (151, 43), (163, 58),
            (178, 66), (176, 54), (160, 48), (145, 31),
            (123, 21), (108, 15), (105, 0), (96, -6), (78, 7), (67, 23), (48, 29),
            (40, 40), (32, 50),
        ],
        [(44, 30), (58, 25), (61, 16), (52, 12), (44, 19)],
        [(68, 24), (82, 22), (89, 10), (80, 7), (72, 15)],
        [(95, 7), (105, 6), (116, 1), (122, -8), (111, -10), (101, -3)],
        [(113, -11), (126, -13), (138, -17), (149, -25), (153, -34), (144, -39), (131, -35), (116, -29), (112, -20)],
        [(166, -34), (174, -37), (179, -42), (175, -47), (168, -46), (166, -40)],
        [(172, -41), (178, -44), (179, -47), (173, -46)],
        [(128, 44), (143, 45), (146, 36), (132, 31)],
        [(155, 52), (164, 58), (163, 47), (158, 43)],
        [(141, 54), (145, 49), (144, 45), (139, 47)],
        [(48, -13), (51, -19), (49, -25), (44, -22)],
        [(-180, -60), (-150, -56), (-118, -58), (-82, -56), (-45, -57), (-12, -55), (26, -58), (62, -56), (101, -59), (142, -56), (180, -58), (180, -60), (-180, -60)],
    ]
    for polygon in continents_lonlat:
        points = [geo_to_screen(lat, lon) for lon, lat in polygon]
        pygame.draw.polygon(surface, LAND_DARK, [(x + 3, y + 3) for x, y in points])
        pygame.draw.polygon(surface, LAND, points)
        pygame.draw.lines(surface, COAST, True, points, 2)

    label_font = pygame.font.SysFont("arial", 17, True)
    labels = [
        ("North America", 46, -108),
        ("South America", -24, -58),
        ("Europe", 49, 10),
        ("Africa", 2, 20),
        ("Asia", 38, 88),
        ("Oceania", -23, 137),
        ("London meridian", 69, LONDON_MERIDIAN + 3),
    ]
    for label, lat, lon in labels:
        draw_text(surface, label_font, label, geo_to_screen(lat, lon), TEXT_MUTED)


def draw_port_based_world_outline(surface: pygame.Surface, font: pygame.font.Font) -> None:
    for group in PORT_OUTLINE_GROUPS:
        points = [node_to_screen(name) for name in group]
        if len(points) < 2:
            continue
        pygame.draw.lines(surface, LAND_DARK, False, [(x + 2, y + 2) for x, y in points], 5)
        pygame.draw.lines(surface, LAND, False, points, 4)
        pygame.draw.lines(surface, COAST, False, points, 1)

    for name in ["North America", "South America", "Europe", "Africa", "Asia", "Oceania"]:
        label_positions = {
            "North America": (47, -105),
            "South America": (-23, -58),
            "Europe": (52, 10),
            "Africa": (3, 18),
            "Asia": (35, 92),
            "Oceania": (-24, 138),
        }
        draw_text(surface, font, name, geo_to_screen(*label_positions[name]), TEXT_MUTED)


def course_endpoints() -> list[tuple[str, str, int]]:
    grouped_courses: dict[tuple[str, str], list[int]] = defaultdict(list)
    first_direction: dict[tuple[str, str], tuple[str, str]] = {}
    for start, end, distance in NOTEBOOK_COURSES:
        key = tuple(sorted((start, end)))
        grouped_courses[key].append(distance)
        first_direction.setdefault(key, (start, end))
    endpoints = []
    for key, distances in grouped_courses.items():
        sorted_distances = sorted(distances)
        middle = len(sorted_distances) // 2
        if len(sorted_distances) % 2:
            distance = sorted_distances[middle]
        else:
            distance = math.floor((sorted_distances[middle - 1] + sorted_distances[middle]) / 2)
        start, end = first_direction[key]
        endpoints.append((start, end, distance))
    return endpoints


def course_graph() -> dict[str, list[tuple[str, int]]]:
    graph: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for start, end, distance in course_endpoints():
        graph[start].append((end, distance))
        graph[end].append((start, distance))
    for neighbors in graph.values():
        neighbors.sort(key=lambda item: item[0])
    return dict(graph)


def course_distance_between(start: str, end: str) -> int | None:
    for neighbor, distance in COURSE_GRAPH.get(start, []):
        if neighbor == end:
            return distance
    return None


COURSE_GRAPH = course_graph()


def ports_within_course_distance(center: str, max_distance: int) -> set[str]:
    found = {center}
    frontier = [(center, 0)]
    while frontier:
        port, distance_so_far = frontier.pop(0)
        for neighbor, distance in COURSE_GRAPH.get(port, []):
            new_distance = distance_so_far + distance
            if new_distance <= max_distance and neighbor not in found:
                found.add(neighbor)
                frontier.append((neighbor, new_distance))
    return found

GOODS_LAND_ROUTES = {
    tuple(sorted(("Acapulco", "Veracruz"))): 2,
    tuple(sorted(("Panama_City", "Colon"))): 1,
    tuple(sorted(("Murmansk", "St_Pertersburg"))): 1,
    tuple(sorted(("Suez_City", "Port_Said"))): 1,
}


def curve_points(a: tuple[int, int], b: tuple[int, int], bend: float = 0.18) -> list[tuple[int, int]]:
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    distance = math.hypot(dx, dy) or 1
    normal_x = -dy / distance
    normal_y = dx / distance
    curve_height = min(70, max(18, distance * bend))
    control = ((ax + bx) / 2 + normal_x * curve_height, (ay + by) / 2 + normal_y * curve_height)
    points = []
    for step in range(25):
        t = step / 24
        one_minus = 1 - t
        x = one_minus * one_minus * ax + 2 * one_minus * t * control[0] + t * t * bx
        y = one_minus * one_minus * ay + 2 * one_minus * t * control[1] + t * t * by
        points.append((round(x), round(y)))
    return points


def draw_wrapped_curve(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    a: tuple[int, int],
    b: tuple[int, int],
    width: int,
) -> list[tuple[int, int]]:
    rect = map_projection_rect()
    map_w = rect.width
    ax, ay = a
    bx, by = b
    if abs(ax - bx) <= map_w / 2:
        points = curve_points(a, b)
        pygame.draw.lines(surface, color, False, points, width)
        return points
    if ax < bx:
        ax += map_w
    else:
        bx += map_w
    points = curve_points((ax, ay), (bx, by))
    pygame.draw.lines(surface, color, False, points, width)
    wrapped_points = [(x - map_w, y) for x, y in points]
    pygame.draw.lines(surface, color, False, wrapped_points, width)
    visible_points = [point for point in points if MAP_RECT.left <= point[0] <= MAP_RECT.right]
    visible_points += [point for point in wrapped_points if MAP_RECT.left <= point[0] <= MAP_RECT.right]
    return visible_points or wrapped_points


def sea_waypoints(start: str, end: str) -> list[tuple[float, float]]:
    if (start, end) in SEA_ROUTE_WAYPOINTS:
        return SEA_ROUTE_WAYPOINTS[(start, end)]
    if (end, start) in SEA_ROUTE_WAYPOINTS:
        return list(reversed(SEA_ROUTE_WAYPOINTS[(end, start)]))
    return []


def route_geo_points(start: str, end: str) -> list[tuple[float, float]]:
    start_node = MAP_NODES[start]
    end_node = MAP_NODES[end]
    return [(start_node.lat, start_node.lon), *sea_waypoints(start, end), (end_node.lat, end_node.lon)]


def ship_speed(ship: Ship) -> int:
    return effective_ship_speed(ship, [])


def base_ship_speed(ship: Ship) -> int:
    if ship.owner == "Pirates":
        return 4
    if ship.kind == "Merchant":
        return 3
    return 2


def active_monsoon_ports(active_news: list[NewsEvent]) -> set[str]:
    ports: set[str] = set()
    for event in active_news:
        if event.kind == "monsoon":
            ports.update(event.ports)
    return ports


def active_plague_ports(active_news: list[NewsEvent]) -> set[str]:
    ports: set[str] = set()
    for event in active_news:
        if event.kind == "plague":
            ports.update(event.ports)
    return ports


def effective_ship_speed(ship: Ship, active_news: list[NewsEvent]) -> int:
    speed = base_ship_speed(ship)
    if ship.sugar_speed_active:
        speed += 1
    if ship.location in active_monsoon_ports(active_news):
        speed += 1 if ship.owner == "Pirates" or ship.kind == "Pirate" else 2
    return speed


def effective_ship_speed_for_players(ship: Ship, players: list[PlayerState], round_number: int, active_news: list[NewsEvent]) -> int:
    return effective_ship_speed(ship, active_news)


def ship_is_enroute(ship: Ship) -> bool:
    return ship.destination is not None


def player_has_license(
    country: str,
    license_key: str,
    players: list[PlayerState] | None = None,
    player: PlayerState | None = None,
) -> bool:
    if player and player.country == country:
        return license_key in player.licenses
    if players:
        owner = player_by_country(players, country)
        return bool(owner and license_key in owner.licenses)
    return False


def ship_has_license(
    ship: Ship,
    license_key: str,
    players: list[PlayerState] | None = None,
    player: PlayerState | None = None,
) -> bool:
    return player_has_license(ship.owner, license_key, players, player)


def ship_can_attack(
    ship: Ship,
    players: list[PlayerState] | None = None,
    player: PlayerState | None = None,
) -> bool:
    return ship.kind != "Merchant" or ship_has_license(ship, "pirate", players, player)


def ships_can_fight(attacker: Ship, target: Ship, players: list[PlayerState] | None = None) -> bool:
    if attacker.owner == target.owner:
        return False
    if attacker.kind == "Pirate" and target.kind == "Pirate":
        return False
    if attacker.kind == "Merchant":
        if not ship_has_license(attacker, "pirate", players):
            return False
        if target.kind != "Merchant":
            return False
        if port_guard_for_target(attacker, target):
            return False
    defender = attack_defender_for_target(attacker, target)
    if not can_attack_defender(attacker, defender):
        return False
    return True


def ship_kind_label(
    ship: Ship,
    players: list[PlayerState] | None = None,
    player: PlayerState | None = None,
) -> str:
    if ship.kind == "Merchant" and ship_has_license(ship, "pirate", players, player):
        suffix = " (*)" if ship.trade_card else " (x)"
        return f"Merchant{suffix}"
    suffix = " (+)" if ship.trade_card else ""
    return f"{ship.kind}{suffix}"


ENTRY_MODE_LABELS = {
    "default": "Default",
    "allow_only": "Accept selected",
    "reject_selected": "Reject selected",
    "reject_all": "Reject all",
    "open_all": "Open all",
}


def can_arrange_port(player: PlayerState, node: MapNode) -> bool:
    return node.owner == player.country and player.country != "Pirates"


def port_allows_ship_entry(
    node: MapNode,
    ship: Ship,
    players: list[PlayerState] | None = None,
    player: PlayerState | None = None,
) -> bool:
    if ship_has_license(ship, "smuggler", players, player):
        return True
    if ship.kind == "Merchant":
        return True
    if ship.owner == "Japan":
        return True
    if node.owner == "Pirates":
        return True
    if node.owner == ship.owner:
        return True
    mode = node.entry_mode
    if mode == "default" or mode == "open_all":
        return True
    if mode == "reject_all":
        return False
    if mode == "allow_only":
        return ship.owner in node.entry_countries
    if mode == "reject_selected":
        return ship.owner not in node.entry_countries
    return True


def can_ship_enter_port(
    ship: Ship,
    destination: str,
    active_news: list[NewsEvent] | None = None,
    players: list[PlayerState] | None = None,
    player: PlayerState | None = None,
) -> bool:
    node = MAP_NODES.get(destination)
    if not node:
        return False
    plague_ports = active_plague_ports(active_news or [])
    if destination in plague_ports and ship.location not in plague_ports:
        return False
    return port_allows_ship_entry(node, ship, players, player)


def port_entry_policy_line(node: MapNode) -> str:
    if node.owner == "Pirates":
        return "Pirate ports: open/free"
    label = ENTRY_MODE_LABELS.get(node.entry_mode, "Default")
    if node.entry_mode in ("allow_only", "reject_selected") and node.entry_countries:
        countries = ", ".join(OWNER_LEGEND_LABELS.get(country, country) for country in sorted(node.entry_countries))
        return f"{label}: {countries}"
    return label


def charge_arrival_fee(ship: Ship, players: list[PlayerState], round_number: int | None = None) -> None:
    port = MAP_NODES.get(ship.location)
    if not port or not port.owner or port.owner == ship.owner:
        return
    if ship_has_license(ship, "smuggler", players):
        return
    if port.owner == "Pirates":
        return
    if port.entry_mode == "open_all":
        return
    if ship.owner in port.free_entry_countries:
        return
    fee = adjusted_port_fee(ship.owner, port)
    ship_owner = player_by_country(players, ship.owner)
    port_owner = player_by_country(players, port.owner)
    if ship_owner and port_owner and fee:
        ship_owner.money -= fee
        port_owner.money += fee
        if round_number is not None:
            record_transaction(ship_owner, round_number, -fee, f"entry fee at {display_place_name(port.name)}")
            record_transaction(port_owner, round_number, fee, f"fee from {ship.owner} at {display_place_name(port.name)}")


def adjusted_port_fee(payer_country: str, port: MapNode) -> int:
    fee = port.fee or 0
    if payer_country == "China" and port.owner != "China":
        fee -= 10 if port.kind == "choking" else 5
        return max(5, fee)
    if port.owner == "China" and payer_country != "China":
        fee += 15 if port.kind == "choking" else 10
    return max(0, fee)


def declarable_trade_card_for_port(player: PlayerState, ship: Ship | None, port_name: str) -> TradeCard | None:
    if not ship or ship.owner != player.country or ship.kind != "Merchant" or ship.trade_card:
        return None
    for card in player.trade_cards:
        if card.status != "undeclared":
            continue
        if trade_card_other_endpoint(card, port_name):
            return card
    return None


def declare_trade_for_ship(player: PlayerState, ship: Ship, port_name: str) -> bool:
    card = declarable_trade_card_for_port(player, ship, port_name)
    if not card:
        return False
    destination = trade_card_other_endpoint(card, port_name)
    if not destination:
        return False
    card.status = "declared"
    ship.trade_card = card
    ship.trade_destination = destination
    return True


def complete_trade_if_ready(
    ship: Ship,
    players: list[PlayerState],
    round_number: int,
    history_events: list[HistoryEvent],
    last_trade_summary: dict[str, str],
    force_sell: bool = False,
) -> bool:
    if not ship.trade_card or not ship.trade_destination:
        return False
    player = player_by_country(players, ship.owner)
    if not player:
        return False
    card = ship.trade_card
    port = MAP_NODES.get(ship.location)
    at_destination = ship.location == ship.trade_destination
    if not at_destination and not force_sell:
        return False
    if at_destination:
        profit = card.profit
    elif ship.owner == "Pirates" and port and port.owner == "Pirates":
        profit = 200
    elif ship.kind == "Merchant" and port and port.owner == ship.owner:
        profit = 100
    elif ship.kind == "Merchant" and port and port.owner == "Pirates":
        profit = 150
    else:
        return False
    player.money += profit
    record_transaction(player, round_number, profit, f"trade {card.start} -> {card.end}")
    card.status = "interrupted" if force_sell and ship.kind == "Merchant" and not at_destination else "success"
    last_trade_summary[player.country] = f"+${profit} {card.start} -> {card.end}"
    history_events.append(
        HistoryEvent(
            round_number=round_number,
            kind="trade",
            title=f"{player.country} completed a trade route",
            details=[f"{card.start} -> {card.end}", f"Profit: ${profit}", f"Ship: {ship.name}"],
        )
    )
    ship.trade_card = None
    ship.trade_destination = None
    return True


def can_sell_trade_at_port(ship: Ship | None, port_name: str) -> bool:
    if not ship or not ship.trade_card or not ship.trade_destination:
        return False
    port = MAP_NODES.get(port_name)
    if not port:
        return False
    if port_name == ship.trade_destination:
        return True
    if ship.owner == "Pirates" and ship.kind == "Pirate" and port.owner == "Pirates":
        return True
    if ship.kind == "Merchant" and port.owner in (ship.owner, "Pirates"):
        return True
    return False


def land_route_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def land_goods_distance_between(start: str, end: str) -> int | None:
    return GOODS_LAND_ROUTES.get(land_route_key(start, end))


def land_goods_neighbors(port_name: str) -> list[tuple[str, int]]:
    neighbors = []
    for (a, b), distance in GOODS_LAND_ROUTES.items():
        if a == port_name:
            neighbors.append((b, distance))
        elif b == port_name:
            neighbors.append((a, distance))
    return sorted(neighbors)


def port_storage(port_storage_by_port: dict[str, list[StoredGood]], port_name: str) -> list[StoredGood]:
    return port_storage_by_port.setdefault(port_name, [])


def port_storage_capacity(port_name: str) -> int:
    node = MAP_NODES.get(port_name)
    return node.storage_capacity if node else 3


def can_store_good(ship: Ship | None, port_name: str, port_storage_by_port: dict[str, list[StoredGood]]) -> bool:
    if not ship or ship.kind != "Merchant" or ship.location != port_name:
        return False
    if not ship.trade_card or not ship.trade_destination:
        return False
    return len(port_storage(port_storage_by_port, port_name)) < port_storage_capacity(port_name)


def storage_pickup_allowed(ship: Ship, port_name: str, good: StoredGood) -> bool:
    port = MAP_NODES.get(port_name)
    if port and port.owner == "Pirates" and ship.kind in ("Merchant", "Pirate"):
        return True
    return ship.kind == "Merchant" and good.owner == ship.owner


def assign_stored_good_to_ship(good: StoredGood, ship: Ship, players: list[PlayerState] | None = None) -> None:
    old_owner = good.owner
    new_owner = "Pirates" if ship.owner == "Pirates" or ship.kind == "Pirate" else ship.owner
    if players and old_owner != new_owner:
        old_player = player_by_country(players, old_owner)
        new_player = player_by_country(players, new_owner)
        if old_player and good.trade_card in old_player.trade_cards:
            old_player.trade_cards.remove(good.trade_card)
        if new_player and good.trade_card not in new_player.trade_cards:
            new_player.trade_cards.append(good.trade_card)
    if new_owner == "Pirates":
        good.trade_card.stolen_from = good.trade_card.stolen_from or old_owner
        good.trade_card.status = "robbed"
    else:
        good.trade_card.status = "declared"
    good.owner = new_owner
    ship.trade_card = good.trade_card
    ship.trade_destination = good.trade_destination


def store_ship_good(ship: Ship, port_storage_by_port: dict[str, list[StoredGood]]) -> bool:
    if not can_store_good(ship, ship.location, port_storage_by_port):
        return False
    assert ship.trade_card and ship.trade_destination
    ship.trade_card.status = "stored"
    port_storage(port_storage_by_port, ship.location).append(
        StoredGood(ship.owner, ship.trade_card, ship.trade_destination)
    )
    ship.trade_card = None
    ship.trade_destination = None
    return True


def can_pickup_good_here(ship: Ship | None, port_name: str, port_storage_by_port: dict[str, list[StoredGood]]) -> bool:
    if not ship or ship.kind not in ("Merchant", "Pirate") or ship.location != port_name or ship.trade_card:
        return False
    return any(storage_pickup_allowed(ship, port_name, good) for good in port_storage(port_storage_by_port, port_name))


def pickup_good_here(
    ship: Ship,
    port_storage_by_port: dict[str, list[StoredGood]],
    players: list[PlayerState] | None = None,
) -> bool:
    if not can_pickup_good_here(ship, ship.location, port_storage_by_port):
        return False
    goods = port_storage(port_storage_by_port, ship.location)
    for idx, good in enumerate(goods):
        if storage_pickup_allowed(ship, ship.location, good):
            goods.pop(idx)
            assign_stored_good_to_ship(good, ship, players)
            return True
    return False


def can_request_land_pickup(
    ship: Ship | None,
    source_port: str,
    port_storage_by_port: dict[str, list[StoredGood]],
    pending_transfers: list[PendingGoodsTransfer],
) -> bool:
    if not ship or ship.kind not in ("Merchant", "Pirate") or ship.trade_card or ship_is_enroute(ship):
        return False
    if ship.location == source_port:
        return can_pickup_good_here(ship, source_port, port_storage_by_port)
    if land_goods_distance_between(ship.location, source_port) is None:
        return False
    if any(transfer.waiting_ship_id == id(ship) for transfer in pending_transfers):
        return False
    return any(storage_pickup_allowed(ship, source_port, good) for good in port_storage(port_storage_by_port, source_port))


def land_pickup_source_for_ship(
    ship: Ship | None,
    pickup_port: str,
    port_storage_by_port: dict[str, list[StoredGood]],
    pending_transfers: list[PendingGoodsTransfer],
) -> str | None:
    if not ship or ship.location != pickup_port:
        return None
    if can_pickup_good_here(ship, pickup_port, port_storage_by_port):
        return pickup_port
    for neighbor, _ in land_goods_neighbors(pickup_port):
        if can_request_land_pickup(ship, neighbor, port_storage_by_port, pending_transfers):
            return neighbor
    return None


def pay_port_fee_between_players(
    owner: str,
    port_name: str,
    players: list[PlayerState],
    round_number: int | None = None,
    detail: str = "port fee",
) -> int:
    port = MAP_NODES.get(port_name)
    if not port or not port.owner or port.owner == "Pirates":
        return 0
    fee = adjusted_port_fee(owner, port)
    payer = player_by_country(players, owner)
    payee = player_by_country(players, port.owner)
    if payer and payee and fee:
        payer.money -= fee
        payee.money += fee
        if round_number is not None:
            place = display_place_name(port_name)
            record_transaction(payer, round_number, -fee, f"{detail} at {place}")
            record_transaction(payee, round_number, fee, f"{detail} from {owner} at {place}")
        return fee
    return 0


def request_land_good_pickup(
    ship: Ship,
    source_port: str,
    players: list[PlayerState],
    port_storage_by_port: dict[str, list[StoredGood]],
    pending_transfers: list[PendingGoodsTransfer],
    round_number: int,
    history_events: list[HistoryEvent],
) -> bool:
    if source_port == ship.location:
        return pickup_good_here(ship, port_storage_by_port, players)
    distance = land_goods_distance_between(ship.location, source_port)
    if distance is None or not can_request_land_pickup(ship, source_port, port_storage_by_port, pending_transfers):
        return False
    goods = port_storage(port_storage_by_port, source_port)
    for idx, good in enumerate(goods):
        if not storage_pickup_allowed(ship, source_port, good):
            continue
        goods.pop(idx)
        old_owner = good.owner
        new_owner = "Pirates" if ship.owner == "Pirates" or ship.kind == "Pirate" else ship.owner
        if old_owner != new_owner:
            old_player = player_by_country(players, old_owner)
            new_player = player_by_country(players, new_owner)
            if old_player and good.trade_card in old_player.trade_cards:
                old_player.trade_cards.remove(good.trade_card)
            if new_player and good.trade_card not in new_player.trade_cards:
                new_player.trade_cards.append(good.trade_card)
        if new_owner == "Pirates":
            good.trade_card.stolen_from = good.trade_card.stolen_from or old_owner
            good.trade_card.status = "robbed"
        else:
            good.trade_card.status = "declared"
        good.owner = new_owner
        cost = 20 * distance
        owner = player_by_country(players, ship.owner)
        if owner:
            owner.money -= cost
            record_transaction(owner, round_number, -cost, f"land goods transit {display_place_name(source_port)} -> {display_place_name(ship.location)}")
        pending_transfers.append(
            PendingGoodsTransfer(ship.owner, good, source_port, ship.location, distance, id(ship))
        )
        history_events.append(
            HistoryEvent(
                round_number=round_number,
                kind="goods",
                title=f"{ship.owner} started land goods transit",
                details=[
                    f"{display_place_name(source_port)} -> {display_place_name(ship.location)}",
                    f"Transit: {distance} turn(s), cost: ${cost}",
                ],
            )
        )
        return True
    return False


def advance_pending_goods_transfers(
    pending_transfers: list[PendingGoodsTransfer],
    players: list[PlayerState],
    port_storage_by_port: dict[str, list[StoredGood]],
    round_number: int,
    history_events: list[HistoryEvent],
) -> None:
    for transfer in list(pending_transfers):
        transfer.turns_remaining = max(0, transfer.turns_remaining - 1)
        if transfer.turns_remaining > 0:
            continue
        waiting_ship = None
        for player in players:
            for ship in player.ships:
                if id(ship) == transfer.waiting_ship_id:
                    waiting_ship = ship
                    break
            if waiting_ship:
                break
        fee = 0
        if not transfer.arrival_fee_paid:
            fee = pay_port_fee_between_players(transfer.owner, transfer.to_port, players, round_number, "goods arrival fee")
            transfer.arrival_fee_paid = True
        if (
            waiting_ship
            and waiting_ship.owner == transfer.owner
            and waiting_ship.kind in ("Merchant", "Pirate")
            and waiting_ship.location == transfer.to_port
            and not waiting_ship.trade_card
        ):
            assign_stored_good_to_ship(transfer.good, waiting_ship, players)
            pending_transfers.remove(transfer)
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="goods",
                    title=f"{transfer.owner} picked up transferred goods",
                    details=[
                        f"Arrived at {display_place_name(transfer.to_port)}",
                        f"Port fee: ${fee}",
                    ],
                )
            )
        elif len(port_storage(port_storage_by_port, transfer.to_port)) < port_storage_capacity(transfer.to_port):
            transfer.good.trade_card.status = "stored"
            port_storage(port_storage_by_port, transfer.to_port).append(transfer.good)
            pending_transfers.remove(transfer)
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="goods",
                    title=f"{transfer.owner} goods arrived in storage",
                    details=[
                        f"{display_place_name(transfer.from_port)} -> {display_place_name(transfer.to_port)}",
                        f"Port fee: ${fee}",
                    ],
                )
            )


def collect_storage_fees(
    players: list[PlayerState],
    port_storage_by_port: dict[str, list[StoredGood]],
    round_number: int,
) -> dict[str, int]:
    totals = {country: 0 for country in EMPIRE_ORDER}
    for port_name, goods in port_storage_by_port.items():
        for good in goods:
            fee = pay_port_fee_between_players(good.owner, port_name, players, round_number, "goods storage fee")
            totals[good.owner] = totals.get(good.owner, 0) + fee
    return totals


def move_ship_toward(
    ship: Ship,
    destination: str,
    players: list[PlayerState],
    active_news: list[NewsEvent] | None = None,
    round_number: int | None = None,
) -> bool:
    plague_ports = active_plague_ports(active_news or [])
    if ship.location in plague_ports or destination in plague_ports:
        return False
    distance = course_distance_between(ship.location, destination)
    if distance is None:
        return False
    ship.destination = destination
    ship.course_distance = distance
    ship.progress = 0
    ship.sugar_speed_active = False
    advance_ship(ship, players, active_news, round_number)
    return True


def advance_ship(
    ship: Ship,
    players: list[PlayerState],
    active_news: list[NewsEvent] | None = None,
    round_number: int | None = None,
) -> bool:
    if not ship.destination:
        return False
    plague_ports = active_plague_ports(active_news or [])
    if ship.location in plague_ports:
        return False
    old_progress = ship.progress
    speed = (
        effective_ship_speed_for_players(ship, players, round_number, active_news or [])
        if round_number is not None
        else effective_ship_speed(ship, active_news or [])
    )
    ship.progress += speed
    advanced = min(ship.progress, ship.course_distance) - old_progress
    ship.distance_since_upkeep += max(0, advanced)
    if ship.progress >= ship.course_distance:
        if ship.destination in plague_ports and ship.location not in plague_ports:
            ship.progress = old_progress
            ship.distance_since_upkeep -= max(0, advanced)
            return False
        ship.location = ship.destination
        ship.destination = None
        ship.progress = 0
        ship.course_distance = 0
        ship.sugar_speed_active = False
        return True
    return False


def reverse_ship_course(ship: Ship) -> bool:
    if not ship.destination:
        return False
    old_location = ship.location
    old_destination = ship.destination
    ship.location = old_destination
    ship.destination = old_location
    ship.progress = max(0, ship.course_distance - ship.progress)
    return True


def route_screen_polyline(start: str, end: str) -> list[tuple[int, int]]:
    return [geo_to_screen(lat, lon) for lat, lon in route_geo_points(start, end)]


def point_along_polyline(points: list[tuple[int, int]], ratio: float) -> tuple[int, int]:
    if not points:
        return 0, 0
    if len(points) == 1:
        return points[0]
    segments = []
    total = 0.0
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        segments.append((a, b, length))
        total += length
    target = max(0.0, min(1.0, ratio)) * total
    walked = 0.0
    for a, b, length in segments:
        if walked + length >= target:
            t = 0 if length == 0 else (target - walked) / length
            return round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
        walked += length
    return points[-1]


def ship_screen_position(ship: Ship) -> tuple[int, int]:
    if ship.destination:
        points = route_screen_polyline(ship.location, ship.destination)
        ratio = ship.progress / max(1, ship.course_distance)
        return point_along_polyline(points, ratio)
    return node_to_screen(ship.location)


def draw_routes(surface: pygame.Surface, font: pygame.font.Font) -> None:
    for start, end, distance in course_endpoints():
        points = []
        geo_points = route_geo_points(start, end)
        for first, second in zip(geo_points, geo_points[1:]):
            a = geo_to_screen(first[0], first[1])
            b = geo_to_screen(second[0], second[1])
            segment_points = draw_wrapped_curve(surface, ROUTE, a, b, 2)
            points.extend(segment_points)
        mid = points[len(points) // 2]
        label = font.render(str(distance), True, ROUTE)
        bg = label.get_rect(center=mid).inflate(4, 2)
        pygame.draw.rect(surface, OCEAN, bg, border_radius=3)
        surface.blit(label, label.get_rect(center=mid))


def draw_land_goods_routes(surface: pygame.Surface, font: pygame.font.Font) -> None:
    for (start, end), distance in GOODS_LAND_ROUTES.items():
        a = node_to_screen(start)
        b = node_to_screen(end)
        points = curve_points(a, b, bend=0.10)
        if len(points) >= 2:
            pygame.draw.lines(surface, LAND_GOODS_ROUTE, False, points, 3)
        mid = points[len(points) // 2] if points else ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
        label = font.render(str(distance), True, LAND_GOODS_ROUTE)
        bg = label.get_rect(center=mid).inflate(5, 3)
        pygame.draw.rect(surface, (245, 236, 210), bg, border_radius=3)
        surface.blit(label, label.get_rect(center=mid))


def draw_goods_icon(
    surface: pygame.Surface,
    pos: tuple[int, int],
    count: int,
    font: pygame.font.Font,
) -> None:
    x, y = pos
    rect = pygame.Rect(x - 9, y - 9, 18, 16)
    pygame.draw.rect(surface, (161, 111, 52), rect, border_radius=3)
    pygame.draw.rect(surface, (72, 45, 24), rect, 2, border_radius=3)
    pygame.draw.line(surface, (217, 170, 91), rect.midleft, rect.midright, 2)
    pygame.draw.line(surface, (110, 70, 32), (rect.centerx, rect.top), (rect.centerx, rect.bottom), 1)
    if count > 1:
        badge = pygame.Rect(0, 0, 16, 16)
        badge.center = (x + 11, y + 9)
        pygame.draw.ellipse(surface, (235, 245, 250), badge)
        pygame.draw.ellipse(surface, (65, 96, 123), badge, 1)
        label = font.render(str(count), True, (32, 49, 63))
        surface.blit(label, label.get_rect(center=badge.center))


def draw_stored_goods(
    surface: pygame.Surface,
    font: pygame.font.Font,
    port_storage_by_port: dict[str, list[StoredGood]],
    pending_transfers: list[PendingGoodsTransfer],
) -> None:
    for port_name, goods in port_storage_by_port.items():
        if goods:
            pos = node_to_screen(port_name)
            draw_goods_icon(surface, (pos[0] + 16, pos[1] + 16), len(goods), font)
    for transfer in pending_transfers:
        points = [node_to_screen(transfer.from_port), node_to_screen(transfer.to_port)]
        total = max(1, GOODS_LAND_ROUTES.get(land_route_key(transfer.from_port, transfer.to_port), 1))
        ratio = 1.0 - transfer.turns_remaining / total
        pos = point_along_polyline(points, ratio)
        draw_goods_icon(surface, pos, 1, font)


def draw_active_ship_choices(
    surface: pygame.Surface,
    font: pygame.font.Font,
    ship: Ship,
    attack_mode: bool = False,
    player: PlayerState | None = None,
) -> None:
    if ship_is_enroute(ship):
        pos = ship_screen_position(ship)
        label = "G/Continue   R/Return   S/Stay"
        draw_text(surface, font, label, (pos[0] + 18, pos[1] - 24), (255, 236, 142))
        return

    current = ship.location
    if current not in COURSE_GRAPH:
        return
    for neighbor, distance in COURSE_GRAPH[current]:
        pos = node_to_screen(neighbor)
        pygame.draw.circle(surface, (255, 211, 76), pos, 21, 2)
        label = font.render(str(distance), True, (255, 211, 76))
        surface.blit(label, label.get_rect(center=(pos[0], pos[1] - 22)))
    port_pos = node_to_screen(current)
    label = "Hover neighbor, choose Enter/Attack/Enforce; S to stay"
    if ship_can_attack(ship, player=player):
        label += "  A attack on" if attack_mode else "  A attack off"
    draw_text(surface, font, label, (port_pos[0] + 28, port_pos[1] - 28), (255, 236, 142))


def draw_enroute_action_popup(
    surface: pygame.Surface,
    font: pygame.font.Font,
    ship: Ship,
    player: PlayerState,
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    pos = ship_screen_position(ship)
    can_speed = player.resources.get("sugar", 0) > 0 and not ship.sugar_speed_active
    width = 238 if can_speed else 168
    height = 38
    x = pos[0] + 18
    y = pos[1] + 16
    if x + width > SCREEN_WIDTH - SIDE_PANEL_WIDTH - 8:
        x = pos[0] - width - 18
    if y + height > SCREEN_HEIGHT - 62:
        y = pos[1] - height - 34
    panel = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (250, 249, 239), panel, border_radius=6)
    pygame.draw.rect(surface, (64, 88, 104), panel, 1, border_radius=6)
    continue_rect = pygame.Rect(x + 8, y + 7, 76, 24)
    return_rect = pygame.Rect(x + 92, y + 7, 66, 24)
    speed_rect = pygame.Rect(0, 0, 0, 0)
    pygame.draw.rect(surface, (65, 96, 123), continue_rect, border_radius=5)
    pygame.draw.rect(surface, (116, 86, 151), return_rect, border_radius=5)
    draw_text(surface, font, "Continue", (continue_rect.x + 6, continue_rect.y + 4), TEXT)
    draw_text(surface, font, "Return", (return_rect.x + 9, return_rect.y + 4), TEXT)
    if can_speed:
        speed_rect = pygame.Rect(x + 166, y + 7, 62, 24)
        pygame.draw.rect(surface, (180, 152, 68), speed_rect, border_radius=5)
        draw_text(surface, font, "Speed", (speed_rect.x + 9, speed_rect.y + 4), TEXT)
    return continue_rect, return_rect, speed_rect


def draw_enroute_target_popup(
    surface: pygame.Surface,
    font: pygame.font.Font,
    ship: Ship,
    target: Ship,
    players: list[PlayerState],
) -> tuple[pygame.Rect, pygame.Rect]:
    pos = ship_screen_position(target)
    can_attack = ship_can_attack(ship, players)
    action_label = attack_action_label(ship, target) if can_attack else ""
    attack_button_width = 70 if action_label == "Enforce" else 60
    width = 76 + attack_button_width if can_attack else 70
    height = 38
    x = pos[0] + 18
    y = pos[1] + 18
    if x + width > SCREEN_WIDTH - SIDE_PANEL_WIDTH - 8:
        x = pos[0] - width - 18
    if y + height > SCREEN_HEIGHT - 62:
        y = pos[1] - height - 36
    panel = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (250, 249, 239), panel, border_radius=6)
    pygame.draw.rect(surface, (64, 88, 104), panel, 1, border_radius=6)
    join_rect = pygame.Rect(x + 8, y + 7, 52, 24)
    pygame.draw.rect(surface, (67, 132, 221), join_rect, border_radius=5)
    draw_text(surface, font, "Join", (join_rect.x + 10, join_rect.y + 4), TEXT)
    attack_rect = pygame.Rect(0, 0, 0, 0)
    if can_attack:
        attack_rect = pygame.Rect(x + 68, y + 7, attack_button_width, 24)
        pygame.draw.rect(surface, (157, 63, 58), attack_rect, border_radius=5)
        draw_text(surface, font, action_label, (attack_rect.x + 7, attack_rect.y + 4), TEXT)
    return join_rect, attack_rect


def neighbor_at_position(location: str, mouse_pos: tuple[int, int]) -> str | None:
    for neighbor, _ in COURSE_GRAPH.get(location, []):
        if math.dist(mouse_pos, node_to_screen(neighbor)) <= 24:
            return neighbor
    return None


def hovered_port_action(
    player: PlayerState,
    ship: Ship | None,
    mouse_pos: tuple[int, int],
    port_storage_by_port: dict[str, list[StoredGood]],
    pending_transfers: list[PendingGoodsTransfer],
    active_news: list[NewsEvent] | None = None,
) -> str | None:
    if not ship or ship_is_enroute(ship):
        return None
    if not MAP_RECT.collidepoint(mouse_pos):
        return None
    hovered_port = port_at_position(mouse_pos, radius=24)
    if hovered_port == ship.location and (
        declarable_trade_card_for_port(player, ship, ship.location)
        or can_sell_trade_at_port(ship, ship.location)
        or can_store_good(ship, ship.location, port_storage_by_port)
        or land_pickup_source_for_ship(ship, ship.location, port_storage_by_port, pending_transfers)
    ):
        return ship.location
    destination = neighbor_at_position(ship.location, mouse_pos)
    if destination and (
        (MAP_NODES[destination].owner != ship.owner and can_ship_enter_port(ship, destination, active_news, player=player))
        or declarable_trade_card_for_port(player, ship, destination)
        or can_sell_trade_at_port(ship, destination)
    ):
        return destination
    return None


def draw_port_action_popup(
    surface: pygame.Surface,
    font: pygame.font.Font,
    player: PlayerState,
    ship: Ship,
    destination: str,
    port_storage_by_port: dict[str, list[StoredGood]],
    pending_transfers: list[PendingGoodsTransfer],
    active_news: list[NewsEvent] | None = None,
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
    node = MAP_NODES[destination]
    pos = node_to_screen(destination)
    same_port = destination == ship.location
    reachable_by_sea = same_port or course_distance_between(ship.location, destination) is not None
    peaceful_entry_allowed = same_port or can_ship_enter_port(ship, destination, active_news, player=player)
    can_sell = reachable_by_sea and can_sell_trade_at_port(ship, destination)
    can_attack = (
        reachable_by_sea
        and node.owner != ship.owner
        and ship.kind != "Merchant"
        and ship_can_attack(ship, player=player)
        and can_attack_defender(ship, node)
    )
    can_declare = reachable_by_sea and declarable_trade_card_for_port(player, ship, destination) is not None
    can_store = can_store_good(ship, destination, port_storage_by_port)
    pickup_source = land_pickup_source_for_ship(ship, destination, port_storage_by_port, pending_transfers)
    can_pickup = pickup_source is not None
    can_speed = False
    remote_pickup = bool(pickup_source and pickup_source != destination)
    attack_label = attack_action_label(ship, node) if can_attack else ""
    button_widths = []
    if not same_port and reachable_by_sea and peaceful_entry_allowed:
        button_widths.append(58)
    if can_sell:
        button_widths.append(52)
    if can_declare:
        button_widths.append(66)
    if can_speed:
        button_widths.append(62)
    if can_store:
        button_widths.append(56)
    if can_pickup:
        button_widths.append(62)
    if can_attack:
        button_widths.append(74 if attack_label == "Enforce" else 64)
    width = max(96, 20 + sum(button_widths) + max(0, len(button_widths) - 1) * 8)
    height = 76 if remote_pickup else 58
    x = pos[0] + 18
    y = pos[1] - height - 12
    if x + width > SCREEN_WIDTH - SIDE_PANEL_WIDTH - 8:
        x = pos[0] - width - 18
    if y < MAP_RECT.top + 4:
        y = pos[1] + 18
    panel = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (250, 249, 239), panel, border_radius=6)
    pygame.draw.rect(surface, (64, 88, 104), panel, 1, border_radius=6)
    draw_text(surface, font, display_place_name(destination), (x + 10, y + 7), (22, 38, 52))

    button_x = x + 10
    enter_rect = pygame.Rect(0, 0, 0, 0)
    if not same_port and reachable_by_sea and peaceful_entry_allowed:
        enter_rect = pygame.Rect(button_x, y + 30, 58, 24)
        pygame.draw.rect(surface, (65, 96, 123), enter_rect, border_radius=5)
        draw_text(surface, font, "Enter", (enter_rect.x + 10, enter_rect.y + 4), TEXT)
        button_x = enter_rect.right + 8

    sell_rect = pygame.Rect(0, 0, 0, 0)
    if can_sell:
        sell_rect = pygame.Rect(button_x, y + 30, 52, 24)
        pygame.draw.rect(surface, (54, 130, 94), sell_rect, border_radius=5)
        draw_text(surface, font, "Sell", (sell_rect.x + 10, sell_rect.y + 4), TEXT)
        button_x = sell_rect.right + 8

    declare_rect = pygame.Rect(0, 0, 0, 0)
    if can_declare:
        declare_rect = pygame.Rect(button_x, y + 30, 66, 24)
        pygame.draw.rect(surface, (44, 116, 190), declare_rect, border_radius=5)
        draw_text(surface, font, "Declare", (declare_rect.x + 6, declare_rect.y + 4), TEXT)
        button_x = declare_rect.right + 8

    speed_rect = pygame.Rect(0, 0, 0, 0)
    if can_speed:
        speed_rect = pygame.Rect(button_x, y + 30, 62, 24)
        pygame.draw.rect(surface, (180, 152, 68), speed_rect, border_radius=5)
        draw_text(surface, font, "Speed", (speed_rect.x + 9, speed_rect.y + 4), TEXT)
        button_x = speed_rect.right + 8

    store_rect = pygame.Rect(0, 0, 0, 0)
    if can_store:
        store_rect = pygame.Rect(button_x, y + 30, 56, 24)
        pygame.draw.rect(surface, (142, 93, 47), store_rect, border_radius=5)
        draw_text(surface, font, "Store", (store_rect.x + 9, store_rect.y + 4), TEXT)
        button_x = store_rect.right + 8

    pickup_rect = pygame.Rect(0, 0, 0, 0)
    if can_pickup:
        pickup_rect = pygame.Rect(button_x, y + 30, 62, 24)
        pygame.draw.rect(surface, (122, 78, 42), pickup_rect, border_radius=5)
        draw_text(surface, font, "Pickup", (pickup_rect.x + 7, pickup_rect.y + 4), TEXT)
        button_x = pickup_rect.right + 8
        if remote_pickup:
            draw_text(
                surface,
                font,
                f"<- {display_place_name(pickup_source)}",
                (pickup_rect.x, pickup_rect.bottom + 4),
                (122, 78, 42),
            )

    attack_rect = pygame.Rect(0, 0, 0, 0)
    if can_attack:
        button_width = 74 if attack_label == "Enforce" else 64
        attack_rect = pygame.Rect(button_x, y + 30, button_width, 24)
        pygame.draw.rect(surface, (157, 63, 58), attack_rect, border_radius=5)
        draw_text(surface, font, attack_label, (attack_rect.x + 8, attack_rect.y + 4), TEXT)
    return enter_rect, sell_rect, declare_rect, store_rect, pickup_rect, speed_rect, attack_rect


def node_color(node: MapNode) -> tuple[int, int, int]:
    if node.kind == "capital":
        return CAPITAL
    if node.kind == "choking":
        return STRAIT
    return PORT


def node_icon(node: MapNode) -> str:
    return OWNER_ICONS.get(node.owner, "⚓")


def node_type_label(node: MapNode) -> str:
    return "chocking" if node.kind == "choking" else node.kind


def draw_owner_marker(
    surface: pygame.Surface,
    owner: str | None,
    center: tuple[int, int],
    font: pygame.font.Font,
    size: int = 24,
) -> None:
    x, y = center
    rect = pygame.Rect(0, 0, size, round(size * 0.72))
    rect.center = center
    shadow = rect.move(1, 2)
    pygame.draw.rect(surface, (0, 0, 0), shadow, border_radius=2)

    if owner == "United Kingdom":
        pygame.draw.rect(surface, (16, 56, 138), rect, border_radius=2)
        pygame.draw.line(surface, (255, 255, 255), rect.topleft, rect.bottomright, 4)
        pygame.draw.line(surface, (255, 255, 255), rect.bottomleft, rect.topright, 4)
        pygame.draw.line(surface, (200, 16, 46), rect.topleft, rect.bottomright, 2)
        pygame.draw.line(surface, (200, 16, 46), rect.bottomleft, rect.topright, 2)
        pygame.draw.line(surface, (255, 255, 255), (rect.centerx, rect.top), (rect.centerx, rect.bottom), 6)
        pygame.draw.line(surface, (255, 255, 255), (rect.left, rect.centery), (rect.right, rect.centery), 6)
        pygame.draw.line(surface, (200, 16, 46), (rect.centerx, rect.top), (rect.centerx, rect.bottom), 3)
        pygame.draw.line(surface, (200, 16, 46), (rect.left, rect.centery), (rect.right, rect.centery), 3)
    elif owner == "Russia":
        pygame.draw.rect(surface, (245, 245, 245), rect, border_radius=2)
        pygame.draw.rect(surface, (28, 70, 158), (rect.left, rect.top + rect.height // 3, rect.width, rect.height // 3))
        pygame.draw.rect(surface, (210, 45, 55), (rect.left, rect.top + 2 * rect.height // 3, rect.width, rect.height // 3))
    elif owner == "China":
        pygame.draw.rect(surface, (210, 28, 45), rect, border_radius=2)
        gold = (255, 222, 55)
        dark_gold = (191, 128, 22)
        scale = max(1, size / 24)
        body_points = [
            (rect.left + round(4 * scale), rect.centery + round(3 * scale)),
            (rect.left + round(8 * scale), rect.centery - round(3 * scale)),
            (rect.left + round(13 * scale), rect.centery + round(2 * scale)),
            (rect.left + round(18 * scale), rect.centery - round(3 * scale)),
        ]
        pygame.draw.lines(surface, dark_gold, False, body_points, max(2, round(4 * scale)))
        pygame.draw.lines(surface, gold, False, body_points, max(1, round(2 * scale)))
        head = (rect.left + round(19 * scale), rect.centery - round(3 * scale))
        pygame.draw.circle(surface, gold, head, max(2, round(3 * scale)))
        pygame.draw.circle(surface, (210, 28, 45), (head[0] + max(1, round(scale)), head[1] - max(1, round(scale))), max(1, round(scale)))
        pygame.draw.line(surface, gold, (head[0] - round(2 * scale), head[1] - round(2 * scale)), (head[0] - round(4 * scale), head[1] - round(6 * scale)), max(1, round(scale)))
        pygame.draw.line(surface, gold, (head[0] + round(1 * scale), head[1] - round(2 * scale)), (head[0] + round(3 * scale), head[1] - round(6 * scale)), max(1, round(scale)))
        pygame.draw.line(surface, gold, body_points[0], (rect.left + round(2 * scale), rect.centery - round(1 * scale)), max(1, round(scale)))
        for claw_x, claw_y in body_points[1:3]:
            pygame.draw.line(surface, gold, (claw_x, claw_y + round(1 * scale)), (claw_x - round(2 * scale), claw_y + round(5 * scale)), max(1, round(scale)))
            pygame.draw.line(surface, gold, (claw_x, claw_y + round(1 * scale)), (claw_x + round(2 * scale), claw_y + round(5 * scale)), max(1, round(scale)))
    elif owner == "Japan":
        pygame.draw.rect(surface, (250, 250, 250), rect, border_radius=2)
        pygame.draw.circle(surface, (188, 0, 45), rect.center, max(4, rect.height // 4))
    elif owner == "Pirates":
        pygame.draw.rect(surface, (20, 20, 24), rect, border_radius=2)
        skull_center = (rect.centerx, rect.centery - 1)
        pygame.draw.circle(surface, (245, 245, 245), skull_center, max(4, rect.height // 4))
        pygame.draw.rect(surface, (245, 245, 245), (skull_center[0] - 4, skull_center[1] + 2, 8, 5))
        pygame.draw.circle(surface, (20, 20, 24), (skull_center[0] - 2, skull_center[1] - 1), 1)
        pygame.draw.circle(surface, (20, 20, 24), (skull_center[0] + 2, skull_center[1] - 1), 1)
        pygame.draw.line(surface, (245, 245, 245), (rect.left + 4, rect.bottom - 3), (rect.right - 4, rect.top + 3), 2)
        pygame.draw.line(surface, (245, 245, 245), (rect.left + 4, rect.top + 3), (rect.right - 4, rect.bottom - 3), 2)
    elif owner == "United States":
        pygame.draw.rect(surface, (250, 250, 250), rect, border_radius=2)
        stripe_h = max(1, rect.height // 7)
        for idx in range(0, 7, 2):
            pygame.draw.rect(surface, (190, 35, 50), (rect.left, rect.top + idx * stripe_h, rect.width, stripe_h))
        pygame.draw.rect(surface, (35, 68, 140), (rect.left, rect.top, rect.width // 2, rect.height // 2))
        pygame.draw.circle(surface, (255, 255, 255), (rect.left + rect.width // 4, rect.top + rect.height // 4), 2)
    else:
        icon = font.render("⚓", True, PORT)
        shadow_icon = font.render("⚓", True, BLACK)
        surface.blit(shadow_icon, shadow_icon.get_rect(center=(x + 1, y + 2)))
        surface.blit(icon, icon.get_rect(center=center))
        return

    pygame.draw.rect(surface, (30, 45, 56), rect, 1, border_radius=2)


def draw_ports(
    surface: pygame.Surface,
    small_font: pygame.font.Font,
    icon_font: pygame.font.Font,
    selected_country: str,
    mouse_pos: tuple[int, int],
) -> MapNode | None:
    hovered = None
    for node in MAP_NODES.values():
        pos = node_to_screen(node.name)
        draw_owner_marker(surface, node.owner, pos, icon_font)
        if node.kind == "capital":
            pygame.draw.circle(surface, CAPITAL, pos, 15, 2)
        elif node.kind == "choking":
            pygame.draw.circle(surface, STRAIT, pos, 14, 2)
        if node.owner == selected_country:
            pygame.draw.circle(surface, HOVER, pos, 17, 2)
        if math.dist(mouse_pos, pos) <= 14:
            hovered = node

    for node in MAP_NODES.values():
        if node.kind == "capital":
            pos = node_to_screen(node.name)
            label = small_font.render(node.name.replace("_", " "), True, TEXT)
            surface.blit(label, (pos[0] + 11, pos[1] - 8))

    if hovered:
        pos = node_to_screen(hovered.name)
        pygame.draw.circle(surface, HOVER, pos, 16, 2)
    return hovered


def ship_counts_by_location(players: list[PlayerState]) -> dict[str, dict[str, dict[str, int]]]:
    counts: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for player in players:
        for ship in player.ships:
            if ship_is_enroute(ship):
                continue
            counts[ship.location][player.country][ship_kind_label(ship, players)] += 1
    return {
        location: {country: dict(kind_counts) for country, kind_counts in country_counts.items()}
        for location, country_counts in counts.items()
    }


def total_ships_at(country_counts: dict[str, dict[str, int]]) -> int:
    return sum(sum(kind_counts.values()) for kind_counts in country_counts.values())


def draw_ship_icon(surface: pygame.Surface, center: tuple[int, int], font: pygame.font.Font, count: int) -> pygame.Rect:
    x, y = center
    hull = [(x - 13, y + 3), (x + 13, y + 3), (x + 8, y + 10), (x - 8, y + 10)]
    pygame.draw.polygon(surface, (24, 65, 98), hull)
    pygame.draw.line(surface, (24, 65, 98), (x, y + 3), (x, y - 12), 2)
    pygame.draw.polygon(surface, (250, 250, 238), [(x + 1, y - 11), (x + 1, y + 1), (x + 10, y + 1)])
    pygame.draw.rect(surface, (255, 255, 255), (x + 7, y + 4, 14, 14), border_radius=7)
    pygame.draw.rect(surface, (24, 65, 98), (x + 7, y + 4, 14, 14), 1, border_radius=7)
    label = font.render(str(count), True, (24, 65, 98))
    surface.blit(label, label.get_rect(center=(x + 14, y + 11)))
    return pygame.Rect(x - 15, y - 14, 38, 34)


def draw_ships(
    surface: pygame.Surface,
    font: pygame.font.Font,
    players: list[PlayerState],
    mouse_pos: tuple[int, int],
    selected_ship: Ship | None = None,
    operable_ships: list[Ship] | None = None,
) -> tuple[str | None, dict[str, dict[str, dict[str, int]]], Ship | None]:
    ship_counts = ship_counts_by_location(players)
    operable_ships = operable_ships or []
    operable_locations = {ship.location for ship in operable_ships if not ship_is_enroute(ship)}
    trade_locations = {
        ship.location
        for player in players
        for ship in player.ships
        if ship.trade_card and not ship_is_enroute(ship)
    }
    hovered_location = None
    hovered_ship = None
    for location, country_counts in ship_counts.items():
        if location not in MAP_NODES:
            continue
        port_pos = node_to_screen(location)
        ship_pos = (port_pos[0] + 22, port_pos[1] + 18)
        rect = draw_ship_icon(surface, ship_pos, font, total_ships_at(country_counts))
        if location in trade_locations:
            pygame.draw.circle(surface, (63, 143, 238), ship_pos, 28, 4)
        if location in operable_locations:
            pygame.draw.circle(surface, (255, 222, 69), ship_pos, 24, 2)
        if selected_ship and not ship_is_enroute(selected_ship) and selected_ship.location == location:
            pygame.draw.circle(surface, (255, 245, 180), ship_pos, 29, 3)
        if rect.collidepoint(mouse_pos):
            hovered_location = location

    for player in players:
        for ship in player.ships:
            if not ship_is_enroute(ship):
                continue
            pos = ship_screen_position(ship)
            rect = draw_ship_icon(surface, pos, font, 1)
            if ship.trade_card:
                pygame.draw.circle(surface, (63, 143, 238), pos, 26, 4)
            if ship in operable_ships:
                pygame.draw.circle(surface, (255, 222, 69), pos, 22, 2)
            if ship is selected_ship:
                pygame.draw.circle(surface, (255, 245, 180), pos, 27, 3)
            if rect.collidepoint(mouse_pos):
                hovered_ship = ship

    return hovered_location, ship_counts, hovered_ship


def ship_selection_rect(ship: Ship) -> pygame.Rect:
    pos = ship_screen_position(ship)
    if not ship_is_enroute(ship):
        pos = (pos[0] + 22, pos[1] + 18)
    return pygame.Rect(pos[0] - 19, pos[1] - 17, 42, 38)


def clicked_operable_ship(
    ships: list[Ship],
    mouse_pos: tuple[int, int],
    selected_ship: Ship | None,
) -> Ship | None:
    candidates = [ship for ship in ships if ship_selection_rect(ship).collidepoint(mouse_pos)]
    if not candidates:
        return None
    candidates.sort(key=lambda ship: 0 if ship.kind == "Pirate" and ship.trade_card else 1)
    if selected_ship in candidates and len(candidates) > 1:
        idx = candidates.index(selected_ship)
        return candidates[(idx + 1) % len(candidates)]
    return candidates[0]


def attackable_enemy_ships(ship: Ship | None, players: list[PlayerState]) -> list[Ship]:
    if not ship or ship_is_enroute(ship) or not ship_can_attack(ship, players):
        return []
    speed = ship_speed(ship)
    targets = []
    for player in players:
        if player.country == ship.owner:
            continue
        for enemy in player.ships:
            if not ships_can_fight(ship, enemy, players):
                continue
            if not ship_is_enroute(enemy):
                if enemy.location == ship.location:
                    targets.append(enemy)
                    continue
                distance = course_distance_between(ship.location, enemy.location)
                if distance is not None and distance <= speed:
                    targets.append(enemy)
                continue
            if enemy.location == ship.location and enemy.progress <= speed:
                targets.append(enemy)
            elif enemy.destination == ship.location and enemy.course_distance - enemy.progress <= speed:
                targets.append(enemy)
    return targets


def enroute_target_distance(ship: Ship, target: Ship) -> int | None:
    if not ship_is_enroute(ship) or not ship_is_enroute(target):
        return None
    if ship.course_distance != target.course_distance:
        return None
    if ship.location == target.location and ship.destination == target.destination:
        target_progress = target.progress
    elif ship.location == target.destination and ship.destination == target.location:
        target_progress = target.course_distance - target.progress
    else:
        return None
    return abs(target_progress - ship.progress)


def reachable_enroute_enemy_ships(
    ship: Ship | None,
    players: list[PlayerState],
    active_news: list[NewsEvent] | None = None,
) -> list[Ship]:
    if not ship or not ship_is_enroute(ship):
        return []
    targets = []
    for player in players:
        if player.country == ship.owner:
            continue
        for target in player.ships:
            if not ships_can_fight(ship, target, players):
                continue
            distance = enroute_target_distance(ship, target)
            if distance is not None and distance <= effective_ship_speed(ship, active_news or []):
                targets.append(target)
    return targets


def join_enroute_ship(ship: Ship, target: Ship, active_news: list[NewsEvent] | None = None) -> bool:
    distance = enroute_target_distance(ship, target)
    if ship.location in active_plague_ports(active_news or []):
        return False
    if distance is None or distance > effective_ship_speed(ship, active_news or []):
        return False
    old_progress = ship.progress
    if ship.location == target.location and ship.destination == target.destination:
        ship.progress = target.progress
    elif ship.location == target.destination and ship.destination == target.location:
        ship.progress = ship.course_distance - target.progress
    else:
        return False
    ship.distance_since_upkeep += abs(ship.progress - old_progress)
    return True


def enroute_target_at_position(
    ship: Ship | None,
    players: list[PlayerState],
    mouse_pos: tuple[int, int],
    active_news: list[NewsEvent] | None = None,
) -> Ship | None:
    for target in reachable_enroute_enemy_ships(ship, players, active_news):
        if math.dist(mouse_pos, ship_screen_position(target)) <= 30:
            return target
    return None


def attackable_ship_at_position(ship: Ship | None, players: list[PlayerState], mouse_pos: tuple[int, int]) -> Ship | None:
    for target in attackable_enemy_ships(ship, players):
        if math.dist(mouse_pos, ship_screen_position(target)) <= 24:
            return target
    return None


def move_ship_to_intercept(attacker: Ship, target: Ship, active_news: list[NewsEvent] | None = None) -> bool:
    plague_ports = active_plague_ports(active_news or [])
    if attacker.location in plague_ports:
        return False
    if not ship_is_enroute(target):
        if target.location == attacker.location:
            return True
        distance = course_distance_between(attacker.location, target.location)
        if target.location in plague_ports:
            return False
        if distance is None or distance > effective_ship_speed(attacker, active_news or []):
            return False
        attacker.distance_since_upkeep += distance
        attacker.location = target.location
        attacker.destination = None
        attacker.progress = 0
        attacker.course_distance = 0
        return True
    if target.location == attacker.location:
        attacker.destination = target.destination
        attacker.course_distance = target.course_distance
        attacker.progress = target.progress
        attacker.distance_since_upkeep += target.progress
        return True
    if target.destination == attacker.location:
        attacker.destination = target.location
        attacker.course_distance = target.course_distance
        attacker.progress = target.course_distance - target.progress
        attacker.distance_since_upkeep += attacker.progress
        return True
    return False


def draw_attackable_ship_targets(
    surface: pygame.Surface,
    font: pygame.font.Font,
    ship: Ship | None,
    players: list[PlayerState],
    active_news: list[NewsEvent] | None = None,
) -> None:
    if ship and ship_is_enroute(ship):
        for target in reachable_enroute_enemy_ships(ship, players, active_news):
            pos = ship_screen_position(target)
            pygame.draw.circle(surface, (67, 132, 221), pos, 30, 3)
            join_label = font.render("Join", True, (67, 132, 221))
            surface.blit(join_label, join_label.get_rect(center=(pos[0], pos[1] - 34)))
            if ship_can_attack(ship, players):
                pygame.draw.circle(surface, (255, 86, 86), pos, 24, 2)
                attack_label = font.render(attack_action_label(ship, target), True, (255, 86, 86))
                surface.blit(attack_label, attack_label.get_rect(center=(pos[0], pos[1] - 52)))
        return
    targets = attackable_enemy_ships(ship, players)
    for target in targets:
        pos = ship_screen_position(target)
        pygame.draw.circle(surface, (255, 86, 86), pos, 26, 3)
        defender = attack_defender_for_target(ship, target) if ship else target
        label = font.render(attack_action_label(ship, defender), True, (255, 86, 86))
        surface.blit(label, label.get_rect(center=(pos[0], pos[1] - 30)))


def draw_port_tooltip(
    surface: pygame.Surface,
    font: pygame.font.Font,
    node: MapNode | None,
    mouse_pos: tuple[int, int],
    ship_counts: dict[str, dict[str, dict[str, int]]] | None = None,
    ship_location: str | None = None,
    hovered_ship: Ship | None = None,
    port_storage_by_port: dict[str, list[StoredGood]] | None = None,
    pending_transfers: list[PendingGoodsTransfer] | None = None,
    players: list[PlayerState] | None = None,
) -> None:
    if not node and not ship_location and not hovered_ship:
        return
    location = ship_location or (node.name if node else None)
    lines: list[str] = []
    ship_rows: list[tuple[str, str]] = []
    if hovered_ship:
        destination = hovered_ship.destination or hovered_ship.location
        lines += [
            "Ship underway" if hovered_ship.destination else hovered_ship.location.replace("_", " "),
            f"{hovered_ship.location.replace('_', ' ')} -> {destination.replace('_', ' ')}",
            f"Progress: {hovered_ship.progress}/{hovered_ship.course_distance or 0}",
        ]
        ship_rows.append((hovered_ship.owner, f"{ship_kind_label(hovered_ship, players or [])} x1"))
    elif node:
        name = node.name.replace("_", " ")
        tax = f"${node.tax}" if node.tax is not None else "n/a"
        fee = f"${node.fee}" if node.fee is not None else "n/a"
        lines += [name, f"Tax: {tax}", f"Fee: {fee}"]
        lines.append(f"Entry: {port_entry_policy_line(node)}")
        if node.free_entry_countries:
            free = ", ".join(OWNER_LEGEND_LABELS.get(country, country) for country in sorted(node.free_entry_countries))
            lines.append(f"Free: {free}")
    elif location:
        lines.append(location.replace("_", " "))
    if location and port_storage_by_port is not None:
        goods = port_storage_by_port.get(location, [])
        inbound = [transfer for transfer in (pending_transfers or []) if transfer.to_port == location]
        if node or goods or inbound:
            lines.append(f"Storage: {len(goods)}/{port_storage_capacity(location)}")
        for good in goods[:4]:
            lines.append(
                f"Goods: {good.owner} -> {display_place_name(good.trade_destination)} ${good.trade_card.profit}"
            )
        for transfer in inbound[:3]:
            lines.append(
                f"In transit: {transfer.owner} {transfer.turns_remaining} turn(s)"
            )
    if ship_counts and location in ship_counts:
        lines.append("Ships:")
        for country in EMPIRE_ORDER:
            kind_counts = ship_counts[location].get(country, {})
            if kind_counts:
                parts = []
                merchant_count = kind_counts.get("Merchant", 0)
                merchant_trade_count = kind_counts.get("Merchant (+)", 0)
                warship_count = kind_counts.get("Warship", 0)
                pirate_count = kind_counts.get("Pirate", 0)
                pirate_trade_count = kind_counts.get("Pirate (+)", 0)
                if merchant_count:
                    parts.append(f"Merchant x{merchant_count}")
                if merchant_trade_count:
                    parts.append(f"Merchant (+) x{merchant_trade_count}")
                if warship_count:
                    parts.append(f"Warship x{warship_count}")
                if pirate_count:
                    parts.append(f"Pirate x{pirate_count}")
                if pirate_trade_count:
                    parts.append(f"Pirate (+) x{pirate_trade_count}")
                ship_rows.append((country, ", ".join(parts)))
    text_widths = [font.size(line)[0] for line in lines]
    text_widths += [font.size(detail)[0] + 42 for _, detail in ship_rows]
    width = max(text_widths) + 22
    height = len(lines) * (font.get_height() + 3) + len(ship_rows) * 25 + 18
    x = mouse_pos[0] + 16
    y = mouse_pos[1] + 14
    if x + width > SCREEN_WIDTH - SIDE_PANEL_WIDTH - 8:
        x = mouse_pos[0] - width - 16
    if y + height > SCREEN_HEIGHT - 8:
        y = mouse_pos[1] - height - 14
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (250, 249, 239), rect, border_radius=6)
    pygame.draw.rect(surface, (64, 88, 104), rect, 1, border_radius=6)
    text_y = y + 8
    for idx, line in enumerate(lines):
        color = (22, 38, 52) if idx == 0 else (58, 72, 82)
        draw_text(surface, font, line, (x + 11, text_y), color)
        text_y += font.get_height() + 3
    for country, detail in ship_rows:
        draw_owner_marker(surface, country, (x + 22, text_y + 10), font, size=22)
        draw_text(surface, font, detail, (x + 42, text_y + 1), (42, 58, 70))
        text_y += 25


def draw_player_tabs(
    surface: pygame.Surface,
    font: pygame.font.Font,
    players: list[PlayerState],
    selected_idx: int,
) -> list[pygame.Rect]:
    rects = []
    x = 18
    y = 14
    for idx, player in enumerate(players):
        w = 156
        h = 34
        rect = pygame.Rect(x, y, w, h)
        rects.append(rect)
        color = OWNER_COLORS[player.country]
        bg = color if idx == selected_idx else (32, 49, 63)
        pygame.draw.rect(surface, bg, rect, border_radius=6)
        pygame.draw.rect(surface, (220, 226, 229), rect, 1, border_radius=6)
        text_color = BLACK if idx == selected_idx and player.country != "Pirates" else TEXT
        draw_text(surface, font, player.country, (x + 10, y + 8), text_color)
        x += w + 8
        if x + w > SCREEN_WIDTH - SIDE_PANEL_WIDTH - 12:
            x = 18
            y += h + 8
    return rects


def draw_resource_glyph(
    surface: pygame.Surface,
    resource: str,
    rect: pygame.Rect,
    font: pygame.font.Font,
    show_label: bool = True,
) -> None:
    color = RESOURCE_COLORS.get(resource, (160, 166, 172))
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, (220, 226, 229), rect, 1, border_radius=5)
    if resource == "wood":
        pygame.draw.line(surface, (83, 55, 32), rect.midleft, rect.midright, 3)
        pygame.draw.circle(surface, (98, 66, 38), rect.center, max(4, rect.width // 5), 2)
    elif resource == "metal":
        pygame.draw.polygon(
            surface,
            (205, 214, 221),
            [(rect.centerx, rect.top + 4), (rect.right - 5, rect.centery), (rect.centerx, rect.bottom - 4), (rect.left + 5, rect.centery)],
        )
    elif resource == "gold":
        pygame.draw.circle(surface, (255, 231, 117), rect.center, max(5, rect.width // 4))
    elif resource == "sugar":
        pygame.draw.circle(surface, (255, 255, 255), (rect.centerx - 4, rect.centery), 4)
        pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + 4, rect.centery + 2), 4)
    elif resource == "fertilizer":
        pygame.draw.circle(surface, (52, 96, 48), (rect.centerx, rect.centery + 3), 5)
        pygame.draw.line(surface, (190, 225, 137), (rect.centerx, rect.centery + 2), (rect.centerx, rect.top + 5), 2)
        pygame.draw.ellipse(surface, (190, 225, 137), (rect.centerx, rect.top + 6, 9, 6))
    elif resource == "oil":
        pygame.draw.circle(surface, (8, 10, 14), rect.center, max(5, rect.width // 4))
        pygame.draw.circle(surface, (76, 83, 93), (rect.centerx - 2, rect.centery - 3), 2)
    if show_label:
        label = RESOURCE_LABELS.get(resource, resource[:4].upper())
        rendered = font.render(label, True, BLACK if resource in ("gold", "sugar") else TEXT)
        surface.blit(rendered, rendered.get_rect(center=(rect.centerx, rect.bottom + 10)))


def draw_license_glyph(surface: pygame.Surface, license_key: str, rect: pygame.Rect, font: pygame.font.Font) -> None:
    if license_key == "smuggler":
        pygame.draw.rect(surface, (92, 72, 49), rect, border_radius=5)
        pygame.draw.rect(surface, (228, 196, 118), rect.inflate(-6, -6), 2, border_radius=4)
        pygame.draw.line(surface, (228, 196, 118), (rect.left + 8, rect.centery), (rect.right - 8, rect.centery), 2)
        pygame.draw.circle(surface, (228, 196, 118), rect.center, 4)
    else:
        pygame.draw.rect(surface, (20, 22, 28), rect, border_radius=5)
        skull_center = rect.center
        pygame.draw.circle(surface, (245, 245, 245), (skull_center[0], skull_center[1] - 2), 7)
        pygame.draw.rect(surface, (245, 245, 245), (skull_center[0] - 5, skull_center[1] + 4, 10, 6))
        pygame.draw.circle(surface, (20, 22, 28), (skull_center[0] - 3, skull_center[1] - 2), 1)
        pygame.draw.circle(surface, (20, 22, 28), (skull_center[0] + 3, skull_center[1] - 2), 1)
    pygame.draw.rect(surface, (220, 226, 229), rect, 1, border_radius=5)


def try_buy_license(
    player: PlayerState,
    license_key: str,
    round_number: int,
) -> bool:
    if player.country == "Pirates":
        return False
    current_expiry = player.licenses.get(license_key)
    if current_expiry is not None and current_expiry - round_number > LICENSE_RENEW_WINDOW:
        return False
    is_renewal = current_expiry is not None and current_expiry >= round_number
    price = LICENSES[license_key]["renewal" if is_renewal else "price"]
    if player.money < price:
        return False
    player.money -= price
    base_round = max(current_expiry or round_number - 1, round_number - 1)
    player.licenses[license_key] = base_round + LICENSE_DURATION_ROUNDS
    action = "renew" if is_renewal else "buy"
    record_transaction(player, round_number, -price, f"{action} {LICENSES[license_key]['label']} until R{player.licenses[license_key]}")
    return True


def expire_player_licenses(players: list[PlayerState], round_number: int) -> None:
    for player in players:
        expired = [license_key for license_key, expiry in player.licenses.items() if expiry < round_number]
        for license_key in expired:
            del player.licenses[license_key]
            record_transaction(player, round_number, 0, f"{LICENSES[license_key]['label']} expired")


def draw_panel_popup(
    surface: pygame.Surface,
    font: pygame.font.Font,
    title: str,
    lines: list[str],
    mouse_pos: tuple[int, int],
) -> None:
    if not lines:
        return
    max_body_lines = 20
    body_lines = lines[:max_body_lines]
    if len(lines) > max_body_lines:
        body_lines.append(f"+ {len(lines) - max_body_lines} more")
    text_lines = [title, *body_lines]
    width = max(font.size(line)[0] for line in text_lines) + 24
    height = len(text_lines) * (font.get_height() + 4) + 16
    x = mouse_pos[0] - width - 14
    y = mouse_pos[1] + 12
    if x < 8:
        x = mouse_pos[0] + 14
    if y + height > SCREEN_HEIGHT - 8:
        y = SCREEN_HEIGHT - height - 8
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (250, 249, 239), rect, border_radius=6)
    pygame.draw.rect(surface, (64, 88, 104), rect, 1, border_radius=6)
    text_y = y + 8
    for idx, line in enumerate(text_lines):
        color = (22, 38, 52) if idx == 0 else (58, 72, 82)
        draw_text(surface, font, line, (x + 12, text_y), color)
        text_y += font.get_height() + 4


def trade_info_lines(card: TradeCard) -> list[str]:
    lines = [
        f"Start: {card.start}",
        f"End: {card.end}",
        f"Profit: ${card.profit}",
        f"Status: {card.status}",
    ]
    if card.stolen_from:
        lines.append(f"Stolen from: {card.stolen_from}")
    return lines


def trade_card_display_line(card: TradeCard) -> str:
    stolen = f" stolen from {card.stolen_from}" if card.stolen_from else ""
    return f"{card.start} -> {card.end}  ${card.profit}  {card.status}{stolen}"


def draw_market_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left, SCREEN_HEIGHT - 48, 96, 34)
    pygame.draw.rect(surface, (67, 132, 221), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "Market", (rect.x + 20, rect.y + 8), TEXT)
    return rect


def draw_trade_card_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left + 110, SCREEN_HEIGHT - 48, 176, 34)
    pygame.draw.rect(surface, (54, 130, 94), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "Invest", (rect.x + 18, rect.y + 8), TEXT)
    return rect


def draw_new_treaty_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left + 300, SCREEN_HEIGHT - 48, 142, 34)
    pygame.draw.rect(surface, (126, 93, 55), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "New Treaty", (rect.x + 18, rect.y + 8), TEXT)
    return rect


def draw_transfer_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left + 456, SCREEN_HEIGHT - 48, 118, 34)
    pygame.draw.rect(surface, (116, 86, 151), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "Transfer", (rect.x + 20, rect.y + 8), TEXT)
    return rect


def draw_history_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left + 588, SCREEN_HEIGHT - 48, 108, 34)
    pygame.draw.rect(surface, (84, 104, 116), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "History", (rect.x + 20, rect.y + 8), TEXT)
    return rect


def draw_new_factory_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left + 710, SCREEN_HEIGHT - 48, 118, 34)
    pygame.draw.rect(surface, (52, 121, 82), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "Arrange", (rect.x + 24, rect.y + 8), TEXT)
    return rect


def draw_new_ship_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left + 840, SCREEN_HEIGHT - 48, 96, 34)
    pygame.draw.rect(surface, (45, 95, 132), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "New Ship", (rect.x + 10, rect.y + 8), TEXT)
    return rect


def draw_rules_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = pygame.Rect(MAP_RECT.left + 946, SCREEN_HEIGHT - 48, 86, 34)
    pygame.draw.rect(surface, (90, 98, 58), rect, border_radius=7)
    pygame.draw.rect(surface, (224, 232, 238), rect, 1, border_radius=7)
    draw_text(surface, font, "Rules", (rect.x + 20, rect.y + 8), TEXT)
    return rect


def draw_trade_card_options() -> list[TradeCard]:
    by_profit: dict[int, list[TradeCard]] = defaultdict(list)
    for card in TRADE_CARDS:
        by_profit[card.profit].append(card)
    if len(by_profit) >= 3:
        profits = random.sample(list(by_profit), 3)
        return [random.choice(by_profit[profit]) for profit in profits]
    return random.sample(TRADE_CARDS, min(3, len(TRADE_CARDS)))


def choose_trade_card(player: PlayerState, card: TradeCard) -> TradeCard:
    chosen = TradeCard(card.start, card.end, card.profit)
    player.trade_cards.append(chosen)
    return chosen


def try_buy_resource(
    player: PlayerState,
    resource: str,
    prices: dict[str, dict[str, int]],
    round_number: int | None = None,
) -> bool:
    price = prices[resource]["buy"]
    if player.money < price:
        return False
    player.money -= price
    player.resources[resource] = player.resources.get(resource, 0) + 1
    if round_number is not None:
        record_transaction(player, round_number, -price, f"buy {resource}")
    return True


def try_sell_resource(
    player: PlayerState,
    resource: str,
    prices: dict[str, dict[str, int]],
    round_number: int | None = None,
) -> bool:
    if player.resources.get(resource, 0) <= 0:
        return False
    player.resources[resource] -= 1
    price = prices[resource]["sell"]
    player.money += price
    if round_number is not None:
        record_transaction(player, round_number, price, f"sell {resource}")
    return True


def dynamic_bill(cost: dict[str, int], prices: dict[str, dict[str, int]]) -> int:
    return (
        cost.get("base_money", 0)
        + cost.get("wood", 0) * prices["wood"]["buy"]
        + cost.get("metal", 0) * prices["metal"]["buy"]
    )


def discounted_amount(amount: int) -> int:
    return max(1, math.ceil(amount / 2)) if amount else 0


def cost_for_player(player: PlayerState, cost: dict[str, int], category: str) -> dict[str, int]:
    if category == "ship" and player.country == "Russia":
        adjusted = dict(cost)
        for key in ("base_money", "wood", "metal"):
            adjusted[key] = discounted_amount(adjusted.get(key, 0))
        return adjusted
    if category == "factory" and player.country == "United States":
        adjusted = dict(cost)
        adjusted["base_money"] = discounted_amount(adjusted.get("base_money", 0))
        return adjusted
    return cost


def factory_cost_label(action: str, prices: dict[str, dict[str, int]] | None = None, player: PlayerState | None = None) -> str:
    cost = cost_for_player(player, FACTORY_COSTS[action], "factory") if player else FACTORY_COSTS[action]
    parts = []
    if prices:
        parts.append(f"${dynamic_bill(cost, prices)}")
    elif cost["base_money"]:
        parts.append(f"${cost['base_money']} + materials")
    for resource in ("wood", "metal"):
        if cost[resource]:
            parts.append(f"{resource} x{cost[resource]}")
    return ", ".join(parts) if parts else "free"


def can_pay_factory_cost(player: PlayerState, action: str, prices: dict[str, dict[str, int]]) -> bool:
    cost = cost_for_player(player, FACTORY_COSTS[action], "factory")
    return (
        player.money >= dynamic_bill(cost, prices)
        and player.resources.get("wood", 0) >= cost["wood"]
        and player.resources.get("metal", 0) >= cost["metal"]
    )


def can_build_factory(player: PlayerState, node: MapNode, action: str, prices: dict[str, dict[str, int]]) -> bool:
    if node.owner != player.country:
        return False
    if node.kind == "capital" or node.resource is None:
        return False
    if player.country == "Pirates" and node.resource == "shipyard":
        return False
    if action == "green" and node.factory_level is not None:
        return False
    if action == "red" and node.factory_level is not None:
        return False
    if action == "upgrade" and node.factory_level != "green":
        return False
    return can_pay_factory_cost(player, action, prices)


def build_factory(
    player: PlayerState,
    node: MapNode,
    action: str,
    prices: dict[str, dict[str, int]],
    round_number: int | None = None,
    history_events: list[HistoryEvent] | None = None,
) -> bool:
    if not can_build_factory(player, node, action, prices):
        return False
    cost = cost_for_player(player, FACTORY_COSTS[action], "factory")
    money_cost = dynamic_bill(cost, prices)
    player.money -= money_cost
    player.resources["wood"] = player.resources.get("wood", 0) - cost["wood"]
    player.resources["metal"] = player.resources.get("metal", 0) - cost["metal"]
    node.factory_level = "green" if action == "green" else "red"
    node.factory_owner = player.country
    if round_number is not None and money_cost:
        detail = f"{action} factory at {display_place_name(node.name)}"
        record_transaction(player, round_number, -money_cost, detail)
        if history_events is not None:
            history_events.append(
                HistoryEvent(round_number, "factory", f"{player.country} built a factory", [detail, f"Bill: ${money_cost}"])
            )
    return True


def player_factory_lines(player: PlayerState) -> list[str]:
    factories = [
        node
        for node in MAP_NODES.values()
        if node.factory_owner == player.country and node.factory_level
    ]
    if not factories:
        return ["No factories"]
    return [
        f"{display_place_name(node.name)}: {node.factory_level} factory, {node.resource or 'none'}"
        for node in sorted(factories, key=lambda item: item.name)
    ]


def ship_build_cost_label(player: PlayerState, ship_kind: str, prices: dict[str, dict[str, int]]) -> str:
    actual_kind = "Pirate" if player.country == "Pirates" else ship_kind
    cost = cost_for_player(player, SHIP_COSTS.get(actual_kind, SHIP_COSTS["Warship"]), "ship")
    return f"${dynamic_bill(cost, prices)}, wood x{cost['wood']}, metal x{cost['metal']}"


def port_ship_capacity_available(location: str, players: list[PlayerState]) -> bool:
    return len(ships_at_location(players, location)) < 3


def shipyard_level(node: MapNode) -> str | None:
    if node.kind == "capital":
        return "capital"
    if node.resource != "shipyard":
        return None
    return node.factory_level


def can_build_ship_at(
    player: PlayerState,
    node: MapNode,
    ship_kind: str,
    players: list[PlayerState],
    prices: dict[str, dict[str, int]],
) -> bool:
    if node.owner != player.country:
        return False
    level = shipyard_level(node)
    if level is None:
        return False
    if ship_kind in ("Warship", "Pirate") and level == "green":
        return False
    if not port_ship_capacity_available(node.name, players):
        return False
    actual_kind = "Pirate" if player.country == "Pirates" else ship_kind
    cost = cost_for_player(player, SHIP_COSTS.get(actual_kind, SHIP_COSTS["Warship"]), "ship")
    return (
        player.money >= dynamic_bill(cost, prices)
        and player.resources.get("wood", 0) >= cost["wood"]
        and player.resources.get("metal", 0) >= cost["metal"]
    )


def queued_ship_count(location: str, pending_builds: list[PendingShipBuild], owner: str | None = None) -> int:
    return sum(
        1
        for build in pending_builds
        if build.location == location and (owner is None or build.owner == owner)
    )


def can_queue_ship_at(
    player: PlayerState,
    node: MapNode,
    ship_kind: str,
    players: list[PlayerState],
    pending_builds: list[PendingShipBuild],
    prices: dict[str, dict[str, int]],
) -> bool:
    if not can_build_ship_at(player, node, ship_kind, players, prices):
        return False
    return len(ships_at_location(players, node.name)) + queued_ship_count(node.name, pending_builds) < 3


def queue_ship_build(
    player: PlayerState,
    node: MapNode,
    ship_kind: str,
    players: list[PlayerState],
    pending_builds: list[PendingShipBuild],
    current_round: int,
    prices: dict[str, dict[str, int]],
    history_events: list[HistoryEvent] | None = None,
) -> bool:
    if not can_queue_ship_at(player, node, ship_kind, players, pending_builds, prices):
        return False
    actual_kind = "Pirate" if player.country == "Pirates" else ship_kind
    cost = cost_for_player(player, SHIP_COSTS.get(actual_kind, SHIP_COSTS["Warship"]), "ship")
    money_cost = dynamic_bill(cost, prices)
    player.money -= money_cost
    player.resources["wood"] -= cost["wood"]
    player.resources["metal"] -= cost["metal"]
    pending_builds.append(PendingShipBuild(player.country, node.name, actual_kind, current_round + 1))
    record_transaction(player, current_round, -money_cost, f"build {actual_kind} at {display_place_name(node.name)}")
    if history_events is not None:
        history_events.append(
            HistoryEvent(current_round, "build", f"{player.country} queued a {actual_kind}", [f"At {display_place_name(node.name)}", f"Bill: ${money_cost}"])
        )
    return True


def complete_pending_ship_builds(
    player: PlayerState,
    pending_builds: list[PendingShipBuild],
    current_round: int,
) -> list[PendingShipBuild]:
    completed = []
    remaining = []
    for build in pending_builds:
        if build.owner == player.country and build.ready_round <= current_round:
            ship_count = len(player.ships) + len(completed) + 1
            kind = "Pirate" if player.country == "Pirates" else build.kind
            name = "pirate" if player.country == "Pirates" else f"{player.country} {kind.lower()} {ship_count}"
            player.ships.append(
                Ship(name=name, owner=player.country, location=build.location, kind=kind, last_port_round=current_round)
            )
            completed.append(build)
        else:
            remaining.append(build)
    pending_builds[:] = remaining
    return completed


def draw_trade_card_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    player: PlayerState,
    trade_card_options: list[TradeCard],
    selected_card: TradeCard | None,
    confirmed: bool,
) -> tuple[pygame.Rect, pygame.Rect, list[tuple[pygame.Rect, TradeCard]]]:
    surface.fill((18, 28, 38))
    panel = pygame.Rect(170, 80, SCREEN_WIDTH - 340, SCREEN_HEIGHT - 160)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 38
    y = panel.y + 28
    draw_text(surface, title_font, "Choose Trade Card", (x, y), (22, 38, 52))
    draw_owner_marker(surface, player.country, (x + 205, y + 18), font, size=28)
    draw_text(surface, font, player.country, (x + 228, y + 9), (42, 58, 70))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)
    confirm_rect = pygame.Rect(panel.right - 210, panel.y + 24, 92, 32)
    confirm_enabled = selected_card is not None and not confirmed
    pygame.draw.rect(surface, (42, 130, 79) if confirm_enabled else (130, 138, 142), confirm_rect, border_radius=6)
    draw_text(surface, small_font, "Confirm" if not confirmed else "Confirmed", (confirm_rect.x + 12, confirm_rect.y + 8), TEXT)

    option_rects: list[tuple[pygame.Rect, TradeCard]] = []
    cards_y = y + 78
    card_w = 300
    card_h = 245
    for idx, card in enumerate(trade_card_options):
        card_rect = pygame.Rect(x + idx * (card_w + 24), cards_y, card_w, card_h)
        option_rects.append((card_rect, card))
        selected = card is selected_card
        pygame.draw.rect(surface, (255, 252, 235), card_rect, border_radius=10)
        pygame.draw.rect(surface, (42, 130, 79) if selected else (132, 102, 49), card_rect, 3 if selected else 2, border_radius=10)
        draw_text(surface, font, f"Option {idx + 1}", (card_rect.x + 20, card_rect.y + 18), (132, 102, 49))
        draw_wrapped_text(
            surface,
            font,
            card.start,
            pygame.Rect(card_rect.x + 20, card_rect.y + 58, card_rect.width - 40, 56),
            (22, 38, 52),
        )
        draw_text(surface, font, "to", (card_rect.x + 20, card_rect.y + 118), (87, 101, 112))
        draw_wrapped_text(
            surface,
            font,
            card.end,
            pygame.Rect(card_rect.x + 20, card_rect.y + 148, card_rect.width - 40, 50),
            (22, 38, 52),
        )
        draw_text(surface, font, f"Profit: ${card.profit}", (card_rect.x + 20, card_rect.y + 207), (42, 105, 72))
        if selected:
            draw_text(surface, small_font, "Selected", (card_rect.right - 78, card_rect.y + 21), (42, 105, 72))
    info_x = x
    info_y = cards_y + card_h + 22
    draw_text(surface, font, "Trade Info", (info_x, info_y), (22, 38, 52))
    if selected_card:
        info = trade_card_display_line(selected_card)
        draw_text(
            surface,
            small_font,
            info,
            (info_x + 120, info_y + 4),
            (42, 105, 72),
        )
    else:
        draw_text(surface, small_font, "Select one option, then Confirm.", (info_x + 120, info_y + 4), (87, 101, 112))

    list_x = x
    list_top = cards_y + card_h + 62
    draw_text(surface, font, f"{player.country} Cards ({len(player.trade_cards)})", (list_x, list_top), (22, 38, 52))
    list_y = list_top + 32
    if not player.trade_cards:
        draw_text(surface, small_font, "No trade cards yet.", (list_x, list_y), (87, 101, 112))
    else:
        for card in player.trade_cards[-8:]:
            draw_text(surface, small_font, trade_card_display_line(card), (list_x, list_y), (58, 72, 82))
            list_y += 22
        if len(player.trade_cards) > 8:
            draw_text(surface, small_font, f"+ {len(player.trade_cards) - 8} older cards", (list_x, list_y), (87, 101, 112))

    draw_text(surface, small_font, "Esc or Close returns to the map.", (panel.x + 38, panel.bottom - 38), (87, 101, 112))
    return close_rect, confirm_rect, option_rects


def draw_market_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    player: PlayerState,
    prices: dict[str, dict[str, int]],
    round_number: int,
    scroll_offset: int,
) -> tuple[pygame.Rect, dict[str, pygame.Rect], dict[str, pygame.Rect], dict[str, pygame.Rect], int]:
    surface.fill((20, 28, 36))
    panel = pygame.Rect(140, 80, SCREEN_WIDTH - 280, SCREEN_HEIGHT - 160)
    pygame.draw.rect(surface, (238, 241, 236), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 34
    y = panel.y + 26
    draw_text(surface, title_font, "Resource Market", (x, y), (22, 38, 52))
    draw_owner_marker(surface, player.country, (x + 270, y + 18), font, size=28)
    draw_text(surface, font, f"{player.country}   Money: ${player.money}", (x + 292, y + 9), (42, 58, 70))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    content_top = panel.y + 100
    content_bottom = panel.bottom - 52
    content_y = content_top - scroll_offset
    y = content_y
    headers = [("Resource", x), ("You Have", x + 250), ("Buy", x + 410), ("Sell", x + 570)]
    for label, hx in headers:
        if content_top - 34 <= y <= content_bottom:
            draw_text(surface, font, label, (hx, y), (42, 58, 70))
    y += 34

    buy_rects: dict[str, pygame.Rect] = {}
    sell_rects: dict[str, pygame.Rect] = {}
    license_rects: dict[str, pygame.Rect] = {}
    previous_clip = surface.get_clip()
    surface.set_clip(panel.inflate(-40, -112))
    for resource in RESOURCE_ORDER:
        row = pygame.Rect(x - 12, y - 8, panel.width - 44, 66)
        if row.bottom >= content_top and row.top <= content_bottom:
            pygame.draw.rect(surface, (225, 231, 227), row, border_radius=6)
            glyph = pygame.Rect(x, y + 6, 44, 28)
            draw_resource_glyph(surface, resource, glyph, small_font, show_label=False)
            draw_text(surface, font, resource.capitalize(), (x + 62, y + 10), (22, 38, 52))
            draw_text(surface, font, str(player.resources.get(resource, 0)), (x + 278, y + 10), (22, 38, 52))

        buy_price = prices[resource]["buy"]
        sell_price = prices[resource]["sell"]
        buy_rect = pygame.Rect(x + 400, y + 4, 110, 34)
        sell_rect = pygame.Rect(x + 560, y + 4, 110, 34)
        buy_rects[resource] = buy_rect
        sell_rects[resource] = sell_rect
        buy_enabled = player.money >= buy_price
        sell_enabled = player.resources.get(resource, 0) > 0
        if row.bottom >= content_top and row.top <= content_bottom:
            pygame.draw.rect(surface, (54, 130, 94) if buy_enabled else (130, 138, 142), buy_rect, border_radius=6)
            pygame.draw.rect(surface, (157, 97, 54) if sell_enabled else (130, 138, 142), sell_rect, border_radius=6)
            draw_text(surface, small_font, f"Buy ${buy_price}", (buy_rect.x + 25, buy_rect.y + 9), TEXT)
            draw_text(surface, small_font, f"Sell ${sell_price}", (sell_rect.x + 23, sell_rect.y + 9), TEXT)
        y += 78

    y += 10
    draw_text(surface, font, "Letter of Marque", (x, y), (22, 38, 52))
    y += 40
    for license_key, info in LICENSES.items():
        row = pygame.Rect(x - 12, y - 8, panel.width - 44, 74)
        buy_rect = pygame.Rect(x + 650, y + 10, 126, 34)
        license_rects[license_key] = buy_rect
        expiry = player.licenses.get(license_key)
        owned = expiry is not None
        can_renew = owned and expiry - round_number <= LICENSE_RENEW_WINDOW
        pirate_blocked = player.country == "Pirates"
        license_price = info["renewal"] if can_renew else info["price"]
        can_buy = player.money >= license_price and not pirate_blocked and (not owned or can_renew)
        if row.bottom >= content_top and row.top <= content_bottom:
            pygame.draw.rect(surface, (225, 231, 227), row, border_radius=6)
            draw_license_glyph(surface, license_key, pygame.Rect(x, y + 8, 46, 32), small_font)
            draw_text(surface, font, info["label"], (x + 62, y + 8), (22, 38, 52))
            if pirate_blocked:
                detail = "Pirates cannot buy licenses"
            elif owned:
                detail = f"Expires R{expiry}; renewal ${info['renewal']} opens R{expiry - LICENSE_RENEW_WINDOW}"
            else:
                detail = f"Price: ${license_price}; valid {LICENSE_DURATION_ROUNDS} rounds"
            draw_text(surface, small_font, detail, (x + 62, y + 35), (58, 72, 82))
            pygame.draw.rect(surface, (54, 130, 94) if can_buy else (130, 138, 142), buy_rect, border_radius=6)
            button_label = "Blocked" if pirate_blocked else ("Renew" if can_renew else ("Owned" if owned else "Buy"))
            draw_text(surface, small_font, button_label, (buy_rect.x + 32, buy_rect.y + 9), TEXT)
        y += 86
    surface.set_clip(previous_clip)

    content_height = y - content_y
    max_scroll = max(0, content_height - (content_bottom - content_top))
    if max_scroll:
        draw_text(surface, small_font, "Use mouse wheel to scroll.", (panel.right - 230, panel.bottom - 38), (87, 101, 112))
    draw_text(surface, small_font, "Esc or Close returns to the map.", (panel.x + 34, panel.bottom - 38), (87, 101, 112))
    return close_rect, buy_rects, sell_rects, license_rects, max_scroll


def draw_build_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    player: PlayerState,
    prices: dict[str, dict[str, int]],
) -> tuple[pygame.Rect, list[tuple[str, str, pygame.Rect]]]:
    surface.fill((19, 30, 26))
    panel = pygame.Rect(110, 58, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 116)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 34
    y = panel.y + 24
    draw_text(surface, title_font, "New Factory", (x, y), (22, 38, 52))
    draw_owner_marker(surface, player.country, (x + 220, y + 18), font, size=28)
    draw_text(surface, font, f"{player.country}   Money: ${player.money}", (x + 244, y + 9), (42, 58, 70))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    y += 58
    cost_line = (
        f"Green: {factory_cost_label('green', prices, player)}    "
        f"Red: {factory_cost_label('red', prices, player)}    "
        f"Upgrade: {factory_cost_label('upgrade', prices, player)}"
    )
    draw_text(surface, small_font, cost_line, (x, y), (58, 72, 82))
    y += 28
    resource_line = f"Available: wood x{player.resources.get('wood', 0)}, metal x{player.resources.get('metal', 0)}"
    draw_text(surface, small_font, resource_line, (x, y), (58, 72, 82))
    y += 42

    headers = [("Port", x), ("Resource", x + 290), ("Factory", x + 430), ("Actions", x + 580)]
    for label, hx in headers:
        draw_text(surface, font, label, (hx, y), (42, 58, 70))
    y += 32

    action_rects: list[tuple[str, str, pygame.Rect]] = []
    ports = sorted(
        [
            port
            for port in player.ports
            if port.kind != "capital" and port.resource is not None
        ],
        key=lambda port: port.name,
    )
    for node in ports[:13]:
        row = pygame.Rect(x - 12, y - 7, panel.width - 44, 42)
        pygame.draw.rect(surface, (225, 231, 227), row, border_radius=6)
        draw_text(surface, small_font, display_place_name(node.name), (x, y + 6), (22, 38, 52))
        draw_text(surface, small_font, node.resource or "none", (x + 290, y + 6), (58, 72, 82))
        factory_text = node.factory_level or "none"
        factory_color = (42, 105, 72) if node.factory_level == "green" else ((157, 63, 58) if node.factory_level == "red" else (87, 101, 112))
        draw_text(surface, small_font, factory_text, (x + 430, y + 6), factory_color)
        button_specs = [
            ("green", "Green", x + 580, (54, 130, 94)),
            ("red", "Red", x + 660, (157, 63, 58)),
            ("upgrade", "Upgrade", x + 730, (112, 91, 151)),
        ]
        for action, label, bx, color in button_specs:
            rect = pygame.Rect(bx, y - 1, 72 if action != "upgrade" else 86, 28)
            action_rects.append((node.name, action, rect))
            enabled = can_build_factory(player, node, action, prices)
            pygame.draw.rect(surface, color if enabled else (130, 138, 142), rect, border_radius=5)
            draw_text(surface, small_font, label, (rect.x + 9, rect.y + 7), TEXT)
        y += 48
        if y > panel.bottom - 64:
            break
    if len(ports) > 13:
        draw_text(surface, small_font, f"+ {len(ports) - 13} more ports not shown", (x, panel.bottom - 62), (87, 101, 112))

    draw_text(surface, small_font, "Esc or Close returns to the map.", (panel.x + 34, panel.bottom - 38), (87, 101, 112))
    return close_rect, action_rects


def draw_arrange_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    player: PlayerState,
    scroll: int,
    prices: dict[str, dict[str, int]],
) -> tuple[pygame.Rect, list[tuple[str, str, str, pygame.Rect]], int]:
    surface.fill((19, 30, 26))
    panel = pygame.Rect(72, 42, SCREEN_WIDTH - 144, SCREEN_HEIGHT - 84)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 30
    y = panel.y + 22
    draw_text(surface, title_font, "Arrange Ports", (x, y), (22, 38, 52))
    draw_owner_marker(surface, player.country, (x + 230, y + 18), font, size=28)
    draw_text(surface, font, player.country, (x + 254, y + 9), (42, 58, 70))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    y += 58
    draw_text(
        surface,
        small_font,
        "Merchant ships and Japanese ships are always accepted. Japan still pays fees.",
        (x, y),
        (58, 72, 82),
    )
    y += 18
    cost_line = (
        f"Factory cost - Green: {factory_cost_label('green', prices, player)}    "
        f"Red: {factory_cost_label('red', prices, player)}    Upgrade: {factory_cost_label('upgrade', prices, player)}"
    )
    draw_text(surface, small_font, cost_line, (x, y), (58, 72, 82))
    y += 30

    action_rects: list[tuple[str, str, str, pygame.Rect]] = []
    ports = sorted([port for port in player.ports if port.owner == player.country], key=lambda item: item.name)
    visible_count = 6
    max_scroll = max(0, len(ports) - visible_count)
    scroll = max(0, min(max_scroll, scroll))
    mode_specs = [
        ("default", "Default"),
        ("allow_only", "Only"),
        ("reject_selected", "Reject"),
        ("reject_all", "Reject All"),
        ("open_all", "Open All"),
    ]
    chip_w = 76
    free_chip_w = 76
    for node in ports[scroll : scroll + visible_count]:
        row = pygame.Rect(x - 12, y - 6, panel.width - 36, 104)
        pygame.draw.rect(surface, (225, 231, 227), row, border_radius=6)
        draw_text(surface, small_font, display_place_name(node.name), (x, y + 4), (22, 38, 52))
        draw_text(surface, small_font, f"Resource: {node.resource or 'none'}", (x, y + 26), (58, 72, 82))
        factory_text = node.factory_level or "none"
        draw_text(surface, small_font, f"Factory: {factory_text}", (x, y + 48), (58, 72, 82))
        entry_text = "Pirate ports: open/free" if player.country == "Pirates" else port_entry_policy_line(node)
        draw_text(surface, small_font, f"Entry: {entry_text}", (x, y + 70), (58, 72, 82))
        if node.free_entry_countries:
            free_text = ", ".join(OWNER_LEGEND_LABELS.get(country, country) for country in sorted(node.free_entry_countries))
            draw_text(surface, small_font, f"Free: {free_text}", (x + 170, y + 70), (58, 72, 82))
        bx = x + 250
        if player.country == "Pirates":
            draw_text(surface, small_font, "Entry controls locked for Pirates", (bx, y + 4), (157, 63, 58))
        else:
            for mode, label in mode_specs:
                rect = pygame.Rect(bx, y + 2, 78 if mode != "reject_all" else 90, 24)
                action_rects.append(("mode", node.name, mode, rect))
                selected = node.entry_mode == mode
                pygame.draw.rect(surface, (52, 121, 82) if selected else (132, 142, 149), rect, border_radius=5)
                draw_text(surface, small_font, label, (rect.x + 7, rect.y + 5), TEXT)
                bx = rect.right + 6
        bx = x + 250
        if player.country != "Pirates":
            draw_text(surface, small_font, "Countries", (bx, y + 32), (58, 72, 82))
            bx += 82
            for country in EMPIRE_ORDER:
                if country == player.country:
                    continue
                rect = pygame.Rect(bx, y + 29, chip_w, 22)
                action_rects.append(("toggle_country", node.name, country, rect))
                selected = country in node.entry_countries
                pygame.draw.rect(surface, OWNER_COLORS[country] if selected else (204, 211, 213), rect, border_radius=5)
                draw_text(surface, small_font, OWNER_LEGEND_LABELS.get(country, country), (rect.x + 7, rect.y + 4), BLACK if selected and country != "Pirates" else (22, 38, 52))
                bx = rect.right + 5
        bx = x + 250
        if player.country != "Pirates":
            draw_text(surface, small_font, "Free", (bx, y + 55), (58, 72, 82))
            bx += 82
            for country in EMPIRE_ORDER:
                if country == player.country:
                    continue
                rect = pygame.Rect(bx, y + 52, free_chip_w, 22)
                action_rects.append(("toggle_free", node.name, country, rect))
                selected = country in node.free_entry_countries
                pygame.draw.rect(surface, OWNER_COLORS[country] if selected else (204, 211, 213), rect, border_radius=5)
                draw_text(surface, small_font, OWNER_LEGEND_LABELS.get(country, country), (rect.x + 7, rect.y + 4), BLACK if selected and country != "Pirates" else (22, 38, 52))
                bx = rect.right + 5
        factory_specs = [
            ("green", "Green", x + 920, (54, 130, 94)),
            ("red", "Red", x + 996, (157, 63, 58)),
            ("upgrade", "Upgrade", x + 1062, (112, 91, 151)),
        ]
        for action, label, fx, color in factory_specs:
            rect = pygame.Rect(fx, y + 74, 72 if action != "upgrade" else 86, 24)
            action_rects.append(("factory", node.name, action, rect))
            enabled = can_build_factory(player, node, action, prices)
            pygame.draw.rect(surface, color if enabled else (130, 138, 142), rect, border_radius=5)
            draw_text(surface, small_font, label, (rect.x + 8, rect.y + 5), TEXT)
        y += 112
        if y > panel.bottom - 72:
            break
    if len(ports) > visible_count:
        draw_text(surface, small_font, f"Scroll: showing {scroll + 1}-{min(len(ports), scroll + visible_count)} of {len(ports)} ports", (x, panel.bottom - 58), (87, 101, 112))
    draw_text(surface, small_font, "Default: all ships can enter and foreign ships pay fee. Pirate ports are open/free. Pirates cannot build shipyard factories.", (x, panel.bottom - 34), (87, 101, 112))
    return close_rect, action_rects, max_scroll


def draw_new_ship_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    player: PlayerState,
    players: list[PlayerState],
    pending_builds: list[PendingShipBuild],
    prices: dict[str, dict[str, int]],
) -> tuple[pygame.Rect, list[tuple[str, str, pygame.Rect]]]:
    surface.fill((18, 29, 38))
    panel = pygame.Rect(110, 58, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 116)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 34
    y = panel.y + 24
    draw_text(surface, title_font, "New Ship", (x, y), (22, 38, 52))
    draw_owner_marker(surface, player.country, (x + 150, y + 18), font, size=28)
    draw_text(surface, font, f"{player.country}   Money: ${player.money}", (x + 174, y + 9), (42, 58, 70))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    y += 58
    draw_text(
        surface,
        small_font,
        f"Merchant: {ship_build_cost_label(player, 'Merchant', prices)}    Warship: {ship_build_cost_label(player, 'Warship', prices)}",
        (x, y),
        (58, 72, 82),
    )
    y += 26
    draw_text(
        surface,
        small_font,
        f"Available: wood x{player.resources.get('wood', 0)}, metal x{player.resources.get('metal', 0)}",
        (x, y),
        (58, 72, 82),
    )
    y += 42

    headers = [("Port", x), ("Yard", x + 290), ("Ships", x + 430), ("Actions", x + 570)]
    for label, hx in headers:
        draw_text(surface, font, label, (hx, y), (42, 58, 70))
    y += 32

    ship_rects: list[tuple[str, str, pygame.Rect]] = []
    ports = sorted(
        [
            port
            for port in player.ports
            if port.kind == "capital" or (port.resource == "shipyard" and port.factory_level)
        ],
        key=lambda port: port.name,
    )
    for node in ports[:13]:
        row = pygame.Rect(x - 12, y - 7, panel.width - 44, 42)
        pygame.draw.rect(surface, (225, 231, 227), row, border_radius=6)
        draw_text(surface, small_font, display_place_name(node.name), (x, y + 6), (22, 38, 52))
        level = shipyard_level(node) or "none"
        draw_text(surface, small_font, level, (x + 290, y + 6), (58, 72, 82))
        docked = len(ships_at_location(players, node.name))
        queued = queued_ship_count(node.name, pending_builds)
        draw_text(surface, small_font, f"{docked}/3 docked, +{queued}", (x + 430, y + 6), (58, 72, 82))
        if player.country == "Pirates":
            button_specs = [("Pirate", "Pirate", x + 570, (35, 35, 42))]
        else:
            button_specs = [
                ("Merchant", "Merchant", x + 570, (54, 130, 94)),
                ("Warship", "Warship", x + 680, (157, 63, 58)),
            ]
        for ship_kind, label, bx, color in button_specs:
            rect = pygame.Rect(bx, y - 1, 96, 28)
            ship_rects.append((node.name, ship_kind, rect))
            enabled = can_queue_ship_at(player, node, ship_kind, players, pending_builds, prices)
            pygame.draw.rect(surface, color if enabled else (130, 138, 142), rect, border_radius=5)
            draw_text(surface, small_font, label, (rect.x + 14, rect.y + 7), TEXT)
        y += 48
        if y > panel.bottom - 64:
            break
    if len(ports) > 13:
        draw_text(surface, small_font, f"+ {len(ports) - 13} more shipyards not shown", (x, panel.bottom - 62), (87, 101, 112))

    draw_text(surface, small_font, "Queued ships are completed at this player's next round. Green shipyard factory builds merchants only.", (panel.x + 34, panel.bottom - 38), (87, 101, 112))
    return close_rect, ship_rects


def price_snapshot_lines(prices: dict[str, dict[str, int]]) -> list[str]:
    return [
        f"{RESOURCE_LABELS[resource]} buy ${prices[resource]['buy']} / sell ${prices[resource]['sell']}"
        for resource in RESOURCE_ORDER
    ]


def active_trade_card_cost(active_news: list[NewsEvent]) -> int:
    costs = [event.trade_card_cost for event in active_news if event.kind == "trade_card_discount" and event.trade_card_cost]
    return min(costs) if costs else 200


def apply_resource_news_delta(prices: dict[str, dict[str, int]], resource: str, delta: int) -> None:
    for side in ("buy", "sell"):
        base_price = RESOURCE_PRICES[resource][side]
        prices[resource][side] = max(base_price, prices[resource][side] + delta)


def create_maritime_news(round_number: int) -> NewsEvent:
    center = random.choice(sorted(MAP_NODES))
    ports = ports_within_course_distance(center, 2)
    if random.choice([True, False]):
        return NewsEvent(
            category="maritime",
            kind="plague",
            title="Maritime News: Port Plague",
            details=[
                f"Outbreak around {display_place_name(center)}.",
                "Affected ports cannot move ships out; foreign ships cannot enter.",
                "Duration: 3 rounds.",
            ],
            ports=ports,
            expires_round=round_number + 2,
        )
    return NewsEvent(
        category="maritime",
        kind="monsoon",
        title="Maritime News: Monsoon Winds",
        details=[
            f"Monsoon affects {display_place_name(center)} and nearby ports.",
            "Ships starting from affected ports move faster: pirates +1, others +2.",
            "Duration: 3 rounds.",
        ],
        ports=ports,
        expires_round=round_number + 2,
    )


def create_economic_news(round_number: int, prices: dict[str, dict[str, int]]) -> NewsEvent:
    if random.choice([True, False]):
        resource = random.choice(RESOURCE_ORDER)
        if random.choice([True, False]):
            delta = random.randint(30, 100)
            direction = "rises"
        else:
            delta = -random.randint(20, 50)
            direction = "falls"
        apply_resource_news_delta(prices, resource, delta)
        return NewsEvent(
            category="economic",
            kind="resource_price",
            title="Economic News: Commodity Shock",
            details=[
                f"{RESOURCE_LABELS[resource]} price {direction} by ${abs(delta)}.",
                "Temporary market effect lasts 3 rounds.",
            ],
            expires_round=round_number + 2,
            resource=resource,
            price_delta=delta,
        )
    cost = random.randint(100, 180)
    return NewsEvent(
        category="economic",
        kind="trade_card_discount",
        title="Economic News: Trade Intelligence Discount",
        details=[
            f"Trade card draw cost is reduced to ${cost}.",
            "Duration: 5 rounds.",
        ],
        expires_round=round_number + 4,
        trade_card_cost=cost,
    )


def expire_news_events(
    active_news: list[NewsEvent],
    prices: dict[str, dict[str, int]],
    round_number: int,
    history_events: list[HistoryEvent],
) -> None:
    remaining = []
    for event in active_news:
        if round_number <= event.expires_round:
            remaining.append(event)
            continue
        if event.kind == "resource_price" and event.resource and event.price_delta:
            apply_resource_news_delta(prices, event.resource, -event.price_delta)
        history_events.append(
            HistoryEvent(
                round_number=round_number,
                kind="news",
                title=f"Expired: {event.title}",
                details=event.details[:2],
            )
        )
    active_news[:] = remaining


def append_news_history(history_events: list[HistoryEvent], round_number: int, events: list[NewsEvent]) -> None:
    for event in events:
        extra = []
        if event.ports:
            names = ", ".join(display_place_name(port) for port in sorted(event.ports)[:6])
            extra.append(f"Ports: {names}" + (" ..." if len(event.ports) > 6 else ""))
        history_events.append(
            HistoryEvent(
                round_number=round_number,
                kind="news",
                title=event.title,
                details=[*event.details, *extra],
            )
        )


def draw_history_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    prices: dict[str, dict[str, int]],
    history_events: list[HistoryEvent],
    scroll_offset: int,
) -> tuple[pygame.Rect, int]:
    surface.fill((20, 27, 34))
    panel = pygame.Rect(120, 58, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 116)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 34
    y = panel.y + 24
    draw_text(surface, title_font, "Game History", (x, y), (22, 38, 52))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    y += 64
    price_panel = pygame.Rect(x, y, panel.width - 68, 98)
    pygame.draw.rect(surface, (225, 231, 227), price_panel, border_radius=8)
    draw_text(surface, font, "Current Resource Prices", (price_panel.x + 14, price_panel.y + 12), (22, 38, 52))
    price_x = price_panel.x + 14
    price_y = price_panel.y + 42
    for idx, resource in enumerate(RESOURCE_ORDER):
        col = idx % 3
        row = idx // 3
        pos_x = price_x + col * 300
        pos_y = price_y + row * 26
        draw_resource_glyph(surface, resource, pygame.Rect(pos_x, pos_y - 2, 28, 18), small_font, show_label=False)
        draw_text(surface, small_font, f"{RESOURCE_LABELS[resource]} buy ${prices[resource]['buy']} / sell ${prices[resource]['sell']}", (pos_x + 38, pos_y), (42, 58, 70))

    y = price_panel.bottom + 24
    draw_text(surface, font, "Events", (x, y), (22, 38, 52))
    y += 32
    if not history_events:
        draw_text(surface, small_font, "No events yet.", (x, y), (87, 101, 112))
    else:
        reversed_events = list(reversed(history_events))
        max_scroll = max(0, len(reversed_events) - 1)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        visible_events = reversed_events[scroll_offset:]
        y_event = y
        visible_count = 0
        for event in visible_events:
            row_height = 28 + len(event.details[:3]) * 18
            row = pygame.Rect(x, y_event - 6, panel.width - 68, row_height)
            pygame.draw.rect(surface, (255, 252, 235), row, border_radius=6)
            color = (157, 63, 58) if event.kind == "war" else (42, 105, 72)
            draw_text(surface, small_font, f"R{event.round_number}  {event.title}", (row.x + 12, row.y + 8), color)
            detail_y = row.y + 28
            for detail in event.details[:3]:
                draw_text(surface, small_font, detail, (row.x + 24, detail_y), (58, 72, 82))
                detail_y += 18
            y_event += row_height + 8
            visible_count += 1
            if y_event > panel.bottom - 58:
                if scroll_offset + visible_count < len(reversed_events):
                    draw_text(surface, small_font, "Scroll down for older events", (x, panel.bottom - 42), (87, 101, 112))
                break
        if scroll_offset > 0:
            draw_text(surface, small_font, "Scroll up for newer events", (panel.right - 210, panel.bottom - 42), (87, 101, 112))
    max_scroll = max(0, len(history_events) - 1)

    draw_text(surface, small_font, "Esc or Close returns to the map.", (panel.x + 34, panel.bottom - 38), (87, 101, 112))
    return close_rect, max_scroll


def draw_rules_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    scroll_offset: int,
) -> tuple[pygame.Rect, int]:
    surface.fill((18, 27, 35))
    panel = pygame.Rect(120, 58, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 116)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 34
    y = panel.y + 24
    draw_text(surface, title_font, "Game Rules", (x, y), (22, 38, 52))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    content_top = panel.y + 86
    content_bottom = panel.bottom - 52
    previous_clip = surface.get_clip()
    surface.set_clip(pygame.Rect(panel.x + 24, content_top, panel.width - 48, content_bottom - content_top))
    y = content_top - scroll_offset
    for idx, paragraph in enumerate(GAME_RULES):
        is_heading = idx % 2 == 0
        if is_heading:
            if y > content_top - 34 and y < content_bottom:
                draw_text(surface, font, paragraph, (x, y), (22, 38, 52))
            y += 28
        else:
            if y < content_bottom and y + 96 > content_top:
                y = draw_wrapped_text(
                    surface,
                    small_font,
                    paragraph,
                    pygame.Rect(x + 12, y, panel.width - 92, 120),
                    (58, 72, 82),
                    4,
                )
            else:
                words = paragraph.split()
                line_count = max(1, math.ceil(max(1, small_font.size(paragraph)[0]) / max(1, panel.width - 92)))
                y += line_count * (small_font.get_height() + 4)
            y += 18
    surface.set_clip(previous_clip)
    content_height = y + scroll_offset - content_top
    max_scroll = max(0, content_height - (content_bottom - content_top))
    if max_scroll:
        draw_text(surface, small_font, "Use mouse wheel to scroll rules.", (panel.right - 236, panel.bottom - 38), (87, 101, 112))
    draw_text(surface, small_font, "Esc or Close returns to the map.", (panel.x + 34, panel.bottom - 38), (87, 101, 112))
    return close_rect, max_scroll


def draw_round_limit_controls(
    surface: pygame.Surface,
    font: pygame.font.Font,
    round_number: int,
    max_rounds: int,
) -> tuple[pygame.Rect, pygame.Rect]:
    panel = pygame.Rect(MAP_RECT.left, MAP_RECT.top - 30, 206, 26)
    pygame.draw.rect(surface, (232, 240, 244), panel, border_radius=6)
    pygame.draw.rect(surface, (82, 112, 128), panel, 1, border_radius=6)
    draw_text(surface, font, f"Round {round_number}/{max_rounds}", (panel.x + 10, panel.y + 5), (22, 38, 52))
    minus_rect = pygame.Rect(panel.right - 58, panel.y + 4, 22, 18)
    plus_rect = pygame.Rect(panel.right - 30, panel.y + 4, 22, 18)
    pygame.draw.rect(surface, (94, 107, 116), minus_rect, border_radius=4)
    pygame.draw.rect(surface, (52, 121, 82), plus_rect, border_radius=4)
    draw_text(surface, font, "-", (minus_rect.x + 8, minus_rect.y + 1), TEXT)
    draw_text(surface, font, "+", (plus_rect.x + 6, plus_rect.y + 1), TEXT)
    return minus_rect, plus_rect


def draw_game_over_popup(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    evaluation_lines: list[str],
    export_path: Path | None,
) -> pygame.Rect:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(280, 110, SCREEN_WIDTH - 560, SCREEN_HEIGHT - 220)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=10)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=10)
    x = panel.x + 34
    y = panel.y + 28
    draw_text(surface, title_font, "Game Over", (x, y), (22, 38, 52))
    y += 42
    draw_text(surface, font, "Final Evaluation", (x, y), (42, 58, 70))
    y += 30
    for line in evaluation_lines[:10]:
        draw_text(surface, small_font, line, (x, y), (22, 38, 52))
        y += 24
    if export_path:
        y += 12
        draw_text(surface, small_font, f"History exported: {export_path}", (x, y), (42, 105, 72))
    close_rect = pygame.Rect(panel.right - 116, panel.bottom - 48, 84, 32)
    pygame.draw.rect(surface, (65, 96, 123), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 24, close_rect.y + 8), TEXT)
    return close_rect


def initial_resource_prices() -> dict[str, dict[str, int]]:
    return {
        resource: {"buy": values["buy"], "sell": values["sell"]}
        for resource, values in RESOURCE_PRICES.items()
    }


def resource_price_window(round_number: int) -> int:
    return ((max(1, round_number) - 1) // 5) * 5


def adjust_all_resource_prices(
    prices: dict[str, dict[str, int]],
    delta: int,
) -> bool:
    changed = False
    for resource in RESOURCE_ORDER:
        for side in ("buy", "sell"):
            old_price = prices[resource][side]
            base_price = RESOURCE_PRICES[resource][side]
            prices[resource][side] = max(base_price, old_price + delta)
            changed = changed or prices[resource][side] != old_price
    return changed


def apply_war_price_increase(
    prices: dict[str, dict[str, int]],
    round_number: int,
    price_increase_by_window: dict[int, int],
) -> int:
    window = resource_price_window(round_number)
    already_increased = price_increase_by_window.get(window, 0)
    increase = min(10, max(0, 30 - already_increased))
    if increase:
        adjust_all_resource_prices(prices, increase)
        price_increase_by_window[window] = already_increased + increase
    return increase


def apply_resource_price_decay(
    prices: dict[str, dict[str, int]],
    round_number: int,
    last_price_drop_round: int,
) -> tuple[int, int]:
    if round_number - last_price_drop_round < 1:
        return 0, last_price_drop_round
    if adjust_all_resource_prices(prices, -10):
        return 10, round_number
    return 0, round_number


def append_combat_history(
    history_events: list[HistoryEvent],
    round_number: int,
    result: dict[str, int | str | bool],
    price_increase: int,
    prices: dict[str, dict[str, int]],
) -> None:
    is_war = bool(result["is_war"])
    action_label = str(result["action_label"])
    details = [
        f"Attacker entities: {result['attacker_entities']}",
        f"Defender entities: {result['defender_entities']}",
        f"Winner: {result['winner']} | Lost: {result['lost_entity']}",
    ]
    if result.get("stolen_trade"):
        details.append(str(result["stolen_trade"]))
    if result.get("defender_weakened"):
        details.append(f"Defender power now: {result['defender_effective_power']}")
    if result.get("captured_port"):
        details.append(f"Captured port: {display_place_name(str(result['captured_port']))}")
    history_events.append(
        HistoryEvent(
            round_number=round_number,
            kind="war" if is_war else str(result["action_kind"]),
            title=f"{action_label}: {result['attacker']} vs {result['defender']}",
            details=details,
        )
    )
    if not is_war:
        return
    price_detail = "No price increase; 5-round cap reached." if price_increase == 0 else f"All resource prices +${price_increase}."
    history_events.append(
        HistoryEvent(
            round_number=round_number,
            kind="price",
            title="Resource price update after war",
            details=[price_detail, *price_snapshot_lines(prices)[:2]],
        )
    )


def transfer_captured_port_storage(
    port_name: str,
    new_owner: str,
    players: list[PlayerState],
    port_storage_by_port: dict[str, list[StoredGood]],
) -> int:
    goods = port_storage_by_port.get(port_name, [])
    winner = player_by_country(players, new_owner)
    transferred = 0
    for good in goods:
        old_owner = good.owner
        old_player = player_by_country(players, old_owner)
        if old_player and good.trade_card in old_player.trade_cards:
            old_player.trade_cards.remove(good.trade_card)
        if winner and good.trade_card not in winner.trade_cards:
            winner.trade_cards.append(good.trade_card)
        good.owner = new_owner
        good.trade_card.stolen_from = good.trade_card.stolen_from or old_owner
        good.trade_card.status = "stored"
        transferred += 1
    return transferred


EXPORT_HISTORY_KINDS = {"invest", "war", "resources", "factory", "news", "price", "tax", "license", "trade"}


def history_line(event: HistoryEvent) -> str:
    details = "; ".join(event.details)
    return f"[{event.kind}] {event.title}" + (f" - {details}" if details else "")


def grouped_history_lines(events: list[HistoryEvent], allowed_kinds: set[str] | None = None) -> list[str]:
    selected = [event for event in events if allowed_kinds is None or event.kind in allowed_kinds]
    lines: list[str] = []
    for round_no in sorted({event.round_number for event in selected}):
        lines.append(f"Round {round_no}")
        for event in selected:
            if event.round_number == round_no:
                lines.append(f"  {history_line(event)}")
        lines.append("")
    return lines


def war_winrates(history_events: list[HistoryEvent]) -> dict[str, float]:
    attempts = {country: 0 for country in EMPIRE_ORDER}
    wins = {country: 0 for country in EMPIRE_ORDER}
    for event in history_events:
        if event.kind != "war" or ": " not in event.title or " vs " not in event.title:
            continue
        sides = event.title.split(": ", 1)[1].split(" vs ", 1)
        if len(sides) != 2:
            continue
        attacker, defender = sides[0], sides[1]
        winner = None
        for detail in event.details:
            if detail.startswith("Winner: "):
                winner = detail.split("Winner: ", 1)[1].split(" | ", 1)[0]
                break
        for country in (attacker, defender):
            if country in attempts:
                attempts[country] += 1
        if winner in wins:
            wins[winner] += 1
    return {
        country: (wins[country] / attempts[country] if attempts[country] else 0.0)
        for country in EMPIRE_ORDER
    }


def evaluate_players(players: list[PlayerState], history_events: list[HistoryEvent]) -> list[str]:
    winrates = war_winrates(history_events)
    rows = []
    for player in players:
        factories = sum(1 for node in MAP_NODES.values() if node.factory_owner == player.country and node.factory_level)
        resource_value = sum(player.resources.get(resource, 0) * RESOURCE_PRICES[resource]["sell"] for resource in RESOURCE_ORDER)
        trade_success = sum(1 for card in player.trade_cards if card.status == "success")
        score = (
            player.money
            + len(player.ports) * 50
            + factories * 75
            + resource_value
            + trade_success * 100
            + round(winrates[player.country] * 100)
        )
        rows.append((score, player.country, player.money, len(player.ports), factories, winrates[player.country]))
    rows.sort(reverse=True)
    return [
        f"{idx + 1}. {country}: score {score} | money ${money} | ports {ports} | factories {factories} | war winrate {winrate:.0%}"
        for idx, (score, country, money, ports, factories, winrate) in enumerate(rows)
    ]


def next_history_export_path() -> Path:
    idx = 1
    while True:
        path = Path(f"game{idx}.txt")
        if not path.exists():
            return path
        idx += 1


def export_game_history(history_events: list[HistoryEvent], evaluation_lines: list[str]) -> Path:
    path = next_history_export_path()
    lines = ["ALL HISTORY", ""]
    lines.extend(grouped_history_lines(history_events, EXPORT_HISTORY_KINDS))
    lines.extend(["FINAL RESULT", *evaluation_lines, ""])
    for kind in sorted(EXPORT_HISTORY_KINDS):
        kind_events = [event for event in history_events if event.kind == kind]
        if not kind_events:
            continue
        lines.extend([kind.upper(), ""])
        lines.extend(grouped_history_lines(kind_events))
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def draw_treaty_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    draft_text: str,
    selected_countries: set[str],
    effective_round: int,
    expire_round: int,
    active_field: str,
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect, list[tuple[str, pygame.Rect]], dict[str, pygame.Rect]]:
    surface.fill((22, 28, 34))
    panel = pygame.Rect(170, 70, SCREEN_WIDTH - 340, SCREEN_HEIGHT - 140)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 38
    y = panel.y + 28
    draw_text(surface, title_font, "New Treaty", (x, y), (22, 38, 52))
    save_rect = pygame.Rect(panel.right - 198, panel.y + 24, 78, 32)
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    can_save = bool(draft_text.strip()) and bool(selected_countries) and effective_round <= expire_round
    pygame.draw.rect(surface, (42, 130, 79) if can_save else (130, 138, 142), save_rect, border_radius=6)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Save", (save_rect.x + 22, save_rect.y + 8), TEXT)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    y += 70
    draw_text(surface, font, "Treaty Text", (x, y), (22, 38, 52))
    text_rect = pygame.Rect(x, y + 30, panel.width - 76, 150)
    pygame.draw.rect(surface, (255, 252, 235), text_rect, border_radius=6)
    pygame.draw.rect(surface, (42, 130, 79) if active_field == "text" else (132, 142, 149), text_rect, 2, border_radius=6)
    draw_wrapped_text(
        surface,
        font,
        draft_text or "Click here and type treaty terms...",
        pygame.Rect(text_rect.x + 14, text_rect.y + 12, text_rect.width - 28, text_rect.height - 24),
        (22, 38, 52) if draft_text else (130, 138, 142),
    )

    y = text_rect.bottom + 26
    draw_text(surface, font, "Countries", (x, y), (22, 38, 52))
    country_rects: list[tuple[str, pygame.Rect]] = []
    chip_x = x
    chip_y = y + 34
    for country in EMPIRE_ORDER:
        rect = pygame.Rect(chip_x, chip_y, 154, 34)
        country_rects.append((country, rect))
        selected = country in selected_countries
        pygame.draw.rect(surface, OWNER_COLORS[country] if selected else (224, 229, 229), rect, border_radius=6)
        pygame.draw.rect(surface, (70, 88, 101), rect, 1, border_radius=6)
        text_color = BLACK if selected and country != "Pirates" else (22, 38, 52)
        draw_text(surface, small_font, country, (rect.x + 10, rect.y + 9), text_color)
        chip_x += 166
        if chip_x + 154 > panel.right - 38:
            chip_x = x
            chip_y += 44

    y = chip_y + 58
    draw_text(surface, font, "Rounds", (x, y), (22, 38, 52))
    controls: dict[str, pygame.Rect] = {}
    labels = [("effective", "Effective Round", effective_round), ("expire", "Expire Round", expire_round)]
    control_x = x
    for name, label, value in labels:
        draw_text(surface, small_font, label, (control_x, y + 36), (58, 72, 82))
        minus_rect = pygame.Rect(control_x, y + 62, 32, 30)
        value_rect = pygame.Rect(control_x + 42, y + 62, 70, 30)
        plus_rect = pygame.Rect(control_x + 122, y + 62, 32, 30)
        controls[f"{name}_minus"] = minus_rect
        controls[f"{name}_value"] = value_rect
        controls[f"{name}_plus"] = plus_rect
        pygame.draw.rect(surface, (78, 91, 103), minus_rect, border_radius=5)
        pygame.draw.rect(surface, (255, 252, 235), value_rect, border_radius=5)
        pygame.draw.rect(surface, (78, 91, 103), plus_rect, border_radius=5)
        pygame.draw.rect(surface, (42, 130, 79) if active_field == name else (132, 142, 149), value_rect, 2, border_radius=5)
        draw_text(surface, font, "-", (minus_rect.x + 12, minus_rect.y + 4), TEXT)
        draw_text(surface, font, str(value), (value_rect.x + 24, value_rect.y + 5), (22, 38, 52))
        draw_text(surface, font, "+", (plus_rect.x + 10, plus_rect.y + 4), TEXT)
        control_x += 230

    draw_text(surface, small_font, "Type text directly. Click countries to include them. Save creates the treaty.", (x, panel.bottom - 38), (87, 101, 112))
    return close_rect, save_rect, text_rect, country_rects, controls


def transfer_amount(value: str) -> int:
    return int(value) if value.isdigit() else 0


def transfer_is_valid(
    players: list[PlayerState],
    from_country: str,
    to_country: str,
    from_amount: str,
    to_amount: str,
    from_ports: set[str],
    to_ports: set[str],
    from_resources: dict[str, int],
    to_resources: dict[str, int],
) -> bool:
    if from_country == to_country:
        return False
    from_player = player_by_country(players, from_country)
    to_player = player_by_country(players, to_country)
    if not from_player or not to_player:
        return False
    if transfer_amount(from_amount) > from_player.money or transfer_amount(to_amount) > to_player.money:
        return False
    for resource in RESOURCE_ORDER:
        if from_resources.get(resource, 0) > from_player.resources.get(resource, 0):
            return False
        if to_resources.get(resource, 0) > to_player.resources.get(resource, 0):
            return False
    return all(MAP_NODES[name].owner == from_country for name in from_ports) and all(
        MAP_NODES[name].owner == to_country for name in to_ports
    )


def apply_transfer(
    players: list[PlayerState],
    from_country: str,
    to_country: str,
    from_amount: str,
    to_amount: str,
    from_ports: set[str],
    to_ports: set[str],
    from_resources: dict[str, int],
    to_resources: dict[str, int],
    round_number: int | None = None,
) -> bool:
    if not transfer_is_valid(
        players,
        from_country,
        to_country,
        from_amount,
        to_amount,
        from_ports,
        to_ports,
        from_resources,
        to_resources,
    ):
        return False
    from_player = player_by_country(players, from_country)
    to_player = player_by_country(players, to_country)
    if not from_player or not to_player:
        return False
    amount_ab = transfer_amount(from_amount)
    amount_ba = transfer_amount(to_amount)
    from_player.money -= amount_ab
    to_player.money += amount_ab
    to_player.money -= amount_ba
    from_player.money += amount_ba
    if round_number is not None:
        if amount_ab:
            record_transaction(from_player, round_number, -amount_ab, f"transfer to {to_country}")
            record_transaction(to_player, round_number, amount_ab, f"transfer from {from_country}")
        if amount_ba:
            record_transaction(to_player, round_number, -amount_ba, f"transfer to {from_country}")
            record_transaction(from_player, round_number, amount_ba, f"transfer from {to_country}")
    for port_name in from_ports:
        MAP_NODES[port_name].owner = to_country
    for port_name in to_ports:
        MAP_NODES[port_name].owner = from_country
    for resource in RESOURCE_ORDER:
        amount_ab = from_resources.get(resource, 0)
        amount_ba = to_resources.get(resource, 0)
        from_player.resources[resource] = from_player.resources.get(resource, 0) - amount_ab + amount_ba
        to_player.resources[resource] = to_player.resources.get(resource, 0) + amount_ab - amount_ba
    refresh_player_ports(players)
    return True


def transfer_summary_lines(
    from_country: str,
    to_country: str,
    from_amount: str,
    to_amount: str,
    from_ports: set[str],
    to_ports: set[str],
    from_resources: dict[str, int],
    to_resources: dict[str, int],
) -> list[str]:
    from_resource_count = sum(from_resources.values())
    to_resource_count = sum(to_resources.values())
    return [
        f"{from_country} -> {to_country}: ${transfer_amount(from_amount)}, {len(from_ports)} port(s), {from_resource_count} resource(s)",
        f"{to_country} -> {from_country}: ${transfer_amount(to_amount)}, {len(to_ports)} port(s), {to_resource_count} resource(s)",
    ]


def draw_transfer_page(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    players: list[PlayerState],
    from_country: str,
    to_country: str,
    from_amount: str,
    to_amount: str,
    from_ports: set[str],
    to_ports: set[str],
    from_resources: dict[str, int],
    to_resources: dict[str, int],
    active_field: str,
) -> tuple[
    pygame.Rect,
    pygame.Rect,
    dict[str, pygame.Rect],
    list[tuple[str, pygame.Rect]],
    list[tuple[str, pygame.Rect]],
    dict[str, pygame.Rect],
    dict[str, pygame.Rect],
]:
    surface.fill((22, 28, 34))
    panel = pygame.Rect(120, 58, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 116)
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)

    x = panel.x + 34
    y = panel.y + 24
    draw_text(surface, title_font, "Transfer Funds / Ports", (x, y), (22, 38, 52))
    save_rect = pygame.Rect(panel.right - 198, panel.y + 24, 78, 32)
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 70, 32)
    can_save = transfer_is_valid(
        players,
        from_country,
        to_country,
        from_amount,
        to_amount,
        from_ports,
        to_ports,
        from_resources,
        to_resources,
    )
    pygame.draw.rect(surface, (42, 130, 79) if can_save else (130, 138, 142), save_rect, border_radius=6)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Save", (save_rect.x + 22, save_rect.y + 8), TEXT)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)

    y += 66
    draw_text(surface, font, "Countries", (x, y), (22, 38, 52))
    country_rects: dict[str, pygame.Rect] = {}
    chip_x = x
    for country in EMPIRE_ORDER:
        rect = pygame.Rect(chip_x, y + 32, 154, 34)
        country_rects[f"from:{country}"] = rect
        selected = country == from_country
        pygame.draw.rect(surface, OWNER_COLORS[country] if selected else (224, 229, 229), rect, border_radius=6)
        pygame.draw.rect(surface, (70, 88, 101), rect, 1, border_radius=6)
        draw_text(surface, small_font, f"A {country}" if selected else country, (rect.x + 8, rect.y + 9), BLACK if selected and country != "Pirates" else (22, 38, 52))
        chip_x += 166
        if chip_x + 154 > panel.right - 34:
            chip_x = x
            y += 42
    chip_x = x
    y += 78
    for country in EMPIRE_ORDER:
        rect = pygame.Rect(chip_x, y, 154, 34)
        country_rects[f"to:{country}"] = rect
        selected = country == to_country
        pygame.draw.rect(surface, OWNER_COLORS[country] if selected else (224, 229, 229), rect, border_radius=6)
        pygame.draw.rect(surface, (70, 88, 101), rect, 1, border_radius=6)
        draw_text(surface, small_font, f"B {country}" if selected else country, (rect.x + 8, rect.y + 9), BLACK if selected and country != "Pirates" else (22, 38, 52))
        chip_x += 166
        if chip_x + 154 > panel.right - 34:
            chip_x = x
            y += 42

    y += 58
    left = pygame.Rect(x, y, (panel.width - 92) // 2, 440)
    right = pygame.Rect(left.right + 24, y, left.width, 440)
    amount_rects = {
        "from_amount": pygame.Rect(left.x + 106, left.y + 42, 110, 32),
        "to_amount": pygame.Rect(right.x + 106, right.y + 42, 110, 32),
    }
    from_port_rects: list[tuple[str, pygame.Rect]] = []
    to_port_rects: list[tuple[str, pygame.Rect]] = []
    resource_rects: dict[str, pygame.Rect] = {}
    for side, rect, payer, receiver, amount, selected_ports, selected_resources, port_rects in [
        ("from", left, from_country, to_country, from_amount, from_ports, from_resources, from_port_rects),
        ("to", right, to_country, from_country, to_amount, to_ports, to_resources, to_port_rects),
    ]:
        pygame.draw.rect(surface, (225, 231, 227), rect, border_radius=8)
        draw_text(surface, font, f"{payer} pays {receiver}", (rect.x + 14, rect.y + 14), (22, 38, 52))
        draw_text(surface, small_font, "Money", (rect.x + 14, rect.y + 50), (58, 72, 82))
        amount_box = amount_rects["from_amount" if side == "from" else "to_amount"]
        pygame.draw.rect(surface, (255, 252, 235), amount_box, border_radius=5)
        pygame.draw.rect(surface, (42, 130, 79) if active_field == amount_box_key(side) else (132, 142, 149), amount_box, 2, border_radius=5)
        draw_text(surface, font, amount or "0", (amount_box.x + 12, amount_box.y + 6), (22, 38, 52))
        draw_text(surface, small_font, "Resources", (rect.x + 14, rect.y + 92), (58, 72, 82))
        player = player_by_country(players, payer)
        res_y = rect.y + 118
        for idx, resource in enumerate(RESOURCE_ORDER):
            col = idx % 2
            row = idx // 2
            rx = rect.x + 14 + col * 190
            ry = res_y + row * 28
            minus_rect = pygame.Rect(rx + 88, ry - 2, 24, 22)
            plus_rect = pygame.Rect(rx + 150, ry - 2, 24, 22)
            resource_rects[f"{side}:{resource}:minus"] = minus_rect
            resource_rects[f"{side}:{resource}:plus"] = plus_rect
            amount_selected = selected_resources.get(resource, 0)
            available = player.resources.get(resource, 0) if player else 0
            draw_text(surface, small_font, f"{RESOURCE_LABELS[resource]} {amount_selected}/{available}", (rx, ry), (22, 38, 52))
            pygame.draw.rect(surface, (78, 91, 103) if amount_selected > 0 else (130, 138, 142), minus_rect, border_radius=4)
            pygame.draw.rect(surface, (78, 91, 103) if amount_selected < available else (130, 138, 142), plus_rect, border_radius=4)
            draw_text(surface, small_font, "-", (minus_rect.x + 8, minus_rect.y + 3), TEXT)
            draw_text(surface, small_font, "+", (plus_rect.x + 7, plus_rect.y + 3), TEXT)

        draw_text(surface, small_font, "Ports", (rect.x + 14, rect.y + 208), (58, 72, 82))
        ports = sorted(player.ports, key=lambda port: port.name) if player else []
        port_y = rect.y + 236
        for port in ports[:7]:
            port_rect = pygame.Rect(rect.x + 14, port_y, rect.width - 28, 24)
            port_rects.append((port.name, port_rect))
            checked = port.name in selected_ports
            pygame.draw.rect(surface, (255, 252, 235), port_rect, border_radius=4)
            pygame.draw.rect(surface, (42, 130, 79) if checked else (132, 142, 149), port_rect, 2 if checked else 1, border_radius=4)
            label = f"{'[x]' if checked else '[ ]'} {display_place_name(port.name)}"
            draw_text(surface, small_font, label, (port_rect.x + 8, port_rect.y + 4), (22, 38, 52))
            port_y += 27
        if len(ports) > 7:
            draw_text(surface, small_font, f"+ {len(ports) - 7} more ports not shown", (rect.x + 14, rect.bottom - 24), (87, 101, 112))

    summary_y = panel.bottom - 62
    draw_text(surface, font, "Summary", (x, summary_y), (22, 38, 52))
    for idx, line in enumerate(
        transfer_summary_lines(
            from_country,
            to_country,
            from_amount,
            to_amount,
            from_ports,
            to_ports,
            from_resources,
            to_resources,
        )
    ):
        draw_text(surface, small_font, line, (x + 92, summary_y + idx * 20 + 4), (58, 72, 82))
    return close_rect, save_rect, country_rects, from_port_rects, to_port_rects, amount_rects, resource_rects


def draw_attack_prompt(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    prompt: AttackPrompt,
    result: dict[str, int | str | bool] | None,
    players: list[PlayerState],
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    anchor = node_to_screen(prompt.location) if prompt.location in MAP_NODES else ship_screen_position(prompt.attacker)
    panel = pygame.Rect(anchor[0] + 20, anchor[1] - 132, 430, 264)
    if panel.right > SCREEN_WIDTH - SIDE_PANEL_WIDTH - 8:
        panel.x = anchor[0] - panel.width - 20
    if panel.top < MAP_RECT.top + 8:
        panel.y = anchor[1] + 22
    if panel.bottom > MAP_RECT.bottom - 8:
        panel.y = MAP_RECT.bottom - panel.height - 8
    pygame.draw.rect(surface, (240, 239, 229), panel, border_radius=8)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=8)
    x = panel.x + 28
    y = panel.y + 24
    _, action_label, is_war = combat_action(prompt)
    title = f"{action_label}?"
    if isinstance(prompt.defender, MapNode) and is_war:
        title = "Attack Port?"
    draw_text(surface, title_font, title, (x, y), (22, 38, 52))
    y += 48
    draw_text(surface, font, f"{prompt.attacker.owner}: {prompt.attacker.kind}", (x, y), (22, 38, 52))
    y += 28
    draw_text(surface, font, f"vs {entity_label(prompt.defender)}", (x, y), (22, 38, 52))
    y += 28
    draw_text(surface, small_font, f"Trigger: {prompt.trigger}", (x, y), (87, 101, 112))
    y += 34
    if result:
        lines = [
            f"Attacker: {result['attacker_entities']}",
            f"Defender: {result['defender_entities']}",
            f"{result['attacker']} roll {result['attacker_roll']} => {result['attacker_power']}",
            f"{result['defender']} roll {result['defender_roll']} => {result['defender_power']}",
            f"Winner: {result['winner']}",
            f"Lost: {result['lost_entity']}",
        ]
        if result.get("defender_weakened"):
            lines.append(f"Defender power now: {result['defender_effective_power']}")
        for line in lines:
            draw_text(surface, small_font, line, (x, y), (42, 105, 72))
            y += 19
    else:
        draw_wrapped_text(
            surface,
            small_font,
            "1 vs 1. Power = dice * entity power. Merchant 2 empty / 1 loaded, Pirate 2, Warship 3, Port 4, Pirate port 3.",
            pygame.Rect(x, y, panel.width - 56, 50),
            (58, 72, 82),
        )
    attack_rect = pygame.Rect(panel.right - 198, panel.bottom - 46, 86, 30)
    skip_rect = pygame.Rect(panel.right - 98, panel.bottom - 46, 72, 30)
    oil_rect = pygame.Rect(panel.right - 296, panel.bottom - 46, 84, 30)
    can_continue = bool(result and result.get("can_continue"))
    attack_enabled = result is None or can_continue
    attacker_player = player_by_country(players, prompt.attacker.owner)
    oil_enabled = bool(result is None and attacker_player and attacker_player.resources.get("oil", 0) > 0)
    pygame.draw.rect(surface, (35, 37, 42) if oil_enabled else (130, 138, 142), oil_rect, border_radius=6)
    oil_text = "Oil on" if prompt.attacker_uses_oil else "Oil"
    draw_text(surface, small_font, oil_text, (oil_rect.x + 14, oil_rect.y + 9), TEXT)
    pygame.draw.rect(surface, (157, 63, 58) if attack_enabled else (130, 138, 142), attack_rect, border_radius=6)
    pygame.draw.rect(surface, (78, 91, 103), skip_rect, border_radius=6)
    attack_text = action_label if result is None else ("Continue" if can_continue else "Done")
    skip_text = "Skip" if result is None else "Close"
    draw_text(surface, small_font, attack_text, (attack_rect.x + 14, attack_rect.y + 9), TEXT)
    draw_text(surface, small_font, skip_text, (skip_rect.x + 18, skip_rect.y + 9), TEXT)
    return attack_rect, skip_rect, oil_rect


def draw_news_popup(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    events: list[NewsEvent],
) -> pygame.Rect:
    if not events:
        return pygame.Rect(0, 0, 0, 0)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 95))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(230, 110, SCREEN_WIDTH - 460, SCREEN_HEIGHT - 220)
    pygame.draw.rect(surface, (242, 240, 229), panel, border_radius=10)
    pygame.draw.rect(surface, (70, 88, 101), panel, 2, border_radius=10)
    x = panel.x + 34
    y = panel.y + 28
    draw_text(surface, title_font, "News Dispatch", (x, y), (22, 38, 52))
    close_rect = pygame.Rect(panel.right - 104, panel.y + 24, 72, 32)
    pygame.draw.rect(surface, (78, 91, 103), close_rect, border_radius=6)
    draw_text(surface, small_font, "Close", (close_rect.x + 18, close_rect.y + 8), TEXT)
    y += 58
    for event in events:
        card = pygame.Rect(x - 12, y - 8, panel.width - 44, 154)
        pygame.draw.rect(surface, (225, 231, 227), card, border_radius=8)
        accent = (54, 96, 150) if event.category == "maritime" else (142, 93, 47)
        pygame.draw.rect(surface, accent, (card.x, card.y, 6, card.height), border_radius=4)
        draw_text(surface, font, event.title, (x + 8, y), (22, 38, 52))
        line_y = y + 34
        for detail in event.details:
            draw_wrapped_text(surface, small_font, detail, pygame.Rect(x + 8, line_y, card.width - 32, 24), (58, 72, 82))
            line_y += 24
        if event.ports:
            port_line = ", ".join(display_place_name(port) for port in sorted(event.ports)[:8])
            if len(event.ports) > 8:
                port_line += " ..."
            draw_wrapped_text(surface, small_font, f"Affected: {port_line}", pygame.Rect(x + 8, line_y, card.width - 32, 42), (87, 101, 112))
        y += 170
    draw_text(surface, small_font, "Auto closes after 10 seconds.", (panel.x + 34, panel.bottom - 34), (87, 101, 112))
    return close_rect


def amount_box_key(side: str) -> str:
    return "from_amount" if side == "from" else "to_amount"


def player_resource_lines(player: PlayerState) -> list[str]:
    return [f"{resource}: {player.resources.get(resource, 0)}" for resource in RESOURCE_ORDER]


def player_port_lines(player: PlayerState) -> list[str]:
    return [
        f"{port.name.replace('_', ' ')} - {port.resource or 'none'} - fee ${port.fee or 0}"
        for port in player.ports
    ]


def player_ship_lines(player: PlayerState, pending_builds: list[PendingShipBuild] | None = None) -> list[str]:
    lines = []
    lines.append(f"Unpaid voyage upkeep: ${sum(ship_upkeep_due(ship) for ship in player.ships)}")
    for ship in player.ships:
        trade_suffix = ""
        if ship.trade_card and ship.trade_destination:
            trade_suffix = f" | trade to {display_place_name(ship.trade_destination)}"
        distance_suffix = f" | dist {ship.distance_since_upkeep}"
        if ship.destination:
            lines.append(
                f"{ship.name}: {ship_kind_label(ship, player=player)} {ship.location.replace('_', ' ')}"
                f" -> {ship.destination.replace('_', ' ')} {ship.progress}/{ship.course_distance}{trade_suffix}{distance_suffix}"
            )
        else:
            lines.append(f"{ship.name}: {ship_kind_label(ship, player=player)} at {ship.location.replace('_', ' ')}{trade_suffix}{distance_suffix}")
    if pending_builds:
        for build in pending_builds:
            if build.owner == player.country:
                lines.append(f"Pending: {build.kind} at {display_place_name(build.location)} ready R{build.ready_round}")
    return lines


def player_trade_lines(player: PlayerState) -> list[str]:
    if not player.trade_cards:
        return ["No trade cards"]
    return [trade_card_display_line(card) for card in player.trade_cards]


def treaty_lines(treaties: list[Treaty], country: str | None = None) -> list[str]:
    relevant = [treaty for treaty in treaties if country is None or country in treaty.countries]
    if not relevant:
        return ["No treaties"]
    return [
        f"R{treaty.effective_round}-R{treaty.expire_round}: {', '.join(treaty.countries)} | {treaty.text}"
        for treaty in relevant
    ]


def draw_side_panel(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    player: PlayerState,
    hovered_port,
    ports_expanded: bool,
    round_number: int,
    active_player: str,
    selected_ship: Ship | None,
    operable_ships: list[Ship],
    treaties: list[Treaty],
    last_tax_summary: dict[str, int],
    last_maintenance_summary: dict[str, int],
    last_trade_summary: dict[str, str],
    transaction_scroll: int,
    side_panel_scroll: int,
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect, dict[str, pygame.Rect], int, int]:
    panel_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH
    pygame.draw.rect(surface, PANEL, (panel_x, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
    pygame.draw.line(surface, (87, 108, 122), (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

    x = panel_x + 22
    y = 24
    draw_text(surface, title_font, "ABCDE Map", (x, y))
    y += 42
    draw_text(surface, font, f"Round {round_number}  Turn: {active_player}", (x, y), TEXT)
    y += 28
    if not operable_ships:
        active_label = "No ships left to operate."
    elif selected_ship:
        active_label = f"Selected: {ship_kind_label(selected_ship, player=player)} at {selected_ship.location.replace('_', ' ')}"
        if selected_ship.destination:
            active_label = (
                f"Selected: {ship_kind_label(selected_ship, player=player)} {selected_ship.location.replace('_', ' ')}"
                f" -> {selected_ship.destination.replace('_', ' ')}"
            )
    else:
        active_label = f"{len(operable_ships)} ship(s) ready."
    draw_wrapped_text(surface, small_font, active_label, pygame.Rect(x, y, SIDE_PANEL_WIDTH - 44, 40), TEXT_MUTED)
    y += 42
    next_button = pygame.Rect(x, y, 138, 32)
    new_game_button = pygame.Rect(x + 150, y, 142, 32)
    pygame.draw.rect(surface, (65, 96, 123), next_button, border_radius=6)
    pygame.draw.rect(surface, (94, 73, 123), new_game_button, border_radius=6)
    draw_text(surface, small_font, "Next Player", (next_button.x + 16, next_button.y + 8), TEXT)
    draw_text(surface, small_font, "New Game", (new_game_button.x + 22, new_game_button.y + 8), TEXT)
    y += 42
    content_top = y
    content_bottom = SCREEN_HEIGHT - 14
    previous_clip = surface.get_clip()
    surface.set_clip(pygame.Rect(panel_x + 2, content_top, SIDE_PANEL_WIDTH - 4, content_bottom - content_top))
    y -= side_panel_scroll
    draw_owner_marker(surface, player.country, (x + 11, y + 10), font, size=24)
    draw_text(surface, font, f"Player: {player.country}", (x + 32, y), OWNER_COLORS[player.country])
    license_x = x + 230
    for license_key in sorted(player.licenses):
        draw_license_glyph(surface, license_key, pygame.Rect(license_x, y + 1, 28, 20), small_font)
        license_x += 34
    y += 28
    draw_text(surface, font, f"Money: ${player.money}", (x, y))
    y += 28
    hover_cards: dict[str, pygame.Rect] = {}

    transaction_card = pygame.Rect(x - 10, y - 6, SIDE_PANEL_WIDTH - 24, 84)
    hover_cards["transactions"] = transaction_card
    pygame.draw.rect(surface, PANEL_ALT, transaction_card, border_radius=8)
    draw_text(surface, small_font, "Transactions", (x, y), TEXT)
    visible_transactions = 3
    max_transaction_scroll = max(0, len(player.transactions) - visible_transactions)
    transaction_scroll = max(0, min(max_transaction_scroll, transaction_scroll))
    newest_first = list(reversed(player.transactions))
    for idx, line in enumerate(newest_first[transaction_scroll : transaction_scroll + visible_transactions]):
        draw_text(surface, small_font, line, (x, y + 22 + idx * 18), TEXT_MUTED)
    if not player.transactions:
        draw_text(surface, small_font, "No transactions yet", (x, y + 22), TEXT_MUTED)
    if max_transaction_scroll:
        draw_text(surface, small_font, "scroll", (transaction_card.right - 48, transaction_card.y + 8), TEXT_MUTED)
    y = transaction_card.bottom + 12

    if last_trade_summary.get(player.country):
        draw_text(surface, small_font, f"Last trade: {last_trade_summary[player.country]}", (x, y), (109, 178, 231))
        y += 20
    if last_tax_summary:
        draw_text(surface, small_font, f"Last tax: +${last_tax_summary.get(player.country, 0)}", (x, y), TEXT_MUTED)
    else:
        draw_text(surface, small_font, "Tax collection: every 5 rounds", (x, y), TEXT_MUTED)
    y += 20
    if last_maintenance_summary:
        draw_text(surface, small_font, f"Last non-merchant upkeep: -${last_maintenance_summary.get(player.country, 0)}", (x, y), TEXT_MUTED)
        y += 18
    draw_wrapped_text(surface, small_font, SKILLS[player.country], pygame.Rect(x, y, SIDE_PANEL_WIDTH - 44, 48))
    y += 58

    resources_card = pygame.Rect(x - 10, y - 8, SIDE_PANEL_WIDTH - 24, 112)
    hover_cards["resources"] = resources_card
    pygame.draw.rect(surface, PANEL_ALT, resources_card, border_radius=8)
    draw_text(surface, font, "Resources", (x, y))
    for idx, resource in enumerate(RESOURCE_ORDER):
        col = idx % 3
        row = idx // 3
        glyph = pygame.Rect(x + col * 96, y + 28 + row * 38, 34, 20)
        draw_resource_glyph(surface, resource, glyph, small_font)
        amount = player.resources.get(resource, 0)
        draw_text(surface, small_font, f"x{amount}", (glyph.right + 8, glyph.top + 3), TEXT)
    y = resources_card.bottom + 14

    ports_card = pygame.Rect(x - 10, y - 8, SIDE_PANEL_WIDTH - 24, 72)
    hover_cards["ports"] = ports_card
    pygame.draw.rect(surface, PANEL_ALT, ports_card, border_radius=8)
    draw_text(surface, font, "Ports", (x, y))
    draw_text(surface, title_font, str(len(player.ports)), (x, y + 25), TEXT)
    draw_text(surface, small_font, "owned ports", (x + 52, y + 40), TEXT_MUTED)
    resource_counts = defaultdict(int)
    for port in player.ports:
        if port.resource and port.resource in RESOURCE_ORDER:
            resource_counts[port.resource] += 1
    chip_x = x + 150
    chip_y = y + 22
    for resource in RESOURCE_ORDER[:4]:
        chip = pygame.Rect(chip_x, chip_y, 28, 18)
        draw_resource_glyph(surface, resource, chip, small_font, show_label=False)
        draw_text(surface, small_font, str(resource_counts[resource]), (chip.right + 5, chip.top + 2), TEXT_MUTED)
        chip_x += 62
        if chip_x > panel_x + SIDE_PANEL_WIDTH - 62:
            chip_x = x + 150
            chip_y += 30
    y = ports_card.bottom + 14

    ships_card = pygame.Rect(x - 10, y - 8, SIDE_PANEL_WIDTH - 24, 76)
    hover_cards["ships"] = ships_card
    pygame.draw.rect(surface, PANEL_ALT, ships_card, border_radius=8)
    draw_text(surface, font, "Ships", (x, y))
    merchant_count = sum(1 for ship in player.ships if ship.kind == "Merchant")
    merchant_trade_count = sum(1 for ship in player.ships if ship.kind == "Merchant" and ship.trade_card)
    privateer_active = "pirate" in player.licenses
    warship_count = sum(1 for ship in player.ships if ship.kind == "Warship")
    pirate_count = sum(1 for ship in player.ships if ship.kind == "Pirate")
    pirate_trade_count = sum(1 for ship in player.ships if ship.kind == "Pirate" and ship.trade_card)
    underway_count = sum(1 for ship in player.ships if ship_is_enroute(ship))
    draw_ship_icon(surface, (x + 30, y + 42), small_font, len(player.ships))
    if player.country == "Pirates":
        draw_text(surface, small_font, f"Pirate x{pirate_count}", (x + 72, y + 27), TEXT_MUTED)
        draw_text(surface, small_font, f"Pirate (+) x{pirate_trade_count}", (x + 72, y + 47), TEXT_MUTED)
    else:
        merchant_label = "Privateer" if privateer_active else "Merchant"
        loaded_label = "Merchant (*)" if privateer_active else "Merchant (+)"
        draw_text(surface, small_font, f"{merchant_label} x{merchant_count}", (x + 72, y + 27), TEXT_MUTED)
        draw_text(surface, small_font, f"{loaded_label} x{merchant_trade_count}", (x + 72, y + 47), TEXT_MUTED)
        draw_text(surface, small_font, f"Warship x{warship_count}", (x + 192, y + 27), TEXT_MUTED)
    underway_y = y + 37 if player.country == "Pirates" else y + 47
    draw_text(surface, small_font, f"Underway x{underway_count}", (x + 192, underway_y), TEXT_MUTED)
    y = ships_card.bottom + 14

    trade_card = pygame.Rect(x - 10, y - 8, SIDE_PANEL_WIDTH - 24, 86)
    hover_cards["trade"] = trade_card
    pygame.draw.rect(surface, PANEL_ALT, trade_card, border_radius=8)
    draw_text(surface, font, "Trade Info", (x, y))
    undeclared_count = sum(1 for card in player.trade_cards if card.status == "undeclared")
    declared_count = sum(1 for card in player.trade_cards if card.status == "declared")
    draw_text(surface, title_font, str(len(player.trade_cards)), (x, y + 28), TEXT)
    draw_text(surface, small_font, "cards", (x + 46, y + 45), TEXT_MUTED)
    draw_text(surface, small_font, f"Undeclared x{undeclared_count}", (x + 126, y + 30), TEXT_MUTED)
    draw_text(surface, small_font, f"Declared x{declared_count}", (x + 126, y + 48), TEXT_MUTED)
    if player.trade_cards:
        latest = player.trade_cards[-1]
        draw_text(surface, small_font, f"Latest: ${latest.profit} {latest.status}", (x + 226, y + 48), TEXT_MUTED)
    else:
        draw_text(surface, small_font, "No card selected", (x + 226, y + 48), TEXT_MUTED)
    y = trade_card.bottom + 14

    treaty_card = pygame.Rect(x - 10, y - 8, SIDE_PANEL_WIDTH - 24, 82)
    hover_cards["treaty"] = treaty_card
    pygame.draw.rect(surface, PANEL_ALT, treaty_card, border_radius=8)
    draw_text(surface, font, "Treaty", (x, y))
    relevant_treaties = [treaty for treaty in treaties if player.country in treaty.countries]
    active_treaties = [
        treaty
        for treaty in relevant_treaties
        if treaty.effective_round <= round_number <= treaty.expire_round
    ]
    draw_text(surface, title_font, str(len(relevant_treaties)), (x, y + 26), TEXT)
    draw_text(surface, small_font, "related", (x + 46, y + 43), TEXT_MUTED)
    draw_text(surface, small_font, f"Active x{len(active_treaties)}", (x + 126, y + 30), TEXT_MUTED)
    if relevant_treaties:
        latest = relevant_treaties[-1]
        draw_wrapped_text(surface, small_font, latest.text, pygame.Rect(x + 126, y + 50, 180, 24), TEXT_MUTED)
    else:
        draw_text(surface, small_font, "No treaty", (x + 126, y + 50), TEXT_MUTED)
    y = treaty_card.bottom + 14

    factory_card = pygame.Rect(x - 10, y - 8, SIDE_PANEL_WIDTH - 24, 76)
    hover_cards["factories"] = factory_card
    pygame.draw.rect(surface, PANEL_ALT, factory_card, border_radius=8)
    draw_text(surface, font, "Factories", (x, y))
    player_factories = [
        node
        for node in MAP_NODES.values()
        if node.factory_owner == player.country and node.factory_level
    ]
    green_count = sum(1 for node in player_factories if node.factory_level == "green")
    red_count = sum(1 for node in player_factories if node.factory_level == "red")
    draw_text(surface, title_font, str(len(player_factories)), (x, y + 26), TEXT)
    draw_text(surface, small_font, "built", (x + 46, y + 43), TEXT_MUTED)
    pygame.draw.rect(surface, (54, 130, 94), (x + 126, y + 30, 28, 16), border_radius=4)
    draw_text(surface, small_font, f"x{green_count}", (x + 162, y + 28), TEXT_MUTED)
    pygame.draw.rect(surface, (157, 63, 58), (x + 220, y + 30, 28, 16), border_radius=4)
    draw_text(surface, small_font, f"x{red_count}", (x + 256, y + 28), TEXT_MUTED)

    y = SCREEN_HEIGHT - 78
    y = max(y, factory_card.bottom + 16)
    draw_text(surface, small_font, "Turns advance UK > Russia > China > Japan > Pirates > US", (x, y + 24), TEXT_MUTED)
    content_height = y + 54 + side_panel_scroll - content_top
    max_side_panel_scroll = max(0, content_height - (content_bottom - content_top))
    if max_side_panel_scroll:
        draw_text(surface, small_font, "scroll player info", (panel_x + SIDE_PANEL_WIDTH - 132, content_top + 6 + side_panel_scroll), TEXT_MUTED)
    surface.set_clip(previous_clip)
    return ports_card, next_button, new_game_button, hover_cards, max_transaction_scroll, max_side_panel_scroll


def draw_legend(surface: pygame.Surface, font: pygame.font.Font) -> None:
    x = 22
    y = (BACKGROUND_RECT.bottom + 18) if BACKGROUND_SURFACE else SCREEN_HEIGHT - 82
    y = min(y, SCREEN_HEIGHT - 82)
    for country in EMPIRE_ORDER:
        draw_owner_marker(surface, country, (x + 11, y + 9), font, size=22)
        draw_text(surface, font, OWNER_LEGEND_LABELS[country], (x + 28, y), TEXT_MUTED)
        x += 154


def draw_port_edit_overlay(
    surface: pygame.Surface,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    selected_port: str | None,
    hovered_port: str | None,
    status_message: str,
) -> None:
    panel = pygame.Rect(MAP_RECT.left + 12, MAP_RECT.top + 12, 360, 104)
    pygame.draw.rect(surface, (250, 249, 239), panel, border_radius=8)
    pygame.draw.rect(surface, (58, 88, 106), panel, 1, border_radius=8)
    draw_text(surface, font, "Port Edit Mode", (panel.x + 12, panel.y + 10), (22, 38, 52))
    draw_text(surface, small_font, "Drag port markers. E exits. Cmd/Ctrl+S saves coords.", (panel.x + 12, panel.y + 40), (57, 75, 88))
    active_name = selected_port or hovered_port
    if active_name:
        node = MAP_NODES[active_name]
        label = f"{display_place_name(active_name)}  lat {node.lat:.2f}, lon {node.lon:.2f}"
    else:
        label = "Hover or click a port to inspect coordinates."
    draw_text(surface, small_font, label, (panel.x + 12, panel.y + 62), (22, 38, 52))
    if status_message:
        draw_text(surface, small_font, status_message, (panel.x + 12, panel.y + 82), (28, 113, 72))


def validate_map_data() -> None:
    port_names = set(NOTEBOOK_PORT_ORDER)
    missing_coords = port_names - set(PORT_GEO_COORDS)
    course_nodes = {name for start, end, _ in NOTEBOOK_COURSES for name in (start, end)}
    missing_ports = course_nodes - port_names
    unused_ports = port_names - course_nodes
    if missing_coords or missing_ports or unused_ports:
        raise ValueError(
            "Map data mismatch: "
            f"missing_coords={sorted(missing_coords)}, "
            f"missing_ports={sorted(missing_ports)}, "
            f"unused_ports={sorted(unused_ports)}"
        )


def display_flags(fullscreen: bool) -> int:
    flags = pygame.SCALED
    if fullscreen:
        flags |= pygame.FULLSCREEN
    return flags


def main() -> int:
    validate_map_data()
    pygame.init()
    pygame.display.set_caption("ABCDE - Phase 1 Map")
    fullscreen = FULLSCREEN_START
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags(fullscreen))
    load_background_image()
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 28, True)
    font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 14)
    tiny_font = pygame.font.SysFont("arial", 11)
    icon_font = pygame.font.SysFont("arial", 24, True)

    players = randomize_game()
    selected_idx = 0
    active_player_idx = 0
    round_number = 1
    max_rounds = DEFAULT_MAX_ROUNDS
    game_over = False
    show_game_over_popup = False
    game_over_evaluation: list[str] = []
    game_over_export_path: Path | None = None
    game_over_close_rect = pygame.Rect(0, 0, 0, 0)
    round_limit_minus_rect = pygame.Rect(0, 0, 0, 0)
    round_limit_plus_rect = pygame.Rect(0, 0, 0, 0)
    acted_ship_ids: set[int] = set()
    selected_ship: Ship | None = None
    running = True
    player_tab_rects: list[pygame.Rect] = []
    ports_card_rect = pygame.Rect(0, 0, 0, 0)
    next_button_rect = pygame.Rect(0, 0, 0, 0)
    new_game_button_rect = pygame.Rect(0, 0, 0, 0)
    panel_hover_cards: dict[str, pygame.Rect] = {}
    buy_button_rect = pygame.Rect(0, 0, 0, 0)
    trade_card_button_rect = pygame.Rect(0, 0, 0, 0)
    new_treaty_button_rect = pygame.Rect(0, 0, 0, 0)
    transfer_button_rect = pygame.Rect(0, 0, 0, 0)
    history_button_rect = pygame.Rect(0, 0, 0, 0)
    new_factory_button_rect = pygame.Rect(0, 0, 0, 0)
    new_ship_button_rect = pygame.Rect(0, 0, 0, 0)
    rules_button_rect = pygame.Rect(0, 0, 0, 0)
    market_close_rect = pygame.Rect(0, 0, 0, 0)
    market_buy_rects: dict[str, pygame.Rect] = {}
    market_sell_rects: dict[str, pygame.Rect] = {}
    market_license_rects: dict[str, pygame.Rect] = {}
    market_scroll = 0
    market_max_scroll = 0
    market_open = False
    history_open = False
    history_close_rect = pygame.Rect(0, 0, 0, 0)
    history_scroll = 0
    history_max_scroll = 0
    rules_open = False
    rules_close_rect = pygame.Rect(0, 0, 0, 0)
    rules_scroll = 0
    rules_max_scroll = 0
    transaction_scroll = 0
    transaction_max_scroll = 0
    side_panel_scroll = 0
    side_panel_max_scroll = 0
    build_open = False
    build_close_rect = pygame.Rect(0, 0, 0, 0)
    build_action_rects: list[tuple[str, str, str, pygame.Rect]] = []
    arrange_scroll = 0
    arrange_max_scroll = 0
    new_ship_open = False
    new_ship_close_rect = pygame.Rect(0, 0, 0, 0)
    new_ship_action_rects: list[tuple[str, str, pygame.Rect]] = []
    trade_card_open = False
    trade_card_close_rect = pygame.Rect(0, 0, 0, 0)
    trade_card_confirm_rect = pygame.Rect(0, 0, 0, 0)
    trade_card_option_rects: list[tuple[pygame.Rect, TradeCard]] = []
    trade_card_options: list[TradeCard] = []
    selected_trade_card: TradeCard | None = None
    trade_card_confirmed = False
    treaty_open = False
    treaty_close_rect = pygame.Rect(0, 0, 0, 0)
    treaty_save_rect = pygame.Rect(0, 0, 0, 0)
    treaty_text_rect = pygame.Rect(0, 0, 0, 0)
    treaty_country_rects: list[tuple[str, pygame.Rect]] = []
    treaty_controls: dict[str, pygame.Rect] = {}
    treaty_draft_text = ""
    treaty_selected_countries: set[str] = set()
    treaty_effective_round = 1
    treaty_expire_round = 1
    treaty_active_field = "text"
    treaties: list[Treaty] = []
    last_tax_summary: dict[str, int] = {}
    last_resource_summary: dict[str, dict[str, int]] = {}
    last_maintenance_summary: dict[str, int] = {}
    last_storage_fee_summary: dict[str, int] = {}
    last_trade_summary: dict[str, str] = {}
    history_events: list[HistoryEvent] = []
    active_news: list[NewsEvent] = []
    news_popup_events: list[NewsEvent] = []
    news_popup_until = 0
    news_close_rect = pygame.Rect(0, 0, 0, 0)
    pending_ship_builds: list[PendingShipBuild] = []
    port_storage_by_port: dict[str, list[StoredGood]] = defaultdict(list)
    pending_goods_transfers: list[PendingGoodsTransfer] = []
    resource_prices = initial_resource_prices()
    price_increase_by_window: dict[int, int] = {}
    battle_power_penalties: dict[int, int] = {}
    last_price_drop_round = round_number
    transfer_open = False
    transfer_close_rect = pygame.Rect(0, 0, 0, 0)
    transfer_save_rect = pygame.Rect(0, 0, 0, 0)
    transfer_country_rects: dict[str, pygame.Rect] = {}
    transfer_from_port_rects: list[tuple[str, pygame.Rect]] = []
    transfer_to_port_rects: list[tuple[str, pygame.Rect]] = []
    transfer_amount_rects: dict[str, pygame.Rect] = {}
    transfer_resource_rects: dict[str, pygame.Rect] = {}
    transfer_from_country = EMPIRE_ORDER[0]
    transfer_to_country = EMPIRE_ORDER[1]
    transfer_from_amount = ""
    transfer_to_amount = ""
    transfer_from_ports: set[str] = set()
    transfer_to_ports: set[str] = set()
    transfer_from_resources = {resource: 0 for resource in RESOURCE_ORDER}
    transfer_to_resources = {resource: 0 for resource in RESOURCE_ORDER}
    transfer_active_field = "from_amount"
    pending_attack: AttackPrompt | None = None
    attack_result: dict[str, int | str | bool] | None = None
    attack_button_rect = pygame.Rect(0, 0, 0, 0)
    attack_skip_rect = pygame.Rect(0, 0, 0, 0)
    attack_oil_rect = pygame.Rect(0, 0, 0, 0)
    attack_mode_ship_ids: set[int] = set()
    port_action_destination: str | None = None
    port_enter_rect = pygame.Rect(0, 0, 0, 0)
    port_sell_rect = pygame.Rect(0, 0, 0, 0)
    port_declare_rect = pygame.Rect(0, 0, 0, 0)
    port_store_rect = pygame.Rect(0, 0, 0, 0)
    port_pickup_rect = pygame.Rect(0, 0, 0, 0)
    port_speed_rect = pygame.Rect(0, 0, 0, 0)
    port_attack_rect = pygame.Rect(0, 0, 0, 0)
    port_action_expires_at = 0
    enroute_continue_rect = pygame.Rect(0, 0, 0, 0)
    enroute_return_rect = pygame.Rect(0, 0, 0, 0)
    enroute_speed_rect = pygame.Rect(0, 0, 0, 0)
    enroute_join_rect = pygame.Rect(0, 0, 0, 0)
    enroute_attack_rect = pygame.Rect(0, 0, 0, 0)
    enroute_action_target: Ship | None = None
    enroute_target_expires_at = 0
    ports_expanded = False
    dragging_map = False
    last_drag_pos = (0, 0)
    port_edit_mode = False
    dragging_port: str | None = None
    selected_edit_port: str | None = None
    edit_status_message = ""
    edit_status_until = 0

    def active_player() -> PlayerState:
        return players[active_player_idx]

    def finish_game() -> None:
        nonlocal game_over, show_game_over_popup, game_over_evaluation, game_over_export_path
        if game_over:
            return
        game_over_evaluation = evaluate_players(players, history_events)
        history_events.append(
            HistoryEvent(
                round_number,
                "evaluation",
                "Final result",
                game_over_evaluation,
            )
        )
        game_over_export_path = export_game_history(history_events, game_over_evaluation)
        game_over = True
        show_game_over_popup = True

    def ships_waiting_for_goods() -> set[int]:
        return {transfer.waiting_ship_id for transfer in pending_goods_transfers if transfer.waiting_ship_id is not None}

    def operable_ships() -> list[Ship]:
        waiting_ship_ids = ships_waiting_for_goods()
        return [
            ship
            for ship in active_player().ships
            if id(ship) not in acted_ship_ids and id(ship) not in waiting_ship_ids
        ]

    def advance_round() -> None:
        nonlocal round_number, acted_ship_ids, last_tax_summary, last_resource_summary, last_storage_fee_summary
        nonlocal last_maintenance_summary, last_price_drop_round, news_popup_events, news_popup_until
        completed_round = round_number
        round_number += 1
        acted_ship_ids = set()
        battle_power_penalties.clear()
        attack_mode_ship_ids.clear()
        expire_player_licenses(players, round_number)
        expire_news_events(active_news, resource_prices, round_number, history_events)
        sunk_counts = sink_overdue_ships()
        if any(sunk_counts.values()):
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="ship",
                    title="Ships sunk by sail limit",
                    details=[
                        f"{country}: {count} sunk"
                        for country, count in sunk_counts.items()
                        if count
                    ][:4],
                )
            )
        advance_pending_goods_transfers(
            pending_goods_transfers,
            players,
            port_storage_by_port,
            round_number,
            history_events,
        )
        if completed_round % 5 == 0:
            new_events = [create_maritime_news(round_number), create_economic_news(round_number, resource_prices)]
            active_news.extend(new_events)
            append_news_history(history_events, round_number, new_events)
            news_popup_events = new_events
            news_popup_until = pygame.time.get_ticks() + 10000
            last_tax_summary = collect_taxes(players, round_number)
            history_events.append(
                HistoryEvent(
                    round_number,
                    "tax",
                    "Tax income collected",
                    [f"{country}: +${last_tax_summary.get(country, 0)}" for country in EMPIRE_ORDER],
                )
            )
            last_resource_summary = collect_factory_resources(players)
            last_maintenance_summary = collect_ship_maintenance(players, round_number)
            last_storage_fee_summary = collect_storage_fees(players, port_storage_by_port, round_number)
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="resources",
                    title="Factory resources collected",
                    details=[
                        f"{country}: " + ", ".join(resource_gain_lines(last_resource_summary, country))
                        for country in EMPIRE_ORDER
                    ][:3],
                )
            )
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="maintenance",
                    title="Non-merchant upkeep paid",
                    details=[
                        f"{country}: -${last_maintenance_summary.get(country, 0)}"
                        for country in EMPIRE_ORDER
                    ][:3],
                )
            )
            if any(last_storage_fee_summary.values()):
                history_events.append(
                    HistoryEvent(
                        round_number=round_number,
                        kind="goods",
                        title="Port storage fees paid",
                        details=[
                            f"{country}: -${last_storage_fee_summary.get(country, 0)}"
                            for country in EMPIRE_ORDER
                        ][:3],
                    )
                )
        decrease, last_price_drop_round = apply_resource_price_decay(
            resource_prices,
            round_number,
            last_price_drop_round,
        )
        if decrease:
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="price",
                    title="Resource prices cooled down",
                    details=[f"All resource prices -${decrease}.", *price_snapshot_lines(resource_prices)[:2]],
                )
            )
        if round_number > max_rounds:
            finish_game()

    def resolve_pending_attack_once() -> None:
        nonlocal attack_result, last_price_drop_round, selected_ship
        if not pending_attack:
            return
        attacker_player = player_by_country(players, pending_attack.attacker.owner)
        if attacker_player:
            _, action_label, _ = combat_action(pending_attack)
            attacker_player.money -= 20
            record_transaction(attacker_player, round_number, -20, f"{action_label} start cost")
        attack_result = resolve_attack(pending_attack, players, battle_power_penalties, round_number)
        price_increase = 0
        if attack_result["is_war"]:
            price_increase = apply_war_price_increase(
                resource_prices,
                round_number,
                price_increase_by_window,
            )
            last_price_drop_round = round_number
        append_combat_history(
            history_events,
            round_number,
            attack_result,
            price_increase,
            resource_prices,
        )
        captured_port = str(attack_result.get("captured_port") or "")
        if captured_port:
            transferred = transfer_captured_port_storage(captured_port, str(attack_result["winner"]), players, port_storage_by_port)
            if transferred:
                history_events.append(
                    HistoryEvent(
                        round_number,
                        "war",
                        f"{display_place_name(captured_port)} storage captured",
                        [f"{transferred} stored load(s) transferred to {attack_result['winner']}"],
                    )
                )
        if (
            player_for_ship(players, pending_attack.attacker) is not None
            and not ship_is_enroute(pending_attack.attacker)
            and pending_attack.attacker.distance_since_upkeep > 0
        ):
            process_ship_arrival(pending_attack.attacker)
        if selected_ship and player_for_ship(players, selected_ship) is None:
            selected_ship = None

    def process_ship_arrival(ship: Ship) -> None:
        charge_ship_arrival_upkeep(ship, players, round_number, history_events)
        charge_arrival_fee(ship, players, round_number)
        ship.last_port_round = round_number

    def sink_overdue_ships() -> dict[str, int]:
        sunk_counts = {country: 0 for country in EMPIRE_ORDER}
        for player in players:
            survivors = []
            for ship in player.ships:
                if ship_is_enroute(ship) and round_number - ship.last_port_round >= 4:
                    sunk_counts[player.country] += 1
                    if ship.kind == "Merchant" and ship.trade_card:
                        ship.trade_card.status = "sunk"
                    ship.distance_since_upkeep = 0
                    history_events.append(
                        HistoryEvent(
                            round_number=round_number,
                            kind="ship",
                            title=f"{player.country} ship sunk by sail limit",
                            details=[
                                f"{ship.name}: {ship_kind_label(ship, player=player)}",
                                f"Last port entry: R{ship.last_port_round}",
                                "Unfinished voyage distance was not charged.",
                            ],
                        )
                    )
                    record_transaction(player, round_number, 0, f"{ship.name} sunk by sail limit")
                else:
                    survivors.append(ship)
            player.ships = survivors
        return sunk_counts

    def auto_advance_enroute_ships_for_active_player() -> bool:
        nonlocal selected_ship, selected_idx
        selected_ship = None
        for ship in list(active_player().ships):
            if not ship_is_enroute(ship):
                continue
            old_pos = ship_screen_position(ship)
            advance_ship(ship, players, active_news, round_number)
            check_attack_after_move(ship, old_pos, ship.attack_on_arrival)
            if not ship_is_enroute(ship) and not pending_attack:
                process_ship_arrival(ship)
                ship.attack_on_arrival = False
                complete_trade_if_ready(ship, players, round_number, history_events, last_trade_summary)
            if pending_attack:
                selected_idx = active_player_idx
                resolve_pending_attack_once()
                return True
        return False

    def begin_active_player_turn() -> None:
        nonlocal selected_idx, selected_ship
        selected_ship = None
        selected_idx = active_player_idx
        completed_builds = complete_pending_ship_builds(active_player(), pending_ship_builds, round_number)
        for build in completed_builds:
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="ship",
                    title=f"{build.owner} completed a {build.kind}",
                    details=[f"Built at {display_place_name(build.location)}"],
                )
            )
        if not pending_attack:
            pass

    def mark_ship_done(ship: Ship | None) -> None:
        nonlocal selected_ship
        if ship:
            acted_ship_ids.add(id(ship))
            attack_mode_ship_ids.discard(id(ship))
        if ship is selected_ship:
            selected_ship = None

    def next_player_turn() -> None:
        nonlocal active_player_idx, selected_idx, selected_ship
        for ship in active_player().ships:
            acted_ship_ids.add(id(ship))
            attack_mode_ship_ids.discard(id(ship))
        selected_ship = None
        next_idx = (active_player_idx + 1) % len(players)
        if next_idx == 0:
            advance_round()
        active_player_idx = next_idx
        selected_idx = active_player_idx
        begin_active_player_turn()

    def restart_game() -> None:
        nonlocal players, selected_idx, active_player_idx, round_number, max_rounds, game_over, show_game_over_popup
        nonlocal game_over_evaluation, game_over_export_path
        nonlocal acted_ship_ids, ports_expanded, selected_ship
        nonlocal trade_card_options, selected_trade_card, trade_card_confirmed, treaties
        nonlocal last_tax_summary, last_resource_summary, last_maintenance_summary, last_storage_fee_summary
        nonlocal last_trade_summary, pending_ship_builds, port_storage_by_port, pending_goods_transfers
        nonlocal transfer_from_ports, transfer_to_ports, transfer_from_resources, transfer_to_resources
        nonlocal history_events, resource_prices, price_increase_by_window, battle_power_penalties, last_price_drop_round
        nonlocal transaction_scroll, transaction_max_scroll, side_panel_scroll, side_panel_max_scroll, rules_open, rules_scroll, rules_max_scroll
        nonlocal active_news, news_popup_events, news_popup_until
        players = randomize_game()
        for node in MAP_NODES.values():
            node.factory_level = None
            node.factory_owner = None
            node.entry_mode = "default"
            node.entry_countries.clear()
            node.free_entry_countries.clear()
        selected_idx = 0
        active_player_idx = 0
        round_number = 1
        max_rounds = DEFAULT_MAX_ROUNDS
        game_over = False
        show_game_over_popup = False
        game_over_evaluation = []
        game_over_export_path = None
        acted_ship_ids = set()
        attack_mode_ship_ids.clear()
        selected_ship = None
        trade_card_options = []
        selected_trade_card = None
        trade_card_confirmed = False
        treaties = []
        last_tax_summary = {}
        last_resource_summary = {}
        last_maintenance_summary = {}
        last_storage_fee_summary = {}
        last_trade_summary = {}
        history_events = []
        active_news = []
        news_popup_events = []
        news_popup_until = 0
        pending_ship_builds = []
        port_storage_by_port = defaultdict(list)
        pending_goods_transfers = []
        resource_prices = initial_resource_prices()
        price_increase_by_window = {}
        battle_power_penalties = {}
        last_price_drop_round = round_number
        transfer_from_ports = set()
        transfer_to_ports = set()
        transfer_from_resources = {resource: 0 for resource in RESOURCE_ORDER}
        transfer_to_resources = {resource: 0 for resource in RESOURCE_ORDER}
        ports_expanded = False
        transaction_scroll = 0
        transaction_max_scroll = 0
        side_panel_scroll = 0
        side_panel_max_scroll = 0
        rules_open = False
        rules_scroll = 0
        rules_max_scroll = 0

    def open_trade_card_choices() -> None:
        nonlocal trade_card_options, selected_trade_card, trade_card_open, market_open, trade_card_confirmed
        nonlocal history_open, build_open, new_ship_open, rules_open
        player = players[selected_idx]
        cost = active_trade_card_cost(active_news)
        if player.country == "Pirates" or player.money < cost:
            return
        player.money -= cost
        record_transaction(player, round_number, -cost, "draw trade cards")
        history_events.append(
            HistoryEvent(
                round_number,
                "invest",
                f"{player.country} invested in trade cards",
                [f"Cost: ${cost}"],
            )
        )
        trade_card_options = draw_trade_card_options()
        selected_trade_card = None
        trade_card_confirmed = False
        trade_card_open = True
        market_open = False
        history_open = False
        build_open = False
        new_ship_open = False
        rules_open = False

    def open_treaty_page() -> None:
        nonlocal treaty_open, market_open, trade_card_open, treaty_draft_text, treaty_selected_countries
        nonlocal history_open, build_open, new_ship_open, rules_open
        nonlocal treaty_effective_round, treaty_expire_round, treaty_active_field
        treaty_open = True
        market_open = False
        trade_card_open = False
        history_open = False
        build_open = False
        new_ship_open = False
        rules_open = False
        treaty_draft_text = ""
        treaty_selected_countries = {players[selected_idx].country}
        treaty_effective_round = round_number
        treaty_expire_round = round_number
        treaty_active_field = "text"

    def open_transfer_page() -> None:
        nonlocal transfer_open, market_open, trade_card_open, treaty_open, history_open, build_open, new_ship_open, rules_open
        nonlocal transfer_from_country, transfer_to_country, transfer_from_amount, transfer_to_amount
        nonlocal transfer_from_ports, transfer_to_ports, transfer_from_resources, transfer_to_resources, transfer_active_field
        transfer_open = True
        market_open = False
        trade_card_open = False
        treaty_open = False
        history_open = False
        build_open = False
        new_ship_open = False
        rules_open = False
        transfer_from_country = players[selected_idx].country
        transfer_to_country = next(country for country in EMPIRE_ORDER if country != transfer_from_country)
        transfer_from_amount = ""
        transfer_to_amount = ""
        transfer_from_ports = set()
        transfer_to_ports = set()
        transfer_from_resources = {resource: 0 for resource in RESOURCE_ORDER}
        transfer_to_resources = {resource: 0 for resource in RESOURCE_ORDER}
        transfer_active_field = "from_amount"

    def open_build_page() -> None:
        nonlocal build_open, market_open, trade_card_open, treaty_open, transfer_open, history_open, new_ship_open, rules_open, arrange_scroll
        build_open = True
        arrange_scroll = 0
        market_open = False
        trade_card_open = False
        treaty_open = False
        transfer_open = False
        history_open = False
        new_ship_open = False
        rules_open = False

    def open_new_ship_page() -> None:
        nonlocal new_ship_open, build_open, market_open, trade_card_open, treaty_open, transfer_open, history_open, rules_open
        new_ship_open = True
        build_open = False
        market_open = False
        trade_card_open = False
        treaty_open = False
        transfer_open = False
        history_open = False
        rules_open = False

    def open_rules_page() -> None:
        nonlocal rules_open, rules_scroll, market_open, trade_card_open, treaty_open, transfer_open, history_open, build_open, new_ship_open
        rules_open = True
        rules_scroll = 0
        market_open = False
        trade_card_open = False
        treaty_open = False
        transfer_open = False
        history_open = False
        build_open = False
        new_ship_open = False

    def check_attack_after_move(ship: Ship, old_pos: tuple[int, int], attack_requested: bool | None = None) -> None:
        nonlocal pending_attack, attack_result
        wants_attack = (id(ship) in attack_mode_ship_ids) if attack_requested is None else attack_requested
        if not wants_attack or not ship_can_attack(ship, players):
            return
        prompt = find_attack_prompt(ship, players, old_pos, ship_screen_position(ship))
        if prompt:
            pending_attack = prompt
            attack_result = None
        return

    def move_selected_ship_to(destination: str, attack_requested: bool) -> None:
        nonlocal port_action_destination, port_action_expires_at
        current = selected_ship
        if not current:
            return
        if not attack_requested and not can_ship_enter_port(current, destination, active_news, players):
            port_action_destination = None
            port_action_expires_at = 0
            return
        current.attack_on_arrival = bool(attack_requested and ship_can_attack(current, players))
        old_pos = ship_screen_position(current)
        if move_ship_toward(current, destination, players, active_news, round_number):
            check_attack_after_move(current, old_pos, attack_requested)
            if not ship_is_enroute(current) and not pending_attack:
                process_ship_arrival(current)
                current.attack_on_arrival = False
                complete_trade_if_ready(current, players, round_number, history_events, last_trade_summary)
            mark_ship_done(current)
            port_action_destination = None
            port_action_expires_at = 0

    def speed_selected_enroute_ship() -> None:
        player = active_player()
        current = selected_ship
        if not current or not ship_is_enroute(current) or current.sugar_speed_active:
            return
        if player.resources.get("sugar", 0) <= 0:
            return
        player.resources["sugar"] -= 1
        current.sugar_speed_active = True
        record_transaction(player, round_number, 0, f"used sugar for {current.name} speed")
        advance_selected_enroute_ship(False)

    def sell_selected_ship_at(destination: str) -> None:
        nonlocal port_action_destination, port_action_expires_at
        current = selected_ship
        if not current or not can_sell_trade_at_port(current, destination):
            return
        if destination != current.location:
            old_pos = ship_screen_position(current)
            if not move_ship_toward(current, destination, players, active_news, round_number):
                return
            check_attack_after_move(current, old_pos, False)
            if ship_is_enroute(current) or pending_attack:
                mark_ship_done(current)
                port_action_destination = None
                port_action_expires_at = 0
                return
            process_ship_arrival(current)
        complete_trade_if_ready(current, players, round_number, history_events, last_trade_summary, force_sell=True)
        mark_ship_done(current)
        port_action_destination = None
        port_action_expires_at = 0

    def store_selected_ship_good() -> None:
        nonlocal port_action_destination, port_action_expires_at
        current = selected_ship
        if not current:
            return
        stored_card = current.trade_card
        stored_destination = current.trade_destination
        if store_ship_good(current, port_storage_by_port):
            history_events.append(
                HistoryEvent(
                    round_number=round_number,
                    kind="goods",
                    title=f"{current.owner} stored goods",
                    details=[
                        f"Port: {display_place_name(current.location)}",
                        f"Route: {stored_card.start} -> {stored_card.end}" if stored_card else "Route: unknown",
                        f"Destination: {display_place_name(stored_destination)}" if stored_destination else "Destination: unknown",
                    ],
                )
            )
            mark_ship_done(current)
        port_action_destination = None
        port_action_expires_at = 0

    def pickup_selected_ship_good(source_port: str) -> None:
        nonlocal port_action_destination, port_action_expires_at
        current = selected_ship
        if not current:
            return
        resolved_source = land_pickup_source_for_ship(
            current,
            source_port,
            port_storage_by_port,
            pending_goods_transfers,
        )
        if not resolved_source:
            port_action_destination = None
            port_action_expires_at = 0
            return
        if resolved_source == current.location:
            if pickup_good_here(current, port_storage_by_port, players):
                history_events.append(
                    HistoryEvent(
                        round_number=round_number,
                        kind="goods",
                        title=f"{current.owner} picked up stored goods",
                        details=[f"Port: {display_place_name(current.location)}", f"Ship: {current.name}"],
                    )
                )
                mark_ship_done(current)
        elif request_land_good_pickup(
            current,
            resolved_source,
            players,
            port_storage_by_port,
            pending_goods_transfers,
            round_number,
            history_events,
        ):
            mark_ship_done(current)
        port_action_destination = None
        port_action_expires_at = 0

    def declare_and_move_selected_ship_to(destination: str) -> None:
        nonlocal port_action_destination, port_action_expires_at
        current = selected_ship
        if not current:
            return
        if declare_trade_for_ship(active_player(), current, destination):
            if current.trade_card:
                history_events.append(
                    HistoryEvent(
                        round_number,
                        "invest",
                        f"{active_player().country} declared a trade route",
                        [
                            f"{current.trade_card.start} -> {current.trade_card.end}",
                            f"Destination: {display_place_name(current.trade_destination or destination)}",
                            f"Ship: {current.name}",
                        ],
                    )
                )
            if destination == current.location:
                mark_ship_done(current)
                port_action_destination = None
                port_action_expires_at = 0
                return
            move_selected_ship_to(destination, False)

    def advance_selected_enroute_ship(return_to_origin: bool = False) -> None:
        current = selected_ship
        if not current or not ship_is_enroute(current):
            return
        if return_to_origin:
            reverse_ship_course(current)
        old_pos = ship_screen_position(current)
        advance_ship(current, players, active_news, round_number)
        check_attack_after_move(current, old_pos, current.attack_on_arrival)
        if not ship_is_enroute(current) and not pending_attack:
            process_ship_arrival(current)
            current.attack_on_arrival = False
            complete_trade_if_ready(current, players, round_number, history_events, last_trade_summary)
        mark_ship_done(current)

    def join_enroute_target(target: Ship) -> None:
        current = selected_ship
        if not current or not ship_is_enroute(current):
            return
        if target.owner == current.owner:
            return
        if join_enroute_ship(current, target, active_news):
            mark_ship_done(current)

    def attack_enemy_ship_target(target: Ship) -> None:
        nonlocal pending_attack, attack_result
        current = selected_ship
        if not current or not ship_can_attack(current, players):
            return
        if not ships_can_fight(current, target, players):
            return
        if ship_is_enroute(current):
            if not join_enroute_ship(current, target, active_news):
                return
        elif not move_ship_to_intercept(current, target, active_news):
            return
        defender = attack_defender_for_target(current, target)
        location = defender.name if isinstance(defender, MapNode) else (current.location if not ship_is_enroute(current) else None)
        pending_attack = AttackPrompt(current, defender, "intercepted enemy ship", location)
        attack_result = None
        resolve_pending_attack_once()
        mark_ship_done(current)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        if edit_status_message and pygame.time.get_ticks() > edit_status_until:
            edit_status_message = ""
        if news_popup_events and pygame.time.get_ticks() > news_popup_until:
            news_popup_events = []
            news_popup_until = 0
        current_operable_ships = operable_ships()
        if selected_ship not in current_operable_ships:
            selected_ship = None
        current_ship = selected_ship
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    restart_game()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if show_game_over_popup and game_over_close_rect.collidepoint(event.pos):
                        show_game_over_popup = False
                    elif new_game_button_rect.collidepoint(event.pos):
                        restart_game()
                continue
            elif pending_attack and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if attack_button_rect.collidepoint(event.pos) and (
                    attack_result is None or can_continue_attack(pending_attack, players)
                ):
                    resolve_pending_attack_once()
                elif attack_oil_rect.collidepoint(event.pos) and attack_result is None:
                    attacker_player = player_by_country(players, pending_attack.attacker.owner)
                    if attacker_player and attacker_player.resources.get("oil", 0) > 0:
                        pending_attack.attacker_uses_oil = not pending_attack.attacker_uses_oil
                elif attack_skip_rect.collidepoint(event.pos):
                    pending_attack = None
                    attack_result = None
            elif news_popup_events and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if news_close_rect.collidepoint(event.pos):
                    news_popup_events = []
                    news_popup_until = 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags(fullscreen))
                    continue
                if pending_attack:
                    if event.key == pygame.K_ESCAPE:
                        pending_attack = None
                        attack_result = None
                    continue
                if event.key == pygame.K_e and not (
                    market_open or trade_card_open or treaty_open or transfer_open or history_open or build_open or new_ship_open or rules_open
                ):
                    port_edit_mode = not port_edit_mode
                    dragging_port = None
                    dragging_map = False
                    selected_ship = None
                    port_action_destination = None
                    edit_status_message = "Edit mode on" if port_edit_mode else "Edit mode off"
                    edit_status_until = pygame.time.get_ticks() + 1800
                    continue
                if port_edit_mode and event.key == pygame.K_s and (
                    pygame.key.get_mods() & (pygame.KMOD_CTRL | pygame.KMOD_META)
                ):
                    export_port_geo_coords(write_back=True)
                    edit_status_message = "Saved coords to abcde_pygame_map.py"
                    edit_status_until = pygame.time.get_ticks() + 2400
                    continue
                if event.key == pygame.K_ESCAPE:
                    if port_edit_mode:
                        port_edit_mode = False
                        dragging_port = None
                        dragging_map = False
                    elif market_open:
                        market_open = False
                    elif trade_card_open:
                        trade_card_open = False
                    elif treaty_open:
                        treaty_open = False
                    elif transfer_open:
                        transfer_open = False
                    elif history_open:
                        history_open = False
                    elif rules_open:
                        rules_open = False
                    elif build_open:
                        build_open = False
                    elif new_ship_open:
                        new_ship_open = False
                    else:
                        running = False
                if transfer_open:
                    if event.key == pygame.K_BACKSPACE:
                        if transfer_active_field == "from_amount":
                            transfer_from_amount = transfer_from_amount[:-1]
                        elif transfer_active_field == "to_amount":
                            transfer_to_amount = transfer_to_amount[:-1]
                    elif event.unicode and event.unicode.isdigit():
                        if transfer_active_field == "from_amount":
                            transfer_from_amount = (transfer_from_amount + event.unicode)[:6]
                        elif transfer_active_field == "to_amount":
                            transfer_to_amount = (transfer_to_amount + event.unicode)[:6]
                    continue
                if treaty_open:
                    if event.key == pygame.K_BACKSPACE:
                        treaty_draft_text = treaty_draft_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        treaty_draft_text += "\n"
                    elif event.key != pygame.K_ESCAPE and event.unicode:
                        treaty_draft_text += event.unicode
                    continue
                if market_open or trade_card_open or history_open or build_open or new_ship_open:
                    continue
                if port_edit_mode:
                    continue
                if pygame.K_1 <= event.key <= pygame.K_6:
                    selected_idx = event.key - pygame.K_1
                if event.key == pygame.K_b:
                    market_open = True
                    market_scroll = 0
                    trade_card_open = False
                    treaty_open = False
                    transfer_open = False
                    history_open = False
                    build_open = False
                    new_ship_open = False
                    rules_open = False
                if event.key == pygame.K_t:
                    open_trade_card_choices()
                if event.key == pygame.K_n:
                    open_treaty_page()
                if event.key == pygame.K_x:
                    open_transfer_page()
                if event.key == pygame.K_p:
                    ports_expanded = not ports_expanded
                if event.key == pygame.K_r:
                    restart_game()
                if event.key == pygame.K_s and current_ship:
                    mark_ship_done(current_ship)
                if event.key == pygame.K_a and current_ship and ship_can_attack(current_ship, players):
                    if ship_is_enroute(current_ship):
                        current_ship.attack_on_arrival = not current_ship.attack_on_arrival
                    elif id(current_ship) in attack_mode_ship_ids:
                        attack_mode_ship_ids.remove(id(current_ship))
                    else:
                        attack_mode_ship_ids.add(id(current_ship))
                if event.key == pygame.K_g and current_ship and ship_is_enroute(current_ship):
                    advance_selected_enroute_ship(False)
                if event.key == pygame.K_r and current_ship and ship_is_enroute(current_ship):
                    advance_selected_enroute_ship(True)
            elif pending_attack:
                continue
            elif market_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected_player = players[selected_idx]
                if market_close_rect.collidepoint(event.pos):
                    market_open = False
                else:
                    for license_key, rect in market_license_rects.items():
                        if rect.collidepoint(event.pos):
                            if try_buy_license(selected_player, license_key, round_number):
                                history_events.append(
                                    HistoryEvent(
                                        round_number,
                                        "license",
                                        f"{selected_player.country} acquired {LICENSES[license_key]['label']}",
                                        [f"Valid until R{selected_player.licenses[license_key]}"],
                                    )
                                )
                            break
                    else:
                        for resource, rect in market_buy_rects.items():
                            if rect.collidepoint(event.pos):
                                try_buy_resource(selected_player, resource, resource_prices, round_number)
                                break
                        else:
                            for resource, rect in market_sell_rects.items():
                                if rect.collidepoint(event.pos):
                                    try_sell_resource(selected_player, resource, resource_prices, round_number)
                                    break
            elif market_open and event.type == pygame.MOUSEWHEEL:
                market_scroll = max(0, min(market_max_scroll, market_scroll - event.y * 36))
            elif history_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if history_close_rect.collidepoint(event.pos):
                    history_open = False
            elif history_open and event.type == pygame.MOUSEWHEEL:
                history_scroll = max(0, min(history_max_scroll, history_scroll - event.y))
            elif rules_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rules_close_rect.collidepoint(event.pos):
                    rules_open = False
            elif rules_open and event.type == pygame.MOUSEWHEEL:
                rules_scroll = max(0, min(rules_max_scroll, rules_scroll - event.y * 36))
            elif build_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if build_close_rect.collidepoint(event.pos):
                    build_open = False
                else:
                    selected_player = players[selected_idx]
                    for action_kind, port_name, value, rect in build_action_rects:
                        if rect.collidepoint(event.pos):
                            node = MAP_NODES[port_name]
                            if action_kind == "factory":
                                build_factory(selected_player, node, value, resource_prices, round_number, history_events)
                            elif not can_arrange_port(selected_player, node):
                                break
                            elif action_kind == "mode":
                                node.entry_mode = value
                                if value not in ("allow_only", "reject_selected"):
                                    node.entry_countries.clear()
                            elif action_kind == "toggle_country":
                                if value in node.entry_countries:
                                    node.entry_countries.remove(value)
                                else:
                                    node.entry_countries.add(value)
                            elif action_kind == "toggle_free":
                                if value in node.free_entry_countries:
                                    node.free_entry_countries.remove(value)
                                else:
                                    node.free_entry_countries.add(value)
                            break
            elif build_open and event.type == pygame.MOUSEWHEEL:
                arrange_scroll = max(0, min(arrange_max_scroll, arrange_scroll - event.y))
            elif new_ship_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if new_ship_close_rect.collidepoint(event.pos):
                    new_ship_open = False
                else:
                    selected_player = players[selected_idx]
                    for port_name, ship_kind, rect in new_ship_action_rects:
                        if rect.collidepoint(event.pos):
                            queue_ship_build(
                                selected_player,
                                MAP_NODES[port_name],
                                ship_kind,
                                players,
                                pending_ship_builds,
                                round_number,
                                resource_prices,
                                history_events,
                            )
                            break
            elif trade_card_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if trade_card_close_rect.collidepoint(event.pos):
                    trade_card_open = False
                elif trade_card_confirm_rect.collidepoint(event.pos) and selected_trade_card and not trade_card_confirmed:
                    selected_trade_card = choose_trade_card(players[selected_idx], selected_trade_card)
                    history_events.append(
                        HistoryEvent(
                            round_number,
                            "invest",
                            f"{players[selected_idx].country} selected a trade route",
                            [f"{selected_trade_card.start} -> {selected_trade_card.end}", f"Profit: ${selected_trade_card.profit}"],
                        )
                    )
                    trade_card_confirmed = True
                elif not trade_card_confirmed:
                    for rect, card in trade_card_option_rects:
                        if rect.collidepoint(event.pos):
                            selected_trade_card = card
                            break
            elif treaty_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if treaty_close_rect.collidepoint(event.pos):
                    treaty_open = False
                elif treaty_save_rect.collidepoint(event.pos):
                    if treaty_draft_text.strip() and treaty_selected_countries and treaty_effective_round <= treaty_expire_round:
                        treaties.append(
                            Treaty(
                                treaty_draft_text.strip(),
                                sorted(treaty_selected_countries, key=EMPIRE_ORDER.index),
                                treaty_effective_round,
                                treaty_expire_round,
                            )
                        )
                        treaty_open = False
                elif treaty_text_rect.collidepoint(event.pos):
                    treaty_active_field = "text"
                else:
                    for country, rect in treaty_country_rects:
                        if rect.collidepoint(event.pos):
                            if country in treaty_selected_countries:
                                treaty_selected_countries.remove(country)
                            else:
                                treaty_selected_countries.add(country)
                            break
                    else:
                        if treaty_controls.get("effective_minus", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                            treaty_effective_round = max(1, treaty_effective_round - 1)
                            treaty_active_field = "effective"
                        elif treaty_controls.get("effective_plus", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                            treaty_effective_round += 1
                            treaty_active_field = "effective"
                        elif treaty_controls.get("expire_minus", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                            treaty_expire_round = max(1, treaty_expire_round - 1)
                            treaty_active_field = "expire"
                        elif treaty_controls.get("expire_plus", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                            treaty_expire_round += 1
                            treaty_active_field = "expire"
            elif transfer_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if transfer_close_rect.collidepoint(event.pos):
                    transfer_open = False
                elif transfer_save_rect.collidepoint(event.pos):
                    if apply_transfer(
                        players,
                        transfer_from_country,
                        transfer_to_country,
                        transfer_from_amount,
                        transfer_to_amount,
                        transfer_from_ports,
                        transfer_to_ports,
                        transfer_from_resources,
                        transfer_to_resources,
                        round_number,
                    ):
                        transfer_open = False
                elif transfer_amount_rects.get("from_amount", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    transfer_active_field = "from_amount"
                elif transfer_amount_rects.get("to_amount", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    transfer_active_field = "to_amount"
                else:
                    clicked_transfer = False
                    for key, rect in transfer_country_rects.items():
                        if rect.collidepoint(event.pos):
                            side, country = key.split(":", 1)
                            if side == "from":
                                transfer_from_country = country
                                if transfer_to_country == transfer_from_country:
                                    transfer_to_country = next(c for c in EMPIRE_ORDER if c != transfer_from_country)
                                transfer_from_ports = set()
                                transfer_to_ports = set()
                                transfer_from_resources = {resource: 0 for resource in RESOURCE_ORDER}
                                transfer_to_resources = {resource: 0 for resource in RESOURCE_ORDER}
                            else:
                                transfer_to_country = country
                                if transfer_to_country == transfer_from_country:
                                    transfer_from_country = next(c for c in EMPIRE_ORDER if c != transfer_to_country)
                                transfer_from_ports = set()
                                transfer_to_ports = set()
                                transfer_from_resources = {resource: 0 for resource in RESOURCE_ORDER}
                                transfer_to_resources = {resource: 0 for resource in RESOURCE_ORDER}
                            clicked_transfer = True
                            break
                    if not clicked_transfer:
                        for port_name, rect in transfer_from_port_rects:
                            if rect.collidepoint(event.pos):
                                if port_name in transfer_from_ports:
                                    transfer_from_ports.remove(port_name)
                                else:
                                    transfer_from_ports.add(port_name)
                                clicked_transfer = True
                                break
                    if not clicked_transfer:
                        for port_name, rect in transfer_to_port_rects:
                            if rect.collidepoint(event.pos):
                                if port_name in transfer_to_ports:
                                    transfer_to_ports.remove(port_name)
                                else:
                                    transfer_to_ports.add(port_name)
                                clicked_transfer = True
                                break
                    if not clicked_transfer:
                        for key, rect in transfer_resource_rects.items():
                            if not rect.collidepoint(event.pos):
                                continue
                            side, resource, direction = key.split(":", 2)
                            selected_resources = transfer_from_resources if side == "from" else transfer_to_resources
                            payer_country = transfer_from_country if side == "from" else transfer_to_country
                            payer = player_by_country(players, payer_country)
                            available = payer.resources.get(resource, 0) if payer else 0
                            current = selected_resources.get(resource, 0)
                            if direction == "plus" and current < available:
                                selected_resources[resource] = current + 1
                            elif direction == "minus" and current > 0:
                                selected_resources[resource] = current - 1
                            break
            elif market_open:
                continue
            elif trade_card_open:
                continue
            elif history_open:
                continue
            elif rules_open:
                continue
            elif build_open:
                continue
            elif new_ship_open:
                continue
            elif treaty_open:
                continue
            elif transfer_open:
                continue
            elif event.type == pygame.MOUSEWHEEL:
                if panel_hover_cards.get("transactions", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_pos):
                    transaction_scroll = max(0, min(transaction_max_scroll, transaction_scroll - event.y))
                elif mouse_pos[0] >= SCREEN_WIDTH - SIDE_PANEL_WIDTH:
                    side_panel_scroll = max(0, min(side_panel_max_scroll, side_panel_scroll - event.y * 34))
                elif MAP_RECT.collidepoint(mouse_pos):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        pan_map(delta_x=-event.y * MAP_SCROLL_SPEED)
                    else:
                        pan_map(delta_x=event.x * MAP_SCROLL_SPEED, delta_y=-event.y * MAP_SCROLL_SPEED)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if round_limit_minus_rect.collidepoint(event.pos):
                    max_rounds = max(MIN_MAX_ROUNDS, max_rounds - 1)
                    if round_number > max_rounds:
                        finish_game()
                    continue
                if round_limit_plus_rect.collidepoint(event.pos):
                    max_rounds += 1
                    continue
                if port_edit_mode:
                    if MAP_RECT.collidepoint(event.pos):
                        clicked_port = port_at_position(event.pos)
                        if clicked_port:
                            dragging_port = clicked_port
                            selected_edit_port = clicked_port
                            move_port_to_screen(dragging_port, event.pos)
                        else:
                            dragging_map = True
                            last_drag_pos = event.pos
                    continue
                clicked_tab = False
                for idx, rect in enumerate(player_tab_rects):
                    if rect.collidepoint(event.pos):
                        selected_idx = idx
                        transaction_scroll = 0
                        clicked_tab = True
                if ports_card_rect.collidepoint(event.pos):
                    ports_expanded = not ports_expanded
                    clicked_tab = True
                if next_button_rect.collidepoint(event.pos):
                    next_player_turn()
                    clicked_tab = True
                if new_game_button_rect.collidepoint(event.pos):
                    restart_game()
                    clicked_tab = True
                if buy_button_rect.collidepoint(event.pos):
                    market_open = True
                    market_scroll = 0
                    trade_card_open = False
                    treaty_open = False
                    transfer_open = False
                    history_open = False
                    build_open = False
                    new_ship_open = False
                    rules_open = False
                    clicked_tab = True
                if trade_card_button_rect.collidepoint(event.pos):
                    open_trade_card_choices()
                    clicked_tab = True
                if new_treaty_button_rect.collidepoint(event.pos):
                    open_treaty_page()
                    clicked_tab = True
                if transfer_button_rect.collidepoint(event.pos):
                    open_transfer_page()
                    clicked_tab = True
                if history_button_rect.collidepoint(event.pos):
                    history_open = True
                    history_scroll = 0
                    market_open = False
                    trade_card_open = False
                    treaty_open = False
                    transfer_open = False
                    build_open = False
                    new_ship_open = False
                    rules_open = False
                    clicked_tab = True
                if new_factory_button_rect.collidepoint(event.pos):
                    open_build_page()
                    clicked_tab = True
                if new_ship_button_rect.collidepoint(event.pos):
                    open_new_ship_page()
                    clicked_tab = True
                if rules_button_rect.collidepoint(event.pos):
                    open_rules_page()
                    clicked_tab = True
                if not clicked_tab and port_action_destination and port_enter_rect.collidepoint(event.pos):
                    move_selected_ship_to(port_action_destination, False)
                    clicked_tab = True
                if not clicked_tab and port_action_destination and port_sell_rect.collidepoint(event.pos):
                    sell_selected_ship_at(port_action_destination)
                    clicked_tab = True
                if not clicked_tab and port_action_destination and port_declare_rect.collidepoint(event.pos):
                    declare_and_move_selected_ship_to(port_action_destination)
                    clicked_tab = True
                if not clicked_tab and port_action_destination and port_store_rect.collidepoint(event.pos):
                    store_selected_ship_good()
                    clicked_tab = True
                if not clicked_tab and port_action_destination and port_pickup_rect.collidepoint(event.pos):
                    pickup_selected_ship_good(port_action_destination)
                    clicked_tab = True
                if not clicked_tab and port_action_destination and port_attack_rect.collidepoint(event.pos):
                    move_selected_ship_to(port_action_destination, True)
                    clicked_tab = True
                if not clicked_tab and current_ship and ship_is_enroute(current_ship):
                    if enroute_continue_rect.collidepoint(event.pos):
                        advance_selected_enroute_ship(False)
                        clicked_tab = True
                    elif enroute_return_rect.collidepoint(event.pos):
                        advance_selected_enroute_ship(True)
                        clicked_tab = True
                    elif enroute_speed_rect.collidepoint(event.pos):
                        speed_selected_enroute_ship()
                        clicked_tab = True
                    elif enroute_action_target and enroute_join_rect.collidepoint(event.pos):
                        join_enroute_target(enroute_action_target)
                        clicked_tab = True
                    elif enroute_action_target and enroute_attack_rect.collidepoint(event.pos):
                        attack_enemy_ship_target(enroute_action_target)
                        clicked_tab = True
                if not clicked_tab and current_ship and MAP_RECT.collidepoint(event.pos) and not ship_is_enroute(current_ship):
                    target_ship = attackable_ship_at_position(current_ship, players, event.pos)
                    if target_ship:
                        attack_enemy_ship_target(target_ship)
                        clicked_tab = True
                if not clicked_tab and current_ship and MAP_RECT.collidepoint(event.pos) and not ship_is_enroute(current_ship):
                    destination = neighbor_at_position(current_ship.location, event.pos)
                    if destination and MAP_NODES[destination].owner == current_ship.owner:
                        move_selected_ship_to(destination, False)
                        clicked_tab = True
                if not clicked_tab and MAP_RECT.collidepoint(event.pos):
                    clicked_ship = clicked_operable_ship(current_operable_ships, event.pos, selected_ship)
                    if clicked_ship:
                        selected_ship = clicked_ship
                        current_ship = selected_ship
                        clicked_tab = True
                if not clicked_tab and MAP_RECT.collidepoint(event.pos):
                    dragging_map = True
                    last_drag_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_port = None
                dragging_map = False
            elif event.type == pygame.MOUSEMOTION and port_edit_mode and dragging_port:
                move_port_to_screen(dragging_port, event.pos)
                selected_edit_port = dragging_port
            elif event.type == pygame.MOUSEMOTION and dragging_map:
                pan_map(last_drag_pos[0] - event.pos[0], last_drag_pos[1] - event.pos[1])
                last_drag_pos = event.pos

        draw_world(screen)
        previous_clip = screen.get_clip()
        screen.set_clip(MAP_RECT)
        if not BACKGROUND_SURFACE:
            draw_port_based_world_outline(screen, small_font)
        draw_land_goods_routes(screen, small_font)
        hovered_port = draw_ports(screen, small_font, icon_font, players[selected_idx].country, mouse_pos)
        draw_stored_goods(screen, small_font, port_storage_by_port, pending_goods_transfers)
        hovered_edit_port = port_at_position(mouse_pos) if port_edit_mode and MAP_RECT.collidepoint(mouse_pos) else None
        if port_edit_mode:
            for edit_name, edit_color in ((hovered_edit_port, (255, 236, 142)), (selected_edit_port, (71, 158, 219))):
                if edit_name:
                    pygame.draw.circle(screen, edit_color, node_to_screen(edit_name), 22, 3)
        current_operable_ships = operable_ships()
        if selected_ship not in current_operable_ships:
            selected_ship = None
        if selected_ship and not port_edit_mode:
            draw_active_ship_choices(
                screen,
                small_font,
                selected_ship,
                selected_ship.attack_on_arrival if ship_is_enroute(selected_ship) else id(selected_ship) in attack_mode_ship_ids,
                players[selected_idx],
            )
        hovered_ship_location, ship_counts, hovered_ship = draw_ships(
            screen,
            small_font,
            players,
            mouse_pos,
            selected_ship,
            current_operable_ships,
        )
        if selected_ship and not port_edit_mode:
            draw_attackable_ship_targets(screen, small_font, selected_ship, players, active_news)
        now_ms = pygame.time.get_ticks()
        hovered_enroute_target = None
        if selected_ship and ship_is_enroute(selected_ship) and not port_edit_mode:
            hovered_enroute_target = enroute_target_at_position(selected_ship, players, mouse_pos, active_news)
        if hovered_enroute_target:
            enroute_action_target = hovered_enroute_target
            enroute_target_expires_at = now_ms + 2000
        elif (
            selected_ship
            and enroute_action_target
            and (enroute_join_rect.collidepoint(mouse_pos) or enroute_attack_rect.collidepoint(mouse_pos))
        ):
            enroute_target_expires_at = now_ms + 2000
        elif enroute_action_target and now_ms > enroute_target_expires_at:
            enroute_action_target = None
        hovered_action_destination = None if port_edit_mode else hovered_port_action(
            players[selected_idx],
            selected_ship,
            mouse_pos,
            port_storage_by_port,
            pending_goods_transfers,
            active_news,
        )
        if hovered_action_destination:
            port_action_destination = hovered_action_destination
            port_action_expires_at = now_ms + 2000
        elif (
            selected_ship
            and port_action_destination
            and (
                port_enter_rect.collidepoint(mouse_pos)
                or port_sell_rect.collidepoint(mouse_pos)
                or port_declare_rect.collidepoint(mouse_pos)
                or port_store_rect.collidepoint(mouse_pos)
                or port_pickup_rect.collidepoint(mouse_pos)
                or port_speed_rect.collidepoint(mouse_pos)
                or port_attack_rect.collidepoint(mouse_pos)
            )
        ):
            port_action_expires_at = now_ms + 2000
        elif port_action_destination and now_ms > port_action_expires_at:
            port_action_destination = None
        port_enter_rect = pygame.Rect(0, 0, 0, 0)
        port_sell_rect = pygame.Rect(0, 0, 0, 0)
        port_declare_rect = pygame.Rect(0, 0, 0, 0)
        port_store_rect = pygame.Rect(0, 0, 0, 0)
        port_pickup_rect = pygame.Rect(0, 0, 0, 0)
        port_speed_rect = pygame.Rect(0, 0, 0, 0)
        port_attack_rect = pygame.Rect(0, 0, 0, 0)
        enroute_continue_rect = pygame.Rect(0, 0, 0, 0)
        enroute_return_rect = pygame.Rect(0, 0, 0, 0)
        enroute_join_rect = pygame.Rect(0, 0, 0, 0)
        enroute_attack_rect = pygame.Rect(0, 0, 0, 0)
        screen.set_clip(previous_clip)
        player_tab_rects = draw_player_tabs(screen, small_font, players, selected_idx)
        round_limit_minus_rect, round_limit_plus_rect = draw_round_limit_controls(screen, small_font, round_number, max_rounds)
        draw_legend(screen, small_font)
        buy_button_rect = draw_market_button(screen, font)
        trade_card_button_rect = draw_trade_card_button(screen, font)
        new_treaty_button_rect = draw_new_treaty_button(screen, font)
        transfer_button_rect = draw_transfer_button(screen, font)
        history_button_rect = draw_history_button(screen, font)
        new_factory_button_rect = draw_new_factory_button(screen, font)
        new_ship_button_rect = draw_new_ship_button(screen, font)
        rules_button_rect = draw_rules_button(screen, font)
        tooltip_port = hovered_port
        if hovered_ship_location:
            tooltip_port = MAP_NODES.get(hovered_ship_location, hovered_port)
        tooltip_ship_location = hovered_ship_location or (tooltip_port.name if tooltip_port else None)
        draw_port_tooltip(
            screen,
            small_font,
            tooltip_port,
            mouse_pos,
            ship_counts,
            tooltip_ship_location,
        hovered_ship,
        port_storage_by_port,
        pending_goods_transfers,
        players,
    )
        if selected_ship and port_action_destination and not port_edit_mode:
            (
                port_enter_rect,
                port_sell_rect,
                port_declare_rect,
                port_store_rect,
                port_pickup_rect,
                port_speed_rect,
                port_attack_rect,
            ) = draw_port_action_popup(
                screen,
                small_font,
                players[selected_idx],
                selected_ship,
                port_action_destination,
                port_storage_by_port,
                pending_goods_transfers,
                active_news,
            )
        if selected_ship and ship_is_enroute(selected_ship) and not port_edit_mode:
            enroute_continue_rect, enroute_return_rect, enroute_speed_rect = draw_enroute_action_popup(
                screen,
                small_font,
                selected_ship,
                players[selected_idx],
            )
            if enroute_action_target:
                enroute_join_rect, enroute_attack_rect = draw_enroute_target_popup(
                    screen,
                    small_font,
                    selected_ship,
                    enroute_action_target,
                    players,
                )
        (
            ports_card_rect,
            next_button_rect,
            new_game_button_rect,
            panel_hover_cards,
            transaction_max_scroll,
            side_panel_max_scroll,
        ) = draw_side_panel(
            screen,
            title_font,
            font,
            small_font,
            players[selected_idx],
            hovered_port,
            ports_expanded,
            round_number,
            active_player().country,
            selected_ship,
            current_operable_ships,
            treaties,
            last_tax_summary,
            last_maintenance_summary,
            last_trade_summary,
            transaction_scroll,
            side_panel_scroll,
        )
        selected_player = players[selected_idx]
        if panel_hover_cards.get("resources", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_pos):
            lines = player_resource_lines(selected_player)
            if last_resource_summary:
                lines += ["Last factory gain:", *resource_gain_lines(last_resource_summary, selected_player.country)]
            draw_panel_popup(screen, small_font, "Resources", lines, mouse_pos)
        elif panel_hover_cards.get("ports", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Ports", player_port_lines(selected_player), mouse_pos)
        elif panel_hover_cards.get("ships", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Ships", player_ship_lines(selected_player, pending_ship_builds), mouse_pos)
        elif panel_hover_cards.get("trade", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_pos):
            lines = [f"Draw cost: ${active_trade_card_cost(active_news)}", *player_trade_lines(selected_player)]
            draw_panel_popup(screen, small_font, "Trade Info", lines, mouse_pos)
        elif panel_hover_cards.get("treaty", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Treaty", treaty_lines(treaties, selected_player.country), mouse_pos)
        elif panel_hover_cards.get("factories", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Factories", player_factory_lines(selected_player), mouse_pos)
        elif trade_card_button_rect.collidepoint(mouse_pos):
            lines = (
                ["Pirates cannot draw trade cards"]
                if selected_player.country == "Pirates"
                else [f"Draw cost: ${active_trade_card_cost(active_news)}", f"Cards: {len(selected_player.trade_cards)}"]
            )
            lines += [trade_card_display_line(card) for card in selected_player.trade_cards[-6:]]
            draw_panel_popup(screen, small_font, "Trade Info", lines, mouse_pos)
        elif new_treaty_button_rect.collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Treaty", ["Draft a new treaty", "Shortcut: N"], mouse_pos)
        elif transfer_button_rect.collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Transfer", ["Transfer money and/or ports", "Shortcut: X"], mouse_pos)
        elif buy_button_rect.collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Market", ["Buy and sell resources", "Letter of marque licenses"], mouse_pos)
        elif history_button_rect.collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "History", ["View wars and resource prices"], mouse_pos)
        elif new_factory_button_rect.collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Arrange", ["Arrange port entry rules", "Merchant ships are always accepted"], mouse_pos)
        elif new_ship_button_rect.collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "New Ship", ["Build a merchant or warship"], mouse_pos)
        elif rules_button_rect.collidepoint(mouse_pos):
            draw_panel_popup(screen, small_font, "Rules", ["View complete game rules"], mouse_pos)
        if port_edit_mode:
            draw_port_edit_overlay(
                screen,
                font,
                small_font,
                selected_edit_port,
                hovered_edit_port,
                edit_status_message,
            )

        if market_open:
            market_close_rect, market_buy_rects, market_sell_rects, market_license_rects, market_max_scroll = draw_market_page(
                screen,
                title_font,
                font,
                small_font,
                players[selected_idx],
                resource_prices,
                round_number,
                market_scroll,
            )
        elif history_open:
            history_close_rect, history_max_scroll = draw_history_page(
                screen,
                title_font,
                font,
                small_font,
                resource_prices,
                history_events,
                history_scroll,
            )
        elif rules_open:
            rules_close_rect, rules_max_scroll = draw_rules_page(
                screen,
                title_font,
                font,
                small_font,
                rules_scroll,
            )
        elif build_open:
            build_close_rect, build_action_rects, arrange_max_scroll = draw_arrange_page(
                screen,
                title_font,
                font,
                small_font,
                players[selected_idx],
                arrange_scroll,
                resource_prices,
            )
        elif new_ship_open:
            new_ship_close_rect, new_ship_action_rects = draw_new_ship_page(
                screen,
                title_font,
                font,
                small_font,
                players[selected_idx],
                players,
                pending_ship_builds,
                resource_prices,
            )
        elif trade_card_open:
            trade_card_close_rect, trade_card_confirm_rect, trade_card_option_rects = draw_trade_card_page(
                screen,
                title_font,
                font,
                small_font,
                players[selected_idx],
                trade_card_options,
                selected_trade_card,
                trade_card_confirmed,
            )
            hovered_trade_card = None
            for rect, card in trade_card_option_rects:
                if rect.collidepoint(mouse_pos):
                    hovered_trade_card = card
                    break
            if hovered_trade_card:
                draw_panel_popup(screen, small_font, "Trade Info", trade_info_lines(hovered_trade_card), mouse_pos)
        elif treaty_open:
            treaty_close_rect, treaty_save_rect, treaty_text_rect, treaty_country_rects, treaty_controls = draw_treaty_page(
                screen,
                title_font,
                font,
                small_font,
                treaty_draft_text,
                treaty_selected_countries,
                treaty_effective_round,
                treaty_expire_round,
                treaty_active_field,
            )
        elif transfer_open:
            (
                transfer_close_rect,
                transfer_save_rect,
                transfer_country_rects,
                transfer_from_port_rects,
                transfer_to_port_rects,
                transfer_amount_rects,
                transfer_resource_rects,
            ) = draw_transfer_page(
                screen,
                title_font,
                font,
                small_font,
                players,
                transfer_from_country,
                transfer_to_country,
                transfer_from_amount,
                transfer_to_amount,
                transfer_from_ports,
                transfer_to_ports,
                transfer_from_resources,
                transfer_to_resources,
                transfer_active_field,
            )
        if pending_attack:
            attack_button_rect, attack_skip_rect, attack_oil_rect = draw_attack_prompt(
                screen,
                title_font,
                font,
                small_font,
                pending_attack,
                attack_result,
                players,
            )
        if news_popup_events:
            news_close_rect = draw_news_popup(screen, title_font, font, small_font, news_popup_events)
        if game_over and show_game_over_popup:
            game_over_close_rect = draw_game_over_popup(
                screen,
                title_font,
                font,
                small_font,
                game_over_evaluation,
                game_over_export_path,
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
