// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/// @title GoldenAge - GA staking token with reward minting
/// @notice Provides basic staking with time-based rewards and owner-controlled pause
contract GoldenAge is ERC20, Ownable, ReentrancyGuard, Pausable {
    uint8 private constant TOKEN_DECIMALS = 18;
    uint256 private constant INITIAL_SUPPLY = 1_000_000_000_000 * 10 ** TOKEN_DECIMALS;
    uint256 public constant REWARD_RATE = 10 ** TOKEN_DECIMALS / 1_000_000; // 1 token per hour per 1M staked

    struct Stake {
        uint256 amount;
        uint256 timestamp;
        uint256 rewards;
    }

    mapping(address => Stake) public stakes;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);

    constructor() ERC20("GoldenAge", "GA") Ownable(msg.sender) {
        _mint(msg.sender, INITIAL_SUPPLY);
    }

    function decimals() public pure override returns (uint8) {
        return TOKEN_DECIMALS;
    }

    function stake(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");

        updateRewards(msg.sender);

        _transfer(msg.sender, address(this), amount);

        Stake storage userStake = stakes[msg.sender];
        userStake.amount += amount;
        userStake.timestamp = block.timestamp;

        emit Staked(msg.sender, amount);
    }

    function unstake(uint256 amount) external nonReentrant whenNotPaused {
        Stake storage userStake = stakes[msg.sender];
        require(userStake.amount >= amount, "Insufficient staked balance");

        updateRewards(msg.sender);

        userStake.amount -= amount;
        _transfer(address(this), msg.sender, amount);

        if (userStake.amount == 0) {
            userStake.timestamp = 0;
        } else {
            userStake.timestamp = block.timestamp;
        }

        emit Unstaked(msg.sender, amount);
    }

    function claimRewards() external nonReentrant whenNotPaused {
        updateRewards(msg.sender);

        Stake storage userStake = stakes[msg.sender];
        uint256 rewardsToClaim = userStake.rewards;
        require(rewardsToClaim > 0, "No rewards to claim");

        userStake.rewards = 0;
        _mint(msg.sender, rewardsToClaim);

        emit RewardsClaimed(msg.sender, rewardsToClaim);
    }

    function stakedAmount(address account) external view returns (uint256) {
        return stakes[account].amount;
    }

    function viewRewards(address account) external view returns (uint256) {
        return stakes[account].rewards;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function updateRewards(address user) internal {
        Stake storage userStake = stakes[user];

        if (userStake.amount == 0 || userStake.timestamp == 0) {
            userStake.timestamp = block.timestamp;
            return;
        }

        if (block.timestamp <= userStake.timestamp) {
            return;
        }

        uint256 hoursPassed = (block.timestamp - userStake.timestamp) / 1 hours;
        if (hoursPassed == 0) {
            return;
        }

        uint256 earnedRewards = (userStake.amount * REWARD_RATE * hoursPassed) / 10 ** TOKEN_DECIMALS;
        userStake.rewards += earnedRewards;
        userStake.timestamp = block.timestamp;
    }
}
