# Funbuy Token

This repository contains the Funbuy ERC-20 token contract (`contracts/FunbuyToken.sol`).
The steps below walk you through deploying the token to Ethereum (or any EVM
network) and then listing it for trading on Uniswap.

## 1. Deploy the contract with Remix

1. Go to [https://remix.ethereum.org](https://remix.ethereum.org) and create a new
   file named `FunbuyToken.sol`. Paste in the contents of
   [`contracts/FunbuyToken.sol`](contracts/FunbuyToken.sol).
2. On the **Solidity Compiler** tab select compiler version `0.8.20` (or any
   0.8.20+ build) and click **Compile FunbuyToken.sol**.
3. Switch to the **Deploy & Run** tab.
   - Environment: `Injected Provider - Metamask` (or another wallet provider)
   - Account: the wallet that should receive the initial supply.
   - Contract: `FunbuyToken`.
4. Click **Deploy** and confirm the transaction in your wallet. The deploying
   wallet receives the full `1_260_000_000 * 10^18` FUNBUY supply.
5. After confirmation, copy the deployed contract address from Remix or from your
   wallet's transaction history.

## 2. Deploy with Hardhat (alternative CLI workflow)

1. Install dependencies in an empty folder:

   ```bash
   npm init -y
   npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv
   npx hardhat
   ```

   When prompted, choose the **JavaScript project** template and let Hardhat
   install the sample files.

2. Replace the contents of `contracts/Lock.sol` with the contents of
   [`contracts/FunbuyToken.sol`](contracts/FunbuyToken.sol).
3. Create `.env` and store your RPC URL and deployer private key:

   ```dotenv
   RPC_URL="https://mainnet.infura.io/v3/<project-id>"
   PRIVATE_KEY="0x..."
   ```

4. Update `hardhat.config.js` to use the network you plan to deploy to:

   ```js
   require("@nomicfoundation/hardhat-toolbox");
   require("dotenv").config();

   const { RPC_URL, PRIVATE_KEY } = process.env;

   module.exports = {
     solidity: "0.8.20",
     networks: {
       mainnet: {
         url: RPC_URL,
         accounts: [PRIVATE_KEY],
       },
     },
   };
   ```

5. Add a deploy script `scripts/deploy.js`:

   ```js
   const hre = require("hardhat");

   async function main() {
     const FunbuyToken = await hre.ethers.getContractFactory("FunbuyToken");
     const token = await FunbuyToken.deploy();

     await token.waitForDeployment();
     console.log("FunbuyToken deployed to:", await token.getAddress());
   }

   main().catch((error) => {
     console.error(error);
     process.exitCode = 1;
   });
   ```

6. Deploy:

   ```bash
   npx hardhat run scripts/deploy.js --network mainnet
   ```

   The command prints the contract address once the transaction is mined.

## 3. Verify the contract (optional but recommended)

Verification lets explorers such as Etherscan show the source code.

- **Remix:** use the "Publish on verification services" checkbox when deploying,
  or verify later on Etherscan by pasting the flattened source code.
- **Hardhat:** install `@nomicfoundation/hardhat-verify` and run
  `npx hardhat verify <contract-address>`.

## 4. Add the token to your wallet

In MetaMask (or your preferred wallet) choose **Import Tokens** and paste the
contract address. The wallet reads the token name, symbol, and decimals
automatically.

## 5. List on Uniswap

1. Go to the Uniswap interface (e.g. [https://app.uniswap.org](https://app.uniswap.org)).
2. Connect the same wallet that holds the initial FUNBUY supply.
3. Choose **Pool → New Position** (for v3) or **+ New Position** depending on the
   interface version.
4. In the token selector paste the FUNBUY contract address and click **Import**.
5. Select the pair token (e.g. WETH or USDC) and choose your price range / fee tier.
6. Enter the amount of FUNBUY and the paired asset you want to deposit, approve
   the tokens, then supply liquidity.

After liquidity is added, the token becomes tradable on Uniswap. Anyone can swap
by importing the contract address in the token selector.

## Troubleshooting

- Confirm the deployer's wallet has enough ETH for gas.
- Ensure you are using the correct network (testnet vs mainnet) consistently
  across Remix/Hardhat, your wallet, and Uniswap.
- If a deployment fails with `insufficient funds`, increase the gas limit or gas
  price.

## Additional resources

- [Ethereum Remix documentation](https://remix-ide.readthedocs.io)
- [Hardhat getting started guide](https://hardhat.org/tutorial)
- [Uniswap support docs](https://support.uniswap.org)

