#!/usr/bin/env python3

import requests
import time
import os
import threading

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})


ASCII_ART = """\033[97m                                \033[95m                
\033[97m  ___ _ __   __ _ _ __ ___  _ __ \033[95m___   ___ _ __ 
\033[97m / __| '_ \\ / _` | '_ ` _ \\| '_ \\\033[95m _ \\ / _ \\ '__|
\033[97m \\__ \\ |_) | (_| | | | | | | | | \033[95m | |  __/ |   
\033[97m |___/ .__/ \\__,_|_| |_| |_|_| |_\033[95m|_|\\___|_|   
\033[97m     |_|                         \033[95m             \033[0m
"""


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_WHITE = "\033[97m"
ANSI_PURPLE = "\033[95m"
ANSI_CYAN = "\033[36m"
ANSI_RESET = "\033[0m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_title(title):
    print(f"\033]0;{title}\007", end='', flush=True)

def print_green(text):
    print(f"{ANSI_GREEN}{text}{ANSI_RESET}")

def print_red(text):
    print(f"{ANSI_RED}{text}{ANSI_RESET}")

def validate_webhook(webhook_url):
    """Test if webhook is valid by sending empty request"""
    try:
        response = SESSION.post(webhook_url, json={'content': ""}, timeout=5)
        return response.status_code in (200, 204)
    except Exception:
        return False

def spam_webhook(webhook_url, message):
    """Send a single message to webhook"""
    try:
        SESSION.post(webhook_url, json={'content': message}, timeout=5)
    except Exception as e:
        print_red(f"❌ Error: {type(e).__name__}")

def show_banner():
    """Display banner with tool description"""
    clear()
    print(ASCII_ART)
    print(f"{ANSI_CYAN}💬 Flood Discord webhooks with custom messages{ANSI_RESET}")
    print(f"{ANSI_WHITE}   Multi-threaded rapid message delivery\n{ANSI_RESET}")
    print(f"{ANSI_WHITE}╔═══════════════════\033[95m═══════════════════╗")
    print(f"{ANSI_WHITE}║   Discord Webhook\033[95m Spammer           ║")
    print(f"{ANSI_WHITE}╚═══════════════════\033[95m═══════════════════╝\n{ANSI_RESET}")

def webhook_spammer():
    """Main webhook spammer function"""
    set_title("Webhook Spammer")
    show_banner()

    while True:
        
        print(f"{ANSI_WHITE}Webhook URL (or \033[95m'q' to quit):")
        webhook = input(f"{ANSI_WHITE}-> {ANSI_RESET}").strip()

        if webhook.lower() == 'q':
            print(f"{ANSI_WHITE}\n👋 Good\033[95mbye!\n{ANSI_RESET}")
            break

        
        print(f"{ANSI_WHITE}\n🔍 Validating we\033[95mbhook...{ANSI_RESET}")
        if not validate_webhook(webhook):
            print_red("\n❌ Invalid webhook! Check the URL and try again.")
            input(f"\n{ANSI_WHITE}Press Enter to c\033[95montinue...{ANSI_RESET}")
            show_banner()
            continue

        print_green("✅ Webhook is valid!")

        
        print(f"\n{ANSI_WHITE}Enter message to\033[95m spam:")
        message = input(f"{ANSI_WHITE}Message -> {ANSI_RESET}").strip()

        if not message:
            print_red("\n❌ Message cannot be empty!")
            input(f"\n{ANSI_WHITE}Press Enter to c\033[95montinue...{ANSI_RESET}")
            show_banner()
            continue

        
        print(f"\n{ANSI_WHITE}Number of message\033[95ms to send:")
        try:
            amount = int(input(f"{ANSI_WHITE}Amount -> {ANSI_RESET}").strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            print_red("\n❌ Invalid amount! Enter a positive number.")
            input(f"\n{ANSI_WHITE}Press Enter to c\033[95montinue...{ANSI_RESET}")
            show_banner()
            continue

        # Confirm spam
        print(f"\n{ANSI_WHITE}Ready to send {amount} message\033[95m(s)")
        confirm = input(f"{ANSI_WHITE}Continue? (y/n) -\033[95m> {ANSI_RESET}").strip().lower()
        
        if confirm != 'y':
            print(f"{ANSI_WHITE}\n❌ Cancelled\033[95m.{ANSI_RESET}")
            input(f"\n{ANSI_WHITE}Press Enter to c\033[95montinue...{ANSI_RESET}")
            show_banner()
            continue

        
        print(f"\n{ANSI_WHITE}🚀 Sending message\033[95ms...{ANSI_RESET}\n")
        
        threads = []
        for i in range(amount):
            thread = threading.Thread(target=spam_webhook, args=(webhook, message), daemon=True)
            thread.start()
            threads.append(thread)
            
            
            if (i + 1) % 10 == 0 or i == amount - 1:
                print(f"{ANSI_WHITE}[{i + 1}/{amount}] Sent{ANSI_RESET}")
            
            time.sleep(0.05)  

        
        for thread in threads:
            thread.join(timeout=10)

        show_banner()
        print_green(f"\n✅ Successfully sent {amount} message(s)!")
        
        
        print(f"\n{ANSI_WHITE}1. Spam another \033[95mwebhook")
        print(f"{ANSI_WHITE}q. Quit{ANSI_RESET}\n")
        
        choice = input(f"{ANSI_WHITE}Choice -> {ANSI_RESET}").strip().lower()
        
        if choice == 'q':
            print(f"{ANSI_WHITE}\n👋 Good\033[95mbye!\n{ANSI_RESET}")
            break
        elif choice == '1':
            show_banner()
            continue
        else:
            show_banner()
            continue

if __name__ == "__main__":
    try:
        webhook_spammer()
    except KeyboardInterrupt:
        print(f"{ANSI_WHITE}\n\n👋 Interrupted. \033[95mGoodbye!\n{ANSI_RESET}")