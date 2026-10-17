"""Figures for the System Design lessons, drawn by script from a small spec (docs/figures.md).

A spec (JSON) says what is on the figure: cards with a pictogram, numbered steps, notes, a message sequence. `scene.py` lays it
out once, in a single 320 px column; `svg.py` writes the lesson figure and `drawio.py`, `excalidraw.py` and `moda.py` write the same
picture for the editors. Nothing here calls a model or the network. A session picks the words and the icon names; it never writes
a coordinate, a path or an SVG tag, so a figure cannot hold a script, a link or a source image.
"""
