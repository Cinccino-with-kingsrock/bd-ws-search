import json
import re

INPUT_FILE = "data/cards_bottleneko.json"
OUTPUT_FILE = "data/clean_cards.json"

def clean_data():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        print(f"Original count: {len(raw_data)}")
        
        # 1. Deduplication Grouping
        # Key: Base ID (e.g., "BD/W47-001"), Value: List of cards
        grouped_cards = {}
        
        for card in raw_data:
            card_id = card.get("id", "")
            if not card_id:
                continue
                
            # Extract base ID: "BD/W47-001" from "BD/W47-001SP"
            # Regex: Start with anything, follow with hyphen and digits. Stop before any letters.
            # Actually, standard format is SERIES/SIDE-NUMBER[SUFFIX]
            # NUMBER is usually digits. SUFFIX is usually letters.
            # Example: BD/W47-001 -> Base: BD/W47-001
            # Example: BD/W47-T01 -> Base: BD/W47-T01 (Trial deck)
            # Example: BD/W47-101 -> Base: BD/W47-101
            # Example: BD/W47-P01 -> Base: BD/W47-P01 (Promo)
            
            # Match strictly: (Prefix)-(Digits) or (Prefix)-(Letter)(Digits)
            # But the suffix is what we want to ignore.
            # Suffixes are usually 'S', 'SP', 'SSP', 'R', 'OFR', 'HYR'...
            # Base always ends with digits? Yes.
            # So we split by '-' and check the last part.
            
            # Correct regex: Capture everything up to the last digit sequence.
            # This handles "BD/W47-001", "BD/W47-T01" (Trial), "BD/W47-101"
            # It should capture "BD/W47-001" from "BD/W47-001SP"
            # And "BD/W54-071" from "BD/W54-071a"
            
            match = re.search(r"^(.*-[\w]*?\d+)", card_id)
            base_id = match.group(1) if match else card_id
            
            if base_id not in grouped_cards:
                grouped_cards[base_id] = []
            grouped_cards[base_id].append(card)
            
        cleaned_list = []
        
        # 2. Select representative & 3. Filter fields
        for base_id, group in grouped_cards.items():
            # Sort by ID length (ascending), then by ID (for stability)
            # Shortest ID is preferred (e.g. BD/W47-001 over BD/W47-001SP)
            group.sort(key=lambda x: (len(x["id"]), x["id"]))
            
            selected_card = group[0]
            
            # Map fields
            new_card = {
                "id": selected_card.get("id"),
                "name": selected_card.get("name"),   # Already mapped in scraper
                "type": selected_card.get("type"),
                "level": selected_card.get("level"),
                "cost": selected_card.get("cost"),
                "color": selected_card.get("color"),
                "soul": selected_card.get("soul"),
                "power": selected_card.get("power"), # Already mapped
                "rare": selected_card.get("rarity"), # User wants 'rare', we have 'rarity'
                "text": selected_card.get("text"),
                "traits": selected_card.get("traits"),
                "trigger": selected_card.get("trigger")
            }
            
            # Ensure "rare" is present if user insisted (scraper has 'rarity')
            # User request: "rare: 保持原樣" (keep as is).
            # Raw API had 'rare'. My scraper mapped it to 'rarity'.
            # I should rename 'rarity' back to 'rare' for the output.
            
            cleaned_list.append(new_card)
            
        print(f"Cleaned count: {len(cleaned_list)}")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_list, f, indent=4, ensure_ascii=False)
            
        print(f"Saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clean_data()
