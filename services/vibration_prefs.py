from services import esp_service
from services.firestore_service import get_vibration_settings

PARTNER_SAFE_MAX = 35      # Partner-Safe on නම් උපරිම vibration %


def raw_level_from_settings(s):
    """Firestore settings වලින් 10..100 level එකක් හදනවා (පරණ 0/1/2 අගයත් support)."""
    s = s or {}
    if s.get("vibration_level") is not None:
        lvl = int(round(float(s["vibration_level"])))
    else:
        old = int(round(float(s.get("vibration_intensity", 1))))
        lvl = {0: 30, 1: 60, 2: 100}.get(old, 60)
    return max(10, min(100, lvl))


def effective_level(level, partner_safe):
    level = max(10, min(100, int(level)))
    if partner_safe:
        level = min(level, PARTNER_SAFE_MAX)
    return level


def apply_saved(user_id):
    """Login වුනාම save කරපු vibration settings ESP එකට යවන්න (ESP reboot වුනත් නැවත set වෙනවා)."""
    if not user_id:
        return
    try:
        s = get_vibration_settings(user_id) or {}
        lvl = effective_level(raw_level_from_settings(s), s.get("partner_safe_alerts", False))
        esp_service.set_prefs(vib=lvl, anti=s.get("anti_snore_mode", True))
    except Exception as e:
        print("Apply saved vibration prefs failed:", e)