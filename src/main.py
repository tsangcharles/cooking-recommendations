#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from store_selector import FlippStoreSelector
from flyer_downloader import FlyerDownloader
from gemini_recommender import GeminiRecommender
from discord_notifier import DiscordNotifier

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Gemini API key
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY not found in .env file")
        print("Please create a .env file with your Gemini API key:")
        print("GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    print("=" * 60)
    print("No Frills Cooking Recommendation System")
    print("=" * 60)
    print()
    
    # Configuration from environment variables
    POSTAL_CODE = os.getenv('POSTAL_CODE', 'L6E1T8')
    NUM_PEOPLE = int(os.getenv('NUM_PEOPLE', '2'))
    NUM_MEALS = int(os.getenv('NUM_MEALS', '7'))
    CUISINE = os.getenv('CUISINE', 'Chinese')
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    selector = None
    
    try:
        # Step 1: Setup browser and set postal code
        print("STEP 1: Setting up browser and setting postal code...")
        selector = FlippStoreSelector(headless=HEADLESS)
        selector.setup_driver()
        
        if not selector.select_store(postal_code=POSTAL_CODE):
            print("Failed to set postal code. Exiting...")
            sys.exit(1)
        
        print()
        
        # Step 2: Download flyer images
        print("STEP 2: Downloading flyer images...")
        downloader = FlyerDownloader(selector.driver, output_dir="data")
        flyer_files = downloader.download_flyers()
        
        if not flyer_files:
            print("No flyer images downloaded. Exiting...")
            sys.exit(1)
        
        print()
        
        # Step 3: Stitch images together
        print("STEP 3: Stitching flyer images together...")
        from image_stitcher import ImageStitcher
        stitcher = ImageStitcher(output_dir="output")
        stitched_image = stitcher.stitch_images(flyer_files, output_filename="complete_flyer.jpg")
        
        if not stitched_image:
            print("Failed to stitch images. Exiting...")
            sys.exit(1)
        
        print()
        
        # Step 4: Get recommendations from Gemini
        print("STEP 4: Getting recommendations from Gemini AI...")
        recommender = GeminiRecommender(api_key=gemini_api_key)
        recommendations = recommender.get_recommendations(
            flyer_image_path=stitched_image,
            num_people=NUM_PEOPLE,
            num_meals=NUM_MEALS,
            cuisine_preference=CUISINE
        )
        
        if not recommendations:
            print("Failed to get recommendations. Exiting...")
            sys.exit(1)
        
        # Save recommendations
        output_file = recommender.save_recommendations(recommendations)
        
        print()
        print("=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        print()
        print(recommendations)
        print()
        print("=" * 60)
        print(f"Complete! Recommendations saved to: {output_file}")
        print(f"Stitched flyer saved to: {stitched_image}")
        print("=" * 60)
        
        # Send to Discord if webhook URL is configured
        if DISCORD_WEBHOOK_URL:
            print()
            print("Sending to Discord...")
            notifier = DiscordNotifier(DISCORD_WEBHOOK_URL)
            notifier.send_recommendations(recommendations, stitched_image)
        else:
            print()
            print("💡 Tip: Set DISCORD_WEBHOOK_URL in .env to get notifications in Discord!")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Clean up
        if selector:
            print("\nClosing browser...")
            selector.close()

if __name__ == "__main__":
    main()
