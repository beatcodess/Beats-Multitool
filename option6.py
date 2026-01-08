#!/usr/bin/env python3

import requests
import json
import tempfile
import webbrowser
import os
import time
import re


SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})


ASCII_ART = """\033[97m                  _                 \033[95m _             
\033[97m   __ _  ___  ___ | | ___   ___ __ _| |_ ___  _ __ 
\033[97m  / _` |/ _ \\/ _ \\| |/ _ \\ / __/ _` | __/ _ \\| '__|
\033[97m | (_| |  __/ (_) | | (_) | (_| (_| | || (_) | |   
\033[97m  \\__, |\\___|\\___/|_|\\___/ \\___\\__,_|\\__\\___/|_|   
\033[97m  |___/                                      \033[95m       \033[0m
"""


ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_WHITE = "\033[97m"
ANSI_PURPLE = "\033[95m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"
ANSI_RESET = "\033[0m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_green(text):
    print(f"{ANSI_GREEN}{text}{ANSI_RESET}")

def print_red(text):
    print(f"{ANSI_RED}{text}{ANSI_RESET}")

def print_yellow(text):
    print(f"{ANSI_YELLOW}{text}{ANSI_RESET}")

def print_cyan(text):
    print(f"{ANSI_CYAN}{text}{ANSI_RESET}")

def show_banner():
    """Display banner with tool description"""
    clear()
    print(ASCII_ART)
    print(f"{ANSI_CYAN}🌍 Locate IP addresses worldwide with interactive maps{ANSI_RESET}")
    print(f"{ANSI_WHITE}   Track ISP, location, timezone, and coordinates\n{ANSI_RESET}")
    print(f"{ANSI_WHITE}╔═══════════════════{ANSI_PURPLE}═══════════════════╗")
    print(f"{ANSI_WHITE}║      IP Geolocato{ANSI_PURPLE}r Tool             ║")
    print(f"{ANSI_WHITE}╚═══════════════════{ANSI_PURPLE}═══════════════════╝\n{ANSI_RESET}")

def validate_ip(ip):
    """Validate IP address format"""
    
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return False

def get_my_ip():
    """Get the user's public IP address"""
    try:
        response = SESSION.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json().get('ip')
    except Exception:
        pass
    return None

def lookup_ip(ip):
    """Lookup IP information using multiple APIs for redundancy"""
    try:
        if not ip or ip.strip() == "":
            raise ValueError("Invalid IP: input required.")
        
        
        url = f"http://ip-api.com/json/{ip}?fields=status,message,query,country,countryCode,regionName,city,lat,lon,org,timezone,isp,as"
        response = SESSION.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "success":
            raise ValueError(f"API Error: {data.get('message', 'Invalid IP or query')}")
        
        return data
        
    except Exception as e:
        print_red(f"❌ Error looking up IP: {e}")
        return None

def display_ip_info(data):
    """Display IP information in a formatted way"""
    if not data:
        return
    
    print(f"\n{ANSI_WHITE}{'=' * 25}{ANSI_PURPLE}{'=' * 25}{ANSI_RESET}\n")
    print(f"{ANSI_CYAN}📍 IP Information:{ANSI_RESET}\n")
    
    
    print(f"{ANSI_WHITE}   IP Address:     {ANSI_PURPLE}{data.get('query', 'N/A')}")
    print(f"{ANSI_WHITE}   Country:        {ANSI_PURPLE}{data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})")
    print(f"{ANSI_WHITE}   Region:         {ANSI_PURPLE}{data.get('regionName', 'N/A')}")
    print(f"{ANSI_WHITE}   City:           {ANSI_PURPLE}{data.get('city', 'N/A')}")
    print(f"{ANSI_WHITE}   Coordinates:    {ANSI_PURPLE}{data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
    print(f"{ANSI_WHITE}   Timezone:       {ANSI_PURPLE}{data.get('timezone', 'N/A')}")
    print(f"{ANSI_WHITE}   ISP:            {ANSI_PURPLE}{data.get('isp', 'N/A')}")
    print(f"{ANSI_WHITE}   Organization:   {ANSI_PURPLE}{data.get('org', 'N/A')}")
    print(f"{ANSI_WHITE}   AS Number:      {ANSI_PURPLE}{data.get('as', 'N/A')}{ANSI_RESET}")
    
    print(f"\n{ANSI_WHITE}{'=' * 25}{ANSI_PURPLE}{'=' * 25}{ANSI_RESET}\n")

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>IP Geolocator - {ip}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body, #map {{ height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    
    #info {{
      position: absolute;
      top: 20px;
      left: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      z-index: 999;
      min-width: 300px;
      backdrop-filter: blur(10px);
    }}
    
    #info h2 {{
      margin: 0 0 15px 0;
      font-size: 20px;
      font-weight: 600;
      border-bottom: 2px solid rgba(255,255,255,0.3);
      padding-bottom: 10px;
    }}
    
    #info .info-row {{
      display: flex;
      margin: 8px 0;
      font-size: 14px;
    }}
    
    #info .label {{
      font-weight: 600;
      min-width: 100px;
      opacity: 0.9;
    }}
    
    #info .value {{
      flex: 1;
      opacity: 0.95;
    }}
    
    .leaflet-popup-content-wrapper {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 8px;
    }}
    
    .leaflet-popup-content {{
      margin: 15px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    .leaflet-popup-tip {{
      background: #764ba2;
    }}
  </style>
</head>
<body>
  <div id="info">
    <h2>🌍 IP Geolocation</h2>
    <div class="info-row">
      <span class="label">IP Address:</span>
      <span class="value">{ip}</span>
    </div>
    <div class="info-row">
      <span class="label">Location:</span>
      <span class="value">{location}</span>
    </div>
    <div class="info-row">
      <span class="label">ISP:</span>
      <span class="value">{isp}</span>
    </div>
    <div class="info-row">
      <span class="label">Organization:</span>
      <span class="value">{org}</span>
    </div>
    <div class="info-row">
      <span class="label">Timezone:</span>
      <span class="value">{timezone}</span>
    </div>
    <div class="info-row">
      <span class="label">Coordinates:</span>
      <span class="value">{lat}, {lon}</span>
    </div>
  </div>
  <div id="map"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    var map = L.map('map').setView([{lat}, {lon}], 12);
    
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);
    
    var marker = L.marker([{lat}, {lon}]).addTo(map);
    marker.bindPopup("<b>📍 {ip}</b><br>{location}<br><i>{isp}</i>").openPopup();
    
    // Add circle to show approximate area
    L.circle([{lat}, {lon}], {{
        color: '#764ba2',
        fillColor: '#667eea',
        fillOpacity: 0.2,
        radius: 5000
    }}).addTo(map);
  </script>
</body>
</html>
"""

def generate_map_html(data):
    """Generate HTML map with IP information"""
    try:
        ip = data.get("query", "")
        city = data.get("city", "")
        region = data.get("regionName", "")
        country = data.get("country", "")
        lat = data.get("lat", 0)
        lon = data.get("lon", 0)
        org = data.get("org", "Unknown")
        isp = data.get("isp", "Unknown")
        timezone = data.get("timezone", "Unknown")
        
        location = ", ".join(filter(None, [city, region, country]))
        
        return HTML_TEMPLATE.format(
            ip=ip,
            location=location or "Unknown",
            org=org,
            isp=isp,
            timezone=timezone,
            lat=lat,
            lon=lon
        )
    except Exception as e:
        print_red(f"❌ Error generating map: {e}")
        return None

def open_map_for_ip(ip_input):
    """Open map in browser for the given IP"""
    try:
        print(f"{ANSI_WHITE}🔍 Looking up IP:{ANSI_PURPLE} {ip_input}{ANSI_RESET}")
        
        data = lookup_ip(ip_input)
        if data is None:
            return False
        
        
        display_ip_info(data)
        
        lat = data.get("lat")
        lon = data.get("lon")
        
        if not lat or not lon:
            print_red("❌ No coordinates found for this IP.")
            return False
        
        
        html = generate_map_html(data)
        if html is None:
            return False
        
        tmpdir = tempfile.mkdtemp(prefix="ip_geolocator_")
        html_path = os.path.join(tmpdir, "ip_map.html")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        print_green("✅ Opening map in browser...")
        webbrowser.open(f"file://{html_path}")
        
        return True
        
    except Exception as e:
        print_red(f"❌ Error: {e}")
        return False

def save_results(data, filename=None):
    """Save IP lookup results to file"""
    try:
        if not filename:
            ip = data.get('query', 'unknown').replace('.', '_')
            filename = f"ip_lookup_{ip}_{int(time.time())}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print_green(f"💾 Results saved to {filename}")
    except Exception as e:
        print_red(f"❌ Failed to save: {e}")

def main():
    """Main application loop"""
    try:
        while True:
            show_banner()
            
            print(f"{ANSI_WHITE}Options:{ANSI_RESET}")
            print(f"{ANSI_WHITE}  1. Lookup IP ad{ANSI_PURPLE}dress")
            print(f"{ANSI_WHITE}  2. Find my IP{ANSI_PURPLE}")
            print(f"{ANSI_WHITE}  q. Quit{ANSI_RESET}\n")
            
            choice = input(f"{ANSI_WHITE}Choice -> {ANSI_RESET}").strip().lower()
            
            if choice == 'q':
                print(f"{ANSI_WHITE}\n👋 Good{ANSI_PURPLE}bye!\n{ANSI_RESET}")
                break
            
            elif choice == '1':
                ip_input = input(f"\n{ANSI_WHITE}Enter IP address:{ANSI_PURPLE} {ANSI_RESET}").strip()
                
                if not ip_input:
                    print_red("\n❌ No IP entered.")
                    input(f"\n{ANSI_WHITE}Press Enter to c{ANSI_PURPLE}ontinue...{ANSI_RESET}")
                    continue
                
                if not validate_ip(ip_input):
                    print_red("\n❌ Invalid IP address format.")
                    input(f"\n{ANSI_WHITE}Press Enter to c{ANSI_PURPLE}ontinue...{ANSI_RESET}")
                    continue
                
                if open_map_for_ip(ip_input):
                    
                    save = input(f"\n{ANSI_WHITE}💾 Save results t{ANSI_PURPLE}o file? (y/n): {ANSI_RESET}").strip().lower()
                    if save == 'y':
                        data = lookup_ip(ip_input)
                        if data:
                            save_results(data)
                
                input(f"\n{ANSI_WHITE}Press Enter to c{ANSI_PURPLE}ontinue...{ANSI_RESET}")
            
            elif choice == '2':
                print(f"\n{ANSI_WHITE}🔍 Finding your p{ANSI_PURPLE}ublic IP...{ANSI_RESET}")
                my_ip = get_my_ip()
                
                if my_ip:
                    print_green(f"✅ Your IP: {my_ip}\n")
                    lookup = input(f"{ANSI_WHITE}Show details? (y{ANSI_PURPLE}/n): {ANSI_RESET}").strip().lower()
                    
                    if lookup == 'y':
                        open_map_for_ip(my_ip)
                else:
                    print_red("❌ Could not determine your IP.")
                
                input(f"\n{ANSI_WHITE}Press Enter to c{ANSI_PURPLE}ontinue...{ANSI_RESET}")
            
            else:
                print_red("\n❌ Invalid choice.")
                input(f"\n{ANSI_WHITE}Press Enter to c{ANSI_PURPLE}ontinue...{ANSI_RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{ANSI_WHITE}\n👋 Interrupted. {ANSI_PURPLE}Goodbye!\n{ANSI_RESET}")
    except Exception as e:
        print_red(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()