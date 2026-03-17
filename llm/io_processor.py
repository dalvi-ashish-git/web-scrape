import json
import re

class IOProcessor:
    @staticmethod
    def prepare_input(raw_data_list, target_schema="Name, Price, Description, Status"):
        """
        Input Processing: Advanced Prompt Engineering to ensure data transformation.
        """
        # We join the snippets into a numbered list so the AI understands they are separate items
        context = "\n".join([f"{i+1}. {item}" for i, item in enumerate(raw_data_list[:50])])
        
        prompt = f"""
        ACT AS: An Expert Data Extraction Agent.
        TASK: Convert messy web-scraped snippets into a professional, structured JSON database.
        
        TARGET SCHEMA: {target_schema}
        
        RULES:
        1. ENTITY EXTRACTION: Do not just copy the snippet. Extract the actual Name, the actual Price (number only), and a clean Status.
        2. CLEANING: Remove ellipsis (...), HTML artifacts, or extra whitespace.
        3. NORMALIZATION: If you see "In stock" or "Available", set Status to "Available". 
        4. FORMAT: Return ONLY a valid JSON array of objects. No markdown, no "```json", no conversational text.
        5. MISSING DATA: If a field is missing, use "N/A" or 0 for numbers.
        
        RAW DATA SNIPPETS:
        {context}
        
        JSON OUTPUT:
        """
        return prompt

    @staticmethod
    def parse_output(raw_llm_response):
        """
        Output Processing: Sanitizes the string into a Python list.
        """
        try:
            # Robust cleaning in case Gemini adds markdown or backticks
            clean_json = re.sub(r'```json|```', '', raw_llm_response).strip()
            # Find the first '[' and last ']' to handle any stray text outside the JSON
            start_idx = clean_json.find('[')
            end_idx = clean_json.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                clean_json = clean_json[start_idx:end_idx]
            
            return json.loads(clean_json)
        except Exception as e:
            print(f"I/O Error: {e}")
            return []