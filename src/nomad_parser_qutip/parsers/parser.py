from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )

import json

import numpy as np
from nomad.config import config
from nomad.parsing.file_parser.mapping_parser import MappingParser, MetainfoParser
from nomad.parsing.parser import MatchingParser

from nomad_parser_qutip.schema_packages.schema_package import QuantumSimulation

configuration = config.get_plugin_entry_point(
    'nomad_parser_qutip.parsers:parser_entry_point'
)


class JSONParser(MappingParser):
    """
    A minimal JSON-based MappingParser, analogous to XMLParser but for JSON.
    """

    value_key = '__value'
    attribute_prefix = '@'

    def load_file(self):
        with open(self.filepath) as f:
            self.data_object = json.load(f)
        return self.data_object

    def to_dict(self, **kwargs) -> dict:
        """
        Return a dictionary representation of data_object. If the file is
        already JSON, data_object may simply be a dict, so just return it.
        """
        if isinstance(self.data_object, dict):
            return self.data_object
        return {}

    def from_dict(self, data: dict, **kwargs):
        """
        Set the parser’s internal data_object from a given dictionary.
        """
        self.data_object = data

    def get_program(self, source: dict[str, Any], **kwargs) -> dict[str, Any]:
        return source.get('program', {'name': '', 'version': ''})

    def get_system(self, source: dict[str, Any], **kwargs) -> dict[str, Any]:
        return {'name': source.get('simulation_name', 'HASSIKTR')}

    def get_operators(source: dict, **kwargs) -> dict:
        """
        Process operator data from the JSON.

        For each operator, it returns a dictionary with two keys:
        - "name": the operator name (string)
        - "quantum_object": a dictionary with fields required by QuantumObject:
            "dims", "shape", "type", "storage_format", "is_hermitian", and "data".

        In particular, if the operator data contains a "matrix" key
        (with "re" and "im"),
        these are combined into a single complex matrix stored under "data".

        The function returns a dictionary with a single key "quantum_operators"
        whose value is the list.
        """
        ops = source.get('operators', {})
        processed = []
        for op_name, op in ops.items():
            qobj = {}
            if 'dims' in op:
                qobj['dims'] = op['dims']
                try:
                    # Assume dims is of the form [[n],[m]] and derive shape as [n, m]
                    dimension = 2
                    if len(op['dims']) == dimension:
                        qobj['shape'] = [int(op['dims'][0][0]), int(op['dims'][1][0])]
                    else:
                        qobj['shape'] = []
                except Exception:
                    qobj['shape'] = []
            qobj['type'] = op.get('type', 'oper')
            qobj['storage_format'] = op.get('storage_format', 'Dense')
            qobj['is_hermitian'] = op.get('is_hermitian', True)
            if 'matrix' in op:
                matrix_dict = op['matrix']
                re = np.array(matrix_dict.get('re', []))
                im = np.array(matrix_dict.get('im', []))
                qobj['data'] = (re + 1j * im).tolist()
            else:
                qobj['data'] = op.get('data', None)
            processed.append({'name': op_name, 'quantum_object': qobj})
        return {'quantum_operators': processed}


class QutipParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger,
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        # Create your JSON parser and assign the file path
        json_parser = JSONParser()
        json_parser.filepath = mainfile

        data_object = QuantumSimulation()

        # Create a MetainfoParser using the QuantumSimulation instance
        data_parser = MetainfoParser(data_object=data_object)
        data_parser.annotation_key = 'info'

        # Convert from JSON parser to MetainfoParser
        json_parser.convert(data_parser)

        # Store the resulting data object in the archive
        archive.data = data_parser.data_object

        # Optionally close the parsers
        data_parser.close()
        json_parser.close()
