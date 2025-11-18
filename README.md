# Cooking Recommendations with No Frills Flyer

This project automates the process of:
1. Setting your postal code on Flipp.com (L6E1T8)
2. Downloading all No Frills weekly flyer images from Flipp (specifically `extra_large*.jpg` images)
3. Stitching them into a grid layout (square-ish arrangement)
4. Using Google Gemini AI to analyze the flyer image and recommend Chinese recipes and shopping lists for 2 people for 7 meals

## Prerequisites

- Docker and Docker Compose (for containerized approach)
- OR Python 3.12+ with Chrome/Chromium installed (for local approach)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Discord webhook URL (optional - for receiving notifications in Discord)

## Setup

1. **Clone or navigate to this directory**

2. **Create your `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env and configure your settings
   # At minimum, you must set GEMINI_API_KEY
   # All other settings have sensible defaults
   ```
   
   Example `.env`:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   POSTAL_CODE=L6E1T8
   NUM_PEOPLE=2
   NUM_MEALS=7
   CUISINE=Chinese
   HEADLESS=true
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
   ```

3. **Choose your approach:**

### Option A: Using Docker (Recommended)

```bash
# Build the Docker image
docker compose build

# Run the application
docker compose up
```

### Option B: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure you have Chrome installed
# On Ubuntu/Debian:
# sudo apt-get install google-chrome-stable

# Run the application
python src/main.py
```

## Configuration

All configuration is done via the `.env` file:

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `POSTAL_CODE`: Your postal code for store location (default: "L6E1T8")
- `NUM_PEOPLE`: Number of people to cook for (default: 2)
- `NUM_MEALS`: Number of meals to plan (default: 7)
- `CUISINE`: Cuisine preference, e.g., Chinese, Italian, Mexican (default: "Chinese")
- `HEADLESS`: Run browser in headless mode - `true` or `false` (default: true)
  - Note: Headless mode is required when running in Docker
  - Set to `false` only when running locally to see the browser
- `DISCORD_WEBHOOK_URL`: Discord webhook URL for notifications (optional)

### Discord Notifications (Optional)

To receive automatic recommendations in Discord:
1. Create a webhook in your Discord server:
   - Go to Server Settings → Integrations → Webhooks
   - Click "New Webhook" and configure it
   - Copy the webhook URL
2. Add the webhook URL to your `.env` file:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
   ```
3. The application will automatically post the meal plan and flyer image to your Discord channel after generating recommendations

## Output

The application generates:
- `data/flyer_page_*.jpg`: Individual flyer pages downloaded (extra_large images from Flipp)
- `output/complete_flyer.jpg`: All flyer pages stitched together in a grid layout
- `output/recommendations.txt`: Gemini AI's meal recommendations and shopping list based on the flyer

## How It Works

1. **Postal Code Setup**: Uses Selenium to navigate to Flipp.com and set your postal code
2. **Flyer Download**: 
   - Navigates to `https://flipp.com/search/No%20Frills`
   - Extracts all image URLs containing `extra_large` in the filename
   - Downloads up to 20 images concurrently for faster performance
3. **Image Stitching**: 
   - Arranges downloaded flyer pages into a grid layout
   - Calculates optimal rows/columns to create a somewhat square image
   - Centers each image in its grid cell
4. **AI Analysis**: Sends the complete flyer image to Google Gemini with a custom prompt asking for:
   - Shopping list of items on sale from the flyer
   - 7 Chinese meal recipes using those ingredients
   - Budget estimate based on visible prices
   - Money-saving tips and substitutions

## Features

- **Fast Concurrent Downloads**: Downloads up to 20 images simultaneously for faster performance
- **Smart Image Selection**: Automatically filters for high-quality `extra_large` flyer images
- **Grid Layout**: Stitches images into a compact grid arrangement instead of a long vertical strip
- **AI-Powered Recommendations**: Uses Google Gemini's vision capabilities to analyze actual flyer images
- **Discord Integration**: Automatically posts meal plans and flyer images to Discord via webhook (optional)
  - Handles long messages by splitting into multiple chunks
  - Uploads the complete flyer image as an attachment for reference
- **Containerized**: Runs in Docker with all dependencies included
- **Environment Configuration**: Easy setup via `.env` file for API keys and webhook URLs

## Troubleshooting

- **"GEMINI_API_KEY not found"**: Make sure you created a `.env` file with your API key
- **Selenium errors**: Try setting `HEADLESS=False` in main.py to see what's happening
- **No flyer images found**: 
  - The website structure may have changed
  - Script looks for images with `extra_large` in the filename
  - Check `data/page_debug.html` if generated for debugging
- **Docker issues**: Make sure Docker has enough memory (2GB shm_size is set in docker-compose.yml)
- **Slow downloads**: Already optimized with 20 concurrent downloads, but you can adjust in `flyer_downloader.py`

## License

MIT
