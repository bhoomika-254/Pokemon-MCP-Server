# Pokémon MCP Server

A Model Context Protocol (MCP) server that gives AI models access to comprehensive Pokémon data and battle simulation capabilities. Connect this server to Claude Desktop to chat about Pokémon with real data and simulate battles!

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Claude Desktop app

### 1. Install Dependencies

Whatever commands are present inside the ```bash ---- ```. copy them as it is.
Clone this repository and install the required packages:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Test the Server

Run the server to make sure it works:

```bash
python server.py
```

You should see: `server is runningggg`

Press `Ctrl+C` to stop the server.

### 3. Connect to Claude Desktop

#### Step 3.1: Install Claude Desktop
Download and install [Claude Desktop](https://claude.ai/download) if you haven't already.

#### Step 3.2: Configure the Server

2. Initialize your project. 
   In the terminal type this:
```bash
   uv init pokemon-mcp-server
   uv run mcp install server.py
```

3. This creates a configuration file which is saved in some similar fashion 
   - claude_desktop_config.json
   that looks like this: 
   ```bash
   {
      "mcpServers": {
         "pokemon-server": {
            "command": "C:\\Users\\your_file_path",
            "args": [
            "run",
            "--with",
            "mcp[cli]",
            "mcp",
            "run",
            "C:\\Users\\your_file_path"
            ]
         }
      }
   }
   ```

   This configuration file can be viewed here:
   - Press Win + R.
   - Type: %APPDATA%\Claude
   - Press Enter and it should open a folder named Claude.

#### Step 3.3: Connect to Claude Desktop

- Go to Settings -> Developer -> Click on "Edit Config" -> Add the claude_desktop_config.json file. 

#### Step 3.4: Restart Claude Desktop
Close and reopen Claude Desktop for the changes to take effect. Changes might take time to reflect.

## 🧪 Testing the Server

Once connected, test these features in Claude Desktop:

### 1. Get Pokémon Data
Ask Claude:
```
"Can you get information about Pikachu?"
```

### 2. Simulate a Battle
Ask Claude:
```
"Simulate a battle between Charizard and Blastoise"
```

### 3. Check Type Effectiveness
Ask Claude:
```
"What are Garchomp's weaknesses and resistances?"
```

## 🎯 Features

### Pokémon Data Resource
- Complete stats (HP, Attack, Defense, etc.)
- Type information and evolution chains
- Detailed move information with power, accuracy, and effects
- Physical characteristics (height, weight)

### Battle Simulation
- Realistic turn-based combat
- Type effectiveness calculations (Fire beats Grass, Water beats Fire, etc.)
- Status effects: Paralysis, Burn, Poison
- Detailed battle logs showing each turn

### Type Analysis Tools
- Check effectiveness between any two types
- Analyze a Pokémon's weaknesses and resistances
- Strategic team building information

## 🔧 Troubleshooting

**Server won't connect to Claude:**
- Make sure the path in the configuration file is correct
- Check that Python is installed and accessible from command line
- Verify the JSON syntax is correct (no missing commas or brackets)

**Permission errors:**
- On Mac, you might need to allow Claude Desktop in System Preferences > Security & Privacy
- Make sure Claude Desktop has permission to run Python scripts

**Python not found:**
- Use the full path to Python in the configuration:
  - Windows: `"C:/Python39/python.exe"`
  - Mac: `"/usr/bin/python3"`

## 📋 What You Can Do

Once everything is set up, you can have natural conversations with Claude about Pokémon:

- **"Tell me about Mewtwo's stats and abilities"**
- **"Who would win between Pikachu and Raichu?"**
- **"What moves should I teach my Charizard?"**
- **"What types is Dragon weak against?"**
- **"Build me a balanced team with good type coverage"**

The server uses real data from [PokéAPI](https://pokeapi.co/) to ensure accuracy and completeness.

## 🛠️ Technical Details

- **Framework**: FastMCP for Model Context Protocol
- **Data Source**: PokéAPI for real-time Pokémon data
- **Language**: Python 3.8+
- **Dependencies**: `fastmcp`, `httpx` for API requests

## 📁 Project Structure
```
Foldername/
├── server.py              # Main MCP server
├── requirements.txt       # Python dependencies
└── README.md             # This guide
```

---

