import threading
import time
from datetime import datetime

import requests

_cfg = {"ip": "10.33.175.140"}
TIMEOUT = 4

# ---- heartbeat state ----
_state = {"connected": False, "status": None, "last_saved": ""}
_listeners = {}
_hb = {"thread": None, "stop": threading.Event()}

# ---- logged-in user ----
_user = {"id": None}

# ---- alarms ----
_alarms = {"times": [], "dirty": True, "last_time_sync": 0.0}

# ---- vibration prefs (ESP reboot වුනත් ආපහු set කරන්න) ----
_prefs = {"vib": None, "anti": None}


def set_ip(ip: str):
    _cfg["ip"] = ip.strip()


def get_ip() -> str:
    return _cfg["ip"]


def set_user_id(uid):
    _user["id"] = uid


def set_prefs(vib=None, anti=None):
    if vib is not None:
        _prefs["vib"] = int(vib)
    if anti is not None:
        _prefs["anti"] = bool(anti)


def _get(path: str, params: dict | None = None) -> dict:
    url = f"http://{_cfg['ip']}{path}"
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        data = r.json()
        if "ok" not in data:
            data["ok"] = r.ok
        return data
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Timeout - pillow not reachable"}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "Cannot connect - check IP and WiFi"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_status():            return _get("/status")
def inflate(ms=2000):        return _get("/inflate", {"ms": int(ms)})
def deflate(ms=3000):        return _get("/deflate", {"ms": int(ms)})
def stop_all():              return _get("/stop")
def set_vibration(level):    return _get("/vibrate", {"level": int(level)})
def test_vibration():        return _get("/vibrate", {"test": 1})
def vibrate_preview(level):  return _get("/vibrate", {"level": int(level), "test": 1})
def set_config(**kw):        return _get("/config", kw)
def start_session():         return _get("/session/start")
def stop_session():          return _get("/session/stop")
def session_ack():           return _get("/session/ack")
def alarm_stop():            return _get("/alarm/stop")
def alarm_snooze(minutes=5): return _get("/alarm/snooze", {"min": int(minutes)})


def run_async(fn, *args, on_done=None):
    """Network call UI එක freeze නොකර background thread එකක run කරන්න."""
    def worker():
        result = fn(*args)
        if on_done:
            on_done(result)
    threading.Thread(target=worker, daemon=True).start()


# ---- time + alarm sync ----
def sync_time():
    n = datetime.now()
    sod = n.hour * 3600 + n.minute * 60 + n.second
    _alarms["last_time_sync"] = time.time()
    return _get("/settime", {"sod": sod})


def set_alarm_times(times):
    """Enabled alarm times (['06:30', ...]) දෙන්න. ඊළඟ heartbeat එකේදී ESP එකට යනවා."""
    _alarms["times"] = sorted(set(times))
    _alarms["dirty"] = True


def push_alarms():
    s = ",".join(t.replace(":", "") for t in _alarms["times"])
    return _get("/alarms", {"list": s})


def _sync_device(res):
    if not res.get("ok"):
        return
    if (not res.get("timeSet")) or (time.time() - _alarms["last_time_sync"] > 3600):
        sync_time()
        _alarms["dirty"] = True
    if _alarms["dirty"] or res.get("alarms", -1) != len(_alarms["times"]):
        r = push_alarms()
        if r.get("ok"):
            _alarms["dirty"] = False

    # vibration prefs
    q = {}
    if _prefs["vib"] is not None and res.get("vib") != _prefs["vib"]:
        q["vib"] = _prefs["vib"]
    if _prefs["anti"] is not None and res.get("antiSnore") != _prefs["anti"]:
        q["anti"] = 1 if _prefs["anti"] else 0
    if q:
        _get("/config", q)


# ---- auto sleep session -> Firestore ----
def _handle_pending(res):
    uid = _user["id"]
    if not uid or not res.get("pendingSession"):
        return
    try:
        from services.firestore_service import save_sleep_session
        secs = int(res.get("lastSec", 0))
        snores = int(res.get("lastSnores", 0))
        score = max(40, 100 - snores * 4)
        quality = "good" if score >= 80 else "fair" if score >= 60 else "poor"
        duration = f"{secs // 3600}h {(secs % 3600) // 60}m"
        save_sleep_session(uid, {
            "sleep_score": score,
            "quality": quality,
            "duration": duration,
            "snore_count": snores,
            "created_at": datetime.utcnow(),
        })
        _state["last_saved"] = f"Saved: {duration}, {snores} snore events, score {score}"
        session_ack()
    except Exception as e:
        print("Auto session save failed:", e)


# ---- heartbeat ----
def is_connected() -> bool:
    return _state["connected"]


def last_status():
    return _state["status"]


def get_last_saved() -> str:
    return _state["last_saved"]


def set_last_saved(msg: str):
    _state["last_saved"] = msg


def set_listener(fn, key="default"):
    """key වෙනස් කරලා listener කිහිපයක් register කරන්න පුළුවන්."""
    _listeners[key] = fn


def _heartbeat_loop(interval):
    while not _hb["stop"].is_set():
        res = get_status()
        _state["connected"] = bool(res.get("ok"))
        _state["status"] = res if res.get("ok") else None

        if res.get("ok"):
            try:
                _sync_device(res)
                _handle_pending(res)
            except Exception as e:
                print("Heartbeat sync error:", e)

        for fn in list(_listeners.values()):
            try:
                fn(_state["connected"], res)
            except Exception:
                pass
        _hb["stop"].wait(interval)


def start_heartbeat(interval=3):
    if _hb["thread"] and _hb["thread"].is_alive():
        return
    _hb["stop"].clear()
    t = threading.Thread(target=_heartbeat_loop, args=(interval,), daemon=True)
    _hb["thread"] = t
    t.start()


def stop_heartbeat():
    _hb["stop"].set()