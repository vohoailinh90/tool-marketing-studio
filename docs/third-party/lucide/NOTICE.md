# Third-Party Notices

`scripts/figures/icons/*.svg` are icons from **Lucide** (`lucide-static`), copied byte for byte and used under its licence (`LICENSE` in this folder: ISC, with the MIT terms of the Feather project for the icons derived from it).

**Original work:** https://github.com/lucide-icons/lucide
**Version:** see `scripts/figures/icons/index.json` (`version`)
**Used for:** the pictogram on each card or actor of a System Design figure (`scripts/figures/svg.py`, `scripts/figures/drawio.py`). Each file's sha256 is in `scripts/figures/icons/index.json`; `python3 -m scripts.figures icons --verify` and `tests/test_figures.py` fail when a file differs, is missing or is not listed.

To update: copy the new `<name>.svg` files from the package over the old ones, copy its `LICENSE` here, then fix `version` and the `sha256` values in `index.json` (keep each `gloss`). A name is added by adding its file and an `index.json` entry with a short meaning to choose it by.
