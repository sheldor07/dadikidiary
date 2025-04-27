import os
import sys
import io
from typing import List, Dict, Any, Tuple
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()
# Configuration
class Config:
    def __init__(self):
        # Azure Computer Vision configuration
        self.azure = {
            "endpoint": os.getenv("VISION_ENDPOINT"),
            "key": os.getenv("VISION_KEY")
        }

# Create an Image Analysis client
def get_client():
    config = Config().azure
    return ImageAnalysisClient(
        endpoint=config["endpoint"],
        credential=AzureKeyCredential(config["key"])
    )

# Helper functions for OCR processing
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
        client = get_client()
        
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
    Extract text content from the analysis result
    
    Args:
        result: The analysis result from Azure Computer Vision
        
    Returns:
        The extracted text content
    """
    extracted_content = ""
    
    if result.read is not None:
        for block in result.read.blocks:
            for line in block.lines:
                extracted_content += line.text + "\n"
    
    return extracted_content.strip()

# Main processing functions
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
                    combined_content += content + " "
                    print(f"Processed {image_file}")
                except Exception as e:
                    print(f"Error processing {image_file}: {str(e)}")
            
            if combined_content:
                results.append({
                    "title": title,
                    "content": combined_content.strip()
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
                        "content": content
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
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, f"{title}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Saved extracted text to {file_path}")

async def main() -> None:
    """
    Main function to process all images in the 'images' folder
    """
    try:
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        
        # Check if images directory exists
        if not os.path.exists(images_dir):
            print(f"Error: Directory '{images_dir}' does not exist")
            return
        
        print(f"Processing images from {images_dir}")
        results = await process_directory(images_dir)
        
        print(f"Processed {len(results)} items")
        
        # Save all results to files
        for result in results:
            save_to_file(result["title"], result["content"])
        
        print('Processing complete!')
    except Exception as e:
        print(f"Error in main function: {str(e)}")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
