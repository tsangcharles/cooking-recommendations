import requests
import os

class DiscordNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        
    def send_recommendations(self, recommendations_text, flyer_image_path=None):
        """Send cooking recommendations to Discord via webhook"""
        try:
            print(f"Sending recommendations to Discord...")
            
            # Split recommendations if too long (Discord has 2000 char limit per message)
            max_length = 1900
            if len(recommendations_text) > max_length:
                # Send in chunks
                chunks = [recommendations_text[i:i+max_length] for i in range(0, len(recommendations_text), max_length)]
                
                for i, chunk in enumerate(chunks):
                    payload = {
                        "content": f"**🍽️ Your Weekly No Frills Meal Plan (Part {i+1}/{len(chunks)})**\n```\n{chunk}\n```"
                    }
                    response = requests.post(self.webhook_url, json=payload)
                    
                    if response.status_code not in [200, 204]:
                        print(f"✗ Failed to send chunk {i+1}: HTTP {response.status_code}")
                        return False
            else:
                payload = {
                    "content": f"**🍽️ Your Weekly No Frills Meal Plan**\n```\n{recommendations_text}\n```"
                }
                response = requests.post(self.webhook_url, json=payload)
                
                if response.status_code not in [200, 204]:
                    print(f"✗ Failed to send message: HTTP {response.status_code}")
                    return False
            
            # Send flyer image as attachment if available
            if flyer_image_path and os.path.exists(flyer_image_path):
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
                        return False
            
            print(f"✓ Successfully sent recommendations to Discord")
            return True
            
        except Exception as e:
            print(f"✗ Error sending to Discord: {e}")
            import traceback
            traceback.print_exc()
            return False
