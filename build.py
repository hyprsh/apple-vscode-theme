"""Generate the VS Code, Ghostty and herdr themes from the palettes in
palettes.py.

Run: python3 build.py
"""
import colorsys
import json
from pathlib import Path

from palettes import (
    CLEAR_DARK, CLEAR_DARK_GRAYS, CLEAR_LIGHT, CLEAR_LIGHT_GRAYS,
    DARK, DARK_GRAYS, LIGHT, LIGHT_GRAYS, mix,
)

ANSI_NAMES = [
    "Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White",
    "BrightBlack", "BrightRed", "BrightGreen", "BrightYellow",
    "BrightBlue", "BrightMagenta", "BrightCyan", "BrightWhite",
]


def alpha(color, a):
    return f"{color}{a:02x}"


def luminance(color):
    c = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def readable(color, bg, target=4.5, saturate=1.0):
    """Darken (on light bg) or lighten (on dark bg) color until it reaches
    the WCAG contrast target against bg. Hue and saturation are kept (and
    saturation optionally boosted) so the color doesn't turn muddy."""
    h, l, s = colorsys.rgb_to_hls(*(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)))
    s = min(1, s * saturate)
    step = -0.005 if luminance(bg) > 0.5 else 0.005

    def hex_(l):
        return "#" + "".join(f"{round(x * 255):02x}" for x in colorsys.hls_to_rgb(h, l, s))

    while contrast(hex_(l), bg) < target and 0 < l < 1:
        l = min(1, max(0, l + step))
    return hex_(l)


def over(color, under):
    """The opaque color that translucent color (#rrggbbaa) shows over under."""
    a = int(color[7:9], 16) / 255
    return "#" + "".join(
        f"{round(int(color[i:i + 2], 16) * a + int(under[i:i + 2], 16) * (1 - a)):02x}"
        for i in (1, 3, 5))


def vivid(color):
    """color's hue at full saturation, so even a faint tint of it shows."""
    h, _, _ = colorsys.rgb_to_hls(*(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)))
    return "#" + "".join(f"{round(x * 255):02x}" for x in colorsys.hls_to_rgb(h, 0.5, 1))


def tint(color, under, texts, most, layers=1):
    """color, translucent, at the strongest alpha up to most that keeps every
    text color readable (4.5:1) on it, even stacked layers times over under."""
    for a in range(most, 0, -1):
        shown = under
        for _ in range(layers):
            shown = over(alpha(color, a), shown)
        if all(contrast(t, shown) >= 4.5 for t in texts):
            return alpha(color, a)
    return alpha(color, 0)


def terminal_ansi(p):
    """The ANSI colors as the terminal gets them. For palettes marked
    readable_terminal, every color under 4.5:1 on the background is adjusted
    just enough to be readable, keeping its hue. Black and white are left
    alone, as programs use them for backgrounds; bright black is included, as
    it's the usual gray for dimmed text. In a light palette the six normal
    colors take the editor's hues, and the rest get the same saturation
    boost."""
    a = list(p["ansi"])
    if not p.get("readable_terminal"):
        return a
    bg = p["background"]
    dark = luminance(bg) < 0.5
    editor = [] if dark else hues(p, dark)
    for i in range(16):
        if i in (0, 7, 15) or contrast(a[i], bg) >= 4.5:
            continue
        if not dark and 1 <= i <= 6:
            a[i] = editor[i - 1]
        else:
            a[i] = readable(a[i], bg, saturate=1.0 if dark else 1.2)
    return a


def selection_gray(p, dark):
    """Selected list rows and selected code get a neutral gray, so colored
    text (git status, syntax) keeps its contrast on them."""
    return mix(p["background"], p["foreground"], 0.12 if dark else 0.08)


def hues(p, dark):
    """Red, green, yellow, blue, magenta and cyan for colored text. Dark mode
    uses the bright (Apple dark-appearance) hues, light mode the normal ones,
    which read better on white. Each is adjusted just enough to stay
    readable, even on a selected row. This mostly darkens the light palette,
    which is too pale on white; it gets a saturation boost so the darker
    colors stay vivid."""
    a = p["ansi"]
    selected = selection_gray(p, dark)
    if dark:
        return [readable(c, selected) for c in a[9:15]]
    return [readable(c, selected, saturate=1.2) for c in a[1:7]]


def accent_color(p, dark):
    """Filled accent (buttons, badges, menu selection). White on the bright
    dark-mode blue is too faint, so dark mode puts dark text on it; light
    mode darkens the blue under white text instead."""
    return p["ansi"][12] if dark else readable(p["ansi"][12], "#ffffff")


def build(name, p, grays, dark):
    a = p["ansi"]
    bg, fg = p["background"], p["foreground"]
    gray, gray2, gray3, gray4, gray5, gray6 = grays

    selection = selection_gray(p, dark)
    red, green, yellow, blue, magenta, cyan = hues(p, dark)
    comment = readable(p.get("comment", a[7]), selection)
    # Cyan is too faint on white for something as common as types; in light
    # mode types take blue and functions, which are rarer, take cyan.
    type_color, func_color = (cyan, blue) if dark else (blue, cyan)
    muted = gray if dark else a[8]

    accent = accent_color(p, dark)
    on_accent = bg if dark else "#ffffff"
    accent_hover = a[4] if dark else mix(accent, "#000000", 0.15)

    border = gray4
    chrome = bg
    hover = alpha(fg, 0x10)

    # Code shows through the diff, find and bracket-match fills. Each fill is
    # as strong as it can be, up to its designed alpha, while every code
    # color on it stays readable; it uses the hue at full saturation so it
    # still shows. Changed text is tinted on top of its changed line (and
    # added or removed lines get both), so the line leaves room for it.
    code = [fg, comment, red, green, yellow, blue, magenta, cyan]

    def diff_fills(hue):
        line = tint(vivid(hue), bg, code, 0x18, layers=2)
        return line, tint(vivid(hue), over(line, bg), code, 0x30)

    inserted_line, inserted_text = diff_fills(green)
    removed_line, removed_text = diff_fills(red)

    colors = {
        "foreground": fg,
        "focusBorder": blue,
        "selection.background": p["selection_bg"],
        "descriptionForeground": muted,
        "errorForeground": red,
        "icon.foreground": muted,
        "widget.border": border,
        "widget.shadow": "#00000040" if dark else "#00000020",
        "textLink.foreground": blue,
        "textLink.activeForeground": blue,
        "textPreformat.foreground": cyan,
        "textBlockQuote.background": gray6 if not dark else gray5,
        "textCodeBlock.background": gray6 if not dark else gray5,
        "scrollbarSlider.background": "#00000000",
        "scrollbarSlider.hoverBackground": alpha(gray, 0x70),
        "scrollbarSlider.activeBackground": alpha(gray, 0x90),

        # Window chrome
        "titleBar.activeBackground": chrome,
        "titleBar.activeForeground": fg,
        "titleBar.inactiveBackground": chrome,
        "titleBar.inactiveForeground": muted,
        "titleBar.border": border,
        "activityBar.background": chrome,
        "activityBar.foreground": fg,
        "activityBar.inactiveForeground": muted,
        "activityBar.border": border,
        "activityBar.activeBorder": blue,
        "activityBarBadge.background": accent,
        "activityBarBadge.foreground": on_accent,
        "sideBar.background": chrome,
        "sideBar.foreground": fg,
        "sideBar.border": border,
        "sideBarTitle.foreground": muted,
        "sideBarSectionHeader.background": chrome,
        "sideBarSectionHeader.foreground": fg,
        "sideBarSectionHeader.border": border,
        "statusBar.background": chrome,
        "statusBar.foreground": muted,
        "statusBar.border": border,
        "statusBar.noFolderBackground": chrome,
        "statusBar.debuggingBackground": alpha(yellow, 0x40),
        "statusBar.debuggingForeground": fg,
        "statusBarItem.hoverBackground": hover,
        "statusBarItem.remoteBackground": accent,
        "statusBarItem.remoteForeground": on_accent,
        "panel.background": bg,
        "panel.border": border,
        "panelTitle.activeForeground": fg,
        "panelTitle.inactiveForeground": muted,
        "panelTitle.activeBorder": blue,

        # Tabs
        "editorGroupHeader.tabsBackground": chrome,
        "editorGroupHeader.tabsBorder": border,
        "editorGroup.border": border,
        "tab.activeBackground": bg,
        "tab.activeForeground": fg,
        "tab.activeBorderTop": blue,
        "tab.inactiveBackground": chrome,
        "tab.inactiveForeground": muted,
        "tab.border": border,
        "tab.hoverBackground": hover,
        "breadcrumb.foreground": muted,
        "breadcrumb.focusForeground": fg,

        # Lists
        "list.activeSelectionBackground": selection,
        "list.activeSelectionForeground": fg,
        "list.inactiveSelectionBackground": alpha(selection, 0x80),
        "list.hoverBackground": hover,
        "list.focusOutline": blue,
        "list.highlightForeground": blue,
        "list.errorForeground": red,
        "list.warningForeground": yellow,
        "tree.indentGuidesStroke": gray3,

        # Inputs, buttons, dropdowns
        "input.background": gray5 if dark else "#ffffff",
        "input.foreground": fg,
        "input.border": border,
        "input.placeholderForeground": muted,
        "inputOption.activeBorder": blue,
        "inputOption.activeBackground": alpha(blue, 0x30),
        "dropdown.background": gray5 if dark else "#ffffff",
        "dropdown.border": border,
        "button.background": accent,
        "button.foreground": on_accent,
        "button.hoverBackground": accent_hover,
        "button.secondaryBackground": gray4 if dark else gray5,
        "button.secondaryForeground": fg,
        "badge.background": accent,
        "badge.foreground": on_accent,
        "progressBar.background": blue,
        "checkbox.background": gray5 if dark else "#ffffff",
        "checkbox.border": border,

        # Widgets
        "editorWidget.background": gray6 if dark else "#ffffff",
        "editorWidget.border": border,
        "editorHoverWidget.background": gray6 if dark else "#ffffff",
        "editorHoverWidget.border": border,
        "editorSuggestWidget.background": gray6 if dark else "#ffffff",
        "editorSuggestWidget.border": border,
        "editorSuggestWidget.selectedBackground": selection,
        "editorSuggestWidget.highlightForeground": blue,
        "quickInput.background": gray6 if dark else "#ffffff",
        "pickerGroup.foreground": blue,
        "pickerGroup.border": border,
        "menu.background": gray6 if dark else "#ffffff",
        "menu.selectionBackground": accent,
        "menu.selectionForeground": on_accent,
        "notifications.background": gray6 if dark else "#ffffff",
        "notifications.border": border,

        # Editor
        "editor.background": bg,
        "editor.foreground": fg,
        "editorCursor.foreground": p["cursor"],
        "editorCursor.background": p["cursor_text"],
        "editor.selectionBackground": selection,
        "editor.inactiveSelectionBackground": alpha(selection, 0x80),
        "editor.selectionHighlightBackground": alpha(selection, 0x80),
        "editor.wordHighlightBackground": alpha(selection, 0x60),
        "editor.wordHighlightStrongBackground": alpha(selection, 0x90),
        # Faint fill plus outline: the match stands out, the code stays readable.
        "editor.findMatchBackground": tint(vivid(yellow), bg, code, 0x28),
        "editor.findMatchBorder": yellow,
        "editor.findMatchHighlightBackground": tint(vivid(yellow), bg, code, 0x18),
        "editor.findMatchHighlightBorder": alpha(yellow, 0x80),
        "editor.lineHighlightBackground": alpha(fg, 0x0a),
        "editor.lineHighlightBorder": "#00000000",
        "editorLineNumber.foreground": gray2,
        "editorLineNumber.activeForeground": fg,
        "editorIndentGuide.background1": gray4 if dark else gray5,
        "editorIndentGuide.activeBackground1": gray2 if dark else gray3,
        "editorWhitespace.foreground": gray3 if dark else gray4,
        "editorRuler.foreground": gray4 if dark else gray5,
        "editorBracketMatch.background": tint(vivid(blue), bg, code, 0x30),
        "editorBracketMatch.border": "#00000000",
        "editorBracketHighlight.foreground1": blue,
        "editorBracketHighlight.foreground2": magenta,
        "editorBracketHighlight.foreground3": cyan,
        "editorBracketHighlight.foreground4": green,
        "editorBracketHighlight.foreground5": yellow,
        "editorBracketHighlight.foreground6": red,
        "editorError.foreground": red,
        "editorWarning.foreground": yellow,
        "editorInfo.foreground": blue,
        "editorHint.foreground": green,
        "editorLink.activeForeground": blue,
        "editorGutter.addedBackground": green,
        "editorGutter.modifiedBackground": blue,
        "editorGutter.deletedBackground": red,
        "editorOverviewRuler.border": "#00000000",
        "editorOverviewRuler.errorForeground": red,
        "editorOverviewRuler.warningForeground": yellow,
        "editorOverviewRuler.findMatchForeground": yellow,

        # Diff
        "diffEditor.insertedTextBackground": inserted_text,
        "diffEditor.removedTextBackground": removed_text,
        "diffEditor.insertedLineBackground": inserted_line,
        "diffEditor.removedLineBackground": removed_line,

        # Git
        "gitDecoration.addedResourceForeground": green,
        "gitDecoration.untrackedResourceForeground": green,
        "gitDecoration.modifiedResourceForeground": blue,
        "gitDecoration.deletedResourceForeground": red,
        "gitDecoration.conflictingResourceForeground": magenta,
        "gitDecoration.ignoredResourceForeground": muted,

        # Terminal: the same colors as the Ghostty theme
        "terminal.background": bg,
        "terminal.foreground": fg,
        "terminalCursor.foreground": p["cursor"],
        "terminalCursor.background": p["cursor_text"],
        "terminal.selectionBackground": p["selection_bg"],
        "terminal.selectionForeground": p["selection_fg"],
    }
    for n, c in zip(ANSI_NAMES, terminal_ansi(p)):
        colors[f"terminal.ansi{n}"] = c

    def rule(scope, color=None, style=None):
        s = {}
        if color:
            s["foreground"] = color
        if style is not None:
            s["fontStyle"] = style
        return {"scope": scope, "settings": s}

    token_colors = [
        rule(["comment", "punctuation.definition.comment"], comment),
        rule(["keyword", "storage.type", "storage.modifier", "keyword.control"], magenta),
        rule(["keyword.operator"], fg),
        rule(["string", "punctuation.definition.string"], fg),
        rule(["constant.character.escape", "string.regexp"], cyan),
        rule(["constant.numeric", "constant.language", "constant.language.boolean"], red),
        rule(["constant.other", "variable.other.constant", "support.constant"], yellow),
        rule(["entity.name.function", "support.function", "meta.function-call"], func_color),
        rule(["entity.name.type", "entity.name.class", "support.type", "support.class",
              "entity.other.inherited-class"], type_color),
        rule(["variable", "variable.parameter"], fg),
        rule(["variable.language"], magenta),
        rule(["variable.other.property", "variable.other.object.property", "support.variable.property",
              "meta.object-literal.key", "support.type.property-name"], green),
        rule(["entity.name.tag"], blue),
        rule(["entity.other.attribute-name"], green),
        rule(["entity.name.section", "markup.heading"], blue, "bold"),
        rule(["markup.bold"], None, "bold"),
        rule(["markup.italic"], None, "italic"),
        rule(["markup.underline.link", "string.other.link"], cyan),
        rule(["markup.inline.raw", "markup.fenced_code"], cyan),
        rule(["markup.inserted"], green),
        rule(["markup.deleted"], red),
        rule(["markup.changed"], blue),
        rule(["invalid"], red),
    ]

    semantic = {
        "keyword": magenta,
        "string": fg,
        "number": red,
        "function": func_color,
        "method": func_color,
        "type": type_color,
        "class": type_color,
        "interface": type_color,
        "enum": type_color,
        "enumMember": yellow,
        "property": green,
        "parameter": fg,
        "variable": fg,
        "variable.readonly": yellow,
        "*.defaultLibrary": type_color,
        "comment": comment,
    }

    colors = {k: v for k, v in colors.items() if v is not None}

    return {
        "$schema": "vscode://schemas/color-theme",
        "name": name,
        "type": "dark" if dark else "light",
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": token_colors,
        "semanticTokenColors": semantic,
    }


def ghostty(p):
    lines = [f"palette = {i}={c}" for i, c in enumerate(terminal_ansi(p))]
    lines += [
        f"background = {p['background']}",
        f"foreground = {p['foreground']}",
        f"cursor-color = {p['cursor']}",
        f"cursor-text = {p['cursor_text']}",
        f"selection-background = {p['selection_bg']}",
    ]
    if p["selection_fg"]:
        lines.append(f"selection-foreground = {p['selection_fg']}")
    return "\n".join(lines) + "\n"


def herdr(p, grays, dark):
    """herdr's colors for one appearance: every token of its palette, with
    the VS Code theme's grays, accent and hues."""
    fg = p["foreground"]
    gray, gray2, gray3, gray4, gray5, gray6 = grays
    red, green, yellow, blue, magenta, cyan = hues(p, dark)
    # The current row takes the terminal's selection color; the neutral
    # selection gray is too faint to mark it on a translucent window.
    row = p["selection_bg"]
    # Secondary text: the VS Code theme's muted gray, lightened where it
    # isn't readable on the current row.
    muted = gray if dark else p["ansi"][8]
    if contrast(muted, row) < 4.5:
        muted = readable(muted, row)
    # The active tab's label is surface_dim on the accent (panel_bg is reset),
    # so the accent is adjusted until that label is readable.
    accent = readable(accent_color(p, dark), gray4)
    return {
        "text": fg,
        "subtext0": muted,
        "overlay0": muted,
        "overlay1": muted,
        "mauve": muted,
        "sidebar_bg": "reset",
        "panel_bg": "reset",
        "active_row_bg": row,
        "selection_bg": row,
        "surface0": gray5,
        "surface1": gray3,
        "surface_dim": gray4,
        "accent": accent,
        "blue": blue,
        "green": green,
        "yellow": yellow,
        "red": red,
        "teal": cyan,
        "peach": yellow,
    }


# What herdr uses each token for, noted once, on the light block.
HERDR_NOTES = {
    "subtext0": "secondary text: headers, hints, branch names",
    "sidebar_bg": "keep the window's translucent background",
    "panel_bg": "tab bar, status line, popups: translucent too",
    "active_row_bg": "current space/agent: the terminal's selection",
    "selection_bg": "cursor row while navigating",
    "surface1": "dragged row, search matches, popup dividers",
    "surface_dim": "divider lines; text on accent, as panel_bg is reset",
    "accent": "active tab, key hints",
    "green": "idle",
    "yellow": "working",
    "red": "blocked",
    "teal": "done",
    "peach": "interrupted",
}


def herdr_toml(light, dark):
    lines = [
        "# Clear Light and Clear Dark for herdr (https://herdr.dev), generated by",
        "# clear-theme's build.py. herdr switches between them with the terminal's",
        "# appearance. Every color is set, so nothing falls back to the \"terminal\"",
        "# base theme, which assumes a dark background.",
        "[theme]",
        'name = "terminal"',
        "auto_switch = true",
    ]
    for mode, colors in (("light", light), ("dark", dark)):
        lines += ["", f"[theme.custom.{mode}]"]
        for key, color in colors.items():
            line = f'{key} = "{color}"'
            note = HERDR_NOTES.get(key) if mode == "light" else None
            lines.append(f"{line:<25}  # {note}" if note else line)
    return "\n".join(lines) + "\n"


def main():
    out = Path(__file__).parent / "themes"
    out.mkdir(exist_ok=True)
    for name, pal, grays, dark, fname in [
        ("Apple System Colors", DARK, DARK_GRAYS, True, "apple-system-colors-dark.json"),
        ("Apple System Colors Light", LIGHT, LIGHT_GRAYS, False, "apple-system-colors-light.json"),
        ("Clear Dark", CLEAR_DARK, CLEAR_DARK_GRAYS, True, "clear-dark.json"),
        ("Clear Light", CLEAR_LIGHT, CLEAR_LIGHT_GRAYS, False, "clear-light.json"),
    ]:
        (out / fname).write_text(json.dumps(build(name, pal, grays, dark), indent=2) + "\n")
        print(f"wrote themes/{fname}")

    # Ghostty already ships Apple System Colors; only the Clear themes are generated.
    gh = Path(__file__).parent / "ghostty"
    gh.mkdir(exist_ok=True)
    for name, pal in [("Clear Dark", CLEAR_DARK), ("Clear Light", CLEAR_LIGHT)]:
        (gh / name).write_text(ghostty(pal))
        print(f"wrote ghostty/{name}")

    hd = Path(__file__).parent / "herdr"
    hd.mkdir(exist_ok=True)
    (hd / "clear.toml").write_text(herdr_toml(
        herdr(CLEAR_LIGHT, CLEAR_LIGHT_GRAYS, False),
        herdr(CLEAR_DARK, CLEAR_DARK_GRAYS, True),
    ))
    print("wrote herdr/clear.toml")


if __name__ == "__main__":
    main()
