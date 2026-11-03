"""Record the README demos from a live Claude Code session in a Rex pane.

    python3 assets/record.py editor|smart|autocomplete OUT.cast
    agg --theme github-light --font-size 18 OUT.cast assets/OUT.gif

Each run starts its own `claude --plugin-dir .` in a new Rex window with the mod's settings
rewritten for that demo (the dev-session store, ~/.claude/plugins/store/rich-prompt_inline-*.json).
"""
import glob, json, os, subprocess, sys, time

SET, OUT = sys.argv[1], sys.argv[2]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H, W = 9, 71
SMART = dict(capitalize=False, capitalizeI=False, spaceAfterPunct=False, doubleSpacePeriod=False, trimSpaceBeforePunct=False)
SETTINGS = {
    "editor": SMART,
    "smart": dict(capitalize=True, capitalizeI=True, spaceAfterPunct=True, doubleSpacePeriod=True, trimSpaceBeforePunct=True),
    "autocomplete": dict(SMART, autocomplete=True),
}[SET]

def rex(*a, **kw):
    return subprocess.run(["rex", *a], capture_output=True, text=True, **kw).stdout

store = glob.glob(os.path.expanduser("~/.claude/plugins/store/rich-prompt_inline-*.json"))[0]
data = json.load(open(store))
data["settings"] = dict(SETTINGS, autocomplete=SETTINGS.get("autocomplete", False))
json.dump(data, open(store, "w"))

BLOCK = json.loads(rex("run", "--json", "--keep-open", "--focus=false", "-c", "/tmp", "--", "claude", "--plugin-dir", REPO))["block_ids"][0]
time.sleep(9)

def hk(*keys):
    for k in keys:
        rex("send-key", "-b", BLOCK, k)
        time.sleep(0.12)

def snap():
    time.sleep(0.3)
    lines = rex("capture", "-b", BLOCK, "--trim").replace(" ", " ").split("\n")
    borders = [i for i, l in enumerate(lines) if "─" * 10 in l]
    top, bottom = borders[-2], borders[-1]
    out = []
    for i in range(bottom - H, bottom + 1):
        l = lines[i] if i >= 0 else ""
        out.append(l[:W] if i >= top or "rich-prompt" in l else "")
    return out

frames, t, caption = [], 0.0, ""

def emit(dt):
    global t
    cap = f"\x1b[1;38;2;196;90;0m  {caption}\x1b[0m"
    frames.append([round(t, 3), "o", "\x1b[?25l\x1b[2J\x1b[H" + "\r\n".join([cap, ""] + snap())])
    t += dt

SHIFTED = {"!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8", "(": "9", ")": "0",
           "_": "-", "+": "=", ":": ";", '"': "'", "<": ",", ">": ".", "?": "/", "{": "[", "}": "]", "|": "\\", "~": "`"}

def keyname(ch):
    if ch == " ":
        return "space"
    if ch.isupper():
        return f"shift+{ch.lower()}"
    return f"shift+{SHIFTED[ch]}" if ch in SHIFTED else ch

def typ(s, dt=0.09):
    for ch in s:
        hk(keyname(ch))
        emit(dt)

def key(k, dt=0.6):
    hk(k)
    emit(dt)

def scene(name):
    global caption
    hk("escape", "ctrl+c")
    time.sleep(2.5)  # let the "Press Ctrl-C again" hint expire
    caption = name
    emit(0.8)

if SET == "editor":
    scene("Lists continue on Shift+Enter")
    typ("Today:"); key("shift+enter")
    typ("- write README"); key("shift+enter")
    typ("record demo"); key("shift+enter")
    typ("ship it"); key("shift+enter", 0.9)
    key("shift+enter", 0.9)
    typ("1. clone"); key("shift+enter")
    typ("symlink"); key("shift+enter")
    typ("restart Claude"); key("shift+enter", 0.9)
    key("shift+enter", 2.0)

    scene("Nested items + auto-indent")
    typ("- fruits"); key("shift+enter")
    key("space", 0.3); key("space", 0.8)
    typ("apple"); key("shift+enter")
    typ("pear"); key("shift+enter", 0.9)
    key("shift+enter", 0.9)
    key("shift+enter", 0.9)
    typ("  plain indent"); key("shift+enter")
    typ("keeps its margin"); emit(2.0)

    scene("Auto-pair ( [ `  ·  closer steps over  ·  Backspace drops both")
    typ("run `"); emit(0.5)
    typ("npm test"); key("right", 0.5)
    typ(" then print("); emit(0.6)
    typ(")"); emit(0.8)
    typ(" and list["); emit(0.6)
    key("backspace", 0.8)
    typ("[0"); key("right", 2.5)

elif SET == "smart":
    scene("Capitalizes sentences, lines and a lone i")
    typ("hello there. i think it works! ok"); emit(1.0)
    key("shift+enter"); typ("a new line starts with a capital", 0.06); emit(2.0)

    scene("Spaces after , ; ! ?   ·   no space before them")
    typ("well,it works;great!ship it"); emit(1.2)
    typ(" ,"); emit(2.0)

    scene("Double space adds a period")
    typ("that is done"); key("space", 0.5); key("space", 0.8)
    typ("next thought"); emit(2.0)

elif SET == "autocomplete":
    scene("Suggestions follow your typing  ·  Tab accepts and adds a space")
    typ("please impl"); emit(1.8)
    key("tab", 1.0)
    typ("the conf"); emit(1.8)
    key("tab", 1.0)
    typ("it"); emit(1.5)

    scene("Down picks another row  ·  Tab takes it")
    typ("we need auth"); emit(1.2)
    key("down", 1.0); key("down", 1.0)
    key("tab", 2.0)

    scene("Arrow keys stay quiet  ·  Esc closes the rows")
    typ("check the implementation plan"); key("space", 0.4)
    for _ in range(4):
        key("left", 0.35)
    for _ in range(4):
        key("right", 0.35)
    emit(0.8)
    typ("perf"); emit(1.5)
    key("escape", 2.0)

rex("block", "close", BLOCK)
header = {"version": 2, "width": W, "height": H + 3}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for fr in frames:
        f.write(json.dumps(fr) + "\n")
print(len(frames), "frames", round(t, 1), "s")
