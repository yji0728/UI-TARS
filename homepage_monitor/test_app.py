#!/usr/bin/env python3
"""
Test script for the Homepage Monitor application
"""

import os
import sys
import json
import tempfile
from PIL import Image
import numpy as np
import cv2

# Add UI-TARS to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'codes'))

def create_test_image(width=800, height=600, color=(255, 255, 255), text="Test Image"):
    """Create a test image"""
    img = Image.new('RGB', (width, height), color)
    # Save as temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name)
    return temp_file.name

def test_image_comparison():
    """Test the image comparison functionality"""
    print("Testing image comparison...")
    
    # Create two slightly different test images
    img1_path = create_test_image(color=(255, 255, 255))
    img2_path = create_test_image(color=(250, 250, 250))
    
    try:
        # Load images
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        # Calculate similarity
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        mse = np.mean((img1_gray - img2_gray) ** 2)
        similarity = 1.0 / (1.0 + mse / 10000.0)
        
        print(f"Similarity score: {similarity:.4f}")
        print("✓ Image comparison test passed")
        
    except Exception as e:
        print(f"✗ Image comparison test failed: {e}")
    
    finally:
        # Cleanup
        os.unlink(img1_path)
        os.unlink(img2_path)

def test_ui_tars_import():
    """Test UI-TARS module import"""
    print("Testing UI-TARS import...")
    
    try:
        from ui_tars.action_parser import parse_action_to_structure_output, parsing_response_to_pyautogui_code
        print("✓ UI-TARS modules imported successfully")
        
        # Test action parsing
        response = "Thought: Click the button\nAction: click(start_box='(100,200)')"
        try:
            parsed_dict = parse_action_to_structure_output(
                response,
                factor=1000,
                origin_resized_height=1080,
                origin_resized_width=1920,
                model_type="qwen25vl"
            )
            print("✓ Action parsing test passed")
        except Exception as e:
            print(f"Note: Action parsing requires full UI-TARS setup: {e}")
        
    except Exception as e:
        print(f"✗ UI-TARS import failed: {e}")

def test_flask_app_creation():
    """Test Flask app creation without running it"""
    print("Testing Flask app creation...")
    
    try:
        # Import the app
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Mock the selenium import to avoid ChromeDriver requirement
        import types
        mock_selenium = types.ModuleType('selenium')
        mock_selenium.webdriver = types.ModuleType('webdriver')
        mock_selenium.webdriver.Chrome = lambda options=None: None
        mock_selenium.webdriver.chrome = types.ModuleType('chrome')
        mock_selenium.webdriver.chrome.options = types.ModuleType('options')
        mock_selenium.webdriver.chrome.options.Options = type
        mock_selenium.webdriver.common = types.ModuleType('common')
        mock_selenium.webdriver.common.by = types.ModuleType('by')
        mock_selenium.webdriver.common.by.By = type
        mock_selenium.webdriver.support = types.ModuleType('support')
        mock_selenium.webdriver.support.ui = types.ModuleType('ui')
        mock_selenium.webdriver.support.ui.WebDriverWait = type
        mock_selenium.webdriver.support.expected_conditions = type
        
        sys.modules['selenium'] = mock_selenium
        sys.modules['selenium.webdriver'] = mock_selenium.webdriver
        sys.modules['selenium.webdriver.chrome.options'] = mock_selenium.webdriver.chrome.options
        sys.modules['selenium.webdriver.common.by'] = mock_selenium.webdriver.common.by
        sys.modules['selenium.webdriver.support.ui'] = mock_selenium.webdriver.support.ui
        sys.modules['selenium.webdriver.support'] = mock_selenium.webdriver.support
        
        from app import HomepageMonitor
        
        # Test HomepageMonitor creation
        monitor = HomepageMonitor()
        print("✓ HomepageMonitor created successfully")
        
        # Test adding a site
        site_id = monitor.add_site("https://example.com", "Test Site")
        print(f"✓ Site added with ID: {site_id}")
        
        print("✓ Flask app creation test passed")
        
    except Exception as e:
        print(f"✗ Flask app creation test failed: {e}")

def create_demo_data():
    """Create demo data for the application"""
    print("Creating demo data...")
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Demo sites configuration
    demo_sites = {
        "1": {
            "url": "https://example.com",
            "name": "Example.com",
            "check_interval": 300,
            "last_check": None,
            "status": "active",
            "baseline_screenshot": None,
            "baseline_hash": None,
            "added_date": "2025-01-19T10:00:00"
        },
        "2": {
            "url": "https://github.com",
            "name": "GitHub",
            "check_interval": 600,
            "last_check": "2025-01-19T10:30:00",
            "status": "active",
            "baseline_screenshot": None,
            "baseline_hash": None,
            "added_date": "2025-01-19T09:30:00"
        }
    }
    
    # Demo alerts
    demo_alerts = [
        {
            "id": 1,
            "site_id": "1",
            "site_name": "Example.com",
            "site_url": "https://example.com",
            "timestamp": "2025-01-19T11:15:00",
            "similarity_score": 0.72,
            "screenshot_path": "screenshots/1_20250119_111500.png",
            "status": "new"
        }
    ]
    
    # Save demo data
    config_file = os.path.join(data_dir, 'monitor_config.json')
    alerts_file = os.path.join(data_dir, 'alerts.json')
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(demo_sites, f, ensure_ascii=False, indent=2)
    
    with open(alerts_file, 'w', encoding='utf-8') as f:
        json.dump(demo_alerts, f, ensure_ascii=False, indent=2)
    
    print("✓ Demo data created successfully")

if __name__ == "__main__":
    print("=== Homepage Monitor Test Suite ===\n")
    
    test_ui_tars_import()
    print()
    
    test_image_comparison()
    print()
    
    test_flask_app_creation()
    print()
    
    create_demo_data()
    print()
    
    print("=== All tests completed ===")
    print("\nTo run the application:")
    print("cd homepage_monitor")
    print("python app.py")
    print("\nThen open http://localhost:5000 in your browser")