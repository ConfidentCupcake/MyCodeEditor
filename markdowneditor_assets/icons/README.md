# MyCodeEditor — 24 new icons

48 editable SVG files: 24 normal/active pairs. Existing project icons are excluded.

Copy the contents of `markdowneditor_assets/icons/` into the matching directory in your project. These filenames are new and do not replace the existing icon set. Wiring new sidebar buttons or menu actions is a separate implementation step.

Open `preview.html` for a labeled gallery of both states. `preview.png` provides a quick overview. `manifest.json` maps filenames to features and topic numbers.

Style matches the supplied SVG sources: viewBox `0 0 24 24`, width/height 24, fill none, stroke width 2, round line caps and joins. Normal stroke `#5c6370`; active stroke `#528bff`. Each active pair differs only in color. SVGs contain only vector geometry; no embedded bitmaps, fonts, scripts, or external dependencies.

Some icons represent dialogs, menus, or future features rather than an existing sidebar panel. The package does not modify your repository or add UI controls.
