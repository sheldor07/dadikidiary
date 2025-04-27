#!/usr/bin/env python3
"""
DadiKi Diary - Image to WordPress Publisher
This script processes images using OCR and publishes the extracted text to WordPress.
"""

import os
import shutil
import asyncio
from utils.ocr_utils import process_directory, save_to_file
from utils.wordpress_utils import publish_to_wordpress

async def main():
    """
    Main function to process images and publish to WordPress
    """
    try:
        # Process images
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        
        # Check if images directory exists
        if not os.path.exists(images_dir):
            print(f"Error: Directory '{images_dir}' does not exist")
            return
        
        print(f"Processing images from {images_dir}")
        results = await process_directory(images_dir)
        
        print(f"Processed {len(results)} items")
        
        # Create processed directory if it doesn't exist
        processed_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
            print(f"Created processed directory at {processed_dir}")
        
        # Save all results to files and publish to WordPress
        for result in results:
            title = result["title"]
            content = result["content"]
            source_path = result.get("source_path")
            
            # Save to file
            save_to_file(title, content)
            
            # Publish to WordPress
            print(f"\nPublishing '{title}' to WordPress...")
            publish_url = publish_to_wordpress(title, content)
            
            if publish_url:
                print(f"Successfully published '{title}' to WordPress: {publish_url}")
                
                # Move the processed image(s) to the processed directory
                if source_path:
                    if os.path.isdir(source_path):
                        # If it's a directory, move all its contents
                        target_dir = os.path.join(processed_dir, os.path.basename(source_path))
                        if os.path.exists(target_dir):
                            # If target already exists, append timestamp to avoid conflicts
                            import time
                            target_dir = f"{target_dir}_{int(time.time())}"
                        shutil.move(source_path, target_dir)
                        print(f"Moved directory {source_path} to {target_dir}")
                    elif os.path.isfile(source_path):
                        # If it's a file, move it directly
                        target_file = os.path.join(processed_dir, os.path.basename(source_path))
                        if os.path.exists(target_file):
                            # If target already exists, append timestamp to avoid conflicts
                            import time
                            base, ext = os.path.splitext(target_file)
                            target_file = f"{base}_{int(time.time())}{ext}"
                        shutil.move(source_path, target_file)
                        print(f"Moved file {source_path} to {target_file}")
            else:
                print(f"Failed to publish '{title}' to WordPress")
        
        print('\nProcessing and publishing complete!')
    except Exception as e:
        print(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())