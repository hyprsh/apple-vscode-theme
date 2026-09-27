# Apple System Colors for VS Code

Light and dark VS Code themes built from Apple terminal palettes, so the editor
and the integrated terminal match your terminal exactly:

- **Apple System Colors** / **Apple System Colors Light**: Ghostty's bundled
  themes of the same name.
- **Clear Dark** / **Clear Light**: the macOS Terminal profiles of the same name.
  Terminal renders them slightly translucent; here the background is opaque.

## Installation

The theme isn't on the VS Code Marketplace. Install it by cloning the repo into
your VS Code extensions folder:

```sh
git clone https://github.com/hyprsh/apple-vscode-theme.git \
  ~/.vscode/extensions/hyprsh.apple-vscode-theme-0.1.0
```

Then restart VS Code (or run **Developer: Reload Window**) and pick a theme with
**Preferences: Color Theme** (<kbd>Cmd</kbd>+<kbd>K</kbd> <kbd>Cmd</kbd>+<kbd>T</kbd>).

On Windows the extensions folder is `%USERPROFILE%\.vscode\extensions`. For
VS Code Insiders use `~/.vscode-insiders/extensions`, for VSCodium
`~/.vscode-oss/extensions`, and for Cursor `~/.cursor/extensions`.

To update:

```sh
git -C ~/.vscode/extensions/hyprsh.apple-vscode-theme-0.1.0 pull
```

To uninstall, delete that folder and reload VS Code.

## Usage

To switch between light and dark automatically with the system appearance,
add this to your `settings.json`:

```jsonc
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Apple System Colors",
"workbench.preferredLightColorTheme": "Apple System Colors Light"
```

For the Clear themes, use `"Clear Dark"` and `"Clear Light"` instead.

If the theme doesn't switch, remove `"window.systemColorTheme"` from your
settings; any value other than the default stops VS Code from seeing the
system appearance.

## Development

The theme JSON is generated; edit `palettes.py` or `build.py`, then:

```sh
python3 build.py
```

To work on it, symlink your clone into the extensions folder instead and reload VS Code:

```sh
ln -s "$PWD" ~/.vscode/extensions/hyprsh.apple-vscode-theme-0.1.0
```
