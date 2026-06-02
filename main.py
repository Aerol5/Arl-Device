import tkinter as tk
import subprocess
import os
import random
import platform
import sys
import zipfile
import urllib.request
from shutil import which

CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/Aerol5/Arl-Device/refs/heads/main/version.txt"
UPDATE_URL = "https://raw.githubusercontent.com/Aerol5/Arl-Device/refs/heads/main/main.py"

app = tk.Tk()
app.title("ARL")
app.geometry("500x620")
app.configure(bg="#000000")

if platform.system() == "Windows":
    TOOLS_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ARL_Tools")
else:
    TOOLS_DIR = os.path.join(os.path.expanduser("~"), ".arl_tools")

os.makedirs(TOOLS_DIR, exist_ok=True)

if platform.system() == "Windows":
    os.environ["PATH"] = TOOLS_DIR + os.pathsep + os.environ.get("PATH", "")
else:
    os.environ["PATH"] = TOOLS_DIR + os.pathsep + "/usr/local/bin:/usr/bin:/bin" + os.pathsep + os.environ.get("PATH", "")

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

lbl_title = tk.Label(app, text="Arl", font=("Arial", 16, "bold"), fg="#ffffff", bg="#000000")
lbl_title.pack(pady=(10, 5))

lbl_sub = tk.Label(app, text="Arl Multi-Control", font=("Arial", 9), fg="#6b7280", bg="#000000")
lbl_sub.pack(pady=(0, 5))

lbl_status = tk.Label(app, text="Loading...", font=("Arial", 9, "italic"), fg="#94a3b8", bg="#000000")
lbl_status.pack(pady=(0, 15))

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
        
    lbl_status.config(text="Checking system components...", fg="#fef08a")
    app.update()
    
    os_type = platform.system()
    
    if os_type == "Linux":
        needed = []
        if not which("adb"): needed.append("adb")
        if not which("scrcpy"): needed.append("scrcpy")
        
        if needed:
            lbl_status.config(text="Installing missing tools via apt...", fg="#fef08a")
            app.update()
            try:
                subprocess.run(["sudo", "apt", "update", "-y"], check=False)
                subprocess.run(["sudo", "apt", "install", "-y"] + needed, check=True)
            except:
                pass

    elif os_type == "Darwin":
        needed_mac = []
        if not which("adb"): needed_mac.append("android-platform-tools")
        if not which("scrcpy"): needed_mac.append("scrcpy")
        
        if needed_mac:
            lbl_status.config(text="Installing tools via Homebrew...", fg="#fef08a")
            app.update()
            try:
                if not which("brew"):
                    lbl_status.config(text="Please install Homebrew on Mac first!", fg="#ef4444")
                    return
                subprocess.run(["brew", "install"] + needed_mac, check=True)
            except:
                pass

    elif os_type == "Windows":
        adb_path = os.path.join(TOOLS_DIR, "adb.exe")
        scrcpy_path = os.path.join(TOOLS_DIR, "scrcpy.exe")
        
        if not os.path.exists(adb_path) or not os.path.exists(scrcpy_path):
            lbl_status.config(text="Downloading Windows tools (scrcpy/adb)...", fg="#fef08a")
            app.update()
            
            zip_url = "https://github.com/Genymobile/scrcpy/releases/download/v2.4/scrcpy-win64-v2.4.zip"
            zip_path = os.path.join(TOOLS_DIR, "scrcpy.zip")
            
            try:
                urllib.request.urlretrieve(zip_url, zip_path)
                lbl_status.config(text="Extracting tools...", fg="#fef08a")
                app.update()
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    for member in zip_ref.namelist():
                        filename = os.path.basename(member)
                        if not filename: continue
                        source = zip_ref.open(member)
                        target = open(os.path.join(TOOLS_DIR, filename), "wb")
                        with source, target:
                            target.write(source.read())
                            
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            except:
                lbl_status.config(text="Download failed! Check connection.", fg="#ef4444")
                return

    lbl_status.config(text=f"System Ready v{CURRENT_VERSION} ✅", fg="#22c55e")

def twinkle_stars():
    for star in stars:
        color = random.choice(["#ffffff", "#94a3b8", "#cbd5e1", "#e2e8f0", "#1e293b"])
        sky.itemconfig(star, fill=color)
    app.after(500, twinkle_stars) 

def get_devices():
    try:
        cmd = "adb.exe" if platform.system() == "Windows" else "adb"
        output = subprocess.check_output([cmd, "devices"]).decode("utf-8")
        lines = output.strip().split("\n")[1:]
        return [line.split("\t")[0] for line in lines if line.strip() and "device" in line]
    except:
        return []

def open_device():
    devices = get_devices()
    width, height = 280, 450
    start_x, start_y = 50, 50
    adb_cmd = "adb.exe" if platform.system() == "Windows" else "adb"
    scrcpy_cmd = "scrcpy.exe" if platform.system() == "Windows" else "scrcpy"

    for index, serial in enumerate(devices):
        subprocess.Popen(f'{adb_cmd} -s {serial} shell input keyevent 224', shell=True)
        
        if index < 4:
            x_pos = start_x + (index * (width + 20))
            y_pos = start_y
        else:
            x_pos = start_x + ((index - 4) * (width + 20))
            y_pos = start_y + height + 50
            
        cmd = f'{scrcpy_cmd} -s "{serial}" --always-on-top --mouse-bind=++++ --window-width={width} --window-height={height} --window-x={x_pos} --window-y={y_pos} &'
        if platform.system() == "Windows":
            cmd = f'start /b {scrcpy_cmd} -s "{serial}" --always-on-top --mouse-bind=++++ --window-width={width} --window-height={height} --window-x={x_pos} --window-y={y_pos}'
        os.system(cmd)

def open_single_device(num):
    devices = get_devices()
    index = num - 1
    if index < len(devices):
        serial = devices[index]
        adb_cmd = "adb.exe" if platform.system() == "Windows" else "adb"
        scrcpy_cmd = "scrcpy.exe" if platform.system() == "Windows" else "scrcpy"
        
        subprocess.Popen(f'{adb_cmd} -s {serial} shell input keyevent 224', shell=True)
        width, height = 280, 450
        start_x, start_y = 50, 50
        
        if index < 4:
            x_pos = start_x + (index * (width + 20))
            y_pos = start_y
        else:
            x_pos = start_x + ((index - 4) * (width + 20))
            y_pos = start_y + height + 50
            
        cmd = f'{scrcpy_cmd} -s "{serial}" --always-on-top --mouse-bind=++++ --window-width={width} --window-height={height} --window-x={x_pos} --window-y={y_pos} &'
        if platform.system() == "Windows":
            cmd = f'start /b {scrcpy_cmd} -s "{serial}" --always-on-top --mouse-bind=++++ --window-width={width} --window-height={height} --window-x={x_pos} --window-y={y_pos}'
        os.system(cmd)

def back_all():
    adb_cmd = "adb.exe" if platform.system() == "Windows" else "adb"
    for serial in get_devices():
        subprocess.Popen(f'{adb_cmd} -s {serial} shell input keyevent 4', shell=True)

def shut_down_all():
    if platform.system() == "Windows":
        os.system("taskkill /f /im scrcpy.exe")
    else:
        os.system("pkill scrcpy")

btn_main = tk.Button(app, text="🚀 Open all", font=("Arial", 11, "bold"), 
                     bg="#ffffff", fg="#000000", activebackground="#e2e8f0", activeforeground="#000000",
                     bd=0, width=38, pady=12, command=open_device)
btn_main.pack(pady=5)

frame_single = tk.Frame(app, bg="#000000")
frame_single.pack(pady=10)

lbl_single = tk.Label(frame_single, text="Open Single: ", font=("Arial", 10), fg="#94a3b8", bg="#000000")
lbl_single.pack(side="left", padx=5)

for i in range(1, 8):
    btn_num = tk.Button(frame_single, text=str(i), font=("Arial", 10, "bold"),
                        bg="#1e293b", fg="#ffffff", activebackground="#334155", activeforeground="#ffffff",
                        bd=0, width=3, height=1, command=lambda n=i: open_single_device(n))
    btn_num.pack(side="left", padx=3)

btn_back = tk.Button(app, text="Back All", font=("Arial", 11, "bold"), 
                     bg="#1f2937", fg="#ffffff", activebackground="#374151", activeforeground="#ffffff",
                     bd=0, width=38, pady=12, command=back_all)
btn_back.pack(pady=5)

btn_close = tk.Button(app, text="🛑 Shut Down All", font=("Arial", 11, "bold"), 
                      bg="#000000", fg="#ef4444", activebackground="#ef4444", activeforeground="#ffffff",
                      bd=1, relief="solid", width=38, pady=10, command=shut_down_all)
btn_close.pack(pady=15)

twinkle_stars()
app.after(100, check_and_install_dependencies)
app.mainloop()
