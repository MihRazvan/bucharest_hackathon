# app/services/agent_service.py
import os
import json
from dotenv import load_dotenv
from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,  # Changed from SmartWalletProvider
    CdpWalletProviderConfig,  # Changed from SmartWalletProviderConfig
    wallet_action_provider,
    cdp_api_action_provider,  # Added for faucet functionality
)

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
            # Get API keys
            api_key_name = os.getenv("CDP_API_KEY_NAME")
            api_key_private_key = os.getenv("CDP_API_KEY_PRIVATE_KEY")
            
            if not api_key_name or not api_key_private_key:
                raise ValueError("CDP API keys not found in environment variables")
                
            print(f"Initializing with network: {self.network_id}")
            print(f"Using CDP API key name: {api_key_name}")
            
            # Try to load saved wallet data
            wallet_data = self._load_wallet_data()
            
            # Initialize CdpWalletProvider (using wallet_data if available)
            config = CdpWalletProviderConfig(
                api_key_name=api_key_name,
                api_key_private=api_key_private_key,
                network_id=self.network_id
            )
            
            if "wallet_data" in wallet_data:
                # Use existing wallet data if available
                config.wallet_data = wallet_data["wallet_data"]
                print("Using existing wallet data")
            
            self.wallet_provider = CdpWalletProvider(config)
            
            # Save wallet data for future use
            exported_wallet = self.wallet_provider.export_wallet()
            wallet_data["wallet_data"] = exported_wallet
            self._save_wallet_data(wallet_data)
            print("Wallet data saved")
            
            # Initialize AgentKit
            self.agent_kit = AgentKit(
                AgentKitConfig(
                    wallet_provider=self.wallet_provider,
                    action_providers=[
                        wallet_action_provider(),
                        cdp_api_action_provider(),  # Added for faucet functionality
                    ],
                )
            )
            
            print(f"Agent successfully initialized with wallet address: {self.wallet_provider.get_address()}")
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
            # In Render.com, files in the app directory are read-only after deployment
            # Try writing to /tmp instead
            tmp_wallet_file = "/tmp/wallet_data.json"
            with open(tmp_wallet_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Wallet data saved to {tmp_wallet_file}")
            return True
        except Exception as e:
            print(f"Error saving wallet data: {e}")
            return False
    
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

    def request_faucet_funds(self):
        """Request testnet funds from the CDP faucet"""
        try:
            if not self.agent_kit:
                # Try to initialize again if it failed before
                if not self.initialize_agent():
                    return {"status": "error", "message": "Agent initialization failed"}
            
            # Request funds
            result = self.agent_kit.execute_action(
                "cdp_api", "request_faucet_funds", 
                {"asset_id": None}  # Default to ETH
            )
            
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create a single instance to be used by the application
agent_service = AgentService()