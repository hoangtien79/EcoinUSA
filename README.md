# Funbuy Token

`FunbuyToken.sol` implements a fixed-supply ERC-20 token with the following
parameters:

| Property   | Value                          |
| ---------- | ------------------------------ |
| Name       | `Funbuy`                       |
| Symbol     | `FUNBUY`                       |
| Decimals   | `18`                           |
| Total Supply | `1,260,000,000 FUNBUY` (minted to the deployer) |

The sections below describe how to deploy the contract, confirm the supply, and
list the token on Uniswap so it can be traded from your application.

## Before you start

- Install [MetaMask](https://metamask.io/) (or another Web3 wallet) and fund the
  deployment account with enough ETH to cover gas.
- Decide which EVM network you want to deploy to (e.g. Ethereum mainnet,
  Sepolia, Polygon, BNB Chain) and use the matching RPC URL in every step.
- If you prefer a command-line workflow, make sure Node.js 18+ and npm are
  installed.

## 1. Deploy with Remix (browser workflow)

1. Open [https://remix.ethereum.org](https://remix.ethereum.org) and create a new
   file named `FunbuyToken.sol`.
2. Copy the contents of
   [`contracts/FunbuyToken.sol`](contracts/FunbuyToken.sol) into the new file.
3. In the **Solidity Compiler** tab select version `0.8.20` (or any 0.8.20+
   release) and press **Compile FunbuyToken.sol**.
4. Switch to the **Deploy & Run** tab and configure:
   - **Environment:** `Injected Provider - MetaMask` (or your wallet provider)
   - **Account:** the wallet that should receive the entire supply
   - **Contract:** `FunbuyToken`
5. Click **Deploy** and confirm the transaction in your wallet. Once mined, the
   deployer address holds the full `1,260,000,000 * 10^18` FUNBUY balance.
6. Copy the deployed contract address from Remix or the transaction receipt and
   save it—this is the address you will share with wallets, explorers, and
   Uniswap.

### Confirm the minted supply

After deployment, expand the contract instance in Remix and read the `totalSupply`
and `balanceOf(deployer)` values. They should both return
`1260000000000000000000000000`, which is `1,260,000,000` FUNBUY with 18 decimals.

## 2. Deploy with Hardhat (CLI workflow)

1. Create an empty folder and install the dependencies:

   ```bash
   npm init -y
   npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv
   npx hardhat
   ```

   When prompted, choose the **JavaScript project** template and let Hardhat
   write the starter files.

2. Replace `contracts/Lock.sol` with the contents of
   [`contracts/FunbuyToken.sol`](contracts/FunbuyToken.sol).

3. Create `.env` and add your RPC URL and private key (never commit this file):

   ```dotenv
   RPC_URL="https://mainnet.infura.io/v3/<project-id>"
   PRIVATE_KEY="0xYOUR_PRIVATE_KEY"
   ```

4. Update `hardhat.config.js`:

   ```js
   require("@nomicfoundation/hardhat-toolbox");
   require("dotenv").config();

   const { RPC_URL, PRIVATE_KEY } = process.env;

   module.exports = {
     solidity: "0.8.20",
     networks: {
       mainnet: {
         url: RPC_URL,
         accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
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

6. Deploy (replace `mainnet` with your desired network key):

   ```bash
   npx hardhat run scripts/deploy.js --network mainnet
   ```

7. After the transaction is confirmed, record the address printed in the
   terminal and verify the deployer balance with `npx hardhat console` if
   desired:

   ```bash
   npx hardhat console --network mainnet
   > const token = await ethers.getContractAt("FunbuyToken", "<contract-address>");
   > (await token.totalSupply()).toString();
   > (await token.balanceOf("<deployer-address>")).toString();
   ```

## 3. Verify the contract (recommended)

Contract verification lets explorers display the source code and ABI.

- **Remix:** check **Publish on verification services** during deployment or use
  the **Sourcify / Etherscan** plugin afterward.
- **Hardhat:** install the verify plugin and run the command with the compiler
  arguments used during deployment:

  ```bash
  npm install --save-dev @nomicfoundation/hardhat-verify
  npx hardhat verify --network mainnet <contract-address>
  ```

## 4. Import the token in your wallet

In MetaMask (or your preferred wallet) click **Import Tokens**, paste the
contract address, and approve. The wallet auto-fills the name, symbol, and
decimals from the chain.

## 5. Add liquidity on Uniswap

1. Visit [https://app.uniswap.org](https://app.uniswap.org) and connect the
   deployer wallet.
2. Navigate to **Pool → New Position** (Uniswap v3) or **Pool → + New Position**.
3. Paste the FUNBUY contract address, accept the import warning, and choose the
   asset you want to pair with (WETH, USDC, etc.).
4. Set your fee tier and price range (v3) or choose the appropriate pool type.
5. Approve the FUNBUY and pair token if prompted, then supply the amounts you
   want to seed as initial liquidity.

Once liquidity is deposited, your token becomes discoverable on Uniswap. Share
the contract address with users so they can import the token in the swap
interface.

## Troubleshooting checklist

- Ensure the deployer wallet has enough native tokens for gas (deployment,
  approvals, and liquidity supply each cost gas).
- Verify that every tool (Remix/Hardhat, wallet, Uniswap) is pointed to the same
  network.
- If a transaction fails with `insufficient funds`, try raising the gas limit or
  fee. For persistent failures, inspect the transaction in a block explorer for
  detailed error messages.
- If Uniswap cannot find the token, double-check that you are using the correct
  contract address and that the deployment is confirmed on the network.

## Additional resources

- [Remix documentation](https://remix-ide.readthedocs.io)
- [Hardhat guides](https://hardhat.org/tutorial)
- [Uniswap help center](https://support.uniswap.org)

