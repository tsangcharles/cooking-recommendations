import requests
import os
import time

class DiscordNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        
    def send_recommendations(self, recommendations_text, flyer_image_path=None):
        """Send cooking recommendations to Discord via webhook"""
        try:
            print(f"Sending recommendations to Discord...")
            
            # Use embeds for better formatting and to handle long content
            # Each embed description can hold up to 4096 characters
            max_embed_length = 4000
            
            if len(recommendations_text) > max_embed_length:
                # Split into multiple embeds within a single message
                chunks = [recommendations_text[i:i+max_embed_length] for i in range(0, len(recommendations_text), max_embed_length)]
                
                embeds = []
                for i, chunk in enumerate(chunks):
                    embeds.append({
                        "title": f"🍽️ Your Weekly No Frills Meal Plan (Part {i+1}/{len(chunks)})",
                        "description": chunk,
                        "color": 5814783  # Blue color
                    })
                
                payload = {"embeds": embeds}
            else:
                payload = {
                    "embeds": [{
                        "title": "🍽️ Your Weekly No Frills Meal Plan",
                        "description": recommendations_text,
                        "color": 5814783  # Blue color
                    }]
                }
            
            response = requests.post(self.webhook_url, json=payload)
            
            if response.status_code not in [200, 204]:
                print(f"✗ Failed to send message: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            # Send flyer image as attachment if available (with rate limit delay)
            if flyer_image_path and os.path.exists(flyer_image_path):
                time.sleep(1)  # Wait 1 second to avoid rate limit
                
                with open(flyer_image_path, 'rb') as f:
                    files = {
                        'file': ('no_frills_flyer.jpg', f, 'image/jpeg')
                    }
                    payload = {
                        "content": "📄 Complete flyer for reference:"
                    }
                    response = requests.post(self.webhook_url, data=payload, files=files)
                    
                    if response.status_code not in [200, 204]:
                        print(f"✗ Failed to send flyer image: HTTP {response.status_code}")
                        # Don't return False here - recommendations were sent successfully
            
            print(f"✓ Successfully sent recommendations to Discord")
            return True
            
        except Exception as e:
            print(f"✗ Error sending to Discord: {e}")
            import traceback
            traceback.print_exc()
            return False
