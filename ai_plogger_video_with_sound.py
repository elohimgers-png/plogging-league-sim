# ai_plogger_video_with_sound.py
import numpy as np
from moviepy import VideoClip, AudioFileClip, CompositeAudioClip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import random, math, os

FPS, DURATION = 30, 30
OUTPUT = "plogging_ai_video_sound.mp4"
SKY, GRASS, PATH_COLOR = '#87CEEB', '#4CAF50', '#D2B48C'
SKIN, SHIRT, SHORTS, SHOE, BAG, GLOVE = '#FFCD94', '#009688', '#282828', '#323232', '#006400', '#FFC800'
LITTER_COLORS = ['#FF0000', '#FFA500', '#C0C0C0', '#00BFFF', '#FFFF00']

footstep = AudioFileClip("footstep.wav") if os.path.exists("footstep.wav") else None
spot_ding = AudioFileClip("spot_ding.wav") if os.path.exists("spot_ding.wav") else None
pickup_snd = AudioFileClip("pickup.wav") if os.path.exists("pickup.wav") else None
celebration = AudioFileClip("celebration.wav") if os.path.exists("celebration.wav") else None
ambient = AudioFileClip("ambient.wav") if os.path.exists("ambient.wav") else None

class PloggerAnimation:
    def __init__(self):
        self.px, self.pose, self.timer = -2, 'running', 0
        self.stats = {'distance': 0, 'collected': 0, 'points': 0}
        self.litter = [{'x': random.uniform(2,18), 'y_offset': random.uniform(-0.3,0.3),
                        'type': random.choice(['bottle','can','wrapper']),
                        'color': random.choice(LITTER_COLORS), 'collected': False, 'spotted': False} for _ in range(15)]
        self.sound_events = []
        self.last_footstep_time = 0

    def add_sound(self, t, snd):
        if snd is not None:
            self.sound_events.append((t, snd))

    def update(self, t):
        if self.pose == 'running':
            self.px += 0.1; self.stats['distance'] += 0.003
            if t - self.last_footstep_time > 0.4:
                self.add_sound(t, footstep); self.last_footstep_time = t
            for i in self.litter:
                if not i['collected'] and abs(self.px - i['x']) < 1.0:
                    i['spotted'] = True; self.pose = 'spotting'; self.timer = 12
                    self.add_sound(t, spot_ding); break
        elif self.pose == 'spotting':
            self.timer -= 1; self.px += 0.03
            if self.timer <= 0: self.pose = 'bending'; self.timer = 18
        elif self.pose == 'bending':
            self.timer -= 1
            if self.timer <= 0: self.pose = 'picking'; self.timer = 8
        elif self.pose == 'picking':
            self.timer -= 1
            if self.timer <= 0:
                for i in self.litter:
                    if i['spotted'] and not i['collected'] and abs(self.px - i['x']) < 1.5:
                        i['collected'] = True; i['spotted'] = False
                        self.stats['collected'] += 1; self.stats['points'] += 10
                        self.add_sound(t, pickup_snd); self.add_sound(t, celebration)
                        break
                self.pose = 'running'
        if self.px > 20: self.px = -2

    def path_y(self, x, t): return 2.5 + 0.5 * np.sin(x * 2 + t * 2)

    def draw(self, t):
        self.update(t)
        fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=80, facecolor=SKY)
        ax.set_xlim(0, 20); ax.set_ylim(0, 10); ax.axis('off')
        ax.fill_between([0,20], 0, 3.5, color=GRASS)
        ax.fill_between([0,20], 0, 2.8, color='#66BB6A')
        px_arr = np.linspace(0, 20, 500)
        py_arr = self.path_y(px_arr, t)
        ax.fill_between(px_arr, py_arr - 0.6, py_arr + 0.6, color=PATH_COLOR, alpha=0.8)
        for tx in [2,5,8,12,16]:
            ax.add_patch(Rectangle((tx-0.15, 5.5), 0.3, 1.8, color='#654321'))
            ax.add_patch(Circle((tx, 6.8), 0.7, color='#228B22', ec='#1a6b1a', lw=1))
        ax.add_patch(Circle((16, 8.5), 0.6, color='#FFE082', alpha=0.9))
        for item in self.litter:
            if not item['collected']:
                lx, ly = item['x'], self.path_y(item['x'], t) + 0.5 + item['y_offset']
                if item['type'] == 'bottle':
                    ax.add_patch(Rectangle((lx-0.1, ly), 0.2, 0.4, color=item['color'], ec='white', lw=0.5))
                    ax.add_patch(Circle((lx, ly+0.4), 0.05, color=item['color']))
                elif item['type'] == 'can':
                    ax.add_patch(Rectangle((lx-0.08, ly), 0.16, 0.3, color=item['color'], ec='white', lw=0.5))
                else:
                    ax.add_patch(Rectangle((lx-0.18, ly), 0.36, 0.12, color=item['color'], ec='white', lw=0.5, angle=20))
        py = self.path_y(self.px, t) + 1.2
        self.draw_plogger(ax, self.px, py, self.pose, t)
        ax.text(0.5, 9.5, 'PLOGGING LEAGUE', fontsize=20, fontweight='bold', color='#004D40',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))
        ax.text(0.5, 8.8, f"Dist: {self.stats['distance']:.2f} km | Collected: {self.stats['collected']} | CP: {self.stats['points']} | Time: {int(t)}s",
                fontsize=11, color='#333', bbox=dict(boxstyle='round', facecolor='white', alpha=0.75))
        fig.canvas.draw()
        buf = fig.canvas.tostring_argb()
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))[:, :, :3]
        plt.close(fig)
        return img

    def draw_plogger(self, ax, x, y, pose, t):
        if pose == 'running':
            s = 0.25 * math.sin(t*18)
            ax.plot([x,x-0.12],[y,y-0.5+s],color=SHORTS,lw=6,solid_capstyle='round')
            ax.plot([x-0.12,x-0.18+s],[y-0.5+s,y-0.85],color=SHOE,lw=5,solid_capstyle='round')
            ax.plot([x,x+0.12],[y,y-0.5-s],color=SHORTS,lw=6,solid_capstyle='round')
            ax.plot([x+0.12,x+0.18-s],[y-0.5-s,y-0.85],color=SHOE,lw=5,solid_capstyle='round')
            ax.plot([x,x],[y-0.15,y+0.2],color=SHIRT,lw=10,solid_capstyle='round')
            ax.add_patch(Circle((x,y+0.35),0.2,color=SKIN,ec='#d4a574',lw=1))
            ax.plot(x+0.08,y+0.38,'o',color='black',markersize=3)
            ax.plot(x+0.15,y+0.38,'o',color='black',markersize=3)
            ax.add_patch(Rectangle((x-0.15,y+0.45),0.3,0.08,color='#0064C8',angle=3))
        elif pose == 'spotting':
            ax.plot([x,x-0.1],[y,y-0.5],color=SHORTS,lw=6)
            ax.plot([x-0.1,x-0.13],[y-0.5,y-0.85],color=SHOE,lw=5)
            ax.plot([x,x+0.1],[y,y-0.5],color=SHORTS,lw=6)
            ax.plot([x+0.1,x+0.13],[y-0.5,y-0.85],color=SHOE,lw=5)
            ax.plot([x,x],[y-0.15,y+0.2],color=SHIRT,lw=10)
            ax.plot([x,x+0.25],[y+0.1,y+0.28],color=SKIN,lw=5)
            ax.add_patch(Circle((x,y+0.35),0.2,color=SKIN,ec='#d4a574',lw=1))
            ax.plot(x+0.1,y+0.38,'o',color='black',markersize=3)
        elif pose in ('bending','picking'):
            ax.plot([x,x],[y-0.1,y+0.3],color=SHIRT,lw=10)
            ax.plot([x,x-0.1],[y-0.1,y-0.5],color=SHORTS,lw=6)
            ax.plot([x-0.1,x-0.13],[y-0.5,y-0.8],color=SHOE,lw=5)
            ax.plot([x,x+0.1],[y-0.1,y-0.5],color=SHORTS,lw=6)
            ax.plot([x+0.1,x+0.13],[y-0.5,y-0.8],color=SHOE,lw=5)
            ax.plot([x,x+0.18],[y+0.3,y+0.5],color=SKIN,lw=5)
            ax.plot([x+0.18,x+0.23],[y+0.5,y+0.58],color=GLOVE,lw=5)
            ax.add_patch(Circle((x+0.08,y+0.45),0.17,color=SKIN,ec='#d4a574',lw=1))
            if pose == 'picking': ax.add_patch(Circle((x+0.23,y+0.58),0.18,color='yellow',alpha=0.35))

def make_frame(t): return anim.draw(t)

anim = PloggerAnimation()
print("Generating video with sound...")
for t in np.arange(0, DURATION, 1/FPS): make_frame(t)
print(f"Found {len(anim.sound_events)} sound events!")

video = VideoClip(make_frame, duration=DURATION)
audio_clips = []
# Only use ambient background (safe — longer than video)
if ambient:
    amb = ambient.with_duration(DURATION)
    audio_clips.append(amb.with_volume_scaled(0.4))
# Skip short SFX for now — MoviePy v2 has timing bugs with them
if audio_clips:
    video = video.with_audio(CompositeAudioClip(audio_clips))
print("Writing video with ambient sound...")
video.write_videofile(OUTPUT, fps=FPS, codec='libx264', bitrate='2000k', logger=None)
print(f"Done: {OUTPUT}")
print(f"Stats: {anim.stats['collected']} items, {anim.stats['points']} CP, {anim.stats['distance']:.2f} km")
