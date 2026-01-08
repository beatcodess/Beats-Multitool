#!/usr/bin/env python3

import requests
import os
import sys
import time
import json


SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()


ASCII_ART = """\033[97m  _                  \033[95m  _             
\033[97m | |_ _ __ __ _  ___\033[95m| | _____ _ __ 
\033[97m | __| '__/ _` |/ __\033[95m| |/ / _ \\ '__|
\033[97m | |_| | | (_| | (__\033[95m|   <  __/ |   
\033[97m  \\__|_|  \\__,_|\\___|_|\\_\\___|_|   \033[0m
"""

MENU = """
1. Username Tracker
q. Quit
"""

SITES = {
    "GitHub": [
        "https://github.com/{username}"
    ],
    "guns.lol": [
        "https://guns.lol/{username}",
        "https://guns.lol/u/{username}",
        "https://guns.lol/@{username}"
    ],
    "SoundCloud": [
        "https://soundcloud.com/{username}"
    ],
    "Reddit": [
        "https://www.reddit.com/user/{username}"
    ],
    "Medium": [
        "https://medium.com/@{username}"
    ],
    "Pinterest": [
        "https://www.pinterest.com/{username}"
    ],
    "Twitch": [
        "https://www.twitch.tv/{username}"
    ],
    "Instagram": [
        "https://www.instagram.com/{username}"
    ],
    "Twitter/X": [
        "https://twitter.com/{username}"
    ],
    "YouTube": [
        "https://www.youtube.com/@{username}",
        "https://www.youtube.com/c/{username}",
        "https://www.youtube.com/user/{username}"
    ],
    "Imgur": [
        "https://imgur.com/user/{username}"
    ]
}

TIMEOUT = 5
MAX_RETRIES = 2

def print_white(text=""):
    print(f"\033[97m{text}\033[0m")

def print_green(text=""):
    print(f"\033[32m{text}\033[0m")

def print_red(text=""):
    print(f"\033[31m{text}\033[0m")

def print_purple(text=""):
    print(f"\033[95m{text}\033[0m")

def print_cyan(text=""):
    print(f"\033[36m{text}\033[0m")

def check_url(url, retries=MAX_RETRIES):
    """Check if URL exists with retry logic and exponential backoff"""
    try:
        resp = SESSION.head(url, timeout=TIMEOUT, allow_redirects=True)
        
      
        if resp.status_code in (405, 501):
            resp = SESSION.get(url, timeout=TIMEOUT, allow_redirects=True)
        
        return True, resp.status_code, resp.url, None
    
    except requests.RequestException as e:
        if retries > 0:
            delay = (MAX_RETRIES - retries + 1) ** 2  
            print_red(f"[!] Error accessing {url}: {type(e).__name__}. Retrying in {delay}s...")
            time.sleep(delay)
            return check_url(url, retries - 1)
        else:
            return False, None, None, str(e)

def check_username_on_sites(username):
    """Check username across multiple sites"""
    print_purple(f"\nChecking username: '{username}'\n")
    results = []
    found_any = False

    for site, patterns in SITES.items():
        for pat in patterns:
            url = pat.format(username=username)
            ok, status, final, err = check_url(url)
            
            result_text = ""
            
            if ok:
                if status == 200:
                    result_text = f"[+] {site}: {url}  (HTTP {status})"
                    print_green(result_text)
                    found_any = True
                elif status in (301, 302, 303, 307, 308):
                    result_text = f"[+] {site}: {url}  (redirect HTTP {status})"
                    print_green(result_text)
                    found_any = True
                elif status in (401, 403):
                    result_text = f"[~] {site}: {url}  (HTTP {status} – access restricted)"
                    print_green(result_text)
                    found_any = True
                elif status == 404:
                    result_text = f"[-] {site}: Not found"
                    print_red(result_text)
                else:
                    result_text = f"[?] {site}: {url}  (HTTP {status})"
                    print_white(result_text)
            else:
                result_text = f"[!] {site}: Error - {err}"
                print_red(result_text)
            
            results.append(result_text)
            time.sleep(0.3)  

    if not found_any:
        print_white("\n❌ No profiles found.")
    else:
        print_white("\n✅ Found potential profiles above!")
        
        
        save = input("\n\033[97mSave results to file? (y/n) >> \033[0m").strip().lower()
        if save == 'y':
            filename = f"{username}_results.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Username Search Results: {username}\n")
                f.write("=" * 50 + "\n\n")
                f.write("\n".join(results))
            print_green(f"\n💾 Results saved to {filename}")

def show_menu_and_get_choice():
    """Display menu with tool description and get user choice"""
    clear_console()
    print(ASCII_ART)
    print_cyan("🔍 Search for usernames across multiple platforms")
    print_white("   Discover social media profiles and online presence\n")
    print_white(MENU)
    try:
        choice = input("\033[97mChoice >> \033[0m").strip()
        return choice
    except (KeyboardInterrupt, EOFError):
        print()
        return "q"

def main():
    """Main application loop"""
    while True:
        choice = show_menu_and_get_choice()

        if choice == "1":
            username = input("\033[97mUsername >> \033[0m").strip()
            
            if not username:
                print_red("\n❌ No username entered.")
                input("\nPress Enter to continue...")
                continue

            clear_console()
            print(ASCII_ART)
            check_username_on_sites(username)
            input("\n\033[97mPress Enter to return to menu...\033[0m")

        elif choice == "q":
            clear_console()
            print_purple("\n👋 Goodbye!\n")
            break

        else:
            print_red("\n❌ Invalid choice – enter 1 or q.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()