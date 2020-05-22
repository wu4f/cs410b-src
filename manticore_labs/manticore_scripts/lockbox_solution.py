'''
To solve this level, you'll need to find the timestamp of your contract
You can find this by searching ropsten.etherscan.io for the contract
    then viewing the transaction that created the contract
There should be a date for this transaction
You'll need to convert that date into a unix timestamp to put in this file
This can be done with the linux 'date' utility in your docker container:
$ date -d 'Mar-13-2019 08:09:17 PM +UTC' +%s
1552507757
You'll also need to fill in the same blanks from the previous level
There is a section towards the end of the code lab to help you find the correct timestamp
'''

from manticore.ethereum import ManticoreEVM
import binascii
from MEVMCustomState import MEVMCustomState
from manticore.core.smtlib import ConstraintSet
from manticore.platforms import evm
from manticore.ethereum.state import State
import sys

from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
sol_file = sys.argv[3] if len(sys.argv)>3 else "../SI_ctf_levels/LockBox.sol"
gas = 100000
contract_balance = ???

with open(sol_file, "r") as f:
    contract_src = f.read()

# make the ethereum world state
initial_constraints = ConstraintSet() # start with no contraints
initial_world = evm.EVMWorld(initial_constraints, timestamp=???) # create a custom world with the specified timestamp
initial_state = State(initial_constraints, initial_world)
# instantiate manticore's Ethereum Virtual Machine
# this uses a custom Manticore engine that allows for an initial_state as a parmeter
m = MEVMCustomState(initial_state=initial_state)

user_account = m.create_account(address=from_address, balance=contract_balance)
contract_account = m.solidity_create_contract(
    contract_src,
    contract_name="Lockbox1", # new contract name for this level
    owner=user_account,
    balance=contract_balance,
    args=(0,0)
    )

sym_args = m.make_symbolic_buffer(4+???) # 4 bytes for the function signature hash and ??? more for a uint256
m.transaction(caller=user_account, address=contract_account.address, data=sym_args, value=0, gas=10000000)

for state in m.running_states:
    world = state.platform
    if state.can_be_true(world.get_balance(user_account.address) == contract_balance):
      state.constraints.add(world.get_balance(user_account.address) == contract_balance)
      conc_args = state.solve_one(sym_args)
      print("eth.sendTransaction({data:\"0x"+binascii.hexlify(conc_args).decode('utf-8')+"\", from:\""+hex(from_address)+"\", to:\""+hex(si_level_address)+"\", gas:"+str(gas)+"})")
      sys.exit(0)

print("No valid states found")
