from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    pass

import numpy as np
from nomad.config import config
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import MEnum, Quantity, SchemaPackage

configuration = config.get_plugin_entry_point(
    'nomad_parser_qutip.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class Qobj(ArchiveSection):
    """
    A section to semantically represent a QuTiP Qobj.

    The main quantities are:
        dims   : Hilbert space dimensions.
        shape  : Shape of the underlying data.
        type   : MEnum to label the Qobj (e.g. 'ket', 'bra', 'oper', 'super').
        dtype  :  The data type indicator (for example, 'Dense' or 'csr') showing the
        numerical storage format.
        isherm : Boolean flag indicating whether an operator is Hermitian.
        data   : Matrix representing state or operator.
    """

    dims = Quantity(
        type=np.int32,
        shape=['*', '*'],
        description=(
            """List of dimensions keeping track of the tensor structure.
            Example for a ket: [[2], [1]]."""
        ),
    )

    shape = Quantity(
        type=np.int32,
        shape=['*'],
        description=(
            """Shape of the underlying data array.
            Example for a ket : [2, 1]."""
        ),
    )

    type = Quantity(
        type=MEnum('ket', 'bra', 'oper', 'super'),
        description=(
            """Type of the quantum object.
            'ket' for state vectors,
            'bra' for dual vectors,
            'oper' for operators,
            'super' for superoperators."""
        ),
    )

    dtype = Quantity(
        type=str,
        description=(
            """Numerical storage format of the Qobj's data. For example, 'Dense' for a
            full matrix or 'csr' for a compressed sparse row representation."""
        ),
    )

    isherm = Quantity(
        type=bool,
        description=("""Flag indicating whether the operator is Hermitian."""),
    )

    data = Quantity(
        type=np.float64,
        shape=['*', '*'],
        description=(
            """Sparse matrix characterizing the quantum object."""
        ),
    )

    def normalize(self, archive, logger) -> None:
        """
        Normalization method to check consistency of the Qobj.

        """
        super().normalize(archive, logger)
        # a simple example for the normalization function
        if self.data is not None:
            data_shape = list(self.data.shape)
            if self.shape != data_shape:
                logger.warning(
                    "Inconsistent shape!"
                )


m_package.__init_metainfo__()
