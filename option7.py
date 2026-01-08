#!/usr/bin/env python3

import os
import sys
import math
from pathlib import Path
from collections import Counter
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

BANNER = f"""{ANSI['w']}  ___ _                            {ANSI['p']}___      _          _           
{ANSI['w']} / __| |_ ___ __ _ __ _ _ _  ___  {ANSI['p']}|   \\ ___| |_ ___ __| |_ ___ _ _ 
{ANSI['w']} \\__ \\  _/ -_) _` / _` | ' \\/ _ \\ {ANSI['p']}| |) / -_)  _/ -_) _|  _/ _ \\ '_|
{ANSI['w']} |___/\\__\\___|\\__, \\__,_|_||_\\___/ {ANSI['p']}|___/\\___|\\__\\___|\\__|\\__\\___/_|  
{ANSI['w']}              |___/                {ANSI['p']}
{ANSI['x']}"""

def calculate_entropy(data):
    if len(data) == 0:
        return 0
    counter = Counter(data)
    length = len(data)
    entropy = 0
    for count in counter.values():
        prob = count / length
        entropy -= prob * math.log2(prob)
    return entropy

def lsb_analysis(img_path):
    try:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        data = np.array(img)
        height, width, channels = data.shape
        
        results = {
            'suspicious': False,
            'lsb_entropy': {},
            'bit_plane_anomalies': []
        }
        
        for channel_idx, channel_name in enumerate(['Red', 'Green', 'Blue']):
            channel_data = data[:, :, channel_idx]
            lsb_plane = channel_data & 1
            lsb_flat = lsb_plane.flatten()
            entropy = calculate_entropy(lsb_flat)
            results['lsb_entropy'][channel_name] = entropy
            
            if entropy > 0.9:
                results['suspicious'] = True
                results['bit_plane_anomalies'].append(
                    f"{channel_name} channel LSB has high entropy ({entropy:.4f})"
                )
            
            ones = np.sum(lsb_flat)
            zeros = len(lsb_flat) - ones
            ratio = ones / len(lsb_flat)
            
            if ratio < 0.45 or ratio > 0.55:
                if abs(ratio - 0.5) > 0.1:
                    results['bit_plane_anomalies'].append(
                        f"{channel_name} LSB ratio unusual: {ratio:.4f} (expected ~0.5)"
                    )
        
        return results
    except Exception as e:
        print(c(f"✗ Error analyzing LSB: {e}", "r"))
        return None

def chi_square_test(img_path):
    try:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        data = np.array(img)
        results = []
        
        for channel_idx, channel_name in enumerate(['Red', 'Green', 'Blue']):
            channel_data = data[:, :, channel_idx].flatten()
            even_odd_pairs = 0
            odd_even_pairs = 0
            
            for i in range(0, len(channel_data) - 1, 2):
                val1 = channel_data[i]
                val2 = channel_data[i + 1]
                if val1 % 2 == 0 and val2 % 2 == 1:
                    even_odd_pairs += 1
                elif val1 % 2 == 1 and val2 % 2 == 0:
                    odd_even_pairs += 1
            
            expected = (even_odd_pairs + odd_even_pairs) / 2
            if expected > 0:
                chi_square = ((even_odd_pairs - expected) ** 2 / expected + 
                            (odd_even_pairs - expected) ** 2 / expected)
                suspicious = chi_square > 3.841
                results.append({
                    'channel': channel_name,
                    'chi_square': chi_square,
                    'suspicious': suspicious
                })
        
        return results
    except Exception as e:
        print(c(f"✗ Error in chi-square test: {e}", "r"))
        return None

def visual_analysis(img_path, output_dir):
    try:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        data = np.array(img)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        created_files = []
        
        for channel_idx, channel_name in enumerate(['Red', 'Green', 'Blue']):
            channel_data = data[:, :, channel_idx]
            lsb_plane = (channel_data & 1) * 255
            lsb_img = Image.fromarray(lsb_plane.astype(np.uint8), mode='L')
            filename = f"lsb_{channel_name.lower()}.png"
            filepath = output_path / filename
            lsb_img.save(filepath)
            created_files.append(str(filepath))
        
        return created_files
    except Exception as e:
        print(c(f"✗ Error creating visual analysis: {e}", "r"))
        return []

def file_signature_check(img_path):
    try:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        data = np.array(img)
        lsb_data = []
        
        for channel_idx in range(3):
            channel_data = data[:, :, channel_idx]
            lsb_plane = channel_data & 1
            lsb_data.extend(lsb_plane.flatten())
        
        bytes_data = []
        for i in range(0, len(lsb_data) - 7, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | lsb_data[i + j]
            bytes_data.append(byte)
        
        signatures = {
            'PNG': [0x89, 0x50, 0x4E, 0x47],
            'JPEG': [0xFF, 0xD8, 0xFF],
            'GIF': [0x47, 0x49, 0x46],
            'ZIP': [0x50, 0x4B, 0x03, 0x04],
            'PDF': [0x25, 0x50, 0x44, 0x46],
            'RAR': [0x52, 0x61, 0x72, 0x21],
            'EXE': [0x4D, 0x5A],
            'MP3': [0x49, 0x44, 0x33],
        }
        
        found_signatures = []
        search_limit = min(1000, len(bytes_data))
        
        for file_type, sig in signatures.items():
            for i in range(search_limit - len(sig)):
                if bytes_data[i:i+len(sig)] == sig:
                    found_signatures.append({
                        'type': file_type,
                        'position': i
                    })
                    break
        
        return found_signatures
    except Exception as e:
        print(c(f"✗ Error checking file signatures: {e}", "r"))
        return []

def analyze_image(img_path):
    path = Path(img_path)
    
    if not path.exists():
        print(c(f"✗ File not found: {img_path}", "r"))
        return
    
    if path.suffix.lower() not in ['.png', '.bmp', '.tiff', '.tif']:
        print(c(f"✗ Unsupported format. Use PNG, BMP, or TIFF", "r"))
        print(c(f"  JPEGs destroy LSB data due to compression", "y"))
        return
    
    print(c(f"\n📄 Analyzing: {path.name}", "w"))
    print(c(f"   Size: {path.stat().st_size / 1024:.2f} KB", "p"))
    
    try:
        img = Image.open(img_path)
        print(c(f"   Dimensions: {img.width}x{img.height}", "w"))
        print(c(f"   Mode: {img.mode}", "p"))
    except Exception as e:
        print(c(f"✗ Cannot open image: {e}", "r"))
        return
    
    print(c("\n🔍 LSB Bit Plane ", "w") + c("Analysis", "p"))
    lsb_results = lsb_analysis(img_path)
    
    if lsb_results:
        print(c("\n   LSB Entropy ", "w") + c("by Channel:", "p"))
        for channel, entropy in lsb_results['lsb_entropy'].items():
            color = "y" if entropy > 0.9 else "g"
            status = "⚠️  HIGH" if entropy > 0.9 else "✓ Normal"
            print(c(f"   • {channel}: {entropy:.4f} ", "w") + c(f"{status}", color))
        
        if lsb_results['bit_plane_anomalies']:
            print(c("\n   ⚠️  Anomalies ", "y") + c("Detected:", "w"))
            for anomaly in lsb_results['bit_plane_anomalies']:
                print(c(f"   • {anomaly}", "y"))
        
        if lsb_results['suspicious']:
            print(c("\n   🚨 SUSPICIOUS: ", "r") + c("Possible hidden data", "w"))
        else:
            print(c("\n   ✓ No obvious ", "g") + c("LSB anomalies", "w"))
    
    print(c("\n🧪 Chi-Square ", "w") + c("Test", "p"))
    chi_results = chi_square_test(img_path)
    
    if chi_results:
        suspicious_channels = []
        for result in chi_results:
            status = "SUSPICIOUS" if result['suspicious'] else "Clean"
            color = "r" if result['suspicious'] else "g"
            print(c(f"   • {result['channel']}: χ²={result['chi_square']:.4f} ", "w") + c(f"{status}", color))
            if result['suspicious']:
                suspicious_channels.append(result['channel'])
        
        if suspicious_channels:
            print(c(f"\n   🚨 Chi-square test ", "r") + c(f"flagged: {', '.join(suspicious_channels)}", "w"))
        else:
            print(c("\n   ✓ Chi-square test ", "g") + c("passed", "w"))
    
    print(c("\n🔎 File Signature ", "w") + c("Search", "p"))
    signatures = file_signature_check(img_path)
    
    if signatures:
        print(c("   🚨 Found embedded ", "r") + c("file signatures:", "w"))
        for sig in signatures:
            print(c(f"   • {sig['type']} at ", "w") + c(f"byte {sig['position']}", "p"))
    else:
        print(c("   ✓ No file ", "g") + c("signatures found", "w"))
    
    print(c("\n💾 Visual ", "w") + c("Analysis", "p"))
    output_dir = path.parent / f"{path.stem}_lsb_analysis"
    visual_files = visual_analysis(img_path, output_dir)
    
    if visual_files:
        print(c(f"   ✓ Created LSB ", "g") + c(f"visualizations in:", "w"))
        print(c(f"   {output_dir}", "p"))
        for vf in visual_files:
            print(c(f"   • {Path(vf).name}", "w"))
    
    print(c("\n" + "─"*50, "p"))
    
    overall_suspicious = (
        (lsb_results and lsb_results['suspicious']) or
        (chi_results and any(r['suspicious'] for r in chi_results)) or
        (signatures and len(signatures) > 0)
    )
    
    if overall_suspicious:
        print(c("\n🚨 VERDICT: Image shows ", "r") + c("signs of steganography", "w"))
    else:
        print(c("\n✓ VERDICT: No strong ", "g") + c("evidence of steganography", "w"))

def main():
    clr()
    print(BANNER)
    print(c("\n🔎 Detect hidden data in images using LSB analysis", "c"))
    print(c("   Chi-square test, entropy, and file signature detection\n", "w"))
    
    while True:
        print(c("\n" + "─"*60, "p"))
        print(c("Options:", "p"))
        print(c("  1. Analyze image", "w"))
        print(c("  2. Exit", "w"))
        
        choice = input(c("\n👉 Select option → ", "p")).strip()
        
        if choice == "1":
            path = input(c("\n📂 Image path → ", "w")).strip().strip('"').strip("'")
            if path:
                analyze_image(path)
        elif choice == "2":
            print(c("\n👋 Goodbye!", "p"))
            break
        else:
            print(c("✗ Invalid option", "r"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\n\n👋 Goodbye!", "p"))