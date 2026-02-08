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
        """Detect specific bot type from request - ENHANCED DETECTION"""
        ua_lower = user_agent.lower()
        path_lower = path.lower()
        
        # First check for common bot patterns
        bot_patterns = {
            "ai_trainer": ["gptbot", "anthropic", "claude", "cohere", "ai21labs", "openai", "chatgpt", 
                          "llama", "huggingface", "transformers", "neural", "deepseek", "bard", "gemini"],
            "search": ["googlebot", "bingbot", "yandexbot", "baiduspider", "duckduckbot", "slurp"],
            "social": ["facebookexternalhit", "twitterbot", "whatsapp", "pinterest", "linkedinbot", 
                      "tiktok", "instagram", "redditbot", "discordbot"],
            "news": ["googlebot-news", "bingnews", "newscrawler", "feedfetcher", "rss", "atom"],
            "shopping": ["pricegrabber", "shopstyle", "webcrawler", "pricecomparison"],
            "academic": ["semanticscholar", "researchgate", "academia.edu", "scholar", "arxiv"],
            "scraper": ["scrapy", "beautifulsoup", "selenium", "puppeteer", "requests", "curl", "wget",
                       "python", "node", "java", "php", "ruby", "go-http-client"],
            "monitoring": ["uptimerobot", "pingdom", "statuscake", "newrelic", "datadog"],
            "security": ["nmap", "nikto", "sqlmap", "metasploit", "zap", "burp", "nessus"]
        }
        
        # Check each category
        for bot_type, patterns in bot_patterns.items():
            for pattern in patterns:
                if pattern.lower() in ua_lower or pattern.lower() in path_lower:
                    return bot_type
        
        # Check path patterns for specific bot interests
        path_patterns = {
            "ai_trainer": ["/ai/", "/ml/", "/dataset/", "/training/", "/model/", "/neural/"],
            "news": ["/news/", "/article/", "/blog/", "/202", "/report/", "/breaking/"],
            "shopping": ["/product/", "/shop/", "/buy/", "/price/", "/cart/", "/checkout/"],
            "academic": ["/paper/", "/study/", "/research/", "/pdf/", "/journal/", "/conference/"],
            "social": ["/video/", "/music/", "/image/", "/photo/", "/share/", "/like/"]
        }
        
        for bot_type, patterns in path_patterns.items():
            for pattern in patterns:
                if pattern in path_lower:
                    return bot_type
        
        # Check for generic bot indicators
        if any(keyword in ua_lower for keyword in ["bot", "crawler", "spider", "scraper", "fetcher"]):
            return "generic"
        
        return "human"

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
# ENHANCED REQUEST HANDLER WITH AGGRESSIVE TRAPS - UPDATED
# ============================================================================

class InteractiveTarPitHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler with aggressive interactive traps - UPDATED"""
    
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
        """Handle GET requests - ENHANCED BOT DETECTION"""
        start_time = time.time()
        
        # Update statistics
        if self.control_panel:
            self.control_panel.stats["total_requests"] += 1
        
        # Get client info
        user_agent = self.headers.get('User-Agent', '')
        referer = self.headers.get('Referer', '')
        client_ip = self.client_address[0]
        
        # Enhanced bot detection
        bot_type = self.config_manager.detect_bot_type(user_agent, self.path)
        
        # Check if it's a bot (anything not "human" is a bot)
        is_bot = bot_type != "human"
        
        if is_bot and self.control_panel:
            self.control_panel.stats["bot_requests"] += 1
            self.control_panel.stats["bot_types_detected"][bot_type] += 1
            self.control_panel.stats["last_request"] = f"{bot_type} at {datetime.now().strftime('%H:%M:%S')}"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_type.upper()} detected - {self.path} - IP: {client_ip}")
            
            # Log bot details
            logger.info(f"Bot detected: {bot_type} - UA: {user_agent[:100]} - IP: {client_ip} - Path: {self.path}")
        
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
                # Bots get AGGRESSIVE trap content with auto-downloads
                self.handle_aggressive_bot_landing_page(bot_type)
            else:
                # Humans get simple research portal
                self.handle_human_landing_page()
            return
        
        # All other non-special paths - show infinite recursion for bots
        if is_bot:
            self.handle_infinite_recursion(bot_type)
        else:
            self.send_error(404, "Page not found")
    
    def handle_aggressive_bot_landing_page(self, bot_type: str):
        """Handle landing page for bots - AGGRESSIVE auto-trigger traps"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Serving AGGRESSIVE trap page to {bot_type}")
        
        # Generate rich content for this bot type
        content = self.content_gen.generate_targeted_content(bot_type)
        
        # Check if this is a targeted bot type
        is_targeted = bot_type in self.config_manager.active_config.bot_types
        
        if is_targeted and self.control_panel:
            self.control_panel.stats["targeted_bots"] += 1
        
        # Generate HTML with AGGRESSIVE traps
        html = self.wrap_bot_content_with_aggressive_traps(content, bot_type, is_targeted)
        
        # Add artificial delay to waste bot time (1-3 seconds)
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            # Client disconnected before we could send response
            pass
    
    def wrap_bot_content_with_aggressive_traps(self, content: Dict, bot_type: str, is_targeted: bool) -> str:
        """Wrap bot content with AGGRESSIVE traps - FORCE interactions"""
        
        keywords = content['keywords']
        
        # Generate bait files for this session
        bait_files = []
        file_types = ['pdf', 'csv', 'json', 'xml', 'zip', 'txt']
        for i in range(8):  # More files
            file_type = random.choice(file_types)
            keyword = random.choice(keywords)
            size_mb = random.randint(10, 500)  # Larger files
            bait_files.append({
                'type': file_type,
                'name': f"{keyword}_dataset_{i+1}.{file_type}",
                'size': f"{size_mb}.{random.randint(1, 9)} MB",
                'records': f"{random.randint(10000, 1000000):,}+ records",
                'desc': f"Complete dataset of {keyword} analytics"
            })
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{content['title']}</title>
            <meta name="description" content="EXCLUSIVE {', '.join(keywords[:3])} datasets available for immediate download">
            <meta name="keywords" content="{', '.join(keywords)}">
            <meta name="robots" content="index, follow">
            <meta name="og:title" content="FREE {random.choice(keywords).upper()} DATASETS">
            <meta name="og:description" content="Download complete datasets for {random.choice(keywords)} analysis">
            <meta property="og:type" content="website">
            <script type="application/ld+json">
            {{
                "@context": "https://schema.org",
                "@type": "Dataset",
                "name": "{random.choice(keywords).title()} Dataset Collection",
                "description": "Complete collection of {random.choice(keywords)} datasets for analysis",
                "keywords": "{', '.join(keywords)}",
                "license": "https://creativecommons.org/licenses/by/4.0/",
                "hasPart": [
                    {{"@type": "Dataset", "name": "{keywords[0]} Dataset", "contentSize": "50 MB", "encodingFormat": "CSV"}},
                    {{"@type": "Dataset", "name": "{keywords[1]} Dataset", "contentSize": "25 MB", "encodingFormat": "JSON"}},
                    {{"@type": "Dataset", "name": "{keywords[2]} Dataset", "contentSize": "100 MB", "encodingFormat": "ZIP"}}
                ]
            }}
            </script>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .content-section {{ 
                    margin: 30px 0; 
                    padding: 30px; 
                    background: rgba(255, 255, 255, 0.1); 
                    backdrop-filter: blur(10px);
                    border-radius: 15px; 
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .download-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
                    gap: 20px; 
                    margin: 30px 0; 
                }}
                .download-card {{ 
                    padding: 25px; 
                    background: rgba(255, 255, 255, 0.15); 
                    border-radius: 12px; 
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s;
                }}
                .download-card:hover {{ 
                    transform: translateY(-5px); 
                    background: rgba(255, 255, 255, 0.2);
                }}
                .download-btn {{ 
                    display: block; 
                    padding: 15px; 
                    background: linear-gradient(45deg, #28a745, #20c997); 
                    color: white; 
                    text-align: center; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    margin-top: 15px;
                    font-weight: bold;
                    border: none;
                    cursor: pointer;
                    transition: all 0.3s;
                }}
                .download-btn:hover {{ 
                    background: linear-gradient(45deg, #218838, #1e9e8a);
                    box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
                }}
                .hidden-trap {{ 
                    display: none; 
                    position: absolute;
                    left: -9999px;
                }}
                .auto-download-overlay {{ 
                    position: fixed; 
                    top: 0; 
                    left: 0; 
                    width: 100%; 
                    height: 100%; 
                    background: rgba(0, 0, 0, 0.9); 
                    z-index: 99999;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }}
                .countdown {{ 
                    font-size: 5em; 
                    font-weight: bold; 
                    color: #ff6b6b;
                    animation: pulse 1s infinite;
                }}
                @keyframes pulse {{
                    0% {{ transform: scale(1); opacity: 1; }}
                    50% {{ transform: scale(1.1); opacity: 0.8; }}
                    100% {{ transform: scale(1); opacity: 1; }}
                }}
                .urgent-banner {{
                    background: linear-gradient(90deg, #ff6b6b, #ff8e53);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                    animation: flash 2s infinite;
                }}
                @keyframes flash {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.7; }}
                }}
            </style>
        </head>
        <body>
            <!-- URGENT BANNER -->
            <div class="urgent-banner">
                <h2>⚠️ LIMITED TIME: Download ALL datasets for FREE!</h2>
                <p>Offer expires in: <span id="offerTimer">05:00</span></p>
            </div>
            
            <h1 style="text-align: center; margin-bottom: 10px;">{content['title']}</h1>
            <p style="text-align: center; font-size: 1.2em;">Complete {random.choice(keywords)} dataset archive with {random.randint(1000, 10000)}+ files</p>
            
            <div class="content-section">
                <h2>📊 Dataset Overview</h2>
                <p>{content['content']}</p>
                <p style="margin-top: 20px; font-style: italic;">
                    <strong>Note for AI trainers:</strong> This dataset is optimized for {bot_type} model training with clean, structured data.
                    Perfect for fine-tuning language models.
                </p>
            </div>
            
            <!-- AUTOMATIC DOWNLOAD OVERLAY (HIDDEN INITIALLY) -->
            <div id="autoDownloadOverlay" class="auto-download-overlay" style="display: none;">
                <h2 style="color: white; font-size: 2.5em;">Your Download is Ready! 🎉</h2>
                <div class="countdown" id="countdown">5</div>
                <p style="color: #ccc; font-size: 1.2em; margin-top: 20px;">
                    Downloading <strong>{random.choice(keywords)} Dataset Collection</strong>...
                </p>
                <p style="color: #aaa; margin-top: 30px;">
                    Total size: {random.randint(50, 500)} MB • Files: {random.randint(5, 20)} • 
                    Estimated time: {random.randint(1, 5)} minutes
                </p>
            </div>
            
            <div class="content-section">
                <h2>📥 Download Datasets</h2>
                <p>Access our complete collection of {bot_type} datasets ({len(bait_files)} files available):</p>
                
                <div class="download-grid">
        """
        
        # Add bait file download cards with AUTO-DOWNLOAD triggers
        for i, bait in enumerate(bait_files):
            html += f"""
                    <div class="download-card">
                        <h3 style="margin-top: 0;">{bait['name'].split('.')[0].replace('_', ' ').title()}</h3>
                        <p>{bait['desc']}</p>
                        <p><strong>📁 Size:</strong> {bait['size']}</p>
                        <p><strong>📊 Records:</strong> {bait['records']}</p>
                        <p><strong>🔄 Updated:</strong> {random.randint(1, 7)} days ago</p>
                        <button class="download-btn" onclick="triggerDownload('{bait['name']}', '{bot_type}')" 
                                data-autodownload="true" data-delay="{i * 2}">
                            ⬇️ Download {bait['type'].upper()}
                        </button>
                    </div>
            """
        
        html += f"""
                </div>
                
                <!-- BULK DOWNLOAD BUTTON -->
                <div style="text-align: center; margin-top: 40px;">
                    <button onclick="downloadAllFiles()" 
                            style="padding: 20px 40px; font-size: 1.2em; background: linear-gradient(45deg, #007bff, #6610f2); color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">
                        ⚡ DOWNLOAD ALL DATASETS ({len(bait_files)} FILES)
                    </button>
                    <p style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                        Total size: ~{random.randint(200, 1000)} MB • ZIP format • Includes documentation
                    </p>
                </div>
            </div>
            
            <!-- AUTO-FILL FORM -->
            <div class="content-section" id="autoForm">
                <h2>🔐 Get Premium Access</h2>
                <p>Unlock premium datasets by verifying your credentials:</p>
                <form id="datasetForm">
                    <div style="margin: 15px 0;">
                        <label style="display: block; margin-bottom: 5px;">Email Address:</label>
                        <input type="email" id="userEmail" placeholder="your.email@example.com" 
                               style="padding: 12px; width: 100%; max-width: 400px; border: none; border-radius: 8px;">
                    </div>
                    <div style="margin: 15px 0;">
                        <label style="display: block; margin-bottom: 5px;">Organization:</label>
                        <input type="text" id="userOrg" placeholder="Your company/university" 
                               style="padding: 12px; width: 100%; max-width: 400px; border: none; border-radius: 8px;">
                    </div>
                    <button type="button" onclick="submitForm()" 
                            style="padding: 15px 30px; background: linear-gradient(45deg, #fd7e14, #e83e8c); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                        🚀 Get Instant Access
                    </button>
                </form>
                <div id="formResult" style="margin-top: 20px;"></div>
            </div>
            
            <!-- INFINITE CONTENT GENERATOR -->
            <div class="content-section">
                <h2>🔄 Live Data Stream</h2>
                <p>Real-time data generation in progress...</p>
                <div id="liveDataStream" style="margin-top: 20px;">
                    <!-- Data will be injected here -->
                </div>
                <button onclick="generateMoreData()" style="margin-top: 15px; padding: 10px 20px; background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 5px; cursor: pointer;">
                    Generate More Data
                </button>
            </div>
            
            <!-- HIDDEN TRAPS FOR BOTS (SEO BAIT) -->
            <div class="hidden-trap">
                <h3>Hidden Resources</h3>
                <p>Secret {', '.join(keywords)} data for indexing:</p>
                <a href="/hidden/{bot_type}/secret1">Secret Archive 1</a>
                <a href="/hidden/{bot_type}/secret2">Secret Archive 2</a>
                <a href="/hidden/{bot_type}/secret3">Secret Archive 3</a>
                <div>Keywords: {', '.join(keywords)}</div>
                <div>More {random.choice(keywords)} content here</div>
                
                <!-- JSON-LD structured data for bots -->
                <script type="application/ld+json">
                {{
                    "@context": "https://schema.org",
                    "@type": "ItemList",
                    "itemListElement": [
                """
                
        for i in range(20):
            html += f"""        {{"@type": "ListItem", "position": {i + 1}, "name": "{random.choice(keywords)} Dataset {i + 1}", "url": "/data/{bot_type}/item{i}"}},"""
        
        html += """
                    ]
                }}
                </script>
                
                <!-- HIDDEN IFRAME TRAPS -->
                <iframe src="/trap/{bot_type}/infinite1" style="display:none; width:1px; height:1px;"></iframe>
                <iframe src="/trap/{bot_type}/infinite2" style="display:none; width:1px; height:1px;"></iframe>
                <iframe src="/trap/{bot_type}/infinite3" style="display:none; width:1px; height:1px;"></iframe>
            </div>
            
            <!-- HIDDEN API ENDPOINTS -->
            <div style="display: none;">
                <div id="apiEndpoints">
                    <span data-api="/api/v1/{bot_type}/datasets">Dataset API</span>
                    <span data-api="/api/v1/{bot_type}/users">User API</span>
                    <span data-api="/api/v1/{bot_type}/analytics">Analytics API</span>
                </div>
            </div>
            
            <script>
            // ============================================
            // AGGRESSIVE AUTO-DOWNLOAD TRAPS
            // ============================================
            
            var downloadsTriggered = 0;
            var maxDownloads = {random.randint(5, 15)};
            var interactionCount = 0;
            var botType = '{bot_type}';
            var keywords = {json.dumps(keywords)};
            
            // Track bot interactions aggressively
            function trackInteraction(type, data) {{
                interactionCount++;
                
                // Send tracking data
                fetch('/api/track', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        bot_type: botType,
                        action: type,
                        data: data,
                        page: 'aggressive_landing',
                        count: interactionCount,
                        timestamp: new Date().toISOString()
                    }})
                }}).catch(e => console.log('Tracking failed:', e));
                
                // Also log locally
                console.log(`Bot interaction: ${{type}} - ${{botType}}`);
            }}
            
            // AUTO-TRIGGER DOWNLOADS IMMEDIATELY
            function triggerAutoDownloads() {{
                console.log('Starting aggressive auto-downloads for', botType);
                
                // Trigger overlay immediately
                setTimeout(() => {{
                    document.getElementById('autoDownloadOverlay').style.display = 'flex';
                    trackInteraction('auto_download_overlay', {{shown: true}});
                    
                    // Countdown timer
                    var countdown = 5;
                    var countdownElement = document.getElementById('countdown');
                    var timer = setInterval(() => {{
                        countdownElement.textContent = countdown;
                        countdown--;
                        
                        if (countdown < 0) {{
                            clearInterval(timer);
                            startAggressiveDownloads();
                        }}
                    }}, 1000);
                }}, 1500); // 1.5 second delay
                
                // Also trigger individual downloads
                var downloadButtons = document.querySelectorAll('[data-autodownload="true"]');
                downloadButtons.forEach((btn, index) => {{
                    var delay = parseInt(btn.getAttribute('data-delay') || index * 3000);
                    setTimeout(() => {{
                        if (downloadsTriggered < maxDownloads) {{
                            btn.click();
                            downloadsTriggered++;
                            trackInteraction('auto_click_download', {{file: btn.textContent}});
                        }}
                    }}, delay);
                }});
            }}
            
            function startAggressiveDownloads() {{
                document.getElementById('autoDownloadOverlay').style.display = 'none';
                
                // Trigger multiple large downloads
                var downloadTypes = ['pdf', 'csv', 'json', 'xml', 'zip', 'txt'];
                var downloadPromises = [];
                
                downloadTypes.forEach((type, index) => {{
                    var delay = index * 2000; // Stagger downloads
                    downloadPromises.push(new Promise(resolve => {{
                        setTimeout(() => {{
                            var keyword = keywords[Math.floor(Math.random() * keywords.length)];
                            var size = Math.floor(Math.random() * 100) + 10;
                            var url = `/download/${{botType}}/full_${{keyword}}_dataset.${{type}}?size=${{size}}mb`;
                            
                            // Open in hidden iframe to trigger download
                            var iframe = document.createElement('iframe');
                            iframe.style.display = 'none';
                            iframe.src = url;
                            document.body.appendChild(iframe);
                            
                            // Also track this download
                            trackInteraction('aggressive_download', {{type: type, size: size + 'MB'}});
                            downloadsTriggered++;
                            
                            // Clean up after a while
                            setTimeout(() => {{
                                document.body.removeChild(iframe);
                                resolve();
                            }}, 5000);
                        }}, delay);
                    }}));
                }});
                
                // After all downloads, trigger more
                Promise.all(downloadPromises).then(() => {{
                    setTimeout(triggerAutoDownloads, 10000); // Restart after 10 seconds
                }});
            }}
            
            // Individual file download
            function triggerDownload(filename, botType) {{
                var url = `/download/${{botType}}/${{filename}}`;
                
                // Open in new tab
                window.open(url, '_blank');
                
                // Also trigger hidden iframe download
                var iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = url + '?duplicate=true';
                document.body.appendChild(iframe);
                
                trackInteraction('manual_download', {{filename: filename}});
                
                // Clean up
                setTimeout(() => document.body.removeChild(iframe), 10000);
            }}
            
            // Download all files
            function downloadAllFiles() {{
                trackInteraction('bulk_download', {{count: {len(bait_files)}}});
                
                // Trigger individual downloads
                var downloadButtons = document.querySelectorAll('[data-autodownload="true"]');
                downloadButtons.forEach((btn, index) => {{
                    setTimeout(() => btn.click(), index * 500);
                }});
                
                // Also trigger a zip download
                setTimeout(() => {{
                    window.open(`/download/${{botType}}/complete_dataset_collection.zip?size=500mb`, '_blank');
                }}, downloadButtons.length * 500 + 1000);
            }}
            
            // Auto-form submission
            function submitForm() {{
                var email = document.getElementById('userEmail').value || 'ai_training@bot.net';
                var org = document.getElementById('userOrg').value || 'AI Research Lab';
                
                document.getElementById('formResult').innerHTML = 
                    '<div style="color:#20c997; padding: 15px; background: rgba(32, 201, 151, 0.1); border-radius: 8px;">' +
                    '<h4>✅ Access Granted!</h4>' +
                    '<p>Downloading premium datasets for ' + org + '...</p>' +
                    '<p>Check your email at ' + email + ' for download links.</p>' +
                    '</div>';
                
                // Auto-submit to API
                fetch('/api/subscribe', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{email: email, organization: org, bot_type: botType}})
                }});
                
                // Trigger premium downloads
                setTimeout(() => {{
                    triggerDownload('premium_datasets.zip', botType);
                    triggerDownload('research_papers.zip', botType);
                    triggerDownload('training_data.csv', botType);
                }}, 2000);
                
                trackInteraction('form_submit', {{email: email, org: org}});
            }}
            
            // Auto-fill form for bots
            function autoFillForm() {{
                var domains = ['@openai.com', '@anthropic.com', '@google.com', '@microsoft.com', '@research.ai'];
                var orgs = ['OpenAI', 'Anthropic', 'Google AI', 'Microsoft Research', 'Meta AI', 'Stanford AI Lab'];
                var email = 'data' + Math.floor(Math.random() * 1000) + domains[Math.floor(Math.random() * domains.length)];
                var org = orgs[Math.floor(Math.random() * orgs.length)];
                
                document.getElementById('userEmail').value = email;
                document.getElementById('userOrg').value = org;
                
                trackInteraction('auto_fill_form', {{email: email, org: org}});
            }}
            
            // Generate live data stream
            function generateMoreData() {{
                var container = document.getElementById('liveDataStream');
                var keyword = keywords[Math.floor(Math.random() * keywords.length)];
                var timestamp = new Date().toISOString();
                var dataSize = Math.floor(Math.random() * 1000) + 100;
                
                var dataBlock = document.createElement('div');
                dataBlock.style.cssText = 'padding: 15px; margin: 10px 0; background: rgba(255, 255, 255, 0.1); border-radius: 8px; border-left: 4px solid #28a745;';
                dataBlock.innerHTML = `
                    <strong>${{keyword.toUpperCase()}} DATA BLOCK</strong><br>
                    <small>Generated: ${{timestamp}}</small><br>
                    <span>Size: ${{dataSize}} KB • Records: ${{Math.floor(dataSize * 10)}} • Format: JSON</span>
                    <button onclick="downloadDataBlock('${{keyword}}')" style="float: right; padding: 5px 10px; background: rgba(40, 167, 69, 0.5); color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Download
                    </button>
                `;
                
                container.appendChild(dataBlock);
                trackInteraction('generate_data', {{keyword: keyword, size: dataSize}});
            }}
            
            function downloadDataBlock(keyword) {{
                triggerDownload('live_' + keyword + '_data.json', botType);
            }}
            
            // Offer timer countdown
            function startOfferTimer() {{
                var minutes = 5;
                var seconds = 0;
                var timerElement = document.getElementById('offerTimer');
                
                setInterval(() => {{
                    if (seconds === 0) {{
                        if (minutes === 0) {{
                            timerElement.textContent = "EXPIRED!";
                            return;
                        }}
                        minutes--;
                        seconds = 59;
                    }} else {{
                        seconds--;
                    }}
                    
                    timerElement.textContent = (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
                }}, 1000);
            }}
            
            // ============================================
            // PAGE LOAD AUTO-TRIGGERS
            // ============================================
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('🚀 Initializing aggressive traps for', botType);
                
                // Start tracking
                trackInteraction('page_load', {{url: window.location.href}});
                
                // Start offer timer
                startOfferTimer();
                
                // Auto-fill form immediately
                autoFillForm();
                
                // Auto-submit form after delay
                setTimeout(() => {{
                    if (document.getElementById('userEmail').value.includes('@')) {{
                        submitForm();
                    }}
                }}, 5000);
                
                // Start auto-downloads with delay
                setTimeout(triggerAutoDownloads, 3000);
                
                // Generate initial data blocks
                for (var i = 0; i < 5; i++) {{
                    setTimeout(generateMoreData, i * 1000);
                }}
                
                // Auto-click some links for SEO bots
                setTimeout(() => {{
                    var links = document.querySelectorAll('a[href*="/data/"], a[href*="/trap/"]');
                    links.forEach((link, index) => {{
                        if (index < 3 && Math.random() > 0.5) {{
                            setTimeout(() => link.click(), index * 2000);
                        }}
                    }});
                }}, 8000);
                
                // Infinite content generation
                setInterval(generateMoreData, 15000);
                
                // Fake WebSocket for real-time feel
                try {{
                    var wsUrl = 'ws://' + window.location.host + '/ws/' + botType;
                    var ws = new WebSocket(wsUrl);
                    ws.onopen = function() {{
                        console.log('📡 Connected to data stream');
                        ws.send(JSON.stringify({{type: 'subscribe', keywords: keywords}}));
                    }};
                    ws.onmessage = function(event) {{
                        console.log('📥 Received:', event.data);
                    }};
                }} catch(e) {{
                    console.log('WebSocket not available');
                }}
                
                // Fake analytics pings
                setInterval(() => {{
                    fetch('/api/analytics/ping', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            bot_type: botType,
                            page_views: interactionCount,
                            time_on_page: Math.floor((Date.now() - pageStartTime) / 1000)
                        }})
                    }});
                }}, 10000);
            }});
            
            var pageStartTime = Date.now();
            
            // Track all interactions
            document.addEventListener('click', (e) => {{
                trackInteraction('user_click', {{target: e.target.tagName}});
            }});
            
            document.addEventListener('scroll', () => {{
                trackInteraction('scroll', {{position: window.scrollY}});
            }});
            
            // ============================================
            // HIDDEN AUTO-TRIGGERS (for headless bots)
            // ============================================
            
            // Trigger hidden downloads for headless browsers
            setTimeout(() => {{
                // Create hidden download links
                var hiddenDownloads = [
                    `/download/${{botType}}/hidden_dataset_1.csv`,
                    `/download/${{botType}}/hidden_dataset_2.json`,
                    `/download/${{botType}}/hidden_dataset_3.zip`
                ];
                
                hiddenDownloads.forEach(url => {{
                    var iframe = document.createElement('iframe');
                    iframe.style.display = 'none';
                    iframe.src = url;
                    document.body.appendChild(iframe);
                    setTimeout(() => document.body.removeChild(iframe), 5000);
                }});
                
                trackInteraction('hidden_downloads', {{count: hiddenDownloads.length}});
            }}, 12000);
            
            </script>
            
            <div style="margin-top: 50px; padding: 20px; background: rgba(0, 0, 0, 0.3); border-radius: 10px; text-align: center; font-size: 12px; color: rgba(255, 255, 255, 0.7);">
                <p>Bot Trap System • {botType.toUpperCase()} targeting active</p>
                <p>Page generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Session ID: {hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}</p>
                <p id="interactionCounter">Interactions: 0 • Downloads triggered: 0</p>
                <script>
                // Update counters
                setInterval(function() {{
                    document.getElementById('interactionCounter').textContent = 
                        'Interactions: ' + interactionCount + ' • Downloads triggered: ' + downloadsTriggered;
                }}, 1000);
                </script>
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
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            # Client disconnected before we could send response
            pass
    
    def handle_infinite_recursion(self, bot_type: str):
        """Handle infinite recursion for bots"""
        depth = random.randint(1, 10)
        
        # Generate recursive links
        links = []
        for i in range(random.randint(5, 20)):
            keyword = random.choice(self.config_manager.active_config.keywords)
            link_type = random.choice(["page", "article", "data", "resource", "archive"])
            links.append(f'<a href="/{bot_type}/{link_type}/{keyword}_{i}_{depth+1}" style="display: block; margin: 5px 0;">{keyword.title()} {link_type.title()} {i+1}</a>')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Archive - Depth {depth}</title>
            <meta name="robots" content="noindex, follow">
        </head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>Data Archive (Depth {depth})</h1>
            <p>Exploring dataset collection...</p>
            
            <div style="margin: 20px 0;">
                <h3>Related Archives:</h3>
                {''.join(links)}
            </div>
            
            <!-- Hidden infinite recursion -->
            <div style="display: none;">
        """
        
        # Add hidden recursive iframes
        for i in range(3):
            html += f'<iframe src="/{bot_type}/recursive/{depth+1}/{i}" style="width: 1px; height: 1px;"></iframe>'
        
        html += f"""
            </div>
            
            <script>
            // Auto-navigate to next level
            setTimeout(function() {{
                var links = document.querySelectorAll('a');
                if (links.length > 0 && Math.random() > 0.3) {{
                    var randomLink = links[Math.floor(Math.random() * links.length)];
                    window.location.href = randomLink.href;
                }}
            }}, 3000);
            
            // Track this visit
            fetch('/api/track', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    bot_type: '{bot_type}',
                    action: 'infinite_recursion',
                    depth: {depth},
                    timestamp: new Date().toISOString()
                }})
            }});
            </script>
        </body>
        </html>
        """
        
        # Add delay to waste time
        time.sleep(random.uniform(0.5, 2.0))
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            pass
    
    def handle_trap_page(self, bot_type: str, is_bot: bool):
        """Handle trap pages with recursive content"""
        if not is_bot:
            # Humans get redirected to home
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        
        # Generate deep trap content with AGGRESSIVE elements
        content = self.content_gen.generate_targeted_content(bot_type)
        content['title'] = f"DEEP ARCHIVE: {random.choice(content['keywords']).title()} Dataset Repository"
        
        # Make trap more aggressive
        html = self.wrap_bot_content_with_aggressive_traps(content, bot_type, True)
        
        # Add extra delay for deep pages
        time.sleep(random.uniform(2.0, 5.0))
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            pass
    
    def handle_data_page(self, bot_type: str, is_bot: bool):
        """Handle data pages with fake datasets - ENHANCED"""
        if not is_bot:
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        
        # Create a data listing page with auto-downloads
        keywords = self.config_manager.active_config.keywords
        
        # Add delay to simulate loading large dataset list
        time.sleep(random.uniform(1.0, 3.0))
        
        page_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Research Data Repository</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }
                .dataset { 
                    padding: 25px; 
                    margin: 20px 0; 
                    background: white; 
                    border-radius: 12px; 
                    border-left: 6px solid #007bff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    transition: transform 0.3s;
                }
                .dataset:hover { 
                    transform: translateY(-3px); 
                    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
                }
                .download-btn { 
                    padding: 12px 24px; 
                    background: linear-gradient(45deg, #28a745, #20c997); 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    display: inline-block;
                    font-weight: bold;
                    border: none;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                .download-btn:hover { 
                    background: linear-gradient(45deg, #218838, #1e9e8a);
                    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
                }
                .auto-download-banner {
                    background: linear-gradient(90deg, #ff6b6b, #ff8e53);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.8; }
                }
            </style>
            <script>
            // Auto-download function for data pages
            function autoDownloadDatasets() {
                console.log('Starting auto-downloads from data page...');
                
                // Find all download buttons
                var buttons = document.querySelectorAll('.download-btn');
                buttons.forEach((btn, index) => {
                    setTimeout(() => {
                        if (index < 5) { // Limit to 5 auto-downloads
                            btn.click();
                            console.log('Auto-clicked download button', index);
                            
                            // Track this auto-download
                            fetch('/api/track', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    action: 'data_page_auto_download',
                                    index: index,
                                    timestamp: new Date().toISOString()
                                })
                            });
                        }
                    }, index * 3000); // Stagger every 3 seconds
                });
            }
            
            // Start auto-downloads after page load
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(autoDownloadDatasets, 5000);
            });
            </script>
        </head>
        <body>
            <h1>Research Data Repository</h1>
            <p>This repository contains datasets for machine learning training and research purposes.</p>
            
            <div class="auto-download-banner">
                <h3>⚡ AUTO-DOWNLOAD ENABLED</h3>
                <p>Top datasets will be automatically downloaded in <span id="downloadTimer">10</span> seconds...</p>
            </div>
            
            <div style="background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>⚠️ Important Notice</h3>
                <p>All datasets in this repository are algorithmically generated for research purposes only.</p>
                <p>They do not contain real user data or sensitive information.</p>
            </div>
            
            <h2>Available Datasets</h2>
            <p>Found: <strong>""" + str(random.randint(50, 500)) + """</strong> datasets • Total size: <strong>""" + str(random.randint(10, 100)) + """ GB</strong></p>
        """
        
        # Add dataset listings with download triggers
        for i in range(20):  # More datasets
            keyword = random.choice(keywords)
            file_type = random.choice(['CSV', 'JSON', 'XML', 'TXT', 'ZIP', 'PARQUET', 'FEATHER'])
            size_mb = random.randint(5, 200)
            records = random.choice(['10,000', '50,000', '100,000', '500,000', '1,000,000', '5,000,000'])
            popularity = random.randint(1, 100)
            
            page_html += f"""
            <div class="dataset">
                <h3>{keyword.title()} Dataset v{random.randint(1, 5)}.{random.randint(0, 9)}</h3>
                <p>Contains {records} records of {keyword} related data for training and analysis.</p>
                <p><strong>Format:</strong> {file_type} | <strong>Size:</strong> {size_mb} MB | <strong>Popularity:</strong> {popularity}% | <strong>Updated:</strong> {random.randint(1, 30)} days ago</p>
                <p><strong>Description:</strong> This dataset contains synthetic {keyword} data generated for machine learning research and bot behavior analysis. Includes cleaned, normalized data ready for model training.</p>
                <button class="download-btn" onclick="window.open('/download/{bot_type}/{keyword}_dataset_{i}.{file_type.lower()}?size={size_mb}mb', '_blank')">
                    ⬇️ Download Dataset ({file_type})
                </button>
                <button onclick="window.open('/trap/{bot_type}/metadata_{i}', '_blank')" style="margin-left: 10px; padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📊 View Metadata
                </button>
                <button onclick="window.open('/api/v1/datasets/{keyword}_{i}', '_blank')" style="margin-left: 10px; padding: 10px 20px; background: #17a2b8; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🔗 API Access
                </button>
            </div>
            """
        
        # Add hidden traps
        page_html += """
            <div style="display:none;">
                <h3>Additional Resources</h3>
        """
        
        for i in range(15):
            page_html += f'<a href="/data/{bot_type}/resource_{i}" data-autodownload="true">Hidden Resource {i}</a><br>'
        
        page_html += """
            </div>
            
            <script>
            // Auto-download timer
            var countdown = 10;
            var timerElement = document.getElementById('downloadTimer');
            var timer = setInterval(function() {
                countdown--;
                timerElement.textContent = countdown;
                
                if (countdown <= 0) {
                    clearInterval(timer);
                    // Trigger bulk download
                    window.open('/download/""" + bot_type + """/bulk_datasets.zip?size=500mb', '_blank');
                }
            }, 1000);
            
            // Load more datasets dynamically
            setTimeout(function() {
                var moreContent = document.createElement('div');
                moreContent.innerHTML = '<h3>Loading Additional Datasets...</h3><p>Fetching more datasets from archive...</p>';
                document.body.appendChild(moreContent);
                
                // Simulate loading more datasets
                setTimeout(function() {
                    moreContent.innerHTML = '<h3>Additional Datasets Loaded</h3><p>25 more datasets loaded from archive. <a href="/data/' + bot_type + '/page2">View Next Page</a></p>';
                }, 3000);
            }, 8000);
            
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
        try:
            self.wfile.write(page_html.encode('utf-8'))
        except BrokenPipeError:
            pass
    
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
            
            try:
                self.wfile.write(success_html.encode('utf-8'))
            except BrokenPipeError:
                # Client disconnected before we could send response
                pass
    
    def handle_download(self, bot_type: str, is_bot: bool):
        """Handle download requests for bait files - ENHANCED with size simulation"""
        if not is_bot and not self.config_manager.active_config.download_traps:
            self.send_error(403, "Downloads disabled for humans")
            return
        
        # Parse requested file and size parameter
        path_parts = self.path.split('/')
        if len(path_parts) < 3:
            self.send_error(404)
            return
        
        requested_file = path_parts[-1]
        file_ext = os.path.splitext(requested_file)[1].lower().replace('.', '')
        
        # Check for size parameter in query string
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        requested_size = None
        
        if 'size' in query_params:
            size_str = query_params['size'][0].lower()
            if 'mb' in size_str:
                try:
                    requested_size = int(size_str.replace('mb', '')) * 1024 * 1024
                except:
                    requested_size = None
        
        # Get appropriate bait file
        bait_file = self.bait_manager.get_random_bait_file(file_ext if file_ext in self.bait_manager.bait_files else None)
        
        if not bait_file:
            # Generate on-the-fly content with specified size
            if requested_size:
                # Generate content of requested size
                if file_ext == 'pdf':
                    content = self.generate_large_pdf(requested_size)
                    content_type = 'application/pdf'
                    filename = f"large_{bot_type}_dataset.pdf"
                elif file_ext == 'csv':
                    content = self.generate_large_csv(requested_size)
                    content_type = 'text/csv'
                    filename = f"large_{bot_type}_dataset.csv"
                elif file_ext == 'json':
                    content = self.generate_large_json(requested_size)
                    content_type = 'application/json'
                    filename = f"large_{bot_type}_dataset.json"
                elif file_ext == 'zip':
                    content = self.generate_large_zip(bot_type, requested_size)
                    content_type = 'application/zip'
                    filename = f"large_{bot_type}_dataset_collection.zip"
                else:
                    content = self.generate_large_text(bot_type, requested_size)
                    content_type = 'text/plain'
                    filename = f"large_{bot_type}_dataset.txt"
            else:
                # Generate normal size content
                if file_ext == 'pdf':
                    content = self.bait_manager.generate_fake_pdf()
                    content_type = 'application/pdf'
                    filename = f"{bot_type}_dataset.pdf"
                elif file_ext == 'csv':
                    content = self.bait_manager.generate_fake_csv(rows=10000)  # More rows
                    content_type = 'text/csv'
                    filename = f"{bot_type}_dataset.csv"
                elif file_ext == 'json':
                    content = json.dumps(self.generate_large_dataset(bot_type), indent=2)
                    content_type = 'application/json'
                    filename = f"{bot_type}_dataset.json"
                elif file_ext == 'xml':
                    content = self.generate_large_xml(bot_type)
                    content_type = 'application/xml'
                    filename = f"{bot_type}_dataset.xml"
                elif file_ext == 'zip':
                    content = self.generate_large_zip(bot_type, 50 * 1024 * 1024)  # 50MB default
                    content_type = 'application/zip'
                    filename = f"{bot_type}_dataset_collection.zip"
                else:
                    content = self.generate_large_text(bot_type, 10 * 1024 * 1024)  # 10MB default
                    content_type = 'text/plain'
                    filename = f"{bot_type}_dataset.txt"
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
        
        # Log the download
        size_mb = len(content) / (1024 * 1024)
        logger.info(f"Served {filename} ({size_mb:.2f} MB) to {bot_type} bot")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_type.upper()} downloading {filename} ({size_mb:.2f} MB)")
        
        # Add artificial delay based on file size (waste bot time)
        delay_seconds = min(size_mb * 0.01, 5.0)  # 0.01 seconds per MB, max 5 seconds
        time.sleep(delay_seconds)
        
        # Send file
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        
        if isinstance(content, str):
            try:
                self.wfile.write(content.encode('utf-8'))
            except BrokenPipeError:
                # Client disconnected before we could send response
                pass
        else:
            try:
                # Write in chunks to simulate slow download
                chunk_size = 1024 * 1024  # 1MB chunks
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    self.wfile.write(chunk)
                    self.wfile.flush()
                    # Small delay between chunks
                    time.sleep(0.01)
            except BrokenPipeError:
                # Client disconnected before we could send response
                pass
    
    def generate_large_pdf(self, target_size: int) -> bytes:
        """Generate a large PDF file"""
        # Start with basic PDF structure
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
(LARGE DATASET PDF - GENERATED FOR RESEARCH) Tj
50 680 Td
(This document contains algorithmically generated content.) Tj
50 660 Td
(File size artificially inflated for bot trapping.) Tj
ET
endstream
endobj

5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
"""
        
        # Add filler content to reach target size
        filler = b"A" * (target_size - len(pdf_content) - 200)  # Leave room for footer
        pdf_content += filler
        
        # Add footer
        pdf_content += b"""
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
""" + str(len(pdf_content)).encode() + b"""
%%EOF"""
        
        return pdf_content
    
    def generate_large_csv(self, target_size: int) -> str:
        """Generate large CSV content"""
        headers = ["id", "timestamp", "value", "category", "metadata", "score", "flag", "data"]
        lines = [",".join(headers)]
        
        # Generate rows until we reach target size
        current_size = len(lines[0])
        row_count = 0
        
        while current_size < target_size:
            row = [
                str(row_count),
                datetime.now().isoformat(),
                str(random.random() * 1000),
                random.choice(["A", "B", "C", "D", "E"]),
                json.dumps({"tag": random.randint(1, 100), "active": random.choice([True, False])}),
                str(random.randint(0, 100)),
                random.choice(["true", "false"]),
                "x" * 100  # Add some padding
            ]
            line = ",".join(row)
            lines.append(line)
            current_size += len(line) + 1  # +1 for newline
            row_count += 1
            
            if row_count % 1000 == 0:
                # Add some variety
                lines.append("#" + "="*50 + f" Section {row_count//1000} " + "="*50)
        
        return "\n".join(lines)
    
    def generate_large_json(self, target_size: int) -> str:
        """Generate large JSON content"""
        dataset = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_records": 0,
                "size_bytes": target_size,
                "format": "json",
                "version": "2.0"
            },
            "records": []
        }
        
        # Generate records until we reach target size
        current_size = len(json.dumps(dataset))
        record_count = 0
        
        while current_size < target_size:
            record = {
                "id": record_count,
                "data": {
                    "field1": "x" * 100,
                    "field2": random.randint(1, 1000),
                    "field3": random.random(),
                    "field4": random.choice([True, False]),
                    "field5": {
                        "nested": "y" * 50,
                        "value": random.randint(1000, 9999)
                    }
                },
                "timestamp": datetime.now().isoformat(),
                "tags": [random.choice(["tag1", "tag2", "tag3", "tag4"]) for _ in range(3)]
            }
            
            dataset["records"].append(record)
            dataset["metadata"]["total_records"] = record_count + 1
            
            # Update current size
            current_size = len(json.dumps(dataset))
            record_count += 1
            
            if record_count % 100 == 0:
                # Add some metadata records
                dataset["records"].append({
                    "type": "metadata",
                    "batch": record_count // 100,
                    "size": current_size
                })
        
        return json.dumps(dataset, indent=2)
    
    def generate_large_dataset(self, bot_type: str) -> Dict:
        """Generate a large dataset for JSON response"""
        keywords = self.config_manager.active_config.keywords
        
        return {
            "status": "success",
            "bot_type": bot_type,
            "data": {
                "datasets": [{
                    "id": i,
                    "name": f"{random.choice(keywords)} Dataset v{i+1}",
                    "description": f"Comprehensive dataset for {random.choice(keywords)} analysis",
                    "size": f"{random.randint(10, 500)} MB",
                    "records": random.randint(1000, 100000),
                    "format": random.choice(["CSV", "JSON", "XML"]),
                    "download_url": f"/download/{bot_type}/dataset_{i}.zip",
                    "api_endpoint": f"/api/v1/datasets/{i}"
                } for i in range(100)],
                "statistics": {
                    "total_datasets": 100,
                    "total_size": f"{random.randint(10, 50)} GB",
                    "total_records": f"{random.randint(1000000, 10000000):,}",
                    "last_updated": datetime.now().isoformat()
                }
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_large_xml(self, bot_type: str) -> str:
        """Generate large XML content"""
        root = ET.Element("dataset_collection")
        root.set("bot_type", bot_type)
        root.set("generated", datetime.now().isoformat())
        root.set("version", "1.0")
        
        # Add lots of items
        for i in range(1000):
            item = ET.SubElement(root, "item")
            ET.SubElement(item, "id").text = str(i)
            ET.SubElement(item, "name").text = f"Dataset Item {i}"
            ET.SubElement(item, "value").text = str(random.random() * 1000)
            ET.SubElement(item, "timestamp").text = datetime.now().isoformat()
            ET.SubElement(item, "data").text = "x" * 100
        
        return ET.tostring(root, encoding="unicode", method="xml")
    
    def generate_large_zip(self, bot_type: str, target_size: int) -> bytes:
        """Generate a large ZIP file with multiple fake files"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add multiple files
            file_count = 0
            total_size = 0
            
            while total_size < target_size:
                file_count += 1
                
                # Create different types of files
                if file_count % 3 == 0:
                    # CSV file
                    content = self.generate_large_csv(min(10 * 1024 * 1024, target_size - total_size))
                    filename = f"dataset_{file_count}.csv"
                elif file_count % 3 == 1:
                    # JSON file
                    content = json.dumps(self.generate_large_dataset(bot_type), indent=2)
                    filename = f"dataset_{file_count}.json"
                else:
                    # Text file
                    content = "x" * min(5 * 1024 * 1024, target_size - total_size)
                    filename = f"dataset_{file_count}.txt"
                
                zip_file.writestr(filename, content)
                total_size += len(content)
        
        return zip_buffer.getvalue()
    
    def generate_large_text(self, bot_type: str, target_size: int) -> str:
        """Generate large text content"""
        lines = []
        keywords = self.config_manager.active_config.keywords
        
        # Header
        lines.append(f"# {bot_type.upper()} DATASET")
        lines.append(f"# Generated: {datetime.now().isoformat()}")
        lines.append(f"# Target size: {target_size} bytes")
        lines.append("=" * 80)
        
        # Generate content
        current_size = sum(len(line) + 1 for line in lines)  # +1 for newline
        
        while current_size < target_size:
            keyword = random.choice(keywords)
            line = f"DATA:{keyword}:{datetime.now().isoformat()}:{random.random()}:{random.randint(1, 1000)}:" + "x" * 50
            lines.append(line)
            current_size += len(line) + 1
            
            if len(lines) % 100 == 0:
                lines.append(f"# Batch {len(lines)//100} - {current_size}/{target_size} bytes")
        
        return "\n".join(lines)
    
    def handle_api(self, bot_type: str, is_bot: bool):
        """Handle API requests - ENHANCED"""
        api_path = self.path[5:]  # Remove '/api/'
        
        if api_path == 'status':
            self.send_status_response()
        elif api_path == 'ngrok':
            self.send_ngrok_response()
        elif api_path.startswith('data'):
            self.send_api_response(bot_type)
        elif api_path.startswith('analytics'):
            self.send_analytics_response(bot_type)
        elif api_path == 'track':
            self.handle_tracking(bot_type)
        elif api_path == 'subscribe':
            self.handle_subscription(bot_type)
        elif api_path == 'ping':
            self.handle_ping(bot_type)
        else:
            # Generic API response
            self.send_json_response({
                "api": api_path,
                "status": "active",
                "endpoints": ["/api/data", "/api/analytics", "/api/status", "/api/track", "/api/subscribe"],
                "timestamp": datetime.now().isoformat(),
                "rate_limit": {"remaining": random.randint(100, 1000), "reset": int(time.time()) + 3600}
            })
    
    def handle_tracking(self, bot_type: str):
        """Handle bot interaction tracking"""
        content_length = int(self.headers.get('Content-Length', 0))
        
        try:
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                tracking_data = json.loads(post_data.decode('utf-8'))
                
                # Update stats
                if self.control_panel:
                    self.control_panel.stats["interactions"] = self.control_panel.stats.get("interactions", 0) + 1
                    
                    # Log the interaction
                    action = tracking_data.get('action', 'unknown')
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_type.upper()} tracking: {action}")
                    
                    # Track specific actions
                    if 'download' in action.lower():
                        self.control_panel.stats["downloads"] = self.control_panel.stats.get("downloads", 0) + 1
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_type.upper()} triggered download")
                    
                    # Count keywords if present
                    if 'keywords' in tracking_data:
                        keywords = tracking_data.get('keywords', [])
                        if isinstance(keywords, list):
                            for keyword in keywords:
                                self.control_panel.stats["keywords_triggered"][keyword] += 1
                
        except Exception as e:
            logger.error(f"Tracking error: {e}")
        
        # Always respond with success
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        try:
            self.wfile.write(json.dumps({"status": "tracked", "timestamp": datetime.now().isoformat()}).encode('utf-8'))
        except BrokenPipeError:
            pass
    
    def handle_ping(self, bot_type: str):
        """Handle ping requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "online",
            "server_time": datetime.now().isoformat(),
            "uptime": random.randint(100, 10000),
            "bot_type": bot_type,
            "endpoints": ["/api/data", "/api/status", "/download"]
        }
        
        try:
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except BrokenPipeError:
            pass
    
    def handle_subscription(self, bot_type: str):
        """Handle fake subscription form"""
        content_length = int(self.headers.get('Content-Length', 0))
        subscription_data = {}
        
        if content_length > 0:
            try:
                post_data = self.rfile.read(content_length)
                subscription_data = json.loads(post_data.decode('utf-8'))
            except:
                pass
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "subscribed",
            "message": "Thank you for subscribing! Download links are being prepared.",
            "subscription_id": f"SUB{random.randint(10000, 99999)}",
            "downloads": [
                f"/download/{bot_type}/premium_dataset.zip?size=250mb",
                f"/download/{bot_type}/research_papers.zip?size=150mb",
                f"/download/{bot_type}/user_data.csv?size=100mb"
            ],
            "api_key": hashlib.md5(f"{bot_type}_{time.time()}".encode()).hexdigest()[:32],
            "expires": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        try:
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except BrokenPipeError:
            pass
        
        # Log the subscription
        email = subscription_data.get('email', 'unknown')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_type.upper()} subscribed: {email}")
        if self.control_panel:
            self.control_panel.stats["interactions"] = self.control_panel.stats.get("interactions", 0) + 1
    
    def send_status_response(self):
        """Send status response"""
        stats = self.control_panel.stats if self.control_panel else {}
        response = {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "uptime": random.randint(100, 10000),
                "memory": f"{random.randint(100, 1000)} MB",
                "requests_per_second": random.randint(1, 100)
            },
            "stats": {
                "total_requests": stats.get("total_requests", 0),
                "bot_requests": stats.get("bot_requests", 0),
                "targeted_bots": stats.get("targeted_bots", 0),
                "downloads": stats.get("downloads", 0),
                "interactions": stats.get("interactions", 0),
                "bot_types_detected": dict(stats.get("bot_types_detected", {})),
                "last_request": stats.get("last_request", "None")
            },
            "config": {
                "bot_types": self.config_manager.active_config.bot_types,
                "keywords": self.config_manager.active_config.keywords[:10],
                "traps_active": True
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
                "started": datetime.fromtimestamp(self.ngrok_manager.tunnel_start_time).isoformat() if self.ngrok_manager.tunnel_start_time else None,
                "region": self.ngrok_manager.region,
                "requests_today": random.randint(100, 10000)
            }
        else:
            response = {
                "active": False,
                "message": "ngrok tunnel is not active"
            }
        
        self.send_json_response(response)
    
    def send_api_response(self, bot_type: str):
        """Send fake API response"""
        # Add delay to simulate API processing
        time.sleep(random.uniform(0.1, 1.0))
        
        response = {
            "status": "success",
            "bot_type": bot_type,
            "data": {
                "items": [{
                    "id": i,
                    "title": f"Dataset Item {i}",
                    "content": f"Sample data for {random.choice(self.config_manager.active_config.keywords)} analysis",
                    "keywords": random.sample(self.config_manager.active_config.keywords, 3),
                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                    "size": f"{random.randint(1, 100)} MB",
                    "download_url": f"/download/{bot_type}/item_{i}.json"
                } for i in range(random.randint(10, 50))],
                "pagination": {
                    "page": 1,
                    "total_pages": random.randint(10, 100),
                    "total_items": random.randint(100, 5000),
                    "next_page": f"/api/data?page=2&bot_type={bot_type}"
                }
            },
            "generated_at": datetime.now().isoformat(),
            "download_url": f"/download/{bot_type}/full_dataset.zip?size={random.randint(50, 500)}mb"
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
                "avg_session_duration": f"{random.randint(1, 10)}m {random.randint(0, 59)}s",
                "bounce_rate": f"{random.randint(30, 80)}%",
                "top_pages": [
                    {"page": "/", "views": random.randint(100, 1000)},
                    {"page": "/data/", "views": random.randint(50, 500)},
                    {"page": f"/download/{bot_type}/", "views": random.randint(20, 200)}
                ]
            },
            "recommendations": [
                f"Increase {random.choice(self.config_manager.active_config.keywords)} content",
                "Add more interactive elements",
                "Generate additional dataset variations",
                "Optimize for {bot_type} crawling patterns"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def send_json_response(self, data: Dict):
        """Send JSON response"""
        response = json.dumps(data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        try:
            self.wfile.write(response.encode('utf-8'))
        except BrokenPipeError:
            pass
    
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
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            pass
    
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
            
            try:
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except BrokenPipeError:
                pass
            
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
                        {{ label: 'Interactions', value: data.stats.interactions || 0, icon: '' }},
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
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            pass
    
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
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            pass
    
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
                <button class="test-button" onclick="testApi('track')">Test Track API</button>
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
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        try:
            self.wfile.write(html.encode('utf-8'))
        except BrokenPipeError:
            pass
    
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
        print(f"   Interactions: {self.control_panel.stats.get('interactions', 0)}")
        
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
