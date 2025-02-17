# dlookup Tool

![dlookup Banner](loadup.png)

**dlookup-tool** is a powerful domain and IP lookup tool designed to gather comprehensive information about domains and IP addresses. It performs WHOIS lookups, resolves domain IPs using `ping`, and fetches IP details (Organization, Country, City) from `ipinfo.io`. The tool is built with Python and leverages asynchronous programming for efficient processing.

## Features

- **Domain and IP Validation**: Automatically detects whether the input is a domain or an IP address.
- **WHOIS Lookup**: Retrieves detailed WHOIS information for domains, including registrar, creation date, and expiry date.
- **IP Resolution**: Uses `ping` to resolve the IP address of a domain.
- **IP Information**: Fetches IP details (Organization, Country, City) from `ipinfo.io`.
- **Excel Report**: Generates a detailed Excel report with all collected data.
- **Screenshot Capture**: Optionally captures screenshots of domains using `eyewitness`.
- **Asynchronous Processing**: Handles multiple domains/IPs concurrently for faster results.

## Installation

### Prerequisites
- Python 3.7 or higher
- `pip` for installing dependencies
- `eyewitness` (optional, for screenshot functionality)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/LameUser/dlookup-tool.git
   cd dlookup-tool
   ```
   
2. Install the required Python packages:
  ```bash
   pip install -r requirements.txt
  ```

3. Ensure ping and whois are installed on your system. On most Linux distributions, these are pre-installed. If not, install them using:
   ```bash
   sudo apt-get install iputils-ping whois
   ```
   
4. (Optional) Install `eyewitness` for screenshot functionality:
   ```bash
    git clone https://github.com/FortyNorthSecurity/EyeWitness.git
    cd EyeWitness/Python/setup
    sudo ./setup.sh
   ```

## Usage

1. Prepare an Excel file named `domains.xlsx` with a column named `URLS`. This column should contain the domains or IPs you want to analyze. Example:

   | URLS               |
   |--------------------|
   | example.com        |
   | 192.168.1.1       |
   | https://google.com |

2. Place the `domains.xlsx` file in the same directory as the script.

3. Run the script:
   ```bash
   python dlookup.py
   ```
   
4. When prompted, enter the path to the directory containing `domains.xlsx`. For example:
  ```bash
  Enter working directory path: /home/user/dlookup-tool/
  ```

5. The tool will process the domains/IPs and generate an Excel report (`domain_report.xlsx`) in the same directory.

6. Optionally, capture screenshots of the domains by entering `y` when prompted.

## Output

The tool generates two output files:
1. **`domain_report.xlsx`**: Contains detailed information about each domain/IP, including:
   - URL
   - Domain
   - Registrar
   - Creation Date
   - Expiry Date
   - Server IP
   - Organization
   - Country
   - City
   - Active Status

2. **`screenshot_urls.txt`**: Contains a list of URLs for which screenshots were captured (if enabled).

---

## Example Output

### Excel Report (`domain_report.xlsx`)

| URL               | Domain       | Registrar     | Creation Date | Expiry Date | Server IP     | Organization       | Country | City          | Active |
|-------------------|--------------|---------------|---------------|-------------|---------------|--------------------|---------|---------------|--------|
| example.com       | example.com  | GoDaddy       | 2020-01-01    | 2025-01-01  | 93.184.216.34 | AS15169 Google LLC | US      | Mountain View | Yes    |
| 192.168.1.1      | 192.168.1.1  | Not Found     | Not Found     | Not Found   | 192.168.1.1   | Unknown            | Unknown | Unknown       | Yes    |

---

## Screenshot Capture

If you choose to capture screenshots, the tool will use `eyewitness` to take screenshots of the domains. The screenshots will be saved in a folder named `screenshots` within the working directory.

---

## Dependencies

- Python Libraries:
  - `pandas`
  - `aiohttp`
  - `tqdm`
  - `pyfiglet`
  - `termcolor`

- System Tools:
  - `ping`
  - `whois`
  - `eyewitness` (optional)

---

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

---

## Author

- **LameUser**
- GitHub: [https://github.com/LameUser](https://github.com/LameUser)

---

## Acknowledgments

- Thanks to `ipinfo.io` for providing IP information.
- Thanks to the developers of `eyewitness` for the screenshot functionality.
## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
