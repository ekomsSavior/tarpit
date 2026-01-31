#!/usr/bin/env python3
"""
Enhanced Web Interaction Monitor with Keyword Targeting
Educational Security Tool - For authorized research only
"""

import os
import sys
import time
import random
import hashlib
import threading
import json
import sqlite3
import argparse
import signal
import curses
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import requests
from bs4 import BeautifulSoup
from collections import Counter, deque
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

@dataclass
class BotTargetingConfig:
    """Configuration for targeting specific bots"""
    keywords: List[str]
    bot_types: List[str]  # ['tiktok', 'news', 'shopping', 'academic', 'social']
    content_themes: List[str]
    density_multiplier: float = 2.0
    recursion_depth: int = 5
    hidden_traps: bool = True
    embed_tracking: bool = True
    meta_tag_injection: bool = True

class ConfigManager:
    """Manage bot targeting configurations"""
    
    def __init__(self, config_file: str = "bot_config.json"):
        self.config_file = config_file
        self.active_config = BotTargetingConfig(
            keywords=["viral", "trending", "challenge", "dance", "music"],
            bot_types=["social"],
            content_themes=["entertainment", "lifestyle"]
        )
        self.load_config()
        
        # Bot signature database
        self.bot_signatures = {
            "tiktok": {
                "ua_patterns": ["tiktok", "bytedance", "tt_webview"],
                "interest_keywords": ["short video", "trending", "hashtag", "challenge"],
                "content_types": ["video", "music", "dance"],
                "crawl_patterns": ["/video/", "/music/", "/tag/", "/challenge/"]
            },
            "news": {
                "ua_patterns": ["googlebot-news", "bingnews", "newscrawler"],
                "interest_keywords": ["breaking", "exclusive", "report", "analysis"],
                "content_types": ["article", "news", "report"],
                "crawl_patterns": ["/news/", "/article/", "/202", "/breaking/"]
            },
            "shopping": {
                "ua_patterns": ["pricegrabber", "shoppingbot", "alibot"],
                "interest_keywords": ["discount", "sale", "price", "buy", "deal"],
                "content_types": ["product", "review", "price"],
                "crawl_patterns": ["/product/", "/shop/", "/buy/", "/price/"]
            },
            "academic": {
                "ua_patterns": ["semanticscholar", "academicbot", "research"],
                "interest_keywords": ["study", "research", "data", "analysis", "findings"],
                "content_types": ["paper", "study", "research"],
                "crawl_patterns": ["/paper/", "/study/", "/research/", "/pdf/"]
            },
            "ai_trainer": {
                "ua_patterns": ["gptbot", "claudebot", "anthropic", "cohere"],
                "interest_keywords": ["artificial intelligence", "machine learning", "dataset"],
                "content_types": ["tutorial", "explanation", "example"],
                "crawl_patterns": ["/ai/", "/ml/", "/dataset/", "/training/"]
            }
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Convert dict to BotTargetingConfig
                    if isinstance(data, dict):
                        self.active_config = BotTargetingConfig(**data)
                logger.info(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.active_config), f, indent=2)
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def detect_bot_type(self, user_agent: str, path: str) -> str:
        """Detect specific bot type from request"""
        ua_lower = user_agent.lower()
        path_lower = path.lower()
        
        for bot_type, signatures in self.bot_signatures.items():
            # Check user agent patterns
            for pattern in signatures["ua_patterns"]:
                if pattern in ua_lower:
                    return bot_type
            
            # Check path patterns
            for pattern in signatures["crawl_patterns"]:
                if pattern in path_lower:
                    return bot_type
        
        return "generic"

# ============================================================================
#  CONTENT GENERATOR 
# ============================================================================

class TargetedContentGenerator:
    """Generate content targeted to specific bot interests"""
    
    def __init__(self, config: BotTargetingConfig):
        self.config = config
        self.keyword_density = {}
        self.setup_content_templates()
        self.setup_word_banks()
    
    def setup_content_templates(self):
        """Setup content templates for different themes"""
        self.templates = {
            "viral": [
                "BREAKING: {keyword} Takes Internet By Storm!",
                "You Won't Believe This {keyword} Challenge!",
                "{keyword} Goes Viral: Here's What Happened",
                "The {keyword} Trend Everyone Is Talking About"
            ],
            "technical": [
                "Comprehensive Analysis of {keyword} Implementation",
                "{keyword}: A Technical Deep Dive",
                "Optimizing {keyword} Performance Metrics",
                "{keyword} Architecture and Best Practices"
            ],
            "news": [
                "Exclusive Report: {keyword} Developments",
                "{keyword} Makes Headlines Worldwide",
                "Inside the {keyword} Story",
                "{keyword}: What You Need to Know"
            ],
            "product": [
                "Amazing {keyword} Deal Just Dropped!",
                "Review: The Best {keyword} on the Market",
                "{keyword} at Unbeatable Price",
                "Limited Time Offer on {keyword}"
            ]
        }
    
    def setup_word_banks(self):
        """Setup word banks for text generation"""
        self.word_banks = {
            "verbs": ["accelerate", "analyze", "build", "create", "design", "develop", 
                     "engineer", "enhance", "evaluate", "expand", "generate", "implement",
                     "improve", "innovate", "integrate", "launch", "optimize", "produce",
                     "research", "transform", "update", "upgrade", "validate"],
            
            "adjectives": ["advanced", "agile", "automated", "cloud", "collaborative",
                          "comprehensive", "cutting-edge", "data-driven", "digital",
                          "disruptive", "dynamic", "efficient", "enterprise", "flexible",
                          "innovative", "integrated", "intelligent", "interactive",
                          "modern", "next-generation", "scalable", "secure", "smart",
                          "sustainable", "transparent", "user-friendly"],
            
            "nouns": ["algorithm", "application", "architecture", "automation", "cloud",
                     "collaboration", "community", "dashboard", "data", "deployment",
                     "design", "development", "ecosystem", "framework", "infrastructure",
                     "innovation", "integration", "interface", "marketplace", "methodology",
                     "model", "network", "platform", "process", "product", "research",
                     "solution", "strategy", "system", "technology", "tool", "transformation"],
            
            "connectors": ["according to", "additionally", "as a result", "consequently",
                          "furthermore", "however", "in addition", "in conclusion",
                          "in contrast", "in fact", "in summary", "moreover", "nevertheless",
                          "on the other hand", "similarly", "therefore", "thus"]
        }
    
    def generate_targeted_content(self, bot_type: str, seed_keyword: str = None) -> Dict:
        """Generate content targeted to specific bot type"""
        
        # Select appropriate keywords based on bot type
        if bot_type in ["tiktok", "social"]:
            keywords = [seed_keyword] if seed_keyword else ["viral", "trend", "challenge", "dance"]
            theme = "viral"
        elif bot_type in ["news", "academic"]:
            keywords = [seed_keyword] if seed_keyword else ["analysis", "report", "study", "findings"]
            theme = "news"
        elif bot_type == "shopping":
            keywords = [seed_keyword] if seed_keyword else ["deal", "price", "buy", "discount"]
            theme = "product"
        else:
            keywords = self.config.keywords
            theme = random.choice(self.config.content_themes)
        
        # Generate content with high keyword density
        title = self.generate_title(theme, keywords)
        content = self.generate_body(theme, keywords)
        
        # Add bot-specific traps
        traps = self.generate_bot_traps(bot_type, keywords)
        
        return {
            "title": title,
            "content": content,
            "traps": traps,
            "keywords": keywords,
            "bot_type": bot_type,
            "theme": theme,
            "timestamp": datetime.now().isoformat(),
            "content_hash": hashlib.md5((title + content).encode()).hexdigest()
        }
    
    def generate_title(self, theme: str, keywords: List[str]) -> str:
        """Generate targeted title"""
        template = random.choice(self.templates.get(theme, self.templates["viral"]))
        keyword = random.choice(keywords)
        return template.format(keyword=keyword.title())
    
    def generate_sentence(self) -> str:
        """Generate a random sentence"""
        structures = [
            "The {adj} {noun} {verb} the {adj} {noun}.",
            "{adj} {noun} and {adj} {noun} {verb} {adj} solutions.",
            "Our {adj} approach to {noun} {verb} unprecedented results.",
            "The future of {noun} depends on {adj} {noun}.",
            "{adj} {noun} platforms {verb} the {noun} ecosystem."
        ]
        
        structure = random.choice(structures)
        
        # Fill in the blanks
        while True:
            try:
                sentence = structure.format(
                    adj=random.choice(self.word_banks["adjectives"]),
                    noun=random.choice(self.word_banks["nouns"]),
                    verb=random.choice(self.word_banks["verbs"])
                )
                return sentence.capitalize()
            except KeyError:
                # Try again if format fails
                continue
    
    def generate_body(self, theme: str, keywords: List[str], paragraphs: int = 5) -> str:
        """Generate body text with keyword stuffing"""
        paragraphs_list = []
        
        for i in range(paragraphs):
            # Create paragraph with keyword density
            base_text = self.generate_paragraph()
            
            # Inject keywords
            if random.random() > 0.3:  # 70% chance to inject keywords
                injection_points = random.randint(1, 3)
                for _ in range(injection_points):
                    keyword = random.choice(keywords)
                    position = random.randint(0, len(base_text.split()) // 2)
                    words = base_text.split()
                    words.insert(position, f"**{keyword}**")
                    base_text = " ".join(words)
            
            paragraphs_list.append(base_text)
        
        return "\n\n".join(paragraphs_list)
    
    def generate_paragraph(self, sentences: int = None) -> str:
        """Generate a paragraph of text"""
        if sentences is None:
            sentences = random.randint(3, 7)
        
        paragraph_sentences = []
        for i in range(sentences):
            sentence = self.generate_sentence()
            
            # Occasionally add a connector
            if i > 0 and random.random() > 0.5:
                connector = random.choice(self.word_banks["connectors"])
                sentence = f"{connector.capitalize()}, {sentence[0].lower()}{sentence[1:]}"
            
            paragraph_sentences.append(sentence)
        
        return " ".join(paragraph_sentences)
    
    def generate_bot_traps(self, bot_type: str, keywords: List[str]) -> Dict:
        """Generate hidden traps for bots"""
        traps = {
            "hidden_divs": [],
            "meta_tags": [],
            "json_ld": [],
            "infinite_links": []
        }
        
        # Hidden content with keywords
        for i in range(random.randint(3, 7)):
            trap_text = " ".join([random.choice(keywords) for _ in range(random.randint(5, 15))])
            traps["hidden_divs"].append(
                f'<div style="display:none;" data-bot-trap="{bot_type}">{trap_text}</div>'
            )
        
        # Meta tags targeting bots
        for keyword in keywords[:3]:
            traps["meta_tags"].append(
                f'<meta name="keywords" content="{keyword}, {random.choice(keywords)}, related">'
            )
        
        # JSON-LD structured data (attracts certain crawlers)
        if random.random() > 0.5:
            traps["json_ld"].append({
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": f"Important {random.choice(keywords).title()} Information",
                "keywords": ", ".join(keywords)
            })
        
        # Infinite recursion links
        base_path = f"/{bot_type}/content/"
        for i in range(5):
            traps["infinite_links"].append(
                f'<a href="{base_path}{hashlib.md5(str(i).encode()).hexdigest()}" style="display:none;">More</a>'
            )
        
        return traps

# ============================================================================
# INTERACTIVE CONTROL PANEL 
# ============================================================================

class InteractiveControlPanel:
    """Interactive terminal-based control panel"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.running = True
        self.stats = {
            "total_requests": 0,
            "bot_requests": 0,
            "targeted_bots": 0,
            "keywords_triggered": Counter(),
            "bot_types_detected": Counter(),
            "last_request": None
        }
    
    def run(self):
        """Run the interactive control panel"""
        self.fallback_cli()
    
    def fallback_cli(self):
        """Fallback command-line interface"""
        print("\n" + "="*60)
        print(" AI SCRAPER TAR PIT - INTERACTIVE CONTROL PANEL")
        print("="*60)
        
        while self.running:
            print("\nOptions:")
            print("1. View Statistics")
            print("2. Configure Keywords")
            print("3. View Bot Detections")
            print("4. View Active Configuration")
            print("5. Reset Counters")
            print("6. Exit")
            print("7. Start Web Server (in background)")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.print_stats()
            elif choice == "2":
                self.configure_cli()
            elif choice == "3":
                self.print_bot_detections()
            elif choice == "4":
                self.print_config()
            elif choice == "5":
                self.stats = {k: 0 for k in self.stats}
                print("Counters reset!")
            elif choice == "6":
                self.running = False
                print("Exiting control panel...")
            elif choice == "7":
                self.start_server_background()
    
    def print_stats(self):
        """Print statistics"""
        print("\n STATISTICS:")
        print(f"  Total Requests: {self.stats['total_requests']}")
        print(f"  Bot Requests: {self.stats['bot_requests']}")
        print(f"  Targeted Bots: {self.stats['targeted_bots']}")
        if self.stats['total_requests'] > 0:
            bot_percent = (self.stats['bot_requests'] / self.stats['total_requests']) * 100
            print(f"  Bot Percentage: {bot_percent:.1f}%")
        
        if self.stats['last_request']:
            print(f"  Last Request: {self.stats['last_request']}")
    
    def configure_cli(self):
        """Configure via CLI"""
        config = self.config_manager.active_config
        
        print(f"\nCurrent Keywords: {', '.join(config.keywords)}")
        print("Enter new keywords (comma-separated), or press Enter to keep current:")
        new_keywords = input("> ").strip()
        
        if new_keywords:
            config.keywords = [k.strip() for k in new_keywords.split(',') if k.strip()]
            self.config_manager.save_config()
            print(" Configuration updated!")
            
            # Ask about bot types
            print(f"\nCurrent Bot Targets: {', '.join(config.bot_types)}")
            print("Available types: tiktok, news, shopping, academic, ai_trainer, social")
            print("Enter new bot types (comma-separated), or press Enter to keep current:")
            new_bots = input("> ").strip()
            
            if new_bots:
                config.bot_types = [b.strip() for b in new_bots.split(',') if b.strip()]
                self.config_manager.save_config()
                print(" Bot targets updated!")
    
    def print_bot_detections(self):
        """Print bot detections"""
        print("\n BOT DETECTIONS:")
        if not self.stats['bot_types_detected']:
            print("  No bots detected yet.")
        else:
            for bot_type, count in self.stats['bot_types_detected'].most_common():
                print(f"  {bot_type}: {count}")
    
    def print_config(self):
        """Print current configuration"""
        config = self.config_manager.active_config
        print("\n ACTIVE CONFIGURATION:")
        print(f"  Keywords: {', '.join(config.keywords)}")
        print(f"  Target Bots: {', '.join(config.bot_types)}")
        print(f"  Content Themes: {', '.join(config.content_themes)}")
        print(f"  Keyword Density: {config.density_multiplier}x")
        print(f"  Recursion Depth: {config.recursion_depth} levels")
    
    def start_server_background(self):
        """Start server in background thread"""
        print("\nStarting web server in background...")
        print("Server will run on http://localhost:8080")
        print("Press Ctrl+C in the main terminal to stop")
        print("Keep this control panel open to monitor traffic")

# ============================================================================
# ENHANCED REQUEST HANDLER
# ============================================================================

class EnhancedWebMonitorHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler with keyword targeting"""
    
    def __init__(self, *args, content_gen=None, db=None, 
                 config_manager=None, control_panel=None, **kwargs):
        self.content_gen = content_gen
        self.db = db
        self.config_manager = config_manager
        self.control_panel = control_panel
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        start_time = time.time()
        
        # Update statistics
        if self.control_panel:
            self.control_panel.stats["total_requests"] += 1
        
        # Detect bot type
        user_agent = self.headers.get('User-Agent', '')
        bot_type = self.config_manager.detect_bot_type(user_agent, self.path)
        
        # Check if it's a bot
        is_bot = bot_type != "generic"
        
        if is_bot and self.control_panel:
            self.control_panel.stats["bot_requests"] += 1
            self.control_panel.stats["bot_types_detected"][bot_type] += 1
            self.control_panel.stats["last_request"] = f"{bot_type} at {datetime.now().strftime('%H:%M:%S')}"
        
        # Generate targeted response
        response = self.generate_targeted_response(bot_type, is_bot)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', response['content_type'])
        self.end_headers()
        self.wfile.write(response['content'].encode('utf-8'))
        
        # Log
        response_time = time.time() - start_time
        logger.info(f"Bot: {bot_type} | Path: {self.path} | Time: {response_time:.2f}s")
        
        # Also print to console for monitoring
        if is_bot:
            print(f"[{datetime.now().strftime('%H:%M:%S')}]  {bot_type.upper()} detected - {self.path}")
    
    def log_message(self, format, *args):
        """Override to reduce console noise"""
        pass
    
    def generate_targeted_response(self, bot_type: str, is_bot: bool) -> Dict:
        """Generate response targeted to bot type"""
        
        if not is_bot:
            # Human visitor - show simple page
            return {
                'content_type': 'text/html',
                'content': self.generate_human_page()
            }
        
        # Bot detected - generate targeted content
        content = self.content_gen.generate_targeted_content(bot_type)
        
        # Check if this is a targeted bot type
        is_targeted = bot_type in self.config_manager.active_config.bot_types
        
        if is_targeted and self.control_panel:
            self.control_panel.stats["targeted_bots"] += 1
        
        # Generate HTML with traps
        html = self.wrap_content_with_traps(content, bot_type, is_targeted)
        
        return {
            'content_type': 'text/html',
            'content': html
        }
    
    def generate_human_page(self) -> str:
        """Generate page for human visitors"""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Research Site</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h1>Welcome to the Research Portal</h1>
            <p>This site is used for academic research on web traffic patterns.</p>
            <p>For more information, please contact the research team.</p>
            <hr>
            <p><small>Educational use only. All access is logged for research purposes.</small></p>
        </body>
        </html>
        """
    
    def wrap_content_with_traps(self, content: Dict, bot_type: str, is_targeted: bool) -> str:
        """Wrap content with traps and tracking"""
        
        # Base traps from content generator
        traps = content['traps']
        
        # Additional targeted traps
        if is_targeted:
            traps['hidden_divs'].extend(self.generate_deep_traps(bot_type, content['keywords']))
        
        # Build HTML
        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            f'<title>{content["title"]}</title>',
            '<meta name="description" content="Interesting content about various topics">',
            '<meta name="robots" content="index, follow">',
            '<meta name="generator" content="Research Content System">'
        ]
        
        # Add meta tags
        html_parts.extend(traps['meta_tags'])
        
        # Add JSON-LD
        if traps['json_ld']:
            html_parts.append('<script type="application/ld+json">')
            html_parts.append(json.dumps(traps['json_ld'][0]))
            html_parts.append('</script>')
        
        html_parts.extend([
            '</head>',
            '<body>',
            f'<article style="max-width: 800px; margin: 0 auto; padding: 20px;">',
            f'<h1>{content["title"]}</h1>',
            f'<div class="content">{content["content"]}</div>',
            '</article>'
        ])
        
        # Add infinite links section (hidden)
        html_parts.append('<div style="display:none;">')
        html_parts.append('<h2>Related Content</h2>')
        html_parts.extend(traps['infinite_links'])
        html_parts.append('</div>')
        
        # Add hidden traps
        html_parts.extend(traps['hidden_divs'])
        
        # Add recursive iframe for deep trapping
        if is_targeted and self.config_manager.active_config.recursion_depth > 0:
            html_parts.append(self.generate_recursive_iframe(bot_type))
        
        html_parts.extend([
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)
    
    def generate_deep_traps(self, bot_type: str, keywords: List[str]) -> List[str]:
        """Generate deep traps for targeted bots"""
        traps = []
        
        # Infinite comment section
        traps.append('<div style="display:none;" id="infinite-comments">')
        for i in range(20):
            user = random.choice(["user", "viewer", "subscriber"])
            comment = f"Great {random.choice(keywords)} content! More please."
            traps.append(f'<div class="comment"><strong>{user}_{i}:</strong> {comment}</div>')
        traps.append('</div>')
        
        # Fake API endpoints in JavaScript
        traps.append('<script>')
        traps.append('// Fake API endpoints for bots to discover')
        for keyword in keywords[:3]:
            traps.append(f'const {keyword}_api = "/api/v1/{keyword}/data.json";')
        traps.append('</script>')
        
        # Hidden links to trap pages
        traps.append('<div style="display:none;">')
        for i in range(10):
            traps.append(f'<a href="/trap/{bot_type}/page/{i}">Hidden Link {i}</a>')
        traps.append('</div>')
        
        return traps
    
    def generate_recursive_iframe(self, bot_type: str) -> str:
        """Generate recursive iframe for deep trapping"""
        depth = self.config_manager.active_config.recursion_depth
        if depth <= 0:
            return ""
        
        src = f"/deep-trap/{bot_type}/{random.randint(1000, 9999)}"
        return f'<iframe src="{src}" style="display:none;" sandbox="allow-same-origin"></iframe>'

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class EnhancedWebMonitor:
    """Main enhanced web monitor application"""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.config_manager = ConfigManager()
        self.content_gen = TargetedContentGenerator(self.config_manager.active_config)
        self.control_panel = InteractiveControlPanel(self.config_manager)
        self.server = None
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
    
    def start(self):
        """Start the enhanced web monitor"""
        
        # Setup HTTP handler
        handler = lambda *args: EnhancedWebMonitorHandler(
            *args,
            content_gen=self.content_gen,
            db=None,  # We're not using DB in this version
            config_manager=self.config_manager,
            control_panel=self.control_panel
        )
        
        self.server = HTTPServer((self.host, self.port), handler)
        
        print(f"\n Enhanced Web Monitor started on http://{self.host}:{self.port}")
        print(f" Targeting: {', '.join(self.config_manager.active_config.bot_types)}")
        print(f" Keywords: {', '.join(self.config_manager.active_config.keywords[:5])}...")
        print("\n Monitoring active. Bot detections will appear below:")
        print("="*60)
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the web monitor"""
        if self.server:
            self.server.shutdown()
        print("\n Server stopped")

# ============================================================================
# CONFIGURATION WIZARD
# ============================================================================

def configuration_wizard():
    """Interactive configuration wizard"""
    print("\n" + "="*60)
    print(" AI SCRAPER TAR PIT - CONFIGURATION WIZARD")
    print("="*60)
    
    config = {}
    
    # Bot types
    print("\n SELECT BOT TYPES TO TARGET:")
    bot_options = ["tiktok", "news", "shopping", "academic", "ai_trainer", "social", "all"]
    for i, bot in enumerate(bot_options, 1):
        print(f"  {i}. {bot}")
    
    while True:
        bot_choices = input("\nEnter numbers (comma-separated): ").strip()
        if not bot_choices:
            print("Please select at least one bot type.")
            continue
        
        try:
            selected_indices = [int(x.strip()) - 1 for x in bot_choices.split(',') if x.strip().isdigit()]
            config['bot_types'] = [bot_options[i] for i in selected_indices if i < len(bot_options)]
            
            if "all" in config['bot_types']:
                config['bot_types'] = ["tiktok", "news", "shopping", "academic", "ai_trainer", "social"]
            
            if config['bot_types']:
                break
            else:
                print("Invalid selection. Please try again.")
        except:
            print("Invalid input. Please enter numbers like '1,3,5'.")
    
    # Keywords
    print("\n ENTER TARGETING KEYWORDS:")
    print("(These will be injected into content to attract specific bots)")
    
    if "tiktok" in config['bot_types']:
        print("  Suggested for TikTok: viral, trending, challenge, dance, music")
    if "news" in config['bot_types']:
        print("  Suggested for News: breaking, exclusive, report, analysis")
    if "shopping" in config['bot_types']:
        print("  Suggested for Shopping: discount, sale, price, deal, buy")
    if "ai_trainer" in config['bot_types']:
        print("  Suggested for AI Trainers: dataset, training, machine learning, AI")
    
    while True:
        keywords = input("\nEnter keywords (comma-separated): ").strip()
        if keywords:
            config['keywords'] = [k.strip() for k in keywords.split(',') if k.strip()]
            if config['keywords']:
                break
            else:
                print("Please enter at least one keyword.")
        else:
            print("Keywords are required. Please enter some keywords.")
    
    # Content themes
    print("\n SELECT CONTENT THEMES:")
    themes = ["viral", "technical", "news", "product", "academic", "entertainment"]
    for i, theme in enumerate(themes, 1):
        print(f"  {i}. {theme}")
    
    theme_choices = input("\nEnter numbers (comma-separated, or press Enter for default): ").strip()
    if theme_choices:
        try:
            selected_themes = [int(x.strip()) - 1 for x in theme_choices.split(',') if x.strip().isdigit()]
            config['content_themes'] = [themes[i] for i in selected_themes if i < len(themes)]
        except:
            config['content_themes'] = ["viral", "news"]
    else:
        config['content_themes'] = ["viral", "news"]
    
    # Trap intensity
    print("\n TRAP INTENSITY:")
    print("  1. Light (basic traps)")
    print("  2. Medium (recommended)")
    print("  3. Heavy (maximum recursion)")
    
    intensity = input("\nSelect intensity (1-3, default 2): ").strip()
    if intensity == "1":
        config['density_multiplier'] = 1.0
        config['recursion_depth'] = 2
    elif intensity == "3":
        config['density_multiplier'] = 3.0
        config['recursion_depth'] = 10
    else:
        config['density_multiplier'] = 2.0
        config['recursion_depth'] = 5
    
    # Save configuration
    config_file = "bot_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n Configuration saved to {config_file}")
    print(f"\n SUMMARY:")
    print(f"   Target Bots: {', '.join(config['bot_types'])}")
    print(f"   Keywords: {', '.join(config['keywords'][:5])}...")
    print(f"   Themes: {', '.join(config['content_themes'])}")
    print(f"   Intensity: {intensity}/3")
    
    return config

# ============================================================================
# QUICK START FUNCTIONS
# ============================================================================

def quick_start():
    """Quick start with default configuration"""
    print("\n QUICK START - DEFAULT CONFIGURATION")
    print("="*50)
    
    # Create default config
    config = {
        "keywords": ["viral", "trending", "challenge", "dance", "music", "ai", "dataset", "training"],
        "bot_types": ["tiktok", "ai_trainer", "social"],
        "content_themes": ["viral", "technical"],
        "density_multiplier": 2.0,
        "recursion_depth": 5,
        "hidden_traps": True,
        "embed_tracking": True,
        "meta_tag_injection": True
    }
    
    with open("bot_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print(" Created default configuration")
    print(" Targeting: TikTok, AI Trainers, Social bots")
    print(" Keywords: viral, trending, challenge, dance, music, ai, dataset, training")
    print(" Starting server on http://localhost:8080")
    
    # Start server
    monitor = EnhancedWebMonitor('0.0.0.0', 8080)
    monitor.start()

def test_bot_detection():
    """Test bot detection with sample requests"""
    print("\n TESTING BOT DETECTION")
    print("="*50)
    
    config_manager = ConfigManager()
    
    test_cases = [
        ("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", "/news/breaking"),
        ("Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)", "/article/123"),
        ("TikTok/8.0.5 (iPhone; iOS 14.4; Scale/3.00)", "/video/12345"),
        ("python-requests/2.25.1", "/api/data"),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "/"),
        ("GPTBot/1.0 (+https://openai.com/gptbot)", "/ai/training"),
        ("anthropic-ai/1.0", "/dataset/download")
    ]
    
    for ua, path in test_cases:
        bot_type = config_manager.detect_bot_type(ua, path)
        print(f"UA: {ua[:40]}... | Path: {path} -> Bot Type: {bot_type}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description=' AI Scraper Tar Pit - Enhanced Web Interaction Monitor')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    parser.add_argument('--wizard', action='store_true', help='Run configuration wizard')
    parser.add_argument('--quick', action='store_true', help='Quick start with default config')
    parser.add_argument('--test', action='store_true', help='Test bot detection')
    parser.add_argument('--control', action='store_true', help='Start control panel only')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" AI SCRAPER TAR PIT - KEYWORD TARGETING EDITION")
    print("="*70)
    print("Educational tool for researching web scraping patterns.")
    print("by ek0ms savi0r")
    print("="*70)
    
    if args.test:
        test_bot_detection()
        return
    
    if args.control:
        config_manager = ConfigManager()
        control_panel = InteractiveControlPanel(config_manager)
        control_panel.run()
        return
    
    # Run configuration wizard if requested
    if args.wizard:
        configuration_wizard()
        print("\n Configuration complete! Run without --wizard to start the server.")
        choice = input("\nStart server now? (y/n): ").strip().lower()
        if choice == 'y':
            monitor = EnhancedWebMonitor(args.host, args.port)
            monitor.start()
        return
    
    if args.quick:
        quick_start()
        return
    
    # Start the monitor
    print(f"\nStarting server on http://{args.host}:{args.port}")
    print("To configure targeting, run: python3 tarpit.py --wizard")
    print("For quick start with defaults: python3 tarpit.py --quick")
    print("Press Ctrl+C to stop the server\n")
    
    monitor = EnhancedWebMonitor(args.host, args.port)
    
    try:
        monitor.start()
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n Error: {e}")
        print("Try running with: python3 tarpit.py --quick")
        sys.exit(1)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Goodbye!")
        sys.exit(0)
