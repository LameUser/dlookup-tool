import os
import pandas as pd
import subprocess
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import pyfiglet
from termcolor import colored
import re
import time
import json

def display_banner():
    """Display the tool banner with styling."""
    banner = pyfiglet.figlet_format("dlookup", font="slant")
    print(colored(banner, "cyan"))
    print(colored("https://github.com/LameUser", "yellow"))

def clean_domain(url):
    """
    Enhanced domain cleaning with URL validation.
    Identifies if the input is an IP address (IPv4 or IPv6) or a URL.
    If it's a URL, it cleans it; if it's an IP address, it returns it as-is.
    """
    try:
        # Remove protocol and path
        url = url.split('//')[-1].split('/')[0].lower().strip()
        
        # Check if the input is an IPv4 address
        ipv4_pattern = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if ipv4_pattern.match(url):
            return url  # Return the IPv4 address as-is
        
        # Check if the input is an IPv6 address
        ipv6_pattern = re.compile(r"^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$", re.IGNORECASE)
        if ipv6_pattern.match(url):
            return url  # Return the IPv6 address as-is
        
        # If it's not an IP address, assume it's a URL and clean it
        # Remove port if present
        domain = url.split(':')[0]
        
        # Handle subdomains and TLDs
        parts = domain.split('.')
        if len(parts) > 2:
            # Preserve country-code TLDs (e.g., .co.uk)
            if len(parts[-1]) == 2 and len(parts) > 3:
                return '.'.join(parts[-3:])
            return '.'.join(parts[-2:])
        return domain
    except Exception as e:
        print(f"Error cleaning domain {url}: {str(e)}")
        return url

async def run_async_command(command):
    """Run shell commands asynchronously."""
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode().strip() if stdout else stderr.decode().strip()

async def get_whois_info(domain):
    """Robust WHOIS lookup with multiple retry strategies."""
    commands = [
        f"whois -H {domain}",
        f"whois {domain}",
        f"whois -h whois.iana.org {domain}"
    ]
    
    for cmd in commands:
        for attempt in range(3):
            try:
                result = await run_async_command(cmd)
                if not any(e in result.lower() for e in ['error', 'not found', 'invalid']):
                    return result
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except:
                await asyncio.sleep(1)
    return "WHOIS lookup failed"

def extract_registrar_details(whois_result):
    """Improved registrar details extraction with fallbacks."""
    details = {
        'Registry Domain ID': r"Registry Domain ID:\s*(.+)",
        'Registrar WHOIS Server': r"Registrar WHOIS Server:\s*(.+)",
        'Registrar URL': r"Registrar URL:\s*(.+)",
        'Updated Date': r"Updated Date:\s*(.+)",
        'Creation Date': r"(?:Creation Date|Registered on):\s*(.+)",
        'Registry Expiry Date': r"(?:Registry Expiry Date|Expiry Date):\s*(.+)",
        'Registrar': r"Registrar:\s*(.+)",
        'Registrar IANA ID': r"Registrar IANA ID:\s*(.+)"
    }
    
    return {key: (re.search(pattern, whois_result, re.IGNORECASE).group(1).strip() 
                  if re.search(pattern, whois_result) else "Not Found") 
            for key, pattern in details.items()}

async def get_ip_from_domain(domain):
    """Ping the domain to resolve its IP address."""
    try:
        # Use ping command to resolve the IP address
        ping_result = await run_async_command(f"ping -c 1 {domain}")
        ip_match = re.search(r"PING\s[\w\.-]+\s\(([\d\.]+)\)", ping_result)
        if ip_match:
            return ip_match.group(1)
        return "No IP Found"
    except Exception as e:
        print(f"Error resolving IP for {domain}: {str(e)}")
        return "No IP Found"

async def get_ip_info(ip):
    """Fetch IP information using ipinfo.io."""
    url = f"https://ipinfo.io/{ip}/json"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "Organisation": data.get("org", "Unknown"),
                        "Country": data.get("country", "Unknown"),
                        "City": data.get("city", "Unknown")
                    }
        except Exception as e:
            print(f"Error fetching IP info for {ip}: {str(e)}")
            return {"Organisation": "Unknown", "Country": "Unknown", "City": "Unknown"}

async def process_domain(url, counter, sem):
    """Domain processing with enhanced error handling."""
    async with sem:
        if counter % 250 == 0 and counter != 0:
            await asyncio.sleep(5)  # Rate limiting
            
        try:
            domain = clean_domain(url)
            whois_result = await get_whois_info(domain)
            registrar_details = extract_registrar_details(whois_result)
            
            # Resolve IP address
            if domain != url:  # If it's a domain, resolve IP
                ip = await get_ip_from_domain(domain)
            else:  # If it's already an IP, use it directly
                ip = domain
            
            # Fetch IP info
            ip_info = await get_ip_info(ip)
            
            return {
                "URLS": url,
                "Domain": domain,
                "WHOIS Result": whois_result,
                **registrar_details,
                "Server IP": ip,
                **ip_info
            }
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return None

async def process_domains(urls):
    """Main processing pipeline."""
    sem = asyncio.Semaphore(15)  # Control concurrency
    tasks = [process_domain(url, i, sem) for i, url in enumerate(urls)]
    results = []
    
    for future in tqdm(asyncio.as_completed(tasks), total=len(urls), desc="Processing Domains"):
        result = await future
        if result:
            results.append(result)
    return results

def save_outputs(results, folder):
    """Save all output files with proper formatting."""
    # Excel Report
    df = pd.DataFrame([{
        "URL": r["URLS"],
        "Domain": r["Domain"],
        "Registrar": r["Registrar"],
        "Creation Date": r["Creation Date"],
        "Expiry Date": r["Registry Expiry Date"],
        "Server IP": r["Server IP"],
        "Organisation": r.get("Organisation", "Unknown"),
        "Country": r.get("Country", "Unknown"),
        "City": r.get("City", "Unknown"),
        "Active": "Yes" if r["Server IP"] != "No IP Found" else "No"
    } for r in results])
    
    excel_path = os.path.join(folder, "domain_report.xlsx")
    df.to_excel(excel_path, index=False)
    
    # URLs for screenshots
    txt_path = os.path.join(folder, "screenshot_urls.txt")
    with open(txt_path, "w") as f:
        f.write("\n".join([r["URLS"] for r in results]))
    
    return excel_path, txt_path

async def main():
    display_banner()
    
    folder = input("\nEnter working directory path: ").strip()
    
    # Check if the provided path is a valid directory
    if not os.path.isdir(folder):
        print(f"Invalid directory: {folder}")
        return
    
    # Check if domains.xlsx exists in the directory
    domains_file = os.path.join(folder, "domains.xlsx")
    if not os.path.isfile(domains_file):
        print(f"Error: 'domains.xlsx' not found in {folder}")
        return
    
    try:
        df = pd.read_excel(domains_file)
        urls = df['URLS'].dropna().unique().tolist()
    except Exception as e:
        print(f"Input error: {str(e)}")
        return
    
    results = await process_domains(urls)
    excel_path, txt_path = save_outputs(results, folder)
    
    print(f"\nReport saved to: {excel_path}")
    
    if input("Capture screenshots? (y/n): ").lower() == 'y':
        print("Starting eyewitness...")
        if await capture_screenshots(txt_path, folder):
            print("Screenshots captured successfully!")
        else:
            print("Screenshot capture failed")

if __name__ == "__main__":
    asyncio.run(main())
