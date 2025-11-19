# 🍽️ No Frills Cooking Recommendations

An intelligent meal planning system that analyzes weekly grocery flyers and generates personalized cooking recommendations using AI.

## ✨ What It Does

1. **Fetches the Latest Flyer** - Automatically downloads No Frills weekly flyer from Flipp.com
2. **Analyzes Deals** - Uses Google Gemini AI to identify items on sale
3. **Plans Your Meals** - Creates a complete meal plan based on your preferences and the flyer
4. **Generates Shopping List** - Provides a comprehensive shopping list with prices
5. **Sends to Discord** - Optionally shares your meal plan to Discord

## 🎨 Web Interface

This application features a **beautiful, modern web interface** with:
- 🎯 Interactive configuration (postal code, cuisine, number of meals, etc.)
- 📊 Real-time progress tracking with detailed status updates
- 🖼️ Visual flyer preview
- 💬 One-click Discord integration
- 📱 Fully responsive design (works on mobile, tablet, and desktop)

## 📋 Prerequisites

### Required
- **Docker & Docker Compose** (recommended) OR **Python 3.12+** with Chrome/Chromium
- **Google Gemini API key** - [Get one free here](https://makersuite.google.com/app/apikey)

### Optional
- **Discord webhook URL** - For automatic meal plan notifications

## 🚀 Quick Start

### 1. Get Your API Key
Sign up for a free Google Gemini API key at [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Configure Environment
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key (required)
# Other settings are optional with sensible defaults
```

**Minimum `.env` configuration:**
```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Full `.env` options:**
```env
GEMINI_API_KEY=your_actual_api_key_here
POSTAL_CODE=L6E1T8                    # Your postal code
NUM_PEOPLE=2                          # Number of people to cook for
NUM_MEALS=7                           # Number of meals to plan
CUISINE=Chinese                       # Cuisine preference
HEADLESS=true                         # Run browser in background
DISCORD_WEBHOOK_URL=https://...       # Optional Discord webhook
```

### 3. Start the Application

**Option A: Docker (Recommended)**
```bash
docker compose up
```

**Option B: Local Python**
```bash
pip install -r requirements.txt
python src/api.py
```

### 4. Open Your Browser
Navigate to **http://localhost:8000** and enjoy the web interface!

---

## 💻 Usage

### Web Interface (Primary Method)

1. **Open** http://localhost:8000 in your browser
2. **Configure** your preferences (or use the defaults from `.env`)
   - Postal code
   - Number of people
   - Number of meals
   - Cuisine preference
   - Headless mode (recommended: on)
3. **Click** "Generate Recommendations"
4. **Wait** 2-3 minutes while the app:
   - Sets up browser and postal code
   - Downloads flyer images
   - Stitches images together
   - Analyzes with Gemini AI
   - Generates your meal plan
5. **View** your personalized meal plan and shopping list
6. **Optional**: Click "Send to Discord" to share

### Command Line (Alternative)

If you prefer CLI:
```bash
python src/main.py
```

Results are saved to:
- `output/complete_flyer.jpg` - Stitched flyer image
- `output/recommendations.txt` - Your meal plan

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | - | ✅ Yes |
| `POSTAL_CODE` | Your postal code for store location | `L6E1T8` | ❌ No |
| `NUM_PEOPLE` | Number of people to cook for | `2` | ❌ No |
| `NUM_MEALS` | Number of meals to plan | `7` | ❌ No |
| `CUISINE` | Cuisine preference (Chinese, Italian, Mexican, etc.) | `Chinese` | ❌ No |
| `HEADLESS` | Run browser in headless mode (`true`/`false`) | `true` | ❌ No |
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | - | ❌ No |

**Note:** When using the web interface, you can override any of these settings (except `GEMINI_API_KEY`) directly in the UI.

### Discord Integration (Optional)

To get meal plans delivered to Discord:

1. **Create a webhook** in your Discord server:
   - Server Settings → Integrations → Webhooks
   - Click "New Webhook"
   - Copy the webhook URL

2. **Use it in the web interface:**
   - Click "Send to Discord" button after generating recommendations
   - Enter your webhook URL
   - Click Send

3. **Or add to `.env`** for auto-fill:
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
   ```

## 📂 Output Files

The application creates the following files:

```
data/
├── flyer_page_01.jpg          # Individual flyer pages
├── flyer_page_02.jpg          # (high-quality downloads)
└── ...

output/
├── complete_flyer.jpg         # All pages stitched together
└── recommendations.txt        # Your meal plan & shopping list
```

**In the web interface**, you can view both the flyer and recommendations directly in your browser.

## 🔧 How It Works

### Behind the Scenes

1. **📍 Postal Code Setup**
   - Launches a headless Chrome browser
   - Navigates to Flipp.com
   - Sets your postal code to find local stores

2. **📥 Flyer Download**
   - Finds No Frills weekly flyer
   - Extracts high-quality `extra_large` image URLs
   - Downloads up to 20 images concurrently (fast!)

3. **🖼️ Image Stitching**
   - Arranges all flyer pages into a grid layout
   - Calculates optimal rows/columns for readability
   - Creates one comprehensive flyer image

4. **🤖 AI Analysis (Gemini)**
   - Uploads the complete flyer to Google Gemini
   - Analyzes items on sale with prices
   - Generates meal plan based on your preferences
   - Creates shopping list with all ingredients
   - Provides cooking instructions for each meal

5. **✅ Results**
   - Displays in the web interface
   - Saves to `output/` directory
   - Optionally sends to Discord

## ✨ Features

### Web Interface
- 🎨 **Beautiful UI** - Modern purple gradient theme with smooth animations
- 📊 **Real-time Progress** - See exactly what's happening at each step
- 📱 **Responsive Design** - Works perfectly on mobile, tablet, and desktop
- ⚙️ **Easy Configuration** - Override any setting directly in the UI
- 🖼️ **Visual Preview** - View the flyer and recommendations side-by-side

### Functionality
- ⚡ **Fast Downloads** - Concurrent downloads (up to 20 images at once)
- 🎯 **Smart Filtering** - Automatically selects high-quality flyer images
- 📐 **Grid Layout** - Stitches pages into an organized grid
- 🤖 **AI-Powered** - Google Gemini analyzes actual flyer images
- 💬 **Discord Ready** - One-click sharing to Discord channels
- 🐳 **Dockerized** - All dependencies included, no setup hassle

### Intelligence
- 🛒 **Price-Aware** - Identifies sale prices from flyer
- 🍽️ **Cuisine-Specific** - Generates authentic recipes for your preference
- 📝 **Complete Planning** - Meal names, ingredients, instructions, and shopping list
- 💰 **Budget-Friendly** - Focuses on items currently on sale

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"GEMINI_API_KEY not found"** | Create a `.env` file with your API key |
| **Port 8000 already in use** | Stop other services using port 8000 or change port in `docker-compose.yml` |
| **Browser/Selenium errors** | Make sure Chrome is installed; try setting `HEADLESS=false` to debug |
| **No flyer images found** | Flipp.com structure may have changed; check logs for details |
| **Docker memory issues** | Increase Docker memory limit (2GB+ recommended) |
| **Slow processing** | This is normal! Takes 2-3 minutes. Watch the status messages |

### Getting Help

1. **Check the logs** - Look at terminal output for error messages
2. **View debug files** - Check `data/` folder for downloaded images
3. **Test API key** - Verify your Gemini API key is valid
4. **Browser mode** - Set `HEADLESS=false` to see what the browser is doing

### Docker Commands

```bash
# View logs
docker compose logs -f

# Restart the container
docker compose restart

# Rebuild from scratch
docker compose down
docker compose up --build

# Stop everything
docker compose down
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │ ← You interact here
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  FastAPI Server │ ← Web interface & API
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│Selenium │ │ Gemini   │
│ Chrome  │ │ AI API   │
└─────────┘ └──────────┘
```

### Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Browser Automation**: Selenium with Chrome
- **AI**: Google Gemini 2.5 Flash
- **Container**: Docker with Docker Compose

## 📄 Project Structure

```
cooking-recommendations/
├── src/
│   ├── api.py                 # FastAPI web server
│   ├── main.py                # CLI entry point
│   ├── store_selector.py      # Selenium automation
│   ├── flyer_downloader.py    # Image downloading
│   ├── image_stitcher.py      # Image processing
│   ├── gemini_recommender.py  # AI analysis
│   └── discord_notifier.py    # Discord integration
├── static/
│   ├── index.html             # Web UI
│   ├── style.css              # Styling
│   └── script.js              # Frontend logic
├── data/                      # Downloaded flyers
├── output/                    # Generated results
├── docker-compose.yml         # Docker configuration
├── Dockerfile                 # Container definition
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## 📝 License

MIT License - feel free to use this project however you like!
