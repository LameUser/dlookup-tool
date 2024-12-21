import os
import concurrent.futures
import openpyxl
from tldextract import extract
import requests
from subprocess import run, CalledProcessError, PIPE
import threading
import pyfiglet
from termcolor import colored

completed_tasks = 0  # Counter to track completed tasks
total_tasks = 0  # Total number of domains to process


def display_banner():
    """
    Display the banner for the tool with the tool name and credits.
    """
    banner = pyfiglet.figlet_format("dlookup", font="slant")  # Use slant font for readability
    banner = colored(banner, "cyan")
    credits = colored("https://github.com/LameUser", "yellow")
    print(banner)
    print(credits)


def clean_domain(domain):
    extracted = extract(domain)
    return f"{extracted.domain}.{extracted.suffix}" if extracted.domain and extracted.suffix else None


def run_command(command):
    try:
        result = run(command, shell=True, text=True, stdout=PIPE, stderr=PIPE, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"


def is_domain_active(domain):
    session = requests.Session()
    for scheme in ["http", "https"]:
        try:
            response = session.get(f"{scheme}://{domain}", timeout=5)
            if response.status_code == 200:
                return scheme
        except requests.exceptions.RequestException:
            continue
    return None


def extract_server_ip(nslookup_result):
    lines = nslookup_result.splitlines()
    ip_addresses = [line.split(":")[-1].strip() for line in lines if "Address:" in line and not line.startswith("Server:")]
    return ip_addresses[-1] if ip_addresses else "N/A"


def get_geolocation(ip):
    """
    Retrieves geolocation data for a given IP address using ip-api.com.
    """
    url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data['status'] == 'success':
            as_data = data.get('as', 'N/A')
            return {
                'Country': data.get('country', 'N/A'),
                'City': data.get('city', 'N/A'),
                'ISP': data.get('isp', 'N/A'),
                'ASN': as_data.split()[0] if as_data != 'N/A' else 'N/A',  # Extract ASN from AS field
            }
    except Exception as e:
        pass
    return {'Country': 'N/A', 'City': 'N/A', 'ISP': 'N/A', 'ASN': 'N/A'}


def process_domain(domain):
    global completed_tasks
    main_domain = clean_domain(domain)
    if not main_domain:
        completed_tasks += 1
        return domain, None, "Invalid Domain", "N/A", "N/A", "No", None, None, None, None, None

    whois_result = run_command(f"whois {main_domain}")
    nslookup_result = run_command(f"nslookup {main_domain}")
    server_ip = extract_server_ip(nslookup_result)
    active_scheme = is_domain_active(main_domain)
    domain_active = "Yes" if active_scheme else "No"

    # Get geolocation data for the server IP
    geo_data = get_geolocation(server_ip) if server_ip != "N/A" else {
        'Country': 'N/A',
        'City': 'N/A',
        'ISP': 'N/A',
        'ASN': 'N/A'
    }

    completed_tasks += 1
    return (
        domain,
        main_domain,
        whois_result,
        nslookup_result,
        server_ip,
        domain_active,
        active_scheme,
        geo_data['Country'],
        geo_data['City'],
        geo_data['ISP'],
        geo_data['ASN'],
    )


def print_progress():
    """
    Continuously print progress when the user presses Enter.
    """
    global completed_tasks, total_tasks
    while completed_tasks < total_tasks:
        input("\nPress Enter to see progress... ")
        print(f"Progress: {completed_tasks}/{total_tasks} tasks completed ({(completed_tasks / total_tasks) * 100:.2f}%).")


def capture_screenshots(active_domains, screenshot_dir):
    """
    Run the EyeWitness tool to capture screenshots of active domains.
    """
    print("\nStarting screenshot capture...")
    total_urls = len(active_domains)
    for idx, domain in enumerate(active_domains, start=1):
        print(f"Capturing screenshot {idx}/{total_urls} for: {domain}")
        command = f"eyewitness --single {domain} --web --output {screenshot_dir}"
        try:
            run(command, shell=True, check=True)
        except CalledProcessError as e:
            print(f"Error capturing screenshot for {domain}: {e}")


def process_domains(input_file, txt_output, result_output, screenshot_dir):
    global total_tasks
    wb = openpyxl.load_workbook(input_file)
    sheet = wb.active
    result_wb = openpyxl.Workbook()
    result_sheet = result_wb.active
    result_sheet.append([
        "URLS", "Domain", "WHOIS Result", "NSLOOKUP Result", "Server IP",
        "Domain Active", "Successful Scheme", "Country", "City", "ISP", "ASN"
    ])

    domains = [row[0].value for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=1) if row[0].value]
    total_tasks = len(domains)
    active_domains = []

    progress_thread = threading.Thread(target=print_progress, daemon=True)
    progress_thread.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_domain, domain): domain for domain in domains}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            result_sheet.append(result[:11])
            if result[5] == "Yes":
                active_domains.append(f"{result[6]}://{result[1]}")

    result_wb.save(result_output)
    with open(txt_output, 'w') as txt_file:
        txt_file.write("\n".join(active_domains))
    print(f"Active domains saved to {txt_output}")

    # Capture screenshots
    if active_domains:
        capture_screenshots(active_domains, screenshot_dir)


if __name__ == "__main__":
    display_banner()

    base_path = r"/media/sf_Kalisharing/"
    input_path = os.path.join(base_path, "cryptodomain.xlsx")
    txt_output_path = os.path.join(base_path, "urls.txt")
    result_output_path = os.path.join(base_path, "domain_results.xlsx")
    screenshot_dir = os.path.join(base_path, "screens/")

    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    if os.path.exists(input_path):
        process_domains(input_path, txt_output_path, result_output_path, screenshot_dir)
    else:
        print(f"Input file not found: {input_path}")
