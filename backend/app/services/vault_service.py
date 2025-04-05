# app/services/vault_service.py
import os
import json
from web3 import Web3
from dotenv import load_dotenv
# from web3.middleware import geth_poa_middleware

# Load environment variables
load_dotenv()

class VaultService:
    """Service for interacting with the FactoraVault smart contract"""
    
    def __init__(self):
        # RPC URL for Base Sepolia
        self.rpc_url = os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org")
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        # self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # For compatibility with PoA networks
        
        # Contract details
        self.vault_address = os.getenv("VAULT_CONTRACT_ADDRESS")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        self.vault_abi_path = os.path.join(backend_dir, "factora-contracts/out/FactoraVaultETH.sol/FactoraVaultETH.json")
        
        
        # Initialize contract
        self.vault_contract = None
        if self.vault_address:
            self.init_contract()
    
    def init_contract(self):
        """Initialize the contract instance"""
        try:
            print(f"Attempting to initialize contract at {self.vault_address}")
            print(f"ABI file path: {self.vault_abi_path}")
            print(f"ABI file exists: {os.path.exists(self.vault_abi_path)}")

            if not self.vault_address:
                print("Warning: VAULT_CONTRACT_ADDRESS environment variable not set")
                return False
            # Check if we're connected
            if not self.w3.is_connected():
                print("Warning: Could not connect to the RPC endpoint")
                return False
            
            # Load contract ABI
            if os.path.exists(self.vault_abi_path):
                with open(self.vault_abi_path, 'r') as f:
                    contract_json = json.load(f)
                    abi = contract_json["abi"]
            else:
                print(f"Warning: ABI file not found at {self.vault_abi_path}")
                return False
            
            # Create contract instance
            self.vault_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.vault_address),
                abi=abi
            )
            
            return True
        except Exception as e:
            print(f"Error initializing contract: {e}")
            return False
    
    async def get_vault_stats(self):
        """Get stats about the vault"""
        try:
            if not self.vault_contract:
                return {"status": "error", "message": "Contract not initialized"}
            
            # Call the getVaultStats function
            total_funds, available_for_trading = self.vault_contract.functions.getVaultStats().call()
            
            # Get additional information
            total_assets = self.vault_contract.functions.totalAssets().call()
            total_traded = self.vault_contract.functions.totalTraded().call()
            total_profit = self.vault_contract.functions.totalProfitGenerated().call()
            max_trading_percentage = self.vault_contract.functions.maxTradingPercentage().call()
            
            return {
                "status": "success",
                "data": {
                    "total_funds": total_funds,
                    "available_for_trading": available_for_trading,
                    "total_assets": total_assets,
                    "total_traded": total_traded,
                    "total_profit": total_profit,
                    "max_trading_percentage": max_trading_percentage
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def trade_idle_funds(self, strategy_id, amount_to_trade, private_key):
        """Execute a trade of idle funds"""
        try:
            if not self.vault_contract:
                return {"status": "error", "message": "Contract not initialized"}
                
            # Get the account from the private key
            account = self.w3.eth.account.from_key(private_key)
            
            # Build the transaction
            tx = self.vault_contract.functions.tradeIdleFunds(
                strategy_id,
                amount_to_trade
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address)
            })
            
            # Sign the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "status": "success",
                "data": {
                    "tx_hash": tx_hash.hex(),
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "status": receipt.status
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def report_trading_profit(self, profit_amount, private_key):
        """Report profit from trading"""
        try:
            if not self.vault_contract:
                return {"status": "error", "message": "Contract not initialized"}
                
            # Get the account from the private key
            account = self.w3.eth.account.from_key(private_key)
            
            # Build the transaction
            tx = self.vault_contract.functions.reportTradingProfit(
                profit_amount
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address)
            })
            
            # Sign the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "status": "success",
                "data": {
                    "tx_hash": tx_hash.hex(),
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "status": receipt.status
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    async def deposit(self, amount_wei, private_key):
        try:
            if not self.vault_contract:
                return {"status": "error", "message": "Contract not initialized"}
                
            # Add 0x prefix if missing
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
                
            # Get the account from the private key
            account = self.w3.eth.account.from_key(private_key)
            print(f"Using account: {account.address}")
            
            # Check balance
            balance = self.w3.eth.get_balance(account.address)
            print(f"Account balance: {balance / 10**18} ETH")
            
            if balance < amount_wei:
                return {
                    "status": "error", 
                    "message": f"Insufficient balance. Account has {balance / 10**18} ETH, trying to deposit {amount_wei / 10**18} ETH"
                }
            
            # Build the transaction - simplest approach
            tx = self.vault_contract.functions.deposit().build_transaction({
                'from': account.address,
                'value': amount_wei,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'chainId': self.w3.eth.chain_id
            })
            
            print(f"Transaction built: {tx}")
            
            # Sign the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            
            # Debug what attributes the signed transaction has
            print(f"Signed transaction attributes: {dir(signed_tx)}")
            
            # Get the raw transaction bytes, accounting for different attribute names
            if hasattr(signed_tx, 'rawTransaction'):
                raw_tx = signed_tx.rawTransaction
            elif hasattr(signed_tx, 'raw_transaction'):
                raw_tx = signed_tx.raw_transaction
            else:
                return {"status": "error", "message": f"Cannot find raw transaction data. Available attributes: {dir(signed_tx)}"}
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            print(f"Transaction hash: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Transaction receipt: {receipt}")
            
            # Get balance
            shares = self.vault_contract.functions.balanceOf(account.address).call()
            print(f"Shares balance: {shares}")
            
            return {
                "status": "success",
                "data": {
                    "tx_hash": tx_hash.hex(),
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "status": receipt.status,
                    "depositor": account.address,
                    "amount_deposited": amount_wei,
                    "shares_balance": shares
                }
            }
        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            print(f"Error in deposit: {str(e)}\n{trace}")
            return {"status": "error", "message": f"Error: {str(e)}\n{trace}"}
    
    async def withdraw(self, shares_wei, private_key):
        """Withdraw ETH from the vault by burning shares"""
        try:
            if not self.vault_contract:
                return {"status": "error", "message": "Contract not initialized"}
                
            # Add 0x prefix if missing
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
                
            # Get the account from the private key
            account = self.w3.eth.account.from_key(private_key)
            print(f"Using account for withdrawal: {account.address}")
            
            # Build the transaction
            tx = self.vault_contract.functions.withdraw(shares_wei).build_transaction({
                'from': account.address,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'chainId': self.w3.eth.chain_id
            })
            
            print(f"Withdrawal transaction built: {tx}")
            
            # Sign the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            
            # Debug what attributes the signed transaction has
            print(f"Signed transaction attributes: {dir(signed_tx)}")
            
            # Get the raw transaction bytes, accounting for different attribute names
            if hasattr(signed_tx, 'rawTransaction'):
                raw_tx = signed_tx.rawTransaction
            elif hasattr(signed_tx, 'raw_transaction'):
                raw_tx = signed_tx.raw_transaction
            else:
                return {"status": "error", "message": f"Cannot find raw transaction data. Available attributes: {dir(signed_tx)}"}
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            print(f"Withdrawal transaction hash: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Withdrawal transaction receipt: {receipt}")
            
            # Get balance after withdrawal
            shares_balance = self.vault_contract.functions.balanceOf(account.address).call()
            
            return {
                "status": "success",
                "data": {
                    "tx_hash": tx_hash.hex(),
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "status": receipt.status,
                    "withdrawer": account.address,
                    "shares_redeemed": shares_wei,
                    "remaining_shares": shares_balance
                }
            }
        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            print(f"Error in withdraw: {str(e)}\n{trace}")
            return {"status": "error", "message": f"Error: {str(e)}\n{trace}"}
    
    async def get_balance(self, address):
        """Get the balance of shares for an address"""
        try:
            if not self.vault_contract:
                return {"status": "error", "message": "Contract not initialized"}
            
            # Verify the address format
            if not self.w3.is_address(address):
                return {"status": "error", "message": "Invalid Ethereum address"}
            
            checksum_address = self.w3.to_checksum_address(address)
            balance = self.vault_contract.functions.balanceOf(checksum_address).call()
            
            return {
                "status": "success",
                "data": {
                    "address": checksum_address,
                    "shares_balance": balance,
                    "shares_balance_eth": balance / 10**18  # Convert to ETH format
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_asset_balance(self, address):
        """Get the asset (ETH) balance equivalent for an address based on shares"""
        try:
            if not self.vault_contract:
                return {"status": "error", "message": "Contract not initialized"}
            
            # Verify the address format
            if not self.w3.is_address(address):
                return {"status": "error", "message": "Invalid Ethereum address"}
            
            checksum_address = self.w3.to_checksum_address(address)
            
            # Get shares balance
            shares_balance = self.vault_contract.functions.balanceOf(checksum_address).call()
            
            # Get total assets and total supply
            total_assets = self.vault_contract.functions.totalAssets().call()
            total_supply = self.vault_contract.functions.totalSupply().call()
            
            # Calculate asset balance
            asset_balance = 0
            if total_supply > 0:
                asset_balance = (shares_balance * total_assets) // total_supply
            
            return {
                "status": "success",
                "data": {
                    "address": checksum_address,
                    "shares_balance": shares_balance,
                    "shares_balance_eth": shares_balance / 10**18,
                    "asset_balance": asset_balance,
                    "asset_balance_eth": asset_balance / 10**18
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create a single instance to be used throughout the application
vault_service = VaultService()