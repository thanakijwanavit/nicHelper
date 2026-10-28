"""vinf-luj: nicHelper must not fetch the gist, run remote code, unpickle input or call OSRM over http.

Runs with a bare python3 + pytest + pyyaml + requests + jsonschema: third-party modules that are
missing are replaced by small stubs so the hardening checks still import the real nicHelper code.
"""
import base64, hashlib, importlib, json, pickle, re, sys, types, zlib
from pathlib import Path

import pytest
import requests
import yaml

REPO = Path(__file__).resolve().parent.parent
SCHEMA_FILE = REPO / "nicHelper" / "schemas" / "squirrelOpenApiV0.0.3.yaml"
# sha256 of squirrelOpenApiV0.0.3.yaml at gist revision ed2d322eac4900ee0f95b431d0f9067a40f3e0f0
SCHEMA_SHA256 = "a7d82a0b4b0649390a2a986e704bd7b418c086b639eb9d4cf93af33a2209b74c"
PYTHON_TAG_YAML = "point: !!python/tuple [1, 2]\n"  # FullLoader builds a tuple, safe_load refuses


def _stub(name, **attrs):
    try:
        importlib.import_module(name)
    except ImportError:
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        sys.modules[name] = mod
        if "." in name:
            parent, child = name.rsplit(".", 1)
            setattr(sys.modules[parent], child, mod)


def _dpathGet(obj, path):
    for part in [p for p in path.split("/") if p]:
        obj = obj[part]
    return obj


class _Attribute:
    def __init__(self, **kwargs):
        pass


_stub("beartype", beartype=lambda f: f)
_stub("ujson", dumps=json.dumps, loads=json.loads)
_stub("pandas", DataFrame=dict)
_stub("dpath", get=_dpathGet)
_stub("dpath.util", get=_dpathGet)
_stub("pynamodb")
_stub("pynamodb.constants", STRING="S")
_stub("pynamodb.attributes", Attribute=_Attribute, UnicodeAttribute=_Attribute, NumberAttribute=_Attribute)
_stub("pynamodb.models", Model=type("Model", (), {}))
_stub("awsSchema")
_stub("awsSchema.apigateway", Event=object, Response=object)


def _noNetwork(*args, **kwargs):
    raise AssertionError(f"unexpected network call: {args}")


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(requests, "get", _noNetwork)


@pytest.fixture
def serveText(monkeypatch):
    def serve(text):
        response = requests.models.Response()  # a real Response: githubGet is beartype-checked
        response.status_code, response.encoding, response._content = 200, "utf-8", text.encode()
        monkeypatch.setattr(requests, "get", lambda *a, **k: response)
    return serve


def test_no_gist_fullloader_or_http_osrm_in_code_or_notebooks():
    pattern = re.compile(r"gist\.githubusercontent\.com|FullLoader|http://router\.project-osrm")
    files = list((REPO / "nicHelper").glob("*.py")) + list(REPO.glob("*.ipynb")) + list((REPO / "nbs").glob("*.ipynb"))
    hits = [f"{f.relative_to(REPO)}:{n}" for f in files
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1) if pattern.search(line)]
    assert hits == []


def test_schema_is_vendored_from_the_pinned_gist_and_packaged():
    assert hashlib.sha256(SCHEMA_FILE.read_bytes()).hexdigest() == SCHEMA_SHA256
    assert yaml.safe_load(SCHEMA_FILE.read_text())["openapi"] == "3.0.0"
    assert "recursive-include nicHelper/schemas *.yaml" in (REPO / "MANIFEST.in").read_text()
    from nicHelper.schema import squirrelSchemaPath
    assert Path(squirrelSchemaPath).resolve() == SCHEMA_FILE.resolve()


def test_supermodel_schema_loads_without_network(offline):
    import nicHelper.pynamodb
    pynamodbModule = importlib.reload(nicHelper.pynamodb)  # re-runs the SuperModel class body offline
    schema = pynamodbModule.SuperModel.data.schema
    assert schema["openapi"] == "3.0.0"
    assert "Location" in schema["components"]["schemas"]


def test_schema_helpers_read_vendored_files_offline(offline):
    from nicHelper.schema import getSchemaPath, getTypes, squirrelSchemaPath, validateUrl
    assert "properties" in getSchemaPath(squirrelSchemaPath, "components/schemas/Location")
    sample = str(REPO / "testData" / "sampleYaml.yaml")
    assert getTypes(sample)["cprcode"] is int
    assert validateUrl(sample, {"iprcode": 4, "cprcode": 123, "oprCode": "123"}, format_="yaml").cprcode == 123


def test_yaml_loaders_refuse_python_tags(serveText, tmp_path):
    from nicHelper import dictUtil, github, schema, yamlUtil
    local = tmp_path / "tagged.yaml"
    local.write_text(PYTHON_TAG_YAML)
    serveText(PYTHON_TAG_YAML)
    calls = [lambda: yamlUtil.loadYamlUrl("https://example.com/a.yaml"),
             lambda: yamlUtil.loadYaml(str(local)),
             lambda: dictUtil.loadYaml(str(local)),
             lambda: github.githubGetYaml("https://example.com/a.yaml", "token"),
             lambda: schema.getSchemaPath("https://example.com/a.yaml"),
             lambda: schema.getTypes(str(local))]
    for call in calls:
        with pytest.raises(yaml.constructor.ConstructorError):
            call()


def test_github_import_module_never_downloads_or_runs_code(offline, tmp_path):
    from nicHelper.github import githubImportModule
    target = tmp_path / "module.py"
    with pytest.raises(NotImplementedError, match="remote code"):
        githubImportModule("https://example.com/m.py", "token", path=str(target))
    assert not target.exists()


def test_compress_defaults_to_json_and_never_unpickles():
    from nicHelper.compress import compressDict, decompressDict
    data = {"a": [1, 2, {"b": "c"}]}
    packed = compressDict(data)
    assert json.loads(zlib.decompress(base64.b64decode(packed))) == data
    assert decompressDict(packed) == data
    pickled = base64.b64encode(zlib.compress(pickle.dumps(data)))
    with pytest.raises(ValueError):  # pickle.loads would have returned data here
        decompressDict(pickled)


def test_old_pickle_blob_fails_with_the_migration_and_is_never_unpickled(monkeypatch):
    from nicHelper.compress import decompressDict
    def boom(*args, **kwargs):
        raise AssertionError("decompressDict unpickled its input")
    monkeypatch.setattr(pickle, "loads", boom)
    monkeypatch.setattr(pickle, "load", boom)
    monkeypatch.setattr(pickle, "Unpickler", boom)
    for protocol in (2, 4, 5):  # the old default was pickle.dumps, protocol 4 or 5
        blob = base64.b64encode(zlib.compress(pickle.dumps({"keys": [{"kid": "k"}]}, protocol=protocol)))
        with pytest.raises(ValueError, match=r"nicHelper<=0\.0\.120.*never unpickles.*CHANGELOG\.md 0\.1\.0"):
            decompressDict(blob)
        with pytest.raises(ValueError, match="never unpickles"):
            decompressDict(blob.decode())  # env vars arrive as str


def test_compress_change_is_released_as_breaking():
    import nicHelper
    assert nicHelper.__version__ == "0.1.0"
    assert "version = 0.1.0" in (REPO / "settings.ini").read_text()
    changelog = (REPO / "CHANGELOG.md").read_text()
    assert "## 0.1.0" in changelog and "BREAKING: compress uses JSON, not pickle" in changelog
    assert "include CHANGELOG.md" in (REPO / "MANIFEST.in").read_text()
    readme = (REPO / "README.md").read_text()
    index = json.loads((REPO / "index.ipynb").read_text(encoding="utf-8"))
    note = next("".join(c["source"]) for c in index["cells"] if "Breaking changes in 0.1.0" in "".join(c["source"]))
    assert note in readme  # README is built from index.ipynb, so the note must be in both


def test_osrm_default_endpoint_is_https(monkeypatch):
    from nicHelper.distance import getDistanceOsrm
    urls = []
    def fakeGet(url, *args, **kwargs):
        urls.append(url)
        return types.SimpleNamespace(json=lambda: {"routes": [{"distance": 12.5}]})
    monkeypatch.setattr(requests, "get", fakeGet)
    assert getDistanceOsrm(13.7, 100.5, 13.8, 100.6) == 12.5
    assert urls[0].startswith("https://router.project-osrm.org/")


@pytest.mark.parametrize("mod", ["github", "schema", "yamlUtil", "pynamodb", "dictUtil", "distance", "compress", "colab"])
def test_notebooks_export_the_same_code_as_the_package(mod):
    """nbdev_build_lib regenerates nicHelper/*.py from nbs/*.ipynb, so the fix must live in both."""
    norm = lambda s: "\n".join(l.rstrip() for l in s.strip("\n").splitlines()).strip()
    absImports = lambda s: re.sub(r"^(\s*)from \.(\w+) import", r"\1from nicHelper.\2 import", s, flags=re.M)
    pyCells = [norm(absImports(c)) for c in (REPO / "nicHelper" / f"{mod}.py").read_text().split("\n# Cell\n")[1:]]
    nb = json.loads((REPO / "nbs" / f"{mod}.ipynb").read_text(encoding="utf-8"))
    nbCells = [norm("".join(c["source"]).split("\n", 1)[-1]) for c in nb["cells"] if c["cell_type"] == "code"
               and re.match(r"^\s*#\s*export\s*$", "".join(c["source"]).split("\n")[0])]
    assert nbCells == pyCells
