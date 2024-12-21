# dlookup Tool

`dlookup` is a Python-based tool designed to analyze domains and IPs, providing WHOIS, NSLOOKUP, geolocation data, and domain activity status. It also captures screenshots of active domains using EyeWitness.

## Features
- Extracts WHOIS and NSLOOKUP data for domains.
- Checks if a domain is active and determines the scheme (HTTP/HTTPS).
- Retrieves geolocation details such as Country, City, ISP, and ASN using `ip-api.com`.
- Captures screenshots of active domains.
- Outputs results in a comprehensive Excel file.

## Installation

### Dependencies
Ensure you have the following installed:
- Python 3.6 or higher
- Required Python libraries:
  - `openpyxl`
  - `tldextract`
  - `requests`
  - `pyfiglet`
  - `termcolor`

To install the dependencies, run:
```bash
pip install openpyxl tldextract requests pyfiglet termcolor
```
Installation of pyfiglet sometimes shows error in that case you may try 
```bash
import pyfiglet
```

### EyeWitness
Install EyeWitness for screenshot capture:
```bash
sudo apt install eyewitness
```

## Usage

Clone the repository:
```bash
git clone https://github.com/your-username/dlookup-tool.git
cd dlookup-tool
```

Place your input Excel file (e.g., `cryptodomain.xlsx`) in the `dlookup-tool` directory. Modify the script paths if your input/output locations differ.

Run the script:
```bash
python3 dlookup.py
```

