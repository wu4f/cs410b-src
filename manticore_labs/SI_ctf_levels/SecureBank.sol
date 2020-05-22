pragma solidity 0.4.24;



contract SimpleBank{

    mapping(address => uint256) public balances;

    constructor(address _ctfLauncher, address _player) public payable
        
    {
        balances[msg.sender] = msg.value;
    }

    function deposit(address _user) public payable{
        balances[_user] += msg.value;
    }

    function withdraw(address _user, uint256 _value) public{
        require(_value<=balances[_user], "Insufficient Balance");
        balances[_user] -= _value;
        msg.sender.transfer(_value);
    }

    function () public payable{
        deposit(msg.sender);
    }

}

contract MembersBank is SimpleBank{

    mapping(address => string) public members;

    constructor(address _ctfLauncher, address _player) public payable
        SimpleBank(_ctfLauncher, _player)
    {
    }

    function register(address _user, string _username) public{
        members[_user] = _username;
    }

    modifier isMember(address _user){
        bytes memory username = bytes(members[_user]);
        require(username.length != 0, "Member Must First Register");
        _;
    }

    function deposit(address _user) public payable isMember(_user){
        super.deposit(_user);
    }

    function withdraw(address _user, uint256 _value) public isMember(_user){
        super.withdraw(_user, _value);
    }

}

contract SecureBank is MembersBank{

    constructor(address _ctfLauncher, address _player) public payable
        MembersBank(_ctfLauncher, _player)
    {
    }

    function deposit(address _user) public payable{
        require(msg.sender == _user, "Unauthorized User");
        require(msg.value < 100 ether, "Exceeding Account Limits");
        require(msg.value >= 1 ether, "Does Not Satisfy Minimum Requirement");
        super.deposit(_user);
    }

    function withdraw(address _user, uint8 _value) public{
        require(msg.sender == _user, "Unauthorized User");
        require(_value < 100, "Exceeding Account Limits");
        require(_value >= 1, "Does Not Satisfy Minimum Requirement");
        super.withdraw(_user, _value * 1 ether);
    }

    function register(address _user, string _username) public{
        require(bytes(_username).length!=0, "Username Not Enough Characters");
        require(bytes(_username).length<=20, "Username Too Many Characters");
        super.register(_user, _username);
    }
}