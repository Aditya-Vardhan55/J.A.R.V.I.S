import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

async def query_api(payload):
    """Sends a single request to the Hugging Face API."""
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

async def generate_images(prompt: str):
    """Creates and runs tasks to generate 4 images based on the prompt."""
    print(f"Starting generation for prompt: '{prompt}'")
    tasks = []
    
    for i in range(4):
        payload = {
            "inputs": f"{prompt}, 4k, high-resolution, photorealistic, seed={randint(0, 1000000)}",
        }
        tasks.append(query_api(payload))
        
    image_bytes_list = await asyncio.gather(*tasks)
    
    saved_paths = []
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            image_path = os.path.join("Data", f"{prompt.replace(' ', '_')}.{i + 1}.jpg")
            try:
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Successfully saved {image_path}")
                saved_paths.append(image_path)
            except Exception as e:
                print(f"Error saving image {i+1}: {e}")
    
    return saved_paths

def open_images(image_paths):
    """Opens a list of image files."""
    print("Opening generated images...")
    for path in image_paths:
        try:
            img = Image.open(path)
            img.show()
            sleep(1) 
        except IOError:
            print(f"Unable to open {path}")


if __name__ == "__main__":
    while True:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
                data = f.read().strip()
            
            if data and ",True" in data:
                prompt, _ = data.split(",", 1)
                
                generated_files = asyncio.run(generate_images(prompt=prompt))
                
                if generated_files:
                    open_images(generated_files)
                
                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False,False")
                
                break 
            
            else:
                sleep(1) 

        except FileNotFoundError:
            print("Waiting for ImageGeneration.data file...")
            sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break