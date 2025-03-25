from typing import Optional

import numpy as np
import pytest
from nomad.client import normalize_all
from nomad.datamodel import EntryArchive

from nomad_parser_qutip.schema_packages.schema_package import (
    QuantumCircuit,
    QuantumObject,
    QuantumOperator,
    QuantumSimulation,
    QuantumState,
    QuantumSystem,
)

###############################################################################
# Test for QuantumObject
###############################################################################



@pytest.mark.parametrize(
    (
        "qtype",
        "data_array",
        "declared_shape",
        "expected_shape",
        "expected_dims",
        "expected_is_hermitian"
    ),
    [
        # 1) 'ket': no declared shape; shape and dims derived from data.
        (
            "ket",
            np.array([[1.0], [0.0]], dtype=np.complex128),
            None,
            [2, 1],
            [[2], [1]],
            None
        ),
        # 2) Hermitian operator (e.g. Pauli Z)
        (
            "oper",
            np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
            None,
            [2, 2],
            [[2], [2]],
            True
        ),
        # 3) Non-Hermitian operator
        (
            "oper",
            np.array([[0.0, 1.0], [0.0, 0.0]], dtype=np.complex128),
            None,
            [2, 2],
            [[2], [2]],
            False
        ),
        # 4) Mismatch shape: user declared [3, 1] but data is (2,1)
        (
            "ket",
            np.array([[1.0], [0.0]], dtype=np.complex128),
            [3, 1],
            [2, 1],
            [[2], [1]],
            None
        ),
    ],
)
def test_quantum_object(
    qtype: str,
    data_array: np.ndarray,
    declared_shape: Optional[list[int]],
    expected_shape: list[int],
    expected_dims: list[list[int]],
    expected_is_hermitian: Optional[bool],
    #warn_substring: Optional[str],
    #caplog: pytest.LogCaptureFixture,
):
    """
    Test a single QuantumObject.
    The warning check relies on the exact substring in the logged message.
    """
    archive = EntryArchive()

    qobj = QuantumObject()
    qobj.type = qtype
    qobj.data = data_array
    if declared_shape is not None:
        # Store declared shape as a NumPy array of type int32
        qobj.shape = np.array(declared_shape, dtype=np.int32)

    archive.data = qobj
    normalize_all(archive)

    norm_qobj = archive.data

    got_shape = list(norm_qobj.shape) if norm_qobj.shape is not None else None
    got_dims = (
        [list(row) for row in norm_qobj.dims] if norm_qobj.dims is not None else None
    )

    assert got_shape == expected_shape, (
        f'Expected shape {expected_shape}, got {got_shape}'
    )
    assert got_dims == expected_dims, f'Expected dims {expected_dims}, got {got_dims}'

    if qtype in ('oper', 'dm'):
        assert norm_qobj.is_hermitian == expected_is_hermitian, (
            f'Expected is_hermitian={expected_is_hermitian}, \
            got {norm_qobj.is_hermitian}'
        )

    # if warn_substring is not None:
    #     wmsgs = [r.message for r in caplog.records if r.levelname == "WARNING"]
    #     assert any(warn_substring in msg for msg in wmsgs), (
    #         f"Expected warning substring '{warn_substring}', found: {wmsgs}"
    #     )


###############################################################################
# Test for QuantumOperator
###############################################################################


def test_quantum_operator():
    """
    Test a QuantumOperator that references one QuantumObject.
    Ensures the QuantumObject is normalized properly.
    """
    archive = EntryArchive()

    op = QuantumOperator()
    op.name = 'PauliX'

    xobj = QuantumObject()
    xobj.type = 'oper'
    xobj.data = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    # For repeating sub-section, assign a list of QuantumObject instances.
    op.quantum_object = [xobj]

    archive.data = op
    normalize_all(archive)

    norm_op = archive.data
    assert norm_op.name == 'PauliX'
    assert len(norm_op.quantum_object) == 1

    norm_xobj = norm_op.quantum_object[0]
    x_shape = list(norm_xobj.shape) if norm_xobj.shape is not None else None
    assert x_shape == [2, 2], f'Expected shape [2,2], got {x_shape}'
    assert norm_xobj.is_hermitian is True, 'PauliX should be Hermitian.'


###############################################################################
# Test for QuantumState
###############################################################################


def test_quantum_state():
    """
    Test a QuantumState that references a single QuantumObject (ket).
    """
    archive = EntryArchive()

    qstate = QuantumState()
    qstate.label = 'MyKetState'

    ket_obj = QuantumObject()
    ket_obj.type = 'ket'
    ket_obj.data = np.array([[1.0], [0.0]], dtype=np.complex128)
    # For a non-repeating sub-section, assign the object directly.
    qstate.quantum_object = ket_obj

    archive.data = qstate
    normalize_all(archive)

    norm_state = archive.data
    assert norm_state.label == 'MyKetState'

    s_shape = list(norm_state.quantum_object.shape)
    s_dims = [list(row) for row in norm_state.quantum_object.dims]
    assert s_shape == [2, 1], f'Expected shape [2,1], got {s_shape}'
    assert s_dims == [[2], [1]], f'Expected dims [[2],[1]], got {s_dims}'


###############################################################################
# Test for QuantumCircuit
###############################################################################


def test_quantum_circuit():
    """
    Test a QuantumCircuit which has a circuit_representation field.
    """
    archive = EntryArchive()

    qcirc = QuantumCircuit()
    qcirc.circuit_representation = 'OPENQASM 2.0; qreg q[2]; x q[0];'

    archive.data = qcirc
    normalize_all(archive)

    norm_circ = archive.data
    assert 'OPENQASM' in norm_circ.circuit_representation


###############################################################################
# Test for QuantumSimulation
###############################################################################


def test_quantum_simulation():
    """
    Test a QuantumSimulation that references a QuantumSystem, QuantumOperator,
    and QuantumCircuit. Note: Do not assign a string to program (it is a SubSection).
    """
    archive = EntryArchive()

    sim = QuantumSimulation()
    # Do NOT assign sim.program a string; let it remain unset or properly constructed.
    # sim.program = "TestSimProgram"   <-- REMOVE THIS

    # Set up quantum_system
    qsys = QuantumSystem()
    qsys.name = 'My2Qubits'
    qsys.num_qubits = 2
    sim.quantum_system = qsys

    # Set up quantum_operator with a PauliZ object
    op = QuantumOperator()
    op.name = 'PauliZ'
    zobj = QuantumObject()
    zobj.type = 'oper'
    zobj.data = np.array([[1, 0], [0, -1]], dtype=np.complex128)
    op.quantum_object = [zobj]
    sim.quantum_operators = [op]

    # Set up quantum_circuit properly using a QuantumCircuit object
    qc = QuantumCircuit()
    qc.circuit_representation = 'OPENQASM 2.0; qreg q[2]; h q[0]; cx q[0],q[1];'
    sim.quantum_circuit = qc

    archive.data = sim
    normalize_all(archive)

    norm_sim = archive.data
    # Check simulation fields
    # (Do not check sim.program since we are not assigning it.)
    assert norm_sim.quantum_system.name == 'My2Qubits'
    NUMBER_OF_QUBITS = 2
    assert norm_sim.quantum_system.num_qubits == NUMBER_OF_QUBITS

    # Check quantum_operator -> PauliZ properties
    assert len(norm_sim.quantum_operators) == 1
    norm_op = norm_sim.quantum_operators[0]
    assert norm_op.name == 'PauliZ'
    z_shape = list(norm_op.quantum_object[0].shape)
    assert z_shape == [2, 2], f'Expected shape [2,2], got {z_shape}'
    assert norm_op.quantum_object[0].is_hermitian is True

    # Check quantum_circuit
    assert 'OPENQASM' in norm_sim.quantum_circuit.circuit_representation
