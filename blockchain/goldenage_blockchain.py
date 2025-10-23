"""Simple GoldenAge blockchain prototype.

This module provides a minimal blockchain implementation that can be executed
from the terminal. It supports adding pending transactions and mining them into
blocks using a proof-of-work puzzle. The configuration is intentionally
lightweight so users can understand the fundamental components involved in a
public blockchain network while experimenting locally.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional


DIFFICULTY_PREFIX = "0000"
CHAIN_FILE = "goldenage_chain.json"


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
        }


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: Optional[str] = None

    def compute_hash(self) -> str:
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": [tx.to_dict() for tx in self.transactions],
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return sha256(block_string)


@dataclass
class Blockchain:
    name: str
    symbol: str
    chain: List[Block] = field(default_factory=list)
    pending_transactions: List[Transaction] = field(default_factory=list)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def create_genesis_block(self) -> None:
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[Transaction("network", "founder", 1_000_000)],
            previous_hash="0",
        )
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_transaction(self, sender: str, recipient: str, amount: float) -> None:
        self.pending_transactions.append(Transaction(sender, recipient, amount))

    def proof_of_work(self, block: Block) -> str:
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith(DIFFICULTY_PREFIX):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def mine_pending_transactions(self, miner_address: str) -> Block:
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions + [
                Transaction("network", miner_address, 5.0)
            ],
            previous_hash=self.last_block.hash,
        )
        block.hash = self.proof_of_work(block)
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def validate(self) -> bool:
        for idx in range(1, len(self.chain)):
            current = self.chain[idx]
            previous = self.chain[idx - 1]
            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
            if not current.hash.startswith(DIFFICULTY_PREFIX):
                return False
        return True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "chain": [
                {
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "transactions": [tx.to_dict() for tx in block.transactions],
                    "previous_hash": block.previous_hash,
                    "nonce": block.nonce,
                    "hash": block.hash,
                }
                for block in self.chain
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Blockchain":
        chain = []
        for block_data in data.get("chain", []):
            transactions = [
                Transaction(**tx_data) for tx_data in block_data.get("transactions", [])
            ]
            block = Block(
                index=block_data["index"],
                timestamp=block_data["timestamp"],
                transactions=transactions,
                previous_hash=block_data["previous_hash"],
                nonce=block_data.get("nonce", 0),
                hash=block_data.get("hash"),
            )
            chain.append(block)
        blockchain = cls(name=data["name"], symbol=data["symbol"], chain=chain)
        return blockchain


def load_chain() -> Optional[Blockchain]:
    if not os.path.exists(CHAIN_FILE):
        return None
    with open(CHAIN_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    return Blockchain.from_dict(data)


def save_chain(blockchain: Blockchain) -> None:
    with open(CHAIN_FILE, "w", encoding="utf-8") as file:
        json.dump(blockchain.to_dict(), file, indent=2)


def initialize_chain() -> Blockchain:
    chain = Blockchain(name="GoldenAge", symbol="GA")
    chain.create_genesis_block()
    save_chain(chain)
    return chain


def get_or_create_chain() -> Blockchain:
    chain = load_chain()
    if chain is None:
        chain = initialize_chain()
    return chain


def cmd_init(_: argparse.Namespace) -> None:
    chain = initialize_chain()
    print(f"Initialized {chain.name} chain with symbol {chain.symbol}.")


def cmd_status(_: argparse.Namespace) -> None:
    chain = get_or_create_chain()
    print(json.dumps(chain.to_dict(), indent=2))


def cmd_add_tx(args: argparse.Namespace) -> None:
    chain = get_or_create_chain()
    chain.add_transaction(args.sender, args.recipient, args.amount)
    save_chain(chain)
    print(
        f"Queued transaction from {args.sender} to {args.recipient} for {args.amount} {chain.symbol}."
    )


def cmd_mine(args: argparse.Namespace) -> None:
    chain = get_or_create_chain()
    if not chain.chain:
        chain.create_genesis_block()
    if not chain.pending_transactions:
        print("No pending transactions to mine.")
        return
    block = chain.mine_pending_transactions(args.miner)
    save_chain(chain)
    print(
        f"Mined block #{block.index} with hash {block.hash} and reward sent to {args.miner}."
    )


def cmd_validate(_: argparse.Namespace) -> None:
    chain = get_or_create_chain()
    print("Chain valid" if chain.validate() else "Chain invalid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GoldenAge blockchain CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a fresh chain")
    init_parser.set_defaults(func=cmd_init)

    status_parser = subparsers.add_parser("status", help="Show current chain state")
    status_parser.set_defaults(func=cmd_status)

    add_tx_parser = subparsers.add_parser("add-tx", help="Queue a new transaction")
    add_tx_parser.add_argument("sender", help="Transaction sender address")
    add_tx_parser.add_argument("recipient", help="Transaction recipient address")
    add_tx_parser.add_argument("amount", type=float, help="Amount of GA to transfer")
    add_tx_parser.set_defaults(func=cmd_add_tx)

    mine_parser = subparsers.add_parser("mine", help="Mine pending transactions")
    mine_parser.add_argument("miner", help="Address that receives the block reward")
    mine_parser.set_defaults(func=cmd_mine)

    validate_parser = subparsers.add_parser(
        "validate", help="Verify the integrity of the chain"
    )
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
