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

- Clone the repository:
```bash
git clone https://github.com/your-username/dlookup-tool.git
cd dlookup-tool
```

- Run the script:
    - The script will prompt you to enter the folder path where the input Excel file (`cryptodomain.xlsx`) is located.
    - All output files (results and screenshots) will be saved in the same folder.
  Command: - 
```bash
python3 dlookup.py
```

-Input file:
  - Ensure the inpute file `cyptodomain.xlsx` is present in the folder you specify.


## Output

- Excel File: The tool generates an Excel file (`domain_results.xlsx) with detailed informations:
    - URL, Domain, WHOIS Result, NSLOOKUP Result, Server IP, Domain Active, Successful Scheme, Country, City, ISP, ASN.
- Screenshots: Captured screenshots of active domains are saved in the `screens/` directory.

## Configuration

- Input File Path: The script dynamically asks for the folder where the input file (`cryptodomain.xlsx`) is located.

- Output File Path: The script automatically saves:
    - Results (`domain_results.xlsx` and `urls.txt`) in the same folder as the input file.
    - Screenshots in a `screens/` directory with the same folder.

## Example workflow:

- Promt:
    -
   ```bash
      Enter the full path of the folder where the domain Excel sheet is located: /home/user/domains
   ```

- Output:
  - Results will be saved in `/home/user/domains`:
      - `domain_results.xlsx`
      - `urls.txt`
      - `screens/` (directory containing screenshots of active domains) 
