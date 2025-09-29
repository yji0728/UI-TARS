#!/usr/bin/env python3
"""
Homepage Tampering Detection Web Application
Leverages UI-TARS capabilities for automated homepage monitoring and tampering detection.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import cv2
import numpy as np
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import schedule

# Add UI-TARS to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'codes'))
from ui_tars.action_parser import parse_action_to_structure_output, parsing_response_to_pyautogui_code

app = Flask(__name__)
app.secret_key = 'homepage-monitor-secret-key'

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
CONFIG_FILE = os.path.join(DATA_DIR, 'monitor_config.json')
ALERTS_FILE = os.path.join(DATA_DIR, 'alerts.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class HomepageMonitor:
    def __init__(self):
        self.monitored_sites = self.load_config()
        self.alerts = self.load_alerts()
        self.monitoring_active = False
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.monitored_sites, f, ensure_ascii=False, indent=2)
    
    def load_alerts(self):
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_alerts(self):
        with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, ensure_ascii=False, indent=2)
    
    def add_site(self, url, name, check_interval=300):
        """Add a new site to monitor"""
        site_id = str(len(self.monitored_sites) + 1)
        self.monitored_sites[site_id] = {
            'url': url,
            'name': name,
            'check_interval': check_interval,
            'last_check': None,
            'status': 'active',
            'baseline_screenshot': None,
            'baseline_hash': None,
            'added_date': datetime.now().isoformat()
        }
        self.save_config()
        return site_id
    
    def remove_site(self, site_id):
        """Remove a site from monitoring"""
        if site_id in self.monitored_sites:
            del self.monitored_sites[site_id]
            self.save_config()
            return True
        return False
    
    def capture_screenshot(self, url, site_id):
        """Capture screenshot using Selenium (UI-TARS compatible)"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f'{site_id}_{timestamp}.png')
            driver.save_screenshot(screenshot_path)
            driver.quit()
            
            return screenshot_path
            
        except Exception as e:
            print(f"Error capturing screenshot for {url}: {str(e)}")
            return None
    
    def calculate_image_hash(self, image_path):
        """Calculate perceptual hash of image for comparison"""
        try:
            img = cv2.imread(image_path)
            img = cv2.resize(img, (64, 64))
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate DCT hash
            dct = cv2.dct(np.float32(img_gray))
            dct_low = dct[:8, :8]
            med = np.median(dct_low)
            hash_bits = dct_low > med
            return ''.join([str(b) for b in hash_bits.flatten()])
        except Exception as e:
            print(f"Error calculating hash: {str(e)}")
            return None
    
    def compare_images(self, img1_path, img2_path):
        """Compare two images and return similarity score"""
        try:
            # Load images
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # Resize to same dimensions
            height = min(img1.shape[0], img2.shape[0])
            width = min(img1.shape[1], img2.shape[1])
            img1 = cv2.resize(img1, (width, height))
            img2 = cv2.resize(img2, (width, height))
            
            # Calculate structural similarity
            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Simple MSE-based similarity
            mse = np.mean((img1_gray - img2_gray) ** 2)
            similarity = 1.0 / (1.0 + mse / 10000.0)
            
            return similarity
            
        except Exception as e:
            print(f"Error comparing images: {str(e)}")
            return 0.0
    
    def create_diff_image(self, img1_path, img2_path, output_path):
        """Create a visual diff highlighting changes between images"""
        try:
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)
            
            if img1 is None or img2 is None:
                return False
            
            # Resize to same dimensions
            height = min(img1.shape[0], img2.shape[0])
            width = min(img1.shape[1], img2.shape[1])
            img1 = cv2.resize(img1, (width, height))
            img2 = cv2.resize(img2, (width, height))
            
            # Calculate absolute difference
            diff = cv2.absdiff(img1, img2)
            
            # Threshold to highlight significant changes
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Create colored diff
            diff_colored = img2.copy()
            diff_colored[thresh > 0] = [0, 0, 255]  # Red for changes
            
            cv2.imwrite(output_path, diff_colored)
            return True
            
        except Exception as e:
            print(f"Error creating diff image: {str(e)}")
            return False
    
    def check_site(self, site_id):
        """Check a single site for tampering"""
        site = self.monitored_sites.get(site_id)
        if not site:
            return False
        
        print(f"Checking site: {site['name']} ({site['url']})")
        
        # Capture current screenshot
        current_screenshot = self.capture_screenshot(site['url'], site_id)
        if not current_screenshot:
            return False
        
        # Update last check time
        site['last_check'] = datetime.now().isoformat()
        
        # If no baseline, set current as baseline
        if not site['baseline_screenshot']:
            site['baseline_screenshot'] = current_screenshot
            site['baseline_hash'] = self.calculate_image_hash(current_screenshot)
            self.save_config()
            return True
        
        # Compare with baseline
        baseline_path = site['baseline_screenshot']
        if os.path.exists(baseline_path):
            similarity = self.compare_images(baseline_path, current_screenshot)
            
            # If similarity is below threshold, alert for tampering
            threshold = 0.85  # Adjustable threshold
            if similarity < threshold:
                self.create_alert(site_id, current_screenshot, similarity)
                
                # Create diff image
                diff_path = os.path.join(SCREENSHOTS_DIR, f'{site_id}_diff_{int(time.time())}.png')
                self.create_diff_image(baseline_path, current_screenshot, diff_path)
                
                print(f"TAMPERING DETECTED! Similarity: {similarity:.2f}")
                return False
        
        self.save_config()
        return True
    
    def create_alert(self, site_id, screenshot_path, similarity_score):
        """Create an alert for detected tampering"""
        site = self.monitored_sites.get(site_id)
        alert = {
            'id': len(self.alerts) + 1,
            'site_id': site_id,
            'site_name': site['name'],
            'site_url': site['url'],
            'timestamp': datetime.now().isoformat(),
            'similarity_score': similarity_score,
            'screenshot_path': screenshot_path,
            'status': 'new'
        }
        
        self.alerts.insert(0, alert)  # Insert at beginning for newest first
        self.save_alerts()
        
        print(f"Alert created for {site['name']}: similarity {similarity_score:.2f}")
    
    def monitor_sites(self):
        """Monitor all active sites"""
        for site_id in self.monitored_sites:
            if self.monitored_sites[site_id]['status'] == 'active':
                self.check_site(site_id)

# Global monitor instance
monitor = HomepageMonitor()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html', 
                         sites=monitor.monitored_sites, 
                         alerts=monitor.alerts[:10])  # Show latest 10 alerts

@app.route('/add_site', methods=['GET', 'POST'])
def add_site():
    """Add new site to monitor"""
    if request.method == 'POST':
        url = request.form['url']
        name = request.form['name']
        interval = int(request.form.get('interval', 300))
        
        if url and name:
            site_id = monitor.add_site(url, name, interval)
            flash(f'Site "{name}" added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please provide both URL and name', 'error')
    
    return render_template('add_site.html')

@app.route('/remove_site/<site_id>')
def remove_site(site_id):
    """Remove site from monitoring"""
    if monitor.remove_site(site_id):
        flash('Site removed successfully!', 'success')
    else:
        flash('Site not found', 'error')
    return redirect(url_for('index'))

@app.route('/check_site/<site_id>')
def check_site(site_id):
    """Manually check a site"""
    result = monitor.check_site(site_id)
    if result:
        flash('Site checked successfully - no tampering detected', 'success')
    else:
        flash('Check completed - please review alerts', 'warning')
    return redirect(url_for('index'))

@app.route('/set_baseline/<site_id>')
def set_baseline(site_id):
    """Set new baseline for a site"""
    site = monitor.monitored_sites.get(site_id)
    if site:
        screenshot_path = monitor.capture_screenshot(site['url'], site_id)
        if screenshot_path:
            site['baseline_screenshot'] = screenshot_path
            site['baseline_hash'] = monitor.calculate_image_hash(screenshot_path)
            monitor.save_config()
            flash('New baseline set successfully!', 'success')
        else:
            flash('Failed to capture screenshot', 'error')
    else:
        flash('Site not found', 'error')
    return redirect(url_for('index'))

@app.route('/alerts')
def alerts():
    """View all alerts"""
    return render_template('alerts.html', alerts=monitor.alerts)

@app.route('/api/sites')
def api_sites():
    """API endpoint for sites data"""
    return jsonify(monitor.monitored_sites)

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for alerts data"""
    return jsonify(monitor.alerts)

@app.route('/api/check_all')
def api_check_all():
    """API endpoint to check all sites"""
    monitor.monitor_sites()
    return jsonify({'status': 'completed'})

def start_monitoring_scheduler():
    """Start background monitoring scheduler"""
    def run_scheduler():
        schedule.every(5).minutes.do(monitor.monitor_sites)
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

if __name__ == '__main__':
    # Start background monitoring
    start_monitoring_scheduler()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)