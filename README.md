# GoldenAge (GA)

GoldenAge combines an ERC-20 staking token with a lightweight blockchain
prototype that you can run from the terminal. The Solidity contract powers the
tokenomics, while the Python CLI demonstrates the foundational building blocks
of a public chain.

## Features

- **Initial supply:** 1,000,000,000,000 GA minted to the deployer on deployment.
- **Staking:** Users can deposit GA into the contract to begin earning rewards.
- **Rewards:** Every 1,000,000 GA staked earns 1 GA per hour, compounded when
  rewards are claimed or additional tokens are staked/unstaked.
- **Pausable:** The owner can pause or unpause staking-related functions.
- **Secure by design:** Uses OpenZeppelin implementations for ERC20, Ownable,
  ReentrancyGuard, and Pausable.

## Contract location

The Solidity source code is available in [`contracts/GoldenAge.sol`](contracts/GoldenAge.sol).

## Development

1. Install dependencies in your Hardhat/Foundry project that references this
   contract:

   ```bash
   npm install @openzeppelin/contracts
   ```

2. Import and compile the contract as part of your deployment scripts.

3. Deploy the contract with your preferred tooling. The deployer will receive
   the entire initial supply.

4. Interact with the staking functions (`stake`, `unstake`, and `claimRewards`)
   to manage locked balances and earned rewards.

## Terminal blockchain prototype

The `blockchain/goldenage_blockchain.py` module implements a self-contained
GoldenAge blockchain you can explore locally. It persists chain data to the
`goldenage_chain.json` file in the project root and exposes a CLI for common
operations.

### Prerequisites

- Python 3.9+

### Usage

1. Initialize the chain (creates the genesis block and saves the chain file):

   ```bash
   python blockchain/goldenage_blockchain.py init
   ```

2. Queue transactions prior to mining:

   ```bash
   python blockchain/goldenage_blockchain.py add-tx alice bob 250
   ```

3. Mine a block to confirm queued transactions and collect the block reward:

   ```bash
   python blockchain/goldenage_blockchain.py mine miner1
   ```

4. View the complete chain state:

   ```bash
   python blockchain/goldenage_blockchain.py status
   ```

5. Validate the chain integrity:

   ```bash
   python blockchain/goldenage_blockchain.py validate
   ```

These commands illustrate the essential lifecycle of a blockchain: creating a
genesis block, propagating transactions, mining new blocks, and maintaining
consensus through validation.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
