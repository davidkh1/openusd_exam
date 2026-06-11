"""Regenerate the book's tool-rendered figures from the chapter listings.

Figures are never one-off: this script re-extracts the exact listings printed
in the book (same extraction as tests/test_examples.py), adds a display-color
wrapper, and renders with usdrecord (NVIDIA prebuilt binaries, Storm).

Run:  .venv/bin/python tools/regen_figures.py
Requires: ~/opt/openusd/usd_root (set_usd_env.sh is sourced per render call).
"""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
FIGURES = REPO / 'usd_exam_companion/figures'
USD_ENV = pathlib.Path.home() / 'opt/openusd/usd_root/scripts/set_usd_env.sh'

spec = importlib.util.spec_from_file_location(
    'test_examples', REPO / 'tests/test_examples.py')
test_examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_examples)

OFFSETS_WRAPPER = """\
#usda 1.0
(
    subLayers = [@./shot_offsets.usda@]
)
over "Shot" {
    over "BallA" {
        color3f[] primvars:displayColor = [(0.46, 0.72, 0.0)]
    }
    over "BallB" {
        color3f[] primvars:displayColor = [(0.12, 0.44, 0.92)]
    }
    over "BallC" {
        color3f[] primvars:displayColor = [(0.85, 0.45, 0.05)]
    }
}
"""

# Answer-key figure for Q2: a proxy sphere parented under /World/Chair picks
# up the composed translate; gray markers sit at the four answer options.
CHAIR_WRAPPER = """\
#usda 1.0
(
    subLayers = [@./scene.usda@]
)
over "World" {
    over "Chair" {
        def Sphere "Proxy" {
            double radius = 0.16
            color3f[] primvars:displayColor = [(0.46, 0.72, 0.0)]
        }
    }
    def Sphere "MarkA" {
        double radius = 0.06
        color3f[] primvars:displayColor = [(0.6, 0.6, 0.6)]
    }
    def Sphere "MarkB" {
        double radius = 0.06
        color3f[] primvars:displayColor = [(0.6, 0.6, 0.6)]
        double3 xformOp:translate = (1, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
    def Sphere "MarkD" {
        double radius = 0.06
        color3f[] primvars:displayColor = [(0.6, 0.6, 0.6)]
        double3 xformOp:translate = (1, 1, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
}
"""

# Answer-key figure for Q13: same stage, but with a 3/4 camera so the cube
# reads as an object instead of filling the frame.
Q13_CAM_WRAPPER = """\
#usda 1.0
(
    subLayers = [@./main.usda@]
)
def Xform "Cams" {
    def Camera "Cam" {
        float focalLength = 35
        double3 xformOp:translate = (4.3, 3.1, 5.9)
        double xformOp:rotateY = 36
        double xformOp:rotateX = -22
        uniform token[] xformOpOrder = [
            "xformOp:translate", "xformOp:rotateY", "xformOp:rotateX"]
    }
}
"""


def write_listings(root):
    for tex_name, files in test_examples.CHAPTER_LISTINGS.items():
        listings = test_examples.LISTING_RE.findall(
            (test_examples.CHAPTERS / tex_name).read_text())
        assert len(listings) == len(files), f'mapping out of date for {tex_name}'
        for rel, body in zip(files, listings):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)


def usdrecord(args):
    cmd = f'source {USD_ENV} >/dev/null 2>&1 && usdrecord ' + ' '.join(args)
    subprocess.run(['bash', '-c', cmd], check=True)


def main():
    FIGURES.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        write_listings(root)
        scene_dir = root / 'c10'
        (scene_dir / 'offsets_wrapper.usda').write_text(OFFSETS_WRAPPER)

        # Layer-offset scene at stage time 12 (the time discussed in the text).
        usdrecord(['--frames 12:12', '--imageWidth 1200', '--complexity high',
                   str(scene_dir / 'offsets_wrapper.usda'),
                   str(scene_dir / 'offsets_t12_####.png')])
        rendered = scene_dir / 'offsets_t12_0012.png'
        rendered.replace(FIGURES / 'c10_offsets_t12.png')

        # The Q13 variant-trap cube (stays red despite loftedColor = blue).
        (root / 'q13/cam_wrapper.usda').write_text(Q13_CAM_WRAPPER)
        usdrecord(['--imageWidth 900', '--complexity high',
                   '--camera /Cams/Cam',
                   str(root / 'q13/cam_wrapper.usda'),
                   str(root / 'q13/cube.png')])
        (root / 'q13/cube.png').replace(FIGURES / 'q13_cube_red.png')

        # Q2 answer visualization: where does the chair land?
        (root / 'q02/chair_wrapper.usda').write_text(CHAIR_WRAPPER)
        usdrecord(['--imageWidth 900', '--complexity high',
                   str(root / 'q02/chair_wrapper.usda'),
                   str(root / 'q02/chair_options.png')])
        (root / 'q02/chair_options.png').replace(FIGURES / 'q02_chair_options.png')

        # Content Aggregation: the PointInstancer scatter (invisibleIds gap).
        usdrecord(['--imageWidth 1100', '--complexity high',
                   str(root / 'c11/scatter.usda'),
                   str(root / 'c11/scatter.png')])
        (root / 'c11/scatter.png').replace(FIGURES / 'c11_scatter.png')

        # Visualization: one material, primvar-driven colors.
        usdrecord(['--imageWidth 1100', '--complexity high',
                   str(root / 'c17/shaded.usda'),
                   str(root / 'c17/shaded.png')])
        (root / 'c17/shaded.png').replace(FIGURES / 'c17_primvar_material.png')

        # Visualization: textured + lit + authored camera.
        from PIL import Image
        tile, n = 64, 8
        img = Image.new('RGB', (tile * n, tile * n))
        for y in range(n):
            for x in range(n):
                color = (235, 235, 230) if (x + y) % 2 else (40, 90, 160)
                img.paste(color, (x * tile, y * tile,
                                  (x + 1) * tile, (y + 1) * tile))
        img.save(root / 'c17/checker.png')
        usdrecord(['--imageWidth 1100', '--complexity high',
                   '--camera /Scene/Cam',
                   str(root / 'c17/tex_scene.usda'),
                   str(root / 'c17/tex.png')])
        (root / 'c17/tex.png').replace(FIGURES / 'c17_textured.png')

    print('wrote', FIGURES / 'c10_offsets_t12.png')
    print('wrote', FIGURES / 'q13_cube_red.png')
    print('wrote', FIGURES / 'q02_chair_options.png')
    print('wrote', FIGURES / 'c11_scatter.png')
    print('wrote', FIGURES / 'c17_primvar_material.png')


if __name__ == '__main__':
    sys.exit(main())
