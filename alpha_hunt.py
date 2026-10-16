import datetime
import math
import os
import random
import secrets
import threading
import time

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ALPHA HUNT Markets", page_icon="📈", layout="wide")

# ================================================================ CONFIG
try:
    ADMIN_PIN = st.secrets["ADMIN_PIN"]          # .streamlit/secrets.toml -> ADMIN_PIN = "..."
except Exception:
    ADMIN_PIN = os.environ.get("ADMIN_PIN", "MARKET2026")

G, R = "#00B386", "#EB5B3C"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [class*="css"] { font-family:'Inter', sans-serif; }
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #14213D 0%, #0B0F19 55%); color:#E6E9F0; }
header[data-testid="stHeader"] { background:transparent; }
.block-container { padding-top:1rem; max-width:1300px; }
h1,h2,h3,h4 { color:#fff !important; letter-spacing:.2px; }
.topbar { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;
  background:linear-gradient(90deg,#11182B,#16203A); border:1px solid #243256; border-radius:14px;
  padding:14px 22px; margin-bottom:12px; box-shadow:0 8px 24px rgba(0,0,0,.35); }
.brand { font-size:22px; font-weight:800; color:#fff; letter-spacing:.8px; }
.brand span { color:__G__; }
.pill { display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:.6px; }
.pill.open { background:#00B38622; color:__G__; border:1px solid #00B38666; }
.pill.closed { background:#EB5B3C22; color:__R__; border:1px solid #EB5B3C66; }
.pill.warn { background:#F5A62322; color:#F5A623; border:1px solid #F5A62366; }
.idx { color:#9AA4BD; font-size:14px; } .idx b { color:#fff; font-size:20px; margin:0 8px; }
.up { color:__G__; font-weight:600; } .down { color:__R__; font-weight:600; } .flat { color:#9AA4BD; }
.card { background:linear-gradient(160deg,#131C33,#0F1730); border:1px solid #243256; border-radius:14px;
  padding:18px 22px; box-shadow:0 6px 18px rgba(0,0,0,.3); margin-bottom:12px; }
.sub { color:#9AA4BD; font-size:12.5px; }
.big { font-size:36px; font-weight:800; color:#fff; line-height:1.1; }
.stat { display:inline-block; margin-right:26px; } .stat .l { color:#7E89A6; font-size:11px; text-transform:uppercase; letter-spacing:.8px; }
.stat .v { color:#fff; font-weight:600; font-size:15px; }
.badge { background:#1E2942; color:#8FB4FF; border-radius:6px; padding:2px 8px; font-size:11px; margin-left:8px; font-weight:500; }
.badge.new { background:__G__22; color:__G__; }
.heat { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:8px; margin-bottom:14px; }
.tile { border-radius:10px; padding:10px 12px; border:1px solid #ffffff10; }
.tile .n { font-weight:700; font-size:13px; color:#fff; } .tile .p { font-size:15px; font-weight:600; color:#fff; }
.tile .c { font-size:12px; font-weight:600; color:#fff; opacity:.95; }
table.wl { width:100%; border-collapse:collapse; font-size:14px; }
table.wl th { text-align:right; color:#7E89A6; font-weight:500; padding:10px; font-size:12px; text-transform:uppercase;
  letter-spacing:.6px; border-bottom:1px solid #243256; }
table.wl td { text-align:right; padding:11px 10px; border-bottom:1px solid #18223D; }
table.wl tr:hover td { background:#17213B; }
table.wl th:first-child, table.wl td:first-child { text-align:left; }
.news { border-left:3px solid __G__; background:#11182B; padding:12px 18px; margin-bottom:10px; border-radius:0 10px 10px 0; }
.news .t { color:#7E89A6; font-size:12px; }
.loan { border:1px solid #243256; background:#11182B; border-radius:10px; padding:12px 16px; margin-bottom:8px; }
div[data-testid="stMetric"] { background:linear-gradient(160deg,#131C33,#0F1730); border:1px solid #243256;
  padding:14px 18px; border-radius:14px; }
div[data-testid="stMetricLabel"] { color:#8A95B3; }
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] > div { font-size:1.45rem !important; font-weight:700;
  overflow:visible !important; text-overflow:clip !important; white-space:normal !important; line-height:1.2; }
div[data-testid="stMetricDelta"] { font-size:.8rem !important; }
div.stButton > button { background:#1B2744; color:#fff; border:1px solid #2C3D68; border-radius:10px;
  font-weight:700; width:100%; padding:10px; transition:all .15s; }
div.stButton > button:hover { border-color:__G__; color:__G__; transform:translateY(-1px); }
.st-key-buybtn button { background:__G__; border:none; color:#fff; box-shadow:0 4px 14px #00B38655; }
.st-key-buybtn button:hover { background:#009C74; color:#fff; }
.st-key-sellbtn button { background:__R__; border:none; color:#fff; box-shadow:0 4px 14px #EB5B3C55; }
.st-key-sellbtn button:hover { background:#D44A2D; color:#fff; }
button[data-baseweb="tab"] { font-weight:600; }
</style>
""".replace("__G__", G).replace("__R__", R)
st.markdown(CSS, unsafe_allow_html=True)

# ================================================================ MARKET DATA
# Ticker and company name are the SAME string everywhere.
SECTOR = {
    "WONKA": "Consumer Goods", "CYBERPET": "Robotics & AI", "ASTROJUMP": "Space Tourism",
    "NEONKICK": "Apparel & Footwear", "PIXELPULSE": "Gaming", "FLYBY": "Drone Logistics",
    "GLITCHBURGER": "Food & Dining", "COMICCAPES": "Media & Film", "HYDROPOP": "Beverages",
    "THUNDERVOLT": "Mobility",
    "MARSBASE": "Real Estate", "AQUAFARM": "Agri-Tech", "SOLARIS": "Renewable Energy",
    "MEDIBOT": "Healthcare Tech", "SKYRAIL": "Transport Infrastructure",
}
BASE_PRICES = {"WONKA": 100.0, "CYBERPET": 250.0, "ASTROJUMP": 500.0, "NEONKICK": 150.0,
               "PIXELPULSE": 200.0, "FLYBY": 120.0, "GLITCHBURGER": 80.0, "COMICCAPES": 300.0,
               "HYDROPOP": 50.0, "THUNDERVOLT": 400.0,
               "MARSBASE": 350.0, "AQUAFARM": 180.0, "SOLARIS": 260.0, "MEDIBOT": 420.0, "SKYRAIL": 140.0}
CORE = ["WONKA", "CYBERPET", "ASTROJUMP", "NEONKICK", "PIXELPULSE", "FLYBY",
        "GLITCHBURGER", "COMICCAPES", "HYDROPOP", "THUNDERVOLT"]
IPOS = ["MARSBASE", "AQUAFARM", "SOLARIS", "MEDIBOT", "SKYRAIL"]
START_CASH = 1_000_000.0

# 5 news items per company, shown together to the admin. (headline, story, % move for the company, {other stock: multiplier})
COMPANY_NEWS = {
    "WONKA": [
        ("WONKA launches premium chocolate range", "WONKA unveils a premium range aimed at gift buyers; pre-orders are strong.", 20, {}),
        ("WONKA recalls product batch", "WONKA recalls a batch over a labelling error. Analysts trim earnings estimates.", -30, {"HYDROPOP": 1.05}),
        ("WONKA opens online store", "WONKA starts direct online sales in 30 cities, widening its customer base.", 12, {}),
        ("WONKA cocoa costs surge", "Rising cocoa prices are expected to squeeze WONKA's margins this quarter.", -15, {}),
        ("WONKA posts record festive sales", "WONKA reports its best festive-season sales on record.", 25, {}),
    ],
    "CYBERPET": [
        ("CYBERPET wins education order", "CYBERPET wins a large order to supply learning robots to school districts.", 40, {"PIXELPULSE": 0.95}),
        ("CYBERPET issues software recall", "CYBERPET recalls a firmware update after reports of device malfunctions.", -25, {}),
        ("Regulator restricts classroom AI devices", "A new education policy restricts AI-assisted devices in classrooms.", -30, {}),
        ("CYBERPET unveils next-gen assistant", "CYBERPET launches a faster home assistant robot with improved safety features.", 30, {"MEDIBOT": 1.05}),
        ("CYBERPET faces data-privacy lawsuit", "A consumer group sues CYBERPET over how its devices store user data.", -20, {}),
    ],
    "ASTROJUMP": [
        ("ASTROJUMP secures lunar tourism licence", "ASTROJUMP receives approval to begin commercial lunar tourism flights.", 30, {"THUNDERVOLT": 1.05}),
        ("ASTROJUMP delays flagship launch", "ASTROJUMP postpones its flagship launch by six months for technical checks.", -20, {}),
        ("ASTROJUMP bookings sell out", "All ASTROJUMP seats for next year are booked, with a long waiting list.", 25, {}),
        ("ASTROJUMP inspection finds faults", "A safety inspection finds faults in an ASTROJUMP craft; flights are paused.", -25, {}),
        ("ASTROJUMP raises fresh funding", "ASTROJUMP raises new funds from investors to expand its fleet.", 15, {}),
    ],
    "NEONKICK": [
        ("NEONKICK signs athlete endorsement", "NEONKICK signs a multi-year deal with a leading national athlete.", 25, {"PIXELPULSE": 1.05}),
        ("NEONKICK expands to 40 countries", "NEONKICK announces expansion into 40 new international markets.", 20, {"THUNDERVOLT": 1.03}),
        ("NEONKICK faces factory labour inquiry", "Authorities open an inquiry into working conditions at a NEONKICK supplier.", -22, {}),
        ("NEONKICK launches smart-sole range", "NEONKICK releases footwear with built-in fitness tracking.", 18, {}),
        ("NEONKICK forced into discounts", "Excess inventory forces NEONKICK to cut prices, hurting margins.", -15, {}),
    ],
    "PIXELPULSE": [
        ("PIXELPULSE launches multiplayer platform", "PIXELPULSE launches a new online platform; sign-ups beat company targets.", 30, {"NEONKICK": 1.05}),
        ("PIXELPULSE suffers server outage", "PIXELPULSE servers go down for 18 hours; users are being compensated.", -30, {}),
        ("PIXELPULSE signs esports partnership", "PIXELPULSE becomes the official platform of a national esports league.", 20, {}),
        ("PIXELPULSE faces player-data complaint", "Parents' groups file a complaint about PIXELPULSE's data practices.", -18, {}),
        ("PIXELPULSE game tops download charts", "A new PIXELPULSE title reaches number one in downloads.", 28, {}),
    ],
    "FLYBY": [
        ("FLYBY fleet grounded for safety review", "FLYBY suspends its drone fleet pending a safety audit.", -20, {"GLITCHBURGER": 0.95}),
        ("FLYBY signs delivery deal with WONKA", "FLYBY and WONKA agree a long-term delivery partnership.", 25, {"WONKA": 1.10}),
        ("FLYBY gets city airspace approval", "FLYBY wins approval to operate delivery routes over three major cities.", 30, {}),
        ("FLYBY drone collision prompts probe", "A drone collision leads regulators to open an investigation into FLYBY.", -25, {}),
        ("FLYBY cuts costs with new batteries", "Longer-lasting batteries lower FLYBY's cost per delivery.", 15, {"THUNDERVOLT": 1.03}),
    ],
    "GLITCHBURGER": [
        ("GLITCHBURGER cuts supply costs", "GLITCHBURGER restructures its supply chain, expected to improve margins.", 25, {"FLYBY": 1.10}),
        ("GLITCHBURGER food-safety probe", "Health authorities investigate GLITCHBURGER's ingredient sourcing.", -30, {}),
        ("GLITCHBURGER opens 200 new outlets", "GLITCHBURGER announces a major expansion of its restaurant network.", 22, {}),
        ("GLITCHBURGER ingredient prices climb", "Higher ingredient prices threaten GLITCHBURGER's profit margins.", -12, {}),
        ("GLITCHBURGER launches loyalty app", "A new rewards app lifts GLITCHBURGER's repeat customers.", 14, {}),
    ],
    "COMICCAPES": [
        ("COMICCAPES announces film slate", "COMICCAPES unveils five major film releases and a streaming partnership.", 30, {"PIXELPULSE": 1.05}),
        ("COMICCAPES film leaks before release", "A major COMICCAPES film leaks online; box-office forecasts are cut.", -25, {}),
        ("COMICCAPES streaming subscribers double", "COMICCAPES reports its streaming subscriber base has doubled.", 28, {}),
        ("COMICCAPES lead actor exits franchise", "A star actor leaves a flagship COMICCAPES franchise.", -18, {}),
        ("COMICCAPES opening weekend beats forecast", "COMICCAPES's latest film earns more than analysts expected on opening weekend.", 22, {}),
    ],
    "HYDROPOP": [
        ("HYDROPOP wins national distribution deal", "HYDROPOP signs an exclusive nationwide deal with a major retail chain.", 35, {"WONKA": 1.05}),
        ("HYDROPOP posts record sales", "HYDROPOP reports its highest quarterly sales on strong demand.", 20, {"WONKA": 1.03}),
        ("HYDROPOP faces sugar-tax proposal", "A proposed sugar tax could raise HYDROPOP's prices and cut demand.", -18, {}),
        ("HYDROPOP bottling plant shut for repairs", "HYDROPOP closes a bottling plant for repairs, reducing supply.", -15, {}),
        ("HYDROPOP launches zero-sugar line", "HYDROPOP launches a zero-sugar range to reach health-conscious buyers.", 16, {}),
    ],
    "THUNDERVOLT": [
        ("THUNDERVOLT recalls hoverboards", "THUNDERVOLT recalls its latest hoverboards over a battery defect.", -30, {"ASTROJUMP": 1.03}),
        ("THUNDERVOLT unveils next-gen battery", "A longer-lasting battery from THUNDERVOLT could cut production costs.", 35, {"SOLARIS": 1.10, "NEONKICK": 1.03}),
        ("THUNDERVOLT lands city transport contract", "THUNDERVOLT wins a contract to supply electric scooters to a city.", 25, {}),
        ("THUNDERVOLT faces battery shortage", "A shortage of battery cells slows THUNDERVOLT's production.", -18, {}),
        ("THUNDERVOLT safety rating upgraded", "An independent body upgrades THUNDERVOLT's safety rating.", 12, {}),
    ],
    "MARSBASE": [
        ("MARSBASE secures land rights", "MARSBASE wins land-development rights for its first colony site.", 35, {"ASTROJUMP": 1.10}),
        ("MARSBASE construction costs overrun", "MARSBASE reports construction costs well above budget.", -22, {}),
        ("MARSBASE pre-sells first 1,000 units", "MARSBASE sells its first 1,000 housing units before construction starts.", 28, {}),
        ("MARSBASE permits paused by regulator", "A regulator pauses MARSBASE's land permits pending a review.", -25, {}),
        ("MARSBASE partners with SOLARIS", "MARSBASE and SOLARIS agree a power-supply partnership.", 18, {"SOLARIS": 1.08}),
    ],
    "AQUAFARM": [
        ("AQUAFARM beats crop forecasts", "AQUAFARM reports crop yields well above forecasts.", 25, {"GLITCHBURGER": 1.05}),
        ("AQUAFARM hit by drought", "Drought conditions cut AQUAFARM's expected yields.", -22, {}),
        ("AQUAFARM signs export contract", "AQUAFARM wins a multi-year contract to export produce.", 30, {}),
        ("AQUAFARM pesticide rules tighten", "New pesticide rules will raise AQUAFARM's costs.", -12, {}),
        ("AQUAFARM unveils water-saving tech", "AQUAFARM introduces farming technology that cuts water use.", 18, {}),
    ],
    "SOLARIS": [
        ("Government announces solar subsidy", "A new subsidy for solar installations boosts demand for SOLARIS.", 35, {"THUNDERVOLT": 1.05}),
        ("SOLARIS panel defect investigation", "Regulators investigate a defect in a batch of SOLARIS panels.", -25, {}),
        ("SOLARIS wins state grid tender", "SOLARIS wins a state tender to supply solar power to the grid.", 30, {}),
        ("SOLARIS faces import duty on cells", "A new import duty raises SOLARIS's cost of solar cells.", -15, {}),
        ("SOLARIS opens new panel factory", "SOLARIS opens a factory that will double its panel output.", 20, {}),
    ],
    "MEDIBOT": [
        ("MEDIBOT approved for hospital trials", "MEDIBOT receives approval to begin hospital trials of its assistive robots.", 40, {}),
        ("MEDIBOT trial paused for safety review", "A MEDIBOT hospital trial is paused while a safety issue is reviewed.", -30, {}),
        ("MEDIBOT secures hospital network deal", "MEDIBOT agrees to supply a national hospital network.", 28, {}),
        ("MEDIBOT rival launches cheaper device", "A competitor launches a cheaper device, pressuring MEDIBOT's prices.", -15, {}),
        ("MEDIBOT gets international certification", "MEDIBOT earns certification that opens overseas markets.", 22, {}),
    ],
    "SKYRAIL": [
        ("SKYRAIL project delayed", "SKYRAIL's flagship rail project is delayed by a funding gap.", -25, {}),
        ("SKYRAIL wins metro corridor contract", "SKYRAIL wins a contract to build a new metro corridor.", 32, {}),
        ("SKYRAIL land dispute", "A land acquisition dispute halts work on part of SKYRAIL's route.", -20, {}),
        ("SKYRAIL finishes first track early", "SKYRAIL completes its first track section ahead of schedule.", 24, {}),
        ("SKYRAIL funding approved", "The government approves new funding for SKYRAIL's network.", 30, {}),
    ],
}

# 15 random market news items for basic up/down movement. (headline, story, kind, min %, max %)
RANDOM_NEWS = [
    ("Analysts upgrade {c}", "Brokerages raise their rating on {c}, citing steady growth and healthy margins.", "one_up", 2, 5),
    ("Analysts downgrade {c}", "Several brokerages cut their rating on {c} over valuation concerns.", "one_down", 2, 5),
    ("{c} announces share buyback", "{c} will repurchase shares from the open market, signalling confidence.", "one_up", 3, 6),
    ("Profit booking seen in {c}", "Traders sell {c} to lock in recent gains, pushing the price lower.", "one_down", 2, 4),
    ("Institutions accumulate {c}", "Large funds are building positions in {c}, according to exchange data.", "one_up", 2, 4),
    ("Leadership change at {c}", "{c} says a senior executive will step down; investors await a successor.", "one_down", 3, 6),
    ("{c} wins industry award", "{c} is recognised for innovation at a national industry event.", "one_up", 1, 3),
    ("Supplier delays affect {c}", "{c} warns that late deliveries from suppliers may slow its output.", "one_down", 2, 5),
    ("Festive demand lifts markets", "Strong consumer demand in the festive season supports stocks across sectors.", "mkt_up", 1.5, 3),
    ("Global markets slip, local stocks follow", "Weak global cues push most local stocks lower in cautious trading.", "mkt_down", 1.5, 3),
    ("Foreign investors turn buyers", "Overseas funds buy into the market, lifting sentiment broadly.", "mkt_up", 1, 2.5),
    ("Inflation worries weigh on markets", "Higher-than-expected inflation data makes investors cautious.", "mkt_down", 1, 2.5),
    ("Money rotates from {c} to {c2}", "Investors move funds out of {c} and into {c2} as sentiment shifts.", "rotate", 2, 4),
    ("{c} and {c2} agree distribution tie-up", "The two firms will share distribution networks to cut costs.", "pair_up", 2, 4),
    ("{c} beats quarterly estimates", "{c} reports quarterly numbers ahead of analyst expectations.", "one_up", 3, 6),
]


# ================================================================ SHARED STATE
# st.session_state is per-browser; the game needs ONE shared market, so it lives here.
def fresh_ipo():
    return {t: {"state": "upcoming", "low": round(BASE_PRICES[t] * 0.9, 2), "high": round(BASE_PRICES[t] * 1.1, 2),
                "max_qty": 5000, "issue": None, "bids": {}, "results": {}} for t in IPOS}


@st.cache_resource
def get_store():
    return {
        "lock": threading.RLock(),
        "prices": dict(BASE_PRICES), "open_px": dict(BASE_PRICES),
        "pend_news": {t: 0.0 for t in BASE_PRICES}, "pend_trade": {t: 0.0 for t in BASE_PRICES},
        "flick": {t: 0.0 for t in BASE_PRICES}, "last_auto": time.time(),
        "history": [], "last": time.time(), "last_hist": 0.0,
        "news_feed": [], "listed": set(), "audit": [], "drift": {t: 0.0 for t in BASE_PRICES}, "ipo": fresh_ipo(),
        "open": True, "round_no": 1,
        "teams": {}, "codes": {},
        "cfg": {"float": 100_000, "impact": 1.5, "panic_frac": 0.75, "panic_min_float": 0.01,
                "panic_drop": 0.10, "trade_delay": 6.0, "news_mode": "slower", "news_gap": 4.0,
                "auto_news": True, "auto_every": 90.0, "noise": 0.5, "shocks": True,
                "show_rank": False},
    }


S = get_store()
now_s = lambda: datetime.datetime.now().strftime("%H:%M:%S")


def live():
    return CORE + [t for t in IPOS if t in S["listed"]]


def tau_trade():
    return max(1.0, S["cfg"]["trade_delay"])


def tau_news():
    c = S["cfg"]
    g = max(1.0, c["news_gap"])
    if c["news_mode"] == "slower":
        return tau_trade() * g
    if c["news_mode"] == "faster":
        return max(1.0, tau_trade() / g)
    return tau_trade()


def tick():
    """Trades and news each move prices at their own speed; random noise, drift and jumps run on top."""
    with S["lock"]:
        now = time.time()
        dt = now - S["last"]
        if dt < 0.5:
            return
        S["last"] = now
        cfg = S["cfg"]
        kt = 1 - math.exp(-dt / tau_trade())
        kn = 1 - math.exp(-dt / tau_news())
        sd = cfg["noise"] / 100 * math.sqrt(dt / 3)
        for t in live():
            rn, rt = S["pend_news"][t] * kn, S["pend_trade"][t] * kt     # share of each pending move released now
            S["pend_news"][t] -= rn
            S["pend_trade"][t] -= rt
            base = S["prices"][t] / (1 + S["flick"][t])
            d = S["drift"][t] * math.exp(-dt / 60) + random.gauss(0, sd * 0.25)   # slow-moving "mood"
            S["drift"][t] = d
            move = rn + rt
            if sd > 0:
                move += d * 0.2 + random.gauss(0, sd * 0.3)
                if cfg["shocks"] and random.random() < 0.02 * dt / 3:             # occasional random jump
                    S["pend_trade"][t] += random.choice([-1, 1]) * random.uniform(0.01, 0.035)
            base = max(1.0, base * math.exp(move))
            S["flick"][t] = max(-0.2, min(0.2, S["flick"][t] * math.exp(-dt / 10) + random.gauss(0, sd)))
            S["prices"][t] = round(max(1.0, base * (1 + S["flick"][t])), 2)     # visible up/down flicker
        if now - S["last_hist"] >= 3:
            S["last_hist"] = now
            S["history"].append({t: (S["prices"][t] if t in live() else None) for t in BASE_PRICES})
            S["history"] = S["history"][-400:]
        if cfg["auto_news"] and S["open"] and now - S["last_auto"] >= cfg["auto_every"]:
            S["last_auto"] = now
            fire_random_news()


def net_worth(team):
    return team["cash"] + sum(team["holdings"][t] * S["prices"][t] for t in live())


def index_value():
    return sum(S["prices"][t] / S["open_px"][t] for t in CORE) / len(CORE) * 1000


def pct_change(t):
    return (S["prices"][t] / S["open_px"][t] - 1) * 100


def fire_news(name, mods, desc):
    """News adds a pending price move that is released at the (separate) news speed."""
    with S["lock"]:
        for t, m in mods.items():
            if t in live() and m > 0:
                S["pend_news"][t] += math.log(m)
        S["news_feed"].insert(0, {"time": datetime.datetime.now().strftime("%H:%M"), "head": name, "desc": desc})


def fire_random_news():
    with S["lock"]:
        lv = live()
        head, desc, kind, lo, hi = random.choice(RANDOM_NEWS)
        pct = random.uniform(lo, hi) / 100
        c, c2 = random.sample(lv, 2)
        if kind == "one_up":
            mods = {c: 1 + pct}
        elif kind == "one_down":
            mods = {c: 1 - pct}
        elif kind == "mkt_up":
            mods = {t: 1 + pct * random.uniform(0.6, 1.4) for t in lv}
        elif kind == "mkt_down":
            mods = {t: 1 - pct * random.uniform(0.6, 1.4) for t in lv}
        elif kind == "rotate":
            mods = {c: 1 - pct, c2: 1 + pct}
        else:
            mods = {c: 1 + pct, c2: 1 + pct}
        fire_news(head.format(c=c, c2=c2), mods, desc.format(c=c, c2=c2))


def open_ipo(t, low, high, max_qty):
    with S["lock"]:
        S["ipo"][t].update(state="open", low=float(low), high=float(high), max_qty=int(max_qty),
                           bids={}, results={}, issue=None)
        S["news_feed"].insert(0, {"time": datetime.datetime.now().strftime("%H:%M"), "head": f"IPO opens: {t}",
                                  "desc": f"{t} ({SECTOR[t]}) opens for bidding. Price band ₹{low:,.2f} to ₹{high:,.2f}. "
                                          "Bids at or above the final issue price are allotted in full."})


def place_bid(tid, t, qty, price):
    with S["lock"]:
        c, team = S["ipo"][t], S["teams"][tid]
        if team["status"] != "active":
            return False, "Your account is restricted by the administrator."
        if c["state"] != "open":
            return False, "Bidding is not open for this IPO."
        if not (c["low"] <= price <= c["high"]):
            return False, f"Bid price must be within ₹{c['low']:,.2f} to ₹{c['high']:,.2f}."
        if qty < 1 or qty > c["max_qty"]:
            return False, f"Quantity must be between 1 and {c['max_qty']:,}."
        c["bids"][tid] = {"qty": int(qty), "price": float(price), "time": now_s()}
        return True, (f"Bid placed: {qty:,} shares at up to ₹{price:,.2f}. No money is taken now; "
                      "if allotted you pay the final issue price.")


def cancel_bid(tid, t):
    with S["lock"]:
        if S["ipo"][t]["state"] == "open":
            S["ipo"][t]["bids"].pop(tid, None)
            return True, "Bid cancelled."
        return False, "Bidding is closed."


def allot_ipo(t, issue):
    """Bids at or above the issue price get their full quantity at the issue price, deducted automatically."""
    with S["lock"]:
        tick()
        c = S["ipo"][t]
        if c["state"] != "open":
            return False, "Bidding is not open."
        issue = round(float(issue), 2)
        winners = shares = 0
        for tid, b in c["bids"].items():
            team = S["teams"][tid]
            q = 0
            if b["price"] >= issue and team["status"] == "active":
                q = b["qty"]
                if issue * q > team["cash"]:
                    q = int(team["cash"] // issue)
            if q > 0:
                team["cash"] -= issue * q
                team["holdings"][t] += q
                team["cost"][t] += issue * q
                rec = {"time": now_s(), "side": "IPO ALLOT", "stock": t, "qty": q, "price": issue}
                team["orders"].insert(0, rec)
                S["audit"].insert(0, {**rec, "team": tid})
                c["results"][tid] = f"Allotted {q:,} shares at ₹{issue:,.2f}. ₹{issue * q:,.2f} was deducted from your cash."
                winners += 1
                shares += q
            else:
                c["results"][tid] = f"Not allotted. Your bid was below the final issue price of ₹{issue:,.2f}."
        c.update(state="listed", issue=issue)
        S["listed"].add(t)
        S["prices"][t] = S["open_px"][t] = issue
        S["drift"][t] = S["flick"][t] = S["pend_news"][t] = S["pend_trade"][t] = 0.0
        S["news_feed"].insert(0, {"time": datetime.datetime.now().strftime("%H:%M"), "head": f"IPO allotment: {t} lists at ₹{issue:,.2f}",
                                  "desc": f"{t} fixes its issue price at ₹{issue:,.2f}. {winners} bidders were allotted {shares:,} shares. Trading begins now."})
        return True, f"{t} listed at ₹{issue:,.2f}: {winners} allotments, {shares:,} shares."


def new_team_record(code):
    return {"code": code, "label": "", "status": "active", "cash": START_CASH, "orders": [],
            "holdings": {t: 0 for t in BASE_PRICES}, "cost": {t: 0.0 for t in BASE_PRICES}}


def gen_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if code not in S["codes"] and code != ADMIN_PIN:
            return code


def add_teams(n):
    with S["lock"]:
        for _ in range(n):
            tid = f"Team {len(S['teams']) + 1:02d}"
            code = gen_code()
            S["teams"][tid] = new_team_record(code)
            S["codes"][code] = tid


def trade(tid, side, tk, qty):
    cfg = S["cfg"]
    with S["lock"]:
        tick()
        team = S["teams"][tid]
        if team["status"] != "active":
            return False, "Your account is restricted by the administrator."
        if not S["open"]:
            return False, "Market is closed. Orders are not being accepted."
        if tk not in live() or qty <= 0:
            return False, "Invalid order."
        px = S["prices"][tk]
        frac = qty / cfg["float"]
        impact = cfg["impact"] * frac
        if side == "BUY":
            fill = round(px * (1 + min(impact, 0.30)), 2)
            if fill * qty > team["cash"]:
                return False, "Insufficient funds."
            team["cash"] -= fill * qty
            team["holdings"][tk] += qty
            team["cost"][tk] += fill * qty
            S["pend_trade"][tk] += math.log(1 + min(impact, 0.30))
        else:
            held = team["holdings"][tk]
            if qty > held:
                return False, "Insufficient shares."
            if qty >= cfg["panic_frac"] * held and frac >= cfg["panic_min_float"]:
                impact += cfg["panic_drop"]
            drop = min(impact, 0.40)
            fill = round(px * (1 - drop), 2)
            avg = team["cost"][tk] / held
            team["cash"] += fill * qty
            team["holdings"][tk] -= qty
            team["cost"][tk] = max(0.0, team["cost"][tk] - avg * qty)
            S["pend_trade"][tk] += math.log(1 - drop)
        rec = {"time": now_s(), "side": side, "stock": tk, "qty": qty, "price": fill}
        team["orders"].insert(0, rec)
        S["audit"].insert(0, {**rec, "team": tid})
        S["audit"] = S["audit"][:500]
        return True, f"{side} order executed: {qty:,} × {tk} @ ₹{fill:,.2f}"


# ================================================================ UI HELPERS
def chg_html(pct):
    cls, arrow = ("up", "▲") if pct > 0.005 else ("down", "▼") if pct < -0.005 else ("flat", "•")
    return f"<span class='{cls}'>{arrow} {abs(pct):.2f}%</span>"


def spark(t, color):
    vals = [h[t] for h in S["history"][-30:] if h.get(t) is not None]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    pts = " ".join(f"{i * 90 / (len(vals) - 1):.1f},{26 - (v - lo) / rng * 24:.1f}" for i, v in enumerate(vals))
    return f"<svg width='90' height='28'><polyline points='{pts}' fill='none' stroke='{color}' stroke-width='1.8'/></svg>"


def status_pill():
    return ("<span class='pill open'>● MARKET OPEN</span>" if S["open"]
            else "<span class='pill closed'>● MARKET CLOSED</span>")


def topbar(extra=""):
    idx = index_value()
    st.markdown(f"<div class='topbar'><div class='brand'>📈 ALPHA HUNT <span>Markets</span></div>"
                f"<div>{status_pill()} {extra}</div>"
                f"<div class='idx'>ALPHA 10<b>{idx:,.2f}</b>{chg_html((idx / 1000 - 1) * 100)}</div></div>",
                unsafe_allow_html=True)


def heatmap():
    tiles = ""
    for t in live():
        p = pct_change(t)
        a = 0.18 + 0.55 * min(abs(p) / 10, 1)
        col = f"rgba(0,179,134,{a:.2f})" if p >= 0 else f"rgba(235,91,60,{a:.2f})"
        tiles += (f"<div class='tile' style='background:{col}'><div class='n'>{t}</div>"
                  f"<div class='p'>₹{S['prices'][t]:,.2f}</div><div class='c'>{'▲' if p >= 0 else '▼'} {abs(p):.2f}%</div></div>")
    st.markdown(f"<div class='heat'>{tiles}</div>", unsafe_allow_html=True)


def price_chart(series, color):
    df = pd.DataFrame({"tick": range(len(series)), "Price": list(series)})
    grad = alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                        stops=[alt.GradientStop(color="#0B0F1900", offset=0), alt.GradientStop(color=color + "66", offset=1)])
    base = alt.Chart(df).encode(
        x=alt.X("tick:Q", axis=None),
        y=alt.Y("Price:Q", scale=alt.Scale(zero=False), axis=alt.Axis(title=None, labelColor="#8A95B3", gridColor="#1B2540")),
        tooltip=["Price"])
    chart = (base.mark_area(color=grad, line={"color": color, "strokeWidth": 2.2}, interpolate="monotone")
             .properties(height=300).configure_view(strokeWidth=0).configure(background="transparent"))
    st.altair_chart(chart, width="stretch", theme=None)


# ================================================================ LOGIN
if "who" not in st.session_state:
    _, c, _ = st.columns([1, 1.3, 1])
    with c:
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card' style='text-align:center'>"
                    "<div class='brand' style='font-size:32px'>📈 ALPHA HUNT <span>Markets</span></div>"
                    "<div class='sub' style='margin:6px 0 4px'>Trade. Compete. Outsmart the market.</div></div>",
                    unsafe_allow_html=True)
        code = st.text_input("Access code", type="password", placeholder="Enter your private team code").strip()
        if st.button("Sign in"):
            if code == ADMIN_PIN:
                st.session_state.who = ("admin", None)
                st.rerun()
            elif code.upper() in S["codes"]:
                st.session_state.who = ("team", S["codes"][code.upper()])
                st.rerun()
            else:
                st.error("Invalid or deactivated access code.")
    st.stop()

role, tid = st.session_state.who
with st.sidebar:
    if st.button("Sign out"):
        del st.session_state["who"]
        st.rerun()


# ================================================================ PLAYER APP
@st.fragment(run_every=5)
def player_app(tid):
    tick()
    team = S["teams"][tid]
    if team["status"] == "closed":
        st.error("⛔ Your account has been closed by the administrator.")
        return
    restricted = "<span class='pill warn'>ACCOUNT SUSPENDED</span>" if team["status"] == "suspended" else ""
    topbar(restricted)
    if team["status"] == "suspended":
        st.warning("Your account is suspended. You can view the market but cannot trade or borrow. Contact the administrator.")

    t_mkt, t_pf, t_ipo, t_ord, t_news = st.tabs(["Markets", "Portfolio", "IPOs", "Orders", "News"])

    with t_mkt:
        heatmap()
        left, right = st.columns([2.2, 1])
        with left:
            tk = st.selectbox("Select stock", live(), key="tk", label_visibility="collapsed")
            px, chg = S["prices"][tk], pct_change(tk)
            vals = [h[tk] for h in S["history"] if h.get(tk) is not None] or [px]
            new = "<span class='badge new'>NEW LISTING</span>" if tk in IPOS else ""
            st.markdown(
                f"<div class='card'><div class='sub'>{SECTOR[tk]}</div>"
                f"<div style='font-size:20px;font-weight:700;color:#fff'>{tk}{new}</div>"
                f"<div class='big'>₹{px:,.2f} <span style='font-size:16px'>{chg_html(chg)}</span></div><br>"
                f"<span class='stat'><div class='l'>Open</div><div class='v'>₹{S['open_px'][tk]:,.2f}</div></span>"
                f"<span class='stat'><div class='l'>High</div><div class='v'>₹{max(vals + [px]):,.2f}</div></span>"
                f"<span class='stat'><div class='l'>Low</div><div class='v'>₹{min(vals + [px]):,.2f}</div></span>"
                f"<span class='stat'><div class='l'>You hold</div><div class='v'>{team['holdings'][tk]:,}</div></span></div>",
                unsafe_allow_html=True)
            if len(vals) > 1:
                price_chart(vals[-120:], G if chg >= 0 else R)
            else:
                st.caption("Chart will appear as trading begins.")
            rows = ""
            for t in live():
                c = G if pct_change(t) >= 0 else R
                rows += (f"<tr><td><b>{t}</b><span class='badge'>{SECTOR[t]}</span></td><td>{spark(t, c)}</td>"
                         f"<td>₹{S['prices'][t]:,.2f}</td><td>{chg_html(pct_change(t))}</td><td>{team['holdings'][t]:,}</td></tr>")
            st.markdown("<div class='card'><table class='wl'><tr><th>Stock</th><th>Trend</th><th>Price</th><th>Change</th>"
                        f"<th>Qty held</th></tr>{rows}</table></div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='card'><b style='color:#fff;font-size:17px'>Place order</b>"
                        "<div class='sub'>Market order · executes at the live price</div></div>", unsafe_allow_html=True)
            if not S["open"]:
                st.warning("Market is closed.")
            qty = st.number_input("Quantity", min_value=1, value=100, step=10, key="qty")
            st.caption(f"Approx. value ₹{qty * px:,.2f}  ·  Cash ₹{team['cash']:,.2f}")
            b, s = st.columns(2)
            with b, st.container(key="buybtn"):
                buy = st.button("BUY")
            with s, st.container(key="sellbtn"):
                sell = st.button("SELL")
            if buy:
                ok, msg = trade(tid, "BUY", tk, int(qty))
                (st.success if ok else st.error)(msg)
            if sell:
                ok, msg = trade(tid, "SELL", tk, int(qty))
                (st.success if ok else st.error)(msg)
            if S["cfg"]["show_rank"]:
                with S["lock"]:
                    order = sorted((v for v in S["teams"].values() if v["status"] != "closed"), key=net_worth, reverse=True)
                    st.metric("Your rank", f"#{order.index(team) + 1} of {len(order)}")

    with t_pf:
        invested = sum(team["cost"][t] for t in live())
        value = sum(team["holdings"][t] * S["prices"][t] for t in live())
        pnl = value - invested
        m = st.columns(3)
        m[0].metric("Net worth", f"₹{net_worth(team):,.0f}")
        m[1].metric("Cash", f"₹{team['cash']:,.0f}")
        m[2].metric("Value of stocks", f"₹{value:,.0f}")
        m2 = st.columns(3)
        m2[0].metric("Invested", f"₹{invested:,.0f}")
        m2[1].metric("Total P&L", f"₹{pnl:,.0f}", f"{(pnl / invested * 100) if invested else 0:.2f}%")
        m2[2].metric("Return on starting cash", f"{(net_worth(team) / START_CASH - 1) * 100:.2f}%")
        held = [t for t in live() if team["holdings"][t] > 0]
        if held:
            rows = ""
            for t in held:
                q, avg, p = team["holdings"][t], team["cost"][t] / team["holdings"][t], S["prices"][t]
                rows += (f"<tr><td><b>{t}</b></td><td>{q:,}</td><td>₹{avg:,.2f}</td><td>₹{p:,.2f}</td><td>₹{q * p:,.0f}</td>"
                         f"<td>{chg_html((p / avg - 1) * 100)}</td><td>₹{(p - avg) * q:,.0f}</td></tr>")
            st.markdown("<div class='card'><table class='wl'><tr><th>Stock</th><th>Qty</th><th>Avg cost</th><th>LTP</th>"
                        f"<th>Value</th><th>Returns</th><th>P&L</th></tr>{rows}</table></div>", unsafe_allow_html=True)
        else:
            st.info("You don't hold any stocks yet.")

    with t_ipo:
        st.markdown("#### IPO bidding")
        st.caption("Bid for the number of shares you want and the highest price you'll pay inside the band. If the final issue "
                   "price is at or below your bid, you get your full quantity at the issue price, deducted automatically.")
        shown = False
        for t in IPOS:
            c = S["ipo"][t]
            if c["state"] == "open":
                shown = True
                my = c["bids"].get(tid)
                st.markdown(f"<div class='card'><div class='sub'>{SECTOR[t]}</div>"
                            f"<div style='font-size:20px;font-weight:700;color:#fff'>{t}<span class='badge new'>IPO OPEN</span></div>"
                            f"<div class='sub' style='margin-top:6px'>Price band <b style='color:#fff'>₹{c['low']:,.2f} to ₹{c['high']:,.2f}</b>"
                            f" · Max {c['max_qty']:,} shares per team</div></div>", unsafe_allow_html=True)
                with st.form(f"bid_{t}"):
                    f1, f2 = st.columns(2)
                    bq = f1.number_input("Shares", min_value=1, max_value=int(c["max_qty"]),
                                         value=int(my["qty"]) if my else min(100, int(c["max_qty"])), step=10)
                    bp = f2.number_input("Your bid price (₹)", min_value=float(c["low"]), max_value=float(c["high"]),
                                         value=float(my["price"]) if my else float(c["high"]), step=0.5)
                    if st.form_submit_button("Update bid" if my else "Place bid"):
                        ok, msg = place_bid(tid, t, int(bq), float(bp))
                        (st.success if ok else st.error)(msg)
                if my:
                    st.info(f"Your current bid: {my['qty']:,} shares at ₹{my['price']:,.2f}. Money is deducted only if you are allotted shares.")
                    if st.button("Cancel my bid", key=f"cx_{t}"):
                        ok, msg = cancel_bid(tid, t)
                        (st.success if ok else st.error)(msg)
            elif c["state"] == "listed" and tid in c["results"]:
                shown = True
                st.markdown(f"<div class='loan'><b>{t}</b> · {c['results'][tid]}</div>", unsafe_allow_html=True)
        if not shown:
            st.info("No IPOs are open for bidding right now.")

    with t_ord:
        if team["orders"]:
            rows = "".join(f"<tr><td>{o['time']}</td><td class='{'up' if o['side'] in ('BUY', 'IPO ALLOT') else 'down'}'>{o['side']}</td>"
                           f"<td><b>{o['stock']}</b></td><td>{o['qty']:,}</td><td>₹{o['price']:,.2f}</td></tr>"
                           for o in team["orders"][:100])
            st.markdown("<div class='card'><table class='wl'><tr><th>Time</th><th>Side</th><th>Stock</th><th>Qty</th>"
                        f"<th>Price</th></tr>{rows}</table></div>", unsafe_allow_html=True)
        else:
            st.info("No orders yet.")

    with t_news:
        if not S["news_feed"]:
            st.info("No news yet.")
        for n in S["news_feed"][:30]:
            st.markdown(f"<div class='news'><div class='t'>{n['time']}</div><b style='color:#fff'>{n['head']}</b><br>{n['desc']}</div>",
                        unsafe_allow_html=True)


# ================================================================ ADMIN APP
def admin_app():
    tick()
    topbar(f"<span class='pill warn'>ADMIN · ROUND {S['round_no']}</span>")
    cfg = S["cfg"]
    t_news, t_teams, t_act, t_ipo, t_board, t_set = st.tabs(
        ["News & Market", "Teams", "Activity", "IPOs", "Leaderboard", "Settings"])

    with t_news:
        o1, o2, o3 = st.columns([2, 1, 1])
        S["open"] = o1.toggle("Market open (players can trade only while open)", S["open"])
        o2.markdown(f"**Round {S['round_no']}** (only you see this)")
        if o3.button("Next round"):
            S["round_no"] += 1
            st.rerun()

        st.subheader("Company news")
        co = st.selectbox("Company", CORE + IPOS, key="co_sel")
        if co in IPOS and co not in S["listed"]:
            st.warning(f"{co} is not listed yet, so news will have no effect on it.")
        items = COMPANY_NEWS[co]
        pick = st.radio("Choose one of the 5 news items", range(len(items)), key=f"nr_{co}",
                        format_func=lambda i: f"{items[i][0]}  ({items[i][2]:+d}%)")
        head, desc, pct, extra = items[pick]
        effect = f"{co} {pct:+d}%" + "".join(f", {k} {100 * (v - 1):+.0f}%" for k, v in extra.items())
        st.caption(f"{desc}  \nEffect: {effect}")
        if st.button("Broadcast this news"):
            fire_news(head, {co: 1 + pct / 100, **extra}, desc)
            st.success("Broadcast. The price will react at news speed.")

        st.subheader("Random market news (15 items, small basic moves)")
        r1, r2, r3 = st.columns([1, 1, 1])
        if r1.button("Fire a random news now"):
            fire_random_news()
            st.success("Random news broadcast.")
        cfg["auto_news"] = r2.toggle("Auto-fire random news", cfg["auto_news"])
        cfg["auto_every"] = r3.number_input("Every (seconds)", 15.0, 900.0, float(cfg["auto_every"]), 15.0)

        with st.expander("Reaction speed: news vs participants' trades", expanded=True):
            modes = {"slower": "News reacts SLOWER than participants' trades",
                     "same": "News and trades react at the SAME speed",
                     "faster": "News reacts FASTER than participants' trades"}
            cfg["news_mode"] = st.radio("Who moves the price faster?", list(modes), format_func=modes.get,
                                        index=list(modes).index(cfg["news_mode"]), key="news_mode_radio")
            cfg["trade_delay"] = st.slider("Trade reaction time (seconds)", 1.0, 60.0, float(cfg["trade_delay"]), 1.0)
            cfg["news_gap"] = st.slider("Speed gap (times slower or faster)", 1.5, 10.0, float(cfg["news_gap"]), 0.5)
            st.caption(f"Right now: trades take about {tau_trade():.0f}s to move the price, news about {tau_news():.0f}s.")

        with st.expander("Write custom news"):
            h = st.text_input("Headline")
            d = st.text_area("Story")
            picks = st.multiselect("Affected stocks", live())
            cpct = st.slider("Price change %", -90, 200, 0)
            if st.button("Broadcast custom news") and h and picks:
                fire_news(h, {t: 1 + cpct / 100 for t in picks}, d or h)
                st.success("Broadcast.")

        st.subheader("Live prices")
        st.dataframe(pd.DataFrame([{"Stock": t, "Price": S["prices"][t],
                                    "Change %": round(pct_change(t), 2),
                                    "News still to come %": round((math.exp(S["pend_news"][t]) - 1) * 100, 2),
                                    "Trade impact still to come %": round((math.exp(S["pend_trade"][t]) - 1) * 100, 2)}
                                   for t in live()]), hide_index=True, width="stretch")
        if st.button("Refresh"):
            st.rerun()

    with t_teams:
        n = st.number_input("Create how many teams?", 1, 50, 10)
        if st.button("Generate teams & codes"):
            add_teams(int(n))
            st.rerun()
        df = pd.DataFrame([{"Team": k, "Name / note": v["label"], "Access code": v["code"], "Status": v["status"],
                            "Cash": round(v["cash"]), "Net worth": round(net_worth(v))} for k, v in S["teams"].items()])
        st.dataframe(df, hide_index=True, width="stretch")
        if not df.empty:
            st.download_button("Download codes (CSV)", df.to_csv(index=False), "team_codes.csv")
            st.subheader("Manage a team")
            sel = st.selectbox("Team", list(S["teams"]))
            tm = S["teams"][sel]
            lab = st.text_input("Private name / note (only you can see this)", tm["label"])
            c = st.columns(5)
            if c[0].button("Save note"):
                tm["label"] = lab
                st.rerun()
            if c[1].button("Suspend"):
                tm["status"] = "suspended"
                st.rerun()
            if c[2].button("Reinstate"):
                with S["lock"]:
                    tm["status"] = "active"
                    S["codes"][tm["code"]] = sel
                st.rerun()
            if c[3].button("Close team"):
                with S["lock"]:
                    tm["status"] = "closed"
                    S["codes"].pop(tm["code"], None)
                st.rerun()
            if c[4].button("New code"):
                with S["lock"]:
                    S["codes"].pop(tm["code"], None)
                    tm["code"] = gen_code()
                    if tm["status"] != "closed":
                        S["codes"][tm["code"]] = sel
                st.rerun()
            st.caption("Suspend: team can watch but not trade or borrow. Close: team is locked out and its code stops working "
                       "(Reinstate reverses it). New code: use if a code was shared.")

    with t_act:
        st.caption("Latest trades across all teams, useful for spotting suspicious activity.")
        rows = [{**a, "Name / note": S["teams"][a["team"]]["label"]} for a in S["audit"][:150]]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch") if rows else st.info("No trades yet.")

    with t_ipo:
        st.caption("Open bidding with a price band, watch demand, then fix the issue price. Bids at or above it are allotted "
                   "in full at the issue price and deducted automatically.")
        for t in IPOS:
            c = S["ipo"][t]
            st.markdown(f"**{t}** · {SECTOR[t]} · status: `{c['state']}`")
            if c["state"] == "upcoming":
                a, b, d, e = st.columns(4)
                lo = a.number_input("Band low ₹", 1.0, 100000.0, float(c["low"]), 0.5, key=f"lo{t}")
                hi = b.number_input("Band high ₹", 1.0, 100000.0, float(c["high"]), 0.5, key=f"hi{t}")
                mq = d.number_input("Max shares per team", 1, 1_000_000, int(c["max_qty"]), 100, key=f"mq{t}")
                e.write("")
                if e.button("Open bidding", key=f"op{t}"):
                    if hi < lo:
                        st.error("Band high must be at least band low.")
                    else:
                        open_ipo(t, lo, hi, mq)
                        st.rerun()
            elif c["state"] == "open":
                bids = c["bids"]
                st.write(f"Band ₹{c['low']:,.2f} to ₹{c['high']:,.2f} · {len(bids)} bids · "
                         f"{sum(b['qty'] for b in bids.values()):,} shares bid")
                levels = [round(c["low"] + (c["high"] - c["low"]) * i / 5, 2) for i in range(6)]
                st.dataframe(pd.DataFrame({"Issue price ₹": levels,
                                           "Shares allotted if issue price is this": [sum(b["qty"] for b in bids.values() if b["price"] >= p) for p in levels]}),
                             hide_index=True, width="stretch")
                issue = st.number_input("Final issue price ₹", 1.0, 100000.0, float(c["high"]), 0.5, key=f"is{t}")
                x, y = st.columns(2)
                if x.button("Allot & list", key=f"al{t}"):
                    ok, msg = allot_ipo(t, issue)
                    (st.success if ok else st.error)(msg)
                    st.rerun()
                if y.button("Cancel IPO", key=f"ca{t}"):
                    c.update(state="upcoming", bids={}, results={})
                    st.rerun()
            else:
                st.write(f"Listed at ₹{c['issue']:,.2f} · {sum(1 for r in c['results'].values() if r.startswith('Allotted'))} allotments")
            st.divider()

    with t_board:
        rows = sorted(({"Team": k, "Name / note": v["label"], "Status": v["status"], "Net worth": round(net_worth(v))}
                       for k, v in S["teams"].items()), key=lambda r: -r["Net worth"])
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    with t_set:
        cfg["noise"] = st.slider("Random up/down movement intensity % (0 = off)", 0.0, 2.0, cfg["noise"], 0.1)
        cfg["shocks"] = st.toggle("Occasional random price jumps", cfg["shocks"])
        cfg["float"] = st.number_input("Shares in circulation per stock", 1000, 10_000_000, cfg["float"], step=10000)
        cfg["impact"] = st.slider("Trade price impact strength", 0.0, 5.0, cfg["impact"], 0.1)
        cfg["panic_frac"] = st.slider("Bulk dump = selling this share of own holding", 0.1, 1.0, cfg["panic_frac"], 0.05)
        cfg["panic_min_float"] = st.slider("...and order is at least this share of circulation", 0.0, 0.2, cfg["panic_min_float"], 0.005)
        cfg["panic_drop"] = st.slider("Extra panic drop", 0.0, 0.4, cfg["panic_drop"], 0.01)
        cfg["show_rank"] = st.toggle("Show each team its own rank (no names)", cfg["show_rank"])
        st.divider()
        if st.checkbox("Confirm full reset") and st.button("Reset game (keeps teams and codes)"):
            with S["lock"]:
                S["prices"], S["open_px"] = dict(BASE_PRICES), dict(BASE_PRICES)
                for k in ("pend_news", "pend_trade", "flick"):
                    S[k] = {t: 0.0 for t in BASE_PRICES}
                S["history"], S["news_feed"], S["listed"], S["audit"] = [], [], set(), []
                S["round_no"], S["open"] = 1, True
                S["ipo"], S["drift"] = fresh_ipo(), {t: 0.0 for t in BASE_PRICES}
                for v in S["teams"].values():
                    v.update(cash=START_CASH, orders=[], status="active",
                             holdings={t: 0 for t in BASE_PRICES}, cost={t: 0.0 for t in BASE_PRICES})
                    S["codes"][v["code"]] = next(k for k, x in S["teams"].items() if x is v)
            st.success("Game reset.")


if role == "admin":
    admin_app()
else:
    player_app(tid)
