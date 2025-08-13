from mcp.server.fastmcp import FastMCP
import logging
import httpx
from typing import Any
import random

# Initialize the FastMCP server with a name and version.
# The name is important for identifying the server in a client like Claude for Desktop.
mcp = FastMCP(
    name="pokemon-server"
)

# Define the base URL for the PokéAPI
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

async def _make_api_request(url: str) -> dict[str, Any] | None:
    """A helper function to make asynchronous web requests to an API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # In a real server, you'd log this error to stderr
            # For now, we'll just return None on failure
            return None

def _parse_evolution_chain(chain_data: dict) -> str:
    """Parse the evolution chain data and return a formatted string."""
    evolutions = []
    
    def extract_evolutions(chain):
        pokemon_name = chain['species']['name'].capitalize()
        evolutions.append(pokemon_name)
        
        for evolution in chain.get('evolves_to', []):
            extract_evolutions(evolution)
    
    extract_evolutions(chain_data)
    
    if len(evolutions) <= 1:
        return "Does not evolve"
    else:
        return " → ".join(evolutions)

@mcp.resource(
    uri="pokemon/{pokemon_name}",
    name="pokemon",
    description="Provides comprehensive data for a given Pokémon. Usage: mcp://pokemon-server/pokemon/pikachu"
)
async def get_pokemon_data(pokemon_name: str) -> str:
    """
    A reader function that gets triggered when a client tries to read from this resource.
    The pokemon_name parameter is extracted from the URI path.
    """
    # Convert to lowercase for API consistency
    pokemon_name = pokemon_name.lower()
    if not pokemon_name:
        return "Error: Pokémon name not specified in the URI. Example: mcp://pokemon-server/pokemon/pikachu"

    # Fetch the main Pokémon data
    pokemon_data = await _make_api_request(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_name}")
    if not pokemon_data:
        return f"Error: Could not find data for Pokémon '{pokemon_name}'. Please check the spelling."

    # Extract the relevant details
    name = pokemon_data['name'].capitalize()
    hp = next(stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'hp')
    attack = next(stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'attack')
    defense = next(stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'defense')
    special_attack = next(stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'special-attack')
    special_defense = next(stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'special-defense')
    speed = next(stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'speed')

    types = [t['type']['name'].capitalize() for t in pokemon_data['types']]
    abilities = [a['ability']['name'].replace('-', ' ').title() for a in pokemon_data['abilities']]

    # Fetch evolution information
    species_data = await _make_api_request(pokemon_data['species']['url'])
    evolution_info = "None"
    if species_data:
        evolution_chain_data = await _make_api_request(species_data['evolution_chain']['url'])
        if evolution_chain_data:
            evolution_info = _parse_evolution_chain(evolution_chain_data['chain'])

    # Get enhanced move information (first 5 moves with details)
    detailed_moves = []
    for move_data in pokemon_data['moves'][:5]:
        move_details = await _make_api_request(move_data['move']['url'])
        if move_details:
            move_name = move_details['name'].replace('-', ' ').title()
            move_type = move_details['type']['name'].capitalize()
            move_power = move_details['power'] or "N/A"
            move_accuracy = move_details['accuracy'] or "N/A"
            move_pp = move_details['pp'] or "N/A"
            effect = move_details['effect_entries'][0]['short_effect'] if move_details['effect_entries'] else "No effect description"
            detailed_moves.append(f"{move_name} ({move_type}) - Power: {move_power}, Accuracy: {move_accuracy}, PP: {move_pp} - {effect}")

    # Additional moves for variety (just names)
    additional_moves = [m['move']['name'].replace('-', ' ').title() for m in pokemon_data['moves'][5:15]]

    # Format the data into a readable string
    report = (
        f"--- Pokémon Report: {name} ---\n"
        f"ID: {pokemon_data['id']}\n"
        f"Types: {', '.join(types)}\n"
        f"Height: {pokemon_data['height'] / 10} m\n"
        f"Weight: {pokemon_data['weight'] / 10} kg\n\n"
        f"Base Stats:\n"
        f"  - HP: {hp}\n"
        f"  - Attack: {attack}\n"
        f"  - Defense: {defense}\n"
        f"  - Special Attack: {special_attack}\n"
        f"  - Special Defense: {special_defense}\n"
        f"  - Speed: {speed}\n"
        f"  - Total: {hp + attack + defense + special_attack + special_defense + speed}\n\n"
        f"Abilities: {', '.join(abilities)}\n\n"
        f"Evolution Chain: {evolution_info}\n\n"
        f"Notable Moves (with details):\n"
    )
    
    for move in detailed_moves:
        report += f"  • {move}\n"
    
    if additional_moves:
        report += f"\nAdditional Moves: {', '.join(additional_moves)}..."
    return report

# A simplified type effectiveness chart for damage calculation.
# Key: Attacking Type, Value: Dict of {Defending Type: Multiplier}
TYPE_EFFECTIVENESS = {
    'normal': {'rock': 0.5, 'ghost': 0},
    'fire': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 2, 'bug': 2, 'rock': 0.5, 'steel': 2},
    'water': {'fire': 2, 'water': 0.5, 'grass': 0.5, 'ground': 2, 'rock': 2, 'dragon': 0.5},
    'electric': {'water': 2, 'electric': 0.5, 'grass': 0.5, 'ground': 0, 'flying': 2, 'dragon': 0.5},
    'grass': {'fire': 0.5, 'water': 2, 'grass': 0.5, 'poison': 0.5, 'ground': 2, 'flying': 0.5, 'bug': 0.5, 'rock': 2, 'dragon': 0.5, 'steel': 0.5},
    'ice': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 0.5, 'ground': 2, 'flying': 2, 'dragon': 2, 'steel': 0.5},
    'fighting': {'normal': 2, 'ice': 2, 'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'rock': 2, 'ghost': 0, 'dark': 2, 'steel': 2},
    'poison': {'grass': 2, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel': 0},
    'ground': {'fire': 2, 'electric': 2, 'grass': 0.5, 'poison': 2, 'flying': 0, 'bug': 0.5, 'rock': 2, 'steel': 2},
    'flying': {'electric': 0.5, 'grass': 2, 'fighting': 2, 'bug': 2, 'rock': 0.5, 'steel': 0.5},
    'psychic': {'fighting': 2, 'poison': 2, 'psychic': 0.5, 'dark': 0, 'steel': 0.5},
    'bug': {'fire': 0.5, 'grass': 2, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'psychic': 2, 'ghost': 0.5, 'dark': 2, 'steel': 0.5},
    'rock': {'fire': 2, 'ice': 2, 'fighting': 0.5, 'ground': 0.5, 'flying': 2, 'bug': 2, 'steel': 0.5},
    'ghost': {'normal': 0, 'psychic': 2, 'ghost': 2, 'dark': 0.5},
    'dragon': {'dragon': 2, 'steel': 0.5},
    'dark': {'fighting': 0.5, 'psychic': 2, 'ghost': 2, 'dark': 0.5},
    'steel': {'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'ice': 2, 'rock': 2, 'dragon': 1, 'steel': 0.5},
    'fairy': {'fire': 0.5, 'fighting': 2, 'poison': 0.5, 'dragon': 2, 'dark': 2, 'steel': 0.5}
}


@mcp.tool()
async def simulate_battle(pokemon1_name: str, pokemon2_name: str) -> str:
    """
    Simulates a Pokémon battle between two specified Pokémon.

    Args:
        pokemon1_name: The name of the first Pokémon.
        pokemon2_name: The name of the second Pokémon.
    """
    battle_log = [f"A battle is about to begin between {pokemon1_name.capitalize()} and {pokemon2_name.capitalize()}!\n"]

    # 1. Fetch data for both Pokémon
    p1_data = await _make_api_request(f"{POKEAPI_BASE_URL}/pokemon/{pokemon1_name.lower()}")
    p2_data = await _make_api_request(f"{POKEAPI_BASE_URL}/pokemon/{pokemon2_name.lower()}")

    if not p1_data or not p2_data:
        return "Error: Could not fetch data for one or both Pokémon. Please check the names."

    # 2. Create Pokémon state objects for the battle
    pokemon1 = {
        "name": p1_data['name'].capitalize(),
        "hp": p1_data['stats'][0]['base_stat'],
        "attack": p1_data['stats'][1]['base_stat'],
        "defense": p1_data['stats'][2]['base_stat'],
        "speed": p1_data['stats'][5]['base_stat'],
        "types": [t['type']['name'] for t in p1_data['types']],
        "moves": [m['move']['url'] for m in p1_data['moves'] if m['move']['url']],
        "status": None
    }
    pokemon2 = {
        "name": p2_data['name'].capitalize(),
        "hp": p2_data['stats'][0]['base_stat'],
        "attack": p2_data['stats'][1]['base_stat'],
        "defense": p2_data['stats'][2]['base_stat'],
        "speed": p2_data['stats'][5]['base_stat'],
        "types": [t['type']['name'] for t in p2_data['types']],
        "moves": [m['move']['url'] for m in p2_data['moves'] if m['move']['url']],
        "status": None
    }

    # 3. Determine turn order
    attacker, defender = (pokemon1, pokemon2) if pokemon1['speed'] >= pokemon2['speed'] else (pokemon2, pokemon1)
    battle_log.append(f"{attacker['name']} is faster and will attack first.\n")

    # 4. Main Battle Loop
    turn = 1
    while pokemon1['hp'] > 0 and pokemon2['hp'] > 0:
        battle_log.append(f"--- Turn {turn} ---")

        # Check for Paralysis
        if attacker['status'] == 'paralysis' and random.random() < 0.25:
            battle_log.append(f"{attacker['name']} is paralyzed and can't move!")
        else:
            # Attacker's turn
            # Select a random move that has power
            move_data = None
            while not move_data:
                random_move_url = random.choice(attacker['moves'])
                potential_move_data = await _make_api_request(random_move_url)
                if potential_move_data and potential_move_data['power'] is not None and potential_move_data['power'] > 0:
                    move_data = potential_move_data

            move_name = move_data['name'].replace('-', ' ').title()
            move_power = move_data['power']
            move_type = move_data['type']['name']
            battle_log.append(f"{attacker['name']} used {move_name}!")

            # Calculate type effectiveness
            effectiveness = 1.0
            for def_type in defender['types']:
                effectiveness *= TYPE_EFFECTIVENESS.get(move_type, {}).get(def_type, 1.0)

            if effectiveness > 1:
                battle_log.append("It's super effective!")
            elif effectiveness < 1 and effectiveness > 0:
                battle_log.append("It's not very effective...")
            elif effectiveness == 0:
                battle_log.append(f"It doesn't affect {defender['name']}...")

            # Simplified Damage Calculation
            damage = int((((2/5 + 2) * move_power * (attacker['attack'] / defender['defense'])) / 50) * effectiveness + 2)

            # Apply Burn attack drop
            if attacker['status'] == 'burn':
                damage = int(damage * 0.5)

            defender['hp'] -= damage
            battle_log.append(f"{defender['name']} took {damage} damage and has {max(0, defender['hp'])} HP remaining.")

            # Check for fainting
            if defender['hp'] <= 0:
                battle_log.append(f"{defender['name']} fainted!")
                break

            # Apply status effects from the move
            if 'meta' in move_data and move_data['meta'] and not defender['status']:
                ailment = move_data['meta']['ailment']['name']
                chance = move_data['meta']['ailment_chance']
                if ailment in ['paralysis', 'burn', 'poison'] and random.random() < (chance / 100.0):
                    defender['status'] = ailment
                    battle_log.append(f"{defender['name']} was afflicted with {ailment}!")


        # Apply end-of-turn status damage
        if attacker['status'] == 'poison' or attacker['status'] == 'burn':
            # Calculate status damage based on the attacker's original max HP
            original_max_hp = p1_data['stats'][0]['base_stat'] if attacker == pokemon1 else p2_data['stats'][0]['base_stat']
            status_damage = int(original_max_hp / 8) # 1/8th of max HP
            attacker['hp'] -= status_damage
            battle_log.append(f"{attacker['name']} took {status_damage} damage from its {attacker['status']}.")
            if attacker['hp'] <= 0:
                battle_log.append(f"{attacker['name']} fainted!")
                break

        # Swap attacker and defender for the next turn
        attacker, defender = defender, attacker
        turn += 1
        battle_log.append("") # Add a blank line for readability

    # 5. Determine the winner
    winner = pokemon1 if pokemon1['hp'] > 0 else pokemon2
    battle_log.append(f"--- Battle Over ---")
    battle_log.append(f"The winner is {winner['name']}!")

    return "\n".join(battle_log)

@mcp.tool()
async def get_type_effectiveness(attacking_type: str, defending_type: str) -> str:
    """
    Get the type effectiveness multiplier when one type attacks another.
    
    Args:
        attacking_type: The type of the attacking move (e.g., 'fire', 'water', 'grass')
        defending_type: The type of the defending Pokémon (e.g., 'fire', 'water', 'grass')
    """
    attacking_type = attacking_type.lower()
    defending_type = defending_type.lower()
    
    # Check if types exist in our chart
    if attacking_type not in TYPE_EFFECTIVENESS:
        return f"Error: '{attacking_type}' is not a valid Pokémon type."
    
    effectiveness = TYPE_EFFECTIVENESS[attacking_type].get(defending_type, 1.0)
    
    if effectiveness == 2.0:
        result = "Super effective (2x damage)"
    elif effectiveness == 0.5:
        result = "Not very effective (0.5x damage)"
    elif effectiveness == 0.0:
        result = "No effect (0x damage)"
    else:
        result = "Normal effectiveness (1x damage)"
    
    return f"{attacking_type.capitalize()} vs {defending_type.capitalize()}: {result}"

@mcp.tool()
async def get_pokemon_weaknesses_and_resistances(pokemon_name: str) -> str:
    """
    Get a comprehensive breakdown of a Pokémon's weaknesses and resistances based on its type(s).
    
    Args:
        pokemon_name: The name of the Pokémon to analyze
    """
    # Fetch Pokémon data
    pokemon_data = await _make_api_request(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_name.lower()}")
    if not pokemon_data:
        return f"Error: Could not find data for Pokémon '{pokemon_name}'. Please check the spelling."
    
    pokemon_types = [t['type']['name'] for t in pokemon_data['types']]
    name = pokemon_data['name'].capitalize()
    
    # Calculate overall effectiveness for each attacking type
    weaknesses = []  # 2x or more damage
    resistances = []  # 0.5x or less damage
    immunities = []  # 0x damage
    
    for attacking_type in TYPE_EFFECTIVENESS.keys():
        total_effectiveness = 1.0
        for defending_type in pokemon_types:
            total_effectiveness *= TYPE_EFFECTIVENESS[attacking_type].get(defending_type, 1.0)
        
        if total_effectiveness >= 2.0:
            multiplier = "4x" if total_effectiveness == 4.0 else "2x"
            weaknesses.append(f"{attacking_type.capitalize()} ({multiplier})")
        elif total_effectiveness <= 0.5 and total_effectiveness > 0:
            multiplier = "0.25x" if total_effectiveness == 0.25 else "0.5x"
            resistances.append(f"{attacking_type.capitalize()} ({multiplier})")
        elif total_effectiveness == 0:
            immunities.append(attacking_type.capitalize())
    
    # Format the report
    report = f"--- Type Analysis for {name} ---\n"
    report += f"Types: {', '.join([t.capitalize() for t in pokemon_types])}\n\n"
    
    if weaknesses:
        report += f"Weaknesses (takes extra damage):\n  {', '.join(weaknesses)}\n\n"
    else:
        report += "Weaknesses: None\n\n"
    
    if resistances:
        report += f"Resistances (takes reduced damage):\n  {', '.join(resistances)}\n\n"
    else:
        report += "Resistances: None\n\n"
    
    if immunities:
        report += f"Immunities (no damage):\n  {', '.join(immunities)}\n"
    else:
        report += "Immunities: None\n"
    
    return report

# The main entry point to run the server
if __name__ == "__main__":
    # This starts the server and makes it listen for messages over stdio.
    # 'stdio' is a standard way for MCP servers to communicate with clients on the same machine.
    logging.info("server is runningggg")
    mcp.run(transport='stdio')
    logging.info("server is running")