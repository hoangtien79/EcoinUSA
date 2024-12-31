// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <9.1.5;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract ECoin is ERC20, Ownable, ReentrancyGuard, Pausable {
    // Total supply of the token
    uint256 private constant INITIAL_SUPPLY = 1000000000000 * 10**decimals(); // 1 trillion tokens

    struct Stake {
        uint256 amount;
        uint256 timestamp;
        uint256 rewards;
    }

    // Mapping to store staking information per user
    mapping(address => Stake) public stakes;

    // Reward rate (1 token for every 1 million tokens staked per hour)
    uint256 public constant REWARD_RATE = 1 * 10**decimals() / 1_000_000; // 1 token per hour for 1 million staked

    // Events
    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);

    // Constructor to initialize the token with the total supply
    constructor() ERC20("ECoin", "ECN") {
        _mint(msg.sender, INITIAL_SUPPLY); // Mint the total supply to the deployer's address
    }

    // Function to stake tokens
    function stake(uint256 amount) public nonReentrant whenNotPaused {
        require(amount > 0, "Amount should be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance to stake");

        // Update rewards before staking
        updateRewards(msg.sender);

        // Transfer tokens to the contract for staking
        _transfer(msg.sender, address(this), amount);

        // Update staking information
        Stake storage userStake = stakes[msg.sender];
        userStake.amount += amount;
        userStake.timestamp = block.timestamp;

        emit Staked(msg.sender, amount); // Emit Staked event
    }

    // Unstaking function
    function unstake(uint256 amount) public nonReentrant whenNotPaused {
        Stake storage userStake = stakes[msg.sender];
        require(userStake.amount >= amount, "Insufficient staked balance to unstake");

        // Update rewards before unstaking
        updateRewards(msg.sender);

        // Transfer staked tokens back to the user
        userStake.amount -= amount;
        _transfer(address(this), msg.sender, amount);

        emit Unstaked(msg.sender, amount); // Emit Unstaked event
    }

    // Update rewards for a user
    function updateRewards(address user) internal {
        Stake storage userStake = stakes[user];

        // Calculate how many hours have passed since the last update
        uint256 hoursPassed = (block.timestamp - userStake.timestamp) / 1 hours;

        // Calculate the rewards earned
        if (userStake.amount > 0 && hoursPassed > 0) {
            // Rewards based on the amount staked and hours passed
            uint256 earnedRewards = (userStake.amount * REWARD_RATE * hoursPassed) / 10**decimals();
            userStake.rewards += earnedRewards;
            userStake.timestamp = block.timestamp; // Reset the timestamp
        }
    }

    // Claim rewards function
    function claimRewards() public nonReentrant whenNotPaused {
        updateRewards(msg.sender); // Update rewards before claiming

        Stake storage userStake = stakes[msg.sender];
        uint256 rewardsToClaim = userStake.rewards;
        require(rewardsToClaim > 0, "No rewards to claim");

        // Reset the rewards to zero and transfer the rewards to the user
        userStake.rewards = 0;
        _mint(msg.sender, rewardsToClaim); // Mint new tokens as rewards

        emit RewardsClaimed(msg.sender, rewardsToClaim); // Emit RewardsClaimed event
    }

    // Function to view staked amount
    function stakedAmount(address account) public view returns (uint256) {
        return stakes[account].amount;
    }

    // Function to view rewards
    function viewRewards(address account) public view returns (uint256) {
        return stakes[account].rewards;
    }

    // Enable or disable contract functions (Pausable)
    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    // Transfer functions are inherited from ERC20
}
