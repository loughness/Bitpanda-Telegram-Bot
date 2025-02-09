import os
import requests
import json
import pandas as pd

from dotenv import load_dotenv
from database import get_api_key


class BitpandaClient:
    BASE_URL = "https://api.bitpanda.com/v1"

    def __init__(self, user_id):
        self.user_id = user_id
        self.api_key = get_api_key(user_id)

        if not self.api_key:
            raise ValueError("No API key found. User must log in first.")
        
        self.headers = {"X-Api-Key": self.api_key}

    def get_asset_balances(self):
        url = f"{self.BASE_URL}/asset-wallets"
        response = requests.get(url=url, headers=self.headers)

        if response.status_code != 200:
            return "❌ Error fetching fiat balances. Please try again."

        data = response.json()

        # Extract wallet details into a structured format
        asset_wallets = []
        for category, details in data['data']['attributes'].items():
            if 'attributes' in details and 'wallets' in details['attributes']:
                for wallet in details['attributes']['wallets']:
                    attributes = wallet['attributes']
                    asset_wallets.append({
                        'Category': category,
                        'Wallet ID': wallet['id'],
                        'Name': attributes['name'],
                        'Symbol': attributes['cryptocoin_symbol'],
                        'Balance': float(attributes['balance'])
                    })

        if not asset_wallets:
            return "No assets found in your Bitpanda account."
        
        message = "📊 *Your Bitpanda Portfolio:*\n\n"
        for wallet in asset_wallets:
            if wallet['Balance'] > 0:
                message += f"🔹 *{wallet['Name']}* ({wallet['Symbol']}): {wallet['Balance']}\n"

        return message
    
    def get_fiat_balances(self):
        url = f"{self.BASE_URL}/fiatwallets"
        response = requests.get(url=url, headers=self.headers)

        if response.status_code != 200:
            return "❌ Error fetching fiat balances. Please try again."
    
        data = response.json()

        fiat_wallets = []
        for wallet in data["data"]:
            attributes = wallet['attributes']
            fiat_wallets.append({
                'Name': attributes['name'],
                'Symbol': attributes['fiat_symbol'],
                "Balance": float(attributes['balance'])
            })

        if not fiat_wallets:
            return "No fiat balances found"
        
        # Format the message for Telegram
        message = "💰 *Your Fiat Wallet Balances:*\n\n"
        for wallet in fiat_wallets:
            if wallet['Balance'] > 0:
                message += f"🔹 *{wallet['Name']}* ({wallet['Symbol']}): €{wallet['Balance']:.2f}\n"

        return message