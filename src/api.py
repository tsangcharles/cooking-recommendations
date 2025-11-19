#!/usr/bin/env python3
import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
from datetime import datetime

from store_selector import FlippStoreSelector
from flyer_downloader import FlyerDownloader
from gemini_recommender import GeminiRecommender
from image_stitcher import ImageStitcher
from discord_notifier import DiscordNotifier

load_dotenv()

app = FastAPI(title="No Frills Cooking Recommendations")

# Get the parent directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure required directories exist
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class RecommendationRequest(BaseModel):
    postal_code: str = "L6E1T8"
    num_people: int = 2
    num_meals: int = 7
    cuisine: str = "Chinese"
    headless: bool = True

class DiscordRequest(BaseModel):
    webhook_url: str

# Global state to store latest results
latest_results = {
    "recommendations": None,
    "flyer_image": None,
    "timestamp": None,
    "status": "idle",
    "status_message": "Ready",
    "error": None
}

@app.get("/")
async def read_root():
    """Serve the frontend"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/config")
async def get_default_config():
    """Get default configuration from environment variables"""
    return {
        "postal_code": os.getenv('POSTAL_CODE', 'L6E1T8'),
        "num_people": int(os.getenv('NUM_PEOPLE', '2')),
        "num_meals": int(os.getenv('NUM_MEALS', '7')),
        "cuisine": os.getenv('CUISINE', 'Chinese'),
        "headless": os.getenv('HEADLESS', 'true').lower() == 'true',
        "discord_webhook_url": os.getenv('DISCORD_WEBHOOK_URL', '')
    }

@app.get("/api/status")
async def get_status():
    """Get current processing status"""
    return {
        "status": latest_results["status"],
        "status_message": latest_results["status_message"],
        "timestamp": latest_results["timestamp"],
        "error": latest_results["error"],
        "has_results": latest_results["recommendations"] is not None
    }

@app.get("/api/recommendations")
async def get_recommendations():
    """Get the latest recommendations"""
    if latest_results["recommendations"] is None:
        raise HTTPException(status_code=404, detail="No recommendations available yet")
    
    return {
        "recommendations": latest_results["recommendations"],
        "flyer_image": latest_results["flyer_image"],
        "timestamp": latest_results["timestamp"]
    }

@app.get("/api/flyer-image")
async def get_flyer_image():
    """Serve the flyer image"""
    if latest_results["flyer_image"] and os.path.exists(latest_results["flyer_image"]):
        return FileResponse(latest_results["flyer_image"], media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Flyer image not found")

def generate_recommendations_task(request: RecommendationRequest):
    """Background task to generate recommendations"""
    latest_results["status"] = "processing"
    latest_results["status_message"] = "Initializing..."
    latest_results["error"] = None
    selector = None
    
    try:
        # Get Gemini API key
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            raise Exception("GEMINI_API_KEY not found in .env file")
        
        # Step 1: Setup browser and set postal code
        latest_results["status_message"] = "Setting up browser and postal code..."
        print(f"Setting up browser for postal code: {request.postal_code}")
        selector = FlippStoreSelector(headless=request.headless)
        selector.setup_driver()
        
        if not selector.select_store(postal_code=request.postal_code):
            raise Exception("Failed to set postal code")
        
        # Step 2: Download flyer images
        latest_results["status_message"] = "Downloading flyer images..."
        print("Downloading flyer images...")
        downloader = FlyerDownloader(selector.driver, output_dir="data")
        flyer_files = downloader.download_flyers()
        
        if not flyer_files:
            raise Exception("No flyer images downloaded")
        
        # Step 3: Stitch images together
        latest_results["status_message"] = "Stitching flyer images together..."
        print("Stitching flyer images...")
        stitcher = ImageStitcher(output_dir="output")
        stitched_image = stitcher.stitch_images(flyer_files, output_filename="complete_flyer.jpg")
        
        if not stitched_image:
            raise Exception("Failed to stitch images")
        
        # Step 4: Get recommendations from Gemini
        latest_results["status_message"] = "Analyzing flyer with Gemini AI..."
        print("Getting recommendations from Gemini AI...")
        recommender = GeminiRecommender(api_key=gemini_api_key)
        recommendations = recommender.get_recommendations(
            flyer_image_path=stitched_image,
            num_people=request.num_people,
            num_meals=request.num_meals,
            cuisine_preference=request.cuisine
        )
        
        if not recommendations:
            raise Exception("Failed to get recommendations")
        
        # Save recommendations
        latest_results["status_message"] = "Saving recommendations..."
        recommender.save_recommendations(recommendations)
        
        # Update results
        latest_results["recommendations"] = recommendations
        latest_results["flyer_image"] = stitched_image
        latest_results["timestamp"] = datetime.now().isoformat()
        latest_results["status"] = "completed"
        latest_results["status_message"] = "Complete!"
        
        print("Recommendations generated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        latest_results["status"] = "error"
        latest_results["status_message"] = f"Error: {str(e)}"
        latest_results["error"] = str(e)
        
    finally:
        if selector:
            selector.close()

@app.post("/api/generate")
async def generate_recommendations(request: RecommendationRequest, background_tasks: BackgroundTasks):
    """Generate cooking recommendations"""
    if latest_results["status"] == "processing":
        raise HTTPException(status_code=409, detail="Already processing a request")
    
    # Run generation in background
    background_tasks.add_task(generate_recommendations_task, request)
    
    return {
        "message": "Recommendation generation started",
        "status": "processing"
    }

@app.post("/api/send-discord")
async def send_to_discord(request: DiscordRequest):
    """Send recommendations to Discord"""
    if latest_results["recommendations"] is None:
        raise HTTPException(status_code=404, detail="No recommendations available to send")
    
    try:
        notifier = DiscordNotifier(request.webhook_url)
        success = notifier.send_recommendations(
            latest_results["recommendations"],
            latest_results["flyer_image"]
        )
        
        if success:
            return {"message": "Successfully sent to Discord", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to send to Discord")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending to Discord: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
