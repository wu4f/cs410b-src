from manticore.ethereum import ManticoreEVM
from manticore.utils.helpers import PickleSerializer
from manticore.core.manticore import ManticoreBase
import binascii
from manticore.core.smtlib import ConstraintSet
from manticore.platforms import evm
from manticore.ethereum.state import State
import sys

class MEVMCustomState(ManticoreEVM):
    def __init__(self, procs=10, workspace_url: str=None, policy: str='random', initial_state=None):
        # This was copied from the manticore source, but modified to allow for a custom initial state
        """
        A Manticore EVM manager
        :param procs:, number of workers to use in the exploration
        :param workspace_url: workspace folder name
        :param policy: scheduling priority
        """
        self._accounts = dict()
        self._serializer = PickleSerializer()

        self._config_procs = procs
        # Make the constraint store
        constraints = ConstraintSet()
        if initial_state == None:
            # Make the constraint store
            constraints = ConstraintSet()
            # make the ethereum world state
            world = evm.EVMWorld(constraints)
            initial_state = State(constraints, world)
        ManticoreBase.__init__(self, initial_state, workspace_url=workspace_url, policy=policy)

        self.constraints = ConstraintSet()
        self.detectors = {}
        self.metadata: Dict[int, SolidityMetadata] = {}

        # The following should go to manticore.context so we can use multiprocessing
        self.context['ethereum'] = {}
        self.context['ethereum']['_saved_states'] = set()
        self.context['ethereum']['_final_states'] = set()
        self.context['ethereum']['_completed_transactions'] = 0
        self.context['ethereum']['_sha3_states'] = dict()
        self.context['ethereum']['_known_sha3'] = set()

        self._executor.subscribe('did_load_state', self._load_state_callback)
        self._executor.subscribe('will_terminate_state', self._terminate_state_callback)
        self._executor.subscribe('did_evm_execute_instruction', self._did_evm_execute_instruction_callback)
        self._executor.subscribe('did_read_code', self._did_evm_read_code)
        self._executor.subscribe('on_symbolic_sha3', self._on_symbolic_sha3_callback)
        self._executor.subscribe('on_concrete_sha3', self._on_concrete_sha3_callback)
        self.subscribe('will_generate_testcase', self._generate_testcase_callback)
