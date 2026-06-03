import tkinter as tk
import subprocess
import os
import random
import platform
import sys
import urllib.request

CURRENT_VERSION = "1.2.5"
VERSION_URL = "https://raw.githubusercontent.com/Aerol5/Arl-Device/refs/heads/main/version.txt"
UPDATE_URL = "https://raw.githubusercontent.com/Aerol5/Arl-Device/refs/heads/main/main.py"

app = tk.Tk()
app.title("ARL")
app.geometry("500x650")
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

def open_specific_device(index):
    devices = get_devices()
    if len(devices) >= index:
        launch_scrcpy(devices[index - 1])
        lbl_status.config(text=f"Opened Device {index} 🚀", fg="#22c55e")
    else:
        lbl_status.config(text=f"Device {index} is not connected! ❌", fg="#ef4444")

# 🚀 PAG-POPOP-UP NG MENUHIN PARA SA MISMONG GAME WINDOW BUTTON
def open_game_window_menu():
    devices = get_devices()
    if not devices:
        lbl_status.config(text="No devices detected! ❌", fg="#ef4444")
        return
        
    menu_win = tk.Toplevel(app)
    menu_win.title("Select Game Window")
    menu_win.geometry("350x400")
    menu_win.configure(bg="#111827")
    
    lbl_menu = tk.Label(menu_win, text="📱 SELECT DEVICE FOR GAME WINDOW", font=("Arial", 11, "bold"), fg="#ffffff", bg="#111827")
    lbl_menu.pack(pady=15)
    
    for i in range(1, 8):
        btn_menu_dev = tk.Button(menu_win, text=f"Open Device {i}", font=("Arial", 10), 
                                 bg="#1f2937", fg="#ffffff", activebackground="#374151", activeforeground="#ffffff",
                                 bd=0, width=28, pady=5, command=lambda num=i: [open_specific_device(num), menu_win.destroy()])
        btn_menu_dev.pack(pady=3)

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

# --- APP MAIN SYSTEM CONTROLS ---
btn_main = tk.Button(app, text="🚀 Open Game Window (scrcpy)", font=("Arial", 11, "bold"), 
                     bg="#ffffff", fg="#000000", activebackground="#e2e8f0", activeforeground="#000000",
                     bd=0, width=38, pady=10, command=open_game_window_menu) # Ngayon ay nagbubukas na ng pop-up options
btn_main.pack(pady=5)

btn_close = tk.Button(app, text="🛑 Shut Down All Devices", font=("Arial", 11, "bold"), 
                      bg="#000000", fg="#ef4444", activebackground="#ef4444", activeforeground="#ffffff",
                      bd=1, relief="solid", width=38, pady=8, command=shut_down_all)
btn_close.pack(pady=5)

# --- 1 TO 7 MAIN SCREEN DEVICE OPTIONS ---
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
