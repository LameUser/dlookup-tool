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

1. Clone the repository:
```bash
git clone https://github.com/your-username/dlookup-tool.git
cd dlookup-tool
```

2. Place your input Excel file (e.g., `cryptodomain.xlsx`) in the `dlookup-tool` directory. Modify the script paths if your input/output locations differ.

3. Run the script:
```bash
python3 dlookup.py
```

### Output

- Excel File: The tool generates an Excel file (`domain_results.xlsx) with detailed informations:
    - URL, Domain, WHOIS Result, NSLOOKUP Result, Server IP, Domain Active, Successful Scheme, Country, City, ISP, ASN.
- Screenshots: Captured screenshots of active domains are saved in the `screens/` directory.

### Configuration

1. Input File Path: Update the `input_path` variable in `dlookup.py` to match the location of your input file.
   Example:
   ```bash
   input_path = "/path/to/your/cryptodomain.xlsx"
   ```
2. Output File Path: Update the `result_output_path` and `txt_output_path` variables to set the location for the output files.
   Example:
   ```bash
   result_output_path = "/path/to/save/domain_results.xlsx"
    txt_output_path = "/path/to/save/urls.txt"
   ```
3. Screenshot Directory: Update the `screenshot_dir` variable to set the directory for screenshots.
   Example:
   ```bash
   screenshot_dir = "/path/to/save/screens/"
   ```





