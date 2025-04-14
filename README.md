# Network Service Discovery Tool

This is a Python-based network service discovery tool that leverages **masscan** and **httpx** for identifying open ports and HTTP services on given targets.

## Features

- **IP and Domain Handling**: Supports both IP addresses and domain names as input.
- **Masscan Integration**: Quickly scans for open ports on specified targets.
- **httpx Integration**: Gathers HTTP information (status codes, titles, technologies) for discovered services.
- **CDN Detection**: Identifies whether a given IP belongs to a CDN, to avoid unnecessary scanning.
- **Robust Target Handling**: Works with single targets, lists of targets, or files containing targets.

## Requirements

- Python 3.7+
- **masscan** installed and accessible in your system's PATH
- **httpx** installed and accessible in your system's PATH
- **cut-cdn** (optional): For detecting CDN IPs
- Python libraries: `argparse`, `socket`, `re`, `subprocess`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/service-discovery-tool.git
   cd service-discovery-tool
   ```

2. Install `masscan` and `httpx`:
   ```bash
   sudo apt install masscan
   go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
   ```

3. (Optional) Install `cut-cdn` for CDN detection:
   ```bash
   go install -v github.com/dwisiswant0/cut-cdn@latest
   ```

## Usage

Run the tool with either a list of targets from a file or a single target.

### Command-Line Options

| Option | Description |
|--------|-------------|
| `-f, --file` | Path to a file containing a list of IPs, domains, or CIDRs. |
| `-t, --target` | Single IP or domain (e.g., `1.1.1.1` or `example.com`). |

### Examples

#### Scan a single target:
```bash
python service_discovery.py -t example.com
```

#### Scan multiple targets from a file:
```bash
python service_discovery.py -f targets.txt
```

### Input File Format

The input file should contain a list of IPs, domains, or CIDRs, one per line:
```
1.1.1.1
example.com
192.168.0.0/24
```

## How It Works

1. **Target Processing**:
   - Validates the format of each target.
   - Resolves domain names to IP addresses.
   - Detects if IPs belong to a CDN.

2. **Scanning**:
   - For non-CDN IPs, `masscan` scans for open ports.
   - `httpx` is used to gather HTTP information for both CDN and non-CDN targets.

3. **Result Parsing**:
   - Extracts open ports from `masscan` output.
   - Outputs detailed HTTP information from `httpx`.

## Output

- **Masscan Results**: Saved in `masscan-res.txt`.
- **Discovered Ports**: Displayed in the terminal and passed to `httpx` for further processing.

## Banner

```
   ___              _           ____  _                                      
  / __| ___ _ _ ___| |_ ___ _ _|  _ \| |_  ___ _ __  ___ __ _ _ __ ___ _ _   
 | (_ |/ -_) '_/ -_)  _/ _ \ '_| | | | ' \/ -_) '  \/ -_) _` | '_/ _ \ ' \  
  \___|\___|_| \___|\__\___/_| |_| |_|_||_\___|_|_|_\___\__,_|_| \___/_||_|

        [~] Network Service Discovery Tool (masscan + httpx)
```

## Disclaimer

This tool is intended for authorized network security assessments only. Misuse of this tool may result in legal consequences. Ensure you have proper authorization before using it.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions or need support, feel free to contact: [your-email@example.com]
