'''
To solve this level, we'll need to fill in several contract values
similar to prior levels, including the amount that is needed to play
the lottery
'''
from manticore.ethereum import ABI, ManticoreEVM
import sys

# Parse arguments
#   arg1 = from_address = Your wallet address
#   arg2 = si_level_address = Your CTF level address
#   arg3 = sol_file = CTF level source code to symbolically execute
from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
sol_file = sys.argv[3] if len(sys.argv)>3 else "../SI_ctf_levels/Lottery.sol"
gas = 100000

# Set the amount of ETH you want to obtain from the contract
contract_balance = ???

# Set the amount of ETH we need to send in our transaction (msg.value) to play.
msg_value = ???

# read in the contract source
with open(sol_file, "r") as f:
    contract_src = f.read()

# instantiate manticore's Ethereum Virtual Machine
m = ManticoreEVM()
# m.verbosity(0)

# Create an account for your wallet address on the EVM with funds to
# both deploy the contract and to play the lottery
user_account = m.create_account(address=from_address, balance=contract_balance+msg_value)

# Create the Lottery CTF level contract on the EVM using wallet
contract_account = m.solidity_create_contract(
    contract_src,
    contract_name="Lottery",
    owner=user_account,
    balance=contract_balance,
    args=(0,0)
)

# Make symbolic buffer to hold msg.data and ask Manticore to calculate the "winning" value
# 4 bytes for the function signature hash and ??? more for a uint256
sym_args = m.make_symbolic_buffer(???)

# Issue a symbolic transaction to the EVM by setting msg.data to symbolic buffer
#   as well as msg.value to the amount needed to play
m.transaction(
    caller=user_account,
    address=contract_account.address,
    data=sym_args,
    value=msg_value,
    gas=gas
)

# Symbolically execute program to find an exploit that obtains our funds back.
for state in m.running_states:
    # this is just some silly manticore stuff
    world = state.platform
    # Check if funds can be retrieved
    if state.can_be_true(world.get_balance(user_account.address) == contract_balance + msg_value):
      # If so, add constraint
      #   Then concretize symbolic buffer to provide one solution
      state.constraints.add(world.get_balance(user_account.address) == contract_balance + msg_value)
      conc_args = state.solve_one(sym_args)
      # Print out our transaction to send to win
      print("eth.sendTransaction({data:\"0x"+binascii.hexlify(conc_args).decode('utf-8')+"\", from:\""+ hex(from_address) + "\", to:\""+hex(si_level_address)+"\", value:"+str(msg_value)+", gas:"+str(gas)+"})")
      print(f'''eth.sendTransaction({{data:"0x{conc_args.hex()}", from:"{hex(from_address)}", to:"{hex(si_level_address)}", value: {value}, gas:{gas}}})''')
      sys.exit(0)
    print('No state found')