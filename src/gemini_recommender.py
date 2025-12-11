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
I need help planning EASY meals and grocery shopping based on this No Frills flyer.

Requirements:
- Number of people: {num_people}
- Number of meals to plan: {num_meals} meals, for each meal, there should be {num_people} dishes (one per person)
- Cuisine preference: {cuisine_preference} food, it should be genuine cuisine from that culture
- Focus on items that are ON SALE in this flyer

Please analyze this flyer and provide:

1. **Shopping List**: List specific items from the flyer that are on sale that would be good for cooking {cuisine_preference} food. Include the prices if visible. Shopping list must be comprehensive so everything in the meal plan can be made.

2. **Meal Plan**: Suggest {num_meals} {cuisine_preference} recipes/meals that can be made using the ingredients from the flyer. For each meal:
   - Meal name (Provide a chinese name as well)
   - Key ingredients (highlighting what's on sale from the flyer)
   - Brief cooking instructions (2-3 sentences) with PRECEISE MEASUREMENTS for each ingredient.
   - Estimated servings ({num_people} people)

Please be specific and practical. While it would be great to buy stuff from this flyer as these items are on sale, you do not need to limit yourself only to items shown in the flyer if you can suggest better alternatives that fit within a reasonable budget.
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
