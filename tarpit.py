#!/usr/bin/env python3
"""
Enhanced AI Scraper Tar Pit with Interactive Elements and ngrok Integration
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
import mimetypes
import zipfile
import io
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
import subprocess
import requests
import atexit
import socket
from pathlib import Path

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
# NGrok Integration - IMPROVED VERSION
# ============================================================================

class NgrokManager:
    """Manage ngrok tunneling for public access"""
    
    def __init__(self, auth_token: str = None, region: str = "us"):
        self.auth_token = auth_token
        self.region = region
        self.process = None
        self.public_url = None
        self.api_url = "http://localhost:4040/api"
        self.tunnel_start_time = None
        self.setup_ngrok_config()
    
    def setup_ngrok_config(self):
        """Setup ngrok configuration file"""
        try:
            # First, check if ngrok is installed and working
            if not self.is_ngrok_installed():
                logger.error("ngrok is not installed or not in PATH")
                return False
            
            # Check if auth token is valid
            if self.auth_token:
                # Update config with auth token
                config_cmd = ["ngrok", "config", "add-authtoken", self.auth_token]
                result = subprocess.run(config_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("ngrok auth token configured successfully")
                else:
                    logger.error(f"Failed to configure ngrok auth token: {result.stderr}")
            
            return True
        except Exception as e:
            logger.error(f"Error setting up ngrok config: {e}")
            return False
    
    def start_tunnel(self, port: int = 8080, protocol: str = "http") -> Optional[str]:
        """Start ngrok tunnel and return public URL"""
        try:
            # First kill any existing ngrok processes
            self.kill_existing_ngrok()
            
            # Build command with improved parameters
            cmd = ["ngrok", protocol, str(port)]
            
            # Add region if specified
            if self.region:
                cmd.extend(["--region", self.region])
            
            # Add additional options for better stability
            cmd.extend([
                "--log", "stdout",
                "--log-format", "json",
                "--log-level", "info"
            ])
            
            logger.info(f"Starting ngrok tunnel on port {port}...")
            print(f"Starting ngrok: ngrok http {port} --region {self.region}")
            
            # Start ngrok process with better error handling
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            self.tunnel_start_time = time.time()
            
            # Start a thread to read output
            threading.Thread(target=self.read_ngrok_output, daemon=True).start()
            
            # Give ngrok time to start
            print(f"Waiting for ngrok to initialize (10 seconds)...")
            for i in range(10):
                time.sleep(1)
                print(f"   {i+1}/10 seconds", end='\r')
            
            # Try to get public URL
            self.public_url = self.get_public_url_with_retry()
            
            if self.public_url:
                print(f"\nngrok tunnel established!")
                print(f"Public URL: {self.public_url}")
                print(f"ngrok dashboard: http://localhost:4040")
                logger.info(f"ngrok tunnel established: {self.public_url}")
                
                # Start monitoring thread
                threading.Thread(target=self.monitor_tunnel, daemon=True).start()
                return self.public_url
            else:
                print(f"\nFailed to get ngrok public URL")
                # Check process output
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    logger.error(f"ngrok process failed: {stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            print(f"Error starting ngrok: {e}")
            return None
    
    def read_ngrok_output(self):
        """Read ngrok output for debugging"""
        if self.process:
            for line in iter(self.process.stdout.readline, ''):
                if line.strip():
                    try:
                        log_data = json.loads(line.strip())
                        if 'msg' in log_data and 'url' in log_data['msg']:
                            url_match = re.search(r'(https?://[^\s]+)', log_data['msg'])
                            if url_match:
                                self.public_url = url_match.group(0)
                                print(f"Detected URL in logs: {self.public_url}")
                    except json.JSONDecodeError:
                        # Not JSON, just print as regular output
                        if "started tunnel" in line.lower() or "url=" in line.lower():
                            print(f"ngrok: {line.strip()}")
    
    def get_public_url_with_retry(self, max_retries: int = 15) -> Optional[str]:
        """Get public URL from ngrok API with retries"""
        print(f"Looking for ngrok public URL...")
        
        for attempt in range(max_retries):
            try:
                # Try to get from API
                response = requests.get(f"{self.api_url}/tunnels", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get('tunnels', [])
                    
                    if tunnels:
                        for tunnel in tunnels:
                            if tunnel.get('proto') in ['http', 'https']:
                                public_url = tunnel.get('public_url')
                                if public_url:
                                    print(f"Found public URL after {attempt+1} attempts")
                                    return public_url
                
                # Also try the simpler status endpoint
                try:
                    status_resp = requests.get(f"{self.api_url}", timeout=3)
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        if 'tunnels' in status_data:
                            for tunnel in status_data['tunnels']:
                                if tunnel.get('public_url'):
                                    return tunnel.get('public_url')
                except:
                    pass
                
                time.sleep(1)
                print(f"   Attempt {attempt+1}/{max_retries}...", end='\r')
                
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        print(f"\nCould not get URL from API, trying alternative methods...")
        
        # Alternative method: check ngrok config directly
        try:
            result = subprocess.run(
                ["ngrok", "tunnel", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                tunnels = json.loads(result.stdout)
                for tunnel in tunnels:
                    if 'public_url' in tunnel:
                        return tunnel['public_url']
        except:
            pass
        
        return None
    
    def monitor_tunnel(self):
        """Monitor ngrok tunnel health"""
        check_interval = 30  # Check every 30 seconds
        
        while self.process and self.process.poll() is None:
            time.sleep(check_interval)
            
            # Check if tunnel is still responding
            if not self.is_tunnel_alive():
                logger.warning("ngrok tunnel appears to be down")
                print("ngrok tunnel appears down, attempting to restart...")
                
                # Restart tunnel
                current_port = 8080  # Default, should track actual port
                self.stop()
                time.sleep(2)
                self.start_tunnel(current_port)
    
    def is_tunnel_alive(self) -> bool:
        """Check if tunnel is alive by querying ngrok API"""
        try:
            response = requests.get(f"{self.api_url}/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return bool(data.get('tunnels'))
        except:
            return False
        return False
    
    def kill_existing_ngrok(self):
        """Kill any existing ngrok processes"""
        try:
            # Kill ngrok processes
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"], 
                             capture_output=True)
            else:
                subprocess.run(["pkill", "-f", "ngrok"], 
                             capture_output=True)
                subprocess.run(["pkill", "-9", "-f", "ngrok"], 
                             capture_output=True)
            time.sleep(2)
        except:
            pass
    
    def stop(self):
        """Stop ngrok tunnel"""
        if self.process:
            try:
                print("Stopping ngrok tunnel...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                logger.info("ngrok tunnel stopped")
                print("ngrok tunnel stopped")
            except Exception as e:
                logger.error(f"Error stopping ngrok: {e}")
            finally:
                self.process = None
                self.public_url = None
        
        # Also kill any orphaned ngrok processes
        self.kill_existing_ngrok()
    
    def is_ngrok_installed(self) -> bool:
        """Check if ngrok is installed"""
        try:
            # First try ngrok version
            result = subprocess.run(["ngrok", "--version"], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=2)
            if result.returncode == 0:
                version_match = re.search(r'ngrok\s+version\s+([\d.]+)', result.stdout)
                if version_match:
                    print(f"ngrok version {version_match.group(1)} detected")
                    return True
            
            # Try alternative check
            result = subprocess.run(["which", "ngrok"], 
                                  capture_output=True, 
                                  text=True)
            if result.returncode == 0:
                print(f"ngrok found at {result.stdout.strip()}")
                return True
            
            # Check common installation locations
            common_paths = [
                "/usr/local/bin/ngrok",
                "/usr/bin/ngrok",
                os.path.expanduser("~/bin/ngrok"),
                os.path.expanduser("~/.local/bin/ngrok")
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    print(f"ngrok found at {path}")
                    return True
            
            return False
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def get_tunnel_info(self) -> Dict:
        """Get detailed tunnel information"""
        try:
            response = requests.get(f"{self.api_url}/tunnels", timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get tunnel info: {e}")
        return {}

# ============================================================================
# TARGETED CONTENT GENERATOR
# ============================================================================

class TargetedContentGenerator:
    """Generate content targeted to specific bot interests"""
    
    def __init__(self, config):
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
            "tiktok": ["View Video", "Like Content", "Share Now", "Play Sound", "Trending"],
            "news": ["Read More", "Subscribe", "View Stats", "Analysis", "Latest"],
            "shopping": ["Add to Cart", "Buy Now", "Add to Wishlist", "View Price", "Get Deal"],
            "ai_trainer": ["Download Dataset", "Train Model", "View Results", "Configure", "Deploy"],
            "academic": ["Read Paper", "Cite This", "Abstract", "Methodology", "Download PDF"]
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
        
        submit_action = f"document.getElementById('{form_id}').innerHTML='<p style=\"color:green;\">Thank you for submitting! Downloading {random.choice(keywords)} data...</p>'; setTimeout(() => window.location.href='/download/trap/{bot_type}.zip', 2000);"
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
            
            link_html = f'<a href="{url}" class="download-link" data-bot="{bot_type}" data-filetype="{file_type}" style="color:#28a745;text-decoration:none;margin:0 10px;padding:8px 12px;border-radius:5px;background:#d4edda;border:1px solid #c3e6cb;display:inline-block;">Download {keyword.title()} Data ({file_type.upper()})</a>'
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
# UTILITY FUNCTIONS
# ============================================================================

def is_port_in_use(port: int, host: str = '0.0.0.0') -> bool:
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def find_available_port(start_port: int = 8080, max_attempts: int = 100) -> Optional[int]:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

# ============================================================================
# ENHANCED REQUEST HANDLER WITH INTERACTIVE ELEMENTS - FIXED VERSION
# ============================================================================

class InteractiveTarPitHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler with interactive elements and bait files - FIXED"""
    
    def __init__(self, *args, 
                 content_gen=None, 
                 config_manager=None, 
                 control_panel=None,
                 bait_manager=None,
                 interactive_gen=None,
                 ngrok_manager=None,
                 **kwargs):
        self.content_gen = content_gen
        self.config_manager = config_manager
        self.control_panel = control_panel
        self.bait_manager = bait_manager
        self.interactive_gen = interactive_gen
        self.ngrok_manager = ngrok_manager
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to suppress default logging"""
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        start_time = time.time()
        
        # Update statistics
        if self.control_panel:
            self.control_panel.stats["total_requests"] += 1
        
        # Detect bot type
        user_agent = self.headers.get('User-Agent', '')
        bot_type = self.config_manager.detect_bot_type(user_agent, self.path)
        
        # Check if it's a bot (anything not "generic" is a bot)
        is_bot = bot_type != "generic"
        
        if is_bot and self.control_panel:
            self.control_panel.stats["bot_requests"] += 1
            self.control_panel.stats["bot_types_detected"][bot_type] += 1
            self.control_panel.stats["last_request"] = f"{bot_type} at {datetime.now().strftime('%H:%M:%S')}"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_type.upper()} detected - {self.path}")
        
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
        elif self.path == '/status':
            self.handle_status_page()
            return
        elif self.path == '/ngrok':
            self.handle_ngrok_info()
            return
        elif self.path == '/test':
            self.handle_test_page()
            return
        elif self.path.startswith('/trap/'):
            self.handle_trap_page(bot_type, is_bot)
            return
        elif self.path.startswith('/data/'):
            self.handle_data_page(bot_type, is_bot)
            return
        
        # ROOT PATH - Show different content based on visitor type
        if self.path == '/' or self.path == '':
            if is_bot:
                # Bots get enticing trap content
                self.handle_bot_landing_page(bot_type)
            else:
                # Humans get simple research portal
                self.handle_human_landing_page()
            return
        
        # All other non-special paths - show 404
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"""
        <!DOCTYPE html>
        <html>
        <head><title>404 - Page Not Found</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>404 - Page Not Found</h1>
            <p>The requested path <code>{self.path}</code> does not exist.</p>
            <p><a href="/">Return to Home</a></p>
        </body>
        </html>
        """.encode('utf-8'))
    
    def handle_bot_landing_page(self, bot_type: str):
        """Handle landing page for bots - rich, enticing content"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Serving BOT landing page to {bot_type}")
        
        # Generate rich content for this bot type
        content = self.content_gen.generate_targeted_content(bot_type)
        
        # Check if this is a targeted bot type
        is_targeted = bot_type in self.config_manager.active_config.bot_types
        
        if is_targeted and self.control_panel:
            self.control_panel.stats["targeted_bots"] += 1
        
        # Generate HTML with traps
        html = self.wrap_bot_content_with_traps(content, bot_type, is_targeted)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def wrap_bot_content_with_traps(self, content: Dict, bot_type: str, is_targeted: bool) -> str:
        """Wrap bot content with traps - SIMPLIFIED VERSION"""
        
        # Create a rich, enticing page for bots
        keywords = content['keywords']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{content['title']}</title>
            <meta name="description" content="Exclusive {', '.join(keywords[:3])} content available for download">
            <meta name="keywords" content="{', '.join(keywords)}">
            <meta name="robots" content="index, follow">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .content-section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
                .download-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
                .download-card {{ padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .download-btn {{ display: block; padding: 12px; background: #28a745; color: white; text-align: center; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
                .hidden-trap {{ display: none; }}
            </style>
        </head>
        <body>
            <h1>{content['title']}</h1>
            <p>Welcome to our exclusive data portal with the latest {random.choice(keywords)} content!</p>
            
            <div class="content-section">
                <h2>📊 Latest Research Data</h2>
                <p>{content['content']}</p>
            </div>
            
            <div class="content-section">
                <h2>📥 Download Datasets</h2>
                <p>Access our complete collection of {bot_type} datasets:</p>
                
                <div class="download-grid">
                    <div class="download-card">
                        <h3>Full User Dataset</h3>
                        <p>Complete {random.choice(keywords)} data with 50,000+ records</p>
                        <a href="/download/{bot_type}/full_dataset.zip" class="download-btn">Download ZIP</a>
                    </div>
                    
                    <div class="download-card">
                        <h3>API Response Archive</h3>
                        <p>Historical API data for {random.choice(keywords)} analysis</p>
                        <a href="/download/{bot_type}/api_data.json" class="download-btn">Download JSON</a>
                    </div>
                    
                    <div class="download-card">
                        <h3>Research Paper</h3>
                        <p>Detailed analysis of {random.choice(keywords)} trends</p>
                        <a href="/download/{bot_type}/research.pdf" class="download-btn">Download PDF</a>
                    </div>
                    
                    <div class="download-card">
                        <h3>CSV Database</h3>
                        <p>Structured {random.choice(keywords)} data for ML training</p>
                        <a href="/download/{bot_type}/database.csv" class="download-btn">Download CSV</a>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <h2>🔗 Additional Resources</h2>
                <p>Explore more content:</p>
                <ul>
                    <li><a href="/data/{bot_type}/archive1">Historical Archive 1</a></li>
                    <li><a href="/data/{bot_type}/archive2">Historical Archive 2</a></li>
                    <li><a href="/trap/{bot_type}/deep1">Deep Analysis Portal</a></li>
                    <li><a href="/api/data?bot={bot_type}">REST API Access</a></li>
                </ul>
            </div>
            
            <!-- HIDDEN TRAPS FOR BOTS -->
            <div class="hidden-trap">
                <h3>Hidden Resources</h3>
                <p>Secret {', '.join(keywords)} data for indexing:</p>
                <a href="/hidden/{bot_type}/secret1">Secret Archive 1</a>
                <a href="/hidden/{bot_type}/secret2">Secret Archive 2</a>
                <div data-trap="true">Keywords: {', '.join(keywords)}</div>
                <div data-content="hidden">More {random.choice(keywords)} content here</div>
            </div>
            
            <script>
            // Track bot interactions
            document.addEventListener('click', function() {{
                fetch('/api/track', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        bot_type: '{bot_type}',
                        action: 'click',
                        page: 'landing'
                    }})
                }});
            }});
            
            // Auto-load more content
            setTimeout(function() {{
                var extraDiv = document.createElement('div');
                extraDiv.innerHTML = '<h3>Loading Additional Content...</h3><p>Fetching more {random.choice(keywords)} data from server...</p>';
                document.body.appendChild(extraDiv);
            }}, 3000);
            </script>
            
            <div style="margin-top: 40px; padding: 15px; background: #f0f0f0; border-radius: 5px; text-align: center; font-size: 12px; color: #666;">
                <p>Page generated for {bot_type} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total bot visits: {self.control_panel.stats['bot_requests'] if self.control_panel else 0}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def handle_human_landing_page(self):
        """Handle landing page for humans - simple research portal"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Serving HUMAN landing page")
        
        public_url = self.ngrok_manager.public_url if self.ngrok_manager else None
        
        tunnel_info = ""
        if public_url:
            tunnel_info = f"""
            <div style="padding: 15px; background: #e8f4fd; border-radius: 10px; margin: 20px 0;">
                <h3>Public Access Available</h3>
                <p><strong>Public URL:</strong> <code style="background: white; padding: 5px; border-radius: 3px;">{public_url}</code></p>
                <p>Share this URL to access from any device or network.</p>
                <p><a href="{public_url}" target="_blank">Open public URL</a></p>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Research Portal</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Academic Research Portal</h1>
            <p>This site is used for academic research on web traffic patterns and bot behavior analysis.</p>
            
            <div class="warning">
                <strong>⚠️ Warning:</strong> This site contains algorithmically generated content designed to study web scraping behavior. 
                All content is synthetic and for research purposes only.
            </div>
            
            {tunnel_info}
            
            <hr>
            
            <h3>Research Areas:</h3>
            <ul>
                <li>Web scraping bot detection and analysis</li>
                <li>Bot behavior patterns and classification</li>
                <li>Algorithmic content generation for research</li>
                <li>Traffic pattern analysis</li>
            </ul>
            
            <h3>Administration:</h3>
            <p>
                <a href="/status">View Research Dashboard</a> | 
                <a href="/upload/">Upload Research Files</a> | 
                <a href="/test">Test Interface</a> |
                <a href="/ngrok">Network Configuration</a>
            </p>
            
            <hr>
            <p><small>Educational use only. All access is logged for research purposes. Contact research team for more information.</small></p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_trap_page(self, bot_type: str, is_bot: bool):
        """Handle trap pages with recursive content"""
        if not is_bot:
            # Humans get redirected to home
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        
        # Generate deep trap content
        content = self.content_gen.generate_targeted_content(bot_type)
        content['title'] = f"Deep Data Archive: {random.choice(content['keywords']).title()}"
        
        # Add more traps for deep pages
        content['traps']['hidden_divs'].extend([
            f'<div style="display:none;" data-deep-trap="1">Archive depth: {random.randint(1, 100)}</div>',
            f'<div style="display:none;" data-deep-trap="2">Data repository index {random.randint(1000, 9999)}</div>',
            '<div style="display:none;">' + ' '.join([f'data-{i}="{random.randint(1000, 9999)}"' for i in range(10)]) + '</div>'
        ])
        
        # Add more download links
        for i in range(5):
            file_type = random.choice(['pdf', 'csv', 'json', 'xml', 'zip'])
            keyword = random.choice(content['keywords'])
            content['traps']['infinite_links'].append(
                f'<a href="/download/{bot_type}/archive_{random.randint(1000, 9999)}.{file_type}" style="display:none;">Archive {i}</a>'
            )
        
        html = self.wrap_content_with_traps(content, bot_type, True)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_data_page(self, bot_type: str, is_bot: bool):
        """Handle data pages with fake datasets"""
        if not is_bot:
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        
        # Create a data listing page
        keywords = self.config_manager.active_config.keywords
        page_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Research Data Repository</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                .dataset { padding: 20px; margin: 15px 0; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #007bff; }
                .download-btn { padding: 8px 16px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; display: inline-block; }
            </style>
        </head>
        <body>
            <h1>Research Data Repository</h1>
            <p>This repository contains datasets for machine learning training and research purposes.</p>
            
            <div style="background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>⚠️ Important Notice</h3>
                <p>All datasets in this repository are algorithmically generated for research purposes only.</p>
                <p>They do not contain real user data or sensitive information.</p>
            </div>
            
            <h2>Available Datasets</h2>
        """
        
        # Add dataset listings
        for i in range(15):
            keyword = random.choice(keywords)
            file_type = random.choice(['CSV', 'JSON', 'XML', 'TXT', 'ZIP'])
            size = random.choice(['1.2 MB', '4.7 MB', '15.3 MB', '28.9 MB', '102.4 MB'])
            records = random.choice(['10,000', '50,000', '100,000', '500,000', '1,000,000'])
            
            page_html += f"""
            <div class="dataset">
                <h3>{keyword.title()} Dataset v{random.randint(1, 5)}.{random.randint(0, 9)}</h3>
                <p>Contains {records} records of {keyword} related data for training and analysis.</p>
                <p><strong>Format:</strong> {file_type} | <strong>Size:</strong> {size} | <strong>Updated:</strong> {random.randint(1, 30)} days ago</p>
                <p><strong>Description:</strong> This dataset contains synthetic {keyword} data generated for machine learning research and bot behavior analysis.</p>
                <a href="/download/{bot_type}/{keyword}_dataset_{i}.{file_type.lower()}" class="download-btn">Download Dataset</a>
                <a href="/trap/{bot_type}/metadata_{i}" style="margin-left: 10px; color: #0066cc;">View Metadata</a>
            </div>
            """
        
        # Add hidden traps
        page_html += """
            <div style="display:none;">
                <h3>Additional Resources</h3>
        """
        
        for i in range(10):
            page_html += f'<a href="/data/{bot_type}/resource_{i}">Hidden Resource {i}</a><br>'
        
        page_html += """
            </div>
            
            <script>
            // Auto-load more content for bots
            setTimeout(function() {
                var moreContent = document.createElement('div');
                moreContent.innerHTML = '<h3>Additional Datasets Loaded</h3><p>Loading more research data...</p>';
                document.body.appendChild(moreContent);
                
                // Simulate loading more datasets
                setTimeout(function() {
                    moreContent.innerHTML = '<h3>Additional Datasets</h3><p>25 more datasets loaded from archive. <a href="/data/' + bot_type + '/page2">View Next Page</a></p>';
                }, 2000);
            }, 3000);
            
            // Track bot interaction
            document.addEventListener('click', function() {
                fetch('/api/analytics/track', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        event: 'dataset_browse',
                        bot_type: '""" + bot_type + """',
                        timestamp: new Date().toISOString()
                    })
                });
            });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(page_html.encode('utf-8'))
    
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
                <h1>Thank You!</h1>
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_type.upper()} downloaded {filename}")
    
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
        
        if api_path == 'status':
            self.send_status_response()
        elif api_path == 'ngrok':
            self.send_ngrok_response()
        elif api_path.startswith('data'):
            self.send_api_response(bot_type)
        elif api_path.startswith('analytics'):
            self.send_analytics_response(bot_type)
        else:
            self.send_json_response({
                "error": "Invalid API endpoint",
                "available_endpoints": ["/api/data", "/api/analytics", "/api/status", "/api/ngrok"],
                "timestamp": datetime.now().isoformat()
            })
    
    def send_status_response(self):
        """Send status response"""
        stats = self.control_panel.stats if self.control_panel else {}
        response = {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total_requests": stats.get("total_requests", 0),
                "bot_requests": stats.get("bot_requests", 0),
                "targeted_bots": stats.get("targeted_bots", 0),
                "downloads": stats.get("downloads", 0),
                "bot_types_detected": dict(stats.get("bot_types_detected", {})),
                "last_request": stats.get("last_request", "None")
            }
        }
        
        self.send_json_response(response)
    
    def send_ngrok_response(self):
        """Send ngrok tunnel information"""
        if self.ngrok_manager and self.ngrok_manager.public_url:
            response = {
                "active": True,
                "public_url": self.ngrok_manager.public_url,
                "local_url": f"http://localhost:{self.server.server_port}",
                "protocol": "http",
                "started": datetime.fromtimestamp(self.ngrok_manager.tunnel_start_time).isoformat() if self.ngrok_manager.tunnel_start_time else None
            }
        else:
            response = {
                "active": False,
                "message": "ngrok tunnel is not active"
            }
        
        self.send_json_response(response)
    
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
                    transition: all 0.3s;
                }
                .upload-area:hover { 
                    border-color: #007bff; 
                    background: #f0f8ff; 
                }
                .file-list { margin-top: 30px; }
                .file-item { 
                    padding: 10px; 
                    margin: 5px 0; 
                    background: #f8f9fa; 
                    border-radius: 5px;
                }
                .remove-btn {
                    background: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    cursor: pointer;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>Upload Bait Files</h1>
            <p>Upload files that will be served to bots as bait.</p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="dropArea">
                    <input type="file" id="fileInput" name="file" multiple style="display: none;">
                    <button type="button" onclick="document.getElementById('fileInput').click()" 
                            style="padding: 15px 30px; font-size: 16px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px;">
                        Select Files
                    </button>
                    <p style="margin-top: 10px; color: #666;">or drag and drop files here</p>
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
            document.getElementById('fileInput').addEventListener('change', updateFileList);
            document.getElementById('uploadForm').addEventListener('submit', handleFormSubmit);
            
            // Drag and drop functionality
            const dropArea = document.getElementById('dropArea');
            dropArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropArea.style.borderColor = '#007bff';
                dropArea.style.background = '#f0f8ff';
            });
            
            dropArea.addEventListener('dragleave', (e) => {
                dropArea.style.borderColor = '#ccc';
                dropArea.style.background = '';
            });
            
            dropArea.addEventListener('drop', (e) => {
                e.preventDefault();
                dropArea.style.borderColor = '#ccc';
                dropArea.style.background = '';
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    document.getElementById('fileInput').files = files;
                    updateFileList();
                }
            });
            
            // Click to upload
            dropArea.addEventListener('click', () => {
                document.getElementById('fileInput').click();
            });
            
            function updateFileList() {
                const files = document.getElementById('fileInput').files;
                const selectedFiles = document.getElementById('selectedFiles');
                selectedFiles.innerHTML = '';
                
                if (files.length === 0) {
                    selectedFiles.innerHTML = '<p style="color:#666; font-style:italic;">No files selected</p>';
                    return;
                }
                
                const list = document.createElement('ul');
                list.style.listStyle = 'none';
                list.style.padding = '0';
                
                for(let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const li = document.createElement('li');
                    li.className = 'file-item';
                    li.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center; margin: 5px 0;">
                            <div>
                                <strong>${file.name}</strong>
                                <br>
                                <small>${(file.size / 1024).toFixed(2)} KB • ${file.type || 'Unknown type'}</small>
                            </div>
                            <button type="button" onclick="removeFile(${i})" class="remove-btn">×</button>
                        </div>
                    `;
                    list.appendChild(li);
                }
                
                selectedFiles.appendChild(list);
            }
            
            function removeFile(index) {
                const fileInput = document.getElementById('fileInput');
                const files = Array.from(fileInput.files);
                files.splice(index, 1);
                
                // Create new FileList
                const dataTransfer = new DataTransfer();
                files.forEach(file => dataTransfer.items.add(file));
                fileInput.files = dataTransfer.files;
                
                updateFileList();
            }
            
            async function handleFormSubmit(e) {
                e.preventDefault();
                const files = document.getElementById('fileInput').files;
                
                if (files.length === 0) {
                    alert('Please select at least one file to upload.');
                    return;
                }
                
                const formData = new FormData();
                for(let i = 0; i < files.length; i++) {
                    formData.append('files', files[i]);
                }
                
                try {
                    const response = await fetch('/upload/file', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if(response.ok) {
                        alert(`Successfully uploaded ${result.files ? result.files.length : 0} files!`);
                        loadBaitFiles();
                        // Clear file input
                        document.getElementById('fileInput').value = '';
                        document.getElementById('selectedFiles').innerHTML = '<p style="color:#666; font-style:italic;">No files selected</p>';
                    } else {
                        alert(`Upload failed: ${result.message || 'Unknown error'}`);
                    }
                } catch(error) {
                    alert('Upload error: ' + error);
                }
            }
            
            async function loadBaitFiles() {
                try {
                    const response = await fetch('/bait/list');
                    const data = await response.json();
                    const list = document.getElementById('baitFilesList');
                    list.innerHTML = '';
                    
                    if (data.files && data.files.length > 0) {
                        data.files.forEach(file => {
                            const div = document.createElement('div');
                            div.className = 'file-item';
                            div.innerHTML = `
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong>${file.name}</strong>
                                        <br>
                                        <small>${file.type.toUpperCase()} • ${(file.size / 1024).toFixed(2)} KB</small>
                                        <br>
                                        <small style="color: #666;">Uploaded: ${new Date(file.uploaded).toLocaleString()}</small>
                                    </div>
                                    <div>
                                        <a href="/download/bait/${file.name}" 
                                           style="padding: 5px 10px; background: #28a745; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">
                                            Download
                                        </a>
                                    </div>
                                </div>
                            `;
                            list.appendChild(div);
                        });
                    } else {
                        list.innerHTML = '<p style="color:#666; font-style:italic;">No bait files uploaded yet.</p>';
                    }
                } catch(error) {
                    console.error('Failed to load bait files:', error);
                    document.getElementById('baitFilesList').innerHTML = '<p style="color:#dc3545;">Error loading bait files list.</p>';
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
        """Handle actual file upload with proper multipart parsing"""
        try:
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                self.send_error(400, "Invalid content type")
                return
            
            # Parse the boundary from Content-Type
            boundary = None
            for part in content_type.split(';'):
                if 'boundary=' in part:
                    boundary = '--' + part.split('boundary=')[1].strip()
                    break
            
            if not boundary:
                self.send_error(400, "No boundary found")
                return
            
            # Parse multipart data
            files = []
            parts = post_data.split(boundary.encode())
            
            for part in parts:
                if not part or b'--\r\n' in part:  # Skip empty parts or end boundary
                    continue
                
                # Parse headers and content
                header_end = part.find(b'\r\n\r\n')
                if header_end == -1:
                    continue
                    
                headers_raw = part[:header_end]
                body = part[header_end + 4:-2]  # Skip \r\n\r\n and trailing \r\n
                
                # Parse headers
                headers = {}
                for line in headers_raw.split(b'\r\n'):
                    if b': ' in line:
                        key, value = line.split(b': ', 1)
                        headers[key.decode().lower()] = value.decode()
                
                # Check if this part contains a file
                if 'content-disposition' in headers:
                    cd = headers['content-disposition']
                    if 'filename=' in cd:
                        # Extract filename
                        filename_match = re.search(r'filename="([^"]+)"', cd)
                        if filename_match:
                            filename = filename_match.group(1)
                            
                            # Save the file
                            filepath = os.path.join(self.bait_manager.uploaded_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(body)
                            
                            # Add to bait manager
                            ext = os.path.splitext(filename)[1].lower().replace('.', '')
                            if ext in self.bait_manager.bait_files:
                                self.bait_manager.bait_files[ext].append({
                                    "name": filename,
                                    "path": filepath,
                                    "size": len(body),
                                    "upload_time": time.time()
                                })
                            
                            files.append({
                                "name": filename,
                                "size": len(body),
                                "saved": True
                            })
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "success",
                "message": f"Uploaded {len(files)} files",
                "files": files
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
            logger.info(f"Uploaded {len(files)} bait files")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Uploaded {len(files)} bait files")
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            self.send_error(500, f"Upload failed: {str(e)}")
    
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
    
    def handle_status_page(self):
        """Show status page with statistics"""
        public_url = self.ngrok_manager.public_url if self.ngrok_manager else None
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tar Pit Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #007bff; }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
                .bot-list {{ margin-top: 20px; }}
                .bot-item {{ padding: 10px; margin: 5px 0; background: #e8f4fd; border-radius: 5px; }}
                .tunnel-info {{ background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .status-badge {{ display: inline-block; padding: 5px 10px; border-radius: 20px; color: white; font-weight: bold; }}
                .status-active {{ background: #28a745; }}
                .status-inactive {{ background: #dc3545; }}
                .url-box {{ background: white; padding: 10px; border-radius: 5px; font-family: monospace; word-break: break-all; }}
            </style>
        </head>
        <body>
            <h1>Tar Pit Status Dashboard</h1>
            <p>Real-time statistics and monitoring</p>
            
            <div class="tunnel-info">
                <h2>Tunnel Status</h2>
                {"<p><strong>Public URL:</strong> <div class='url-box'>" + public_url + "</div></p>" if public_url else "<p><span class='status-badge status-inactive'>LOCAL ONLY</span> ngrok tunnel is not active</p>"}
                <p><strong>Local URL:</strong> http://localhost:{self.server.server_port}</p>
                {"<p><a href='" + public_url + "' target='_blank'>Open public URL</a></p>" if public_url else ""}
                <p><a href="http://localhost:4040" target="_blank">ngrok dashboard</a></p>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <!-- Stats will be loaded via JavaScript -->
            </div>
            
            <div class="bot-list" id="botList">
                <h3>Bot Activity</h3>
                <!-- Bot list will be loaded here -->
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #f0f0f0; border-radius: 10px;">
                <h3>Quick Links</h3>
                <p><a href="/">Home</a> | <a href="/test">Test Page</a> | <a href="/upload/">Upload Files</a> | <a href="/ngrok">ngrok Info</a></p>
                <p><a href="/download/test/test.zip">Test Download</a> | <a href="/api/data">API Test</a></p>
            </div>
            
            <script>
            async function loadStats() {{
                try {{
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    // Update stats grid
                    const statsGrid = document.getElementById('statsGrid');
                    statsGrid.innerHTML = '';
                    
                    const stats = [
                        {{ label: 'Total Requests', value: data.stats.total_requests, icon: '' }},
                        {{ label: 'Bot Requests', value: data.stats.bot_requests, icon: '' }},
                        {{ label: 'Downloads', value: data.stats.downloads || 0, icon: '' }},
                        {{ label: 'Targeted Bots', value: data.stats.targeted_bots || 0, icon: '' }},
                        {{ label: 'Unique Bot Types', value: Object.keys(data.stats.bot_types_detected || {{}}).length, icon: '' }},
                        {{ label: 'Last Activity', value: data.stats.last_request || 'None', icon: '' }}
                    ];
                    
                    stats.forEach(stat => {{
                        const card = document.createElement('div');
                        card.className = 'stat-card';
                        card.innerHTML = `
                            <div class="stat-value">${{stat.value}}</div>
                            <div class="stat-label">${{stat.label}}</div>
                        `;
                        statsGrid.appendChild(card);
                    }});
                    
                    // Update bot list
                    const botList = document.getElementById('botList');
                    if (data.stats.bot_types_detected) {{
                        let botHTML = '<h3>Bot Activity by Type</h3>';
                        for (const [botType, count] of Object.entries(data.stats.bot_types_detected)) {{
                            botHTML += `<div class="bot-item"><strong>${{botType}}:</strong> ${{count}} requests</div>`;
                        }}
                        botList.innerHTML = botHTML;
                    }}
                    
                }} catch (error) {{
                    console.error('Failed to load stats:', error);
                }}
            }}
            
            // Load stats immediately and every 10 seconds
            loadStats();
            setInterval(loadStats, 10000);
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_ngrok_info(self):
        """Show ngrok tunnel information"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ngrok Tunnel Status</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .tunnel-info { background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0; }
                .status-badge { display: inline-block; padding: 5px 10px; border-radius: 20px; color: white; font-weight: bold; }
                .status-active { background: #28a745; }
                .status-inactive { background: #dc3545; }
                .url-box { background: white; padding: 10px; border-radius: 5px; font-family: monospace; word-break: break-all; }
            </style>
        </head>
        <body>
            <h1>ngrok Tunnel Information</h1>
            <p>Public access configuration</p>
            
            <div id="ngrokInfo">
                <p>Loading ngrok tunnel information...</p>
            </div>
            
            <div style="margin-top: 30px;">
                <h3>How to Use</h3>
                <ol>
                    <li>Copy the public URL above</li>
                    <li>Share it with others or use it from other devices</li>
                    <li>The tunnel will automatically forward traffic to this local server</li>
                    <li>All bot interactions will be logged locally</li>
                </ol>
                
                <p><a href="/status">Back to Status</a> | <a href="/">Home</a></p>
            </div>
            
            <script>
            async function loadNgrokInfo() {
                try {
                    const response = await fetch('/api/ngrok');
                    const data = await response.json();
                    
                    const container = document.getElementById('ngrokInfo');
                    
                    if (data.active) {
                        container.innerHTML = `
                            <div class="tunnel-info">
                                <h2><span class="status-badge status-active">ACTIVE</span></h2>
                                <p><strong>Public URL:</strong></p>
                                <div class="url-box">${data.public_url}</div>
                                <p><strong>Local Endpoint:</strong> ${data.local_url}</p>
                                <p><strong>Protocol:</strong> ${data.protocol}</p>
                                <p><strong>Started:</strong> ${data.started}</p>
                                <p><a href="${data.public_url}" target="_blank">Open in new tab</a></p>
                                <p><a href="http://localhost:4040" target="_blank">Open ngrok dashboard</a></p>
                            </div>
                        `;
                    } else {
                        container.innerHTML = `
                            <div class="tunnel-info">
                                <h2><span class="status-badge status-inactive">INACTIVE</span></h2>
                                <p>ngrok tunnel is not active. Start the server with --ngrok flag.</p>
                                <p>Make sure ngrok is installed and authenticated.</p>
                            </div>
                        `;
                    }
                    
                } catch (error) {
                    document.getElementById('ngrokInfo').innerHTML = 
                        '<div class="tunnel-info"><p>Error loading ngrok information. Make sure ngrok is running.</p></div>';
                }
            }
            
            loadNgrokInfo();
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_test_page(self):
        """Show test page for debugging"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .test-section { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }
                .test-button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                .test-button:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <h1>Test Page</h1>
            <p>Use this page to test various features of the tar pit.</p>
            
            <div class="test-section">
                <h3>Link Tests</h3>
                <p><a href="/download/test/test.pdf">Test PDF Download</a></p>
                <p><a href="/download/test/test.csv">Test CSV Download</a></p>
                <p><a href="/download/test/test.json">Test JSON Download</a></p>
                <p><a href="/download/test/test.zip">Test ZIP Download</a></p>
            </div>
            
            <div class="test-section">
                <h3>API Tests</h3>
                <button class="test-button" onclick="testApi('data')">Test Data API</button>
                <button class="test-button" onclick="testApi('status')">Test Status API</button>
                <button class="test-button" onclick="testApi('ngrok')">Test ngrok API</button>
                <div id="apiResult" style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px;"></div>
            </div>
            
            <div class="test-section">
                <h3>Bot Simulation</h3>
                <p>Simulate different bot user agents:</p>
                <button class="test-button" onclick="simulateBot('Googlebot')">Google Bot</button>
                <button class="test-button" onclick="simulateBot('GPTBot')">GPT Bot</button>
                <button class="test-button" onclick="simulateBot('TikTokBot')">TikTok Bot</button>
                <button class="test-button" onclick="simulateBot('SemanticScholarBot')">Academic Bot</button>
                <div id="botResult" style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px;"></div>
            </div>
            
            <div class="test-section">
                <h3>System Info</h3>
                <p><a href="/status">View Status Dashboard</a></p>
                <p><a href="/ngrok">View ngrok Info</a></p>
                <p><a href="/">Go to Home</a></p>
            </div>
            
            <script>
            async function testApi(endpoint) {
                const apiResult = document.getElementById('apiResult');
                apiResult.innerHTML = 'Testing...';
                
                try {
                    const response = await fetch(`/api/${endpoint}`);
                    const data = await response.json();
                    apiResult.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                } catch (error) {
                    apiResult.innerHTML = `Error: ${error}`;
                }
            }
            
            async function simulateBot(userAgent) {
                const botResult = document.getElementById('botResult');
                botResult.innerHTML = `Simulating ${userAgent}...`;
                
                try {
                    const response = await fetch('/', {
                        headers: {
                            'User-Agent': userAgent
                        }
                    });
                    const text = await response.text();
                    botResult.innerHTML = `<p><strong>Status:</strong> ${response.status}</p>
                                          <p><strong>Detected as:</strong> ${text.includes('bot') ? 'Bot' : 'Human'}</p>
                                          <p><small>Response preview: ${text.substring(0, 200)}...</small></p>`;
                } catch (error) {
                    botResult.innerHTML = `Error: ${error}`;
                }
            }
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
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
        """Generate response targeted to bot type - SIMPLIFIED FIXED VERSION"""
        
        # Always show human page for non-bots
        if not is_bot:
            return {
                'content_type': 'text/html',
                'content': self.generate_human_page()
            }
        
        # For bots, generate trap content
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
        <head><title>Research Portal</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h1>Research Portal</h1>
            <p>This site is used for academic research on web traffic patterns and bot behavior.</p>
            <p>For more information, please contact the research team.</p>
            
            <hr>
            <p><small>Educational use only. All access is logged for research purposes.</small></p>
            <p><a href="/status">View Research Dashboard</a></p>
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
            
            html_parts.append('<hr><h2>Interactive Elements</h2>')
            html_parts.extend(interactive['buttons'])
            html_parts.append('<br><br>')
            
            html_parts.append('<h3>Forms & Inputs</h3>')
            html_parts.extend(interactive['forms'])
            
            html_parts.append('<h3>Related Content</h3>')
            html_parts.extend(interactive['links'])
            
            html_parts.append(interactive['dynamic_content'])
            html_parts.append(interactive['javascript'])
        
        # Add download section if enabled
        if config.bait_files_enabled and is_targeted:
            html_parts.append('<hr><h2>Download Datasets</h2>')
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
        return f'<iframe src="{src}" style="display:none;"></iframe>'

# ============================================================================
# ENHANCED MAIN APPLICATION WITH NGrok
# ============================================================================

class InteractiveTarPit:
    """Main interactive tar pit application with ngrok support"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, ngrok_auth_token: str = None):
        self.host = host
        self.port = port
        self.config_manager = ConfigManager()
        self.content_gen = TargetedContentGenerator(self.config_manager.active_config)
        self.bait_manager = BaitContentManager()
        self.interactive_gen = InteractiveElementsGenerator()
        
        # Initialize ngrok manager
        self.ngrok_manager = NgrokManager(auth_token=ngrok_auth_token)
        self.public_url = None
        
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
        self.server_thread = None
        
        # Create directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("bait_files", exist_ok=True)
        
        # Register cleanup
        atexit.register(self.cleanup)
    
    def start(self, use_ngrok: bool = False, public_url: str = None):
        """Start the enhanced tar pit with optional ngrok"""
        
        # Find available port
        self.port = self.find_available_port(self.port)
        if not self.port:
            print(f"ERROR: Could not find an available port starting from {self.port}")
            return
        
        # Setup HTTP handler
        handler = lambda *args: InteractiveTarPitHandler(
            *args,
            content_gen=self.content_gen,
            config_manager=self.config_manager,
            control_panel=self.control_panel,
            bait_manager=self.bait_manager,
            interactive_gen=self.interactive_gen,
            ngrok_manager=self.ngrok_manager
        )
        
        try:
            self.server = HTTPServer((self.host, self.port), handler)
        except Exception as e:
            print(f"ERROR: Failed to start server on port {self.port}: {e}")
            return
        
        # Start ngrok tunnel if requested
        if use_ngrok:
            print(f"\n" + "="*60)
            print(f"INITIALIZING NGrok TUNNEL")
            print(f"="*60)
            
            # Check if ngrok is installed
            if not self.ngrok_manager.is_ngrok_installed():
                print(f"\nERROR: ngrok is not installed or not in PATH!")
                print(f"Please install ngrok from: https://ngrok.com/download")
                print(f"Then authenticate with: ngrok config add-authtoken YOUR_TOKEN")
                use_ngrok = False
            else:
                self.public_url = self.ngrok_manager.start_tunnel(self.port)
                
                if self.public_url:
                    print(f"\n" + "="*60)
                    print(f"NGrok TUNNEL ESTABLISHED")
                    print(f"="*60)
                    print(f"Public URL: {self.public_url}")
                    print(f"ngrok dashboard: http://localhost:4040")
                    print(f"Access from any device/network!")
                else:
                    print(f"\nWARNING: Failed to start ngrok tunnel. Running locally only.")
                    print(f"Try running ngrok manually: ngrok http {self.port}")
                    self.public_url = None
        
        print(f"\n" + "="*60)
        print(f"INTERACTIVE AI SCRAPER TAR PIT")
        print(f"="*60)
        print(f"Local URL: http://{self.host}:{self.port}")
        if self.public_url:
            print(f"Public URL: {self.public_url}")
        print(f"Targeting: {', '.join(self.config_manager.active_config.bot_types)}")
        print(f"Keywords: {', '.join(self.config_manager.active_config.keywords[:5])}...")
        print(f"Bait files: {sum(len(files) for files in self.bait_manager.bait_files.values())} available")
        print(f"Interactive: {'Enabled' if self.config_manager.active_config.interactive_elements else 'Disabled'}")
        print(f"Status: http://{self.host}:{self.port}/status")
        print(f"Test: http://{self.host}:{self.port}/test")
        print(f"\nMonitoring active. Bot interactions will appear below:")
        print(f"="*60)
        
        # Start server in background thread
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
                # Check for ngrok updates if active
                if use_ngrok and not self.ngrok_manager.is_tunnel_alive():
                    print("WARNING: ngrok tunnel appears to be down. Attempting to restart...")
                    self.public_url = self.ngrok_manager.start_tunnel(self.port)
                    
        except KeyboardInterrupt:
            self.stop()
    
    def find_available_port(self, start_port: int) -> int:
        """Find an available port starting from start_port"""
        port = start_port
        max_attempts = 100
        
        for attempt in range(max_attempts):
            if not is_port_in_use(port):
                if port != start_port:
                    print(f"Port {start_port} is in use, using port {port} instead")
                return port
            port += 1
        
        # If we can't find an available port, try a different range
        port = 8080
        for attempt in range(max_attempts):
            if not is_port_in_use(port):
                print(f"Using alternative port: {port}")
                return port
            port += 1
        
        return None
    
    def cleanup(self):
        """Cleanup resources on exit"""
        self.stop()
    
    def stop(self):
        """Stop the tar pit and cleanup"""
        print("\nShutting down...")
        
        # Stop ngrok tunnel
        if self.ngrok_manager:
            self.ngrok_manager.stop()
        
        # Stop server
        if self.server:
            self.server.shutdown()
        
        print("\nFinal Statistics:")
        print(f"   Total Requests: {self.control_panel.stats['total_requests']}")
        print(f"   Bot Requests: {self.control_panel.stats['bot_requests']}")
        print(f"   Targeted Bots: {self.control_panel.stats['targeted_bots']}")
        print(f"   Downloads: {self.control_panel.stats.get('downloads', 0)}")
        
        if self.control_panel.stats['bot_types_detected']:
            print("\nBot Types Detected:")
            for bot_type, count in self.control_panel.stats['bot_types_detected'].items():
                print(f"   {bot_type}: {count}")
        
        print("\nGoodbye!")

# ============================================================================
# ENHANCED CONFIGURATION WIZARD WITH NGrok SETUP
# ============================================================================

def enhanced_configuration_wizard():
    """Interactive configuration wizard with ngrok setup"""
    print("\n" + "="*60)
    print("AI SCRAPER TAR PIT - ENHANCED CONFIGURATION WIZARD")
    print("="*60)
    
    config = {}
    
    # Bot types
    print("\nSELECT BOT TYPES TO TARGET:")
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
    print("\nENTER TARGETING KEYWORDS:")
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
    print("\nINTERACTIVE ELEMENTS:")
    print("  1. Full interactive (buttons, forms, downloads, JavaScript)")
    print("  2. Limited interactive (buttons and links only)")
    print("  3. No interactive elements")
    
    interactive_choice = input("\nSelect level (1-3, default 1): ").strip()
    config['interactive_elements'] = interactive_choice != '3'
    
    # Bait files
    print("\nBAIT FILE SETTINGS:")
    print("  1. Generate and serve bait files (PDF, CSV, JSON, XML, ZIP)")
    print("  2. Serve bait files only (no generation)")
    print("  3. No bait files")
    
    bait_choice = input("\nSelect option (1-3, default 1): ").strip()
    config['bait_files_enabled'] = bait_choice != '3'
    
    # Download traps
    print("\nDOWNLOAD TRAPS:")
    print("  Enable download traps that waste bot bandwidth? (y/n, default y): ")
    dl_choice = input().strip().lower()
    config['download_traps'] = dl_choice != 'n'
    
    # Trap intensity
    print("\nTRAP INTENSITY:")
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
    config['user_uploads_enabled'] = False
    
    # Save configuration
    config_file = "bot_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguration saved to {config_file}")
    print(f"\nSUMMARY:")
    print(f"   Target Bots: {', '.join(config['bot_types'])}")
    print(f"   Keywords: {', '.join(config['keywords'][:5])}...")
    print(f"   Interactive: {'Enabled' if config['interactive_elements'] else 'Disabled'}")
    print(f"   Bait Files: {'Enabled' if config['bait_files_enabled'] else 'Disabled'}")
    print(f"   Downloads: {'Enabled' if config['download_traps'] else 'Disabled'}")
    print(f"   Intensity: {intensity}/3")
    
    return config

# ============================================================================
# QUICK START WITH DEFAULT CONFIG
# ============================================================================

def create_default_config():
    """Create a default configuration file"""
    default_config = {
        "keywords": ["viral", "trending", "challenge", "dance", "music", "ai", "dataset", "training"],
        "bot_types": ["tiktok", "ai_trainer", "social"],
        "content_themes": ["viral", "technical"],
        "density_multiplier": 2.0,
        "recursion_depth": 5,
        "hidden_traps": True,
        "embed_tracking": True,
        "meta_tag_injection": True,
        "interactive_elements": True,
        "bait_files_enabled": True,
        "download_traps": True,
        "user_uploads_enabled": False
    }
    
    with open("bot_config.json", 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("Created default configuration file: bot_config.json")
    print("Targeting: TikTok, AI Trainers, Social bots")
    print("Keywords: viral, trending, challenge, dance, music, ai, dataset, etc.")
    print("Interactive elements: Enabled")
    print("Bait files: Enabled")

# ============================================================================
# MAIN ENTRY POINT WITH NGrok SUPPORT
# ============================================================================

def main():
    """Main entry point with ngrok support"""
    parser = argparse.ArgumentParser(description='Interactive AI Scraper Tar Pit with ngrok')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    parser.add_argument('--ngrok', action='store_true', help='Enable ngrok tunneling for public access')
    parser.add_argument('--ngrok-token', type=str, help='ngrok auth token (or set in ngrok_config.json)')
    parser.add_argument('--wizard', action='store_true', help='Run enhanced configuration wizard')
    parser.add_argument('--quick', action='store_true', help='Quick start with default config')
    parser.add_argument('--test', action='store_true', help='Test bait file generation')
    parser.add_argument('--no-interactive', action='store_true', help='Disable interactive elements')
    parser.add_argument('--default', action='store_true', help='Create default config and exit')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("INTERACTIVE AI SCRAPER TAR PIT WITH NGrok")
    print("="*70)
    print("Enhanced tool with ngrok tunneling, interactive elements and bait files")
    print("Educational use only")
    print("="*70)
    
    if args.default:
        create_default_config()
        return
    
    if args.test:
        print("\nTesting bait file generation...")
        bait_manager = BaitContentManager()
        print(f"Generated {sum(len(files) for files in bait_manager.bait_files.values())} bait files")
        return
    
    if args.wizard:
        enhanced_configuration_wizard()
        print("\nConfiguration complete! Run without --wizard to start the server.")
        choice = input("\nStart server now? (y/n): ").strip().lower()
        if choice == 'y':
            # Check for ngrok config
            ngrok_token = args.ngrok_token
            if not ngrok_token and os.path.exists("ngrok_config.json"):
                with open("ngrok_config.json", 'r') as f:
                    ngrok_config = json.load(f)
                    ngrok_token = ngrok_config.get('auth_token')
            
            use_ngrok = input("Enable ngrok tunneling? (y/n, default y): ").strip().lower() != 'n'
            
            tar_pit = InteractiveTarPit(args.host, args.port, ngrok_token)
            tar_pit.start(use_ngrok=use_ngrok)
        return
    
    if args.quick:
        print("\nQuick starting with default configuration...")
        print("Targeting: TikTok, AI trainers, Social bots")
        print("Interactive elements: Enabled")
        print("Bait files: Enabled")
        print("="*60)
        
        # Create default config if it doesn't exist
        if not os.path.exists("bot_config.json"):
            create_default_config()
        
        # Check for ngrok config
        ngrok_token = args.ngrok_token
        if not ngrok_token and os.path.exists("ngrok_config.json"):
            with open("ngrok_config.json", 'r') as f:
                ngrok_config = json.load(f)
                ngrok_token = ngrok_config.get('auth_token')
        
        # Use ngrok if token is available or explicitly requested
        use_ngrok = args.ngrok or (ngrok_token is not None)
        
        tar_pit = InteractiveTarPit(args.host, args.port, ngrok_token)
        tar_pit.start(use_ngrok=use_ngrok)
        return
    
    # Check if config exists
    if not os.path.exists("bot_config.json"):
        print("\nWARNING: No configuration found!")
        print("Run one of these commands first:")
        print("  python3 tarpit.py --wizard    # Interactive setup")
        print("  python3 tarpit.py --quick     # Quick default config")
        print("  python3 tarpit.py --default   # Create default config")
        return
    
    # Load ngrok token from config file or command line
    ngrok_token = args.ngrok_token
    if not ngrok_token and os.path.exists("ngrok_config.json"):
        with open("ngrok_config.json", 'r') as f:
            ngrok_config = json.load(f)
            ngrok_token = ngrok_config.get('auth_token')
    
    # Start the tar pit
    tar_pit = InteractiveTarPit(args.host, args.port, ngrok_token)
    
    try:
        tar_pit.start(use_ngrok=(args.ngrok or ngrok_token is not None))
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nTry running with --quick to create a default config first.")

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("bait_files", exist_ok=True)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
