# ai_plogger_multi.py — 4 Ploggers from 4 Teams with Sound
import numpy as np
from moviepy import VideoClip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import random, math, os, wave

FPS, DURATION = 30, 30
OUTPUT_VIDEO = "plogging_multi_nosound.mp4"
OUTPUT_FINAL = "plogging_ai_multi_sound.mov"

# Team colors
TEAMS = [
    {"name": "Red Rangers", "color": "#ff0000", "shirt": "#ff0000", "shorts": "#660000"},
    {"name": "Green Guardians", "color": "#00ff00", "shirt": "#00ff00", "shorts": "#006600"},
    {"name": "Black Knights", "color": "#ffffff", "shirt": "#ffffff", "shorts": "#666666"},
    {"name": "Yellow Storm", "color": "#ffff00", "shirt": "#ffff00", "shorts": "#666600"},
]

SKY, GRASS, PATH_COLOR = '#87CEEB', '#4CAF50', '#D2B48C'
LITTER_COLORS = ['#FF0000', '#FFA500', '#C0C0C0', '#00BFFF', '#FFFF00']

class MultiPlogger:
    def __init__(self, team, start_x):
        self.team = team
        self.px = start_x
        self.pose = 'running'
        self.timer = 0
        self.stats = {'collected': 0, 'points': 0}
        self.sound_events = []
        self.last_footstep = 0

    def update(self, t, litter_list):
        if self.pose == 'running':
            self.px += 0.08
            if t - self.last_footstep > 0.5:
                self.sound_events.append((t, "footstep.wav"))
                self.last_footstep = t
            for item in litter_list:
                if not item['collected'] and abs(self.px - item['x']) < 0.7:
                    item['spotted_by'] = self.team["name"]
                    self.pose = 'spotting'
                    self.timer = 10
                    self.sound_events.append((t, "spot_ding.wav"))
                    return item
        elif self.pose == 'spotting':
            self.timer -= 1
            self.px += 0.02
            if self.timer <= 0:
                self.pose = 'bending'
                self.timer = 15
        elif self.pose == 'bending':
            self.timer -= 1
            if self.timer <= 0:
                self.pose = 'picking'
                self.timer = 6
        elif self.pose == 'picking':
            self.timer -= 1
            if self.timer <= 0:
                self.pose = 'running'
                self.sound_events.append((t, "pickup.wav"))
                self.sound_events.append((t, "celebration.wav"))
                return 'collect'
        if self.px > 22:
            self.px = -2
        return None

    def path_y(self, x, t, offset=0):
        return 2.5 + 0.5 * np.sin(x * 2 + t * 2 + offset)


class MultiPloggerAnimation:
    def __init__(self):
        self.ploggers = []
        for i, team in enumerate(TEAMS):
            self.ploggers.append(MultiPlogger(team, -2 - i * 4))
        self.litter = []
        for _ in range(25):
            self.litter.append({
                'x': random.uniform(2, 20),
                'y_offset': random.uniform(-0.3, 0.3),
                'type': random.choice(['bottle', 'can', 'wrapper']),
                'color': random.choice(LITTER_COLORS),
                'collected': False,
                'spotted_by': None
            })
        self.global_sounds = []

    def update_all(self, t):
        for plogger in self.ploggers:
            # Give each plogger a path offset so they spread out
            result = plogger.update(t, self.litter)
            if result == 'collect' or (isinstance(result, dict) and result.get('collected')):
                pass
            # Handle actual collection
            if result and isinstance(result, dict):
                for item in self.litter:
                    if item.get('spotted_by') == plogger.team["name"] and not item['collected']:
                        item['collected'] = True
                        item['collected_by'] = plogger.team["name"]
                        plogger.stats['collected'] += 1
                        plogger.stats['points'] += 10
                        plogger.sound_events.append((t, "pickup.wav"))
                        plogger.sound_events.append((t, "celebration.wav"))
                        break
            elif result == 'collect':
                for item in self.litter:
                    if item.get('spotted_by') == plogger.team["name"] and not item['collected']:
                        item['collected'] = True
                        item['collected_by'] = plogger.team["name"]
                        plogger.stats['collected'] += 1
                        plogger.stats['points'] += 10
                        break
            # Collect sound events
            self.global_sounds.extend(plogger.sound_events)
            plogger.sound_events = []

    def path_y_base(self, x, t):
        return 2.5 + 0.5 * np.sin(x * 2 + t * 2)

    def draw(self, t):
        self.update_all(t)
        fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=80, facecolor=SKY)
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Ground
        ax.fill_between([0, 20], 0, 3.5, color=GRASS)
        ax.fill_between([0, 20], 0, 2.8, color='#66BB6A')
        
        # Path
        px_arr = np.linspace(0, 20, 500)
        py_arr = self.path_y_base(px_arr, t)
        ax.fill_between(px_arr, py_arr - 0.6, py_arr + 0.6, color=PATH_COLOR, alpha=0.8)
        
        # Trees
        for tx in [1, 3, 6, 9, 12, 15, 18]:
            ax.add_patch(Rectangle((tx-0.12, 5.5), 0.24, 1.5, color='#654321'))
            ax.add_patch(Circle((tx, 6.5), 0.6, color='#228B22', ec='#1a6b1a', lw=1))
            ax.add_patch(Circle((tx-0.2, 6.2), 0.4, color='#228B22'))
            ax.add_patch(Circle((tx+0.2, 6.2), 0.4, color='#228B22'))
        
        # Sun
        ax.add_patch(Circle((17, 8.5), 0.5, color='#FFE082', alpha=0.9))
        
        # Litter
        for item in self.litter:
            if not item['collected']:
                lx = item['x']
                ly = self.path_y_base(item['x'], t) + 0.5 + item['y_offset']
                if item['type'] == 'bottle':
                    ax.add_patch(Rectangle((lx-0.08, ly), 0.16, 0.35, color=item['color'], ec='white', lw=0.5))
                    ax.add_patch(Circle((lx, ly+0.35), 0.04, color=item['color']))
                elif item['type'] == 'can':
                    ax.add_patch(Rectangle((lx-0.06, ly), 0.12, 0.25, color=item['color'], ec='white', lw=0.5))
                else:
                    ax.add_patch(Rectangle((lx-0.15, ly), 0.3, 0.1, color=item['color'], ec='white', lw=0.5, angle=20))
        
        # Draw each plogger
        for i, plogger in enumerate(self.ploggers):
            offset = i * 0.6 - 0.9  # Spread them across the path width
            py = self.path_y_base(plogger.px, t) + 1.2 + offset * 0.3
            self.draw_plogger(ax, plogger.px, py, plogger.pose, t, plogger.team, offset)
        
        # Scoreboard
        ax.text(0.5, 9.6, 'PLOGGING LEAGUE - ALL 4 TEAMS', fontsize=18, fontweight='bold', color='#004D40',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))
        
        total_collected = sum(p.stats['collected'] for p in self.ploggers)
        total_points = sum(p.stats['points'] for p in self.ploggers)
        ax.text(0.5, 9.0, f"Total Collected: {total_collected} | Total CP: {total_points} | Time: {int(t)}s",
                fontsize=10, color='#333', bbox=dict(boxstyle='round', facecolor='white', alpha=0.75))
        
        # Team scores
        for i, plogger in enumerate(self.ploggers):
            ax.text(1 + i * 5, 0.3, f"{plogger.team['name']}: {plogger.stats['collected']} items",
                    fontsize=8, color='white', fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor=plogger.team['color'], alpha=0.8))
        
        fig.canvas.draw()
        buf = fig.canvas.tostring_argb()
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))[:, :, :3]
        plt.close(fig)
        return img

    def draw_plogger(self, ax, x, y, pose, t, team, offset):
        """Draw a single plogger with team colors."""
        c_shirt = team['shirt']
        c_shorts = team['shorts']
        
        if pose == 'running':
            s = 0.2 * math.sin(t * 15 + offset * 10)
            ax.plot([x, x-0.1], [y, y-0.4+s], color=c_shorts, lw=6, solid_capstyle='round')
            ax.plot([x-0.1, x-0.15+s], [y-0.4+s, y-0.7], color='#333', lw=4, solid_capstyle='round')
            ax.plot([x, x+0.1], [y, y-0.4-s], color=c_shorts, lw=6, solid_capstyle='round')
            ax.plot([x+0.1, x+0.15-s], [y-0.4-s, y-0.7], color='#333', lw=4, solid_capstyle='round')
            ax.plot([x, x], [y-0.1, y+0.15], color=c_shirt, lw=9, solid_capstyle='round')
            ax.add_patch(Circle((x, y+0.28), 0.15, color='#FFCD94', ec='#d4a574', lw=0.5))
            ax.plot(x+0.06, y+0.3, 'o', color='black', markersize=2)
            ax.plot(x+0.11, y+0.3, 'o', color='black', markersize=2)
            # Cap
            ax.add_patch(Rectangle((x-0.12, y+0.35), 0.24, 0.06, color=team['color'], angle=3))
        elif pose == 'spotting':
            ax.plot([x, x-0.08], [y, y-0.4], color=c_shorts, lw=5)
            ax.plot([x-0.08, x-0.1], [y-0.4, y-0.7], color='#333', lw=4)
            ax.plot([x, x+0.08], [y, y-0.4], color=c_shorts, lw=5)
            ax.plot([x+0.08, x+0.1], [y-0.4, y-0.7], color='#333', lw=4)
            ax.plot([x, x], [y-0.1, y+0.15], color=c_shirt, lw=8)
            ax.plot([x, x+0.2], [y+0.05, y+0.2], color='#FFCD94', lw=4)  # Pointing
            ax.add_patch(Circle((x, y+0.28), 0.15, color='#FFCD94', ec='#d4a574', lw=0.5))
            ax.plot(x+0.07, y+0.3, 'o', color='black', markersize=2)
        elif pose in ('bending', 'picking'):
            ax.plot([x, x], [y-0.05, y+0.25], color=c_shirt, lw=8)
            ax.plot([x, x-0.08], [y-0.05, y-0.4], color=c_shorts, lw=5)
            ax.plot([x-0.08, x-0.1], [y-0.4, y-0.65], color='#333', lw=4)
            ax.plot([x, x+0.08], [y-0.05, y-0.4], color=c_shorts, lw=5)
            ax.plot([x+0.08, x+0.1], [y-0.4, y-0.65], color='#333', lw=4)
            ax.plot([x, x+0.14], [y+0.25, y+0.4], color='#FFCD94', lw=4)
            ax.plot([x+0.14, x+0.18], [y+0.4, y+0.48], color='#FFC800', lw=3)
            ax.add_patch(Circle((x+0.06, y+0.38), 0.12, color='#FFCD94', ec='#d4a574', lw=0.5))
            if pose == 'picking':
                ax.add_patch(Circle((x+0.18, y+0.48), 0.14, color='yellow', alpha=0.3))


def make_frame(t):
    return anim.draw(t)


# ==================== MAIN ====================
print("=" * 50)
print("MULTI-PLOGGER ANIMATION")
print("4 ploggers from 4 teams: Park Rangers, Ocean Defenders,")
print("Solar Striders, Green Guardians")
print("=" * 50)

anim = MultiPloggerAnimation()

# Step 1: Render video without sound
print("\nStep 1: Rendering video frames...")
video = VideoClip(make_frame, duration=DURATION)
video.write_videofile(OUTPUT_VIDEO, fps=FPS, codec='libx264', bitrate='2000k', logger=None)
print(f"Video saved: {OUTPUT_VIDEO}")

# Step 2: Build mixed audio from all sound events
print(f"\nStep 2: Mixing audio from {len(anim.global_sounds)} sound events...")

# Read ambient base
with wave.open("ambient.wav", 'r') as af:
    amb_data = np.frombuffer(af.readframes(30 * 44100), dtype=np.int16).astype(np.float64)

# Mix in all sound events
for t, snd_file in anim.global_sounds:
    try:
        with wave.open(snd_file, 'r') as sf:
            snd_data = np.frombuffer(sf.readframes(sf.getnframes()), dtype=np.int16).astype(np.float64)
            start_sample = int(t * 44100)
            end_sample = min(start_sample + len(snd_data), len(amb_data))
            if start_sample < len(amb_data):
                amb_data[start_sample:end_sample] += snd_data[:end_sample-start_sample] * 0.8
    except:
        pass

mixed = np.clip(amb_data, -32767, 32767).astype(np.int16)
with wave.open("mixed_audio_multi.wav", 'w') as mf:
    mf.setnchannels(1)
    mf.setsampwidth(2)
    mf.setframerate(44100)
    mf.writeframes(mixed.tobytes())
print("Mixed audio saved: mixed_audio_multi.wav")

# Step 3: Merge with ffmpeg
print("\nStep 3: Merging video + audio with ffmpeg...")
import subprocess
subprocess.run([
    "ffmpeg", "-y",
    "-i", OUTPUT_VIDEO,
    "-i", "mixed_audio_multi.wav",
    "-c:v", "copy",
    "-c:a", "pcm_s16le",
    "-shortest",
    OUTPUT_FINAL
], check=True)

print(f"\n{'='*50}")
print("DONE! 🎉👥🎵")
print(f"Output: {OUTPUT_FINAL}")
for p in anim.ploggers:
    print(f"  {p.team['name']}: {p.stats['collected']} items, {p.stats['points']} CP")
print(f"{'='*50}")
