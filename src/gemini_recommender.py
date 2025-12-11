import google.generativeai as genai
from PIL import Image
import os

class GeminiRecommender:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
    def get_recommendations(self, flyer_image_path, num_people=2, num_meals=7, cuisine_preference="Chinese"):
        """Get cooking and shopping recommendations from Gemini based on the flyer image"""
        try:
            print("Analyzing flyer with Gemini AI...")
            
            # Open the image
            img = Image.open(flyer_image_path)
            
            # Create the prompt
            prompt = f"""
Analyze this No Frills flyer and create an EASY meal plan. Output ONLY the Shopping List and Meal Plan sections. No introductions, conclusions, or extra commentary.

Requirements:
- Number of people: {num_people}
- Number of meals to plan: {num_meals} meals, for each meal, there should be {num_people} dishes (one per person)
- Cuisine preference: {cuisine_preference} food, it should be genuine cuisine from that culture
- Focus on items that are ON SALE in this flyer

Format your response EXACTLY as follows (no additional text):

**Shopping List**
For each item, you MUST specify the quantity to buy (e.g., "2 lbs chicken thighs", "3 bunches green onions", "1 package tofu"). List items from the flyer that are on sale for cooking {cuisine_preference} food. Include prices if visible. Calculate quantities based on making {num_meals} meals for {num_people} people. Be comprehensive so everything in the meal plan can be made.

Example format:
- 2 lbs Ground Pork ($X.XX)
- 3 lbs Chicken Thighs ($X.XX)
- 1 package Firm Tofu ($X.XX)

**Meal Plan**
Suggest {num_meals} {cuisine_preference} meals. For EACH meal, create {num_people} different dishes. For each dish include:
- Dish name (Provide a name in its native language if possible)
- Key ingredients (highlighting what's on sale from the flyer)
- Brief cooking instructions (2-3 sentences) with PRECISE MEASUREMENTS for each ingredient

Be specific and practical. While prioritizing sale items from the flyer, you may suggest other ingredients if they fit within a reasonable budget.
"""
            
            # Generate content
            response = self.model.generate_content([prompt, img])
            
            print("Recommendations generated successfully!")
            return response.text
            
        except Exception as e:
            print(f"Error getting recommendations from Gemini: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def save_recommendations(self, recommendations, output_file="output/recommendations.txt"):
        """Save recommendations to a text file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(recommendations)
            print(f"Recommendations saved to: {output_file}")
            return output_file
        except Exception as e:
            print(f"Error saving recommendations: {e}")
            return None
