# app.py - Plogging League Berlin Edition
import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import math
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import database as db
import uuid

st.set_page_config(page_title="Plogging League Berlin", layout="wide")

# Unique health session ID (persists across reruns)
if "health_session_id" not in st.session_state:
    st.session_state.health_session_id = str(uuid.uuid4())

st.title("🏃‍♂️ Plogging League Berlin")
st.caption("Hex tiles rise as litter piles up · sink as cleaned")


TEAMS = [
    {"name": "Red Rangers", "color": "#ff0000"},
    {"name": "Green Guardians", "color": "#00cc00"},
    {"name": "Black Knights", "color": "#999999"},
    {"name": "Yellow Storm", "color": "#ffdd00"},
]

ZONE_NAMES = [
    "Mitte", "Kreuzberg", "Prenzlauer Berg", "Friedrichshain",
    "Charlottenburg", "Neukölln", "Schöneberg", "Wedding",
    "Tiergarten", "Moabit", "Lichtenberg", "Tempelhof"
]

if "zones" not in st.session_state:
    zones = []
    num_x, num_y = 5, 4
    for iy in range(num_y):
        for ix in range(num_x):
            idx = ix + iy * num_x
            zones.append({
                "id": idx, "name": ZONE_NAMES[idx % 12],
                "x_center": ix * 100 + 50, "y_center": iy * 100 + 50,
                "litter": 0, "max_litter": 50
            })
    st.session_state.zones = zones
    ploggers = []
    for i in range(60):
        z = random.choice(zones)
        ploggers.append({
            "id": i, "team": random.choice(TEAMS),
            "x": z["x_center"] + random.uniform(-40, 40),
            "y": z["y_center"] + random.uniform(-40, 40),
            "motivation": random.uniform(0.4, 0.9),
            "fitness": random.uniform(0.4, 1.0),
            "points": random.randint(0, 200),
            "state": "idle", "target_zone_id": None,
            "collect_timer": 0, "idle_timer": random.randint(0, 50),
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

with st.sidebar:
    # Custom Plogger Logo
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
            <circle cx="60" cy="60" r="58" fill="#1a3a2a" stroke="#00cc66" stroke-width="3"/>
            <circle cx="60" cy="35" r="14" fill="#FFCD94" stroke="#d4a574" stroke-width="1.5"/>
            <circle cx="64" cy="33" r="2" fill="#333"/>
            <circle cx="70" cy="33" r="2" fill="#333"/>
            <path d="M63 38 Q67 42 71 38" stroke="#333" stroke-width="1.5" fill="none"/>
            <rect x="50" y="18" width="20" height="6" rx="2" fill="#0064C8"/>
            <rect x="47" y="22" width="12" height="4" rx="1" fill="#0064C8"/>
            <line x1="60" y1="49" x2="60" y2="70" stroke="#009688" stroke-width="8" stroke-linecap="round"/>
            <line x1="60" y1="55" x2="40" y2="60" stroke="#00cc88" stroke-width="5" stroke-linecap="round"/>
            <line x1="60" y1="55" x2="80" y2="60" stroke="#00cc88" stroke-width="5" stroke-linecap="round"/>
            <line x1="60" y1="70" x2="48" y2="90" stroke="#FF8C00" stroke-width="6" stroke-linecap="round"/>
            <line x1="60" y1="70" x2="72" y2="90" stroke="#FF8C00" stroke-width="6" stroke-linecap="round"/>
            <line x1="48" y1="90" x2="44" y2="105" stroke="#FF6600" stroke-width="5" stroke-linecap="round"/>
            <line x1="72" y1="90" x2="76" y2="105" stroke="#FF6600" stroke-width="5" stroke-linecap="round"/>
            <rect x="40" y="58" width="18" height="14" rx="3" fill="#006400" stroke="#00cc66" stroke-width="1"/>
            <text x="49" y="69" font-size="8" fill="white" text-anchor="middle">R</text>
            <circle cx="85" cy="85" r="6" fill="#ff0000" opacity="0.8"/>
            <circle cx="95" cy="78" r="5" fill="#ffdd00" opacity="0.8"/>
            <circle cx="88" cy="72" r="4" fill="#00cc00" opacity="0.8"/>
            <text x="60" y="118" text-anchor="middle" font-size="8" fill="#00cc66" font-weight="bold">PLOGGING</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)
    st.title("About the Dashboard")
    
    with st.expander("🔊 Audio Instructions / Audio-Anleitung / Maagizo ya Sauti"):
        st.markdown("**English**")
        try:
            with open("instructions_en.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        except:
            st.info("Audio file generating...")
        
        st.markdown("**Deutsch (German)**")
        try:
            with open("instructions_de.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        except:
            st.info("Audio file generating...")
        
        st.markdown("**Kiswahili (Swahili)**")
        try:
            with open("instructions_sw.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        except:
            st.info("Audio file generating...")
        
        st.markdown("**Svenska (Swedish)**")
        try:
            with open("instructions_sv.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        except:
            st.info("Audio file generating...")
        
        st.markdown("**한국어 (Korean)**")
        try:
            with open("instructions_ko.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        except:
            st.info("Audio file generating...")
    
    with st.expander("What is Plogging League Simulator?"):
        st.markdown("""
        The **Plogging League Simulator** is an interactive game-like simulation where teams compete to collect litter while jogging.
        
        **Plogging** = Jogging + picking up litter (from Swedish *plocka upp*).
        
        Teams earn points for collecting litter, and their motivation affects performance. Rain slows down collection, while team boosts amplify efforts.
        """)
    
    with st.expander("How to Use the App"):
        st.markdown("""
        1. **Run Simulation** - Watch ploggers clean Berlin
        2. **Adjust Controls** - Change spawn rate, motivation, speed
        3. **Toggle Rain** - See weather effects
        4. **Trigger Challenge** - Boost all teams
        5. **Pause** - View video, save session, download report
        """)
    
    with st.expander("Berlin Districts"):
        st.markdown("""
        This edition features 12 real Berlin districts:
        Mitte, Kreuzberg, Prenzlauer Berg, Friedrichshain, Charlottenburg, Neukolln, Schoneberg, Wedding, Tiergarten, Moabit, Lichtenberg, Tempelhof.
        """)
    
    st.divider()
    st.header("Controls")
    spawn_rate = st.slider("Litter spawn rate", 1.0, 15.0, 5.0, 0.5)
    motivation = st.slider("Plogger motivation", 20, 100, 70, 5) / 100.0
    team_boost = st.slider("Team boost multiplier", 1.0, 3.0, 1.5, 0.1)
    speed = st.slider("Sim speed", 1, 10, 3)
    rain = st.checkbox("Rain (x0.5 activity)")
    st.session_state.rain = rain
    if st.button("Trigger League Challenge"):
        st.session_state.challenge_active = True
        st.session_state.challenge_timer = 200
        for p in st.session_state.ploggers:
            p["motivation"] = min(1.0, p["motivation"] + 0.25)
    st.header("Live Metrics")
    metric_placeholder = st.empty()
    st.header("Team Leaderboard")
    lb_placeholder = st.empty()

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
                wf = 0.5 if rain else 1.0
                cf = team_boost if challenge else 1.0
                zf = 1.0
                if current_zone:
                    zf = 1 + (1 - (100 * (1 - current_zone["litter"]/50)) / 100) * 2
                prob = p["motivation"] * wf * cf * zf * 0.02 * speed
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

run_sim = st.sidebar.checkbox("Run Simulation", value=True)
if run_sim:
    for _ in range(speed):
        update_simulation(spawn_rate, motivation, team_boost, speed)

active_count = sum(1 for p in st.session_state.ploggers if p["state"] != "idle")
total_litter = sum(z["litter"] for z in st.session_state.zones)
avg_clean = np.mean([100 * (1 - z["litter"]/z["max_litter"]) for z in st.session_state.zones])
metric_placeholder.markdown(f"Active: {active_count} | Litter: {total_litter} | Collected: {st.session_state.total_collected} | CP: {st.session_state.total_cp} | Clean: {avg_clean:.1f}% | Day: {st.session_state.sim_day}")

teams_pts = {t["name"]: 0 for t in TEAMS}
for p in st.session_state.ploggers:
    teams_pts[p["team"]["name"]] += p["points"]
sorted_teams = sorted(teams_pts.items(), key=lambda x: x[1], reverse=True)
lb_placeholder.table(pd.DataFrame(sorted_teams, columns=["Team", "Points"]).set_index("Team"))

st.subheader("Hex Tile City View")
fig, ax = plt.subplots(figsize=(10, 7), facecolor="#0a0e14")
ax.set_facecolor("#0a0e14")
ax.set_xlim(-20, 520)
ax.set_ylim(-20, 420)
ax.set_aspect("equal")
ax.axis("off")
height_scale = 4.0
base_radius = 30
for zone in st.session_state.zones:
    litter = zone["litter"]
    radius = base_radius + litter * height_scale
    radius = max(base_radius * 0.6, min(80, radius))
    cr = 1 - litter / zone["max_litter"]
    face_color = (1.0 - cr, cr * 0.8, cr * 0.4)
    ec = "white" if radius > base_radius + 20 else "#555555"
    lw = 1.5 if radius > base_radius + 20 else 0.8
    hp = RegularPolygon((zone["x_center"], zone["y_center"]), numVertices=6, radius=radius, orientation=0, facecolor=face_color, edgecolor=ec, linewidth=lw, alpha=0.85)
    ax.add_patch(hp)
    if radius > base_radius + 10:
        ax.text(zone["x_center"], zone["y_center"], zone["name"], fontsize=6, ha="center", va="center", color="white", fontweight="bold", alpha=0.9)
    ax.text(zone["x_center"], zone["y_center"] - radius - 6, f"{100*(1-litter/zone['max_litter']):.0f}%", fontsize=5, ha="center", va="center", color="#aaaaaa", alpha=0.7)
for p in st.session_state.ploggers:
    ax.plot(p["x"], p["y"], "o", color=p["team"]["color"], markersize=5, alpha=0.9, markeredgecolor="white", markeredgewidth=0.5)
if st.session_state.litter_items:
    lx = [l[0] for l in st.session_state.litter_items]
    ly = [l[1] for l in st.session_state.litter_items]
    ax.plot(lx, ly, ".", color="#888888", markersize=1, alpha=0.6)
if st.session_state.rain:
    ax.text(250, 390, "RAINING", fontsize=14, ha="center", alpha=0.5, color="#7799cc")
if st.session_state.challenge_active:
    ax.text(250, 10, f"LEAGUE CHALLENGE ({team_boost}x)", fontsize=10, ha="center", color="gold", fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.6))
st.pyplot(fig)

if not run_sim:
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Save This Session")
        if st.button("Save to Global Leaderboard"):
            for team_name, points in sorted_teams:
                db.save_session(team_name=team_name, points=points, collected=st.session_state.total_collected // 4, distance=total_litter * 0.01 / 4, clean_score=avg_clean, day=st.session_state.sim_day, hour=st.session_state.sim_hour)
            st.success("Session saved!")
            st.rerun()
    with col2:
        st.subheader("Global Stats")
        try:
            gs = db.get_global_stats()
            st.metric("Total Litter Collected", f"{gs['total_litter_collected']:,}")
            st.metric("Total CP Earned", f"{gs['total_cp_earned']:,}")
            st.metric("Total Sessions", gs['total_sessions'])
        except:
            st.info("Run a session first!")
    st.subheader("All-Time Leaderboard")
    try:
        lb = db.get_leaderboard()
        if lb:
            lb_data = [{"Rank": f"{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else i+1}", "Team": t['name'], "Points": f"{t['total_points']:,}", "Collected": f"{t['total_collected']:,}", "Games": t['games_played']} for i, t in enumerate(lb)]
            st.dataframe(lb_data, use_container_width=True, hide_index=True)
        else:
            st.info("No sessions saved yet!")
    except:
        st.info("Database will initialize on first save.")
    st.divider()
    st.subheader("AI Plogger in Action")
    st.caption("Watch all 4 teams plogging with sound effects!")
    try:
        with open("plogging_ai_multi_sound.mov", "rb") as f:
            st.video(f.read())
    except:
        st.info("Video available on Streamlit Cloud")
    st.divider()
    st.subheader("Download Your Impact Report")
    if st.button("Generate Impact Report PDF"):
        try:
            from impact_report import generate_report
            import tempfile, os as os_mod
            stats = {"distance": total_litter * 0.01, "collected": st.session_state.total_collected, "points": int(st.session_state.total_cp), "clean_score": avg_clean, "day": st.session_state.sim_day, "hour": st.session_state.sim_hour}
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                fig.savefig(tmp.name, dpi=150, bbox_inches="tight", facecolor="#0a0e14")
                hp = tmp.name
            rp = generate_report(stats, sorted_teams, hp)
            with open(rp, "rb") as f:
                st.download_button("Download PDF Report", f, os_mod.path.basename(rp), "application/pdf")
        except Exception as e:
            st.error(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════
    # HEALTH HUB – Preventive Check-ins
    # ═══════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🩺 Health Hub")
    with st.expander("Preventive Health Check-ins", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Balance", "Flexibility", "Reaction Time"])

        # ----- BALANCE TEST -----
        with tab1:
            st.markdown("**Single-Leg Balance Test**")
            st.write("Stand on one leg. Click Start when ready, Stop when you lose balance.")
            col1, col2 = st.columns(2)
            if "balance_start" not in st.session_state:
                st.session_state.balance_start = None
                st.session_state.balance_end = None
            with col1:
                if st.button("Start Balancing"):
                    st.session_state.balance_start = time.time()
                    st.session_state.balance_end = None
            with col2:
                if st.button("Stop (lost balance)"):
                    if st.session_state.balance_start is not None:
                        st.session_state.balance_end = time.time()
            if st.session_state.balance_start and st.session_state.balance_end:
                balance_sec = st.session_state.balance_end - st.session_state.balance_start
                st.success(f"Balance time: **{balance_sec:.1f} seconds**")
                if balance_sec >= 30:
                    st.balloons()
                    st.write("Excellent! Keep it up.")
                elif balance_sec >= 10:
                    st.write("Average. Try to reach 30+ seconds.")
                else:
                    st.warning("Below average. Consider mentioning this to a doctor.")
                db.save_health_checkin(st.session_state.health_session_id, balance_sec=balance_sec)

        # ----- FLEXIBILITY TEST -----
        with tab2:
            st.markdown("**Sit-and-Reach Flexibility Test**")
            st.write("Sit with legs straight. Reach forward and measure distance (cm).")
            flex_cm = st.number_input("Reach distance (cm)", min_value=-30.0, max_value=40.0, value=0.0, step=0.5)
            if st.button("Save Flexibility Score"):
                st.write(f"Flexibility: **{flex_cm:.1f} cm**")
                if flex_cm >= 10:
                    st.success("Great flexibility!")
                elif flex_cm >= 0:
                    st.info("Average. Stretch regularly.")
                else:
                    st.warning("Below average. Regular stretching helps.")
                db.save_health_checkin(st.session_state.health_session_id, flexibility_cm=flex_cm)

        # ----- REACTION TIME TEST -----
        with tab3:
            st.markdown("**Reaction Time Test**")
            st.write("Click as soon as the button turns green!")
            if "reaction_stage" not in st.session_state:
                st.session_state.reaction_stage = "ready"
                st.session_state.reaction_t0 = None
                st.session_state.reaction_time = None
            if st.session_state.reaction_stage == "ready":
                if st.button("Start Reaction Test"):
                    st.session_state.reaction_stage = "waiting"
                    st.rerun()
            elif st.session_state.reaction_stage == "waiting":
                time.sleep(random.uniform(1.5, 4.0))
                st.session_state.reaction_t0 = time.time()
                st.session_state.reaction_stage = "click_now"
                st.rerun()
            elif st.session_state.reaction_stage == "click_now":
                st.markdown("### CLICK NOW!")
                if st.button("CLICK!"):
                    st.session_state.reaction_time = (time.time() - st.session_state.reaction_t0) * 1000
                    st.session_state.reaction_stage = "done"
                    st.rerun()
            elif st.session_state.reaction_stage == "done":
                reaction_ms = st.session_state.reaction_time
                st.success(f"Reaction time: **{reaction_ms:.0f} ms**")
                if reaction_ms < 250:
                    st.balloons()
                    st.write("Lightning fast!")
                elif reaction_ms < 350:
                    st.write("Good. Keep practicing.")
                else:
                    st.warning("Slower than average. Exercise and sleep can improve this.")
                db.save_health_checkin(st.session_state.health_session_id, reaction_ms=reaction_ms)
                if st.button("Try Again"):
                    st.session_state.reaction_stage = "ready"
                    st.rerun()
    
    # ═══════════════════════════════════════════════════════════
    # MOOD MAPPER – Mental Wellbeing
    # ═══════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🧠 Mood Mapper")
    
    mood_emojis = {"😟 Stressed": 1, "😐 Meh": 2, "🙂 Good": 3, "😄 Great": 4}
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Before Exercise**")
        mood_before_str = st.select_slider("How do you feel before plogging?", options=list(mood_emojis.keys()), key="mood_before")
        mood_before = mood_emojis[mood_before_str]
    with col2:
        st.markdown("**After Exercise**")
        mood_after_str = st.select_slider("How do you feel after plogging?", options=list(mood_emojis.keys()), key="mood_after")
        mood_after = mood_emojis[mood_after_str]
    
    if st.button("💾 Log My Mood"):
        db.save_mood(st.session_state.health_session_id, mood_before, mood_after)
        shift = mood_after - mood_before
        if shift > 0:
            st.success(f"Mood improved by {shift} level(s)! Plogging is working for you! 🌟")
            st.info("🌿 **Suggestion:** Try a mindfulness walk in **Tiergarten** or **Tempelhofer Feld** to keep the positive energy going!")
        elif shift == 0:
            st.info("Mood stayed the same. A change of scenery might help!")
            st.info("🌿 **Suggestion:** Explore a new route in **Kreuzberg** or join a walking group in **Prenzlauer Berg**.")
        else:
            st.warning("Mood dropped slightly. That's okay — movement still helps long-term.")
            st.info("👥 **Suggestion:** You've been plogging solo. Want to connect with a local walking group in **Friedrichshain**? (Opt-in)")
            if st.button("Yes, connect me with a group"):
                st.balloons()
                st.success("Great! Check out: **Berlin Plogging Meetup** — Saturdays at 9 AM in Volkspark Friedrichshain.")
        st.caption("All mood data is anonymous and private.")
    
    # Show mood trends
    moods = db.get_mood_trends(st.session_state.health_session_id)
    if len(moods) >= 2:
        st.markdown("**📊 Your Mood Trend**")
        df_mood = pd.DataFrame(moods)
        df_mood = df_mood.sort_values('timestamp')
        st.line_chart(df_mood.set_index('timestamp')[['mood_before', 'mood_after']], use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888888; padding: 10px;">
        <p>This app was developed by <strong>Gerson Japhet Fumbuka</strong></p>
        <p>PhD Candidate at <strong>INTI International University and Colleges</strong></p>
        <p>Nilai, Malaysia</p>
        <p style="font-size: 0.8rem; margin-top: 10px;">Plogging League Berlin &copy; 2025 &mdash; Sweat for the planet. Run, collect, connect.</p>
        <p style="font-size: 0.75rem; color: #666666;">Contact: <a href="mailto:ephatatalithacumi@gmail.com" style="color: #00cc66;">ephatatalithacumi@gmail.com</a></p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
if run_sim:
    time.sleep(0.2)
    st.rerun()
