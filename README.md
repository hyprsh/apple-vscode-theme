# Apple System Colors for VS Code

Light and dark VS Code themes built from Apple terminal palettes, so the editor
and the integrated terminal match your terminal exactly:

- **Apple System Colors** / **Apple System Colors Light**: Ghostty's bundled
  themes of the same name.
- **Clear Dark** / **Clear Light**: the macOS Terminal profiles of the same name.
  Terminal renders them slightly translucent; here the background is opaque.

## Usage

```jsonc
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Apple System Colors",
"workbench.preferredLightColorTheme": "Apple System Colors Light"
```

For the Clear themes, use `"Clear Dark"` and `"Clear Light"` instead.

## Development

The theme JSON is generated; edit `palettes.py` or `build.py`, then:

```sh
python3 build.py
```

To try it locally, symlink the repo into your extensions folder and reload VS Code:

```sh
ln -s "$PWD" ~/.vscode/extensions/hyprsh.apple-vscode-theme-0.1.0
```
