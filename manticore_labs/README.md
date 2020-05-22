# Manticore Ethereum Codelab
Welcome to the smart contract symbolic execution code lab  
In this lab, you'll be using trail-of-bits' symbolic executor "manticore" (in the `~/manticore` directory)  
You'll also use geth to run your exploits (in `~/go-ethereum`)  
Skeleton code for the solutions will be in `manticore_scripts` with the first level already completed (`~/manticore_scripts/donation_solution.py`)  
The rest of the code will have some blanks (marked "???") that you'll need to fill in  

The google doc for this is located here:  
https://docs.google.com/document/d/1EDqbYwdv4yfmCB2Tme6PtTcMjyAf8pKLKdq4up3T4Fk/edit#  
This .docx in this repo will probably be an older version  

# First Level
Go ahead and run the first level with your address and the CTF address:

```
python3 ~/manticore_scripts/donation_solution.py 0xyouraddress 0xctfcontractaddress
```

to run geth:
```
cd ~/go-ethereum
./build/bin/geth --syncmode light --testnet --rpcapi eth,web3,personal --rpc # this will start a light geth node on your machine
# in another window: (use tmux's `Ctrl+b, c` to create a new bash shell window, then `Ctrl+b, n` to toggle between them)
./build/bin/geth attach http://localhost:8545/ # this will attach a console to it
> personal.importRawKey("enteryourprivatekeyfrommetamaskherea8263gd8a2g38dga283dga8372gda","YourAmazinglySecurePassword")
> eth.sendTransaction({from:"your address", data:"data from manticore", to:"security innovations ctf", gas:10000, gasPrice:10000000})
```
if the transaction takes a long time, up the gas price
The command will show a transaction hash that you can paste into ropsten.etherscan.io to watch your exploit complete
It should drain the contract of all of it's ether and reimburse you

# Other levels
Each level builds on knowledge from the previous and are meant to be played in this order:  
Donation  
PiggyBank  
LockBox  
SimpleToken (will be used to exploit SITokenSale)  
TrustFund  

Once you've completed exploiting the Donation level with manticore, move on to look at `piggybank_solution.py` which will have instruction in the file

The password for the auditor user is 'manticore' (needed for sudo)
