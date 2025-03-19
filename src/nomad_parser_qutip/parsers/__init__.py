from nomad.config.models.plugins import ParserEntryPoint

# from pydantic import Field


class QutipEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_parser_qutip.parsers.parser import QutipParser

        return QutipParser(**self.dict())


parser_entry_point = QutipEntryPoint(
    name='QuTiP Parser',
    description='Parser for QuTiP outputs.',
    # The following is a regular expression for the name of a potential mainfile.
    # If this expression is given:
    # the parser is only considered for a file, if the expression matches.
    # mainfile_name_re='.*\.json.*',
    mainfile_name_re=r'.*\.json$',
    # mainfile_contents_re=r'QuTiP',
)
