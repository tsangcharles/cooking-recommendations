from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class FlyerDownloader:
    def __init__(self, driver, output_dir="data"):
        self.driver = driver
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def download_flyers(self):
        """Navigate to Flipp No Frills page and save all JPG images"""
        try:
            print("Navigating to No Frills flyers on Flipp...")
            flyer_url = "https://flipp.com/search/No%20Frills"
            self.driver.get(flyer_url)
            
            # Wait for page to load
            print("Waiting for flyer images to load...")
            time.sleep(10)
            
            # Wait for page to be fully loaded
            try:
                WebDriverWait(self.driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(5)
                print("Page loaded!")
            except Exception as e:
                print(f"Timeout waiting for page: {e}")
            
            print(f"Current URL: {self.driver.current_url}")
            
            # Get ALL resources loaded on the page including images
            print("Extracting all .jpg image URLs from page...")
            
            # Use performance API to get all loaded resources
            all_resources = self.driver.execute_script("""
                var resources = performance.getEntriesByType('resource');
                var imageUrls = [];
                
                // Get from performance API - look for extra_large*.jpg
                for(var i = 0; i < resources.length; i++) {
                    var url = resources[i].name;
                    if(url.includes('extra_large') && url.toLowerCase().endsWith('.jpg')) {
                        imageUrls.push(url);
                    }
                }
                
                // Also get from img tags - look for extra_large*.jpg
                var images = document.getElementsByTagName('img');
                for(var i = 0; i < images.length; i++) {
                    var src = images[i].src;
                    if(src && src.includes('extra_large') && src.toLowerCase().endsWith('.jpg')) {
                        imageUrls.push(src);
                    }
                }
                
                // Remove duplicates
                return [...new Set(imageUrls)];
            """)
            
            print(f"Found {len(all_resources)} extra_large*.jpg image URLs")
            
            if not all_resources:
                print("No extra_large*.jpg images found! Trying to find all images with 'extra_large' in the name...")
                # Fallback: get all img src attributes that contain 'extra_large'
                all_resources = self.driver.execute_script("""
                    var images = document.getElementsByTagName('img');
                    var urls = [];
                    for(var i = 0; i < images.length; i++) {
                        if(images[i].src && images[i].src.includes('extra_large')) {
                            urls.push(images[i].src);
                        }
                    }
                    return urls;
                """)
                print(f"Found {len(all_resources)} images with 'extra_large' in the name")
            
            # Filter URLs first
            filtered_urls = []
            for img_url in all_resources:
                if 'extra_large' in img_url.lower() and (img_url.lower().endswith('.jpg') or img_url.lower().endswith('.jpeg')):
                    filtered_urls.append(img_url)
            
            print(f"Downloading {len(filtered_urls)} images (20 concurrent downloads)...")
            
            # Function to download a single image
            def download_image(args):
                idx, img_url = args
                try:
                    # Add headers to mimic a browser
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Referer': 'https://flipp.com/'
                    }
                    
                    response = requests.get(img_url, timeout=30, headers=headers)
                    if response.status_code == 200:
                        file_size = len(response.content)
                        
                        # If we found an extra_large image, download it no matter the size
                        filename = os.path.join(self.output_dir, f"flyer_page_{idx+1:02d}.jpg")
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f"✓ Saved: {filename} ({file_size/1024:.1f} KB)")
                        return filename
                    else:
                        print(f"✗ Failed: HTTP {response.status_code} for image {idx+1}")
                        return None
                        
                except Exception as e:
                    print(f"✗ Error downloading image {idx+1}: {e}")
                    return None
            
            # Download images concurrently (20 at a time)
            downloaded_files = []
            with ThreadPoolExecutor(max_workers=20) as executor:
                # Submit all download tasks
                future_to_url = {executor.submit(download_image, (i, url)): url for i, url in enumerate(filtered_urls)}
                
                # Collect results as they complete
                for future in as_completed(future_to_url):
                    result = future.result()
                    if result:
                        downloaded_files.append(result)
            
            # Sort downloaded files by name to maintain order
            downloaded_files = sorted(downloaded_files)
            
            print(f"\n{'='*60}")
            print(f"Successfully downloaded {len(downloaded_files)} flyer images")
            print(f"{'='*60}\n")
            
            # If we still have no images, save debug info
            if not downloaded_files:
                print("WARNING: No images downloaded!")
                print("\nSaving page HTML for debugging...")
                debug_file = os.path.join(self.output_dir, "page_debug.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print(f"Page source saved to: {debug_file}")
                
                # Print all image URLs found
                print(f"\nAll image URLs found ({len(all_resources)}):")
                for url in all_resources[:20]:
                    print(f"  - {url}")
                if len(all_resources) > 20:
                    print(f"  ... and {len(all_resources)-20} more")
            
            return downloaded_files
            
        except Exception as e:
            print(f"Error downloading flyers: {e}")
            import traceback
            traceback.print_exc()
            return []
