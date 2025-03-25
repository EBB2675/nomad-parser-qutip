import logging

import pytest
from nomad.datamodel import EntryArchive

from nomad_parser_qutip.parsers.parser import QutipParser


@pytest.mark.skip(reason='Disabled test for now')
def test_parse_file():
    parser = QutipParser()
    archive = EntryArchive()
    parser.parse('tests/data/simulation_driven.json', archive, logging.getLogger())

    assert archive.workflow2.name == 'test'
