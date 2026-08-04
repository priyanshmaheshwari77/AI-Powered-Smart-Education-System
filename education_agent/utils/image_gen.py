import requests
import os
import base64
import time
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

def generate_image(prompt: str):
    """
    Generate an image using Pollinations.ai — optimized for speed.
    """
    max_retries = 2  # Reduced from 3
    
    try:
        clean_prompt = prompt.strip().replace("\n", " ")
        encoded_prompt = urllib.parse.quote(clean_prompt)
        
        seed = os.urandom(4).hex()
        # Reduced from 1024x1024 to 512x512 for faster generation
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed={seed}"
        
        print(f"--- [DEBUG] Fetching image: {clean_prompt[:40]}... ---")

        for attempt in range(max_retries):
            try:
                response = requests.get(image_url, timeout=15)  # Reduced from 30s
                
                if response.status_code == 200:
                    print(f"--- [DEBUG] Success on attempt {attempt + 1} ---")
                    return base64.b64encode(response.content).decode('utf-8')
                else:
                    print(f"Attempt {attempt + 1} failed with status {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} error: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(1)  # Reduced from 2s
                
        return None
            
    except Exception as e:
        print(f"Image generation exception: {e}")
        return None
