"""Theme definitions for akYtec TV Dashboard."""

THEMES = {
    "akYtec Default": {
        "bg": "#0A0F1D",
        "surface": "rgba(15,23,42,0.75)",
        "border": "#1B3756",
        "accent1": "#00a69c",
        "accent2": "#e6007e",
        "text": "#CBD5E1",
        "muted": "#64748B",
        "green": "#22C55E",
        "amber": "#F5A623",
        "red": "#F87171",
        "label": "⚡ akYtec Default",
    },
    "Star Wars": {
        "bg": "#0A0A0A",
        "surface": "rgba(20,20,20,0.85)",
        "border": "#333333",
        "accent1": "#FFE81F",
        "accent2": "#FF4444",
        "text": "#E0E0E0",
        "muted": "#777777",
        "green": "#00FF41",
        "amber": "#FFE81F",
        "red": "#FF4444",
        "label": "⭐ Star Wars",
    },
    "Destiny 2": {
        "bg": "#0B1622",
        "surface": "rgba(12,25,40,0.85)",
        "border": "#1A3A5C",
        "accent1": "#4A9EFF",
        "accent2": "#C4A24E",
        "text": "#D4E4F7",
        "muted": "#5A7A9A",
        "green": "#50C878",
        "amber": "#C4A24E",
        "red": "#E84040",
        "label": "🔵 Destiny 2",
    },
    "StarCraft 2": {
        "bg": "#0D1117",
        "surface": "rgba(15,20,30,0.85)",
        "border": "#21262D",
        "accent1": "#00D4FF",
        "accent2": "#FF6B35",
        "text": "#C9D1D9",
        "muted": "#6E7681",
        "green": "#3FB950",
        "amber": "#D29922",
        "red": "#F85149",
        "label": "🚀 StarCraft 2",
    },
    "Formula 1": {
        "bg": "#15151E",
        "surface": "rgba(25,25,35,0.85)",
        "border": "#2A2A3A",
        "accent1": "#E10600",
        "accent2": "#FFD700",
        "text": "#F0F0F0",
        "muted": "#888888",
        "green": "#00D26A",
        "amber": "#FFD700",
        "red": "#E10600",
        "label": "🏎️ Formula 1",
    },
}

def get_theme(name):
    return THEMES.get(name, THEMES["akYtec Default"])

def get_theme_names():
    return list(THEMES.keys())
