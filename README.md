## TARPIT
# AI Scraper TarPit 
---

<p align="center">

  <img src="https://img.shields.io/badge/ek0ms%20savi0r-yellow.svg" alt="ek0ms_savi0r">
 
</p>

<p align="center">
  <em>An advanced honeypot tool that generates infinite, interactive content with bait files to waste AI scraper resources</em>
</p>

---

## Key Features

### Interactive Bot Engagement
- Clickable buttons with JavaScript actions
- Fillable forms that trigger fake submissions
- Dynamic content that updates in real-time
- Interactive links with bot-specific targeting
- JavaScript traps that track bot interactions

### Bait File System
- Auto-generated files (PDF, CSV, JSON, XML, ZIP)
- User-uploadable bait files
- Realistic datasets that look authentic
- Download traps to waste bot bandwidth
- Multi-file archives with fake research data

### ngrok Public Access
- Public tunneling for remote bot access
- Automatic public URL generation
- Tunnel health monitoring and auto-recovery
- Public and local access simultaneously
- Real-time tunnel status dashboard

### Enhanced Monitoring
- Download tracking with file type analytics
- Interaction logging (clicks, forms, downloads)
- Bandwidth waste measurement
- Real-time interaction feed
- Comprehensive bot behavior analysis

## IMPORTANT DISCLAIMER

**FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

This tool should only be used:
- On systems you own or have explicit permission to test
- In controlled environments for security research
- To protect your own websites from unauthorized scraping
- In compliance with all applicable laws and regulations

**Do NOT use this tool to interfere with legitimate services or violate terms of service.**

## Features

### Targeted Bot Attraction
- Keyword-based targeting – Customize content to attract specific bot types
- Bot signature database – Detect TikTok, news aggregators, shopping bots, AI trainers, and more
- Dynamic content generation – Create infinite, unique pages on the fly
- Interactive elements – Buttons, forms, and links for bots to interact with

### Advanced Trapping Mechanisms
- Hidden content layers – Invisible traps only bots will follow
- Recursive iframes – Infinite loops to waste bot resources
- Fake API endpoints – Decoy data sources for data-hungry scrapers
- Structured data injection – JSON-LD markup to attract specific crawlers
- Download traps – Large bait files to waste bot bandwidth
- Interactive forms – Fake submissions that trigger more traps

### ngrok Integration
- Public URL generation – Access your tar pit from anywhere
- Automatic tunnel setup – One-command public access
- Tunnel monitoring – Automatic restart if tunnel drops
- Dashboard access – View ngrok metrics and logs
- Region selection – Choose tunnel location (US, EU, etc.)

### Bait File Generation
- PDF files – Fake research papers and datasets
- CSV files – User databases and analytics data
- JSON files – API responses and configuration
- XML files – Data feeds and sitemaps
- ZIP archives – Multi-file datasets with READMEs
- User uploads – Add your own bait files

### Real-time Monitoring
- Live statistics dashboard – See bot activity as it happens
- Bot type classification – Identify what kind of bot is visiting
- Download tracking – Monitor what files bots are downloading
- Interaction logging – Track button clicks and form submissions
- Bandwidth metrics – Measure data wasted by bots

### Interactive Control
- Enhanced configuration wizard – Setup interactive elements and bait files
- Live keyword adjustment – Change targeting on the fly
- Multiple operation modes – Wizard, quick start, or control panel
- Customizable trap intensity – Light, medium, or heavy trapping
- Bait file management – Upload and manage bait files

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
curl -s -A "GPTBot" http://localhost:8080/ | head -200         #adjust port for your server
```

### Tunnel Management
- **Automatic monitoring**: Tunnel health is checked every 30 seconds
- **Auto-restart**: If tunnel drops, it automatically restarts
- **Public URL persistence**: URL remains stable across restarts
- **Multiple regions**: Choose US, EU, AP, AU, SA, JP, IN

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

4. Monitoring & Analysis
   - Logs all interactions in real-time
   - Tracks downloaded files and sizes
   - Updates statistics dashboard
   - Measures wasted bot resources
```

### Example Console Output with ngrok:
```
====================================================================
INITIALIZING NGrok TUNNEL
====================================================================
ngrok version 3.4.0 detected
ngrok auth token configured successfully
Starting ngrok tunnel on port 8080...
Waiting for ngrok to initialize (10 seconds)...

ngrok tunnel established!
Public URL: https://a1b2c3d4.ngrok.io
ngrok dashboard: http://localhost:4040

====================================================================
INTERACTIVE AI SCRAPER TAR PIT
====================================================================
Local URL: http://0.0.0.0:8080
Public URL: https://a1b2c3d4.ngrok.io
Targeting: tiktok, ai_trainer, social
Keywords: viral, trending, challenge, dataset, training...
Bait files: 5 available
Interactive: Enabled
Status: http://0.0.0.0:8080/status
Test: http://0.0.0.0:8080/test

Monitoring active. Bot interactions will appear below:
====================================================================
[14:23:17] TIKTOK detected - /video/12345
[14:23:18] TikTok downloaded dataset.zip (52.4 MB)
[14:23:20] AI_TRAINER detected via public URL
[14:23:21] AI trainer downloaded training_data.zip (87.3 MB)
[14:23:22] STATS: 3 bots trapped | 2.1 GB wasted | 47 interactions
```

## Technical Details

### Bot Detection Methods
- User-Agent analysis: Pattern matching against enhanced bot signatures
- Request pattern analysis: Path-based detection with file type preferences
- Behavior monitoring: Interaction patterns and download behavior
- Signature database: 5 bot types with specific characteristics

### Interactive Element Generation
- Button generation: Context-aware buttons with JavaScript actions
- Form creation: Fake forms that simulate user input
- Dynamic content: JavaScript-powered updates and animations
- Link networks: Infinite clickable content hierarchies

### ngrok Integration Features
- Automatic tunnel management: Setup, monitoring, and recovery
- Public URL discovery: Multiple methods to find active tunnel URL
- Health checking: Regular tunnel status verification
- Configuration management: Auth token and region settings
- Process management: Clean startup and shutdown

### Bait File System
- On-the-fly generation: PDF, CSV, JSON, XML, ZIP files
- Realistic content: Algorithmically generated datasets
- Multi-file archives: ZIP files with multiple bait files
- User uploads: Support for custom bait files
- MIME type handling: Proper content-type headers

### Trapping Techniques
- Hidden interactive elements: Buttons and forms invisible to humans
- Recursive downloads: Multiple file download prompts
- JavaScript traps: Client-side interaction tracking
- Bandwidth waste: Large file downloads (up to 100MB+)
- Infinite content: Never-ending page generation

## Use Cases

### Academic Research
- Study interactive bot behavior patterns
- Analyze download and interaction patterns
- Research AI training data collection methods
- Measure bandwidth waste effectiveness

### Security Testing
- Test systems against interactive scraping
- Understand bot interaction patterns
- Develop countermeasures for modern scrapers
- Analyze bot resource consumption

### Content Protection
- Protect proprietary content from being scraped
- Waste resources of unethical scrapers with interactive traps
- Generate fake interactive datasets to poison training data
- Measure effectiveness of different trap types

### Remote Testing
- Test bot interactions from different geographical locations
- Share tar pit access with research collaborators
- Monitor bots accessing via public internet
- Compare local vs public bot behavior

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
```

## Troubleshooting

### ngrok Issues
1. **ngrok not starting**
   - Check ngrok is installed: `ngrok --version`
   - Verify auth token: Check ngrok_config.json
   - Ensure no firewall blocking ngrok
   - Try manual start: `ngrok http 8080`

2. **No public URL generated**
   - Wait 10-15 seconds for tunnel initialization
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
   - Verify User-Agent patterns
   - Test with known bot User-Agents
   - Check detection logic in detect_bot_type()

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

## Learn More

- [The "Dead Internet Theory"](https://en.wikipedia.org/wiki/Dead_Internet_theory)
- [Interactive Honeypot Research](https://www.sciencedirect.com/science/article/pii/S0167404821000274)
- [Web Scraping Ethics](https://www.scrapehero.com/web-scraping-ethics/)
- [AI Training Data Sources](https://www.technologyreview.com/2020/08/31/1007782/ai-training-data-is-messy/)
- [Bandwidth-based DDoS Protection](https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/)
- [ngrok Documentation](https://ngrok.com/docs)

---

<p align="center">
  <strong>by ek0ms savi0r</strong><br>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Certified%20Ethical%20Hacker-blueviolet" alt="Hack The Planet">
</p>
