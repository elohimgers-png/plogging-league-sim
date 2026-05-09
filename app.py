# app.py - Plogging League Simulator (Cloud-Ready + Database + Multi-Plogger Video + Impact Report)
import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import math
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import database as db

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Plogging League Sim", layout="wide")
python3 << 'EOF'
with open("app.py", "r") as f:
    content = f.read()

# Find the set_page_config line and add responsive CSS after it
old_config = '''st.set_page_config(page_title="Plogging League Sim", layout="wide")
st.title("🏃‍♂️ Plogging League Simulator")
st.caption("Hex tiles rise as litter piles up · sink as cleaned")'''

new_config = '''st.set_page_config(page_title="Plogging League Sim", layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════
# MOBILE-RESPONSIVE CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Mobile: collapse sidebar, full-width content */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
    }
    .main > div {
        padding: 10px !important;
    }
    h1 {
        font-size: 1.5rem !important;
    }
    h2 {
        font-size: 1.2rem !important;
    }
    h3 {
        font-size: 1rem !important;
    }
    .stButton button {
        width: 100% !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    [data-testid="stMetric"] {
        font-size: 0.9rem !important;
    }
}

/* Tablet and up: sidebar visible by default */
@media (min-width: 769px) {
    [data-testid="stSidebar"] {
        display: block !important;
    }
}

/* Touch-friendly buttons on all screens */
.stButton button {
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}
.stButton button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
}

/* Better video player on mobile */
video {
    max-width: 100% !important;
    border-radius: 10px !important;
}

/* Clean table styles */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🏃‍♂️ Plogging League Simulator")
st.caption("Hex tiles rise as litter piles up · sink as cleaned")'''

content = content.replace(old_config, new_config)

# Also add a sidebar toggle hint for mobile
old_sidebar = '''with st.sidebar:
    st.header("🎛️ Controls")'''

new_sidebar = '''with st.sidebar:
    st.header("🎛️ Controls")
    st.caption("Tap ☰ to open/close on mobile")'''

content = content.replace(old_sidebar, new_sidebar)

with open("app.py", "w") as f:
    f.write(content)

print("Mobile-responsive CSS added!")
print("Changes:")
print("  - Sidebar auto-collapses on phones")
print("  - Full-width buttons on mobile")
print("  - Touch-friendly design")
print("  - Responsive font sizes")
print("  - Better video player sizing")
EOF
st.title("🏃‍♂️ Plogging League Simulator")
st.caption("Hex tiles rise as litter piles up · sink as cleaned")

# ═══════════════════════════════════════════════════════════
# TEAM DATA
# ═══════════════════════════════════════════════════════════
TEAMS = [
    {"name": "Red Rangers", "color": "#ff0000"},
    {"name": "Green Guardians", "color": "#00cc00"},
    {"name": "Black Knights", "color": "#999999"},
    {"name": "Yellow Storm", "color": "#ffdd00"},
]

ZONE_NAMES = [
    "Downtown", "Riverside Park", "Old Town", "Harbour District",
    "University Area", "Suburbia North", "Industrial Zone", "Market Square",
    "Botanical Gardens", "Coastal Path", "City Centre", "East Village"
]

# ═══════════════════════════════════════════════════════════
# SIMULATION STATE
# ═══════════════════════════════════════════════════════════
if "zones" not in st.session_state:
    zones = []
    num_x, num_y = 5, 4
    for iy in range(num_y):
        for ix in range(num_x):
            idx = ix + iy * num_x
            zones.append({
                "id": idx,
                "name": ZONE_NAMES[idx % len(ZONE_NAMES)],
                "x_center": ix * 100 + 50,
                "y_center": iy * 100 + 50,
                "litter": 0,
                "max_litter": 50
            })
    st.session_state.zones = zones

    ploggers = []
    for i in range(60):
        z = random.choice(zones)
        ploggers.append({
            "id": i,
            "team": random.choice(TEAMS),
            "x": z["x_center"] + random.uniform(-40, 40),
            "y": z["y_center"] + random.uniform(-40, 40),
            "motivation": random.uniform(0.4, 0.9),
            "fitness": random.uniform(0.4, 1.0),
            "points": random.randint(0, 200),
            "state": "idle",
            "target_zone_id": None,
            "collect_timer": 0,
            "idle_timer": random.randint(0, 50),
            "session_items": 0
        })
    st.session_state.ploggers = ploggers

    st.session_state.litter_items = []
    st.session_state.sim_day = 0
    st.session_state.sim_hour = 0
    st.session_state.total_collected = 0
    st.session_state.total_cp = 0
    st.session_state.rain = False
    st.session_state.challenge_active = False
    st.session_state.challenge_timer = 0
    st.session_state.frame = 0

    for _ in range(200):
        z = random.choice(zones)
        x = z["x_center"] + random.uniform(-45, 45)
        y = z["y_center"] + random.uniform(-45, 45)
        st.session_state.litter_items.append((x, y))
        z["litter"] += 1

# ═══════════════════════════════════════════════════════════
# SIDEBAR CONTROLS
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.header("🎛️ Controls")
    spawn_rate = st.slider("Litter spawn rate", 1.0, 15.0, 5.0, 0.5)
    motivation = st.slider("Plogger motivation", 20, 100, 70, 5) / 100.0
    team_boost = st.slider("Team boost multiplier", 1.0, 3.0, 1.5, 0.1)
    speed = st.slider("Sim speed", 1, 10, 3)

    rain = st.checkbox("🌧️ Rain (×0.5 activity)")
    st.session_state.rain = rain

    if st.button("🏆 Trigger League Challenge"):
        st.session_state.challenge_active = True
        st.session_state.challenge_timer = 200
        for p in st.session_state.ploggers:
            p["motivation"] = min(1.0, p["motivation"] + 0.25)

    st.header("📊 Live Metrics")
    metric_placeholder = st.empty()

    st.header("🏅 Team Leaderboard")
    lb_placeholder = st.empty()

# ═══════════════════════════════════════════════════════════
# UPDATE SIMULATION
# ═══════════════════════════════════════════════════════════
def update_simulation(spawn_rate, motivation, team_boost, speed):
    zones = st.session_state.zones
    ploggers = st.session_state.ploggers
    litter = st.session_state.litter_items
    rain = st.session_state.rain
    challenge = st.session_state.challenge_active

    st.session_state.frame += 1
    if st.session_state.frame % max(1, int(200 / speed)) == 0:
        st.session_state.sim_hour += 1
        if st.session_state.sim_hour >= 24:
            st.session_state.sim_hour = 0
            st.session_state.sim_day += 1
        for z in zones:
            for _ in range(int(spawn_rate)):
                x = z["x_center"] + random.uniform(-45, 45)
                y = z["y_center"] + random.uniform(-45, 45)
                litter.append((x, y))
                z["litter"] = min(z["litter"] + 1, z["max_litter"])

    if challenge:
        st.session_state.challenge_timer -= speed
        if st.session_state.challenge_timer <= 0:
            st.session_state.challenge_active = False

    for p in ploggers:
        zx = int(p["x"] // 100)
        zy = int(p["y"] // 100)
        zone_idx = zy * 5 + zx if 0 <= zx < 5 and 0 <= zy < 4 else None
        current_zone = zones[zone_idx] if zone_idx is not None and zone_idx < len(zones) else None

        if p["state"] == "idle":
            p["idle_timer"] -= speed
            if p["idle_timer"] <= 0:
                weather_factor = 0.5 if rain else 1.0
                challenge_factor = team_boost if challenge else 1.0
                zone_factor = 1.0
                if current_zone:
                    zone_factor = 1 + (1 - (100 * (1 - current_zone["litter"]/50)) / 100) * 2
                prob = p["motivation"] * weather_factor * challenge_factor * zone_factor * 0.02 * speed
                if random.random() < prob:
                    target = None
                    best_score = -1
                    for z in zones:
                        dist = np.hypot(z["x_center"] - p["x"], z["y_center"] - p["y"]) + 1
                        score = z["litter"] / dist
                        if score > best_score:
                            best_score = score
                            target = z
                    if target:
                        p["state"] = "moving"
                        p["target_zone_id"] = target["id"]
                        p["session_items"] = 0
                p["idle_timer"] = random.randint(30, 150)

        elif p["state"] == "moving":
            if p["target_zone_id"] is not None:
                target = zones[p["target_zone_id"]]
                dx = target["x_center"] - p["x"]
                dy = target["y_center"] - p["y"]
                dist = np.hypot(dx, dy)
                if dist < 5:
                    p["state"] = "collecting"
                    p["collect_timer"] = random.randint(10, 30)
                else:
                    step = p["fitness"] * 2 * speed
                    p["x"] += (dx / dist) * step
                    p["y"] += (dy / dist) * step
            else:
                p["state"] = "idle"
            for i in range(len(litter) - 1, -1, -1):
                lx, ly = litter[i]
                if np.hypot(p["x"] - lx, p["y"] - ly) < 10:
                    zx = int(lx // 100)
                    zy = int(ly // 100)
                    zi = zy * 5 + zx
                    if 0 <= zi < len(zones):
                        zones[zi]["litter"] = max(0, zones[zi]["litter"] - 1)
                    del litter[i]
                    p["session_items"] += 1
                    st.session_state.total_collected += 1
                    p["points"] += 10 * (team_boost if challenge else 1)
                    st.session_state.total_cp += 10 * (team_boost if challenge else 1)

        elif p["state"] == "collecting":
            p["collect_timer"] -= speed
            for i in range(len(litter) - 1, -1, -1):
                lx, ly = litter[i]
                if np.hypot(p["x"] - lx, p["y"] - ly) < 12:
                    zx = int(lx // 100)
                    zy = int(ly // 100)
                    zi = zy * 5 + zx
                    if 0 <= zi < len(zones):
                        zones[zi]["litter"] = max(0, zones[zi]["litter"] - 1)
                    del litter[i]
                    p["session_items"] += 1
                    st.session_state.total_collected += 1
                    p["points"] += 10 * (team_boost if challenge else 1)
                    st.session_state.total_cp += 10 * (team_boost if challenge else 1)
            if p["collect_timer"] <= 0:
                p["state"] = "idle"
                p["idle_timer"] = random.randint(20, 100)
                if p["session_items"] >= 5:
                    p["motivation"] = min(1.0, p["motivation"] + 0.02)
                else:
                    p["motivation"] = max(0.1, p["motivation"] - 0.005)

        p["x"] = max(0, min(500, p["x"]))
        p["y"] = max(0, min(400, p["y"]))

    while len(litter) > 800:
        del litter[0]

# ═══════════════════════════════════════════════════════════
# RUN SIMULATION
# ═══════════════════════════════════════════════════════════
run_sim = st.sidebar.checkbox("▶️ Run Simulation", value=True)
if run_sim:
    for _ in range(speed):
        update_simulation(spawn_rate, motivation, team_boost, speed)

# ═══════════════════════════════════════════════════════════
# METRICS & LEADERBOARD
# ═══════════════════════════════════════════════════════════
active_count = sum(1 for p in st.session_state.ploggers if p["state"] != "idle")
total_litter = sum(z["litter"] for z in st.session_state.zones)
avg_clean = np.mean([100 * (1 - z["litter"]/z["max_litter"]) for z in st.session_state.zones])
metric_placeholder.markdown(f"""
- **Active Ploggers:** {active_count}
- **Total Litter:** {total_litter}
- **Total Collected:** {st.session_state.total_collected}
- **CP in Circulation:** {st.session_state.total_cp}
- **City Clean Score:** {avg_clean:.1f}%
- **Day:** {st.session_state.sim_day} · Hour: {st.session_state.sim_hour}
""")

teams_pts = {t["name"]: 0 for t in TEAMS}
for p in st.session_state.ploggers:
    teams_pts[p["team"]["name"]] += p["points"]
sorted_teams = sorted(teams_pts.items(), key=lambda x: x[1], reverse=True)
lb_placeholder.table(pd.DataFrame(sorted_teams, columns=["Team", "Points"]).set_index("Team"))

# ═══════════════════════════════════════════════════════════
# 2.5D HEX VIEW
# ═══════════════════════════════════════════════════════════
st.subheader("🗺️ Hex Tile City View")

fig, ax = plt.subplots(figsize=(10, 7), facecolor='#0a0e14')
ax.set_facecolor('#0a0e14')
ax.set_xlim(-20, 520)
ax.set_ylim(-20, 420)
ax.set_aspect('equal')
ax.axis('off')

height_scale = 4.0
base_radius = 30

for zone in st.session_state.zones:
    litter = zone["litter"]
    radius = base_radius + litter * height_scale
    radius = max(base_radius * 0.6, min(80, radius))

    clean_ratio = 1 - litter / zone["max_litter"]
    r = 1.0 - clean_ratio
    g = clean_ratio * 0.8
    b = clean_ratio * 0.4
    face_color = (r, g, b)
    edge_color = 'white' if radius > base_radius + 20 else '#555555'
    line_width = 1.5 if radius > base_radius + 20 else 0.8

    hex_patch = RegularPolygon(
        (zone["x_center"], zone["y_center"]),
        numVertices=6,
        radius=radius,
        orientation=0,
        facecolor=face_color,
        edgecolor=edge_color,
        linewidth=line_width,
        alpha=0.85
    )
    ax.add_patch(hex_patch)

    if radius > base_radius + 10:
        ax.text(zone["x_center"], zone["y_center"],
                zone["name"], fontsize=6, ha='center', va='center',
                color='white', fontweight='bold', alpha=0.9)
    ax.text(zone["x_center"], zone["y_center"] - radius - 6,
            f"{100*(1-litter/zone['max_litter']):.0f}%", fontsize=5,
            ha='center', va='center', color='#aaaaaa', alpha=0.7)

for p in st.session_state.ploggers:
    ax.plot(p["x"], p["y"], 'o', color=p["team"]["color"],
            markersize=5, alpha=0.9, markeredgecolor='white', markeredgewidth=0.5)

if st.session_state.litter_items:
    litter_x = [l[0] for l in st.session_state.litter_items]
    litter_y = [l[1] for l in st.session_state.litter_items]
    ax.plot(litter_x, litter_y, '.', color='#888888', markersize=1, alpha=0.6)

if st.session_state.rain:
    ax.text(250, 390, '🌧️ RAINING', fontsize=14, ha='center', alpha=0.5, color='#7799cc')

if st.session_state.challenge_active:
    ax.text(250, 10, f'🏆 LEAGUE CHALLENGE ACTIVE ({team_boost}×)', fontsize=10,
            ha='center', color='gold', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.6))

ax.text(250, 405, 'PLOGGING LEAGUE SIM', fontsize=7, ha='center', color='#444444', alpha=0.5)

st.pyplot(fig)

# ═══════════════════════════════════════════════════════════
# PAUSE SCREEN: DATABASE + VIDEO + REPORT
# ═══════════════════════════════════════════════════════════
if not run_sim:
    st.divider()
    
    # SAVE SESSION + GLOBAL STATS
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💾 Save This Session")
        if st.button("📊 Save to Global Leaderboard"):
            for team_name, points in sorted_teams:
                db.save_session(
                    team_name=team_name,
                    points=points,
                    collected=st.session_state.total_collected // 4,
                    distance=total_litter * 0.01 / 4,
                    clean_score=avg_clean,
                    day=st.session_state.sim_day,
                    hour=st.session_state.sim_hour
                )
            st.success("Session saved to global leaderboard!")
            st.rerun()
    
    with col2:
        st.subheader("🌍 Global Stats")
        try:
            gs = db.get_global_stats()
            st.metric("Total Litter Collected", f"{gs['total_litter_collected']:,}")
            st.metric("Total CP Earned", f"{gs['total_cp_earned']:,}")
            st.metric("Total Sessions", gs['total_sessions'])
        except:
            st.info("Run a session first!")
    
    # ALL-TIME LEADERBOARD
    st.subheader("🏅 All-Time Leaderboard")
    try:
        lb = db.get_leaderboard()
        if lb:
            lb_data = []
            for i, team in enumerate(lb):
                lb_data.append({
                    "Rank": f"{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else i+1}",
                    "Team": team['name'],
                    "Points": f"{team['total_points']:,}",
                    "Collected": f"{team['total_collected']:,}",
                    "Games": team['games_played']
                })
            st.dataframe(lb_data, use_container_width=True, hide_index=True)
        else:
            st.info("No sessions saved yet. Run the sim and click 'Save Session'!")
    except:
        st.info("Database will initialize on first save.")
    
    st.divider()
    
    # AI PLOGGER VIDEO
    st.subheader("🎬 AI Plogger in Action")
    st.caption("Watch all 4 teams plogging with sound effects!")
    try:
        video_file = open("plogging_ai_multi_sound.mov", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes)
        video_file.close()
    except FileNotFoundError:
        try:
            video_file = open("plogging_ai_video.mp4", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes)
            video_file.close()
        except FileNotFoundError:
            st.info("📹 Video available on Streamlit Cloud")
    
    st.divider()
    
    # DOWNLOAD IMPACT REPORT
    st.subheader("📄 Download Your Impact Report")
    if st.button("📥 Generate Impact Report PDF"):
        try:
            from impact_report import generate_report
            import tempfile, os as os_mod
            stats = {
                "distance": total_litter * 0.01,
                "collected": st.session_state.total_collected,
                "points": int(st.session_state.total_cp),
                "clean_score": avg_clean,
                "day": st.session_state.sim_day,
                "hour": st.session_state.sim_hour
            }
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                fig.savefig(tmp.name, dpi=150, bbox_inches="tight", facecolor="#0a0e14")
                hp = tmp.name
            rp = generate_report(stats, sorted_teams, hp)
            with open(rp, "rb") as f:
                st.download_button("💾 Download PDF Report", f, os_mod.path.basename(rp), "application/pdf")
        except Exception as e:
            st.error(f"Could not generate report: {e}")

# ═══════════════════════════════════════════════════════════
# AUTO-REFRESH
# ═══════════════════════════════════════════════════════════
if run_sim:
    time.sleep(0.2)
    st.rerun()