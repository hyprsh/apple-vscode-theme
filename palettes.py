"""Source palettes for the themes: Clear Dark and Clear Light decoded from
macOS Terminal's profiles, and Apple System Colors (Light) copied verbatim
from Ghostty's bundled themes."""

# Ghostty's "Apple System Colors" and "Apple System Colors Light", verbatim.

DARK = {
    "ansi": [
        "#1a1a1a", "#cc372e", "#26a439", "#cdac08", "#0869cb", "#9647bf", "#479ec2", "#98989d",
        "#464646", "#ff453a", "#32d74b", "#ffd60a", "#0a84ff", "#bf5af2", "#76d6ff", "#ffffff",
    ],
    "background": "#1e1e1e",
    "foreground": "#ffffff",
    "cursor": "#98989d",
    "cursor_text": "#ffffff",
    "selection_bg": "#3f638b",
    "selection_fg": "#ffffff",
}

LIGHT = {
    "ansi": [
        "#1a1a1a", "#cc372e", "#26a439", "#cdac08", "#0869cb", "#9647bf", "#479ec2", "#98989d",
        "#464646", "#ff453a", "#32d74b", "#e5bc00", "#0a84ff", "#bf5af2", "#69c9f2", "#ffffff",
    ],
    "background": "#feffff",
    "foreground": "#000000",
    "cursor": "#98989d",
    "cursor_text": "#ffffff",
    "selection_bg": "#abd8ff",
    "selection_fg": "#000000",
}

# Apple system grays (not part of the Ghostty theme) used for UI chrome only.
DARK_GRAYS = ["#8e8e93", "#636366", "#48484a", "#3a3a3c", "#2c2c2e", "#1c1c1e"]
LIGHT_GRAYS = ["#8e8e93", "#aeaeb2", "#c7c7cc", "#d1d1d6", "#e5e5ea", "#f2f2f7"]


def mix(a, b, t):
    """Blend hex color a toward b by t (0..1)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def tinted_grays(bg, fg):
    """UI grays blended from the theme's own background and foreground. The
    first is Clear Dark's secondary text; at 0.58 it's 5:1 on the background
    (half-way, 0.50, is only 4.1:1)."""
    return [mix(bg, fg, t) for t in (0.58, 0.36, 0.24, 0.16, 0.09, 0.04)]


# Palettes decoded from macOS Terminal's "Clear Dark" and "Clear Light"
# profiles (Terminal.app/Contents/Resources/Initial Settings/*.terminal),
# converted to sRGB. Terminal draws the backgrounds slightly translucent
# (95% / 93%); VS Code can't, so they are opaque here.

CLEAR_DARK = {
    "ansi": [
        "#35424c", "#b45648", "#6caa71", "#c4ac62", "#6d96b4", "#bd7bcd", "#7ccbcd", "#dee5eb",
        "#465c6d", "#df6c5a", "#79be7e", "#e5c872", "#67b5ed", "#d389e5", "#84dde0", "#e5eff5",
    ],
    "background": "#212734",
    "foreground": "#e6e6e6",
    "cursor": "#919191",  # profile doesn't set one; same as Clear Light
    "cursor_text": "#212734",
    "selection_bg": "#334e5e",
    "selection_fg": None,
    "comment": mix("#212734", "#e6e6e6", 0.5),
    # Terminal's red and bright black are hard to read on this background;
    # build.py lightens them for the terminal.
    "readable_terminal": True,
}

CLEAR_LIGHT = {
    "ansi": [
        "#2d3840", "#b45648", "#6caa71", "#c4ac62", "#5685a8", "#ad64be", "#69c6c9", "#c1c8cc",
        "#506573", "#df6c5a", "#79be7e", "#e5c872", "#49a2e1", "#d389e5", "#77e1e5", "#d8e1e7",
    ],
    "background": "#ffffff",
    "foreground": "#3a4851",
    "cursor": "#919191",
    "cursor_text": "#ffffff",
    "selection_bg": "#e5ecf1",
    "selection_fg": None,
    "comment": mix("#ffffff", "#3a4851", 0.5),
    # Most of Terminal's colors are hard to read on white; build.py darkens
    # them for the terminal.
    "readable_terminal": True,
}

CLEAR_DARK_GRAYS = tinted_grays(CLEAR_DARK["background"], CLEAR_DARK["foreground"])
CLEAR_LIGHT_GRAYS = tinted_grays(CLEAR_LIGHT["background"], CLEAR_LIGHT["foreground"])
