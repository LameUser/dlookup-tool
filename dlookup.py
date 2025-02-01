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

def display_banner():
    """Display the tool banner with styling."""
    banner = pyfiglet.figlet_format("dlookup", font="slant")
    print(colored(banner, "cyan"))
    print(colored("https://github.com/LameUser", "yellow"))

def clean_domain(url):
    """Enhanced domain cleaning with URL validation."""
    try:
        # Remove protocol and path
        url = url.split('//')[-1].split('/')[0].lower().strip()
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
    except:
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

async def process_domain(url, counter, sem):
    """Domain processing with enhanced error handling."""
    async with sem:
        if counter % 250 == 0 and counter != 0:
            await asyncio.sleep(5)  # Rate limiting
            
        try:
            domain = clean_domain(url)
            whois_result = await get_whois_info(domain)
            registrar_details = extract_registrar_details(whois_result)
            
            # Get DNS information
            nslookup = await run_async_command(f"nslookup {domain}")
            server_ip = next((line.split("Address:")[-1].strip() 
                            for line in nslookup.splitlines() 
                            if "Address:" in line), "No IP Found")

            return {
                "URLS": url,
                "Domain": domain,
                "WHOIS Result": whois_result,
                **registrar_details,
                "NSLOOKUP Result": nslookup,
                "Server IP": server_ip
            }
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return None

async def get_ip_info(ip, session):
    """IP information with retries."""
    url = f"http://ip-api.com/json/{ip}"
    for attempt in range(3):
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "country": data.get("country", "Unknown"),
                        "city": data.get("city", "Unknown"),
                        "isp": data.get("isp", "Unknown"),
                        "asn": data.get("as", "Unknown"),
                        "proxy": data.get("proxy", False)
                    }
                await asyncio.sleep(2 ** attempt)
        except:
            await asyncio.sleep(1)
    return {"country": "Unknown", "city": "Unknown", "isp": "Unknown", "asn": "Unknown", "proxy": False}

async def process_domains(urls):
    """Main processing pipeline."""
    sem = asyncio.Semaphore(15)  # Control concurrency
    async with aiohttp.ClientSession() as session:
        tasks = [process_domain(url, i, sem) for i, url in enumerate(urls)]
        results = []
        
        for future in tqdm(asyncio.as_completed(tasks), total=len(urls), desc="Processing Domains"):
            result = await future
            if result:
                if result["Server IP"] != "No IP Found":
                    ip_info = await get_ip_info(result["Server IP"], session)
                    result.update(ip_info)
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
        "Country": r.get("country", "Unknown"),
        "ISP": r.get("isp", "Unknown"),
        "ASN": r.get("asn", "Unknown"),
        "Proxy": r.get("proxy", False),
        "Active": "Yes" if r["Server IP"] != "No IP Found" else "No"
    } for r in results])
    
    excel_path = os.path.join(folder, "domain_report.xlsx")
    df.to_excel(excel_path, index=False)
    
    # URLs for screenshots
    txt_path = os.path.join(folder, "screenshot_urls.txt")
    with open(txt_path, "w") as f:
        f.write("\n".join([r["URLS"] for r in results]))
    
    return excel_path, txt_path

async def capture_screenshots(urls_file, folder):
    """Run eyewitness with proper configuration."""
    screenshots_dir = os.path.join(folder, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    cmd = f"eyewitness --web -f {urls_file} --threads 8 -d {screenshots_dir} --no-prompt"
    try:
        proc = await asyncio.create_subprocess_shell(cmd)
        await proc.communicate()
        return True
    except Exception as e:
        print(f"Screenshot error: {str(e)}")
        return False

async def main():
    display_banner()
    
    folder = input("\nEnter working directory path: ").strip()
    if not os.path.isdir(folder):
        print("Invalid directory!")
        return
    
    try:
        df = pd.read_excel(os.path.join(folder, "domains.xlsx"))
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
