import requests
from bs4 import BeautifulSoup

# Transfermarkt is picky; we must pretend to be a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_agent_players(agent_id, agent_name):
    url = f"https://www.transfermarkt.com/{agent_name}/beraterfirma/berater/{agent_id}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    players = []
    # Find the table containing players (usually has class 'items')
    table = soup.find("table", {"class": "items"})
    if table:
        for row in table.find_all("tr", class_=["odd", "even"]):
            name_tag = row.find("td", class_="hauptlink").find("a")
            if name_tag:
                players.append(name_tag.text.strip())
    
    return players

# Example test: Rafaela Pimenta (Agent ID 100)
# print(get_agent_players(100, "rafaela-pimenta"))

