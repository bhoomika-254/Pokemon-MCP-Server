# Pokémon MCP Server

- A comprehensive Model Context Protocol (MCP) server that provides AI models with access to Pokémon data and battle simulation capabilities. 
- Connected it to Claude MCP Client.

## Features

### 🎯 **Pokémon Data Resource**
- **Comprehensive Pokémon Information**: Access detailed data for any Pokémon including stats, types, abilities, moves, and evolution chains
- **Enhanced Move Details**: Get detailed information about moves including power, accuracy, PP, and effects
- **Evolution Chains**: Complete evolution line information with visual progression

### ⚔️ **Battle Simulation Tool**
- **Realistic Battle Mechanics**: Implements core Pokémon battle systems
- **Type Effectiveness**: Full type chart with accurate damage multipliers
- **Status Effects**: Paralysis, Burn, and Poison with proper mechanics
- **Turn-Based Combat**: Speed-based turn order with detailed battle logs
- **Damage Calculation**: Realistic damage formulas based on stats and move power

### 🛡️ **Type Analysis Tools**
- **Type Effectiveness Lookup**: Check effectiveness between any two types
- **Weakness/Resistance Analysis**: Comprehensive breakdown of a Pokémon's defensive matchups
- **Strategic Planning**: Perfect for team building and battle preparation

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/bhoomika-254/Pokemon-MCP-Server.git
   cd Pokemon-MCP-Server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python server.py
   ```

## Usage

### 📊 **Pokémon Data Resource**

Access comprehensive Pokémon data using the resource URI pattern:

```
mcp://pokemon-server/pokemon/{pokemon_name}
```

**Example**: `mcp://pokemon-server/pokemon/pikachu`

**Returns**:
- Basic information (ID, types, height, weight)
- Complete base stats with total
- All abilities
- Evolution chain progression
- Detailed move information (first 5 moves with full details)
- Additional move names for reference

### 🔥 **Battle Simulation Tool**

Simulate realistic battles between any two Pokémon:

```python
simulate_battle(pokemon1_name: str, pokemon2_name: str) -> str
```

**Example**: Simulate a battle between Pikachu and Charizard

**Features**:
- Speed-based turn order
- Type effectiveness calculations
- Status effect mechanics (Paralysis, Burn, Poison)
- Detailed turn-by-turn battle logs
- Winner determination

### 🎯 **Type Effectiveness Tool**

Check type matchups for strategic planning:

```python
get_type_effectiveness(attacking_type: str, defending_type: str) -> str
```

**Example**: Check how Fire attacks affect Grass types

**Returns**:
- Damage multiplier information
- Effectiveness description (Super effective, Not very effective, etc.)

### 🛡️ **Pokémon Type Analysis Tool**

Get comprehensive defensive analysis for any Pokémon:

```python
get_pokemon_weaknesses_and_resistances(pokemon_name: str) -> str
```

**Example**: Analyze Charizard's defensive matchups

**Returns**:
- All weaknesses with damage multipliers
- All resistances with damage reduction
- Complete immunities
- Strategic recommendations

#### `simulate_battle(pokemon1_name, pokemon2_name)`
- **Description**: Simulates a battle between two Pokémon
- **Parameters**:
  - `pokemon1_name`: Name of the first Pokémon
  - `pokemon2_name`: Name of the second Pokémon
- **Returns**: Detailed battle log with turn-by-turn actions and winner

#### `get_type_effectiveness(attacking_type, defending_type)`
- **Description**: Gets type effectiveness multiplier
- **Parameters**:
  - `attacking_type`: The attacking move's type
  - `defending_type`: The defending Pokémon's type
- **Returns**: Effectiveness information and damage multiplier

#### `get_pokemon_weaknesses_and_resistances(pokemon_name)`
- **Description**: Analyzes a Pokémon's defensive type matchups
- **Parameters**:
  - `pokemon_name`: Name of the Pokémon to analyze
- **Returns**: Complete breakdown of weaknesses, resistances, and immunities

## Battle Mechanics

### Type Effectiveness Chart
The server implements a comprehensive type effectiveness chart with 18 Pokémon types:
- **Super Effective**: 2x damage
- **Not Very Effective**: 0.5x damage  
- **No Effect**: 0x damage
- **Dual Types**: Multipliers stack (e.g., 2x × 2x = 4x damage)

### Status Effects
1. **Paralysis**: 25% chance to skip turn
2. **Burn**: Reduces attack damage by 50%, deals 1/8 max HP damage per turn
3. **Poison**: Deals 1/8 max HP damage per turn

### Damage Calculation
```
Damage = (((2/5 + 2) × Move Power × (Attack / Defense)) / 50) × Type Effectiveness + 2
```

## Data Source

This server uses the [PokéAPI](https://pokeapi.co/) to fetch real-time Pokémon data, ensuring accuracy and completeness.

## Development

### Requirements
- Python 3.8+
- FastMCP framework
- httpx for API requests
- PokéAPI
- uv for connecting claude to mcp server.

### Project Structure
```
Pokemon-MCP-Server/
├── server.py              # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
```

### How to connect this with Claude Client

To connect your Pokémon MCP Server with Claude Desktop, follow these steps:

#### 1. **Install Claude Desktop**
Download and install Claude Desktop from [Anthropic's website](https://claude.ai/desktop).

#### 2. **Configure MCP Server in Claude**
Claude Desktop uses a configuration file to connect to MCP servers. You need to add your Pokémon server to this configuration.

**For Windows:**
1. Navigate to: `%APPDATA%\Claude\claude_desktop_config.json`

#### 3. **Verify Connection**
Once Claude Desktop restarts, you should see the Pokémon MCP Server available. You can test it by:

1. **Testing the Resource**: Ask Claude to access Pokémon data:
   ```
   "Can you get information about Pikachu using the Pokémon resource?"
   ```

2. **Testing Battle Simulation**: Ask Claude to simulate a battle:
   ```
   "Can you simulate a battle between Charizard and Blastoise?"
   ```

3. **Testing Type Analysis**: Ask Claude to analyze type effectiveness:
   ```
   "What are Garchomp's weaknesses and resistances?"
   ```

