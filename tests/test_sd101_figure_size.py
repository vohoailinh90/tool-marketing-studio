"""Every System Design figure declares its own size on the root element.

A figure with only a viewBox has no size of its own: a phone, an image viewer or the slide builder scales it to whatever box
it is dropped in. Codex found six figures like that in the sd-01-023..049 integration (PR #136); the owner's rule since is
that the root carries `width` and `height`, `width="320"` and the height of the viewBox.
"""
import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "system-design-101" / "vi" / "diagrams"


class FigureSizeTests(unittest.TestCase):
    def test_every_figure_root_declares_width_and_height(self):
        figures = sorted(DIAGRAMS.glob("*.svg"))
        self.assertTrue(figures, "no figure found: the folder moved or the glob is wrong")
        missing = []
        for path in figures:
            root = ET.parse(path).getroot()
            if not root.get("width") or not root.get("height"):
                missing.append(path.name)
        self.assertEqual([], missing, "figures whose <svg> lacks width or height")

    def test_declared_size_matches_the_viewbox(self):
        wrong = []
        for path in sorted(DIAGRAMS.glob("*.svg")):
            root = ET.parse(path).getroot()
            box = (root.get("viewBox") or "").split()
            if len(box) != 4:
                wrong.append(f"{path.name}: viewBox is {root.get('viewBox')!r}")
                continue
            if (root.get("width"), root.get("height")) != (box[2], box[3]):
                wrong.append(f"{path.name}: {root.get('width')}x{root.get('height')} against viewBox {' '.join(box)}")
        self.assertEqual([], wrong)


if __name__ == "__main__":
    unittest.main()
