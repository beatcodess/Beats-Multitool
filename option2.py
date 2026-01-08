#!/usr/bin/env python3

import requests
import os
import sys
import re
import time


SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()


ASCII_ART = """\033[97m     _      _      \033[95m _            
\033[97m  __| | ___| | ___ \033[95m| |_ ___ _ __ 
\033[97m / _` |/ _ \\ |/ _ \\\033[95m| __/ _ \\ '__|
\033[97m| (_| |  __/ |  __/\033[95m | ||  __/ |   
\033[97m \\__,_|\\___|_|\\___|_\033[95m|\\__\\___|_|   \033[0m
"""

ANSI_WHITE = "\033[97m"
ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_PURPLE = "\033[95m"
ANSI_CYAN = "\033[36m"
ANSI_RESET = "\033[0m"

def print_green(text):
    print(f"{ANSI_GREEN}{text}{ANSI_RESET}")

def print_red(text):
    print(f"{ANSI_RED}{text}{ANSI_RESET}")

def print_white(text):
    print(f"{ANSI_WHITE}{text}{ANSI_RESET}")

def print_purple(text):
    print(f"{ANSI_PURPLE}{text}{ANSI_RESET}")

def validate_webhook_url(url):
    """Validate if URL is a proper Discord webhook"""
    discord_webhook_pattern = r'https://discord(?:app)?\.com/api/webhooks/\d+/[\w-]+'
    return re.match(discord_webhook_pattern, url) is not None

def delete_webhook(webhook_url):
    """Delete a single webhook with improved error handling"""
    try:
        
        if not validate_webhook_url(webhook_url):
            print_red(f"❌ Invalid Discord webhook URL: {webhook_url}")
            print_white("   Expected format: https://discord.com/api/webhooks/...")
            return False
        
        
        response = SESSION.delete(webhook_url, timeout=10)
        
        if response.status_code == 204:
            print_green(f"✅ Webhook deleted successfully!")
            print_white(f"   {webhook_url}")
            return True
        elif response.status_code == 404:
            print_red(f"❌ Webhook not found (already deleted or invalid)")
            print_white(f"   {webhook_url}")
            return False
        elif response.status_code == 401:
            print_red(f"❌ Unauthorized - webhook token is invalid")
            print_white(f"   {webhook_url}")
            return False
        else:
            print_red(f"❌ Failed to delete webhook (Status: {response.status_code})")
            print_white(f"   {webhook_url}")
            return False
            
    except requests.Timeout:
        print_red(f"❌ Request timed out")
        print_white(f"   {webhook_url}")
        return False
    except requests.RequestException as e:
        print_red(f"❌ Error: {type(e).__name__}")
        print_white(f"   {webhook_url}")
        return False

def delete_single_webhook():
    """Delete a single webhook"""
    print(f"{ANSI_WHITE}\n📋 Single Webho\033[95mok Deletion")
    webhook_url = input(f"{ANSI_WHITE}Enter webhook U\033[95mRL: {ANSI_RESET}").strip()
    
    if not webhook_url:
        print_red("No URL entered.")
        return
    
    print()  # Add spacing
    delete_webhook(webhook_url)

def delete_multiple_webhooks():
    """Delete multiple webhooks at once"""
    print(f"{ANSI_WHITE}\n📋 Multiple Webh\033[95mook Deletion")
    print(f"{ANSI_WHITE}Enter webhook UR\033[95mLs (one per line)")
    print(f"{ANSI_WHITE}Type 'done' when\033[95m finished\n")
    
    webhook_urls = []
    while True:
        url = input(f"{ANSI_WHITE}URL {len(webhook_urls) + 1}: {ANSI_RESET}").strip()
        
        if url.lower() == 'done':
            break
        
        if url:
            webhook_urls.append(url)
    
    if not webhook_urls:
        print_red("\n❌ No webhooks entered.")
        return
    
    print(f"{ANSI_WHITE}\n🚀 Deleting {len(webhook_urls)} webho\033[95mok(s)...\n")
    
    success_count = 0
    for i, url in enumerate(webhook_urls, 1):
        print(f"{ANSI_WHITE}[{i}/{len(webhook_urls)}]{ANSI_RESET}")
        if delete_webhook(url):
            success_count += 1
        print()  
    
    
    print(f"{ANSI_WHITE}{'=' * 25}\033[95m{'=' * 25}")
    print_green(f"✅ Successfully deleted: {success_count}/{len(webhook_urls)}")
    if success_count < len(webhook_urls):
        print_red(f"❌ Failed: {len(webhook_urls) - success_count}/{len(webhook_urls)}")

def show_menu():
    """Display main menu with tool description"""
    clear_console()
    print(ASCII_ART)
    print(f"{ANSI_CYAN}🗑️  Permanently remove Discord webhooks{ANSI_RESET}")
    print(f"{ANSI_WHITE}   Supports single or batch deletion\n{ANSI_RESET}")
    print(f"{ANSI_WHITE}╔═══════════════════\033[95m═══════════════════╗")
    print(f"{ANSI_WHITE}║     Discord Webho\033[95mok Deleter        ║")
    print(f"{ANSI_WHITE}╚═══════════════════\033[95m═══════════════════╝\n")
    print(f"{ANSI_WHITE}1. Delete single \033[95mwebhook")
    print(f"{ANSI_WHITE}2. Delete multipl\033[95me webhooks")
    print(f"{ANSI_WHITE}q. Quit\n{ANSI_RESET}")

def main():
    """Main application loop"""
    while True:
        show_menu()
        choice = input(f"{ANSI_WHITE}Choice >> {ANSI_RESET}").strip().lower()
        
        if choice == '1':
            delete_single_webhook()
            input(f"\n{ANSI_WHITE}Press Enter to c\033[95montinue...{ANSI_RESET}")
        
        elif choice == '2':
            delete_multiple_webhooks()
            input(f"\n{ANSI_WHITE}Press Enter to c\033[95montinue...{ANSI_RESET}")
        
        elif choice == 'q':
            clear_console()
            print(f"{ANSI_WHITE}\n👋 Good\033[95mbye!\n{ANSI_RESET}")
            sys.exit(0)
        
        else:
            print_red("\n❌ Invalid choice. Please enter 1, 2, or q.")
            input(f"\n{ANSI_WHITE}Press Enter to c\033[95montinue...{ANSI_RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{ANSI_WHITE}\n\n👋 Interrupted. \033[95mGoodbye!\n{ANSI_RESET}")
        sys.exit(0)