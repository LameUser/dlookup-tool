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

def display_banner():
    """Display the tool banner with the name and GitHub link."""
    banner = pyfiglet.figlet_format("dlookup", font="slant")  # Create banner text
    print(colored(banner, "cyan"))  # Print banner in cyan
    print(colored("https://github.com/LameUser", "yellow"))  # Print GitHub link in yellow

def clean_domain(url):
    """Clean the domain by removing subdomains, prefixes, and trailing dots."""
    url = url.strip('.').lower()
    domain_parts = url.split('.')
    if len(domain_parts) > 2:
        domain = '.'.join(domain_parts[-2:])
    else:
        domain = '.'.join(domain_parts)
    return domain

async def get_ip_info(ip, session):
    """Get detailed IP information including proxy status."""
    url = f"http://ip-api.com/json/{ip}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "proxy": data.get("proxy", False),
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "asn": data.get("as", "Unknown")
                }
            return {"proxy": False, "country": "Unknown", "city": "Unknown", "isp": "Unknown", "asn": "Unknown"}
    except Exception:
        return {"proxy": False, "country": "Unknown", "city": "Unknown", "isp": "Unknown", "asn": "Unknown"}

def run_command_with_retries(command, retries=2):
    """Run a shell command with retries if it fails."""
    for attempt in range(retries + 1):
        try:
            result = subprocess.getoutput(command)
            if result:
                return result
        except Exception:
            if attempt >= retries:
                return "Command failed"

def validate_result(result, command_type):
    """Check for common errors in WHOIS and NSLOOKUP results."""
    if "Temporary failure in name resolution" in result or "host unreachable" in result or "timed out" in result or "no servers could be reached" in result:
        return f"{command_type} Error: {result.splitlines()[0]}"
    return result

def process_domain_sync(url):
    try:
        domain = clean_domain(url)
        # Use WHOIS command with maximum detail
        whois_result = run_command_with_retries(f"whois -I {domain}")
        whois_result = validate_result(whois_result, "WHOIS")

        # NSLOOKUP command
        nslookup_result = run_command_with_retries(f"nslookup {domain}")
        nslookup_result = validate_result(nslookup_result, "NSLOOKUP")

        server_ip = None
        for line in nslookup_result.splitlines():
            if "Address:" in line:
                server_ip = line.split("Address:")[-1].strip()

        return {
            "URLS": url,
            "Domain": domain,
            "WHOIS Result": whois_result,
            "NSLOOKUP Result": nslookup_result,
            "Server IP": server_ip if server_ip else "No IP Found",
        }
    except Exception:
        return None

async def process_domains_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        results = []
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=30) as executor:
            for url in urls:
                tasks.append(loop.run_in_executor(executor, process_domain_sync, url))

            for sync_result in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Domain Processing", unit="url"):
                try:
                    result = await sync_result
                    if result:
                        ip_info = {"proxy": False, "country": "Unknown", "city": "Unknown", "isp": "Unknown", "asn": "Unknown"}
                        if result["Server IP"] and result["Server IP"] != "No IP Found":
                            ip_info = await get_ip_info(result["Server IP"], session)

                        result["PROXY"] = ip_info["proxy"]
                        result["country"] = ip_info["country"]
                        result["city"] = ip_info["city"]
                        result["isp"] = ip_info["isp"]
                        result["asn"] = ip_info["asn"]
                        results.append(result)
                except Exception:
                    continue

        return results

async def main():
    display_banner()

    # Ask user for the folder containing the input Excel file
    folder_path = input("\nEnter the full path of the folder where the domains.xlsx file is located: ").strip()
    input_file = os.path.join(folder_path, "domains.xlsx")
    output_excel = os.path.join(folder_path, "output.xlsx")
    output_text = os.path.join(folder_path, "urls.txt")

    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    df = pd.read_excel(input_file)
    urls = df['URLS'].dropna().tolist()

    results = await process_domains_async(urls)

    structured_results = []
    for result in results:
        structured_results.append({
            "URLS": result["URLS"],
            "Domain": result["Domain"],
            "WHOIS Result": result["WHOIS Result"],
            "NSLOOKUP Result": result["NSLOOKUP Result"],
            "Server IP": result["Server IP"],
            "Domain Active": "Yes" if result["Server IP"] != "No IP Found" and "200" in result["WHOIS Result"] else "No",
            "Successful Scheme": "http" if "http" in result["URLS"] else "https",
            "country": result["country"],
            "city": result["city"],
            "isp": result["isp"],
            "asn": result["asn"],
            "PROXY": "True" if result["PROXY"] else "False"
        })

    results_df = pd.DataFrame(structured_results)
    results_df.to_excel(output_excel, index=False)

    with open(output_text, "w") as f:
        for result in structured_results:
            f.write(f"{result['Domain']}\n")

    print(f"Results saved to '{output_excel}' and '{output_text}'.")

    # Wait for 3 seconds before running gowitness
    await asyncio.sleep(3)

    # Run gowitness to take screenshots
    gowitness_command = f"gowitness scan file -f {output_text}"
    try:
        subprocess.run(gowitness_command, shell=True, check=True)
        print("Screenshots captured successfully using gowitness.")
    except subprocess.CalledProcessError as e:
        print(f"Error running gowitness: {e}")

if __name__ == "__main__":
    asyncio.run(main())
