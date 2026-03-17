import google.generativeai as genai
import os
from dotenv import load_dotenv
from .io_processor import IOProcessor
from .data_refiner import refine_structured_data

# Load environment variables (API Key)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=api_key)

class LLMProcessor:
    def __init__(self):
        """
        Initializes the LLM Engine using the 2026 stable Flash model.
        """
        # Using gemini-2.5-flash as the reliable workhorse for 2026
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.io = IOProcessor()

    def process_scraped_content(self, raw_headings, target_schema="Name, Price, Description"):
        """
        The full AI Pipeline: Input Prep -> LLM Query -> Output Parsing -> Refinement.
        """
        if not raw_headings:
            return None

        # Step 1: Prepare the custom prompt with the user's schema
        prompt = self.io.prepare_input(raw_headings, target_schema)

        try:
            # Step 2: Query the Gemini API
            response = self.model.generate_content(prompt)
            
            # Step 3: Parse the string into JSON
            structured_json = self.io.parse_output(response.text)
            
            # Step 4: Refine the data using the Pandas module
            final_df = refine_structured_data(structured_json)
            
            return final_df
            
        except Exception as e:
            if "404" in str(e):
                print("Error: Model name not recognized. Check gemini_service.py init.")
            else:
                print(f"LLM Module Error: {e}")
            return None