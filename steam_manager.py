# ============================================================
#  NullZone — Steam NFA Manager v11.0
# ============================================================
import customtkinter as ctk
import tkinter as tk
import json, os, re, subprocess, sys, time, threading, base64, winreg
from PIL import Image, ImageDraw
import urllib.request, urllib.error, io, webbrowser

ctk.set_appearance_mode("dark")

NOTE_OPTIONS = [
    "21 hours cooldown",
    "7 days cooldown",
    "30 days cooldown",
    "181 days cooldown",
]

COOLDOWN_SECONDS = {
    "21 hours cooldown":  21 * 3600,
    "7 days cooldown":    7  * 86400,
    "30 days cooldown":   30 * 86400,
    "181 days cooldown":  181 * 86400,
}

def cooldown_status(acc):
    """
    Returns (remaining_str, expired) for the cooldown note.
    remaining_str: e.g. "16h 32m left"  or  "EXPIRED"  or  "" (no note)
    expired: True if cooldown has passed
    """
    note     = acc.get("note", "")
    set_at   = acc.get("note_set_at", 0)
    if not note or note not in COOLDOWN_SECONDS: return "", False
    duration  = COOLDOWN_SECONDS[note]
    remaining = (set_at + duration) - time.time()
    if remaining <= 0:
        return "EXPIRED", True
    h = int(remaining // 3600)
    m = int((remaining % 3600) // 60)
    if h >= 24:
        d = h // 24; h = h % 24
        return f"{d}d {h}h left", False
    return f"{h}h {m}m left", False

class Tooltip:
    """Shows a small popup label on hover."""
    def __init__(self, widget, text_func):
        self._widget   = widget
        self._text_func = text_func   # callable so it always uses latest note
        self._tip      = None
        widget.bind("<Enter>",  self._show)
        widget.bind("<Leave>",  self._hide)
        widget.bind("<Button-1>", self._hide)

    def _show(self, e=None):
        text = self._text_func()
        if not text: return
        self._hide()
        x = self._widget.winfo_rootx() + 24
        y = self._widget.winfo_rooty() - 28
        self._tip = tk.Toplevel(self._widget)
        self._tip.overrideredirect(True)
        self._tip.attributes("-topmost", True)
        self._tip.configure(bg="#2a2a2a")
        tk.Label(self._tip, text=text, bg="#2a2a2a", fg="#e8e8e8",
                 font=("Segoe UI", 9), padx=8, pady=4).pack()
        self._tip.geometry(f"+{x}+{y}")

    def _hide(self, e=None):
        if self._tip:
            try: self._tip.destroy()
            except: pass
            self._tip = None
ctk.set_default_color_theme("dark-blue")

def app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def resource(filename):
    """Resolve path whether running as .py or as PyInstaller --onefile exe."""
    if getattr(sys, '_MEIPASS', None):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(app_dir(), filename)

APP_DIR       = app_dir()
ACCOUNTS_FILE = os.path.join(APP_DIR, "accounts.json")
BLOCKLIST_FILE = os.path.join(APP_DIR, "removed.json")   # never re-import these
CACHE_DIR     = os.path.join(APP_DIR, "session_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
REMOVED_FILE = os.path.join(APP_DIR, "removed_accounts.json")

WIN_W, WIN_H = 500, 630
SF = "Segoe UI"

BG        = "#111111"
PANEL     = "#161616"
INPUT_BG  = "#1e1e1e"
CARD_BG   = "#1a1a1a"
CARD_HOV  = "#232323"
SEP       = "#252525"
BORDER    = "#2a2a2a"
TXT       = "#e8e8e8"
TXT2      = "#999999"
TXT3      = "#505050"
BTN_BG    = "#242424"
BTN_HOV   = "#2e2e2e"
GREEN     = "#00cc55"
RED_ERR   = "#cc3333"
GOLD      = "#cc8800"
LOGIN_BG  = "#3a3a3a"
LOGIN_HOV = "#484848"

# ── Removed accounts blocklist ───────────────────────────────
def load_removed():
    if not os.path.exists(REMOVED_FILE): return set()
    try:
        with open(REMOVED_FILE) as f: return set(json.load(f))
    except: return set()

def save_removed(s):
    with open(REMOVED_FILE, "w") as f: json.dump(list(s), f)

def mark_removed(steam_id):
    s = load_removed(); s.add(steam_id); save_removed(s)

def unmark_removed(steam_id):
    s = load_removed(); s.discard(steam_id); save_removed(s)

# ── Crypto ────────────────────────────────────────────────────
def dpapi_encrypt(data, entropy):
    try:
        import win32crypt
        return win32crypt.CryptProtectData(
            data.encode(), None, entropy.encode(), None, None, 0).hex()
    except ImportError:
        return base64.b64encode(data.encode()).decode()

def compute_crc32(data):
    b = data.encode(); crc = 0xFFFFFFFF
    for byte in b:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if (crc & 1) else crc >> 1
    return hex(crc ^ 0xFFFFFFFF)[2:].lstrip("0")

def parse_jwt(token):
    try:
        # If token has extra data (----metadata or extra dots like .853Z timestamps),
        # extract only the first 3 dot-separated segments which form the valid JWT.
        parts = token.split(".")
        if len(parts) < 3:
            return None
        parts = parts[:3]  # header, payload, signature only
        pad = 4 - len(parts[1]) % 4
        return json.loads(base64.urlsafe_b64decode(parts[1] + "=" * pad))
    except:
        return None

def steam64_from_token(token):
    p = parse_jwt(token)
    return p.get("sub") if p else None

# ── Token checker — local + profile ping only ─────────────────
def check_token(token: str) -> dict:
    result = {"valid": False, "status": "", "detail": "",
              "steam_id": None, "expires": None}
    if not token or not token.strip():
        result.update(status="EMPTY", detail="No token provided.")
        return result
    payload = parse_jwt(token)
    if not payload:
        result.update(status="INVALID FORMAT",
                      detail="Token is not a valid JWT (cannot be decoded).")
        return result
    steam_id = payload.get("sub")
    if not steam_id:
        result.update(status="NO STEAMID",
                      detail="JWT payload missing 'sub' (SteamID) field.")
        return result
    result["steam_id"] = steam_id
    iss = payload.get("iss", "")
    if "steam" not in iss.lower():
        result.update(status="WRONG ISSUER",
                      detail=f"Issuer: '{iss}'. Expected a Steam issuer.")
        return result
    aud = payload.get("aud", [])
    if isinstance(aud, str): aud = [aud]
    if not any(x in aud for x in ("client","renew","web","derive","machine")):
        result.update(status="WRONG AUDIENCE",
                      detail=f"Audience {aud} — not a Steam client token.")
        return result
    exp = payload.get("exp")
    if exp:
        exp_str = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(exp))
        if time.time() > exp:
            result.update(status="EXPIRED",
                          detail=f"Token expired on {exp_str}.")
            result["expires"] = exp_str
            return result
        days_left = int((exp - time.time()) / 86400)
        result["expires"] = f"{exp_str}  ({days_left}d left)"
    # Read-only Steam profile ping
    persona = ""
    try:
        url = f"https://steamcommunity.com/profiles/{steam_id}/?xml=1"
        req = urllib.request.Request(url, headers={"User-Agent":"Valve/Steam HTTP/1.1"})
        with urllib.request.urlopen(req, timeout=7) as r:
            xml = r.read().decode(errors="replace")
        if "<error>" in xml.lower():
            result.update(status="ACCOUNT NOT FOUND",
                          detail=f"SteamID {steam_id} not found on Steam.")
            return result
        m = re.search(r'<steamID><!\[CDATA\[(.*?)\]\]>', xml)
        if m: persona = m.group(1)
    except Exception as e:
        result.update(valid=True, status="VALID (offline)",
                      detail=f"JWT structure OK. Could not reach Steam: {e}")
        return result
    result.update(
        valid=True, status="VALID ✓",
        detail=(f"Account: {persona}  ·  SteamID: {steam_id}"
                if persona else f"Account found. SteamID: {steam_id}"),
    )
    return result

# ── Steam helpers ─────────────────────────────────────────────
def find_steam():
    for reg in [r"SOFTWARE\WOW6432Node\Valve\Steam", r"SOFTWARE\Valve\Steam"]:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg) as k:
                p, _ = winreg.QueryValueEx(k, "InstallPath")
                if os.path.exists(p): return p
        except: pass
    for p in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam",
              r"D:\Steam", r"E:\Steam"]:
        if os.path.exists(p): return p
    return None

def get_local_vdf():
    return os.path.join(os.environ.get("LOCALAPPDATA",""), "Steam", "local.vdf")

def kill_steam():
    for proc in ["steam.exe", "steamwebhelper.exe"]:
        subprocess.run(["taskkill","/f","/im",proc],
                       capture_output=True, creationflags=0x08000000)
    time.sleep(2)

def remove_readonly(path):
    try:
        if os.path.exists(path): os.chmod(path, 0o666)
    except: pass

# ── Remove account from Steam files ───────────────────────────
def remove_from_steam_files(steam_path, steam_id, account_name):
    lu_path = os.path.join(steam_path, "config", "loginusers.vdf")
    if os.path.exists(lu_path):
        try:
            with open(lu_path,"r",encoding="utf-8",errors="replace") as f: content=f.read()
            sid_pos = content.find(f'"{steam_id}"')
            if sid_pos != -1:
                bs = content.find("{", sid_pos); depth=1; i=bs+1
                while i<len(content) and depth>0:
                    if content[i]=='{': depth+=1
                    elif content[i]=='}': depth-=1
                    i+=1
                start = content.rfind("\n", 0, sid_pos)
                if start==-1: start=sid_pos
                content = content[:start] + content[i:]
            remove_readonly(lu_path)
            with open(lu_path,"w",encoding="utf-8") as f: f.write(content)
        except: pass
    cfg_path = os.path.join(steam_path, "config", "config.vdf")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path,"r",encoding="utf-8",errors="replace") as f: content=f.read()
            am = re.search(r'"Accounts"\s*\{', content)
            if am:
                pos=am.end(); depth=1; i=pos
                while i<len(content) and depth>0:
                    if content[i]=='{': depth+=1
                    elif content[i]=='}': depth-=1
                    i+=1
                ae=i-1; inner=content[pos:ae]
                um=re.search(rf'"{re.escape(account_name)}"\s*\{{',inner)
                if um:
                    us=pos+um.start(); ue_rel=um.end()
                    depth2=1; j=pos+ue_rel
                    while j<len(content) and depth2>0:
                        if content[j]=='{': depth2+=1
                        elif content[j]=='}': depth2-=1
                        j+=1
                    start=content.rfind("\n",0,us)
                    if start==-1: start=us
                    content=content[:start]+content[j:]
            remove_readonly(cfg_path)
            with open(cfg_path,"w",encoding="utf-8") as f: f.write(content)
        except: pass
    local_path = get_local_vdf()
    if os.path.exists(local_path):
        try:
            an=account_name.split("@")[0] if "@" in account_name else account_name
            key=compute_crc32(an)+"1"
            with open(local_path,"r",encoding="utf-8",errors="replace") as f: content=f.read()
            lines=[l for l in content.splitlines(keepends=True) if key not in l]
            remove_readonly(local_path)
            with open(local_path,"w",encoding="utf-8") as f: f.writelines(lines)
        except: pass

# ── VDF patchers ──────────────────────────────────────────────
def patch_loginusers(path, steam_id, account_name):
    ts=int(time.time()); existing=""
    if os.path.exists(path):
        try:
            with open(path,"r",encoding="utf-8",errors="replace") as f: existing=f.read()
        except: pass
    if not existing.strip():
        result=(f'users\n{{\n\t"{steam_id}"\n\t{{\n'
                f'\t\tAccountName\t\t"{account_name}"\n\t\tPersonaName\t\t"NullZone"\n'
                f'\t\tRememberPassword\t\t"1"\n\t\tWantsOfflineMode\t\t"0"\n'
                f'\t\tSkipOfflineModeWarning\t\t"0"\n\t\tAllowAutoLogin\t\t"1"\n'
                f'\t\tMostRecent\t\t"1"\n\t\tTimestamp\t\t"{ts}"\n\t}}\n}}\n')
    else:
        result=re.sub(r'("MostRecent"\s+)"1"',r'\g<1>"0"',existing)
        if steam_id in result:
            sp=result.find(f'"{steam_id}"'); bs=result.find("{",sp); d=1; i=bs+1
            while i<len(result) and d>0:
                if result[i]=='{': d+=1
                elif result[i]=='}': d-=1
                i+=1
            be=i-1; blk=result[bs:be+1]
            for field,val in [("RememberPassword","1"),("AllowAutoLogin","1"),("MostRecent","1")]:
                if f'"{field}"' in blk:
                    blk=re.sub(rf'("{re.escape(field)}"\s+)"[^"]*"',rf'\g<1>"{val}"',blk)
                else:
                    blk=blk[:-1].rstrip()+f'\n\t\t"{field}"\t\t"{val}"\n\t}}'
            result=result[:bs]+blk+result[be+1:]
        else:
            entry=(f'\n\t"{steam_id}"\n\t{{\n\t\tAccountName\t\t"{account_name}"\n'
                   f'\t\tPersonaName\t\t"NullZone"\n\t\tRememberPassword\t\t"1"\n'
                   f'\t\tWantsOfflineMode\t\t"0"\n\t\tSkipOfflineModeWarning\t\t"0"\n'
                   f'\t\tAllowAutoLogin\t\t"1"\n\t\tMostRecent\t\t"1"\n'
                   f'\t\tTimestamp\t\t"{ts}"\n\t}}\n')
            close=result.rfind("}"); result=result[:close]+entry+result[close:]
    remove_readonly(path)
    with open(path,"w",encoding="utf-8") as f: f.write(result)

def patch_config(path, steam_id, account_name):
    existing=""
    if os.path.exists(path):
        try:
            with open(path,"r",encoding="utf-8",errors="replace") as f: existing=f.read()
        except: pass
    if not existing.strip():
        import random; mtbf=''.join([str(random.randint(0,9)) for _ in range(9)])
        result=(f'InstallConfigStore\n{{\n\tSoftware\n\t{{\n\t\tValve\n\t\t{{\n\t\t\tSteam\n\t\t\t{{\n'
                f'\t\t\t\tAutoUpdateWindowEnabled\t\t"0"\n\t\t\t\tAccounts\n\t\t\t\t{{\n'
                f'\t\t\t\t\t"{account_name}"\n\t\t\t\t\t{{\n\t\t\t\t\t\t"SteamID"\t\t"{steam_id}"\n'
                f'\t\t\t\t\t}}\n\t\t\t\t}}\n\t\t\t\tMTBF\t\t"{mtbf}"\n\t\t\t}}\n\t\t}}\n\t}}\n}}\n')
    else:
        result=existing; am=re.search(r'"Accounts"\s*\{',result)
        if am:
            pos=am.end(); d=1; i=pos
            while i<len(result) and d>0:
                if result[i]=='{': d+=1
                elif result[i]=='}': d-=1
                i+=1
            ae=i-1; inner=result[pos:ae]
            um=re.search(rf'"{re.escape(account_name)}"\s*\{{',inner)
            if um:
                us=pos+um.end(); d2=1; j=us
                while j<len(result) and d2>0:
                    if result[j]=='{': d2+=1
                    elif result[j]=='}': d2-=1
                    j+=1
                ue=j-1; ublk=result[us:ue]
                if '"SteamID"' in ublk:
                    ublk=re.sub(r'"SteamID"\s+"[^"]*"',f'"SteamID"\t\t"{steam_id}"',ublk)
                else:
                    ublk=ublk.rstrip()+f'\n\t\t\t\t\t\t"SteamID"\t\t"{steam_id}"\n\t\t\t\t\t'
                result=result[:us]+ublk+result[ue:]
            else:
                nu=(f'\n\t\t\t\t\t"{account_name}"\n\t\t\t\t\t{{\n'
                    f'\t\t\t\t\t\t"SteamID"\t\t"{steam_id}"\n\t\t\t\t\t}}\n\t\t\t\t')
                result=result[:ae]+nu+result[ae:]
        else:
            sm=re.search(r'"Steam"\s*\{',result)
            if sm:
                sp=sm.end(); d=1; i=sp
                while i<len(result) and d>0:
                    if result[i]=='{': d+=1
                    elif result[i]=='}': d-=1
                    i+=1
                ab=(f'\n\t\t\t\t"Accounts"\n\t\t\t\t{{\n\t\t\t\t\t"{account_name}"\n\t\t\t\t\t{{\n'
                    f'\t\t\t\t\t\t"SteamID"\t\t"{steam_id}"\n\t\t\t\t\t}}\n\t\t\t\t}}\n\t\t\t')
                result=result[:i-1]+ab+result[i-1:]
    remove_readonly(path)
    with open(path,"w",encoding="utf-8") as f: f.write(result)

def cache_path_for(username):
    safe=re.sub(r'[^a-zA-Z0-9_\-]','_',username)
    return os.path.join(CACHE_DIR,f"{safe}.cache")

def save_session_for(username, token):
    an=username.split("@")[0] if "@" in username else username
    key=compute_crc32(an)+"1"; enc=dpapi_encrypt(token,an)
    with open(cache_path_for(username),"w") as f: json.dump({"key":key,"enc":enc},f)

def patch_local_vdf(username, token):
    an=username.split("@")[0] if "@" in username else username
    key=compute_crc32(an)+"1"; enc=dpapi_encrypt(token,an)
    dst=get_local_vdf(); os.makedirs(os.path.dirname(dst),exist_ok=True)
    existing=""
    if os.path.exists(dst):
        try:
            with open(dst,"r",encoding="utf-8",errors="replace") as f: existing=f.read()
        except: pass
    if not existing.strip():
        result=(f'MachineUserConfigStore\n{{\n\tSoftware\n\t{{\n\t\tValve\n\t\t{{\n\t\t\tSteam\n\t\t\t{{\n'
                f'\t\t\t\tConnectCache\n\t\t\t\t{{\n\t\t\t\t\t{key}\t\t"{enc}"\n'
                f'\t\t\t\t}}\n\t\t\t}}\n\t\t}}\n\t}}\n}}\n')
    else:
        cc=re.search(r'"ConnectCache"\s*\{',existing)
        if cc:
            pos=cc.end(); d=1; i=pos
            while i<len(existing) and d>0:
                if existing[i]=='{': d+=1
                elif existing[i]=='}': d-=1
                i+=1
            ce=i-1; inner=existing[pos:ce]
            if key in inner:
                inner=re.sub(rf'({re.escape(key)}\s+)"[^"]*"',rf'\g<1>"{enc}"',inner)
            else:
                inner=inner.rstrip()+f'\n\t\t\t\t\t{key}\t\t"{enc}"\n\t\t\t\t'
            result=existing[:pos]+inner+existing[ce:]
        else:
            cb=(f'\n\t\t\t\tConnectCache\n\t\t\t\t{{\n\t\t\t\t\t{key}\t\t"{enc}"\n\t\t\t\t}}\n\t\t\t')
            sm=re.search(r'"Steam"\s*\{',existing)
            if sm:
                sp=sm.end(); d=1; i=sp
                while i<len(existing) and d>0:
                    if existing[i]=='{': d+=1
                    elif existing[i]=='}': d-=1
                    i+=1
                result=existing[:i-1]+cb+existing[i-1:]
            else:
                result=existing[:existing.rfind("}")]+cb+existing[existing.rfind("}"):]
    remove_readonly(dst)
    with open(dst,"w",encoding="utf-8") as f: f.write(result)

def read_steam_accounts(steam_path):
    lu=os.path.join(steam_path,"config","loginusers.vdf")
    if not os.path.exists(lu): return []
    try:
        with open(lu,"r",encoding="utf-8",errors="replace") as f: content=f.read()
        results=[]
        for m in re.finditer(r'"(\d{17})"\s*\{([^}]*)\}',content,re.DOTALL):
            sid=m.group(1); block=m.group(2)
            nm=re.search(r'"AccountName"\s+"([^"]+)"',block)
            if nm: results.append({"steamId":sid,"username":nm.group(1)})
        return results
    except: return []


def write_invisible_localconfig(steam_path, steam_id):
    """
    Write PersonaState=7 to localconfig.vdf BEFORE Steam starts.
    Returns the path so the caller can hold a lock on it.
    """
    try:
        steamid3 = str(int(steam_id) - 76561197960265728)
    except Exception:
        return None
    cfg_dir   = os.path.join(steam_path, 'userdata', steamid3, 'config')
    local_cfg = os.path.join(cfg_dir, 'localconfig.vdf')
    if not os.path.exists(cfg_dir):
        return local_cfg   # return path so watcher can handle it later
    try:
        remove_readonly(local_cfg)
        c = ''
        if os.path.exists(local_cfg):
            with open(local_cfg, 'r', encoding='utf-8', errors='replace') as f:
                c = f.read()
        if not c.strip():
            c = ('"UserLocalConfigStore"\n{\n'
                 '\t"friends"\n\t{\n'
                 '\t\t"PersonaState"\t\t"7"\n'
                 '\t}\n}\n')
        else:
            fm = re.search(r'"friends"\s*\{', c, re.IGNORECASE)
            if fm:
                pos = fm.end(); depth = 1; i = pos
                while i < len(c) and depth > 0:
                    if c[i] == '{': depth += 1
                    elif c[i] == '}': depth -= 1
                    i += 1
                fe = i - 1; blk = c[pos:fe]
                if re.search(r'"PersonaState"', blk, re.IGNORECASE):
                    blk = re.sub(r'("PersonaState"\s+)"[^"]*"',
                                 r'\g<1>"7"', blk, flags=re.IGNORECASE)
                else:
                    blk = blk.rstrip() + '\n\t\t"PersonaState"\t\t"7"\n\t\t'
                c = c[:pos] + blk + c[fe:]
            else:
                close = c.rfind('}')
                c = (c[:close] +
                     '\n\t"friends"\n\t{\n\t\t"PersonaState"\t\t"7"\n\t}\n' +
                     c[close:])
        with open(local_cfg, 'w', encoding='utf-8') as f:
            f.write(c)
    except Exception:
        pass
    return local_cfg


def do_login(account_name, token):
    if "@" in account_name: account_name = account_name.split("@")[0]
    payload = parse_jwt(token)
    if not payload: raise Exception("Invalid JWT token")
    steam_id   = payload.get("sub", "")
    steam_path = find_steam()
    if not steam_path: raise Exception("Steam not found")

    kill_steam()
    os.makedirs(os.path.join(steam_path, "config"), exist_ok=True)

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"SOFTWARE\Valve\Steam", 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, "AutoLoginUser", 0, winreg.REG_SZ, account_name)
    except: pass

    patch_config(os.path.join(steam_path,"config","config.vdf"), steam_id, account_name)
    patch_loginusers(os.path.join(steam_path,"config","loginusers.vdf"), steam_id, account_name)
    save_session_for(account_name, token)
    patch_local_vdf(account_name, token)

    # ── Write PersonaState=7 BEFORE Steam starts ──────────────
    local_cfg = write_invisible_localconfig(steam_path, steam_id)

    # ── Hold exclusive write lock on localconfig.vdf ──────────
    # while Steam is starting so it cannot overwrite PersonaState
    lock_handle = None
    if local_cfg and os.path.exists(local_cfg):
        try:
            import win32file, win32con, pywintypes
            lock_handle = win32file.CreateFile(
                local_cfg,
                win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                win32con.FILE_SHARE_READ,   # others can READ, not WRITE
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_ATTRIBUTE_NORMAL,
                None
            )
        except Exception:
            lock_handle = None

    # ── Launch Steam ──────────────────────────────────────────
    subprocess.Popen([os.path.join(steam_path, "steam.exe")],
                     creationflags=0x00000008)

    # ── Background: hold lock + fire URL ─────────────────────
    def _invisible_worker(lh=lock_handle, cfg=local_cfg):
        def fire():
            try:
                subprocess.Popen(
                    ['cmd', '/c', 'start', '', 'steam://friends/status/invisible'],
                    creationflags=0x08000000)
            except Exception:
                try: os.startfile('steam://friends/status/invisible')
                except: pass

        # Fire URL every 400ms for 20 seconds as backup
        for _ in range(50):
            fire()
            time.sleep(0.4)

        # Release lock after 20 seconds
        if lh:
            try:
                import win32file
                win32file.CloseHandle(lh)
            except Exception: pass

        # Handle new account: wait for userdata to appear then write
        if cfg and not os.path.exists(cfg):
            for _ in range(60):
                if os.path.exists(os.path.dirname(cfg)):
                    write_invisible_localconfig(steam_path, steam_id)
                    break
                time.sleep(1)

    threading.Thread(target=_invisible_worker, daemon=True).start()


def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE): return []
    try:
        with open(ACCOUNTS_FILE) as f: return json.load(f)
    except: return []

def save_accounts(a):
    with open(ACCOUNTS_FILE,"w") as f: json.dump(a,f,indent=2)

def load_blocklist():
    """SteamIDs that were explicitly removed — never re-import from Steam."""
    if not os.path.exists(BLOCKLIST_FILE): return set()
    try:
        with open(BLOCKLIST_FILE) as f: return set(json.load(f))
    except: return set()

def add_to_blocklist(steam_id):
    bl = load_blocklist()
    bl.add(steam_id)
    with open(BLOCKLIST_FILE,"w") as f: json.dump(list(bl),f)

# ── Avatar ────────────────────────────────────────────────────
AV_COLORS=["#c0392b","#2980b9","#8e44ad","#27ae60","#e67e22","#16a085","#d35400","#2c3e50"]
def av_color(name):
    h=0
    for c in name: h=(h*31+ord(c))%len(AV_COLORS)
    return AV_COLORS[h]

def make_avatar(size=56, name="?"):
    img=Image.new("RGBA",(size,size),(0,0,0,0))
    ImageDraw.Draw(img).ellipse([0,0,size-1,size-1],fill=av_color(name))
    return img

def fetch_img(url, size=56):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=5) as r: data=r.read()
        img=Image.open(io.BytesIO(data)).convert("RGBA").resize((size,size))
        mask=Image.new("L",(size,size),0)
        ImageDraw.Draw(mask).ellipse([0,0,size-1,size-1],fill=255)
        img.putalpha(mask); return img
    except: return None

def get_steam_avatar(steam_id, size=56):
    try:
        url=f"https://steamcommunity.com/profiles/{steam_id}/?xml=1"
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=5) as r: xml=r.read().decode()
        m=re.search(r'<avatarFull><!\[CDATA\[(.*?)\]\]>',xml)
        if m: return fetch_img(m.group(1),size)
    except: pass
    return None


def load_logo_image(size=32):
    """Load NZ logo — scales to given size. Uses resource() for frozen exe."""
    for name in ["nz_logo.png","nz_logo.jpeg","nz_logo.jpg"]:
        p = resource(name)
        if os.path.exists(p):
            try:
                img = Image.open(p).convert("RGBA").resize((size,size), Image.LANCZOS)
                return ctk.CTkImage(img, size=(size,size))
            except: pass
    return None

def load_cooldown_icon(size=14):
    """
    Returns dict of ImageTk.PhotoImage keyed by state: none/active/expired.
    Uses PIL point() for tinting — no numpy, no CTkImage, works with tk.Label.
    Must be called after the Tk root exists.
    """
    from PIL import ImageTk
    icons = {}
    p = resource("cooldown_icon.png")
    if not os.path.exists(p):
        return icons
    try:
        base = Image.open(p).convert("RGBA")
        # Use luminance as alpha so dark background becomes transparent
        lum = base.convert("L")
        base.putalpha(lum)
        for state, col in [("none",(60,60,60)),("active",(200,140,0)),("expired",(0,200,80))]:
            tinted = Image.merge("RGBA", [
                lum.point(lambda v, c=col[0]: int(v * c / 255)),
                lum.point(lambda v, c=col[1]: int(v * c / 255)),
                lum.point(lambda v, c=col[2]: int(v * c / 255)),
                lum,
            ])
            resized = tinted.resize((size, size), Image.LANCZOS)
            icons[state] = ImageTk.PhotoImage(resized)
    except Exception:
        pass
    return icons

# ═══════════════════════════════════════════════════════════════
#  APP  —  native window (overrideredirect=False) so taskbar
#           and minimize work 100%.  Caption removed via Win32
#           WS_CAPTION so we get clean frameless look.
# ═══════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Native window — taskbar + minimize work out of the box
        self.title("NullZone")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        sw=self.winfo_screenwidth(); sh=self.winfo_screenheight()
        self.geometry(f"{WIN_W}x{WIN_H}+{(sw-WIN_W)//2}+{(sh-WIN_H)//2}")
        # Set window icon — stored on self so GC never deletes it
        try:
            from PIL import ImageTk
            for name in ["nz_logo.png","nz_logo.jpeg","nz_logo.jpg"]:
                p = resource(name)
                if os.path.exists(p):
                    _raw = Image.open(p).convert("RGBA").resize((32,32), Image.LANCZOS)
                    self._tk_icon = ImageTk.PhotoImage(_raw)
                    self.iconphoto(True, self._tk_icon)
                    break
        except: pass
        try:
            ico = resource("nz_icon.ico")
            if os.path.exists(ico):
                self.iconbitmap(default=ico)
        except: pass
        self.update_idletasks()

        self.accounts     = load_accounts()
        self.avatar_cache = {}
        self._logo_img    = load_logo_image(32)
        self._cd_icons    = load_cooldown_icon(14)
        self._cd_icon     = load_cooldown_icon(15)
        self.steam_path   = find_steam()
        self.steam_ok     = self.steam_path is not None
        self._sync_from_steam()
        self._build_ui()
        self._render()
        threading.Thread(target=self._precache_all, daemon=True).start()

    def _start_drag(self, e):
        self._dx=e.x_root-self.winfo_x()
        self._dy=e.y_root-self.winfo_y()
    def _drag(self, e):
        self.geometry(f"+{e.x_root-self._dx}+{e.y_root-self._dy}")
    def _minimize(self): self.iconify()   # works natively
    def _close(self):    self.destroy()

    def _sync_from_steam(self):
        if not self.steam_path: return
        blocklist = load_blocklist()
        changed = False
        for sa in read_steam_accounts(self.steam_path):
            # Skip accounts that were explicitly removed by the user
            if sa["steamId"] in blocklist: continue
            if not any(a.get("steamId")==sa["steamId"] for a in self.accounts):
                self.accounts.append({
                    "id":str(int(time.time()*1000)+len(self.accounts)),
                    "username":sa["username"],"displayName":sa["username"],
                    "token":"","steamId":sa["steamId"],
                    "addedAt":int(time.time()),"noToken":True})
                changed=True
        if changed: save_accounts(self.accounts)

    def _precache_all(self):
        for acc in self.accounts:
            u=acc.get("username",""); t=acc.get("token","")
            if u and t:
                try: save_session_for(u,t)
                except: pass

    # ══════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── TAB ROW ───────────────────────────────────────────
        tr = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=36)
        tr.pack(fill="x"); tr.pack_propagate(False)
        tab_cfg = dict(font=(SF,9,"bold"), height=28, corner_radius=4, width=110)
        self._tab_acc = ctk.CTkButton(tr, text="ACCOUNTS",
            fg_color=BTN_HOV, hover_color=BTN_HOV, text_color=TXT,
            command=lambda: self._switch_tab("accounts"), **tab_cfg)
        self._tab_acc.pack(side="left", padx=(8,2), pady=4)
        self._tab_chk = ctk.CTkButton(tr, text="TOKEN CHECKER",
            fg_color="transparent", hover_color=BTN_BG, text_color=TXT3,
            command=lambda: self._switch_tab("checker"), **tab_cfg)
        self._tab_chk.pack(side="left", padx=2, pady=4)

        ctk.CTkFrame(self, fg_color=SEP, height=1, corner_radius=0).pack(fill="x")

        # ── PAGES ─────────────────────────────────────────────
        self._page_acc = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self._page_chk = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self._build_accounts_page()
        self._build_checker_page()
        self._page_acc.pack(fill="both", expand=True)

    def _switch_tab(self, tab):
        if tab == "accounts":
            self._page_chk.pack_forget()
            self._page_acc.pack(fill="both", expand=True)
            self._tab_acc.configure(fg_color=BTN_HOV, text_color=TXT)
            self._tab_chk.configure(fg_color="transparent", text_color=TXT3)
        else:
            self._page_acc.pack_forget()
            self._page_chk.pack(fill="both", expand=True)
            self._tab_chk.configure(fg_color=BTN_HOV, text_color=TXT)
            self._tab_acc.configure(fg_color="transparent", text_color=TXT3)

    # ── ACCOUNTS PAGE ─────────────────────────────────────────
    def _build_accounts_page(self):
        p = self._page_acc

        # Banner: logo + discord button
        banner = ctk.CTkFrame(p, fg_color=PANEL, corner_radius=0, height=88)
        banner.pack(fill="x"); banner.pack_propagate(False)

        bl = ctk.CTkFrame(banner, fg_color="transparent")
        bl.pack(side="left", padx=14, pady=8)
        # Store on self so Python GC never deletes the image reference
        self._banner_img = load_logo_image(80)
        if self._banner_img:
            ctk.CTkLabel(bl, image=self._banner_img, text="").pack(side="left")
        else:
            ctk.CTkLabel(bl, text="NullZone",
                         font=(SF, 15, "bold"), text_color=TXT2).pack(side="left")

        def open_discord():
            webbrowser.open("https://discord.com/invite/nullzone")
        ctk.CTkButton(banner, text="Join Discord →", width=110, height=28,
            fg_color="#5865F2", hover_color="#4752c4",
            text_color="#ffffff", font=(SF,9,"bold"),
            corner_radius=6, command=open_discord).pack(side="right", padx=14, pady=11)

        ctk.CTkFrame(p, fg_color=SEP, height=1, corner_radius=0).pack(fill="x")

        # Token input
        ip = ctk.CTkFrame(p, fg_color=PANEL, corner_radius=0)
        ip.pack(fill="x")
        ctk.CTkLabel(ip, text="TOKEN LOGIN", font=(SF,10),
                     text_color=TXT3).pack(anchor="w", padx=16, pady=(10,4))
        ir = ctk.CTkFrame(ip, fg_color="transparent")
        ir.pack(fill="x", padx=12, pady=(0,10))
        self.token_var = ctk.StringVar()
        self.token_entry = ctk.CTkEntry(ir, textvariable=self.token_var,
            placeholder_text="username----eyAi...,  steamid----eyAi...  (or  username:eyAi...)",
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TXT, placeholder_text_color=TXT3,
            font=(SF,11), height=40, corner_radius=8)
        self.token_entry.pack(side="left", fill="x", expand=True, padx=(0,8))
        self.token_entry.bind("<Return>", lambda e: self._quick_login())
        ctk.CTkButton(ir, text="Login", width=80, height=40,
            fg_color=LOGIN_BG, hover_color=LOGIN_HOV, text_color=TXT,
            font=(SF,12,"bold"), corner_radius=8, command=self._quick_login).pack(side="left")

        ctk.CTkFrame(p, fg_color=SEP, height=1, corner_radius=0).pack(fill="x")

        # Accounts bar
        ab = ctk.CTkFrame(p, fg_color=PANEL, corner_radius=0, height=38)
        ab.pack(fill="x"); ab.pack_propagate(False)
        ctk.CTkLabel(ab, text="ACCOUNTS", font=(SF,10),
                     text_color=TXT3).pack(side="left", padx=16)
        self.count_lbl = ctk.CTkLabel(ab, text="", font=(SF,10), text_color="#404040")
        self.count_lbl.pack(side="left")
        ctk.CTkButton(ab, text="Clear All", width=64, height=24,
            fg_color=BTN_BG, hover_color="#2a0000",
            text_color="#884444", font=(SF,10),
            corner_radius=5, command=self._clear_all_dialog).pack(side="right", padx=(0,10), pady=7)
        ctk.CTkButton(ab, text="Refresh", width=64, height=24,
            fg_color=BTN_BG, hover_color=BTN_HOV,
            text_color=TXT2, font=(SF,10),
            corner_radius=5, command=self._render).pack(side="right", padx=(0,4), pady=7)

        ctk.CTkFrame(p, fg_color=SEP, height=1, corner_radius=0).pack(fill="x")

        self.scroll = ctk.CTkScrollableFrame(p, fg_color=BG, corner_radius=0,
            scrollbar_button_color="#222222", scrollbar_button_hover_color="#333333")
        self.scroll.pack(fill="both", expand=True)
        self.grid_f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.grid_f.pack(fill="both", expand=True, padx=4, pady=4)

        foot = ctk.CTkFrame(p, fg_color=PANEL, corner_radius=0, height=22)
        foot.pack(fill="x", side="bottom"); foot.pack_propagate(False)
        ctk.CTkLabel(foot,
            text=f"  {'Steam found' if self.steam_ok else 'Steam not found'}",
            font=(SF,10), text_color=TXT3).pack(side="left", pady=4)
        n_c=len([f for f in os.listdir(CACHE_DIR) if f.endswith(".cache")])
        ctk.CTkLabel(foot, text=f"{n_c} sessions  ",
            font=(SF,10), text_color="#333333").pack(side="right", pady=4)

    # ── TOKEN CHECKER PAGE ────────────────────────────────────
    def _build_checker_page(self):
        p = self._page_chk
        ctk.CTkLabel(p, text="NFA TOKEN CHECKER", font=(SF,10,"bold"),
                     text_color=TXT3).pack(pady=(22,4), padx=20, anchor="w")
        ctk.CTkLabel(p, text="Local validation only — token is never sent to any server.",
                     font=(SF,10), text_color="#303030").pack(padx=20, anchor="w")
        inp_f = ctk.CTkFrame(p, fg_color="transparent")
        inp_f.pack(fill="x", padx=20, pady=(14,0))
        self._chk_var = ctk.StringVar()
        self._chk_entry = ctk.CTkEntry(inp_f, textvariable=self._chk_var,
            placeholder_text="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...",
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TXT, placeholder_text_color=TXT3,
            font=(SF,11), height=40, corner_radius=8)
        self._chk_entry.pack(side="left", fill="x", expand=True, padx=(0,8))
        self._chk_entry.bind("<Return>", lambda e: self._run_check())
        self._chk_btn = ctk.CTkButton(inp_f, text="Check", width=80, height=40,
            fg_color=LOGIN_BG, hover_color=LOGIN_HOV, text_color=TXT,
            font=(SF,11,"bold"), corner_radius=8, command=self._run_check)
        self._chk_btn.pack(side="left")

        self._chk_result = ctk.CTkFrame(p, fg_color=CARD_BG, corner_radius=10,
            border_width=1, border_color=BORDER)
        self._chk_result.pack(fill="x", padx=20, pady=16)
        sr = ctk.CTkFrame(self._chk_result, fg_color="transparent")
        sr.pack(fill="x", padx=16, pady=(14,4))
        self._chk_dot    = ctk.CTkLabel(sr, text="●", font=("Arial",11), text_color="#333333")
        self._chk_dot.pack(side="left", padx=(0,8))
        self._chk_status = ctk.CTkLabel(sr, text="Awaiting check…", font=(SF,11,"bold"), text_color="#444444")
        self._chk_status.pack(side="left")
        self._chk_detail = ctk.CTkLabel(self._chk_result, text="",
            font=(SF,10), text_color=TXT3, anchor="w", wraplength=420)
        self._chk_detail.pack(fill="x", padx=16, pady=(0,4))
        self._chk_sid = ctk.CTkLabel(self._chk_result, text="",
            font=(SF,10), text_color=TXT3, anchor="w")
        self._chk_sid.pack(fill="x", padx=16, pady=(0,4))
        self._chk_exp = ctk.CTkLabel(self._chk_result, text="",
            font=(SF,10), text_color=TXT3, anchor="w")
        self._chk_exp.pack(fill="x", padx=16, pady=(0,14))

    def _run_check(self):
        token = self._chk_var.get().strip()
        # Handle full lines with ---- separator (e.g. steamid----jwt----csgoRank:5----...)
        if "----" in token:
            # Extract the JWT (always the part between the first ---- and the second ----, or after the first ----)
            token = token.split("----")[1] if token.count("----") >= 1 else token
            # Also strip any trailing metadata after the JWT
            token = token.split("----")[0]
        self._chk_status.configure(text="Checking…", text_color=TXT2)
        self._chk_dot.configure(text_color="#555555")
        self._chk_detail.configure(text="")
        self._chk_sid.configure(text="")
        self._chk_exp.configure(text="")
        self._chk_btn.configure(state="disabled")
        def do():
            result = check_token(token)
            def update():
                col = GREEN if result["valid"] else RED_ERR
                self._chk_dot.configure(text_color=col)
                self._chk_status.configure(text=result["status"], text_color=col)
                self._chk_detail.configure(text=result["detail"])
                if result.get("steam_id"):
                    self._chk_sid.configure(text=f"SteamID:   {result['steam_id']}")
                if result.get("expires"):
                    self._chk_exp.configure(text=f"Expires:    {result['expires']}")
                self._chk_btn.configure(state="normal")
            self.after(0, update)
        threading.Thread(target=do, daemon=True).start()

    # ── Grid ──────────────────────────────────────────────────
    def _render(self):
        for w in self.grid_f.winfo_children(): w.destroy()
        self.accounts = load_accounts()
        n = len(self.accounts)
        self.count_lbl.configure(text=f"  {n} account{'s' if n!=1 else ''}")
        if not self.accounts:
            ctk.CTkLabel(self.grid_f,
                text="No accounts saved\n\nPaste  username----token  in the login bar",
                font=(SF,10), text_color="#2e2e2e", justify="center").pack(pady=80)
            return
        for i, acc in enumerate(self.accounts):
            r, c = divmod(i, 4)
            self._make_card(acc, r, c)
            self.grid_f.columnconfigure(c, weight=1)

    def _make_card(self, acc, row, col):
        uid   = acc.get("id",""); uname = acc.get("username","?")
        has_t = bool(acc.get("token","")); cached = os.path.exists(cache_path_for(uname))

        card = ctk.CTkFrame(self.grid_f, fg_color=CARD_BG, corner_radius=10,
            width=100, height=112, border_width=1, border_color=BORDER)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        card.grid_propagate(False)

        if uid not in self.avatar_cache:
            self.avatar_cache[uid] = ctk.CTkImage(make_avatar(56,uname), size=(50,50))
            if acc.get("steamId"):
                threading.Thread(target=self._fetch_av, args=(acc,uid), daemon=True).start()

        img_lbl  = ctk.CTkLabel(card, image=self.avatar_cache[uid], text="")
        img_lbl.pack(pady=(8,3))
        display  = acc.get("displayName", uname)
        if len(display) > 11: display = display[:10]+"…"
        name_lbl = ctk.CTkLabel(card, text=display, font=(SF,11,"bold"), text_color=TXT2)
        name_lbl.pack()
        if not has_t:  s,sc = "no token","#553333"
        elif cached:   s,sc = "● ready",  GREEN
        else:          s,sc = "◌ pending", GOLD
        sess = ctk.CTkLabel(card, text=s, font=(SF,9), text_color=sc)
        sess.pack()

        # ── Note / cooldown icon (left, symmetrical with dots) ──
        note_val  = acc.get("note","")
        rem_str, expired = cooldown_status(acc)
        cd_state = "expired" if expired else ("active" if note_val else "none")

        if expired:
            icon_fg = GREEN
        elif note_val:
            icon_fg = "#cc8800"
        else:
            icon_fg = "#3a3a3a"

        # Use cooldown image icon (tinted by state) or text fallback
        cd_icon_img = self._cd_icons.get(cd_state) if hasattr(self,"_cd_icons") else None
        if cd_icon_img:
            note_lbl = tk.Label(card, image=cd_icon_img,
                                bg=CARD_BG, cursor="hand2", bd=0, padx=2, pady=0)
            note_lbl.image = cd_icon_img   # prevent GC
        else:
            note_lbl = tk.Label(card, text="⏱", bg=CARD_BG, fg=icon_fg,
                                font=(SF,11), cursor="hand2", bd=0, padx=3, pady=0)
        note_lbl.place(relx=0.0, rely=0.0, x=4, y=5, anchor="nw")

        # Countdown label below avatar
        if rem_str:
            cd_color = GREEN if expired else "#cc8800"
            cd_lbl = tk.Label(card, text=rem_str, bg=CARD_BG, fg=cd_color,
                              font=(SF, 7), bd=0)
            cd_lbl.place(relx=0.5, rely=1.0, x=0, y=-2, anchor="s")

        # Tooltip: show note + time set
        def get_tooltip(a=acc):
            n = a.get("note","")
            if not n: return ""
            rs, ex = cooldown_status(a)
            ts = a.get("note_set_at", 0)
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts)) if ts else ""
            lines = [n]
            if rs:   lines.append(rs)
            if date_str: lines.append(f"Set: {date_str}")
            return "\n".join(lines)

        Tooltip(note_lbl, get_tooltip)

        # Click -> pick cooldown from menu
        def show_note_menu(event=None, a=acc, nl=note_lbl):
            menu = tk.Menu(self, tearoff=0,
                           bg="#1e1e1e", fg="#cccccc",
                           activebackground="#2e2e2e", activeforeground="#ffffff",
                           bd=0, relief="flat", font=(SF,10))

            def set_note(n, _a=a):
                _a["note"] = n
                _a["note_set_at"] = int(time.time()) if n else 0
                save_accounts(self.accounts)
                self._render()   # refresh cards to show countdown

            for opt in NOTE_OPTIONS:
                is_active = a.get("note") == opt
                menu.add_command(
                    label=f"  {'✓ ' if is_active else '  '}{opt}",
                    command=lambda n=opt: set_note(n),
                    foreground="#cc8800" if is_active else "#cccccc",
                )
            menu.add_separator()
            menu.add_command(label="  Clear cooldown", command=lambda: set_note(""),
                             foreground="#666666", activeforeground="#aaaaaa")

            bx = note_lbl.winfo_rootx()
            by = note_lbl.winfo_rooty() + note_lbl.winfo_height()
            try:
                menu.tk_popup(bx, by)
            finally:
                menu.grab_release()

        note_lbl.bind("<Button-1>", show_note_menu)

        # ── Three-dot menu (right) ────────────────────────────
        def show_menu(event=None, a=acc):
            menu = tk.Menu(self, tearoff=0,
                           bg="#1e1e1e", fg="#cccccc",
                           activebackground="#2e2e2e", activeforeground="#ffffff",
                           bd=0, relief="flat", font=(SF,10))
            def check_it():
                self._chk_var.set(a.get("token",""))
                self._switch_tab("checker")
                self.after(80, self._run_check)
            menu.add_command(label="  Check Token", command=check_it)
            menu.add_separator()
            menu.add_command(label="  Remove Account",
                             command=lambda: self._remove_dialog(a),
                             foreground="#cc4444", activeforeground="#ff6666",
                             activebackground="#2a0000")
            bx = dots.winfo_rootx()
            by = dots.winfo_rooty() + dots.winfo_height()
            try:
                menu.tk_popup(bx, by)
            finally:
                menu.grab_release()

        dots = tk.Label(card, text="⋯", bg=CARD_BG, fg="#555555",
                        activebackground=CARD_HOV, activeforeground="#aaaaaa",
                        font=(SF,12), cursor="hand2", bd=0, padx=3, pady=0)
        dots.place(relx=1.0, rely=0.0, x=-4, y=5, anchor="ne")
        dots.bind("<Button-1>", show_menu)

        def on_e(e, f=card, d=dots, n=note_lbl):
            f.configure(fg_color=CARD_HOV, border_color="#404040")
            d.configure(bg=CARD_HOV); n.configure(bg=CARD_HOV)
            for child in card.winfo_children():
                if isinstance(child, tk.Label): child.configure(bg=CARD_HOV)
        def on_l(e, f=card, d=dots, n=note_lbl):
            f.configure(fg_color=CARD_BG, border_color=BORDER)
            d.configure(bg=CARD_BG); n.configure(bg=CARD_BG)
            for child in card.winfo_children():
                if isinstance(child, tk.Label): child.configure(bg=CARD_BG)
        def on_c(e, a=acc):
            if not a.get("token"): self._set_token_dialog(a)
            else: self._login(a)

        for w in [card, img_lbl, name_lbl, sess]:
            w.bind("<Enter>", on_e); w.bind("<Leave>", on_l); w.bind("<Button-1>", on_c)

    def _fetch_av(self, acc, uid):
        img = get_steam_avatar(acc["steamId"], 56)
        if img:
            self.avatar_cache[uid] = ctk.CTkImage(img, size=(50,50))
            self.after(0, self._render)

    # ── Login ─────────────────────────────────────────────────
    def _quick_login(self):
        raw = self.token_var.get().strip()
        if not raw: self._toast("Paste a token first", err=True); return

        if "----" in raw:
            identifier, token = raw.split("----", 1)
            # Strip any extra metadata appended after the JWT (e.g. ----csgoRank:5----...)
            token = token.split("----")[0]
        elif ":" in raw and not raw.startswith("eyJ"):
            identifier, token = raw.split(":", 1)
        else:
            # Bare JWT — use sub[:8] as username
            p = parse_jwt(raw)
            username = p.get("sub", "account")[:8] if p else "account"
            token = raw
            identifier = username

        identifier = identifier.strip()
        token = token.strip()

        # ── SteamID64 mode (identifier is a 17-digit SteamID starting with 7656) ──
        if len(identifier) == 17 and identifier.startswith("7656") and identifier.isdigit():
            payload = parse_jwt(token)
            if not payload:
                self._toast("Invalid JWT token", err=True); return
            resolved_steam_id = identifier
            resolved_username = payload.get("sub", "")

            # Look for existing account by steamId (not by username) — avoids duplicates
            existing = next((a for a in self.accounts if a.get("steamId") == resolved_steam_id), None)
            if existing:
                existing["token"] = token
                existing["username"] = resolved_username
                existing["displayName"] = resolved_username
                existing.pop("noToken", None)
                save_accounts(self.accounts)
                acc = existing
            else:
                acc = {
                    "id": str(int(time.time()*1000)),
                    "username": resolved_username,
                    "displayName": resolved_username,
                    "token": token,
                    "steamId": resolved_steam_id,
                    "addedAt": int(time.time())
                }
                self.accounts.append(acc)
                save_accounts(self.accounts)

        # ── Username mode (original behaviour) ──
        else:
            username = identifier
            existing = next((a for a in self.accounts if a.get("username") == username), None)
            if existing:
                existing["token"] = token
                existing.pop("noToken", None)
                save_accounts(self.accounts)
                acc = existing
            else:
                acc = {
                    "id": str(int(time.time()*1000)),
                    "username": username,
                    "displayName": username,
                    "token": token,
                    "steamId": steam64_from_token(token),
                    "addedAt": int(time.time())
                }
                self.accounts.append(acc)
                save_accounts(self.accounts)

        self.token_var.set("")
        threading.Thread(target=save_session_for, args=(acc["username"], token), daemon=True).start()
        self._render()
        self._login(acc)

    def _login(self, acc):
        if not self.steam_ok: self._toast("Steam not found",err=True); return
        self._toast(f"Connecting  {acc['displayName']}…")
        threading.Thread(target=self._run_login,args=(acc,),daemon=True).start()

    def _run_login(self, acc):
        try:
            do_login(acc.get("username",""),acc.get("token",""))
            self.after(0,lambda:self._toast(f"Launched as  {acc['displayName']}",ok=True))
            self.after(1000,self._render)
        except Exception as ex:
            self.after(0,lambda:self._toast(f"Error: {ex}",err=True))

    # ── Dialogs ───────────────────────────────────────────────
    def _mk_dialog(self, title, w, h):
        d=ctk.CTkToplevel(self); d.title(title); d.geometry(f"{w}x{h}")
        d.configure(fg_color="#161616"); d.grab_set(); d.resizable(False,False)
        ctk.CTkFrame(d,fg_color=SEP,height=1,corner_radius=0).pack(fill="x")
        return d

    def _set_token_dialog(self, acc):
        d=self._mk_dialog("Add Token",460,210)
        ctk.CTkLabel(d,text=f"Add token for  {acc['username']}",
                     font=(SF,13,"bold"),text_color=TXT).pack(pady=(16,10))
        ctk.CTkLabel(d,text="JWT Refresh Token",font=(SF,10),text_color=TXT3).pack(anchor="w",padx=24)
        e=ctk.CTkEntry(d,fg_color=INPUT_BG,border_color=BORDER,border_width=1,
                       text_color=TXT,font=(SF,11),height=38,corner_radius=6)
        e.pack(fill="x",padx=24,pady=(4,8))
        st=ctk.CTkLabel(d,text="",font=(SF,10),text_color=TXT3); st.pack()
        def save():
            t=e.get().strip()
            if not t: return
            if not parse_jwt(t): st.configure(text="Invalid JWT",text_color=RED_ERR); return
            acc["token"]=t; acc.pop("noToken",None); save_accounts(self.accounts)
            threading.Thread(target=save_session_for,args=(acc["username"],t),daemon=True).start()
            d.destroy(); self._render(); self._login(acc)
        ctk.CTkButton(d,text="Save & Login",height=38,
                      fg_color=LOGIN_BG,hover_color=LOGIN_HOV,text_color=TXT,
                      font=(SF,11,"bold"),corner_radius=6,command=save).pack(fill="x",padx=24,pady=(4,0))

    def _remove_dialog(self, acc):
        d=self._mk_dialog("Remove Account",360,168)
        ctk.CTkLabel(d,text=f'Remove  "{acc["displayName"]}"?',
                     font=(SF,12,"bold"),text_color=TXT).pack(pady=(18,4))
        ctk.CTkLabel(d,text="Removes from this tool and from Steam's saved files.",
                     font=(SF,9),text_color=TXT3).pack(pady=(0,10))
        row=ctk.CTkFrame(d,fg_color="transparent"); row.pack()
        ctk.CTkButton(row,text="Cancel",width=120,height=34,
                      fg_color=BTN_BG,hover_color=BTN_HOV,text_color=TXT2,
                      font=(SF,10),command=d.destroy).pack(side="left",padx=8)
        def confirm():
            cp=cache_path_for(acc.get("username",""))
            if os.path.exists(cp):
                try: os.remove(cp)
                except: pass
            if self.steam_path and acc.get("steamId"):
                try: remove_from_steam_files(self.steam_path,acc["steamId"],acc.get("username",""))
                except: pass
            # Add to blocklist so it never reappears on next sync
            if acc.get("steamId"):
                add_to_blocklist(acc["steamId"])
            self.accounts=[a for a in self.accounts if a["id"]!=acc["id"]]
            save_accounts(self.accounts); d.destroy(); self._render()
            self._toast(f"{acc['displayName']} removed")
        ctk.CTkButton(row,text="Remove",width=120,height=34,
                      fg_color="#6b0000",hover_color="#8b0000",text_color="#fff",
                      font=(SF,10,"bold"),command=confirm).pack(side="left",padx=8)

    def _clear_all_dialog(self):
        d=self._mk_dialog("Clear All",360,170)
        ctk.CTkLabel(d,text="Remove all saved accounts?",
                     font=(SF,13,"bold"),text_color=TXT).pack(pady=(18,4))
        ctk.CTkLabel(d,text="Removes from this tool AND from Steam's saved files.",
                     font=(SF,9),text_color=TXT3).pack(pady=(0,10))
        row=ctk.CTkFrame(d,fg_color="transparent"); row.pack()
        ctk.CTkButton(row,text="Cancel",width=120,height=34,
                      fg_color=BTN_BG,hover_color=BTN_HOV,text_color=TXT2,
                      font=(SF,10),command=d.destroy).pack(side="left",padx=8)
        def confirm():
            for acc in self.accounts:
                cp=cache_path_for(acc.get("username",""))
                if os.path.exists(cp):
                    try: os.remove(cp)
                    except: pass
                if self.steam_path and acc.get("steamId"):
                    try: remove_from_steam_files(self.steam_path,acc["steamId"],acc.get("username",""))
                    except: pass
                # Blocklist so none reappear on next sync
                if acc.get("steamId"):
                    add_to_blocklist(acc["steamId"])
            self.accounts=[]; save_accounts(self.accounts)
            d.destroy(); self._render(); self._toast("All accounts cleared")
        ctk.CTkButton(row,text="Clear All",width=120,height=34,
                      fg_color="#6b0000",hover_color="#8b0000",text_color="#fff",
                      font=(SF,10,"bold"),command=confirm).pack(side="left",padx=8)

    # ── Toast ─────────────────────────────────────────────────
    def _toast(self,msg,err=False,ok=False):
        try:
            t=ctk.CTkToplevel(self); t.overrideredirect(True); t.attributes("-topmost",True)
            bg="#2a0010" if err else ("#0a1a0a" if ok else "#1e1e1e")
            col="#ff4466" if err else (GREEN if ok else TXT)
            t.configure(fg_color=bg)
            x=self.winfo_x()+WIN_W//2-190; y=self.winfo_y()+WIN_H-46
            t.geometry(f"380x34+{x}+{y}")
            ctk.CTkLabel(t,text=msg,font=(SF,10,"bold"),text_color=col).pack(expand=True)
            t.after(2800,t.destroy)
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
