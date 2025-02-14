import logging

from nomad.datamodel import EntryArchive

from nomad_parser_qutip.parsers.parser import QutipParser


def test_parse_file():
    parser = QutipParser()
    archive = EntryArchive()
    parser.parse('tests/data/example.out', archive, logging.getLogger())

    assert archive.workflow2.name == 'test'
