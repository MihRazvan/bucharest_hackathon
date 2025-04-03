# app/services/agent_service.py
import os
from dotenv import load_dotenv
from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    SmartWalletProvider,
    SmartWalletProviderConfig,
    wallet_action_provider,
)
from eth_account.account import Account

class AgentService:
    """Simple service for accessing AgentKit functionality"""
    
    def __init__(self):
        load_dotenv()
        self.network_id = os.getenv("NETWORK_ID", "base-sepolia")
        self.agent_kit = None
        self.wallet_provider = None
        self.initialize_agent()
        
    def initialize_agent(self):
        """Initialize the AgentKit instance with a wallet"""
        try:
            # Get private key from env
            private_key = os.getenv("CDP_PRIVATE_KEY")
            
            # If no key exists, create a new one
            if not private_key:
                acct = Account.create()
                private_key = acct.key.hex()
                # In a real app, you'd save this key securely
            
            # Create account object
            signer = Account.from_key(private_key)
            
            # Initialize SmartWalletProvider
            self.wallet_provider = SmartWalletProvider(
                SmartWalletProviderConfig(
                    network_id=self.network_id,
                    signer=signer,
                    smart_wallet_address=None,  # Will create if needed
                )
            )
            
            # Initialize AgentKit
            self.agent_kit = AgentKit(
                AgentKitConfig(
                    wallet_provider=self.wallet_provider,
                    action_providers=[
                        wallet_action_provider(),
                    ],
                )
            )
            
            print(f"Agent initialized with wallet address: {self.wallet_provider.get_address()}")
            return True
        except Exception as e:
            print(f"Error initializing agent: {e}")
            return False
    
    def get_wallet_details(self):
        """Get details about the agent's wallet"""
        try:
            if not self.agent_kit:
                return {"status": "error", "message": "Agent not initialized"}
                
            # Get wallet details
            wallet_details = self.agent_kit.execute_action(
                "wallet", "get_wallet_details", {}
            )
            return {"status": "success", "data": wallet_details}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_wallet_balance(self):
        """Get the agent's wallet balance"""
        try:
            if not self.agent_kit:
                return {"status": "error", "message": "Agent not initialized"}
                
            # Get wallet balance
            balance = self.agent_kit.execute_action(
                "wallet", "get_balance", {}
            )
            return {"status": "success", "data": balance}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create a single instance to be used by the application
agent_service = AgentService()