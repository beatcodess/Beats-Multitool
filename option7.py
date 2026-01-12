#!/usr/bin/env python3

import os
import sys
from pathlib import Path
try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("📦 Installing required packages...")
    os.system(f"{sys.executable} -m pip install Pillow numpy -q")
    from PIL import Image
    import numpy as np

ANSI = {
    "p": "\033[95m",
    "w": "\033[97m",
    "g": "\033[32m",
    "r": "\033[31m",
    "y": "\033[33m",
    "c": "\033[36m",
    "x": "\033[0m"
}

def c(t, k):
    return f"{ANSI[k]}{t}{ANSI['x']}"

def clr():
    os.system("cls" if os.name == "nt" else "clear")

BANNER = f"""{ANSI['w']}  ___ _                            {ANSI['p']}            _    _             
{ANSI['w']} / __| |_ ___ __ _ __ _ _ _  ___   {ANSI['p']}___ __ _ _ _  _| |__| |__  ___ _ _ 
{ANSI['w']} \\__ \\  _/ -_) _` / _` | ' \\/ _ \\ {ANSI['p']}(_-</ _| '_| || | '_ \\ '_ \\/ -_) '_|
{ANSI['w']} |___/\\__\\___|\\__, \\__,_|_||_\\___/ {ANSI['p']}/__/\\__|_|  \\_,_|_.__/_.__/\\___|_|  
{ANSI['w']}              |___/                {ANSI['p']}
{ANSI['x']}"""

def scrub_image(img_path, output_path):
    try:
        img = Image.open(img_path)
        
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        temp_jpeg = output_path.parent / f"{output_path.stem}_temp.jpg"
        img.save(temp_jpeg, format='JPEG', quality=95, optimize=True)
        
        cleaned_img = Image.open(temp_jpeg)
        cleaned_img.save(output_path, format='PNG')
        
        temp_jpeg.unlink()
        
        return True
    except Exception as e:
        print(c(f"✗ Error: {e}", "r"))
        return False

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def process_single_image(img_path):
    path = Path(img_path)
    
    if not path.exists():
        print(c(f"✗ File not found: {img_path}", "r"))
        return
    
    if path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
        print(c(f"✗ Not an image file", "r"))
        return
    
    output_path = path.parent / f"{path.stem}_clean.png"
    
    print(c(f"\n📄 Processing: {path.name}", "w"))
    print(c(f"   Size: {format_size(path.stat().st_size)}", "p"))
    print(c(f"\n🧹 Scrubbing steganography...", "w"))
    
    if scrub_image(img_path, output_path):
        new_size = output_path.stat().st_size
        print(c(f"\n✓ Cleaned successfully!", "g"))
        print(c(f"   Output: {output_path.name}", "w"))
        print(c(f"   Size: {format_size(new_size)}", "p"))
    else:
        print(c("\n✗ Scrubbing failed", "r"))

def process_folder(folder_path):
    path = Path(folder_path)
    
    if not path.is_dir():
        print(c(f"✗ Not a directory: {folder_path}", "r"))
        return
    
    files = [f for f in path.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']]
    
    if not files:
        print(c("✗ No images found", "r"))
        return
    
    print(c(f"\n📁 Found {len(files)} images", "w"))
    
    for i, img_file in enumerate(files, 1):
        print(c(f"\n{'─'*60}", "p"))
        print(c(f"[{i}/{len(files)}]", "w"))
        process_single_image(img_file)

def main():
    clr()
    print(BANNER)
    print(c("\n🧹 Remove steganography from images", "c"))
    print(c("   JPEG recompression destroys LSB data completely\n", "w"))
    
    while True:
        print(c("\n" + "─"*60, "p"))
        print(c("Options:", "p"))
        print(c("  1. Scrub single image", "w"))
        print(c("  2. Batch scrub folder", "w"))
        print(c("  3. Exit", "w"))
        
        choice = input(c("\n👉 Select option → ", "p")).strip()
        
        if choice == "1":
            path = input(c("\n📂 Image path → ", "w")).strip().strip('"').strip("'")
            if path:
                process_single_image(path)
                
        elif choice == "2":
            folder = input(c("\n📁 Folder path → ", "w")).strip().strip('"').strip("'")
            if folder:
                process_folder(folder)
                
        elif choice == "3":
            print(c("\n👋 Goodbye!", "p"))
            break
        else:
            print(c("✗ Invalid option", "r"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\n\n👋 Goodbye!", "p"))
