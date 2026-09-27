# Apple System Colors for VS Code

Light and dark VS Code themes built from the same palettes as Ghostty's
`Apple System Colors` and `Apple System Colors Light` themes, so the editor and
the integrated terminal match Ghostty exactly.

## Usage

```jsonc
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Apple System Colors",
"workbench.preferredLightColorTheme": "Apple System Colors Light"
```

## Development

The theme JSON is generated; edit `palettes.py` or `build.py`, then:

```sh
python3 build.py
```

To try it locally, symlink the repo into your extensions folder and reload VS Code:

```sh
ln -s "$PWD" ~/.vscode/extensions/hyprsh.apple-vscode-theme-0.1.0
```
