# ai_plogger_video.py — Plogging AI Video Generator
import cv2
import numpy as np
import random
import math

VIDEO_WIDTH, VIDEO_HEIGHT, FPS, DURATION = 1280, 720, 30, 30
OUTPUT_FILE = "plogging_ai_video.mp4"

SKY_TOP = (135, 206, 235)
SKY_BOTTOM = (255, 255, 255)
GRASS_COLOR = (76, 175, 80)
PATH_COLOR = (210, 180, 140)
TREE_COLOR = (34, 139, 34)
LITTER_COLORS = [(255,0,0), (255,165,0), (192,192,192), (0,191,255), (255,255,0)]
SKIN_COLOR = (255, 205, 148)
SHIRT_COLOR = (0, 150, 136)
SHORTS_COLOR = (40, 40, 40)
SHOE_COLOR = (50, 50, 50)
HAIR_COLOR = (60, 40, 20)
GLOVE_COLOR = (255, 200, 0)
BAG_COLOR = (0, 100, 0)

def draw_gradient_sky(frame, progress):
    for y in range(VIDEO_HEIGHT // 2 + 50):
        ratio = y / (VIDEO_HEIGHT // 2 + 50)
        color = tuple(int(c1 + (c2 - c1) * ratio) for c1, c2 in zip(SKY_TOP, SKY_BOTTOM))
        cv2.line(frame, (0, y), (VIDEO_WIDTH, y), color)
    sun_x, sun_y = int(VIDEO_WIDTH * 0.75), int(VIDEO_HEIGHT * 0.25)
    cv2.circle(frame, (sun_x, sun_y), 50, (255, 255, 200), -1)

def draw_trees(frame):
    positions = [(100,380),(250,360),(450,390),(650,370),(850,400),(1050,380),(1200,360)]
    for tx, ty in positions:
        cv2.rectangle(frame, (tx-8, ty), (tx+8, ty+80), (101, 67, 33), -1)
        for dx, dy, r in [(0,-20,35),(-20,0,30),(20,0,30),(0,10,25)]:
            cv2.circle(frame, (tx+dx, ty+dy), r, TREE_COLOR, -1)

def draw_ground(frame, progress):
    cv2.rectangle(frame, (0, VIDEO_HEIGHT//2+20), (VIDEO_WIDTH, VIDEO_HEIGHT), GRASS_COLOR, -1)
    path_points = [(x, VIDEO_HEIGHT//2 + 60 + int(40 * math.sin(x/300 + progress*2))) for x in range(0, VIDEO_WIDTH, 20)]
    pts = np.array(path_points, np.int32)
    cv2.polylines(frame, [pts], False, PATH_COLOR, 80)

def draw_litter(frame, items):
    for item in items:
        if not item['collected']:
            lx, ly, c = item['x'], item['y'], item['color']
            if item['type'] == 'bottle':
                cv2.ellipse(frame, (lx, ly), (8, 14), 0, 0, 360, c, -1)
                cv2.ellipse(frame, (lx, ly-8), (5, 4), 0, 0, 360, (255,255,255), -1)
            elif item['type'] == 'can':
                cv2.rectangle(frame, (lx-6, ly-10), (lx+6, ly+10), c, -1)
                cv2.ellipse(frame, (lx, ly-10), (6, 3), 0, 0, 180, (255,255,255), -1)
            else:
                cv2.ellipse(frame, (lx, ly), (10, 5), 15, 0, 360, c, -1)

def draw_plogger(frame, x, y, pose, progress, right=True):
    flip = 1 if right else -1
    shadow_y = VIDEO_HEIGHT//2 + 55 + int(40 * math.sin(x/300))
    cv2.ellipse(frame, (int(x), shadow_y+78), (25, 8), 0, 0, 360, (0,0,0,50), -1)
    head_y, body_top, body_bot, knee_y, foot_y = y, y+20, y+50, y+75, y+100

    if pose == 'running':
        l_swing = 15 * math.sin(progress * 8)
        r_swing = -15 * math.sin(progress * 8)
        cv2.line(frame, (int(x), int(body_bot)), (int(x-8*flip), int(knee_y)), SHORTS_COLOR, 8)
        cv2.line(frame, (int(x-8*flip), int(knee_y)), (int(x-12*flip+l_swing), int(foot_y)), SHOE_COLOR, 7)
        cv2.line(frame, (int(x), int(body_bot)), (int(x+8*flip), int(knee_y)), SHORTS_COLOR, 8)
        cv2.line(frame, (int(x+8*flip), int(knee_y)), (int(x+12*flip+r_swing), int(foot_y)), SHOE_COLOR, 7)
        a_f = 20 * math.sin(progress*8 + math.pi)
        a_b = 20 * math.sin(progress*8)
        cv2.line(frame, (int(x), int(body_top)), (int(x-15*flip+a_f), int(body_top+5)), SHIRT_COLOR, 7)
        cv2.line(frame, (int(x), int(body_top)), (int(x+15*flip+a_b), int(body_top+5)), SHIRT_COLOR, 7)
        cv2.line(frame, (int(x), int(body_top)), (int(x), int(body_bot)), SHIRT_COLOR, 14)
        bag_x = int(x - 5*flip)
        cv2.rectangle(frame, (bag_x-12, int(body_top+5)), (bag_x+12, int(body_bot-5)), BAG_COLOR, -1)
        cv2.putText(frame, "R", (bag_x-8, int(body_top+18)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    elif pose == 'spotting':
        cv2.line(frame, (int(x), int(body_bot)), (int(x-5*flip), int(knee_y)), SHORTS_COLOR, 8)
        cv2.line(frame, (int(x-5*flip), int(knee_y)), (int(x-8*flip), int(foot_y)), SHOE_COLOR, 7)
        cv2.line(frame, (int(x), int(body_bot)), (int(x+5*flip), int(knee_y)), SHORTS_COLOR, 8)
        cv2.line(frame, (int(x+5*flip), int(knee_y)), (int(x+8*flip), int(foot_y)), SHOE_COLOR, 7)
        cv2.line(frame, (int(x), int(body_top)), (int(x), int(body_bot)), SHIRT_COLOR, 14)
        cv2.line(frame, (int(x), int(body_top)), (int(x+25*flip), int(body_top-15)), SKIN_COLOR, 7)
        cv2.line(frame, (int(x), int(body_top)), (int(x-15*flip), int(body_top+10)), SHIRT_COLOR, 7)
    elif pose in ('bending', 'picking'):
        bo = 20
        cv2.line(frame, (int(x), int(body_top-bo)), (int(x), int(body_bot+bo)), SHIRT_COLOR, 14)
        cv2.line(frame, (int(x), int(body_bot+bo)), (int(x-10*flip), int(knee_y+15)), SHORTS_COLOR, 8)
        cv2.line(frame, (int(x-10*flip), int(knee_y+15)), (int(x-15*flip), int(foot_y+10)), SHOE_COLOR, 7)
        cv2.line(frame, (int(x), int(body_bot+bo)), (int(x+10*flip), int(knee_y+15)), SHORTS_COLOR, 8)
        cv2.line(frame, (int(x+10*flip), int(knee_y+15)), (int(x+15*flip), int(foot_y+10)), SHOE_COLOR, 7)
        cv2.line(frame, (int(x), int(body_top-bo)), (int(x+15*flip), int(body_bot+bo+10)), SKIN_COLOR, 7)
        cv2.line(frame, (int(x+15*flip), int(body_bot+bo+10)), (int(x+20*flip), int(body_bot+bo+25)), GLOVE_COLOR, 5)
        if pose == 'picking':
            cv2.circle(frame, (int(x+20*flip), int(body_bot+bo+25)), 15, (255,255,0,100), -1)

    if pose in ('bending', 'picking'):
        hx, hy = int(x+5*flip), int(head_y-15)
    else:
        hx, hy = int(x), int(head_y)
    cv2.circle(frame, (hx, hy), 15, SKIN_COLOR, -1)
    cv2.circle(frame, (hx, hy), 16, SKIN_COLOR, 2)
    ex = hx + 5*flip
    cv2.circle(frame, (ex, hy-3), 2, (0,0,0), -1)
    cv2.circle(frame, (ex+3*flip, hy-3), 2, (0,0,0), -1)
    cv2.ellipse(frame, (hx+5*flip, hy+5), (5,3), 0, 0, 180, (0,0,0), 1)
    cv2.ellipse(frame, (hx, hy-10), (14,8), 0, 180, 360, HAIR_COLOR, -1)
    if pose in ('running', 'spotting'):
        cv2.rectangle(frame, (hx-12, hy-18), (hx+12, hy-14), (0,100,200), -1)
        cv2.rectangle(frame, (hx-14, hy-14), (hx+8, hy-11), (0,100,200), -1)

def draw_ui(frame, stats, elapsed):
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 160), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    cv2.putText(frame, "Plogging League", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0,255,100), 1)
    cv2.putText(frame, f"Distance: {stats['distance']:.2f} km", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
    cv2.putText(frame, f"Collected: {stats['collected']}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
    cv2.putText(frame, f"Points: {stats['points']} CP", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,215,0), 1)
    cv2.putText(frame, f"Time: {int(elapsed)}s", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

def generate_video():
    print("Generating Plogging AI Video...")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (VIDEO_WIDTH, VIDEO_HEIGHT))
    total_frames = FPS * DURATION
    px, pose, timer = -100, 'running', 0
    stats = {'distance': 0, 'collected': 0, 'points': 0}
    litter = [{'x': random.randint(200, VIDEO_WIDTH-200),
               'y': VIDEO_HEIGHT//2 + 50 + int(40*math.sin(random.randint(200, VIDEO_WIDTH-200)/300)),
               'type': random.choice(['bottle','can','wrapper']),
               'color': random.choice(LITTER_COLORS),
               'collected': False, 'spotted': False} for _ in range(20)]

    for fn in range(total_frames):
        progress = fn / total_frames
        elapsed = fn / FPS
        frame = np.zeros((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)
        draw_gradient_sky(frame, progress)
        draw_trees(frame)
        draw_ground(frame, progress)

        py = VIDEO_HEIGHT//2 + 55 + int(40 * math.sin(px/300))
        if pose == 'running':
            px += 4
            stats['distance'] += 0.004
            for item in litter:
                if not item['collected'] and abs(px - item['x']) < 60:
                    item['spotted'] = True
                    pose, timer = 'spotting', 15
                    break
        elif pose == 'spotting':
            timer -= 1; px += 2
            if timer <= 0:
                pose, timer = 'bending', 20
        elif pose == 'bending':
            timer -= 1
            if timer <= 0:
                pose, timer = 'picking', 10
        elif pose == 'picking':
            timer -= 1
            if timer <= 0:
                for item in litter:
                    if item['spotted'] and not item['collected'] and abs(px - item['x']) < 80:
                        item['collected'] = True; item['spotted'] = False
                        stats['collected'] += 1; stats['points'] += 10
                        break
                pose, timer = 'running', 0
        if px > VIDEO_WIDTH + 100:
            px = -100

        draw_litter(frame, litter)
        draw_plogger(frame, px, py, pose, progress, True)
        draw_ui(frame, stats, elapsed)
        out.write(frame)
        if fn % 30 == 0:
            print(f"  {int(progress*100)}%...")

    out.release()
    print(f"Video saved: {OUTPUT_FILE}")
    print(f"Stats: {stats['collected']} items, {stats['points']} CP, {stats['distance']:.2f} km")
    return OUTPUT_FILE

if __name__ == "__main__":
    generate_video()
