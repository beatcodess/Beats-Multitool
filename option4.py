#!/usr/bin/env python3
import os, sys, shutil
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
try:
    from PyPDF2 import PdfReader, PdfWriter
except:
    print("📦 Installing PyPDF2...")
    os.system(f"{sys.executable} -m pip install PyPDF2 -q")
    from PyPDF2 import PdfReader, PdfWriter

ANSI={"p":"\033[95m","w":"\033[97m","g":"\033[32m","r":"\033[31m","y":"\033[33m","c":"\033[36m","x":"\033[0m"}
def c(t,k): return f"{ANSI[k]}{t}{ANSI['x']}"
def clr(): os.system("cls" if os.name=="nt" else "clear")
BANNER=f"""{ANSI['p']}  __  __      _            _       _        {ANSI['w']}  ___                _    _             
{ANSI['p']} |  \\/  | ___| |_ __ _  __| | __ _| |_ __ _ {ANSI['w']} / __| __ _ _ _  _| |__| |__  ___ _ _ 
{ANSI['p']} | |\\/| |/ -_)  _/ _` |/ _` |/ _` |  _/ _` |{ANSI['w']} \\__ \\/ _| '_| || | '_ \\ '_ \\/ -_) '_|
{ANSI['p']} |_|  |_|\\___|\\__\\__,_|\\__,_|\\__,_|\\__\\__,_|{ANSI['w']} |___/\\__|_|  \\_,_|_.__/_.__/\\___|_|  
{ANSI['x']}"""

def get_image_metadata(path):
    try:
        img=Image.open(path)
        exif=img._getexif()
        if not exif:
            return {}
        meta={}
        for tag_id,val in exif.items():
            tag=TAGS.get(tag_id,tag_id)
            meta[tag]=str(val)[:100]
        return meta
    except:
        return {}

def scrub_image(input_path,output_path):
    try:
        img=Image.open(input_path)
        data=list(img.getdata())
        clean=Image.new(img.mode,img.size)
        clean.putdata(data)
        clean.save(output_path,quality=95,optimize=True)
        return True
    except Exception as e:
        return False

def get_pdf_metadata(path):
    try:
        reader=PdfReader(path)
        meta=reader.metadata
        if not meta:
            return {}
        return {k:str(v)[:100] for k,v in meta.items()}
    except:
        return {}

def scrub_pdf(input_path,output_path):
    try:
        reader=PdfReader(input_path)
        writer=PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({})
        with open(output_path,'wb') as f:
            writer.write(f)
        return True
    except Exception as e:
        return False

def format_size(size):
    for unit in ['B','KB','MB','GB']:
        if size<1024:
            return f"{size:.2f} {unit}"
        size/=1024
    return f"{size:.2f} TB"

def process_file(path):
    p=Path(path)
    if not p.exists():
        print(c(f"❌ File not found: {path}","r"))
        return
    
    ext=p.suffix.lower()
    if ext not in ['.jpg','.jpeg','.png','.pdf']:
        print(c(f"❌ Unsupported format: {ext}","r"))
        print(c("   Supported: .jpg, .jpeg, .png, .pdf","w"))
        return
    
    print(c(f"\n📄 Processing: {p.name}","p"))
    print(c(f"   Size: {format_size(p.stat().st_size)}","w"))
    
    if ext in ['.jpg','.jpeg','.png']:
        meta=get_image_metadata(path)
        print(c(f"\n🔍 Found {len(meta)} metadata fields:","p"))
        if meta:
            for k,v in list(meta.items())[:10]:
                print(c(f"   • {k}: {v}","w"))
            if len(meta)>10:
                print(c(f"   ... and {len(meta)-10} more","y"))
        else:
            print(c("   ✅ No metadata found","g"))
        
        temp_output=p.parent/f"{p.stem}_temp{p.suffix}"
        print(c(f"\n🧹 Scrubbing metadata...","p"))
        if scrub_image(path,temp_output):
            shutil.move(str(temp_output),str(p))
            new_size=p.stat().st_size
            print(c(f"✅ Cleaned: {p.name}","g"))
            print(c(f"   New size: {format_size(new_size)}","w"))
            
            check_meta=get_image_metadata(path)
            print(c(f"   Metadata fields: {len(check_meta)}","g" if len(check_meta)==0 else "y"))
        else:
            if temp_output.exists():
                temp_output.unlink()
            print(c("❌ Failed to scrub image","r"))
    
    elif ext=='.pdf':
        meta=get_pdf_metadata(path)
        print(c(f"\n🔍 Found {len(meta)} metadata fields:","p"))
        if meta:
            for k,v in meta.items():
                print(c(f"   • {k}: {v}","w"))
        else:
            print(c("   ✅ No metadata found","g"))
        
        temp_output=p.parent/f"{p.stem}_temp{p.suffix}"
        print(c(f"\n🧹 Scrubbing metadata...","p"))
        if scrub_pdf(path,temp_output):
            shutil.move(str(temp_output),str(p))
            new_size=p.stat().st_size
            print(c(f"✅ Cleaned: {p.name}","g"))
            print(c(f"   New size: {format_size(new_size)}","w"))
            
            check_meta=get_pdf_metadata(path)
            print(c(f"   Metadata fields: {len(check_meta)}","g" if len(check_meta)==0 else "y"))
        else:
            if temp_output.exists():
                temp_output.unlink()
            print(c("❌ Failed to scrub PDF","r"))

def batch_process(folder):
    p=Path(folder)
    if not p.is_dir():
        print(c(f"❌ Not a directory: {folder}","r"))
        return
    
    files=[f for f in p.iterdir() if f.suffix.lower() in ['.jpg','.jpeg','.png','.pdf']]
    if not files:
        print(c("❌ No supported files found","r"))
        return
    
    print(c(f"\n📁 Found {len(files)} files to process","p"))
    for i,f in enumerate(files,1):
        print(c(f"\n{'='*60}","p"))
        print(c(f"[{i}/{len(files)}]","w"))
        process_file(f)

def main():
    clr()
    print(BANNER)
    print(c("\n🔐 Remove hidden metadata from images & PDFs","c"))
    print(c("   Protects your privacy by cleaning EXIF, location, camera info, etc.\n","w"))
    
    while True:
        print(c("\n" + "─"*60,"p"))
        print(c("Options:","p"))
        print(c("  1. Scrub single file","w"))
        print(c("  2. Batch scrub folder","w"))
        print(c("  3. Exit","w"))
        
        choice=input(c("\n👉 Select option → ","p")).strip()
        
        if choice=="1":
            path=input(c("\n📂 File path → ","w")).strip().strip('"').strip("'")
            if path:
                process_file(path)
        elif choice=="2":
            folder=input(c("\n📁 Folder path → ","w")).strip().strip('"').strip("'")
            if folder:
                batch_process(folder)
        elif choice=="3":
            print(c("\n👋 Goodbye!","p"))
            break
        else:
            print(c("❌ Invalid option","r"))

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\n\n👋 Goodbye!","p"))