#  Create a Knowledge Graph Using LLM

An AI project that extracts knowledge from text and visualizes it as an interactive graph. It uses OpenAI's GPT-4 to identify entities and relationships, then creates a beautiful, interactive visualization.


## What It Does

This tool takes any text and:
1. **Extracts entities** (people, companies, products, concepts)
2. **Identifies relationships** between entities (Subject-Predicate-Object triples)
3. **Standardizes entity names** (e.g., "Apple", "tech giant", "Apple Inc." → "apple inc")
4. **Visualizes everything** as an interactive knowledge graph

##  Example Output
You give it a sample text like this:

   "Apple Inc. announced a new iPhone model yesterday. The tech giant, based in Cupertino, 
    said the device would be available next month. Tim Cook, CEO of Apple, presented the new product.
    The iPhone features an improved camera system and longer battery life. Apple's stock price rose 
    following the announcement. Analysts predict strong sales for the holiday season. Meanwhile, 
    Samsung Electronics is preparing its own product launch. The South Korean company plans to 
    unveil a new Galaxy smartphone next week. Industry experts expect intense competition between 
    the two tech giants in the coming months. Both companies are investing heavily in research 
    and development. The smartphone market has become increasingly competitive in recent years. "
    
  it will then create a knowlege graph drawing relationships from the tex; for example:
   
   - Tim Cook → CEO of → Apple Inc.
   - Apple Inc. → announced → iPhone
   - iPhone → features → improved camera
   - Samsung → competes with → Apple Inc.

##  Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/Ikein-Sarah/knowledge_graph_project.git
   cd knowledge_graph_project
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
```
   OPENAI_API_KEY=your-api-key-here
```

4. **Run the script**
```bash
   python main.py
```

5. **View the result**
   
   The script will generate `knowledge_graph.html` and open it in your browser automatically.

## 📁 Project Structure
```
knowledge_graph_project/
├── main.py              # Main script with all functions
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables (create this)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🔧 How It Works

### 1. Text Cleaning & Chunking
```python
text = clean_text(text)      # Remove special characters, normalize
chunks = chunk_text(text)     # Split into manageable pieces
```

### 2. Triple Extraction (using GPT-4)
```python
triples = extract_triples_with_llm(chunk)
# Returns: [{"subject": "tim cook", "predicate": "is ceo of", "object": "apple inc"}]
```

### 3. Entity Standardization (using GPT-4)
```python
standardization_map = standardize_entities_with_llm(entities)
# Groups: {"apple inc": ["apple", "tech giant", "the company"]}
```

### 4. Visualization (using PyVis)
```python
create_knowledge_graph(triples, standardization_map)
# Generates interactive HTML graph
```

##  Customization

### Change the Input Text

Edit the `large_sample_text` variable in `main.py`:
```python
large_sample_text = """
Your custom text here...
"""
```

### Adjust Chunk Size

For longer texts, modify the chunk size:
```python
chunks = chunk_text(text, max_chunk_size=800)  # Default is 500
```

### Customize Graph Appearance

Modify the network settings in `create_knowledge_graph()`:
```python
net = Network(
    height="1200px",      # Graph height
    width="100%",         # Graph width
    bgcolor="#222222",    # Background color
    font_color="white"    # Text color
)
```

##  Use Cases

- **Research**: Visualize relationships in academic papers
- **Business Intelligence**: Map company relationships and market dynamics
- **Content Analysis**: Understand key themes and connections in documents
- **Education**: Create visual summaries of complex topics
- **Journalism**: Map relationships in investigative stories

##  Tech Stack

- **Python 3.11** - Core programming language
- **OpenAI GPT-4** -   Used for natural language processing and entity extraction
- **PyVis** - Used for creating the interactive network visualization
- **python-dotenv** - Environment variable management

## 📝 Example Output

When you run the script with the sample text about Apple and Samsung, you'll get an interactive graph showing:

- **Blue nodes**: Subject entities
- **Red nodes**: Object entities
- **Labeled edges**: Relationships between entities

You can:
- Drag nodes to rearrange
- Zoom in/out
- Hover over nodes for details
- Click and drag to explore

##  Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



⭐ If you found this project helpful, please give it a star!
