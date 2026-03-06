import os
import json
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __

# 1. Setup the connection outside the handler (Best practice for performance)
# We get the endpoint from the environment variable we set in our CDK stack
neptune_endpoint = os.environ.get('NEPTUNE_ENDPOINT')
neptune_url = f'wss://{neptune_endpoint}:8182/gremlin'

def handler(event, context):
    """
    AWS Lambda calls this function. 
    'event' will contain our data: {"agent": "Rafaela Pimenta", "player": "Erling Haaland"}
    """
    
    # 2. Extract data from the event sent by GitHub Actions/Scraper
    agent_name = event.get('agent')
    player_name = event.get('player')

    if not agent_name or not player_name:
        return {"statusCode": 400, "body": "Missing agent or player name"}

    # 3. Connect to Neptune
    connection = DriverRemoteConnection(neptune_url, 'g')
    g = traversal().withRemote(connection)

    try:
        # 4. The "Upsert" logic (Update or Insert)
        # This adds the Agent, adds the Player, and links them with a 'REPRESENTS' line.
        # It won't create duplicates if they already exist!
        g.V().has('Agent', 'name', agent_name).fold().coalesce(
            __.unfold(), 
            __.addV('Agent').property('name', agent_name)
        ).as_('a').V().has('Player', 'name', player_name).fold().coalesce(
            __.unfold(),
            __.addV('Player').property('name', player_name)
        ).as_('p').addE('REPRESENTS').from_('a').to('p').iterate()

        return {
            "statusCode": 200,
            "body": json.dumps(f"Successfully linked {agent_name} to {player_name}")
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": str(e)}
    
    finally:
        connection.close()

