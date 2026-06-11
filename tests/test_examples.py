"""Unit tests for the USD listings in the book.

Every lstlisting block is extracted verbatim from the chapter .tex sources,
written to disk, and exercised against real USD (usd-core). Stage-level tests
assert exactly what the book and the answer key claim. USD must stay silent:
any warning on stderr (missing defaultPrim, unresolved asset, parse error)
fails the test.

Run:  .venv/bin/python -m pytest tests/ -v
"""
import pathlib
import re

import pytest
from pxr import Sdf, Usd, UsdGeom

REPO = pathlib.Path(__file__).resolve().parent.parent
CHAPTERS = REPO / 'usd_exam_companion/chapters'

# Every lstlisting block per chapter, in document order, mapped to the file it
# represents. Extend this when a chapter gains listings — no listing ships
# untested.
CHAPTER_LISTINGS = {
    '10-composition.tex': [
        'c10/shot.usda',
        'c10/layout.usda',
        'c10/lighting.usda',
        'c10/block.usda',
        'c10/city.usda',
        'c10/payload_demo.py',
        'c10/anim.usda',
        'c10/shot_offsets.usda',
        'c10/forest_inh.usda',
        'c10/broadcast.py',
        'c10/metal.usda',
        'c10/build_shot.py',
    ],
    '11-content-aggregation.tex': [
        'c11/tree.usda',
        'c11/forest.usda',
        'c11/proxy_edit.py',
        'c11/scatter.usda',
        'c11/scatter_tweak.usda',
        'c11/add_prototype.py',
    ],
    '12-customizing-usd.tex': [
        'c12/schema.usda',
        'c12/apply_api.py',
        'c12/kinds_plugin.json',
        'c12/check_kinds.py',
    ],
    '13-data-exchange.tex': [
        'c13/asset.usda',
        'c13/roundtrip.py',
        'c13/traverse_export.py',
        'c13/box.obj',
        'c13/obj2usd.py',
        'c13/bad_export.usda',
        'c13/validate.py',
        'c13/fix_extent.py',
    ],
    '14-data-modeling.tex': [
        'c14/typed.usda',
        'c14/mesh_uv.usda',
        'c14/props.py',
        'c14/update_extent.py',
        'c14/ball_anim.usda',
        'c14/timecode.py',
        'c14/xform_common.py',
    ],
    '15-debugging.tex': [
        'c15/base.usda',
        'c15/lite.usda',
        'c15/shot.usda',
        'c15/who_wins.py',
        'c15/mute.py',
        'c15/batch.py',
        'c15/debug_flags.py',
        'c15/trace.py',
    ],
    '16-pipeline-dev.tex': [
        'c16/Chair.usda',
        'c16/contents.usda',
        'c16/hierarchy.usda',
        'c16/kinds.py',
        'c16/path_check.py',
    ],
    '17-visualization.tex': [
        'c17/shaded.usda',
        'c17/inspect_network.py',
        'c17/tex_scene.usda',
        'c17/subset.usda',
        'c17/purpose.usda',
        'c17/purpose_check.py',
        'c17/sun.usda',
    ],
    '23-mock-exam.tex': [
        'm/setA_base.usda',
        'm/setA_fix.usda',
        'm/setA_shot.usda',
        'm/propA.usda',
        'm/propB.usda',
        'm/mix.usda',
        'm/quad_pv.usda',
    ],
    '20-sample-questions.tex': [
        'q02/chair_base.usda',
        'q02/chair_repositioned.usda',
        'q02/scene.usda',
        'q12/export.usda',
        'q13/main.usda',
        'q13/MyBox.usda',
        'q13/contents.usda',
    ],
}

USDA_FILES = [f for files in CHAPTER_LISTINGS.values() for f in files
              if f.endswith('.usda')]

LISTING_RE = re.compile(
    r'\\begin\{lstlisting\}(?:\[[^\]]*\])?\n(.*?)\\end\{lstlisting\}', re.S)


@pytest.fixture(scope='module')
def scenarios(tmp_path_factory):
    """Write every listing verbatim to a scratch tree; return its root."""
    root = tmp_path_factory.mktemp('listings')
    for tex_name, files in CHAPTER_LISTINGS.items():
        listings = LISTING_RE.findall((CHAPTERS / tex_name).read_text())
        assert len(listings) == len(files), (
            f'{tex_name} has {len(listings)} listings but {len(files)} are '
            f'mapped in CHAPTER_LISTINGS — update the mapping.'
        )
        for rel, body in zip(files, listings):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
    return root


def assert_silent(capfd):
    """USD reports composition problems on stderr; none are acceptable."""
    err = capfd.readouterr().err
    assert err == '', f'USD emitted warnings/errors:\n{err}'


@pytest.mark.parametrize('rel', USDA_FILES)
def test_listing_parses(scenarios, capfd, rel):
    """Every usda listing in the book must be valid usda on its own."""
    layer = Sdf.Layer.FindOrOpen(str(scenarios / rel))
    assert layer is not None
    assert_silent(capfd)


# --- Chapter 10: Composition -------------------------------------------------

def test_c10_sublayer_order_wins(scenarios, capfd):
    """Earlier sublayer (lighting) beats later one (layout): radius == 3."""
    stage = Usd.Stage.Open(str(scenarios / 'c10/shot.usda'))
    assert stage.GetPrimAtPath('/Ball').GetAttribute('radius').Get() == 3
    assert_silent(capfd)


def test_c10_payload_load_states(scenarios, capfd):
    """Payload contents do not exist under LoadNone; Load() composes them."""
    stage = Usd.Stage.Open(str(scenarios / 'c10/city.usda'), Usd.Stage.LoadNone)
    assert not stage.GetPrimAtPath('/City/Block_01/Hydrant').IsValid()
    stage.Load('/City/Block_01')
    hydrant = stage.GetPrimAtPath('/City/Block_01/Hydrant')
    assert hydrant.IsValid()
    assert hydrant.GetAttribute('radius').Get() == 0.3
    assert_silent(capfd)


def test_c10_layer_offsets(scenarios, capfd):
    """The chapter's stated values at stage time 12, plus CQ2 (BallB @ 24)."""
    stage = Usd.Stage.Open(str(scenarios / 'c10/shot_offsets.usda'))

    def translate(path, time):
        return stage.GetPrimAtPath(path).GetAttribute('xformOp:translate').Get(time)

    # Interpolated values: exact in math, float-rounded in practice.
    assert translate('/Shot/BallA', 12) == pytest.approx((11, 0, 0))  # raw animation
    assert translate('/Shot/BallB', 12) == pytest.approx((1, 0, 0))   # offset = 10
    assert translate('/Shot/BallC', 12) == pytest.approx((5, 0, 0))   # scale = 2
    assert translate('/Shot/BallB', 24) == pytest.approx((13, 0, 0))  # checkpoint CQ2
    assert_silent(capfd)


def test_c10_api_matches_usda(scenarios, capfd):
    """The API-built stage composes the same values as the usda twin."""
    stage = Usd.Stage.CreateNew(str(scenarios / 'c10/shot_api.usda'))
    shot = stage.DefinePrim('/Shot', 'Xform')
    stage.SetDefaultPrim(shot)
    ball_a = stage.DefinePrim('/Shot/BallA')
    ball_a.GetReferences().AddReference('./anim.usda')
    ball_b = stage.DefinePrim('/Shot/BallB')
    ball_b.GetReferences().AddReference(
        './anim.usda', layerOffset=Sdf.LayerOffset(offset=10))
    ball_c = stage.DefinePrim('/Shot/BallC')
    ball_c.GetReferences().AddReference(
        './anim.usda', layerOffset=Sdf.LayerOffset(scale=2))

    usda = Usd.Stage.Open(str(scenarios / 'c10/shot_offsets.usda'))
    for name in ('BallA', 'BallB', 'BallC'):
        api_val = stage.GetPrimAtPath(f'/Shot/{name}').GetAttribute(
            'xformOp:translate').Get(12)
        usda_val = usda.GetPrimAtPath(f'/Shot/{name}').GetAttribute(
            'xformOp:translate').Get(12)
        assert api_val == usda_val, name
    assert_silent(capfd)


def test_c10_inherits_broadcast(scenarios, capfd):
    """Editing the inherited class restyles every inheriting prim."""
    stage = Usd.Stage.Open(str(scenarios / 'c10/forest_inh.usda'))
    t1 = stage.GetPrimAtPath('/World/Tree_01').GetAttribute('primvars:displayColor')
    assert t1.Get()[0] == pytest.approx((0, 0.5, 0))
    stage.GetPrimAtPath('/World/_tree').GetAttribute(
        'primvars:displayColor').Set([(0.8, 0.5, 0.1)])
    for name in ('Tree_01', 'Tree_02'):
        got = stage.GetPrimAtPath(f'/World/{name}').GetAttribute(
            'primvars:displayColor').Get()[0]
        assert got == pytest.approx((0.8, 0.5, 0.1)), name
    assert_silent(capfd)


def test_c10_specializes_fallback(scenarios, capfd):
    """Specializes provides values until anyone authors anything stronger."""
    stage = Usd.Stage.Open(str(scenarios / 'c10/metal.usda'))
    rusty = stage.GetPrimAtPath('/World/RustyMetal')
    assert rusty.GetAttribute('roughness').Get() == pytest.approx(0.4)
    assert rusty.GetAttribute('dirt').Get() == pytest.approx(0.8)
    rusty.GetAttribute('roughness').Set(0.9)
    assert rusty.GetAttribute('roughness').Get() == pytest.approx(0.9)
    assert_silent(capfd)


# --- Chapter 11: Content Aggregation -----------------------------------------

def test_c11_instancing_flow(scenarios, capfd):
    """Instance proxies are read-only; edit-all goes to the source asset;
    edit-one requires de-instancing — exactly as the chapter's listing runs."""
    from pxr import Tf
    stage = Usd.Stage.Open(str(scenarios / 'c11/forest.usda'))
    crown = stage.GetPrimAtPath('/Forest/Tree_01/Crown')
    assert crown.IsInstanceProxy()
    with pytest.raises(Tf.ErrorException):
        crown.GetAttribute('primvars:displayColor').Set([(1, 0, 0)])
    capfd.readouterr()  # drain the coding-error text the exception prints

    tree = Usd.Stage.Open(str(scenarios / 'c11/tree.usda'))
    tree.GetPrimAtPath('/Tree/Crown').GetAttribute(
        'primvars:displayColor').Set([(0.8, 0.5, 0.1)])

    t1 = stage.GetPrimAtPath('/Forest/Tree_01')
    t1.SetInstanceable(False)
    stage.GetPrimAtPath('/Forest/Tree_01/Crown').GetAttribute(
        'primvars:displayColor').Set([(0, 0.4, 0)])

    t2_color = stage.GetPrimAtPath('/Forest/Tree_02/Crown').GetAttribute(
        'primvars:displayColor').Get()[0]
    t1_color = stage.GetPrimAtPath('/Forest/Tree_01/Crown').GetAttribute(
        'primvars:displayColor').Get()[0]
    assert t2_color == pytest.approx((0.8, 0.5, 0.1))   # all instances
    assert t1_color == pytest.approx((0, 0.4, 0))       # just this one
    assert stage.GetPrimAtPath('/Forest/Tree_02').IsInstance()
    assert_silent(capfd)


def test_c11_pointinstancer(scenarios, capfd):
    """PointInstancer arrays and invisibleIds read back as authored."""
    stage = Usd.Stage.Open(str(scenarios / 'c11/scatter.usda'))
    pi = UsdGeom.PointInstancer(stage.GetPrimAtPath('/Scatter'))
    assert [str(t) for t in pi.GetPrototypesRel().GetTargets()] == [
        '/Scatter/Protos/Bush', '/Scatter/Protos/Rock']
    assert list(pi.GetProtoIndicesAttr().Get()) == [0, 1, 0, 1]
    assert len(pi.GetPositionsAttr().Get()) == 4
    assert list(pi.GetInvisibleIdsAttr().Get()) == [2]
    assert_silent(capfd)


def test_c11_per_instance_arrays(scenarios, capfd):
    """The override layer authors orientations/scales as printed."""
    layer = Sdf.Layer.FindOrOpen(str(scenarios / 'c11/scatter_tweak.usda'))
    spec = layer.GetPrimAtPath('/Scatter')
    orientations = spec.attributes['orientations'].default
    scales = spec.attributes['scales'].default
    assert len(orientations) == 4 and len(scales) == 4
    assert tuple(scales[3]) == pytest.approx((0.7, 0.7, 0.7))
    assert_silent(capfd)


def test_c11_add_prototype(scenarios, capfd):
    """AddTarget appends prototype index 2; protoIndices can use it."""
    src = Sdf.Layer.FindOrOpen(str(scenarios / 'c11/scatter.usda'))
    work = Sdf.Layer.CreateAnonymous('.usda')
    work.TransferContent(src)
    stage = Usd.Stage.Open(work)
    pi = UsdGeom.PointInstancer(stage.GetPrimAtPath('/Scatter'))
    fern = UsdGeom.Cone.Define(stage, '/Scatter/Protos/Fern')
    pi.GetPrototypesRel().AddTarget(fern.GetPath())
    pi.GetProtoIndicesAttr().Set([0, 1, 0, 2])
    assert [str(t) for t in pi.GetPrototypesRel().GetTargets()] == [
        '/Scatter/Protos/Bush', '/Scatter/Protos/Rock', '/Scatter/Protos/Fern']
    assert list(pi.GetProtoIndicesAttr().Get()) == [0, 1, 0, 2]
    assert_silent(capfd)


# --- Chapter 12: Customizing USD ----------------------------------------------

def test_c12_schema_source(scenarios, capfd):
    """The schema.usda source declares one typed and one API schema class."""
    layer = Sdf.Layer.FindOrOpen(str(scenarios / 'c12/schema.usda'))
    joint = layer.GetPrimAtPath('/SimJoint')
    wear = layer.GetPrimAtPath('/WearAPI')
    assert joint.specifier == Sdf.SpecifierClass
    assert joint.typeName == 'SimJoint'
    assert wear.specifier == Sdf.SpecifierClass
    assert_silent(capfd)


def test_c12_apply_api(scenarios, capfd):
    """Applying an API schema records it in apiSchemas metadata."""
    stage = Usd.Stage.CreateInMemory()
    prim = UsdGeom.Xform.Define(stage, '/Robot').GetPrim()
    Usd.CollectionAPI.Apply(prim, 'render')
    assert prim.HasAPI(Usd.CollectionAPI)
    assert list(prim.GetAppliedSchemas()) == ['CollectionAPI:render']
    assert_silent(capfd)


def test_c12_kind_registration(scenarios, capfd):
    """The book's plugInfo.json registers a kind via PXR_PLUGINPATH_NAME."""
    import subprocess
    import sys
    plug = scenarios / 'c12/studio_kinds'
    plug.mkdir(exist_ok=True)
    (plug / 'plugInfo.json').write_text(
        (scenarios / 'c12/kinds_plugin.json').read_text())
    code = (
        "from pxr import Kind\n"
        "print(Kind.Registry.HasKind('vehicle'),"
        " Kind.Registry.GetBaseKind('vehicle'))\n"
    )
    run = subprocess.run([sys.executable, '-c', code], capture_output=True,
                         text=True, env={'PXR_PLUGINPATH_NAME': str(plug)})
    assert run.stdout.strip() == 'True component'
    assert run.stderr == ''
    capfd.readouterr()


def test_c13_obj_importer(scenarios, capfd):
    """The 25-line importer produces a checker-clean USD asset."""
    import warnings
    from pxr import UsdUtils
    points, counts, indices = [], [], []
    for line in (scenarios / 'c13/box.obj').read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'v':
            points.append(tuple(float(x) for x in parts[1:4]))
        elif parts[0] == 'f':
            face = [int(p.split('/')[0]) - 1 for p in parts[1:]]
            counts.append(len(face))
            indices.extend(face)
    out = scenarios / 'c13/box_imported.usda'
    stage = Usd.Stage.CreateNew(str(out))
    mesh = UsdGeom.Mesh.Define(stage, '/Box')
    stage.SetDefaultPrim(mesh.GetPrim())
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    mesh.GetPointsAttr().Set(points)
    mesh.GetFaceVertexCountsAttr().Set(counts)
    mesh.GetFaceVertexIndicesAttr().Set(indices)
    mesh.GetExtentAttr().Set(UsdGeom.Boundable.ComputeExtentFromPlugins(
        mesh, Usd.TimeCode.Default()))
    stage.Save()

    check = Usd.Stage.Open(str(out))
    m = UsdGeom.Mesh(check.GetPrimAtPath('/Box'))
    assert len(m.GetPointsAttr().Get()) == 4
    assert list(m.GetFaceVertexCountsAttr().Get()) == [4]
    assert list(m.GetFaceVertexIndicesAttr().Get()) == [0, 1, 2, 3]
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        checker = UsdUtils.ComplianceChecker()
        checker.CheckCompliance(str(out))
    assert checker.GetFailedChecks() == []
    capfd.readouterr()


# --- Chapter 14: Data Modeling -------------------------------------------------

def test_c14_value_types(scenarios, capfd):
    """The type-zoo listing resolves to the Sdf types the chapter names."""
    stage = Usd.Stage.Open(str(scenarios / 'c14/typed.usda'))
    crate = stage.GetPrimAtPath('/Props/Crate')
    assert crate.GetAttribute('texture').GetTypeName() == Sdf.ValueTypeNames.Asset
    assert (crate.GetAttribute('primvars:displayColor').GetTypeName() ==
            Sdf.ValueTypeNames.Color3fArray)
    assert (crate.GetAttribute('xformOp:transform').GetTypeName() ==
            Sdf.ValueTypeNames.Matrix4d)
    assert crate.GetAttribute('notes').GetTypeName() == Sdf.ValueTypeNames.String
    assert crate.GetRelationship('inspiration').GetTargets() == [
        Sdf.Path('/Props/Reference')]
    assert_silent(capfd)


def test_c14_indexed_primvar(scenarios, capfd):
    """faceVarying indexed st primvar behaves as the chapter describes."""
    stage = Usd.Stage.Open(str(scenarios / 'c14/mesh_uv.usda'))
    prim = stage.GetPrimAtPath('/Plate')
    st = UsdGeom.PrimvarsAPI(prim).GetPrimvar('st')
    assert st.GetInterpolation() == UsdGeom.Tokens.faceVarying
    assert st.IsIndexed()
    assert list(st.GetIndices()) == [0, 1, 2, 3]
    assert len(st.ComputeFlattened()) == 4
    assert_silent(capfd)


def test_c14_props_api(scenarios, capfd):
    """Mirror of the authoring/retrieval listing, value for value."""
    stage = Usd.Stage.CreateInMemory()
    mesh = UsdGeom.Mesh.Define(stage, '/Crate')
    prim = mesh.GetPrim()
    wear = UsdGeom.PrimvarsAPI(prim).CreatePrimvar(
        'wear', Sdf.ValueTypeNames.Float, UsdGeom.Tokens.constant)
    wear.Set(0.5)
    prim.SetCustomDataByKey('studio:reviewed', True)
    assert wear.GetName() == 'primvars:wear'
    assert wear.Get() == 0.5
    assert wear.GetInterpolation() == UsdGeom.Tokens.constant
    assert prim.GetCustomDataByKey('studio:reviewed') is True
    assert [a.GetName() for a in prim.GetAttributes()
            if a.IsAuthored()] == ['primvars:wear']
    assert_silent(capfd)


def test_c14_update_extent(scenarios, capfd):
    """Doubling points and recomputing extent yields the chapter's bounds."""
    src = Sdf.Layer.FindOrOpen(str(scenarios / 'c14/mesh_uv.usda'))
    work = Sdf.Layer.CreateAnonymous('.usda')
    work.TransferContent(src)
    stage = Usd.Stage.Open(work)
    mesh = UsdGeom.Mesh(stage.GetPrimAtPath('/Plate'))
    points = [(x * 2, y * 2, z * 2) for x, y, z in mesh.GetPointsAttr().Get()]
    mesh.GetPointsAttr().Set(points)
    extent = UsdGeom.Boundable.ComputeExtentFromPlugins(
        mesh, Usd.TimeCode.Default())
    mesh.GetExtentAttr().Set(extent)
    assert list(extent[0]) == [-2, 0, -2]
    assert list(extent[1]) == [2, 0, 2]
    assert_silent(capfd)


def test_c14_timecode_and_interpolation(scenarios, capfd):
    """Linear vs held interpolation and bracketing samples, as printed."""
    stage = Usd.Stage.Open(str(scenarios / 'c14/ball_anim.usda'))
    radius = stage.GetPrimAtPath('/Ball').GetAttribute('radius')
    assert radius.Get(6) == pytest.approx(6.0)
    assert radius.GetBracketingTimeSamples(6) == (1.0, 11.0)
    stage.SetInterpolationType(Usd.InterpolationTypeHeld)
    assert radius.Get(6) == pytest.approx(1.0)
    stage.SetInterpolationType(Usd.InterpolationTypeLinear)
    assert_silent(capfd)


def test_c14_xform_common_api(scenarios, capfd):
    """XformCommonAPI round-trips canonical TRS vectors."""
    from pxr import Gf
    stage = Usd.Stage.CreateInMemory()
    prim = UsdGeom.Xform.Define(stage, '/Crate').GetPrim()
    api = UsdGeom.XformCommonAPI(prim)
    api.SetTranslate(Gf.Vec3d(1, 2, 3))
    api.SetRotate(Gf.Vec3f(0, 45, 0))
    api.SetScale(Gf.Vec3f(2, 2, 2))
    t, r, s, _pivot, _order = api.GetXformVectors(Usd.TimeCode.Default())
    assert t == Gf.Vec3d(1, 2, 3)
    assert r == Gf.Vec3f(0, 45, 0)
    assert s == Gf.Vec3f(2, 2, 2)
    assert_silent(capfd)


def test_c15_trace_scope(scenarios, capfd):
    """The named Trace scope appears in the reporter output."""
    from pxr import Trace
    collector = Trace.Collector()
    collector.enabled = True
    with Trace.TraceScope('open-and-traverse'):
        stage = Usd.Stage.Open(str(scenarios / 'c15/shot.usda'))
        assert len(list(stage.Traverse())) >= 1
    collector.enabled = False
    Trace.Reporter.globalReporter.Report()
    out = capfd.readouterr().out
    assert 'open-and-traverse' in out


# --- Chapter 15: Debugging -----------------------------------------------------

def test_c15_property_stack(scenarios, capfd):
    """GetPropertyStack lists opinions strongest-first with their layers."""
    stage = Usd.Stage.Open(str(scenarios / 'c15/shot.usda'))
    attr = stage.GetPrimAtPath('/Ball').GetAttribute('radius')
    assert attr.Get() == 3.0
    stack = attr.GetPropertyStack(Usd.TimeCode.Default())
    assert [s.layer.GetDisplayName() for s in stack] == ['lite.usda', 'base.usda']
    assert [s.default for s in stack] == [3.0, 1.0]
    assert_silent(capfd)


def test_c15_mute_layer(scenarios, capfd):
    """Muting the stronger sublayer exposes the weaker opinion, reversibly."""
    stage = Usd.Stage.Open(str(scenarios / 'c15/shot.usda'))
    radius = stage.GetPrimAtPath('/Ball').GetAttribute('radius')
    lite = Sdf.Layer.FindOrOpen(str(scenarios / 'c15/lite.usda'))
    assert radius.Get() == 3.0
    stage.MuteLayer(lite.identifier)
    assert radius.Get() == 1.0
    stage.UnmuteLayer(lite.identifier)
    assert radius.Get() == 3.0
    assert_silent(capfd)


def test_c15_change_block(scenarios, capfd):
    """Batched Sdf authoring inside a ChangeBlock lands intact."""
    layer = Sdf.Layer.CreateAnonymous()
    with Sdf.ChangeBlock():
        for i in range(100):
            prim = Sdf.CreatePrimInLayer(layer, f'/Props/Prop_{i:03}')
            prim.specifier = Sdf.SpecifierDef
            prim.typeName = 'Xform'
    assert len(layer.GetPrimAtPath('/Props').nameChildren) == 100
    assert_silent(capfd)


def test_c15_debug_symbols(scenarios, capfd):
    """The TfDebug switches the chapter names actually exist."""
    from pxr import Tf
    names = Tf.Debug.GetDebugSymbolNames()
    assert len(names) > 0
    assert 'USD_CHANGES' in names
    assert 'PLUG_REGISTRATION' in names
    assert_silent(capfd)


# --- Chapter 16: Pipeline Development ------------------------------------------

def test_c16_asset_interface(scenarios, capfd):
    """The interface layer exposes kind/assetInfo and defers contents."""
    stage = Usd.Stage.Open(str(scenarios / 'c16/Chair.usda'),
                           Usd.Stage.LoadNone)
    chair = stage.GetPrimAtPath('/Chair')
    assert Usd.ModelAPI(chair).GetKind() == 'component'
    assert chair.GetAssetInfoByKey('name') == 'Chair'
    assert chair.GetAssetInfoByKey('version') == 'v003'
    assert not stage.GetPrimAtPath('/Chair/Geometry/Seat').IsValid()
    stage.Load('/Chair')
    assert stage.GetPrimAtPath('/Chair/Geometry/Seat').IsValid()
    assert_silent(capfd)


def test_c16_model_hierarchy(scenarios, capfd):
    """The contiguity rule: a component under a plain prim is not a model."""
    stage = Usd.Stage.Open(str(scenarios / 'c16/hierarchy.usda'))
    expect = {
        '/City': ('assembly', True, True),
        '/City/Block': ('group', True, True),
        '/City/Block/Bldg': ('component', True, False),
        '/City/Block/Bldg/Door': ('subcomponent', False, False),
        '/City/Plain/Orphan': ('component', False, False),
    }
    for path, (kind, is_model, is_group) in expect.items():
        prim = stage.GetPrimAtPath(path)
        assert Usd.ModelAPI(prim).GetKind() == kind, path
        assert prim.IsModel() == is_model, path
        assert prim.IsGroup() == is_group, path
    assert_silent(capfd)


def test_c16_path_dependencies(scenarios, capfd):
    """The path-validation gate sees exactly the payload dependency."""
    layer = Sdf.Layer.FindOrOpen(str(scenarios / 'c16/Chair.usda'))
    deps = layer.GetCompositionAssetDependencies()
    assert deps == ['./contents.usda']
    assert all(not d.startswith('/') and '\\\\' not in d for d in deps)
    assert_silent(capfd)


# --- Chapter 17: Visualization --------------------------------------------------

def test_c17_primvar_network(scenarios, capfd):
    """Both plates bind the same material; the network walks as printed."""
    from pxr import UsdShade
    stage = Usd.Stage.Open(str(scenarios / 'c17/shaded.usda'))
    bound = {}
    for name in ('PlateA', 'PlateB'):
        mesh = stage.GetPrimAtPath(f'/Scene/{name}')
        material, _ = UsdShade.MaterialBindingAPI(mesh).ComputeBoundMaterial()
        bound[name] = material.GetPath()
    assert bound['PlateA'] == bound['PlateB'] == Sdf.Path('/Scene/Looks/Painted')

    material = UsdShade.Material(stage.GetPrimAtPath('/Scene/Looks/Painted'))
    src = material.GetSurfaceOutput().GetConnectedSource()
    pbr = UsdShade.Shader(src[0].GetPrim())
    assert pbr.GetIdAttr().Get() == 'UsdPreviewSurface'
    rsrc = pbr.GetInput('diffuseColor').GetConnectedSource()
    reader = UsdShade.Shader(rsrc[0].GetPrim())
    assert reader.GetIdAttr().Get() == 'UsdPrimvarReader_float3'
    assert reader.GetInput('varname').Get() == 'displayColor'
    assert_silent(capfd)


def test_c17_texture_network(scenarios, capfd):
    """UsdUVTexture chain, camera, and light read back as authored."""
    from pxr import UsdLux, UsdShade
    stage = Usd.Stage.Open(str(scenarios / 'c17/tex_scene.usda'))
    pbr = UsdShade.Shader(stage.GetPrimAtPath('/Scene/Looks/Checkered/PBR'))
    tsrc = pbr.GetInput('diffuseColor').GetConnectedSource()
    tex = UsdShade.Shader(tsrc[0].GetPrim())
    assert tex.GetIdAttr().Get() == 'UsdUVTexture'
    assert tex.GetInput('file').Get().path == './checker.png'
    rsrc = tex.GetInput('st').GetConnectedSource()
    reader = UsdShade.Shader(rsrc[0].GetPrim())
    assert reader.GetIdAttr().Get() == 'UsdPrimvarReader_float2'
    assert reader.GetInput('varname').Get() == 'st'
    cam = UsdGeom.Camera(stage.GetPrimAtPath('/Scene/Cam'))
    assert cam.GetFocalLengthAttr().Get() == pytest.approx(35.0)
    sun = UsdLux.DistantLight(stage.GetPrimAtPath('/Scene/Sun'))
    assert sun.GetIntensityAttr().Get() == pytest.approx(1000.0)
    assert_silent(capfd)


def test_c17_geomsubset(scenarios, capfd):
    """The materialBind subset selects face 0 of the two-face plate."""
    stage = Usd.Stage.Open(str(scenarios / 'c17/subset.usda'))
    subset = UsdGeom.Subset(stage.GetPrimAtPath('/Plate/Front'))
    assert subset.GetElementTypeAttr().Get() == 'face'
    assert list(subset.GetIndicesAttr().Get()) == [0]
    assert subset.GetFamilyNameAttr().Get() == 'materialBind'
    assert_silent(capfd)


def test_c17_purpose_visibility(scenarios, capfd):
    """Visibility inherits down; purpose reads back as authored."""
    stage = Usd.Stage.Open(str(scenarios / 'c17/purpose.usda'))
    proxy = UsdGeom.Imageable(stage.GetPrimAtPath('/Rig/ProxySphere'))
    assert proxy.ComputeVisibility() == UsdGeom.Tokens.invisible
    assert proxy.ComputePurpose() == UsdGeom.Tokens.proxy
    assert_silent(capfd)


def test_c17_light(scenarios, capfd):
    """The DistantLight listing reads back through UsdLux."""
    from pxr import UsdLux
    stage = Usd.Stage.Open(str(scenarios / 'c17/sun.usda'))
    sun = UsdLux.DistantLight(stage.GetPrimAtPath('/Sun'))
    assert sun.GetIntensityAttr().Get() == 500.0
    assert sun.GetAngleAttr().Get() == pytest.approx(0.53)
    assert_silent(capfd)


# --- Chapter 13: Data Exchange -----------------------------------------------

def test_c13_traversal_and_custom_attr(scenarios, capfd):
    """The exporter-skeleton loop finds exactly the mesh the chapter claims,
    and the namespaced studio attribute is queryable."""
    stage = Usd.Stage.Open(str(scenarios / 'c13/asset.usda'))
    meshes = [p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
    assert [str(p.GetPath()) for p in meshes] == ['/Plate/Geom']
    mesh = UsdGeom.Mesh(meshes[0])
    assert len(mesh.GetPointsAttr().Get()) == 4
    assert list(mesh.GetFaceVertexCountsAttr().Get()) == [4]
    assert list(mesh.GetFaceVertexIndicesAttr().Get()) == [0, 1, 2, 3]
    prim = meshes[0]
    assert prim.GetAttribute('myStudio:wearAmount').Get() == 0.25
    assert len(prim.GetPropertiesInNamespace('myStudio')) == 1
    assert_silent(capfd)


def test_c13_roundtrip_crate_equals_text(scenarios, capfd):
    """usda -> usdc re-export preserves the data exactly."""
    src = scenarios / 'c13/asset.usda'
    dst = scenarios / 'c13/asset.usdc'
    Sdf.Layer.FindOrOpen(str(src)).Export(str(dst))
    text = Usd.Stage.Open(str(src))
    crate = Usd.Stage.Open(str(dst))
    for attr in ('points', 'primvars:st', 'faceVertexIndices'):
        assert (text.GetPrimAtPath('/Plate/Geom').GetAttribute(attr).Get() ==
                crate.GetPrimAtPath('/Plate/Geom').GetAttribute(attr).Get())
    assert_silent(capfd)


def test_c13_compliance_checker(scenarios, capfd):
    """The clean export passes; the broken one fails exactly the three
    StageMetadataChecker checks the chapter quotes."""
    import warnings
    from pxr import UsdUtils
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        good = UsdUtils.ComplianceChecker()
        good.CheckCompliance(str(scenarios / 'c13/asset.usda'))
        bad = UsdUtils.ComplianceChecker()
        bad.CheckCompliance(str(scenarios / 'c13/bad_export.usda'))
    assert good.GetFailedChecks() == []
    failures = bad.GetFailedChecks()
    assert len(failures) == 3
    joined = ' '.join(failures)
    for token in ('upAxis', 'metersPerUnit', 'defaultPrim',
                  'StageMetadataChecker'):
        assert token in joined
    capfd.readouterr()  # drain; the deprecated shim may chat on stderr


def test_c13_compute_extent(scenarios, capfd):
    """ComputeExtentFromPlugins yields the bounds the chapter prints."""
    stage = Usd.Stage.Open(str(scenarios / 'c13/bad_export.usda'))
    mesh = UsdGeom.Mesh(stage.GetPrimAtPath('/Plate'))
    extent = UsdGeom.Boundable.ComputeExtentFromPlugins(
        mesh, Usd.TimeCode.Default())
    assert list(extent[0]) == [-1, 0, -1]
    assert list(extent[1]) == [1, 0, 1]
    assert_silent(capfd)


# --- Chapter 23: Mock exam ----------------------------------------------------

def test_mock_q3_root_beats_sublayers(scenarios, capfd):
    """Mock Q3, answer C: the root layer's opinion wins with 6."""
    stage = Usd.Stage.Open(str(scenarios / 'm/setA_shot.usda'))
    assert stage.GetPrimAtPath('/Box').GetAttribute('size').Get() == 6
    assert_silent(capfd)


def test_mock_q13_reference_order(scenarios, capfd):
    """Mock Q13, answer A: the earlier reference entry (red) wins."""
    stage = Usd.Stage.Open(str(scenarios / 'm/mix.usda'))
    color = stage.GetPrimAtPath('/World/Prop').GetAttribute(
        'primvars:displayColor').Get()[0]
    assert color == pytest.approx((1, 0, 0))
    assert_silent(capfd)


def test_mock_q17_primvar_counts(scenarios, capfd):
    """Mock Q17, answer C: the uniform primvar's count mismatches the face count."""
    stage = Usd.Stage.Open(str(scenarios / 'm/quad_pv.usda'))
    prim = stage.GetPrimAtPath('/Plate')
    faces = len(prim.GetAttribute('faceVertexCounts').Get())
    pv = UsdGeom.PrimvarsAPI(prim)
    assert len(pv.GetPrimvar('a').Get()) == 1          # constant: 1 == valid
    assert len(pv.GetPrimvar('b').Get()) == len(prim.GetAttribute('points').Get())
    assert len(pv.GetPrimvar('c').Get()) == 3 != faces  # uniform: invalid
    assert_silent(capfd)


# --- Chapter 20: Sample questions -------------------------------------------

def test_q2_local_opinion_wins(scenarios, capfd):
    """Q2, answer C: the local opinion beats both references (L before R)."""
    stage = Usd.Stage.Open(str(scenarios / 'q02/scene.usda'))
    translate = stage.GetPrimAtPath('/World/Chair').GetAttribute('xformOp:translate').Get()
    assert translate == (0, 1, 0)
    assert_silent(capfd)


def test_q12_flaw_is_semantic_not_syntactic(scenarios, capfd):
    """Q12, answer C: the export must parse cleanly and contain all prims;
    its only flaw is that the binding target sits outside the defaultPrim."""
    stage = Usd.Stage.Open(str(scenarios / 'q12/export.usda'))
    paths = {str(p.GetPath()) for p in stage.Traverse()}
    assert {'/World', '/World/bolt', '/Materials', '/Materials/metal'} <= paths
    binding = stage.GetPrimAtPath('/World/bolt').GetRelationship('material:binding')
    target = binding.GetTargets()[0]
    default_root = Sdf.Path('/' + stage.GetRootLayer().defaultPrim)
    assert not target.HasPrefix(default_root), 'the intended flaw disappeared'
    assert_silent(capfd)


def test_q13_local_variant_selection_wins(scenarios, capfd):
    """Q13, answer B: the local color=red selection in main.usda beats the
    selection authored inside the loftedColor=blue variant, so the box stays red."""
    stage = Usd.Stage.Open(str(scenarios / 'q13/main.usda'))
    box = stage.GetPrimAtPath('/World/MyBox')
    cube = stage.GetPrimAtPath('/World/MyBox/Cube')
    assert box.GetVariantSet('loftedColor').GetVariantSelection() == 'blue'
    assert cube.GetVariantSet('color').GetVariantSelection() == 'red'
    assert list(cube.GetAttribute('primvars:displayColor').Get()) == [(1, 0, 0)]
    assert_silent(capfd)
