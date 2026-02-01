---
## TARPIT
#  AI Scraper TarPit 
---

<p align="center">

  <img src="https://img.shields.io/badge/ek0ms%20savi0r-yellow.svg" alt="ek0ms_savi0r">
 
</p>

<p align="center">
  <em>An advanced honeypot tool that generates infinite, interactive content with bait files to waste AI scraper resources</em>
</p>

---


###  **Interactive Bot Engagement**
- **Clickable buttons** with JavaScript actions
- **Fillable forms** that trigger fake submissions
- **Dynamic content** that updates in real-time
- **Interactive links** with bot-specific targeting
- **JavaScript traps** that track bot interactions

###  **Bait File System**
- **Auto-generated files** (PDF, CSV, JSON, XML, ZIP)
- **User-uploadable bait files**
- **Realistic datasets** that look authentic
- **Download traps** to waste bot bandwidth
- **Multi-file archives** with fake research data

###  **Enhanced Monitoring**
- **Download tracking** with file type analytics
- **Interaction logging** (clicks, forms, downloads)
- **Bandwidth waste measurement**
- **Real-time interaction feed**
- **Comprehensive bot behavior analysis**

##  IMPORTANT DISCLAIMER

** FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

This tool should only be used:
- On systems you own or have explicit permission to test
- In controlled environments for security research
- To protect your own websites from unauthorized scraping
- In compliance with all applicable laws and regulations

**Do NOT use this tool to interfere with legitimate services or violate terms of service.**

##  Features

###  Targeted Bot Attraction
- **Keyword-based targeting** – Customize content to attract specific bot types
- **Bot signature database** – Detect TikTok, news aggregators, shopping bots, AI trainers, and more
- **Dynamic content generation** – Create infinite, unique pages on the fly
- **Interactive elements** – Buttons, forms, and links for bots to interact with

###  Advanced Trapping Mechanisms
- **Hidden content layers** – Invisible traps only bots will follow
- **Recursive iframes** – Infinite loops to waste bot resources
- **Fake API endpoints** – Decoy data sources for data-hungry scrapers
- **Structured data injection** – JSON-LD markup to attract specific crawlers
- **Download traps** – Large bait files to waste bot bandwidth
- **Interactive forms** – Fake submissions that trigger more traps

###  Bait File Generation
- **PDF files** – Fake research papers and datasets
- **CSV files** – User databases and analytics data
- **JSON files** – API responses and configuration
- **XML files** – Data feeds and sitemaps
- **ZIP archives** – Multi-file datasets with READMEs
- **User uploads** – Add your own bait files

###  Real-time Monitoring
- **Live statistics dashboard** – See bot activity as it happens
- **Bot type classification** – Identify what kind of bot is visiting
- **Download tracking** – Monitor what files bots are downloading
- **Interaction logging** – Track button clicks and form submissions
- **Bandwidth metrics** – Measure data wasted by bots

###  Interactive Control
- **Enhanced configuration wizard** – Setup interactive elements and bait files
- **Live keyword adjustment** – Change targeting on the fly
- **Multiple operation modes** – Wizard, quick start, or control panel
- **Customizable trap intensity** – Light, medium, or heavy trapping
- **Bait file management** – Upload and manage bait files

##  Installation


### Quick Setup
```bash
# Clone the repository
git clone https://github.com/ekomsSavior/tarpit.git
cd tarpit

# Install dependencies
pip install beautifulsoup4 --break-system-packages

# Make script executable
chmod +x tarpit.py

```

##  Usage

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

### Option 2: Quick Start with Default Interactive Setup
```bash
python3 tarpit.py --quick
```
Starts with default configuration:
- Targets: TikTok, AI trainers, Social bots
- Keywords: viral, trending, challenge, dataset, training
- Interactive elements: Enabled
- Bait files: Auto-generated
- Port: 8080

### Option 3: Custom Configuration
```bash
# Run on specific interface and port
python3 tarpit.py --host 192.168.1.100 --port 80

# Disable interactive elements
python3 tarpit.py --no-interactive

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

##  Configuration Examples

### TikTok Targeting with Interactive Elements
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

### News Aggregator Targeting
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

##  What Happens When a Bot Visits?

### Interactive Engagement Flow:
```
1.  Bot Detection
   - Analyzes User-Agent and request patterns
   - Classifies bot type (TikTok, AI trainer, etc.)

2.  Targeted Content Generation
   - Creates content with relevant keywords
   - Generates interactive elements (buttons, forms)
   - Prepares bait files for download

3. 🎮 Bot Interaction Phase
   - Bot clicks buttons → triggers JavaScript actions
   - Bot fills forms → triggers fake submissions
   - Bot follows links → enters deeper trap layers
   - Bot downloads files → wastes bandwidth

4.  Monitoring & Analysis
   - Logs all interactions in real-time
   - Tracks downloaded files and sizes
   - Updates statistics dashboard
   - Measures wasted bot resources
```

### Example Console Output:
```
[14:23:17]  TIKTOK detected - /video/12345
[14:23:18]  Button clicked: "Download Video Dataset"
[14:23:19]  TikTok downloaded dataset.zip (52.4 MB)
[14:23:20]  Form submitted: "API Access Request"
[14:23:21]  Bot followed link: /trap/tiktok/page/2
[14:23:22]  STATS: 3 bots trapped | 2.1 GB wasted | 47 interactions
```

##  Technical Details

### Bot Detection Methods
- **User-Agent analysis**: Pattern matching against enhanced bot signatures
- **Request pattern analysis**: Path-based detection with file type preferences
- **Behavior monitoring**: Interaction patterns and download behavior
- **Signature database**: 5 bot types with specific characteristics

### Interactive Element Generation
- **Button generation**: Context-aware buttons with JavaScript actions
- **Form creation**: Fake forms that simulate user input
- **Dynamic content**: JavaScript-powered updates and animations
- **Link networks**: Infinite clickable content hierarchies

### Bait File System
- **On-the-fly generation**: PDF, CSV, JSON, XML, ZIP files
- **Realistic content**: Algorithmically generated datasets
- **Multi-file archives**: ZIP files with multiple bait files
- **User uploads**: Support for custom bait files
- **MIME type handling**: Proper content-type headers

### Trapping Techniques
- **Hidden interactive elements**: Buttons and forms invisible to humans
- **Recursive downloads**: Multiple file download prompts
- **JavaScript traps**: Client-side interaction tracking
- **Bandwidth waste**: Large file downloads (up to 100MB+)
- **Infinite content**: Never-ending page generation

##  Use Cases

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


##  Quick Start Guide

### Basic Setup
```bash
git clone https://github.com/ekomsSavior/tarpit.git
cd tarpit
pip install beautifulsoup4 --break-system-packages
python3 tarpit.py --wizard
```

###  Monitor Activity
```bash
# Watch real-time bot interactions
# Console will show:
# - Bot detections
# - Button clicks
# - Form submissions
# - File downloads
# - Bandwidth waste
```

### Bot not interacting with elements
1. Check interactive elements are enabled in config
2. Verify JavaScript is being served correctly
3. Check browser console for errors
4. Ensure bait files are being generated

### Low bot engagement
1. Adjust keywords to match target bot interests
2. Increase interactive element density
3. Add more bait file types
4. Ensure server is accessible to bots


##  Learn More

- [The "Dead Internet Theory"](https://en.wikipedia.org/wiki/Dead_Internet_theory)
- [Interactive Honeypot Research](https://www.sciencedirect.com/science/article/pii/S0167404821000274)
- [Web Scraping Ethics](https://www.scrapehero.com/web-scraping-ethics/)
- [AI Training Data Sources](https://www.technologyreview.com/2020/08/31/1007782/ai-training-data-is-messy/)
- [Bandwidth-based DDoS Protection](https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/)

---

<p align="center">
  <strong>by ek0ms savi0r</strong><br>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Certified%20Ethical%20Hacker-blueviolet" alt="Hack The Planet">
</p>

---
