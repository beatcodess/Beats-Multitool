#!/usr/bin/env python3
import os
import socket
import concurrent.futures
import time
import sys
from typing import List, Dict, Optional, Tuple


RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
WHITE = "\033[97m"
PURPLE = "\033[95m"
CYAN = "\033[36m"
RESET = "\033[0m"


ASCII_ART = f"""{WHITE}                                {PURPLE}           
{WHITE}  ___  ___ __ _ _ __  _ __   ___ {PURPLE}_ __ 
{WHITE} / __|/ __/ _` | '_ \\| '_ \\ / _ \\{PURPLE}| '__|
{WHITE} \\__ \\ (_| (_| | | | | | | |  __/{PURPLE}| |   
{WHITE} |___/\\___\\__,_|_| |_|_| |_|\\___| _|   
{WHITE}                                {PURPLE}       {RESET}
"""



SERVICE_MAP: Dict[int, str] = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB",
    1433: "MSSQL", 1521: "Oracle", 2049: "NFS", 5000: "UPnP",
    8000: "HTTP-Alt", 9000: "HTTP-Alt", 9090: "HTTP-Alt"
}


PRIORITY_PORTS: List[int] = [
    21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 
    5432, 5900, 6379, 8080, 8443, 27017, 1433, 1521, 2049, 
    5000, 8000, 9000, 9090
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Display banner with tool description"""
    clear()
    print(ASCII_ART)
    print(f"{CYAN}🔍 Discover open ports and running services on any target{RESET}")
    print(f"{WHITE}   Fast multi-threaded scanning with banner grabbing\n{RESET}")
    print(f"{WHITE}╔═══════════════════{PURPLE}═══════════════════╗")
    print(f"{WHITE}║   Advanced Port S{PURPLE}canner             ║")
    print(f"{WHITE}╚═══════════════════{PURPLE}═══════════════════╝\n{RESET}")

def resolve_host(hostname: str) -> str:
    """Resolve hostname to IP address"""
    try:
        for fam, _, _, _, sockaddr in socket.getaddrinfo(hostname, None):
            if fam == socket.AF_INET:
                return sockaddr[0]
        return socket.gethostbyname(hostname)
    except Exception as e:
        raise RuntimeError(f"DNS resolution failed: {e}")

def grab_banner(addr: str, port: int, timeout: float = 2.0) -> Optional[str]:
    """Attempt to grab service banner from port"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((addr, port))
        
        
        try:
            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        except Exception:
            pass
        
        try:
            banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
            s.close()
            return banner[:200] if banner else None  # Limit banner length
        except Exception:
            s.close()
            return None
    except Exception:
        return None

def get_service_name(port: int, banner: Optional[str] = None) -> str:
    """Get service name from port number or banner"""
    
    if banner:
        banner_lower = banner.lower()
        if 'http' in banner_lower or 'html' in banner_lower:
            return "HTTP"
        elif 'ssh' in banner_lower:
            return "SSH"
        elif 'ftp' in banner_lower:
            return "FTP"
        elif 'smtp' in banner_lower:
            return "SMTP"
        elif 'mysql' in banner_lower:
            return "MySQL"
    
    
    return SERVICE_MAP.get(port, "Unknown")

def scan_port(addr: str, port: int, timeout: float, grab_banners: bool = False) -> Tuple[int, bool, Optional[str], Optional[str]]:
    """Scan a single port and optionally grab banner"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    
    try:
        res = s.connect_ex((addr, port))
        is_open = (res == 0)
        
        banner = None
        service = None
        
        if is_open and grab_banners:
            s.close()
            banner = grab_banner(addr, port, timeout)
            service = get_service_name(port, banner)
        else:
            service = get_service_name(port)
        
        try:
            s.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        
        return port, is_open, service, banner
        
    except Exception:
        return port, False, None, None
    finally:
        try:
            s.close()
        except Exception:
            pass

def print_port_status(port: int, is_open: bool, service: Optional[str] = None, banner: Optional[str] = None, verbose: bool = False):
    """Print port scan status with optional banner info"""
    if is_open:
        service_str = f" ({service})" if service else ""
        print(f"{GREEN}[+] {port}{service_str}{RESET}")
        
        if verbose and banner:
            
            first_line = banner.split('\n')[0][:100]
            print(f"{YELLOW}    └─ Banner: {first_line}{RESET}")
    elif verbose:
        print(f"{RED}[-] {port}{RESET}")
    
    sys.stdout.flush()

def choose_mode() -> str:
    """Let user choose scan mode"""
    while True:
        print(f"\n{WHITE}Choose scan mode:{RESET}")
        print(f"{WHITE}  1. Quick scan ({PURPLE}priority ports)")
        print(f"{WHITE}  2. Full scan (al{PURPLE}l ports 1-65535){RESET}")
        choice = input(f"{WHITE}Choice -> {RESET}").strip()
        if choice in ("1", "2"):
            return choice
        print(f"{RED}Invalid choice. Enter 1 or 2.{RESET}")

def priority_scan(addr: str, threads: int, timeout: float, grab_banners: bool, verbose: bool) -> List[Dict]:
    """Scan priority ports"""
    print(f"\n{WHITE}🔍 Scanning {len(PRIORITY_PORTS)} priority port{PURPLE}s...{RESET}\n")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(scan_port, addr, p, timeout, grab_banners): p for p in PRIORITY_PORTS}
        
        for fut in concurrent.futures.as_completed(futures):
            port, is_open, service, banner = fut.result()
            print_port_status(port, is_open, service, banner, verbose)
            
            if is_open:
                results.append({
                    'port': port,
                    'service': service,
                    'banner': banner
                })
    
    return sorted(results, key=lambda x: x['port'])

def full_scan(addr: str, threads: int, timeout: float, grab_banners: bool, verbose: bool, exclude: set) -> List[Dict]:
    """Scan all ports excluding already scanned ones"""
    print(f"\n{WHITE}🔍 Scanning remaining port{PURPLE}s...{RESET}\n")
    
    CHUNK = 4096
    results = []
    all_ports = [p for p in range(1, 65536) if p not in exclude]
    
    for i in range(0, len(all_ports), CHUNK):
        chunk = all_ports[i:i+CHUNK]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
            futures = {ex.submit(scan_port, addr, p, timeout, grab_banners): p for p in chunk}
            
            for fut in concurrent.futures.as_completed(futures):
                port, is_open, service, banner = fut.result()
                if verbose or is_open:
                    print_port_status(port, is_open, service, banner, verbose)
                
                if is_open:
                    results.append({
                        'port': port,
                        'service': service,
                        'banner': banner
                    })
        
        
        progress = min(100, int(((i + CHUNK) / len(all_ports)) * 100))
        sys.stdout.write(f"\r{YELLOW}Progress: {progress}%{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
    
    print()  
    return sorted(results, key=lambda x: x['port'])

def export_results(target: str, results: List[Dict]):
    """Export scan results to file"""
    filename = f"scan_{target.replace('.', '_')}_{int(time.time())}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Port Scan Results for {target}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Scan Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Open Ports: {len(results)}\n\n")
            
            for r in results:
                f.write(f"Port {r['port']}: {r['service']}\n")
                if r['banner']:
                    f.write(f"  Banner: {r['banner'][:100]}\n")
                f.write("\n")
        
        print(f"{GREEN}✅ Results saved to {filename}{RESET}")
    except Exception as e:
        print(f"{RED}❌ Failed to save results: {e}{RESET}")

def single_scan_flow():
    """Main scan flow"""
    print_header()
    
    
    target = input(f"{WHITE}Target IP/hostname{PURPLE} (default: 127.0.0.1): {RESET}").strip() or "127.0.0.1"
    
    try:
        addr = resolve_host(target)
        print(f"{GREEN}✅ Resolved {target} → {addr}{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        return
    
    
    threads_input = input(f"{WHITE}Threads [default{PURPLE}: 200]: {RESET}").strip()
    try:
        threads = int(threads_input) if threads_input else 200
        threads = max(1, min(threads, 800))  
    except Exception:
        threads = 200
    
    
    timeout_input = input(f"{WHITE}Timeout seconds [{PURPLE}default: 0.5]: {RESET}").strip()
    try:
        timeout = float(timeout_input) if timeout_input else 0.5
    except Exception:
        timeout = 0.5
    
    
    banner_input = input(f"{WHITE}Enable banner gra{PURPLE}bbing? (y/n) [default: y]: {RESET}").strip().lower()
    grab_banners = banner_input != 'n'
    
    
    verbose_input = input(f"{WHITE}Show closed ports?{PURPLE} (y/n) [default: n]: {RESET}").strip().lower()
    verbose = verbose_input == 'y'
    
    
    mode = choose_mode()
    
    
    start = time.time()
    results = []
    
    if mode == "1":
        results = priority_scan(addr, threads, timeout, grab_banners, verbose)
    else:
        
        priority_results = priority_scan(addr, threads, timeout, grab_banners, verbose)
        results.extend(priority_results)
        
        
        exclude = set(PRIORITY_PORTS)
        full_results = full_scan(addr, threads, timeout, grab_banners, verbose, exclude)
        results.extend(full_results)
        results = sorted(results, key=lambda x: x['port'])
    
    elapsed = time.time() - start
    
    
    print(f"\n{WHITE}{'=' * 25}{PURPLE}{'=' * 25}{RESET}")
    print(f"\n{WHITE}📊 Scan Summary:{RESET}")
    print(f"   • Target: {target} ({addr})")
    print(f"   • Duration: {elapsed:.1f}s")
    print(f"   • Open Ports: {len(results)}")
    
    if results:
        print(f"\n{GREEN}✅ Open Ports:{RESET}")
        for r in results:
            service_str = f" - {r['service']}" if r['service'] else ""
            print(f"{GREEN}   [{r['port']}]{service_str}{RESET}")
            if r['banner'] and grab_banners:
                banner_preview = r['banner'].split('\n')[0][:80]
                print(f"{YELLOW}      └─ {banner_preview}{RESET}")
    else:
        print(f"\n{RED}❌ No open ports found{RESET}")
    
    
    if results:
        export = input(f"\n{WHITE}💾 Export results {PURPLE}to file? (y/n): {RESET}").strip().lower()
        if export == 'y':
            export_results(target, results)

def main():
    """Main loop"""
    while True:
        single_scan_flow()
        
        print(f"\n{WHITE}1. Scan again{RESET}")
        print(f"{WHITE}q. Quit{RESET}")
        
        choice = input(f"\n{WHITE}Choice -> {RESET}").strip().lower()
        
        if choice == 'q':
            print(f"{WHITE}\n👋 Good{PURPLE}bye!\n{RESET}")
            break
        elif choice != '1':
            print(f"{RED}Invalid choice.{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{WHITE}\n👋 Interrupted. {PURPLE}Goodbye!\n{RESET}")
        sys.exit(0)