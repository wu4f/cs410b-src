pragma solidity 0.4.24;

contract SimpleToken {

    uint256 public tokensOwned;
    uint256 public fee;
    uint256 private secretMoney; // no one will ever get this money

    constructor() public payable
    {
      fee = 10 szabo;
      secretMoney = msg.value;
    }

    function () payable {
      uint256 val = msg.value;
      require(val > 0, "Cannot Purchase Zero Tokens");
      val -= fee;
      secretMoney += fee; // give us our cut
      tokensOwned += val;
    }
    function refundTokens(uint256 toks) {
      require(toks <= tokensOwned);
      require(toks/2 <= this.balance);
      tokensOwned -= toks;
      msg.sender.transfer(toks/2);
    }
}
