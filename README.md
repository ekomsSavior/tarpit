<p align="center">
<img width="580" height="193" alt="IMG_2975(1)" src="https://github.com/user-attachments/assets/5612cf9c-0e97-4dbe-942d-c2e8569f4096" />
</p>

<p align="center">
  <em>AI SCRAPER TARPIT</em>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/ek0ms%20savi0r-black.svg" alt="ek0ms_savi0r">
</p>

<p align="center">
  <em>An advanced honeypot tool that generates infinite, interactive content with bait files to waste AI scraper resources</em>
</p>

---

### Infinite Traps
- Meta refresh loops – bots never leave the first page
- Infinite loading pages – progress bars that never reach 100%
- WebSocket mock endpoints – waste connection time
- Recursive iframes and redirect chains
- Session-based content locks – duplicate content with new URLs

### Dark Mode Web UI
- Real‑time statistics 
- Bot activity by type, download tracking, bandwidth waste
- Status, upload, test, and ngrok info pages all styled

### Adaptive Bait Generation
- Tracks bot preferences (CSV, JSON, ZIP, etc.)
- Serves larger files of the type the bot downloads most
- SQLite database dumps (up to 2 GB) for realistic training data

### Enhanced API Traps
- Fake JWT token endpoint with refresh URL
- Paginated API endpoints that never end (`/api/v1/data?page=1` → page 2 → … → page 1000 → back to 1)
- JSON‑LD structured data with hundreds of fake dataset download links

### Sitemap & Robots.txt
- Auto‑generated `sitemap.xml` with 5000+ fake dataset URLs
- `robots.txt` allows all bots and points to the sitemap
- Attracts search engine crawlers (Googlebot, Bingbot) which feed AI training data

### Interactive Bot Engagement
- Clickable buttons with JavaScript actions
- Fillable forms that trigger fake submissions
- Dynamic content that updates in real‑time
- Interactive links with bot‑specific targeting
- JavaScript traps that track bot interactions

### Bait File System
- Auto‑generated files (PDF, CSV, JSON, XML, ZIP, SQLite)
- User‑uploadable bait files
- Realistic datasets that look authentic
- Download traps to waste bot bandwidth
- Multi‑file archives with fake research data

### ngrok Public Access
- Public tunneling for remote bot access
- Automatic public URL generation
- Tunnel health monitoring and auto‑recovery
- Public and local access simultaneously
- Real‑time tunnel status dashboard

### Enhanced Monitoring
- Download tracking with file type analytics
- Interaction logging (clicks, forms, downloads)
- Bandwidth waste measurement
- Real‑time interaction feed
- Comprehensive bot behavior analysis

---

## IMPORTANT DISCLAIMER

**FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

This tool should only be used:
- On systems you own or have explicit permission to test
- In controlled environments for security research
- To protect your own websites from unauthorized scraping
- In compliance with all applicable laws and regulations

**Do NOT use this tool to interfere with legitimate services or violate terms of service.**

---

<img width="586" height="676" alt="IMG_2975" src="https://github.com/user-attachments/assets/855f54c5-0dc2-4f0c-a9b7-e32cfc864b36" />
# Features


### Targeted Bot Attraction
- Keyword‑based targeting – Customize content to attract specific bot types
- Bot signature database – Detect TikTok, news aggregators, shopping bots, AI trainers, and more
- Dynamic content generation – Create infinite, unique pages on the fly
- Interactive elements – Buttons, forms, and links for bots to interact with

### Advanced Trapping Mechanisms
- Hidden content layers – Invisible traps only bots will follow
- Recursive iframes – Infinite loops to waste bot resources
- Fake API endpoints – Decoy data sources for data‑hungry scrapers
- Structured data injection – JSON‑LD markup to attract specific crawlers
- Download traps – Large bait files (up to 2 GB) to waste bot bandwidth
- Interactive forms – Fake submissions that trigger more traps
- **Meta refresh loops** – Instant redirects to new trap pages
- **Infinite loading page** – `/data/stream` with a progress bar that never finishes
- **WebSocket mock** – Returns `426 Upgrade Required` to waste connection attempts

### ngrok Integration
- Public URL generation – Access your tar pit from anywhere
- Automatic tunnel setup – One‑command public access
- Tunnel monitoring – Automatic restart if tunnel drops
- Dashboard access – View ngrok metrics and logs
- Region selection – Choose tunnel location (US, EU, etc.)

### Bait File Generation
- PDF files – Fake research papers and datasets
- CSV files – User databases and analytics data
- JSON files – API responses and configuration
- XML files – Data feeds and sitemaps
- ZIP archives – Multi‑file datasets with READMEs
- **SQLite databases** – Realistic 500 MB – 2 GB database dumps
- User uploads – Add your own bait files

### Real‑time Monitoring
- **Dark mode hacker dashboard** – Green/black terminal style
- Live statistics – See bot activity as it happens
- Bot type classification – Identify what kind of bot is visiting
- Download tracking – Monitor what files bots are downloading
- Interaction logging – Track button clicks and form submissions
- Bandwidth metrics – Measure data wasted by bots

### Adaptive & Infinite Traps
- **Preference learning** – Tracks which file types each bot downloads, then serves more of that type
- **Session‑based duplicate URLs** – After 50 pages, serve the same content under new URLs
- **Fake token API** – Returns a JWT that expires and points to a refresh endpoint
- **Paginated API** – `/api/v1/data?page=1` leads to page 2, 3, … 1000, then loops
- **Sitemap.xml** – 5000+ fake dataset URLs to attract crawlers
- **Robots.txt** – Allows all bots, includes sitemap directive

### Interactive Control
- Enhanced configuration wizard – Setup interactive elements and bait files
- Live keyword adjustment – Change targeting on the fly
- Multiple operation modes – Wizard, quick start, or control panel
- Customizable trap intensity – Light, medium, or heavy trapping
- Bait file management – Upload and manage bait files

---

## Installation

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/ekomsSavior/tarpit.git
cd tarpit

# Install dependencies
pip install beautifulsoup4 requests --break-system-packages

# Make script executable
chmod +x tarpit.py
```

### Install ngrok
```bash
# Download and install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Set up authentication
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
```

---

## Usage

### Option 1: Enhanced Configuration Wizard (Recommended)
```bash
python3 tarpit.py --wizard
```
The enhanced wizard will guide you through:
- Selecting which bot types to target
- Choosing keywords to attract those bots
- Configuring interactive elements (buttons, forms, JavaScript)
- Setting up bait file generation and downloads
- Choosing trap intensity level

### Option 2: Quick Start with Public Access
```bash
# Start with default config and ngrok tunnel
python3 tarpit.py --quick --ngrok

# Or with your own ngrok token
python3 tarpit.py --quick --ngrok --ngrok-token YOUR_TOKEN
```

### Option 3: Custom Configuration with ngrok
```bash
# Run on specific port with public access
python3 tarpit.py --host 0.0.0.0 --port 8080 --ngrok

# Disable interactive elements but enable public access
python3 tarpit.py --no-interactive --ngrok

# Test bait file generation
python3 tarpit.py --test
```

### Option 4: Upload Your Own Bait Files
```bash
# Access upload interface at:
http://your-server:8080/upload/

# Or manually place files in:
tarpit/bait_files/uploaded/
```

### Using the Public URL
When ngrok is enabled:
1. **Local access**: http://localhost:8080
2. **Public access**: https://your-random-subdomain.ngrok.io
3. **Dashboard**: http://localhost:4040 (ngrok metrics)

### See what the bots see:
```bash
curl -s -A "GPTBot" http://localhost:8080/ | head -200
```

### Tunnel Management
- **Automatic monitoring**: Tunnel health is checked every 60 seconds
- **Auto‑restart**: If tunnel drops, it automatically restarts
- **Public URL persistence**: URL remains stable across restarts
- **Multiple regions**: Choose US, EU, AP, AU, SA, JP, IN

---

## Configuration Examples

### TikTok Targeting with Public Access
```json
{
  "keywords": ["viral", "trending", "challenge", "dance", "music", "tiktok"],
  "bot_types": ["tiktok", "social"],
  "content_themes": ["viral", "entertainment"],
  "interactive_elements": true,
  "bait_files_enabled": true,
  "download_traps": true,
  "recursion_depth": 5
}
```

### AI Trainer Targeting with Download Traps
```json
{
  "keywords": ["dataset", "training", "machine learning", "AI", "model"],
  "bot_types": ["ai_trainer", "academic"],
  "content_themes": ["technical"],
  "interactive_elements": true,
  "bait_files_enabled": true,
  "download_traps": true,
  "recursion_depth": 10
}
```

### News Aggregator Targeting with ngrok
```json
{
  "keywords": ["breaking", "exclusive", "report", "analysis", "news"],
  "bot_types": ["news"],
  "content_themes": ["news"],
  "interactive_elements": true,
  "bait_files_enabled": true,
  "download_traps": true,
  "recursion_depth": 3
}
```

---

## What Happens When a Bot Visits?

### Interactive Engagement Flow:
```
1. Bot Detection
   - Analyzes User-Agent and request patterns
   - Classifies bot type (TikTok, AI trainer, etc.)

2. Targeted Content Generation
   - Creates content with relevant keywords
   - Generates interactive elements (buttons, forms)
   - Prepares bait files for download

3. Bot Interaction Phase
   - Bot clicks buttons -> triggers JavaScript actions
   - Bot fills forms -> triggers fake submissions
   - Bot follows links -> enters deeper trap layers
   - Bot downloads files -> wastes bandwidth
   - Meta refresh sends bot into redirect loop
   - WebSocket mock wastes connection time

4. Adaptive Trapping
   - System learns bot's preferred file types
   - Serves larger files of those types
   - Generates new duplicate URLs after threshold

5. Monitoring & Analysis
   - Logs all interactions in real-time
   - Tracks downloaded files and sizes
   - Updates dark mode dashboard
   - Measures wasted bot resources
```

### Example Console Output with ngrok:
```
====================================================================
INITIALIZING NGrok TUNNEL
====================================================================
ngrok version 3.37.3 detected
ngrok auth token configured successfully
Starting ngrok tunnel on port 8080...
Waiting for ngrok to initialize (10 seconds)...

ngrok tunnel established!
Public URL: https://a1b2c3d4.ngrok-free.dev
ngrok dashboard: http://localhost:4040

====================================================================
INTERACTIVE AI SCRAPER TAR PIT
====================================================================
Local URL: http://0.0.0.0:8080
Public URL: https://a1b2c3d4.ngrok-free.dev
Targeting: ai_trainer
Keywords: dataset, training, machine learning, AI, model...
Bait files: 4 available
Interactive: Enabled
Status: http://0.0.0.0:8080/status
Test: http://0.0.0.0:8080/test

Monitoring active. Bot interactions will appear below:
====================================================================
[14:23:17] AI_TRAINER detected - / - IP: 203.0.113.45
[14:23:18] AI_TRAINER downloading training_dataset_1.zip (211.6 MB)
[14:23:20] AI_TRAINER detected - /data/stream - IP: 203.0.113.45
[14:23:21] AI_TRAINER downloading live_dataset.json (87.3 MB)
[14:23:22] STATS: 1 bots trapped | 298.9 MB wasted | 12 interactions
```

---

## Technical Details

### Bot Detection Methods
- User-Agent analysis: Pattern matching against enhanced bot signatures
- Request pattern analysis: Path‑based detection with file type preferences
- Behavior monitoring: Interaction patterns and download behavior
- Signature database: 10+ bot types with specific characteristics

### Interactive Element Generation
- Button generation: Context‑aware buttons with JavaScript actions
- Form creation: Fake forms that simulate user input
- Dynamic content: JavaScript‑powered updates and animations
- Link networks: Infinite clickable content hierarchies

### ngrok Integration Features
- Automatic tunnel management: Setup, monitoring, and recovery
- Public URL discovery: Multiple methods to find active tunnel URL
- Health checking: Regular tunnel status verification
- Configuration management: Auth token and region settings
- Process management: Clean startup and shutdown

### Bait File System
- On‑the‑fly generation: PDF, CSV, JSON, XML, ZIP, SQLite
- Realistic content: Algorithmically generated datasets
- Multi‑file archives: ZIP files with multiple bait files
- User uploads: Support for custom bait files
- MIME type handling: Proper content‑type headers

### Trapping Techniques
- Hidden interactive elements: Buttons and forms invisible to humans
- Recursive downloads: Multiple file download prompts
- JavaScript traps: Client‑side interaction tracking
- Bandwidth waste: Large file downloads (up to 2 GB)
- Infinite content: Never‑ending page generation
- **Meta refresh loops**: Instant redirects to new trap URLs
- **Infinite loading page**: Chunked response that never completes
- **WebSocket mock**: Upgrade required response
- **Adaptive bait**: Serves more of what the bot downloads
- **Sitemap injection**: 5000+ fake URLs for crawlers

### New in v2.0 (Infinite Trap Edition)
- **SQLite database generation** – Realistic 500 MB – 2 GB database dumps
- **Fake JWT token endpoint** – Returns token with refresh URL
- **Paginated API** – `/api/v1/data?page=1` leads to infinite pages
- **Meta refresh loops** – Instant redirect traps
- **Infinite loading page** – Never‑finishing progress bar
- **WebSocket mock** – Wastes connection time
- **Adaptive download preferences** – Tracks bot file type choices
- **Session‑based duplicate URLs** – New content after depth threshold
- **Sitemap.xml and robots.txt** – Attracts search engine crawlers

---


## Quick Start Guide

### Basic Setup with ngrok
```bash
git clone https://github.com/ekomsSavior/tarpit.git
cd tarpit
pip install beautifulsoup4 requests --break-system-packages

# Get ngrok token from https://ngrok.com
# Save it in ngrok_config.json or configure globally

python3 tarpit.py --quick --ngrok
```

### Monitor Activity
```bash
# Watch real-time bot interactions
# Console will show:
# - Public URL when ngrok starts
# - Bot detections (local and remote)
# - Button clicks and form submissions
# - File downloads and sizes
# - Bandwidth waste totals
```

### Access Management Interfaces 
```bash
# Local status dashboard 
http://localhost:8080/status

# ngrok information page 
http://localhost:8080/ngrok

# ngrok metrics dashboard
http://localhost:4040

# Test page for debugging
http://localhost:8080/test

# Upload bait files 
http://localhost:8080/upload/
```

---

## Troubleshooting

### ngrok Issues
1. **ngrok not starting**
   - Check ngrok is installed: `ngrok --version`
   - Verify auth token: Check ngrok_config.json
   - Ensure no firewall blocking ngrok
   - Try manual start: `ngrok http 8080`

2. **No public URL generated**
   - Wait 10‑15 seconds for tunnel initialization
   - Check ngrok dashboard at http://localhost:4040
   - Verify internet connectivity
   - Check ngrok service status at status.ngrok.com

3. **Tunnel drops frequently**
   - Check network stability
   - Consider different region: `--region eu`
   - Monitor ngrok logs at http://localhost:4040
   - Ensure sufficient system resources

### Bot Detection Issues
1. **Bots not being detected**
   - Check bot signatures in ConfigManager class
   - Verify User‑Agent patterns
   - Test with known bot User‑Agents
   - Check detection logic in `detect_bot_type()`

2. **False positives**
   - Review detection thresholds
   - Adjust pattern matching sensitivity
   - Update bot signature database
   - Check request path patterns

### Interactive Elements Issues
1. **Bot not interacting with elements**
   - Check interactive elements are enabled in config
   - Verify JavaScript is being served correctly
   - Check browser console for errors
   - Ensure bait files are being generated

2. **Low bot engagement**
   - Adjust keywords to match target bot interests
   - Increase interactive element density
   - Add more bait file types
   - Ensure server is accessible to bots (check ngrok URL)

### Performance Issues
1. **High memory usage**
   - Reduce recursion depth in config
   - Limit bait file sizes
   - Decrease interactive element count
   - Monitor with system tools

2. **Slow response times**
   - Check system resource usage
   - Reduce content generation complexity
   - Optimize file serving
   - Consider hardware limitations

### No Bots Visiting?
- **This is normal for a new honeypot** – bots must discover your URL
- Submit your sitemap to Google and Bing:
  ```
  https://www.google.com/ping?sitemap=https://your-url.ngrok-free.dev/sitemap.xml
  https://www.bing.com/ping?sitemap=https://your-url.ngrok-free.dev/sitemap.xml
  ```
- Share your public URL on forums, GitHub, or social media
- Use the bot simulation buttons on the `/test` page to leave traces
- Leave the tarpit running for 24–48 hours – real AI scrapers operate on schedules

---

## Learn More

- [The "Dead Internet Theory"](https://en.wikipedia.org/wiki/Dead_Internet_theory)
- [Interactive Honeypot Research](https://www.sciencedirect.com/science/article/pii/S0167404821000274)
- [Web Scraping Ethics](https://www.scrapehero.com/web-scraping-ethics/)
- [AI Training Data Sources](https://www.technologyreview.com/2020/08/31/1007782/ai-training-data-is-messy/)
- [Bandwidth‑based DDoS Protection](https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/)
- [ngrok Documentation](https://ngrok.com/docs)

---
<p align="center">
<img width="580" height="193" alt="IMG_2975(1)" src="https://github.com/user-attachments/assets/5612cf9c-0e97-4dbe-942d-c2e8569f4096" />
</p>

<p align="center">
  <strong>by ek0mssavi0r.dev</strong><br>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/HACK%20THE%20PLANET-black" alt="Hack The Planet">
</p>
