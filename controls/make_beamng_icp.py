"""Build a GameNative/Winlator on-screen control profile (.icp) for BeamNG.drive.

Geometry follows com.winlator.inputcontrols.ControlElement.computeBoundingBox():
snap = screenWidth / 100; half extents (in snaps, times scale):
  BUTTON CIRCLE 3x3, RECT/ROUND_RECT 4x2, SQUARE 2.5x2.5, STICK 6x6.
x/y in the file are the element centre as a fraction of the view size.
Bindings follow BeamNG 0.40 settings/inputmaps/xidevice.json + keyboard.json defaults.
"""
import json, sys

W, H = 2808, 1256            # phone in landscape (HONOR BKQ-N49)
SNAP = W / 100.0
GAME_X0 = (W - 1280 * H / 720) / 2 / W   # gamescope letterbox: ~0.102 each side

HALF = {  # (type, shape) -> half extents in snaps
    ("BUTTON", "CIRCLE"): (3, 3), ("BUTTON", "RECT"): (4, 2), ("BUTTON", "ROUND_RECT"): (4, 2),
    ("BUTTON", "SQUARE"): (2.5, 2.5), ("STICK", "CIRCLE"): (6, 6),
}

GAS, BRAKE, HAND, UTIL, GEAR, TILT, STEER = "#2ECC71", "#E74C3C", "#F39C12", "#FFFFFF", "#5DADE2", "#AF7AC5", "#FFFFFF"

def el(type_, shape, x, y, scale, text, bindings, color=None, active=None, opacity=None):
    b = list(bindings) + ["NONE"] * (4 - len(bindings))
    e = {"type": type_, "shape": shape, "bindings": b, "scale": scale, "x": x, "y": y,
         "toggleSwitch": False, "text": text, "iconId": 0}
    if color: e["buttonColor"] = color
    if active: e["buttonActiveColor"] = active
    if opacity is not None: e["buttonOpacity"] = opacity
    if type_ == "BUTTON": e["lookThrough"] = False
    return e

L = GAME_X0 / 2          # centre of the left black bar
R = 1 - GAME_X0 / 2      # centre of the right black bar
elements = [
    # ---- left hand: steering + utilities --------------------------------------
    el("STICK", "CIRCLE", 0.112, 0.735, 1.25, "",
       ["GAMEPAD_LEFT_THUMB_UP", "GAMEPAD_LEFT_THUMB_RIGHT", "GAMEPAD_LEFT_THUMB_DOWN", "GAMEPAD_LEFT_THUMB_LEFT"],
       opacity=0.55),
    el("STICK", "CIRCLE", L, 0.165, 0.68, "",
       ["GAMEPAD_RIGHT_THUMB_UP", "GAMEPAD_RIGHT_THUMB_RIGHT", "GAMEPAD_RIGHT_THUMB_DOWN", "GAMEPAD_RIGHT_THUMB_LEFT"],
       opacity=0.4),
    el("BUTTON", "ROUND_RECT", L, 0.315, 0.82, "TILT", ["GYRO_MODIFIER"], TILT, "#E8DAEF", 0.6),
    el("BUTTON", "ROUND_RECT", L, 0.405, 0.82, "REWIND", ["GAMEPAD_DPAD_LEFT"], UTIL, None, 0.45),
    el("BUTTON", "ROUND_RECT", L, 0.495, 0.82, "RESET", ["GAMEPAD_DPAD_RIGHT"], UTIL, None, 0.45),
    # ---- right hand: pedals, handbrake, gears -----------------------------------
    el("BUTTON", "SQUARE", 0.942, 0.705, 2.3, "GAS", ["GAMEPAD_BUTTON_R2"], GAS, "#A9F5C8", 0.6),
    el("BUTTON", "SQUARE", 0.818, 0.765, 2.0, "BRAKE", ["GAMEPAD_BUTTON_L2"], BRAKE, "#F5B7B1", 0.6),
    el("BUTTON", "CIRCLE", 0.818, 0.515, 1.1, "B·HBRAKE", ["GAMEPAD_BUTTON_B"], HAND, "#FAD7A0", 0.55),
    el("BUTTON", "ROUND_RECT", R, 0.295, 0.82, "Y·CAM", ["GAMEPAD_BUTTON_Y"], UTIL, None, 0.45),
    el("BUTTON", "ROUND_RECT", R, 0.385, 0.82, "A·GEAR+", ["GAMEPAD_BUTTON_A"], GEAR, "#D6EAF8", 0.5),
    el("BUTTON", "ROUND_RECT", R, 0.475, 0.82, "X·GEAR-", ["GAMEPAD_BUTTON_X"], GEAR, "#D6EAF8", 0.5),
    el("BUTTON", "ROUND_RECT", R, 0.12, 0.82, "HORN", ["KEY_H"], UTIL, None, 0.45),
    # ---- top row (inside the game image, clear of GameNative's HUD) -------------
    el("BUTTON", "ROUND_RECT", 0.655, 0.062, 0.72, "MENU", ["GAMEPAD_BUTTON_START"], UTIL, None, 0.4),
    el("BUTTON", "ROUND_RECT", 0.725, 0.062, 0.72, "MAP", ["GAMEPAD_BUTTON_SELECT"], UTIL, None, 0.4),
    el("BUTTON", "ROUND_RECT", 0.795, 0.062, 0.72, "RADIAL", ["GAMEPAD_DPAD_UP"], UTIL, None, 0.4),
    el("BUTTON", "ROUND_RECT", 0.865, 0.062, 0.72, "LIGHTS", ["KEY_N"], UTIL, None, 0.4),
]

gyro = {
    "mode": 1, "lastTarget": 1,            # left stick (BeamNG steering axis)
    "activationMode": 2,                    # toggle with the TILT button (GYRO_MODIFIER)
    "conversionStyle": 0, "inputPriority": 0,   # combined with the touch stick
    "sensitivity": 1.0, "verticalScale": 1.0, "steadyingDegreesPerSecond": 1.0,
    "smoothingMilliseconds": 25.0, "stickAntiDeadzone": 0.1,   # cancels BeamNG's 0.1 steering deadzone
    "tiltSteeringEnabled": True, "tiltFullScaleDegrees": 28.0, "tiltDeadzoneDegrees": 1.5,
    "invertX": False, "invertY": False,
}

profile = {
    "schemaVersion": 1, "id": 0, "name": "BeamNG Driving", "cursorSpeed": 1.0,
    "includedSections": ["onScreen", "gyro"],
    "elements": elements, "gyroSettings": gyro,
}

# ---- validation (mirrors ControlProfileService.validateElements + geometry) --------
BINDINGS = set("""NONE MOUSE_LEFT_BUTTON KEY_H KEY_N GYRO_MODIFIER GAMEPAD_BUTTON_A GAMEPAD_BUTTON_B GAMEPAD_BUTTON_X
GAMEPAD_BUTTON_Y GAMEPAD_BUTTON_L1 GAMEPAD_BUTTON_R1 GAMEPAD_BUTTON_SELECT GAMEPAD_BUTTON_START GAMEPAD_BUTTON_L2
GAMEPAD_BUTTON_R2 GAMEPAD_LEFT_THUMB_UP GAMEPAD_LEFT_THUMB_RIGHT GAMEPAD_LEFT_THUMB_DOWN GAMEPAD_LEFT_THUMB_LEFT
GAMEPAD_RIGHT_THUMB_UP GAMEPAD_RIGHT_THUMB_RIGHT GAMEPAD_RIGHT_THUMB_DOWN GAMEPAD_RIGHT_THUMB_LEFT GAMEPAD_DPAD_UP
GAMEPAD_DPAD_RIGHT GAMEPAD_DPAD_DOWN GAMEPAD_DPAD_LEFT""".split())
boxes, ok = [], True
for i, e in enumerate(elements):
    assert 0 <= e["x"] <= 1 and 0 <= e["y"] <= 1 and 0.1 <= e["scale"] <= 5 and len(e["text"]) <= 128
    assert all(b in BINDINGS for b in e["bindings"]), e
    hx, hy = HALF[(e["type"], e["shape"])]
    cx, cy = e["x"] * W, e["y"] * H
    hw, hh = hx * SNAP * e["scale"], hy * SNAP * e["scale"]
    box = (cx - hw, cy - hh, cx + hw, cy + hh)
    if box[0] < 0 or box[1] < 0 or box[2] > W or box[3] > H:
        print("OFF-SCREEN:", e["text"] or e["type"], [round(v) for v in box]); ok = False
    for j, (ob, oe) in enumerate(boxes):
        if box[0] < ob[2] and ob[0] < box[2] and box[1] < ob[3] and ob[1] < box[3]:
            print("OVERLAP:", e["text"] or e["type"], "<->", oe["text"] or oe["type"]); ok = False
    boxes.append((box, e))
print("elements:", len(elements), "| letterbox bar width:", round(GAME_X0, 3), "| geometry ok:", ok)

out = sys.argv[1]
with open(out, "w", encoding="utf-8") as f:
    json.dump(profile, f, ensure_ascii=False, indent=1)
print("wrote", out)

# ---- preview image -------------------------------------------------------------
if len(sys.argv) > 2:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H), (12, 12, 14))
    d = ImageDraw.Draw(img, "RGBA")
    gx0 = int(GAME_X0 * W)
    d.rectangle([gx0, 0, W - gx0, H], fill=(52, 70, 84))
    d.text((W // 2, H // 2), "game image (1280x720)", fill=(150, 170, 185), anchor="mm",
           font=ImageFont.load_default(48))
    for box, e in boxes:
        col = e.get("buttonColor", "#FFFFFF").lstrip("#")
        rgb = tuple(int(col[k:k + 2], 16) for k in (0, 2, 4))
        a = int(255 * max(0.35, e.get("buttonOpacity", 0.5)))
        if e["type"] == "STICK" or e["shape"] == "CIRCLE":
            d.ellipse(box, outline=rgb + (a,), width=6, fill=rgb + (40,))
            if e["type"] == "STICK":
                cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2; r = (box[2] - box[0]) * 0.22
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb + (a,))
        else:
            d.rounded_rectangle(box, radius=24 if e["shape"] == "ROUND_RECT" else 4, outline=rgb + (a,), width=6, fill=rgb + (40,))
        label = e["text"] or ("STEER" if "LEFT_THUMB" in e["bindings"][0] else "LOOK")
        size = max(22, min(int((box[3] - box[1]) * 0.32), int((box[2] - box[0]) / max(4, len(label)) * 1.5)))
        d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 if e["type"] != "STICK" else box[3] + 28), label,
               fill=(255, 255, 255, 235), anchor="mm", font=ImageFont.load_default(size))
    img.save(sys.argv[2])
    print("preview", sys.argv[2])
