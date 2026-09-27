# Clear Theme

The macOS Terminal **Clear Dark** and **Clear Light** profiles for VS Code and
Ghostty, so your editor and terminal look just like Terminal.app.

The colors are decoded straight from Terminal's own profiles. Terminal draws
them slightly translucent; in VS Code the background is opaque.

Also included, as a secondary pair: **Apple System Colors** and **Apple System
Colors Light**, matching Ghostty's bundled themes of the same name.

## VS Code

### Installation

The theme isn't on the VS Code Marketplace. Install it by cloning the repo into
your VS Code extensions folder:

```sh
git clone https://github.com/hyprsh/clear-theme.git \
  ~/.vscode/extensions/hyprsh.clear-theme-0.1.0
```

Then restart VS Code (or run **Developer: Reload Window**) and pick a theme with
**Preferences: Color Theme** (<kbd>Cmd</kbd>+<kbd>K</kbd> <kbd>Cmd</kbd>+<kbd>T</kbd>).

On Windows the extensions folder is `%USERPROFILE%\.vscode\extensions`. For
VS Code Insiders use `~/.vscode-insiders/extensions`, for VSCodium
`~/.vscode-oss/extensions`, and for Cursor `~/.cursor/extensions`.

To update:

```sh
git -C ~/.vscode/extensions/hyprsh.clear-theme-0.1.0 pull
```

To uninstall, delete that folder and reload VS Code.

### Usage

To switch between light and dark automatically with the system appearance,
add this to your `settings.json`:

```jsonc
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Clear Dark",
"workbench.preferredLightColorTheme": "Clear Light"
```

For the secondary themes, use `"Apple System Colors"` and
`"Apple System Colors Light"` instead.

If the theme doesn't switch, remove `"window.systemColorTheme"` from your
settings; any value other than the default stops VS Code from seeing the
system appearance.

## Ghostty

Copy the theme files from the `ghostty` folder into Ghostty's themes folder:

```sh
mkdir -p ~/.config/ghostty/themes
cp ghostty/* ~/.config/ghostty/themes/
```

Then set the theme in your Ghostty config:

```
theme = light:Clear Light,dark:Clear Dark
```

For a Terminal-like translucent background, add:

```
background-opacity = 0.95
background-blur-radius = 20
```

Ghostty already ships **Apple System Colors** and **Apple System Colors Light**,
so there are no files for those here.

## Font (optional)

To match macOS Terminal's font too, use **SF Mono Terminal**, the SF Mono
variant Terminal ships inside its app bundle. It isn't installed for other apps,
and copying the files into `~/Library/Fonts` isn't enough; install them with
Font Book:

```sh
cp /System/Applications/Utilities/Terminal.app/Contents/Resources/Fonts/SFMono*-Terminal.ttf /tmp/
open -a "Font Book" /tmp/SFMono-Terminal.ttf /tmp/SFMonoItalic-Terminal.ttf
```

Click **Install** in Font Book, then check that "SF Mono Terminal" appears in
its font list.

VS Code `settings.json` (the integrated terminal inherits the editor font):

```jsonc
"editor.fontFamily": "'SF Mono Terminal', ui-monospace, Menlo, monospace",
"editor.fontSize": 16,
"editor.lineHeight": 29,
"terminal.integrated.fontSize": 16,
"terminal.integrated.lineHeight": 1.5
```

Ghostty config:

```
font-family = SF Mono Terminal
font-size = 16
adjust-cell-height = 50%
```

This gives the editor and both terminals the same roomier line spacing. The
editor's `lineHeight` is in pixels because it multiplies the font size, while
the terminals multiply the font's taller natural line height. For the tighter
spacing Terminal.app uses, drop `adjust-cell-height` and the terminal
`lineHeight`, and set `editor.lineHeight` to 1.2.

Quit and reopen VS Code afterwards; a window reload doesn't pick up new fonts.
The installed copies don't update with macOS, so repeat the install after a
major update if you want Terminal's latest version.

## Development

The VS Code and Ghostty themes are generated from `palettes.py`; edit it or
`build.py`, then:

```sh
python3 build.py
```

To work on it, symlink your clone into the extensions folder and reload VS Code:

```sh
ln -s "$PWD" ~/.vscode/extensions/hyprsh.clear-theme-0.1.0
```

## License

[MIT](LICENSE)
