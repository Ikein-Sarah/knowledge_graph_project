#pip install openai python-dotenv pyvis


import openai
from openai import OpenAI
import json
import re
from pyvis.network import Network
import textwrap
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def clean_text(text):
    """Clean and preprocess text before processing"""
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,;:!?\'"-]', ' ', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.lower()


def chunk_text(text, max_chunk_size=500):
    """Split text into manageable chunks"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def extract_triples_with_llm(text_chunk):
    """Extract S-P-O triples from text using LLM"""
    SYSTEM_PROMPT = """
    You are an advanced AI system specialized in knowledge extraction and knowledge graph generation.
    Your expertise includes identifying consistent entity references and meaningful relationships in text.
    CRITICAL INSTRUCTION: All relationships (predicates) MUST be no more than 3 words maximum.
    """

    USER_PROMPT = f"""
    Extract Subject-Predicate-Object triples from this text (between triple backticks):
    ```{text_chunk}```

    Rules:
    1. Use consistent names for entities (prefer most complete form)
    2. Predicates must be 1-3 words max
    3. Make all text lowercase
    4. Replace pronouns with actual entities
    5. Return ONLY a JSON array of {{"subject", "predicate", "object"}} objects

    Example output:
    [{{"subject": "john smith", "predicate": "works at", "object": "acme corp"}}]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": USER_PROMPT.strip()}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()
        triples = json.loads(content)

        # Validate and normalize triples
        valid_triples = []
        for triple in triples:
            if all(key in triple for key in ["subject", "predicate", "object"]):
                valid_triples.append({
                    "subject": triple["subject"].lower().strip(),
                    "predicate": triple["predicate"].lower().strip(),
                    "object": triple["object"].lower().strip()
                })
        return valid_triples

    except Exception as e:
        print(f"Error extracting triples: {e}")
        print("Raw response:", response.choices[0].message.content.strip() if 'response' in locals() else "No response")
        return None


def standardize_entities_with_llm(entities):
    """Standardize entity names using LLM with robust JSON handling"""
    if not entities:
        print("No entities provided for standardization")
        return {}

    # Clean and prepare entities
    entity_list = [str(e).strip() for e in entities if str(e).strip()]
    if not entity_list:
        print("No valid entities after cleaning")
        return {}

    SYSTEM_PROMPT = """
    You are an expert in entity resolution. Group these entity names that refer to the same concept.
    Provide a standardized name for each group and its variants. Return ONLY valid JSON.
    Important: Your response must contain ONLY the JSON object, no additional text or explanation.
    """

    USER_PROMPT = f"""
    Standardize these entities:
    {entity_list}

    Return JSON where keys are standardized names and values are variant arrays.
    Example:
    {{
      "apple inc": ["tech giant", "apple"],
      "tim cook": ["ceo", "apple ceo"]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": USER_PROMPT.strip()}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        # Get the raw content
        content = response.choices[0].message.content.strip()

        # Try to parse directly first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If direct parse fails, try to extract JSON from the response
            try:
                # Look for the first { and last }
                json_str = content[content.find('{'):content.rfind('}') + 1]
                return json.loads(json_str)
            except Exception as e:
                print(f"Could not parse standardization response: {e}")
                print("Raw response:", content)
                return {}

    except Exception as e:
        print(f"Error in standardization API call: {e}")
        return {}


def create_knowledge_graph(triples, standardization_map=None):
    """Create and display a knowledge graph visualization"""
    if not triples:
        print("No triples provided for visualization")
        return None

    try:
        # Create network
        net = Network(height="1200px", width="100%", directed=True,
                      notebook=False, bgcolor="#222222", font_color="white")

        # Create standardization lookup if available
        std_lookup = {}
        if standardization_map:
            try:
                for standard, variants in standardization_map.items():
                    if isinstance(variants, list):
                        std_lookup[str(standard)] = str(standard)
                        for variant in variants:
                            std_lookup[str(variant)] = str(standard)
            except Exception as e:
                print(f"Error creating standardization lookup: {e}")
                # Continue without standardization

        # Add nodes and edges
        added_nodes = set()
        for triple in triples:
            try:
                subj = std_lookup.get(triple["subject"], triple["subject"])
                obj = std_lookup.get(triple["object"], triple["object"])

                if subj not in added_nodes:
                    net.add_node(subj, title=subj, color="#6a9df6", size=25)
                    added_nodes.add(subj)
                if obj not in added_nodes:
                    net.add_node(obj, title=obj, color="#f66a6a", size=20)
                    added_nodes.add(obj)

                net.add_edge(subj, obj, label=triple["predicate"], width=1)
            except KeyError as e:
                print(f"Skipping malformed triple: {triple} (missing key: {e})")
                continue

        # Configure physics
        net.set_options("""
               {
                   "physics": {
                       "forceAtlas2Based": {
                           "gravitationalConstant": -100,
                           "centralGravity": 0.01,
                           "springLength": 200,
                           "springConstant": 0.08
                       },
                       "minVelocity": 0.75,
                       "solver": "forceAtlas2Based"
                   }
               }
               """)

        # Save and open
        output_file = "knowledge_graph.html"
        try:
            net.save_graph(output_file)
            print(f"Graph saved to {os.path.abspath(output_file)}")

            # Try to open in browser
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(output_file)}")
            except:
                print("Could not open browser automatically")

            return net
        except Exception as e:
            print(f"Error saving graph: {e}")
            return None

    except Exception as e:
        print(f"Error creating graph: {e}")
        return None
def process_large_text_to_knowledge_graph(text):
    """Complete pipeline with chunking for large texts"""
    print("Cleaning text...")
    text = clean_text(text)

    print("Chunking text...")
    chunks = chunk_text(text)
    print(f"Split text into {len(chunks)} chunks")

    all_triples = []
    for i, chunk in enumerate(chunks, 1):
        print(f"\nProcessing chunk {i}/{len(chunks)}...")
        triples = extract_triples_with_llm(chunk)
        if triples:
            all_triples.extend(triples)
            print(f"Added {len(triples)} triples from this chunk")
        else:
            print("No triples extracted from this chunk")

    if not all_triples:
        print("\nNo triples extracted from any chunk")
        return None

    print(f"\nTotal triples extracted: {len(all_triples)}")

    print("\nCollecting all entities...")
    entities = {triple["subject"] for triple in all_triples}.union(
        {triple["object"] for triple in all_triples})
    print(f"Found {len(entities)} unique entities")

    print("\nStandardizing entities...")
    standardization_map = standardize_entities_with_llm(entities)
    if standardization_map:
        print(f"Created {len(standardization_map)} standardization groups")
    else:
        print("No standardization rules were generated")

    print("\nCreating knowledge graph visualization...")
    return create_knowledge_graph(all_triples, standardization_map)


# Example usage with larger text
if __name__ == "__main__":
    large_sample_text = """
    Apple Inc. announced a new iPhone model yesterday. The tech giant, based in Cupertino, 
    said the device would be available next month. Tim Cook, CEO of Apple, presented the new product.
    The iPhone features an improved camera system and longer battery life. Apple's stock price rose 
    following the announcement. Analysts predict strong sales for the holiday season. Meanwhile, 
    Samsung Electronics is preparing its own product launch. The South Korean company plans to 
    unveil a new Galaxy smartphone next week. Industry experts expect intense competition between 
    the two tech giants in the coming months. Both companies are investing heavily in research 
    and development. The smartphone market has become increasingly competitive in recent years.
    """

    print("Starting knowledge graph creation...")
    result = process_large_text_to_knowledge_graph(large_sample_text)

    if result:
        print("\nKnowledge graph successfully created and opened in your browser!")
    else:
        print("\nFailed to create knowledge graph")