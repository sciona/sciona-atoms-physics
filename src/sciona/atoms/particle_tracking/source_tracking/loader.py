"""Hash-verified source closure with invocation-local imports and state."""
import builtins
import hashlib
import json
from pathlib import Path
import types

from sciona.competition_dataframe_compat import compile_as_matrix_compat


ORDER = ['library_trackml_score.py.source', 'library_trackml_dataset.py.source'] + [
    'solution_trackml_solution_'+name+'.py.source' for name in
    ['logging', 'geometry', 'neighbors', 'candidates', 'corrections', 'cells', 'data', 'algorithm']]
MANIFEST_SHA256 = '20d17bc273ede033c6b146e7c0fda52a5cd9de1e72e4050d919b5abe822a6203'


def load_source_modules():
    """Create an independent original module graph; never populate sys.modules.

    The only source translations are three reviewed legacy array conversions.
    Import interception only handles the pinned internal source imports. Other
    imports use Python's normal machinery. Nothing is downloaded at runtime.
    """
    root = Path(__file__).parent
    manifest_bytes = (root/'source_manifest.json').read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
        raise ValueError('Tracking source manifest integrity check failed')
    manifest = json.loads(manifest_bytes)
    contents = {}
    for filename, record in manifest.items():
        if Path(filename).name != filename:
            raise ValueError('Invalid source resource name')
        content = (root/filename).read_bytes()
        if hashlib.sha256(content).hexdigest() != record['sha256']:
            raise ValueError('Tracking source integrity check failed')
        contents[filename] = content
    if not set(ORDER) <= contents.keys():
        raise ValueError('Incomplete tracking source closure')
    modules = {}

    def local_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith(('trackml.', 'trackml_solution.')):
            if level or not fromlist or name not in modules:
                raise ImportError('Unreviewed tracking source import')
            return modules[name]
        return builtins.__import__(name, globals, locals, fromlist, level)

    for filename in ORDER:
        name = manifest[filename]['source_path'][:-3].replace('/', '.')
        module = types.ModuleType(name)
        module.__file__ = str(root/filename)
        module.__dict__['__builtins__'] = dict(vars(builtins), __import__=local_import)
        if name.endswith(('.neighbors', '.cells')):
            code, helpers = compile_as_matrix_compat(contents[filename],
                expected_calls=2 if name.endswith('.neighbors') else 1, filename=name)
            module.__dict__.update(helpers)
        else:
            code = compile(contents[filename], name, 'exec')
        exec(code, module.__dict__)
        modules[name] = module
    return modules
