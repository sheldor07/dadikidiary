#!/usr/bin/env python3
"""
DadiKi Diary - OCR Utilities
This module provides functions for processing images using Azure AI Vision OCR.
"""

import io
from typing import List, Dict
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OCRConfig:
    def __init__(self):
        self.azure = {
            "endpoint": os.getenv("VISION_ENDPOINT"),
            "key": os.getenv("VISION_KEY")
        }

def get_vision_client():
    """Create an Image Analysis client"""
    config = OCRConfig().azure
    return ImageAnalysisClient(
        endpoint=config["endpoint"],
        credential=AzureKeyCredential(config["key"])
    )

def process_image_ocr(file_buffer: bytes) -> str:
    """
    Process an image using Azure Computer Vision OCR
    
    Args:
        file_buffer: The image file as bytes
        
    Returns:
        The extracted text content
    """
    try:
        # Create a client
        client = get_vision_client()
        
        # Create a BytesIO object from the file buffer
        image_stream = io.BytesIO(file_buffer)
        
        # Analyze the image for text (READ feature)
        result = client.analyze(
            image_data=image_stream,
            visual_features=[VisualFeatures.READ],
        )
        
        # Extract text from the result
        return extract_content(result)
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise

def extract_content(result) -> str:
    """
    Extract text content from the analysis result with intelligent text wrapping.
    Adds line breaks after sentence ending punctuation (e.g., '.' or '|')
    
    Args:
        result: The analysis result from Azure Computer Vision
        
    Returns:
        The extracted text content with proper text wrapping
    """
    extracted_content = ""
    current_paragraph = ""
    
    if result.read is not None:
        for block in result.read.blocks:
            for line in block.lines:
                text = line.text.strip()
                
                # Add space between lines unless the current paragraph is empty
                if current_paragraph and not current_paragraph.endswith(' '):
                    current_paragraph += " "
                
                current_paragraph += text
                
                # Check if the text ends with a sentence delimiter
                if text.endswith('.') or text.endswith('।') or text.endswith('|'):
                    extracted_content += current_paragraph + "\n"
                    current_paragraph = ""
    
    # Add any remaining text
    if current_paragraph:
        extracted_content += current_paragraph
    
    return extracted_content.strip()

async def process_image(file_buffer: bytes) -> str:
    """
    Process a single image file using OCR
    
    Args:
        file_buffer: The image file as bytes
        
    Returns:
        The extracted text content
    """
    try:
        print('Analyzing document...')
        return process_image_ocr(file_buffer)
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise

async def process_directory(dir_path: str) -> List[Dict[str, str]]:
    """
    Process all images in a directory
    
    Args:
        dir_path: Path to the directory containing images
        
    Returns:
        List of dictionaries with title and content
    """
    results = []
    items = os.listdir(dir_path)
    
    for item in items:
        item_path = os.path.join(dir_path, item)
        
        if os.path.isdir(item_path):
            # If it's a directory, process all images inside as one entry
            title = os.path.basename(item_path)
            combined_content = ""
            
            # Filter for image files
            image_files = [f for f in os.listdir(item_path) if os.path.splitext(f)[1].lower() 
                          in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')]
            
            print(f"Processing folder {title} with {len(image_files)} images")
            
            for image_file in image_files:
                image_path = os.path.join(item_path, image_file)
                with open(image_path, 'rb') as f:
                    file_buffer = f.read()
                
                try:
                    content = await process_image(file_buffer)
                    combined_content += content + "\n\n"
                    print(f"Processed {image_file}")
                except Exception as e:
                    print(f"Error processing {image_file}: {str(e)}")
            
            if combined_content:
                results.append({
                    "title": title,
                    "content": combined_content.strip(),
                    "source_path": item_path
                })
        
        elif os.path.isfile(item_path):
            # If it's a file, check if it's an image and process it
            ext = os.path.splitext(item)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'):
                title = os.path.splitext(item)[0]
                
                with open(item_path, 'rb') as f:
                    file_buffer = f.read()
                
                try:
                    print(f"Processing image {item}")
                    content = await process_image(file_buffer)
                    results.append({
                        "title": title,
                        "content": content,
                        "source_path": item_path
                    })
                except Exception as e:
                    print(f"Error processing {item}: {str(e)}")
    
    return results

def save_to_file(title: str, content: str) -> None:
    """
    Save the extracted text content to a file
    
    Args:
        title: The title to use for the filename
        content: The text content to save
    """
    # Get the parent directory (src) and then add 'output'
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, f"{title}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Saved extracted text to {file_path}")