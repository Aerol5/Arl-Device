import tkinter as tk
import subprocess
import os
import random
import platform
import sys
import urllib.request

CURRENT_VERSION = "1.1.5"
VERSION_URL = "https://raw.githubusercontent.com/Aerol5/Arl-Device/refs/heads/main/version.txt"
UPDATE_URL = "https://raw.githubusercontent.com/Aerol5/Arl-Device/refs/heads/main/main.py"

app = tk.Tk()
app.title("ARL")
app.geometry("500x720")
app.configure(bg="#000000")

# --- AUTO UPDATE ENGINE ---
def check_for_updates():
    lbl_status.config(text="Checking for updates...", fg="#38bdf8")
    app.update()
    try:
        req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            latest_version = response.read().decode('utf-8').strip()
            
        if latest_version != CURRENT_VERSION:
            lbl_status.config(text=f"Updating to v{latest_version}...", fg="#fef08a")
            app.update()
            
            current_script = os.path.abspath(sys.argv[0])
            backup_script = current_script + ".bak"
            
            if os.path.exists(backup_script):
                os.remove(backup_script)
            os.rename(current_script, backup_script)
            
            req_update = urllib.request.Request(UPDATE_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_update, timeout=10) as response_file:
                with open(current_script, "wb") as f:
                    f.write(response_file.read())
            
            lbl_status.config(text="Update complete! Restarting...", fg="#22c55e")
            app.update()
            app.after(2000, lambda: os.execv(sys.executable, ['python'] + sys.argv))
            return True
    except:
        pass
    return False

def check_and_install_dependencies():
    if check_for_updates():
        return
    lbl_status.config(text=f"System Ready v{CURRENT_VERSION} ✅", fg="#22c55e")

# --- UI DESIGN ELEMENTS ---
sky = tk.Canvas(app, width=500, height=120, bg="#000000", highlightthickness=0)
sky.pack(pady=(10, 0))
sky.create_oval(380, 20, 440, 80, fill="#fef08a", outline="") 
sky.create_oval(365, 15, 425, 75, fill="#000000", outline="") 

stars = []
for _ in range(15):
    x = random.randint(20, 480)
    y = random.randint(10, 100)
    if not (350 < x < 450 and 10 < y < 90):
        star = sky.create_oval(x, y, x+3, y+3, fill="#ffffff", outline="")
        stars.append(star)

def twinkle_stars():
    for star in stars:
        color = random.choice(["#ffffff", "#94a3b8", "#cbd5e1", "#e2e8f0", "#1e293b"])
        sky.itemconfig(star, fill=color)
    app.after(500, twinkle_stars) 

lbl_title = tk.Label(app, text="Arl", font=("Arial", 16, "bold"), fg="#ffffff", bg="#000000")
lbl_title.pack(pady=(10, 5))
lbl_status = tk.Label(app, text="Loading...", font=("Arial", 9, "italic"), fg="#94a3b8", bg="#000000")
lbl_status.pack(pady=(0, 15))

# --- ADB & SCRCPY MULTI-DEVICE ENGINE ---
def get_devices():
    try:
        cmd = "adb.exe" if platform.system() == "Windows" else "adb"
        output = subprocess.check_output([cmd, "devices"]).decode("utf-8")
        lines = output.strip().split("\n")[1:]
        return [line.split("\t")[0] for line in lines if line.strip() and "device" in line]
    except:
        return []

def launch_scrcpy(serial):
    scrcpy_cmd = "scrcpy.exe" if platform.system() == "Windows" else "scrcpy"
    cmd = f'{scrcpy_cmd} -s "{serial}" --always-on-top &'
    if platform.system() == "Windows":
        cmd = f'start /b {scrcpy_cmd} -s "{serial}" --always-on-top'
    os.system(cmd)

def open_device():
    devices = get_devices()
    if devices:
        launch_scrcpy(devices[0])
    else:
        lbl_status.config(text="No device detected! ❌", fg="#ef4444")

def open_specific_device(index):
    devices = get_devices()
    if len(devices) >= index:
        launch_scrcpy(devices[index - 1])
    else:
        lbl_status.config(text=f"Device {index} is not connected! ❌", fg="#ef4444")

def open_all_devices():
    devices = get_devices()
    if devices:
        for serial in devices:
            launch_scrcpy(serial)
        lbl_status.config(text=f"Opened {len(devices)} device(s) 🚀", fg="#22c55e")
    else:
        lbl_status.config(text="No devices detected to open! ❌", fg="#ef4444")

def shut_down_all():
    if platform.system() == "Windows":
        os.system("taskkill /f /im scrcpy.exe")
    else:
        os.system("pkill scrcpy")
    lbl_status.config(text="All device windows closed 🛑", fg="#ef4444")

# --- 🎮 CUSTOM KEYMAPPER ENGINE ---
def open_game_controller():
    devices = get_devices()
    if not devices:
        lbl_status.config(text="No device detected for Controller! ❌", fg="#ef4444")
        return

    target_device = devices[0]
    adb_cmd = "adb.exe" if platform.system() == "Windows" else "adb"

    game_win = tk.Toplevel(app)
    game_win.title("ARL - Keymapper")
    game_win.geometry("400x350")
    game_win.configure(bg="#111827")
    
    lbl_game = tk.Label(game_win, text="🎮 KEYMAPPER ACTIVE", font=("Arial", 12, "bold"), fg="#22c55e", bg="#111827")
    lbl_game.pack(pady=10)

    lbl_bindings = tk.Label(game_win, text="🕹️ WASD: Move Around\n\n⚔️ KEYBINDINGS:\nL: Skill 1\nK: Skill 2\nJ: Skill 3\nO: Basic Attack ⚔️\n\n💥 UTILITIES:\nQ: Spell | E: Regen | R: Recall", font=("Arial", 10), fg="#94a3b8", bg="#111827", justify="left")
    lbl_bindings.pack(pady=10)

    # Virtual Joystick Setup
    JOY_X, JOY_Y = 270, 630  
    DIST = 120               

    def send_cmd(args):
        subprocess.Popen([adb_cmd, "-s", target_device] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def on_key_press(event):
        key = str(event.keysym).lower()
        
        # MOVEMENT
        if key == 'w':   
            send_cmd(["shell", "input", "swipe", str(JOY_X), str(JOY_Y), str(JOY_X), str(JOY_Y - DIST), "80"])
        elif key == 's': 
            send_cmd(["shell", "input", "swipe", str(JOY_X), str(JOY_Y), str(JOY_X), str(JOY_Y + DIST), "80"])
        elif key == 'a': 
            send_cmd(["shell", "input", "swipe", str(JOY_X), str(JOY_Y), str(JOY_X - DIST), str(JOY_Y), "80"])
        elif key == 'd': 
            send_cmd(["shell", "input", "swipe", str(JOY_X), str(JOY_Y), str(JOY_X + DIST), str(JOY_Y), "80"])
            
        # SKILLS & ATTACK MAPPING (1920x856)
        elif key == 'l':     # Skill 1
            send_cmd(["shell", "input", "tap", "1540", "720"])
        elif key == 'k':     # Skill 2
            send_cmd(["shell", "input", "tap", "1650", "590"])
        elif key == 'j':     # Skill 3
            send_cmd(["shell", "input", "tap", "1790", "440"])
        elif key == 'o':     # Basic Attack (Naka-map sa O)
            send_cmd(["shell", "input", "tap", "1765", "735"])
            
        # UTILITIES
        elif key == 'q':     # Spell
            send_cmd(["shell", "input", "tap", "1360", "790"])
        elif key == 'e':     # Regen
            send_cmd(["shell", "input", "tap", "1220", "790"])
        elif key == 'r':     # Recall
            send_cmd(["shell", "input", "tap", "1090", "790"])

    game_win.bind("<KeyPress>", on_key_press)

# --- APP SYSTEM CONTROLS ---
btn_main = tk.Button(app, text="🚀 Open Game Window (scrcpy)", font=("Arial", 11, "bold"), 
                     bg="#ffffff", fg="#000000", activebackground="#e2e8f0", activeforeground="#000000",
                     bd=0, width=38, pady=10, command=open_device)
btn_main.pack(pady=5)

btn_close = tk.Button(app, text="🛑 Shut Down All Devices", font=("Arial", 11, "bold"), 
                      bg="#000000", fg="#ef4444", activebackground="#ef4444", activeforeground="#ffffff",
                      bd=1, relief="solid", width=38, pady=8, command=shut_down_all)
btn_close.pack(pady=5)

btn_game = tk.Button(app, text="🎮 Open Keymapper Window", font=("Arial", 11, "bold"), 
                     bg="#3b82f6", fg="#ffffff", activebackground="#2563eb", activeforeground="#ffffff",
                     bd=0, width=38, pady=8, command=open_game_controller)
btn_game.pack(pady=5)

# --- 1 TO 7 DEVICE OPTIONS ---
lbl_dev_section = tk.Label(app, text="📋 DEVICES LIST", font=("Arial", 10, "bold"), fg="#6b7280", bg="#000000")
lbl_dev_section.pack(pady=(15, 5))

for i in range(1, 8):
    btn_dev = tk.Button(app, text=f"Device {i}", font=("Arial", 10), 
                        bg="#111827", fg="#cbd5e1", activebackground="#1f2937", activeforeground="#ffffff",
                        bd=0, width=38, pady=4, command=lambda num=i: open_specific_device(num))
    btn_dev.pack(pady=2)

# --- OPEN ALL DEVICES OPTION ---
btn_all_devs = tk.Button(app, text="🌐 Open All Devices", font=("Arial", 11, "bold"), 
                        bg="#22c55e", fg="#ffffff", activebackground="#16a34a", activeforeground="#ffffff",
                        bd=0, width=38, pady=8, command=open_all_devices)
btn_all_devs.pack(pady=10)

twinkle_stars()
app.after(100, check_and_install_dependencies)
app.pack_propagate(False)
app.mainloop()
