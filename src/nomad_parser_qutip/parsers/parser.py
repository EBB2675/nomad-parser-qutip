from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.parsing.parser import MatchingParser
from nomad_simulations.schema_packages.general import Program, Simulation

configuration = config.get_plugin_entry_point(
    'nomad_parser_qutip.parsers:parser_entry_point'
)


class QutipParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        simulation = Simulation()
        # here we are populating the archive with the program name
        simulation.program = Program(name='QuTiP')

        # an example Qobj instance:
        # qobj_instance = Qobj(
        # dims=[[2], [1]],
        # shape=[2, 1],
        # type='ket',
        # dtype='Dense',
        # isherm=True,
        # data=np.array([[1.0], [0.0]]),
        # )

        # put the simulation section into archive data
        archive.data = simulation
