"""Generate the VS Code color themes from the palettes in palettes.py.

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


def build(name, p, grays, dark):
    a = p["ansi"]
    bg, fg = p["background"], p["foreground"]
    gray, gray2, gray3, gray4, gray5, gray6 = grays

    # Dark mode uses the bright (Apple dark-appearance) hues, light mode the
    # normal ones, which read better on white.
    hue = a[9:15] if dark else a[1:7]
    comment = p.get("comment", a[7])
    # Selected list rows and selected code get a neutral gray, so colored text
    # (git status, syntax) keeps its contrast on them.
    selection = mix(bg, fg, 0.12 if dark else 0.08)
    # Adjust each hue just enough to stay readable, even on a selected row.
    # This mostly darkens the light palette, which is too pale on white; it
    # gets a saturation boost so the darker colors stay vivid.
    if dark:
        hue = [readable(c, selection) for c in hue]
    else:
        hue = [readable(c, bg, saturate=1.2) for c in hue]
        comment = readable(comment, bg)
    red, green, yellow, blue, magenta, cyan = hue
    # Cyan is too faint on white for something as common as types; in light
    # mode types take blue and functions, which are rarer, take cyan.
    type_color, func_color = (cyan, blue) if dark else (blue, cyan)
    muted = gray if dark else a[8]

    # Filled accent (buttons, badges, menu selection). White on the bright
    # dark-mode blue is too faint, so dark mode puts dark text on it; light
    # mode darkens the blue under white text instead.
    accent = a[12] if dark else readable(a[12], "#ffffff")
    on_accent = bg if dark else "#ffffff"
    accent_hover = a[4] if dark else mix(accent, "#000000", 0.15)

    border = gray4
    chrome = bg
    hover = alpha(fg, 0x10)

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
        "tree.indentGuidesStroke": gray3 if dark else gray3,

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
        "editor.findMatchBackground": alpha(yellow, 0x28),
        "editor.findMatchBorder": yellow,
        "editor.findMatchHighlightBackground": alpha(yellow, 0x18),
        "editor.findMatchHighlightBorder": alpha(yellow, 0x80),
        "editor.lineHighlightBackground": alpha(fg, 0x0a),
        "editor.lineHighlightBorder": "#00000000",
        "editorLineNumber.foreground": gray2 if dark else gray2,
        "editorLineNumber.activeForeground": fg,
        "editorIndentGuide.background1": gray4 if dark else gray5,
        "editorIndentGuide.activeBackground1": gray2 if dark else gray3,
        "editorWhitespace.foreground": gray3 if dark else gray4,
        "editorRuler.foreground": gray4 if dark else gray5,
        "editorBracketMatch.background": alpha(blue, 0x30),
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
        "diffEditor.insertedTextBackground": alpha(green, 0x30),
        "diffEditor.removedTextBackground": alpha(red, 0x30),
        "diffEditor.insertedLineBackground": alpha(green, 0x18),
        "diffEditor.removedLineBackground": alpha(red, 0x18),

        # Git
        "gitDecoration.addedResourceForeground": green,
        "gitDecoration.untrackedResourceForeground": green,
        "gitDecoration.modifiedResourceForeground": blue,
        "gitDecoration.deletedResourceForeground": red,
        "gitDecoration.conflictingResourceForeground": magenta,
        "gitDecoration.ignoredResourceForeground": muted,

        # Terminal: exact Ghostty colors
        "terminal.background": bg,
        "terminal.foreground": fg,
        "terminalCursor.foreground": p["cursor"],
        "terminalCursor.background": p["cursor_text"],
        "terminal.selectionBackground": p["selection_bg"],
        "terminal.selectionForeground": p["selection_fg"],
    }
    for i, n in enumerate(ANSI_NAMES):
        colors[f"terminal.ansi{n}"] = a[i]

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
    lines = [f"palette = {i}={c}" for i, c in enumerate(p["ansi"])]
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


if __name__ == "__main__":
    main()
