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
import json

class AgentService:
    """Simple service for accessing AgentKit functionality"""
    
    def __init__(self):
        load_dotenv()
        self.network_id = os.getenv("NETWORK_ID", "base-sepolia")
        self.agent_kit = None
        self.wallet_provider = None
        self.wallet_file = "wallet_data.json"
        
        # Initialize the agent
        success = self.initialize_agent()
        if not success:
            print("WARNING: Agent initialization failed!")
        
    def initialize_agent(self):
        """Initialize the AgentKit instance with a wallet"""
        try:
            # Try to load saved wallet data
            wallet_data = self._load_wallet_data()
            
            # Get or generate private key
            private_key = wallet_data.get("private_key")
            if not private_key:
                # Generate new key
                acct = Account.create()
                private_key = acct.key.hex()
                wallet_data["private_key"] = private_key
                self._save_wallet_data(wallet_data)
                print("Generated new private key")
            
            # Create account object 
            signer = Account.from_key(private_key)
            
            # Get smart wallet address if we have one
            smart_wallet_address = wallet_data.get("smart_wallet_address")
            
            print(f"Initializing with network: {self.network_id}")
            print(f"Signer address: {signer.address}")
            print(f"Smart wallet address: {smart_wallet_address or 'Not created yet'}")
            
            # Initialize SmartWalletProvider
            self.wallet_provider = SmartWalletProvider(
                SmartWalletProviderConfig(
                    network_id=self.network_id,
                    signer=signer,
                    smart_wallet_address=smart_wallet_address,
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
            
            # Save the smart wallet address if it was created
            new_wallet_address = self.wallet_provider.get_address()
            if new_wallet_address != smart_wallet_address:
                wallet_data["smart_wallet_address"] = new_wallet_address
                self._save_wallet_data(wallet_data)
                print(f"Smart wallet address updated: {new_wallet_address}")
            
            print(f"Agent successfully initialized with wallet address: {new_wallet_address}")
            return True
        except Exception as e:
            print(f"Error initializing agent: {e}")
            return False
    
    def _load_wallet_data(self):
        """Load wallet data from file"""
        try:
            if os.path.exists(self.wallet_file):
                with open(self.wallet_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading wallet data: {e}")
            return {}
    
    def _save_wallet_data(self, data):
        """Save wallet data to file"""
        try:
            with open(self.wallet_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving wallet data: {e}")
    
    def get_wallet_details(self):
        """Get details about the agent's wallet"""
        try:
            if not self.agent_kit:
                # Try to initialize again if it failed before
                if not self.initialize_agent():
                    return {"status": "error", "message": "Agent initialization failed"}
                
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
                # Try to initialize again if it failed before
                if not self.initialize_agent():
                    return {"status": "error", "message": "Agent initialization failed"}
                
            # Get wallet balance
            balance = self.agent_kit.execute_action(
                "wallet", "get_balance", {}
            )
            return {"status": "success", "data": balance}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create a single instance to be used by the application
agent_service = AgentService()