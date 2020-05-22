pragma solidity 0.4.24;



// https://github.com/OpenZeppelin/openzeppelin-solidity/blob/v1.8.0/contracts/token/ERC20/StandardToken.sol


/**
 * @title SafeMath
 * @dev Math operations with safety checks that revert on error
 */
library SafeMath {

  /**
  * @dev Multiplies two numbers, reverts on overflow.
  */
  function mul(uint256 a, uint256 b) internal pure returns (uint256) {
    // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
    // benefit is lost if 'b' is also tested.
    // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
    if (a == 0) {
      return 0;
    }

    uint256 c = a * b;
    require(c / a == b);

    return c;
  }

  /**
  * @dev Integer division of two numbers truncating the quotient, reverts on division by zero.
  */
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b > 0); // Solidity only automatically asserts when dividing by 0
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold

    return c;
  }

  /**
  * @dev Subtracts two numbers, reverts on overflow (i.e. if subtrahend is greater than minuend).
  */
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b <= a);
    uint256 c = a - b;

    return c;
  }

  /**
  * @dev Adds two numbers, reverts on overflow.
  */
  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    require(c >= a);

    return c;
  }

  /**
  * @dev Divides two numbers and returns the remainder (unsigned integer modulo),
  * reverts when dividing by zero.
  */
  function mod(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b != 0);
    return a % b;
  }
}

contract SIToken {
  using SafeMath for uint256;
  mapping(address => uint256) balances;
  uint public decimals = 18;
  uint public INITIAL_SUPPLY = 1000 * (10 ** decimals);
  constructor() public{
    balances[this] = INITIAL_SUPPLY;
  }
  function transfer(address _to, uint256 _value) internal returns (bool) {
    require(_to != address(0));
    require(_value <= balances[msg.sender]);
    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(_value);
    return true;
  }
}

contract SITokenSale is SIToken {

    uint256 public feeAmount;
    uint256 public etherCollection;
    address public developer;

    constructor(address _ctfLauncher, address _player) public payable
        
    {
        feeAmount = 10 szabo; 
        developer = msg.sender;
        purchaseTokens(msg.value);
    }

    function purchaseTokens(uint256 _value) internal{
        require(_value > 0, "Cannot Purchase Zero Tokens");
        require(_value < balances[this], "Not Enough Tokens Available");
        balances[msg.sender] += _value - feeAmount;
        balances[this] -= _value;
        balances[developer] += feeAmount; 
        etherCollection += msg.value;
    }

    function () payable external{
        purchaseTokens(msg.value);
    }

    // Allow users to refund their tokens for half price ;-)
    function refundTokens(uint256 _value) external{
        require(_value>0, "Cannot Refund Zero Tokens");
        transfer(this, _value);
        etherCollection -= _value/2;
        msg.sender.transfer(_value/2);
    }

    function withdrawEther() external{
        require(msg.sender == developer, "Unauthorized: Not Developer");
        require(balances[this] == 0, "Only Allowed Once Sale is Complete");
        msg.sender.transfer(etherCollection);
    }

}
