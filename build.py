"""Generate the VS Code color themes from the palettes in palettes.py.

Run: python3 build.py
"""
import json
from pathlib import Path

from palettes import (
    CLEAR_DARK, CLEAR_DARK_GRAYS, CLEAR_LIGHT, CLEAR_LIGHT_GRAYS,
    DARK, DARK_GRAYS, LIGHT, LIGHT_GRAYS,
)

ANSI_NAMES = [
    "Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White",
    "BrightBlack", "BrightRed", "BrightGreen", "BrightYellow",
    "BrightBlue", "BrightMagenta", "BrightCyan", "BrightWhite",
]


def alpha(color, a):
    return f"{color}{a:02x}"


def build(name, p, grays, dark):
    a = p["ansi"]
    bg, fg = p["background"], p["foreground"]
    gray, gray2, gray3, gray4, gray5, gray6 = grays

    # Dark mode uses the bright (Apple dark-appearance) hues, light mode the
    # normal ones, which read better on white.
    hue = a[9:15] if dark else a[1:7]
    red, green, yellow, blue, magenta, cyan = hue
    comment = p.get("comment", a[7])
    muted = gray if dark else a[8]

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
        "scrollbarSlider.background": alpha(gray, 0x40),
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
        "activityBarBadge.background": blue,
        "activityBarBadge.foreground": "#ffffff",
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
        "statusBarItem.remoteBackground": blue,
        "statusBarItem.remoteForeground": "#ffffff",
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
        "list.activeSelectionBackground": p["selection_bg"],
        "list.activeSelectionForeground": p["selection_fg"],
        "list.inactiveSelectionBackground": alpha(p["selection_bg"], 0x80),
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
        "button.background": a[12],
        "button.foreground": "#ffffff",
        "button.hoverBackground": a[4],
        "button.secondaryBackground": gray4 if dark else gray5,
        "button.secondaryForeground": fg,
        "badge.background": blue,
        "badge.foreground": "#ffffff",
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
        "editorSuggestWidget.selectedBackground": p["selection_bg"],
        "editorSuggestWidget.highlightForeground": blue,
        "quickInput.background": gray6 if dark else "#ffffff",
        "pickerGroup.foreground": blue,
        "pickerGroup.border": border,
        "menu.background": gray6 if dark else "#ffffff",
        "menu.selectionBackground": a[12],
        "menu.selectionForeground": "#ffffff",
        "notifications.background": gray6 if dark else "#ffffff",
        "notifications.border": border,

        # Editor
        "editor.background": bg,
        "editor.foreground": fg,
        "editorCursor.foreground": p["cursor"],
        "editorCursor.background": p["cursor_text"],
        "editor.selectionBackground": p["selection_bg"],
        "editor.selectionForeground": p["selection_fg"],
        "editor.inactiveSelectionBackground": alpha(p["selection_bg"], 0x80),
        "editor.selectionHighlightBackground": alpha(p["selection_bg"], 0x60),
        "editor.wordHighlightBackground": alpha(p["selection_bg"], 0x50),
        "editor.wordHighlightStrongBackground": alpha(p["selection_bg"], 0x70),
        "editor.findMatchBackground": alpha(yellow, 0x80),
        "editor.findMatchHighlightBackground": alpha(yellow, 0x40),
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
        rule(["string", "punctuation.definition.string"], red),
        rule(["constant.character.escape", "string.regexp"], cyan),
        rule(["constant.numeric", "constant.language", "constant.language.boolean"], yellow),
        rule(["constant.other", "variable.other.constant", "support.constant"], yellow),
        rule(["entity.name.function", "support.function", "meta.function-call"], blue),
        rule(["entity.name.type", "entity.name.class", "support.type", "support.class",
              "entity.other.inherited-class"], cyan),
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
        "string": red,
        "number": yellow,
        "function": blue,
        "method": blue,
        "type": cyan,
        "class": cyan,
        "interface": cyan,
        "enum": cyan,
        "enumMember": yellow,
        "property": green,
        "parameter": fg,
        "variable": fg,
        "variable.readonly": yellow,
        "*.defaultLibrary": cyan,
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


if __name__ == "__main__":
    main()
