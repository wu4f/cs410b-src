pragma solidity 0.4.24;



contract Lockbox1{

    uint256 private pin;

    constructor(address _ctfLauncher, address _player) public payable
        
    {
        pin = now%10000;
    }
    
    function unlock(uint256 _pin) external{
        require(pin == _pin, "Incorrect PIN");
        msg.sender.transfer(address(this).balance);
    }

}