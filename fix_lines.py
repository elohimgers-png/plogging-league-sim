with open("ai_plogger_video_moviepy.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'img = img.reshape' in line:
        # Replace that entire line with the correct one
        lines[i] = '        img = img.reshape((h, w, 4))[:, :, :3]\n'
    if "fig.canvas.tostring_rgb()" in line and "np.frombuffer" in line:
        lines[i] = '        buf = fig.canvas.tostring_rgb()\n'
        lines.insert(i+1, '        w, h = fig.canvas.get_width_height()\n')

with open("ai_plogger_video_moviepy.py", "w") as f:
    f.writelines(lines)

print("Fixed! Running now...")
