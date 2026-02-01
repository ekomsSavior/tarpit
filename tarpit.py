#!/usr/bin/env python3
"""
Enhanced AI Scraper Tar Pit with Interactive Elements
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
import mimetypes
import zipfile
import io
import base64
import uuid
import tempfile
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote, unquote
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
from collections import Counter, defaultdict
import re
import textwrap
import math
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tarpit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FILE UPLOAD AND BAIT CONTENT MANAGEMENT
# ============================================================================

class BaitContentManager:
    """Manage user-uploaded bait files and generated trap content"""
    
    def __init__(self, bait_dir: str = "bait_files"):
        self.bait_dir = bait_dir
        self.generated_dir = os.path.join(bait_dir, "generated")
        self.uploaded_dir = os.path.join(bait_dir, "uploaded")
        
        # Create directories
        os.makedirs(self.bait_dir, exist_ok=True)
        os.makedirs(self.generated_dir, exist_ok=True)
        os.makedirs(self.uploaded_dir, exist_ok=True)
        
        # Track bait files
        self.bait_files = {
            "pdf": [],
            "csv": [],
            "json": [],
            "xml": [],
            "txt": [],
            "zip": [],
            "image": []
        }
        
        self.scan_bait_files()
        
        # Generate default bait files if none exist
        if not any(files for files in self.bait_files.values()):
            self.generate_default_bait_files()
    
    def scan_bait_files(self):
        """Scan bait directories for files"""
        for filename in os.listdir(self.uploaded_dir):
            filepath = os.path.join(self.uploaded_dir, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower().replace('.', '')
                if ext in self.bait_files:
                    self.bait_files[ext].append({
                        "name": filename,
                        "path": filepath,
                        "size": os.path.getsize(filepath),
                        "upload_time": os.path.getmtime(filepath)
                    })
    
    def generate_default_bait_files(self):
        """Generate default bait files for trapping"""
        logger.info("Generating default bait files...")
        
        # Generate fake PDF
        pdf_content = self.generate_fake_pdf()
        pdf_path = os.path.join(self.generated_dir, "dataset_research_paper.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_content)
        self.bait_files["pdf"].append({
            "name": "dataset_research_paper.pdf",
            "path": pdf_path,
            "size": len(pdf_content),
            "upload_time": time.time()
        })
        
        # Generate fake CSV
        csv_content = self.generate_fake_csv()
        csv_path = os.path.join(self.generated_dir, "user_data.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        self.bait_files["csv"].append({
            "name": "user_data.csv",
            "path": csv_path,
            "size": len(csv_content),
            "upload_time": time.time()
        })
        
        # Generate fake JSON
        json_content = self.generate_fake_json()
        json_path = os.path.join(self.generated_dir, "api_response.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_content, indent=2))
        self.bait_files["json"].append({
            "name": "api_response.json",
            "path": json_path,
            "size": len(json.dumps(json_content)),
            "upload_time": time.time()
        })
        
        # Generate fake XML
        xml_content = self.generate_fake_xml()
        xml_path = os.path.join(self.generated_dir, "data_feed.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        self.bait_files["xml"].append({
            "name": "data_feed.xml",
            "path": xml_path,
            "size": len(xml_content),
            "upload_time": time.time()
        })
        
        logger.info(f"Generated {len(self.bait_files['pdf'] + self.bait_files['csv'] + self.bait_files['json'] + self.bait_files['xml'])} bait files")
    
    def generate_fake_pdf(self) -> bytes:
        """Generate a fake PDF file with garbage content"""
        # Simple PDF header and fake content
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj

4 0 obj
<< /Length 100 >>
stream
BT
/F1 12 Tf
50 700 Td
(FAKE RESEARCH DATASET - GENERATED FOR TESTING PURPOSES) Tj
50 680 Td
(This document contains randomly generated data intended for) Tj
50 660 Td
(web scraping research and bot trapping applications.) Tj
50 640 Td
(All content is meaningless and generated algorithmically.) Tj
ET
endstream
endobj

5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000101 00000 n 
0000000220 00000 n 
0000000468 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
578
%%EOF"""
        return pdf_content
    
    def generate_fake_csv(self, rows: int = 1000) -> str:
        """Generate fake CSV data"""
        headers = ["user_id", "username", "email", "signup_date", "last_login", "activity_score", "preferences"]
        
        csv_lines = [",".join(headers)]
        
        for i in range(rows):
            user_id = f"USER{10000 + i}"
            username = f"user_{random.randint(1000, 9999)}"
            email = f"{username}@example.com"
            date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
            last_login = (datetime.now() - timedelta(hours=random.randint(0, 24))).strftime("%Y-%m-%d %H:%M:%S")
            score = random.randint(0, 100)
            prefs = json.dumps({"theme": random.choice(["dark", "light"]), "notifications": random.choice([True, False])})
            
            csv_lines.append(f"{user_id},{username},{email},{date},{last_login},{score},{prefs}")
        
        return "\n".join(csv_lines)
    
    def generate_fake_json(self) -> Dict:
        """Generate fake JSON API response"""
        return {
            "status": "success",
            "data": {
                "users": [{
                    "id": i,
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
                    "metadata": {
                        "preferences": random.choice(["dark", "light", "auto"]),
                        "notifications": random.choice([True, False]),
                        "language": random.choice(["en", "es", "fr", "de"])
                    }
                } for i in range(50)],
                "pagination": {
                    "page": 1,
                    "total_pages": 100,
                    "total_items": 5000,
                    "next_page": "/api/v2/users?page=2"
                }
            },
            "generated_at": datetime.now().isoformat(),
            "version": "2.0.1"
        }
    
    def generate_fake_xml(self) -> str:
        """Generate fake XML feed"""
        root = ET.Element("data_feed")
        root.set("version", "1.0")
        root.set("generated", datetime.now().isoformat())
        
        for i in range(20):
            item = ET.SubElement(root, "item")
            ET.SubElement(item, "id").text = str(1000 + i)
            ET.SubElement(item, "title").text = f"Generated Content Item {i+1}"
            ET.SubElement(item, "description").text = "This is algorithmically generated content for research purposes."
            ET.SubElement(item, "timestamp").text = datetime.now().isoformat()
            ET.SubElement(item, "category").text = random.choice(["news", "research", "data", "analysis"])
        
        return ET.tostring(root, encoding="unicode", method="xml")
    
    def upload_file(self, file_path: str, original_name: str) -> bool:
        """Upload a bait file from user"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Copy to uploaded directory
            dest_path = os.path.join(self.uploaded_dir, original_name)
            with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())
            
            # Add to tracking
            ext = os.path.splitext(original_name)[1].lower().replace('.', '')
            if ext in self.bait_files:
                self.bait_files[ext].append({
                    "name": original_name,
                    "path": dest_path,
                    "size": os.path.getsize(dest_path),
                    "upload_time": time.time()
                })
            
            logger.info(f"Uploaded bait file: {original_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False
    
    def get_random_bait_file(self, file_type: str = None) -> Optional[Dict]:
        """Get a random bait file, optionally filtered by type"""
        if file_type and file_type in self.bait_files:
            if self.bait_files[file_type]:
                return random.choice(self.bait_files[file_type])
        
        # Get any bait file
        all_files = []
        for files in self.bait_files.values():
            all_files.extend(files)
        
        if all_files:
            return random.choice(all_files)
        
        return None

# ============================================================================
# INTERACTIVE ELEMENTS GENERATOR
# ============================================================================

class InteractiveElementsGenerator:
    """Generate interactive elements for bots to interact with"""
    
    def __init__(self):
        self.button_styles = [
            "padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;",
            "padding: 12px 24px; background: #2ecc71; color: white; border: 2px solid #27ae60; border-radius: 8px; cursor: pointer; font-weight: bold;",
            "padding: 8px 16px; background: #e74c3c; color: white; border: none; border-radius: 3px; cursor: pointer; text-transform: uppercase;",
            "padding: 10px 20px; background: linear-gradient(45deg, #9b59b6, #8e44ad); color: white; border: none; border-radius: 20px; cursor: pointer;"
        ]
        
        self.form_styles = [
            "padding: 20px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px;",
            "padding: 30px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 15px;",
            "padding: 15px; background: #f0f0f0; border: 2px dashed #ccc; border-radius: 5px;"
        ]
    
    def generate_interactive_page(self, bot_type: str, keywords: List[str]) -> Dict:
        """Generate a page with interactive elements"""
        
        elements = {
            "buttons": self.generate_buttons(bot_type, keywords),
            "forms": self.generate_forms(bot_type, keywords),
            "links": self.generate_interactive_links(bot_type, keywords),
            "javascript": self.generate_javascript_traps(bot_type, keywords),
            "dynamic_content": self.generate_dynamic_content(bot_type, keywords)
        }
        
        return elements
    
    def generate_buttons(self, bot_type: str, keywords: List[str]) -> List[str]:
        """Generate interactive buttons"""
        buttons = []
        
        button_texts = {
            "tiktok": [" View Video", " Like Content", " Share Now", " Play Sound", " Trending"],
            "news": [" Read More", " Subscribe", " View Stats", " Analysis", " Latest"],
            "shopping": [" Add to Cart", " Buy Now", " Add to Wishlist", " View Price", " Get Deal"],
            "ai_trainer": [" Download Dataset", " Train Model", " View Results", " Configure", " Deploy"],
            "academic": [" Read Paper", " Cite This", " Abstract", " Methodology", " Download PDF"]
        }
        
        texts = button_texts.get(bot_type, ["Click Here", "Learn More", "Download", "View Details"])
        
        for i in range(random.randint(3, 7)):
            text = random.choice(texts)
            style = random.choice(self.button_styles)
            action = self.generate_button_action(bot_type, keywords)
            
            button = f'<button style="{style}" onclick="{action}" data-bot-target="{bot_type}">{text}</button>'
            buttons.append(button)
        
        return buttons
    
    def generate_button_action(self, bot_type: str, keywords: List[str]) -> str:
        """Generate JavaScript action for buttons"""
        actions = [
            f"window.location.href='/download/{bot_type}/{random.choice(keywords)}.pdf'",
            f"document.getElementById('hidden-content-{random.randint(1000,9999)}').style.display='block'",
            f"fetch('/api/{bot_type}/data').then(r => r.json()).then(console.log)",
            f"localStorage.setItem('bot_trap_{bot_type}', '{datetime.now().isoformat()}')",
            f"alert('Loading {random.choice(keywords)} content...')",
            f"document.cookie='bot_interaction={bot_type}_{int(time.time())}; path=/'",
            f"window.open('/trap/{bot_type}/page/{random.randint(1,100)}', '_blank')"
        ]
        
        return random.choice(actions)
    
    def generate_forms(self, bot_type: str, keywords: List[str]) -> List[str]:
        """Generate interactive forms"""
        forms = []
        
        form_templates = {
            "tiktok": ["video_upload", "comment_form", "hashtag_suggestion", "challenge_participation"],
            "news": ["newsletter_signup", "comment_form", "tip_submission", "reader_poll"],
            "shopping": ["checkout_form", "newsletter_signup", "review_form", "wishlist_add"],
            "ai_trainer": ["dataset_request", "model_training", "api_key_request", "feedback_form"],
            "academic": ["paper_submission", "citation_request", "data_request", "peer_review"]
        }
        
        form_types = form_templates.get(bot_type, ["contact_form", "signup_form", "feedback_form"])
        
        for form_type in random.sample(form_types, min(2, len(form_types))):
            form_html = self.generate_form_html(form_type, bot_type, keywords)
            forms.append(form_html)
        
        return forms
    
    def generate_form_html(self, form_type: str, bot_type: str, keywords: List[str]) -> str:
        """Generate HTML for a specific form type"""
        form_id = f"form-{hashlib.md5(f'{form_type}-{bot_type}'.encode()).hexdigest()[:8]}"
        
        fields = {
            "newsletter_signup": [
                ('email', 'Email Address', 'email', 'Enter your email'),
                ('name', 'Full Name', 'text', 'Your name'),
                ('preferences', 'Preferences', 'checkbox', 'Weekly updates, Daily digest')
            ],
            "comment_form": [
                ('comment', 'Your Comment', 'textarea', 'Share your thoughts...'),
                ('name', 'Name (optional)', 'text', ''),
                ('email', 'Email (optional)', 'email', '')
            ],
            "dataset_request": [
                ('purpose', 'Research Purpose', 'textarea', 'Describe your research...'),
                ('institution', 'Institution', 'text', 'University/Company'),
                ('email', 'Academic Email', 'email', ''),
                ('dataset_type', 'Dataset Type', 'select', 'training,validation,test')
            ],
            "checkout_form": [
                ('name', 'Full Name', 'text', ''),
                ('address', 'Shipping Address', 'textarea', ''),
                ('card', 'Card Number', 'text', 'XXXX-XXXX-XXXX-XXXX'),
                ('expiry', 'Expiry Date', 'text', 'MM/YY')
            ]
        }
        
        form_fields = fields.get(form_type, [
            ('input1', 'Field 1', 'text', 'Enter text'),
            ('input2', 'Field 2', 'email', 'Email address')
        ])
        
        style = random.choice(self.form_styles)
        
        form_html = f'<div style="{style}" id="{form_id}">\n'
        form_html += f'<h3>{form_type.replace("_", " ").title()}</h3>\n'
        
        for field_name, label, field_type, placeholder in form_fields:
            if field_type == 'textarea':
                form_html += f'<div><label>{label}:</label><br><textarea name="{field_name}" placeholder="{placeholder}" rows="3" style="width:100%;"></textarea></div>\n'
            elif field_type == 'select':
                form_html += f'<div><label>{label}:</label><br><select name="{field_name}" style="width:100%;padding:8px;"><option value="option1">Option 1</option><option value="option2">Option 2</option></select></div>\n'
            else:
                form_html += f'<div><label>{label}:</label><br><input type="{field_type}" name="{field_name}" placeholder="{placeholder}" style="width:100%;padding:8px;margin:5px 0;"></div>\n'
        
        submit_action = f"document.getElementById('{form_id}').innerHTML='<p style=\\'color:green;\\'>Thank you for submitting! Downloading {random.choice(keywords)} data...</p>'; setTimeout(() => window.location.href='/download/trap/{bot_type}.zip', 2000);"
        form_html += f'<br><button onclick="{submit_action}" style="padding:10px 20px;background:#007bff;color:white;border:none;border-radius:5px;cursor:pointer;">Submit</button>\n'
        form_html += '</div>'
        
        return form_html
    
    def generate_interactive_links(self, bot_type: str, keywords: List[str]) -> List[str]:
        """Generate interactive links and navigation"""
        links = []
        
        link_types = {
            "tiktok": ["video", "profile", "hashtag", "sound", "effect"],
            "news": ["article", "category", "author", "archive", "live"],
            "shopping": ["product", "category", "deal", "review", "comparison"],
            "ai_trainer": ["dataset", "model", "paper", "code", "tutorial"],
            "academic": ["paper", "author", "conference", "dataset", "method"]
        }
        
        link_templates = link_types.get(bot_type, ["page", "section", "item", "resource"])
        
        for i in range(random.randint(5, 15)):
            link_type = random.choice(link_templates)
            keyword = random.choice(keywords)
            url = f"/{bot_type}/{link_type}/{keyword}_{i}"
            
            link_html = f'<a href="{url}" class="interactive-link" data-bot="{bot_type}" data-type="{link_type}" style="color:#0066cc;text-decoration:none;margin:0 10px;padding:5px;border-radius:3px;background:#f0f0f0;">{keyword.title()} {link_type.title()} {i+1}</a>'
            links.append(link_html)
        
        # Add some download links
        for i in range(random.randint(2, 5)):
            file_types = ["pdf", "csv", "json", "xml", "zip"]
            file_type = random.choice(file_types)
            keyword = random.choice(keywords)
            url = f"/download/{bot_type}/{keyword}_dataset.{file_type}"
            
            link_html = f'<a href="{url}" class="download-link" data-bot="{bot_type}" data-filetype="{file_type}" style="color:#28a745;text-decoration:none;margin:0 10px;padding:8px 12px;border-radius:5px;background:#d4edda;border:1px solid #c3e6cb;display:inline-block;">⬇️ Download {keyword.title()} Data ({file_type.upper()})</a>'
            links.append(link_html)
        
        return links
    
    def generate_javascript_traps(self, bot_type: str, keywords: List[str]) -> str:
        """Generate JavaScript traps"""
        js_code = f"""
        <script>
        // Interactive traps for {bot_type} bots
        document.addEventListener('DOMContentLoaded', function() {{
            // Track interactions
            window.botInteractions = [];
            
            // Fake analytics
            setInterval(function() {{
                var fakeEvent = {{
                    type: 'bot_interaction',
                    bot_type: '{bot_type}',
                    timestamp: new Date().toISOString(),
                    keywords: {json.dumps(keywords)},
                    page: window.location.pathname
                }};
                // Simulate sending to fake analytics endpoint
                fetch('/analytics/track', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(fakeEvent)
                }}).catch(() => {{}});
            }}, 5000);
            
            // Dynamic content loading
            function loadMoreContent() {{
                var container = document.createElement('div');
                container.innerHTML = '<p>Loading more {random.choice(keywords)} content...</p>';
                document.body.appendChild(container);
                
                // Simulate AJAX content loading
                setTimeout(function() {{
                    container.innerHTML = '<h4>Additional Content Loaded</h4><p>This is dynamically loaded content about {random.choice(keywords)}.</p><button onclick="loadMoreContent()">Load Even More</button>';
                }}, 1000);
            }}
            
            // Auto-trigger some interactions
            setTimeout(loadMoreContent, 2000);
            setTimeout(function() {{
                document.cookie = 'bot_visited_{bot_type}=true; path=/; max-age=86400';
            }}, 1000);
            
            // Fake WebSocket connection
            try {{
                var ws = new WebSocket('ws://localhost:8080/ws/{bot_type}');
                ws.onopen = function() {{
                    console.log('Connected to fake WebSocket');
                }};
            }} catch(e) {{}}
        }});
        </script>
        """
        
        return js_code
    
    def generate_dynamic_content(self, bot_type: str, keywords: List[str]) -> str:
        """Generate dynamic content that changes/updates"""
        content_id = f"dynamic-content-{random.randint(1000, 9999)}"
        
        html = f"""
        <div id="{content_id}" style="padding:20px;background:#f8f9fa;border-radius:10px;margin:20px 0;">
            <h4>Live Updates & Dynamic Content</h4>
            <div id="{content_id}-updates">
                <p>Initializing {random.choice(keywords)} data stream...</p>
            </div>
            <button onclick="updateDynamicContent('{content_id}')" style="margin-top:10px;padding:8px 16px;background:#6c757d;color:white;border:none;border-radius:5px;">Refresh Data</button>
        </div>
        
        <script>
        function updateDynamicContent(containerId) {{
            var container = document.getElementById(containerId + '-updates');
            var keywords = {json.dumps(keywords)};
            var newContent = '';
            
            for(var i = 0; i < 3; i++) {{
                var keyword = keywords[Math.floor(Math.random() * keywords.length)];
                var timestamp = new Date().toISOString();
                newContent += '<div style="padding:10px;margin:5px 0;background:white;border-radius:5px;border-left:4px solid #007bff;">';
                newContent += '<strong>' + keyword.toUpperCase() + ' UPDATE</strong><br>';
                newContent += 'New data available at ' + timestamp + '<br>';
                newContent += '<small>Data points: ' + Math.floor(Math.random() * 1000) + '</small>';
                newContent += '</div>';
            }}
            
            container.innerHTML = newContent;
            
            // Fake API call
            fetch('/api/update/' + containerId, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{action: 'refresh', bot_type: '{bot_type}'}})
            }});
        }}
        
        // Auto-update every 10 seconds
        setInterval(function() {{ updateDynamicContent('{content_id}'); }}, 10000);
        </script>
        """
        
        return html

# ============================================================================
# CONFIGURATION MANAGEMENT (Enhanced)
# ============================================================================

@dataclass
class BotTargetingConfig:
    """Configuration for targeting specific bots"""
    keywords: List[str]
    bot_types: List[str]
    content_themes: List[str]
    density_multiplier: float = 2.0
    recursion_depth: int = 5
    hidden_traps: bool = True
    embed_tracking: bool = True
    meta_tag_injection: bool = True
    interactive_elements: bool = True
    bait_files_enabled: bool = True
    download_traps: bool = True
    user_uploads_enabled: bool = False

class ConfigManager:
    """Manage bot targeting configurations"""
    
    def __init__(self, config_file: str = "bot_config.json"):
        self.config_file = config_file
        self.active_config = BotTargetingConfig(
            keywords=["viral", "trending", "challenge", "dance", "music"],
            bot_types=["social"],
            content_themes=["entertainment", "lifestyle"],
            interactive_elements=True,
            bait_files_enabled=True
        )
        self.load_config()
        
        # Enhanced bot signature database
        self.bot_signatures = {
            "tiktok": {
                "ua_patterns": ["tiktok", "bytedance", "tt_webview"],
                "interest_keywords": ["short video", "trending", "hashtag", "challenge"],
                "content_types": ["video", "music", "dance"],
                "crawl_patterns": ["/video/", "/music/", "/tag/", "/challenge/"],
                "interactive_preferences": ["buttons", "forms", "downloads"],
                "file_preferences": ["mp4", "json", "zip"]
            },
            "news": {
                "ua_patterns": ["googlebot-news", "bingnews", "newscrawler"],
                "interest_keywords": ["breaking", "exclusive", "report", "analysis"],
                "content_types": ["article", "news", "report"],
                "crawl_patterns": ["/news/", "/article/", "/202", "/breaking/"],
                "interactive_preferences": ["forms", "links", "comments"],
                "file_preferences": ["pdf", "xml", "json"]
            },
            "shopping": {
                "ua_patterns": ["pricegrabber", "shoppingbot", "alibot"],
                "interest_keywords": ["discount", "sale", "price", "buy", "deal"],
                "content_types": ["product", "review", "price"],
                "crawl_patterns": ["/product/", "/shop/", "/buy/", "/price/"],
                "interactive_preferences": ["buttons", "forms", "cart"],
                "file_preferences": ["csv", "json", "xml"]
            },
            "academic": {
                "ua_patterns": ["semanticscholar", "academicbot", "research"],
                "interest_keywords": ["study", "research", "data", "analysis", "findings"],
                "content_types": ["paper", "study", "research"],
                "crawl_patterns": ["/paper/", "/study/", "/research/", "/pdf/"],
                "interactive_preferences": ["downloads", "forms", "links"],
                "file_preferences": ["pdf", "csv", "json", "zip"]
            },
            "ai_trainer": {
                "ua_patterns": ["gptbot", "claudebot", "anthropic", "cohere"],
                "interest_keywords": ["artificial intelligence", "machine learning", "dataset"],
                "content_types": ["tutorial", "explanation", "example"],
                "crawl_patterns": ["/ai/", "/ml/", "/dataset/", "/training/"],
                "interactive_preferences": ["downloads", "forms", "api"],
                "file_preferences": ["json", "csv", "txt", "zip", "pdf"]
            }
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
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

# ============================================================================
# ENHANCED REQUEST HANDLER WITH INTERACTIVE ELEMENTS
# ============================================================================

class InteractiveTarPitHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler with interactive elements and bait files"""
    
    def __init__(self, *args, 
                 content_gen=None, 
                 config_manager=None, 
                 control_panel=None,
                 bait_manager=None,
                 interactive_gen=None,
                 **kwargs):
        self.content_gen = content_gen
        self.config_manager = config_manager
        self.control_panel = control_panel
        self.bait_manager = bait_manager
        self.interactive_gen = interactive_gen
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
        
        # Handle special paths
        if self.path.startswith('/download/'):
            self.handle_download(bot_type, is_bot)
            return
        elif self.path.startswith('/api/'):
            self.handle_api(bot_type, is_bot)
            return
        elif self.path.startswith('/upload/'):
            self.handle_upload_page()
            return
        elif self.path.startswith('/bait/'):
            self.handle_bait_files()
            return
        
        # Generate targeted response
        response = self.generate_targeted_response(bot_type, is_bot)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', response['content_type'])
        self.end_headers()
        
        if isinstance(response['content'], bytes):
            self.wfile.write(response['content'])
        else:
            self.wfile.write(response['content'].encode('utf-8'))
        
        # Log
        response_time = time.time() - start_time
        logger.info(f"Bot: {bot_type} | Path: {self.path} | Time: {response_time:.2f}s")
        
        # Print to console
        if is_bot:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 {bot_type.upper()} detected - {self.path}")
    
    def do_POST(self):
        """Handle POST requests (for forms, uploads, etc.)"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        if self.path.startswith('/upload/file'):
            self.handle_file_upload(post_data)
        else:
            # For form submissions, show success page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Submission Received</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                <h1> Thank You!</h1>
                <p>Your submission has been received and is being processed.</p>
                <p><a href="/">Return to homepage</a></p>
                <div style="display:none;">
                    <!-- Hidden tracking for bots -->
                    <p>Additional data is being generated for your request...</p>
                    <script>
                        setTimeout(function() {
                            window.location.href = '/download/trap_dataset.zip';
                        }, 3000);
                    </script>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(success_html.encode('utf-8'))
    
    def handle_download(self, bot_type: str, is_bot: bool):
        """Handle download requests for bait files"""
        if not is_bot and not self.config_manager.active_config.download_traps:
            self.send_error(403, "Downloads disabled for humans")
            return
        
        # Parse requested file
        path_parts = self.path.split('/')
        if len(path_parts) < 3:
            self.send_error(404)
            return
        
        requested_file = path_parts[-1]
        file_ext = os.path.splitext(requested_file)[1].lower().replace('.', '')
        
        # Get appropriate bait file
        bait_file = self.bait_manager.get_random_bait_file(file_ext if file_ext in self.bait_manager.bait_files else None)
        
        if not bait_file:
            # Generate on-the-fly content
            if file_ext == 'pdf':
                content = self.bait_manager.generate_fake_pdf()
                content_type = 'application/pdf'
                filename = f"generated_{bot_type}_data.pdf"
            elif file_ext == 'csv':
                content = self.bait_manager.generate_fake_csv(rows=500)
                content_type = 'text/csv'
                filename = f"generated_{bot_type}_data.csv"
            elif file_ext == 'json':
                content = json.dumps(self.bait_manager.generate_fake_json(), indent=2)
                content_type = 'application/json'
                filename = f"generated_{bot_type}_data.json"
            elif file_ext == 'xml':
                content = self.bait_manager.generate_fake_xml()
                content_type = 'application/xml'
                filename = f"generated_{bot_type}_data.xml"
            elif file_ext == 'zip':
                # Create a zip with multiple fake files
                content = self.generate_fake_zip(bot_type)
                content_type = 'application/zip'
                filename = f"{bot_type}_dataset_collection.zip"
            else:
                content = f"Fake data for {bot_type} bots\nGenerated: {datetime.now().isoformat()}\nKeywords: {', '.join(self.config_manager.active_config.keywords[:5])}"
                content_type = 'text/plain'
                filename = f"generated_{bot_type}_data.txt"
        else:
            # Serve existing bait file
            try:
                with open(bait_file['path'], 'rb') as f:
                    content = f.read()
                content_type = self.get_mime_type(bait_file['name'])
                filename = bait_file['name']
            except Exception as e:
                logger.error(f"Failed to serve bait file: {e}")
                self.send_error(500)
                return
        
        # Update download stats
        if self.control_panel:
            self.control_panel.stats["downloads"] = self.control_panel.stats.get("downloads", 0) + 1
            self.control_panel.stats.setdefault("downloads_by_type", Counter())[bot_type] += 1
        
        # Send file
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        
        if isinstance(content, str):
            self.wfile.write(content.encode('utf-8'))
        else:
            self.wfile.write(content)
        
        logger.info(f"Download served: {filename} to {bot_type} bot")
        print(f"[{datetime.now().strftime('%H:%M:%S')}]  {bot_type.upper()} downloaded {filename}")
    
    def generate_fake_zip(self, bot_type: str) -> bytes:
        """Generate a fake ZIP file with multiple bait files"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add CSV
            csv_content = self.bait_manager.generate_fake_csv(rows=100)
            zip_file.writestr(f"{bot_type}_users.csv", csv_content)
            
            # Add JSON
            json_content = json.dumps(self.bait_manager.generate_fake_json(), indent=2)
            zip_file.writestr(f"{bot_type}_data.json", json_content)
            
            # Add README
            readme = f"""# {bot_type.upper()} Dataset Collection
Generated: {datetime.now().isoformat()}
Purpose: Research and analysis
Files: {bot_type}_users.csv, {bot_type}_data.json, {bot_type}_metadata.txt

This dataset contains algorithmically generated data for research purposes.
All content is synthetic and does not represent real information.
"""
            zip_file.writestr("README.txt", readme)
            
            # Add metadata
            metadata = {
                "generated_at": datetime.now().isoformat(),
                "bot_type": bot_type,
                "file_count": 3,
                "data_type": "synthetic",
                "keywords": self.config_manager.active_config.keywords[:10]
            }
            zip_file.writestr(f"{bot_type}_metadata.json", json.dumps(metadata, indent=2))
        
        return zip_buffer.getvalue()
    
    def handle_api(self, bot_type: str, is_bot: bool):
        """Handle API requests"""
        api_path = self.path[5:]  # Remove '/api/'
        
        if api_path.startswith('data'):
            self.send_api_response(bot_type)
        elif api_path.startswith('analytics'):
            self.send_analytics_response(bot_type)
        else:
            self.send_json_response({
                "error": "Invalid API endpoint",
                "available_endpoints": ["/api/data", "/api/analytics", "/api/downloads"],
                "timestamp": datetime.now().isoformat()
            })
    
    def send_api_response(self, bot_type: str):
        """Send fake API response"""
        response = {
            "status": "success",
            "bot_type": bot_type,
            "data": {
                "items": [{
                    "id": i,
                    "title": f"Generated Item {i}",
                    "content": f"This is fake content for {bot_type} bots",
                    "keywords": random.sample(self.config_manager.active_config.keywords, 3),
                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                } for i in range(random.randint(10, 50))],
                "pagination": {
                    "page": 1,
                    "total_pages": random.randint(10, 100),
                    "next_page": f"/api/data?page=2&bot_type={bot_type}"
                }
            },
            "generated_at": datetime.now().isoformat(),
            "download_url": f"/download/{bot_type}/full_dataset.zip"
        }
        
        self.send_json_response(response)
    
    def send_analytics_response(self, bot_type: str):
        """Send fake analytics data"""
        response = {
            "bot_type": bot_type,
            "analytics": {
                "total_requests": random.randint(1000, 10000),
                "unique_visitors": random.randint(100, 1000),
                "popular_keywords": random.sample(self.config_manager.active_config.keywords, 5),
                "downloads": random.randint(50, 500),
                "avg_session_duration": f"{random.randint(1, 10)}m {random.randint(0, 59)}s"
            },
            "recommendations": [
                f"Increase {random.choice(self.config_manager.active_config.keywords)} content",
                "Add more interactive elements",
                "Generate additional dataset variations"
            ]
        }
        
        self.send_json_response(response)
    
    def send_json_response(self, data: Dict):
        """Send JSON response"""
        response = json.dumps(data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def handle_upload_page(self):
        """Show file upload page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Bait Files</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .upload-area { 
                    border: 3px dashed #ccc; 
                    padding: 40px; 
                    text-align: center; 
                    margin: 20px 0;
                    border-radius: 10px;
                }
                .file-list { margin-top: 30px; }
                .file-item { 
                    padding: 10px; 
                    margin: 5px 0; 
                    background: #f8f9fa; 
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <h1> Upload Bait Files</h1>
            <p>Upload files that will be served to bots as bait.</p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area">
                    <input type="file" id="fileInput" name="file" multiple style="display: none;">
                    <button type="button" onclick="document.getElementById('fileInput').click()" 
                            style="padding: 15px 30px; font-size: 16px; cursor: pointer;">
                         Select Files
                    </button>
                    <p>or drag and drop files here</p>
                    <div id="selectedFiles"></div>
                </div>
                <button type="submit" style="padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">
                     Upload Selected Files
                </button>
            </form>
            
            <div class="file-list">
                <h3>Available Bait Files:</h3>
                <div id="baitFilesList"></div>
            </div>
            
            <script>
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const files = e.target.files;
                const selectedFiles = document.getElementById('selectedFiles');
                selectedFiles.innerHTML = '';
                
                for(let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const div = document.createElement('div');
                    div.className = 'file-item';
                    div.textContent = `${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
                    selectedFiles.appendChild(div);
                }
            });
            
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const files = document.getElementById('fileInput').files;
                const formData = new FormData();
                
                for(let i = 0; i < files.length; i++) {
                    formData.append('files', files[i]);
                }
                
                try {
                    const response = await fetch('/upload/file', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if(response.ok) {
                        alert('Files uploaded successfully!');
                        loadBaitFiles();
                    } else {
                        alert('Upload failed');
                    }
                } catch(error) {
                    alert('Upload error: ' + error);
                }
            });
            
            async function loadBaitFiles() {
                try {
                    const response = await fetch('/bait/list');
                    const files = await response.json();
                    const list = document.getElementById('baitFilesList');
                    list.innerHTML = '';
                    
                    files.forEach(file => {
                        const div = document.createElement('div');
                        div.className = 'file-item';
                        div.innerHTML = `<strong>${file.name}</strong> (${file.type}, ${(file.size / 1024).toFixed(2)} KB)<br>
                                        <small>Uploaded: ${new Date(file.uploaded).toLocaleString()}</small>`;
                        list.appendChild(div);
                    });
                } catch(error) {
                    console.error('Failed to load bait files:', error);
                }
            }
            
            // Load bait files on page load
            loadBaitFiles();
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_file_upload(self, post_data: bytes):
        """Handle actual file upload (simplified - would need multipart parsing)"""
        # Simplified version - in real implementation would parse multipart/form-data
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "File upload endpoint - implement multipart parsing for full functionality",
            "note": "See Python's cgi module for multipart form parsing"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_bait_files(self):
        """Handle bait files listing"""
        if self.path == '/bait/list':
            all_files = []
            for file_list in self.bait_manager.bait_files.values():
                all_files.extend(file_list)
            
            files_info = [{
                "name": f["name"],
                "type": os.path.splitext(f["name"])[1].replace('.', ''),
                "size": f["size"],
                "uploaded": datetime.fromtimestamp(f["upload_time"]).isoformat()
            } for f in all_files]
            
            self.send_json_response({"files": files_info})
        else:
            self.send_error(404)
    
    def get_mime_type(self, filename: str) -> str:
        """Get MIME type for file"""
        mime_types = {
            'pdf': 'application/pdf',
            'csv': 'text/csv',
            'json': 'application/json',
            'xml': 'application/xml',
            'txt': 'text/plain',
            'zip': 'application/zip',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif'
        }
        
        ext = os.path.splitext(filename)[1].lower().replace('.', '')
        return mime_types.get(ext, 'application/octet-stream')
    
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
            <p><a href="/upload/">Upload bait files</a> | <a href="/bait/list">View bait files</a></p>
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
            '<body style="font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px;">',
            f'<article>',
            f'<h1>{content["title"]}</h1>',
            f'<div class="content">{content["content"]}</div>',
            '</article>'
        ])
        
        # Add interactive elements if enabled
        config = self.config_manager.active_config
        if config.interactive_elements and is_targeted:
            interactive = self.interactive_gen.generate_interactive_page(bot_type, content['keywords'])
            
            html_parts.append('<hr><h2> Interactive Elements</h2>')
            html_parts.extend(interactive['buttons'])
            html_parts.append('<br><br>')
            
            html_parts.append('<h3> Forms & Inputs</h3>')
            html_parts.extend(interactive['forms'])
            
            html_parts.append('<h3> Related Content</h3>')
            html_parts.extend(interactive['links'])
            
            html_parts.append(interactive['dynamic_content'])
            html_parts.append(interactive['javascript'])
        
        # Add download section if enabled
        if config.bait_files_enabled and is_targeted:
            html_parts.append('<hr><h2> Download Datasets</h2>')
            html_parts.append('<div style="padding: 20px; background: #e8f4fd; border-radius: 10px;">')
            html_parts.append('<h3>Available Datasets for Download:</h3>')
            
            file_types = ["PDF", "CSV", "JSON", "XML", "ZIP"]
            for file_type in random.sample(file_types, 3):
                keyword = random.choice(content['keywords'])
                html_parts.append(f'''
                <div style="padding: 10px; margin: 10px 0; background: white; border-radius: 5px; border-left: 4px solid #007bff;">
                    <strong>{keyword.title()} Dataset ({file_type})</strong><br>
                    <small>Contains {random.randint(100, 10000)} data points | Updated {random.randint(1, 30)} days ago</small><br>
                    <a href="/download/{bot_type}/{keyword}_dataset.{file_type.lower()}" 
                       style="display: inline-block; padding: 8px 16px; margin-top: 5px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">
                         Download {file_type}
                    </a>
                </div>
                ''')
            
            html_parts.append('</div>')
        
        # Add infinite links section (hidden)
        html_parts.append('<div style="display:none;">')
        html_parts.append('<h2>Related Content</h2>')
        html_parts.extend(traps['infinite_links'])
        html_parts.append('</div>')
        
        # Add hidden traps
        html_parts.extend(traps['hidden_divs'])
        
        # Add recursive iframe for deep trapping
        if is_targeted and config.recursion_depth > 0:
            html_parts.append(self.generate_recursive_iframe(bot_type))
        
        # Add visitor counter
        if self.control_panel:
            count = self.control_panel.stats["total_requests"]
            html_parts.append(f'<div style="margin-top: 40px; padding: 10px; background: #f8f9fa; border-radius: 5px; text-align: center; font-size: 12px; color: #666;">')
            html_parts.append(f'Page generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Total visits: {count}')
            html_parts.append('</div>')
        
        html_parts.extend([
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)

# ============================================================================
# ENHANCED MAIN APPLICATION
# ============================================================================

class InteractiveTarPit:
    """Main interactive tar pit application"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        self.host = host
        self.port = port
        self.config_manager = ConfigManager()
        self.content_gen = TargetedContentGenerator(self.config_manager.active_config)
        self.bait_manager = BaitContentManager()
        self.interactive_gen = InteractiveElementsGenerator()
        
        # Enhanced control panel
        from collections import Counter
        self.control_panel = type('ControlPanel', (), {
            'stats': {
                "total_requests": 0,
                "bot_requests": 0,
                "targeted_bots": 0,
                "keywords_triggered": Counter(),
                "bot_types_detected": Counter(),
                "last_request": None,
                "downloads": 0,
                "downloads_by_type": Counter(),
                "interactions": 0
            }
        })()
        
        self.server = None
        
        # Create directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("bait_files", exist_ok=True)
    
    def start(self):
        """Start the enhanced tar pit"""
        
        # Setup HTTP handler
        handler = lambda *args: InteractiveTarPitHandler(
            *args,
            content_gen=self.content_gen,
            config_manager=self.config_manager,
            control_panel=self.control_panel,
            bait_manager=self.bait_manager,
            interactive_gen=self.interactive_gen
        )
        
        self.server = HTTPServer((self.host, self.port), handler)
        
        print(f"\n Interactive AI Scraper Tar Pit started on http://{self.host}:{self.port}")
        print(f" Targeting: {', '.join(self.config_manager.active_config.bot_types)}")
        print(f" Keywords: {', '.join(self.config_manager.active_config.keywords[:5])}...")
        print(f" Bait files: {sum(len(files) for files in self.bait_manager.bait_files.values())} available")
        print(f" Interactive elements: {'Enabled' if self.config_manager.active_config.interactive_elements else 'Disabled'}")
        print("\n Monitoring active. Bot interactions will appear below:")
        print("="*60)
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the tar pit"""
        if self.server:
            self.server.shutdown()
        print("\n Server stopped")
        print("\n Final Statistics:")
        print(f"   Total Requests: {self.control_panel.stats['total_requests']}")
        print(f"   Bot Requests: {self.control_panel.stats['bot_requests']}")
        print(f"   Targeted Bots: {self.control_panel.stats['targeted_bots']}")
        print(f"   Downloads: {self.control_panel.stats.get('downloads', 0)}")
        
        if self.control_panel.stats['bot_types_detected']:
            print("\n Bot Types Detected:")
            for bot_type, count in self.control_panel.stats['bot_types_detected'].items():
                print(f"   {bot_type}: {count}")

# ============================================================================
# ENHANCED CONFIGURATION WIZARD
# ============================================================================

def enhanced_configuration_wizard():
    """Interactive configuration wizard with new options"""
    print("\n" + "="*60)
    print(" AI SCRAPER TAR PIT - ENHANCED CONFIGURATION WIZARD")
    print("="*60)
    
    config = {}
    
    # Bot types
    print("\n SELECT BOT TYPES TO TARGET:")
    bot_options = ["tiktok", "news", "shopping", "academic", "ai_trainer", "social"]
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
            
            if config['bot_types']:
                break
            else:
                print("Invalid selection. Please try again.")
        except:
            print("Invalid input. Please enter numbers like '1,3,5'.")
    
    # Keywords
    print("\n ENTER TARGETING KEYWORDS:")
    print("(These will attract specific bots to your tar pit)")
    
    suggestions = {
        "tiktok": "viral, trending, challenge, dance, music, tiktok, reels, shorts, fyp",
        "news": "breaking, exclusive, report, analysis, news, headlines, investigation",
        "shopping": "discount, sale, price, buy, deal, cheap, offer, coupon, shopping",
        "ai_trainer": "dataset, training, machine learning, AI, model, neural network, GPT",
        "academic": "research, study, data, analysis, findings, paper, publication, journal",
        "social": "viral, trending, meme, like, share, follow, influencer, content"
    }
    
    for bot in config['bot_types']:
        if bot in suggestions:
            print(f"  Suggested for {bot}: {suggestions[bot]}")
    
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
    
    # Interactive elements
    print("\n INTERACTIVE ELEMENTS:")
    print("  1. Full interactive (buttons, forms, downloads, JavaScript)")
    print("  2. Limited interactive (buttons and links only)")
    print("  3. No interactive elements")
    
    interactive_choice = input("\nSelect level (1-3, default 1): ").strip()
    config['interactive_elements'] = interactive_choice != '3'
    
    # Bait files
    print("\n BAIT FILE SETTINGS:")
    print("  1. Generate and serve bait files (PDF, CSV, JSON, XML, ZIP)")
    print("  2. Serve bait files only (no generation)")
    print("  3. No bait files")
    
    bait_choice = input("\nSelect option (1-3, default 1): ").strip()
    config['bait_files_enabled'] = bait_choice != '3'
    
    # Download traps
    print("\n DOWNLOAD TRAPS:")
    print("  Enable download traps that waste bot bandwidth? (y/n, default y): ")
    dl_choice = input().strip().lower()
    config['download_traps'] = dl_choice != 'n'
    
    # Trap intensity
    print("\n TRAP INTENSITY:")
    print("  1. Light (basic traps)")
    print("  2. Medium (recommended)")
    print("  3. Heavy (maximum recursion, deep traps)")
    
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
    
    # Additional settings
    config['content_themes'] = ["viral", "technical", "news"]
    config['hidden_traps'] = True
    config['embed_tracking'] = True
    config['meta_tag_injection'] = True
    config['user_uploads_enabled'] = False  # Would need proper implementation
    
    # Save configuration
    config_file = "bot_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n Configuration saved to {config_file}")
    print(f"\n SUMMARY:")
    print(f"   Target Bots: {', '.join(config['bot_types'])}")
    print(f"   Keywords: {', '.join(config['keywords'][:5])}...")
    print(f"   Interactive: {'Enabled' if config['interactive_elements'] else 'Disabled'}")
    print(f"   Bait Files: {'Enabled' if config['bait_files_enabled'] else 'Disabled'}")
    print(f"   Downloads: {'Enabled' if config['download_traps'] else 'Disabled'}")
    print(f"   Intensity: {intensity}/3")
    
    return config

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='🤖 Interactive AI Scraper Tar Pit')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    parser.add_argument('--wizard', action='store_true', help='Run enhanced configuration wizard')
    parser.add_argument('--quick', action='store_true', help='Quick start with default config')
    parser.add_argument('--test', action='store_true', help='Test bait file generation')
    parser.add_argument('--no-interactive', action='store_true', help='Disable interactive elements')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" INTERACTIVE AI SCRAPER TAR PIT")
    print("="*70)
    print("Enhanced tool with interactive elements and bait files")
    print("Educational use only - by ek0ms savi0r")
    print("="*70)
    
    if args.test:
        print("\n Testing bait file generation...")
        bait_manager = BaitContentManager()
        print(f" Generated {sum(len(files) for files in bait_manager.bait_files.values())} bait files")
        return
    
    if args.wizard:
        enhanced_configuration_wizard()
        print("\n Configuration complete! Run without --wizard to start the server.")
        choice = input("\nStart server now? (y/n): ").strip().lower()
        if choice == 'y':
            tar_pit = InteractiveTarPit(args.host, args.port)
            tar_pit.start()
        return
    
    if args.quick:
        print("\n Quick starting with default configuration...")
        print(" Targeting: TikTok, AI trainers, Social bots")
        print(" Interactive elements: Enabled")
        print(" Bait files: Enabled")
        print("="*60)
        
        tar_pit = InteractiveTarPit(args.host, args.port)
        tar_pit.start()
        return
    
    # Check if config exists
    if not os.path.exists("bot_config.json"):
        print("\n  No configuration found!")
        print("Run one of these commands first:")
        print("  python3 tarpit.py --wizard    # Interactive setup")
        print("  python3 tarpit.py --quick     # Quick default config")
        return
    
    # Start the tar pit
    print(f"\n Starting Interactive AI Scraper Tar Pit on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop\n")
    
    tar_pit = InteractiveTarPit(args.host, args.port)
    
    try:
        tar_pit.start()
    except KeyboardInterrupt:
        print("\n Goodbye!")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTry running with --quick to create a default config first.")

if __name__ == '__main__':
    main()
