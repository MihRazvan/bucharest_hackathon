# agent_test.py
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

def test_agent_kit():
    # Load environment variables
    load_dotenv()
    
    print("Testing AgentKit integration...")
    
    try:
        # Get CDP API keys
        api_key_name = os.getenv("CDP_API_KEY_NAME")
        api_key_private = os.getenv("CDP_API_KEY_PRIVATE_KEY")
        network_id = os.getenv("NETWORK_ID", "base-sepolia")
        
        print(f"Using network: {network_id}")
        
        # Get or create private key
        private_key = os.getenv("CDP_PRIVATE_KEY")
        if not private_key:
            print("No private key found, creating a new one...")
            acct = Account.create()
            private_key = acct.key.hex()
            print(f"Created new private key (first 10 chars): {private_key[:10]}...")
        else:
            print(f"Using existing private key (first 10 chars): {private_key[:10]}...")
        
        # Create account object
        signer = Account.from_key(private_key)
        print(f"Signer address: {signer.address}")
        
        # Initialize SmartWalletProvider
        wallet_provider = SmartWalletProvider(
            SmartWalletProviderConfig(
                network_id=network_id,
                signer=signer,
                smart_wallet_address=None,  # Will create if needed
            )
        )
        
        # Initialize AgentKit
        agent_kit = AgentKit(
            AgentKitConfig(
                wallet_provider=wallet_provider,
                action_providers=[
                    wallet_action_provider(),
                ],
            )
        )
        
        # Get wallet details
        print("Getting wallet details...")
        wallet_details = agent_kit.execute_action(
            "wallet", "get_wallet_details", {}
        )
        
        print("\nWallet Details:")
        print(wallet_details)
        
        # Get balance
        print("\nGetting wallet balance...")
        balance = agent_kit.execute_action(
            "wallet", "get_balance", {}
        )
        
        print("\nWallet Balance:")
        print(balance)
        
        print("\nAgentKit integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during AgentKit test: {e}")
        return False

if __name__ == "__main__":
    test_agent_kit()