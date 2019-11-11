# Utilities
import logging

# Sawtooth SDK
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

# Skltn protos
from protobuf.task_pb2 import *
from protobuf.payload_pb2 import *
from protobuf.project_node_pb2 import *

# Skltn addressing specs
import addressing

LOGGER = logging.getLogger(__name__)


class TodoTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return addressing.FAMILY_NAME

    @property
    def family_versions(self):
        return ['0.1']

    @property
    def namespaces(self):
        return [addressing.NAMESPACE]

    def apply(self, transaction, state):
        '''
        A Payload consists of a timestamp, an action tag, and
        attributes corresponding to various actions (create_asset,
        touch_asset, etc).  The appropriate attribute will be selected
        depending on the action tag, and that information plus the 
        timestamp and the public key with which the transaction was signed
        will be passed to the appropriate handler function
        unpack_transaction gets the signing key, the timestamp, and the 
        appropriate payload attribute and handler function
        '''
        # TO DO : check that timestamp is valid before calling handler.
        signer, timestamp, payload, handler = _unpack_transaction(transaction, state)

        # note that handler will be chosen by what was given to unpack
        handler(payload, signer, timestamp, state)


# Handler functions

def _create_project(payload, signer, timestamp, state):
    ''' Creates a project metanode and allows tasks to be created

        Takes the project name and makes an address given the METANODE tag 
        that name, and the txn family.  A project name must be unique, the 
        txn will fail if it is not.  
    '''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_create_project(..) NOT IMPLEMENTED")
    pass


def _create_task(payload, signer, timestamp, state):
    ''' Creates a task node and adds the task to the project's list of task names

        Takes a task_name and description.  Makes an address given the project
        name and the task name. Each task name must be unique in the
        project.
    '''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_create_task(..) NOT IMPLEMENTED")
    pass


def _progress_task(payload, signer, timestamp, state):
    ''' Progress task moves a task along the four possible stages.

        Takes a project name and a task name.  The four stages are
        NOT_STARTED, IN_PROGRESS, TESTING, and DONE.  Moves the 
        task's stage from its current stage to the next if possible.
        It is not possible to progress beyond DONE. 
    '''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_progress_task(..) NOT IMPLEMENTED")
    pass


def _edit_task(payload, signer, timestamp, state):
    ''' Edit a task's description.

        Takes a project name, task name, and task description.
        Only an authorized contributor can make changes, and 
        the project/task must exist.
    '''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_edit_task(..) NOT IMPLEMENTED")
    pass


def _add_user(payload, signer, timestamp, state):
    ''' Adds a public key to the list of authorized keys in the project metanode

        Payload should include project name and the new public key
        Transaction must be signed by project owner (0th element of authorized keys list)
    '''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_add_user(..) NOT IMPLEMENTED")
    pass


def _unpack_transaction(transaction, state):
    '''Return the transaction signing key, the SCPayload timestamp, the
    appropriate SCPayload action attribute, and the appropriate
    handler function (with the latter two determined by the constant
    TYPE_TO_ACTION_HANDLER table.
    '''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_unpack_transaction(..) NOT IMPLEMENTED")
    pass



def _get_container(state, address):
    '''Returns the container at a given address from state'''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_get_container(..) NOT IMPLEMENTED")
    pass


def _set_container(state, address, container):
    '''Sets the state at a certain address to a given container'''
    # DELETE THIS PRINT STATEMENT ONCE FULFILLED
    print("_set_container(..) NOT IMPLEMENTED")
    pass


def _get_project_node(state, project_name):
    '''Returns project metanode of give project name'''
    # make address of project metanode
    project_node_address = addressing.make_project_node_address(project_name)
    # pull the project metanode container from this address
    project_container = _get_container(state, project_node_address)
    # find metanode with correct project name and return it
    for project_node in project_container.entries: #find project with correct name
        if project_node.project_name == project_name:
            return project_node
    # in the case that no project of this name exists, invalidate the transaction
    raise InvalidTransaction(
        "This project does not exist")


def _verify_contributor(state, signer, project_name):
    ''' Checks to see if a public key belongs to an authorized contributor of the project.

        Takes the state provided from the apply function, the public key of the signer,
        and the name of the project to check.
        Invalidates the transaction if the public key is not authorized.
    '''
    # get list of authorized contributor public keys from project node
    auth_keys = _get_project_node(state,project_name).public_keys
    # checks if the public key of the signer is in the list
    # of authorized keys
    if not any(signer == key for key in auth_keys):
        raise InvalidTransaction(
            'Signer not authorized as a contributor')
