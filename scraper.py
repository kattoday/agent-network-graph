import requests
from bs4 import BeautifulSoup
import boto3
import json
import time

# --- 1. CONFIGURATION ---
# Replace this with the Physical ID from your CDK Deploy output
FUNCTION_NAME = "MyTestProjectStack-GraphIngestor59F1AD16-jtgozp5pklhs"

# Transfermarkt headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# AWS Lambda Client
lambda_client = boto3.client('lambda', region_name='us-east-1')

# --- 2. SCRAPING LOGIC ---
def get_agent_players(agent_id, agent_name):
    print(f"Scraping players for {agent_name}...")
    url = f"https://www.transfermarkt.com/{agent_name}/beraterfirma/berater/{agent_id}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        players = []
        # Find the table containing players (usually has class 'items')
        table = soup.find("table", {"class": "items"})
        if table:
            for row in table.find_all("tr", class_=["odd", "even"]):
                name_tag = row.find("td", class_="hauptlink")
                if name_tag and name_tag.find("a"):
                    player_name = name_tag.find("a").text.strip()
                    players.append(player_name)
        
        return players
    except Exception as e:
        print(f"Error scraping {agent_name}: {e}")
        return []

# --- 3. AWS TRIGGER LOGIC ---
def send_to_graph(agent_name, player_name):
    payload = {
        "agent": agent_name,
        "player": player_name,
        "action": "add_relationship"
    }
    
    response = lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='Event', # Async: Don't wait for the graph to finish
        Payload=json.dumps(payload)
    )
    return response

# --- 4. MAIN EXECUTION ---
if __name__ == "__main__":
    # Test with Rafaela Pimenta
    agent_id = 100
    agent_name = "rafaela-pimenta"
    
    found_players = get_agent_players(agent_id, agent_name)
    print(f"Found {len(found_players)} players for {agent_name}.")

    for player in found_players:
        print(f"Syncing to Graph: {agent_name} -> {player}")
        send_to_graph(agent_name, player)
        # Small sleep to avoid hitting Lambda rate limits during mass ingestion
        time.sleep(0.1)

    print("\n✅ Success! Data is being processed by the Ingestor Lambda.")

