'''
To solve this level, you'll need to find the timestamp of your contract on
ropsten.etherscan.io then convert it to a unix timestamp to put in this file.
This can be done with the linux 'date' utility
$ date -d 'Mar-13-2019 08:09:17 PM +UTC' +%s
1552507757
You'll also need to fill in the same blanks from the previous level
'''
from manticore.ethereum import ManticoreEVM
from MEVMCustomState import MEVMCustomState
from manticore.core.smtlib import ConstraintSet
from manticore.platforms import evm
from manticore.ethereum.state import State
import sys

# Parse arguments
#   arg1 = from_address = Your wallet address
#   arg2 = si_level_address = Your CTF level address
#   arg3 = sol_file = CTF level source code to symbolically execute
from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
sol_file = sys.argv[3] if len(sys.argv)>3 else "../SI_ctf_levels/LockBox.sol"
gas = 1000000

# Set the amount of ETH you want to obtain from the contract
contract_balance = ???

# Read in the contract source
with open(sol_file, "r") as f:
    contract_src = f.read()

# Create the initial Ethereum world state at the time the Lockbox
#   CTF level is created
#   1. Start with no constraints
initial_constraints = ConstraintSet()
#   2. Then, create custom world state with specified Unix timestamp
initial_world = evm.EVMWorld(initial_constraints, timestamp=???)
initial_state = State(initial_constraints, initial_world)

# Instantiate Manticore's Symbolic Ethereum Virtual Machine
#   and specify its initial_state as the one created
m = MEVMCustomState(initial_state=initial_state)

# Create an account for your wallet address on the EVM.
user_account = m.create_account(address=from_address, balance=contract_balance)

# Create the Lockbox CTF level contract on the EVM using wallet
contract_account = m.solidity_create_contract(
    contract_src,
    contract_name="Lockbox1",
    owner=user_account,
    balance=contract_balance,
    args=(0,0)
)

# Make symbolic buffer to hold msg.data and ask Manticore to calculate the "winning" value
# 4 bytes for the function signature hash and ??? more for a uint256
sym_args = m.make_symbolic_buffer(4+???) 

# Issue a symbolic transaction to the EVM by setting msg.data to symbolic buffer
m.transaction(
    caller=user_account,
    address=contract_account.address,
    data=sym_args,
    value=0,
    gas=gas
)

# Symbolically execute program to find an exploit that obtains our funds back.
for state in m.running_states:
    world = state.platform
    # Check if funds can be retrieved
    if state.can_be_true(world.get_balance(user_account.address) == contract_balance):
      # If so, add constraint
      #   Then concretize symbolic buffer to provide one solution
      state.constraints.add(world.get_balance(user_account.address) == contract_balance)
      conc_args = state.solve_one(sym_args)
      # Print out our transaction to send to win
      print(f'''eth.sendTransaction({{data:"0x{conc_args.hex()}", from:"{hex(from_address)}", to:"{hex(si_level_address)}", gas:{gas}}})''')
      sys.exit(0)

print("No valid states found")