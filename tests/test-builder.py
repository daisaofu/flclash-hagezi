import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'tools' / 'build_hagezi.py'
spec = importlib.util.spec_from_file_location('builder', path)
builder = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(builder)

fixtures = {
    'https://unit.test/test-onlydomains.txt': '# header\nExample.COM\nexample.org\n',
    'https://unit.test/test.txt': '# header\n*.example.com\n*.sub.example.org\n',
}
builder.BASE = 'https://unit.test'
builder.fetch = lambda url: fixtures[url]
payload, exact_count, wildcard_count = builder.build('test')
rows = set(payload.splitlines())
assert exact_count == 2
assert wildcard_count == 2
assert 'example.com' in rows
assert '.example.com' in rows
assert '.sub.example.org' in rows
assert '*.example.com' not in rows
assert 'example.org' in rows
print('PASS: exact domains + wildcard-to-suffix conversion')
