import os.path

import pytest
from nomad.client import normalize_all, parse


@pytest.mark.skip(reason='Disabled test for now')
def test_schema_package():
    test_file = os.path.join('tests', 'data', 'test.archive.yaml')
    entry_archive = parse(test_file)[0]
    normalize_all(entry_archive)

    assert entry_archive.data.message == 'Hello Markus!'
