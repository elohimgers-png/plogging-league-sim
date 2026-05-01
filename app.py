import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from dataclasses import dataclass, field
from typing import List
import random

# ==================== CONFIGURATION ====================
st.set_page_config(page_title="Plogging League Simulator", layout="wide")
st.title("  Plogging League Simulator")
st.markdown("**A living simulation. Adjust sliders and watch the city transform.**")

# ==================== SIDEBAR WITH ABOUT & INSTRUCTIONS ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/plogging.png", width=80)  # Optional logo
    st.title("📖 About the Dashboard")
    
    with st.expander("🎯 What is Plogging League Simulator?"):
        st.markdown("""
        The **Plogging League Simulator** is an interactive game-like simulation where teams compete to collect litter while jogging.
        
        **Plogging** = Jogging + picking up litter (from Swedish *plocka upp*).
        
        Teams earn points for collecting litter, and their motivation affects performance. Rain slows down collection, while team boosts amplify efforts.
        """)
    
    with st.expander("🎮 How to Use the App"):
        st.markdown("""
        **1. Adjust Controls (Left Panel)**  
        - **Litter spawn rate** – How fast new litter appears on the map  
        - **Logger motivation** – Affects how much litter each plogger collects  
        - **Team boost multiplier** – Temporary power-up for selected team  
        - **Simulation speed** – Slows down or speeds up the simulation  
        - **Rain** – Reduces collection activity by 50%  
        - **Trigger League Challenge** – Starts a competitive event between teams
        
        **2. Monitor Live Metrics**  
        - **Active Ploggers** – Currently active team members  
        - **Total Litter on Map** – Uncollected litter remaining  
        - **Litter Collected Ever** – Total cumulative collections
        
        **3. Explore Map Views**  
        Use the tabs to see litter distribution and team territories.
        """)
    
    with st.expander("🏆 Teams & Scoring"):
        st.markdown("""
        | Team | Color | Special Ability |
        |------|-------|-----------------|
        | 🏞️ Park Rangers | Red | Balanced collectors |
        | 🌊 Ocean Defenders | Teal | Efficient in wet conditions |
        | ☀️ Solar Striders | Yellow | Bonus in clear weather |
        | 🌿 Green Guardians | Green | Boosted by team multiplier |
        
        **Scoring System:**  
        - Each litter collected = 1 point for the team  
        - League challenges give bonus points to winning teams  
        - Higher motivation = faster collection rate
        """)
    
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **Q: Why aren't my ploggers moving?**  
        A: Check simulation speed – set it higher than 0. Also ensure litter exists on the map.
        
        **Q: How do I win?**  
        A: Collect as much litter as possible! Trigger League Challenges to earn bonus points.
        
        **Q: What does rain do?**  
        A: Rain reduces collection efficiency by 50% for all teams.
        
        **Q: Can I reset the simulation?**  
        A: Refresh the page or adjust sliders to change parameters.
        """)
    
    with st.expander("📞 Support & Feedback"):
        st.markdown("""
        **Developer:** Gerson Fumbuka  
        **Contact:** [Your Email / GitHub]  
        **Report issues:** [GitHub Issues](https://github.com/elohimgers-png/plogging-league-sim/issues)
        
        ---
        *Version 1.0 | Last updated: May 2026*
        """)
    
    st.caption("👈 Use the sliders above to control the simulation")
# ==================== DATA CLASSES ====================
TEAMS = [
    {"name": "Park Rangers", "color": "#ff6b6b"},
    {"name": "Ocean Defenders", "color": "#4ecdc4"},
    {"name": "Solar Striders", "color": "#ffe66d"},
    {"name": "Green Guardians", "color": "#a29bfe"},
]

@dataclass
class Zone:
    id: int
    name: str
    x_center: float
    y_center: float
    litter: int = 0
    max_litter: int = 50

    @property
    def clean_score(self):
        return max(0, 100 * (1 - self.litter / self.max_litter))

@dataclass
class Plogger:
    id: int
    team: dict
    x: float
    y: float
    motivation: float
    fitness: float
    points: int = 0
    state: str = "idle" # idle, moving, collecting
    target_zone_id: int = None
    collect_timer: int = 0
    idle_timer: int = 0
    session_items: int = 0

# ==================== SIMULATION STATE ====================
if "zones" not in st.session_state:
    # Create 5x4 grid of zones (matching the HTML prototype)
    num_x, num_y = 5, 4
    zones = []
    zone_id = 0
    zone_names = [
        "Downtown", "Riverside Park", "Old Town", "Harbour District",
        "University Area", "Suburbia North", "Industrial Zone", "Market Square",
        "Botanical Gardens", "Coastal Path", "City Centre", "East Village"
    ]
    for iy in range(num_y):
        for ix in range(num_x):
            zones.append(Zone(
                id=zone_id,
                name=zone_names[zone_id % len(zone_names)],
                x_center=ix * 100 + 50,
                y_center=iy * 100 + 50
            ))
            zone_id += 1
    st.session_state.zones = zones

    # Create ploggers
    ploggers = []
    for i in range(60):
        team = random.choice(TEAMS)
        zone = random.choice(zones)
        ploggers.append(Plogger(
            id=i,
            team=team,
            x=zone.x_center + random.uniform(-40, 40),
            y=zone.y_center + random.uniform(-40, 40),
            motivation=random.uniform(0.4, 0.9),
            fitness=random.uniform(0.4, 1.0),
            points=random.randint(0, 200),
            idle_timer=random.randint(0, 50)
        ))
    st.session_state.ploggers = ploggers
    st.session_state.litter_items = [] # list of (x,y)
    st.session_state.sim_day = 0
    st.session_state.sim_hour = 0
    st.session_state.total_collected = 0
    st.session_state.total_cp = 0
    st.session_state.rain = False
    st.session_state.challenge_active = False
    st.session_state.challenge_timer = 0
    st.session_state.frame = 0
    # Random initial litter
    for _ in range(200):
        z = random.choice(zones)
        x = z.x_center + random.uniform(-45, 45)
        y = z.y_center + random.uniform(-45, 45)
        st.session_state.litter_items.append((x, y))
        z.litter += 1

# ==================== SIDEBAR CONTROLS ====================
with st.sidebar:
    st.header("  Controls")
    spawn_rate = st.slider("Litter spawn rate (per zone/hour)", 1.0, 15.0, 5.0, 0.5)
    motivation = st.slider("Plogger motivation", 20, 100, 70, 5) / 100.0
    team_boost = st.slider("Team boost multiplier", 1.0, 3.0, 1.5, 0.1)
    speed = st.slider("Simulation speed", 1, 10, 3)

    rain = st.checkbox("  Rain (activity ×0.5)")
    st.session_state.rain = rain

    if st.button("  Trigger League Challenge"):
        st.session_state.challenge_active = True
        st.session_state.challenge_timer = 200 # frames
        for p in st.session_state.ploggers:
            p.motivation = min(1.0, p.motivation + 0.25)

    st.header("  Live Metrics")
    metric_placeholder = st.empty()

    st.header("  Team Leaderboard")
    lb_placeholder = st.empty()

# ==================== MAIN DISPLAY ====================
map_placeholder = st.empty()

# ==================== UPDATE FUNCTION ====================
def update_simulation(spawn_rate, motivation, team_boost, speed):
    zones = st.session_state.zones
    ploggers = st.session_state.ploggers
    litter = st.session_state.litter_items
    rain = st.session_state.rain
    challenge = st.session_state.challenge_active
    challenge_timer = st.session_state.challenge_timer

    # Hourly litter spawn
    st.session_state.frame += 1
    if st.session_state.frame % max(1, int(200 / speed)) == 0:
        st.session_state.sim_hour += 1
        if st.session_state.sim_hour >= 24:
            st.session_state.sim_hour = 0
            st.session_state.sim_day += 1
        # Spawn litter
        for _ in range(int(spawn_rate * len(zones))):
            z = random.choice(zones)
            x = z.x_center + random.uniform(-45, 45)
            y = z.y_center + random.uniform(-45, 45)
            litter.append((x, y))
            z.litter = min(z.litter + 1, z.max_litter)

    # Decay challenge
    if challenge and challenge_timer > 0:
        st.session_state.challenge_timer -= speed
        if st.session_state.challenge_timer <= 0:
            st.session_state.challenge_active = False
    elif challenge and challenge_timer <= 0:
        st.session_state.challenge_active = False

    # Update ploggers
    for p in ploggers:
        # Find current zone
        zx = int(p.x // 100)
        zy = int(p.y // 100)
        zone_idx = zy * 5 + zx if 0 <= zx < 5 and 0 <= zy < 4 else None
        current_zone = zones[zone_idx] if zone_idx is not None and zone_idx < len(zones) else None

        if p.state == "idle":
            p.idle_timer -= speed
            if p.idle_timer <= 0:
                # decide to plog
                weather_factor = 0.5 if rain else 1.0
                challenge_factor = team_boost if challenge else 1.0
                zone_factor = 1.0
                if current_zone:
                    zone_factor = 1 + (1 - current_zone.clean_score / 100) * 2
                prob = p.motivation * weather_factor * challenge_factor * zone_factor * 0.02 * speed
                if random.random() < prob:
                    # find litter-heavy zone nearby
                    target = None
                    best_score = -1
                    for z in zones:
                        dist = np.hypot(z.x_center - p.x, z.y_center - p.y) + 1
                        score = z.litter / dist
                        if score > best_score:
                            best_score = score
                            target = z
                    if target:
                        p.state = "moving"
                        p.target_zone_id = target.id
                        p.session_items = 0
                p.idle_timer = random.randint(30, 150)

        elif p.state == "moving":
            if p.target_zone_id is not None:
                target = zones[p.target_zone_id]
                dx = target.x_center - p.x
                dy = target.y_center - p.y
                dist = np.hypot(dx, dy)
                if dist < 5:
                    p.state = "collecting"
                    p.collect_timer = random.randint(10, 30)
                else:
                    step = p.fitness * 2 * speed
                    p.x += (dx / dist) * step
                    p.y += (dy / dist) * step
            else:
                p.state = "idle"

            # Collect nearby litter while moving
            for i in range(len(litter) - 1, -1, -1):
                lx, ly = litter[i]
                if np.hypot(p.x - lx, p.y - ly) < 10:
                    # find zone of litter
                    zx = int(lx // 100)
                    zy = int(ly // 100)
                    zi = zy * 5 + zx
                    if 0 <= zi < len(zones):
                        zones[zi].litter = max(0, zones[zi].litter - 1)
                    del litter[i]
                    p.session_items += 1
                    st.session_state.total_collected += 1
                    p.points += 10 * (team_boost if challenge else 1)
                    st.session_state.total_cp += 10 * (team_boost if challenge else 1)

        elif p.state == "collecting":
            p.collect_timer -= speed
            # Collect nearby litter
            for i in range(len(litter) - 1, -1, -1):
                lx, ly = litter[i]
                if np.hypot(p.x - lx, p.y - ly) < 12:
                    zx = int(lx // 100)
                    zy = int(ly // 100)
                    zi = zy * 5 + zx
                    if 0 <= zi < len(zones):
                        zones[zi].litter = max(0, zones[zi].litter - 1)
                    del litter[i]
                    p.session_items += 1
                    st.session_state.total_collected += 1
                    p.points += 10 * (team_boost if challenge else 1)
                    st.session_state.total_cp += 10 * (team_boost if challenge else 1)

            if p.collect_timer <= 0:
                p.state = "idle"
                p.idle_timer = random.randint(20, 100)
                if p.session_items >= 5:
                    p.motivation = min(1.0, p.motivation + 0.02)
                else:
                    p.motivation = max(0.1, p.motivation - 0.005)
        # Keep inside 0-500,0-400
        p.x = max(0, min(500, p.x))
        p.y = max(0, min(400, p.y))

    # Cap litter list
    while len(litter) > 800:
        del litter[0]

# ==================== RUN LOOP ====================
run_sim = st.sidebar.checkbox("  Run Simulation", value=True)

if run_sim:
    for _ in range(speed):
        update_simulation(spawn_rate, motivation, team_boost, speed)

# ==================== RENDER METRICS ====================
active = sum(1 for p in st.session_state.ploggers if p.state != "idle")
total_litter = sum(z.litter for z in st.session_state.zones)
avg_clean = np.mean([z.clean_score for z in st.session_state.zones])

metric_placeholder.markdown(f"""
- **Active Ploggers:** {active}
- **Total Litter on Map:** {total_litter}
- **Litter Collected Ever:** {st.session_state.total_collected}
- **CP in Circulation:** {st.session_state.total_cp}
- **City Clean Score:** {avg_clean:.1f}%
- **Day:** {st.session_state.sim_day} · Hour: {st.session_state.sim_hour}
""")

# Team leaderboard
teams_pts = {t["name"]: 0 for t in TEAMS}
for p in st.session_state.ploggers:
    teams_pts[p.team["name"]] += p.points
sorted_teams = sorted(teams_pts.items(), key=lambda x: x[1], reverse=True)
lb_df = pd.DataFrame(sorted_teams, columns=["Team", "Points"])
lb_placeholder.table(lb_df.set_index("Team"))

# ==================== MAP VISUALIZATION ====================
# Create a Plotly figure with zones, litter, ploggers
fig = go.Figure()

# Draw zones as rectangles
for z in st.session_state.zones:
    col = z.clean_score / 100
    r, g, b = int(30 + (1 - col) * 180), int(50 + col * 160), int(60 + col * 80)
    fig.add_shape(
        type="rect",
        x0=z.x_center - 45, y0=z.y_center - 45,
        x1=z.x_center + 45, y1=z.y_center + 45,
        line=dict(color=f"rgb({r},{g},{b})", width=1),
        fillcolor=f"rgba({r},{g},{b},0.25)",
    )
    # Show clean score
    fig.add_annotation(
        x=z.x_center, y=z.y_center,
        text=f"{z.clean_score:.0f}%",
        showarrow=False,
        font=dict(size=10, color="white"),
    )

# Litter points
if st.session_state.litter_items:
    litter_x = [l[0] for l in st.session_state.litter_items]
    litter_y = [l[1] for l in st.session_state.litter_items]
    fig.add_trace(go.Scatter(
        x=litter_x, y=litter_y,
        mode="markers",
        marker=dict(size=3, color="lightgray", opacity=0.7),
        name="Litter"
    ))

# Ploggers points (with team color)
for team in TEAMS:
    team_ploggers = [p for p in st.session_state.ploggers if p.team["name"] == team["name"]]
    if team_ploggers:
        xs = [p.x for p in team_ploggers]
        ys = [p.y for p in team_ploggers]
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers",
            marker=dict(size=8, color=team["color"], line=dict(width=1, color="white")),
            name=team["name"]
        ))

fig.update_layout(
    xaxis=dict(range=[0, 500], showgrid=False, zeroline=False, visible=False),
    yaxis=dict(range=[0, 400], showgrid=False, zeroline=False, visible=False),
    plot_bgcolor="rgba(10,14,20,1)",
    paper_bgcolor="rgba(10,14,20,1)",
    margin=dict(l=0, r=0, t=10, b=0),
    height=450,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white"))
)
# Rain overlay text
if rain:
    fig.add_annotation(
        x=250, y=380,
        text="  RAINING",
        showarrow=False,
        font=dict(size=20, color="rgba(100,150,255,0.6)"),
    )
if st.session_state.challenge_active:
    fig.add_annotation(
        x=250, y=30,
        text=f"  LEAGUE CHALLENGE ({team_boost}×)",
        showarrow=False,
        font=dict(size=16, color="gold"),
    )

map_placeholder.plotly_chart(fig, use_container_width=True)

# Auto-rerun to keep animation alive
if run_sim:
    time.sleep(0.2)
    st.rerun()


