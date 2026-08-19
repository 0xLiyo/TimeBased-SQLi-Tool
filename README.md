# Time-Based Blind SQL Injection Tool

A lightweight Python utility for authorized security testing of **time-based blind SQL injection** vulnerabilities.

The tool accepts a raw HTTP request, replaces configurable placeholders, sends requests to the target, and detects potential matches based on response time.

> ⚠️ **Disclaimer:** This tool is intended for authorized security testing, CTFs, security labs, and educational purposes only. Do not use it against systems or applications without explicit permission.

## Features

* Parse raw HTTP request packets
* Support for `GET`, `POST`, and other HTTP methods
* Automatic extraction of the `sleep()` delay from the request
* Character-by-character testing
* Configurable numeric range
* Configurable request rate and interval
* Optional request debugging
* Automatic response-time comparison
* Extracted character mapping and final output

## Requirements

* Python 3.8+
* `requests`

Install the dependency with:

```bash
pip install requests
```

Or use the included `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/time-based-sqli-tool.git
cd time-based-sqli-tool
```

Install the required package:

```bash
pip install -r requirements.txt
```

## Usage

Run the script:

```bash
python sqli_tool.py
```

The program will ask for a raw HTTP request.

Example structure:

```http
POST /example HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

id=1
```

The input packet should be terminated with an empty line.

## Placeholders

The tool supports two placeholders inside the HTTP request.

### `XXX`

`XXX` is replaced with the numeric value being tested.

For example:

```text
id=XXX
```

If the configured range is `1` to `3`, the tool will test:

```text
id=1
id=2
id=3
```

### `FUZZ`

`FUZZ` is replaced character-by-character using the tool's built-in character set.

The current character set contains:

* Numbers `0-9`
* `+`
* Lowercase letters `a-z`
* `_`
* `-`
* Uppercase letters `A-Z`

Example:

```text
id=XXX' AND ... FUZZ ...
```

## Configuration

During execution, the tool asks for several parameters.

### Start / End Number

Defines the numeric range used for `XXX`.

```text
Start number for XXX:
End number for XXX:
```

### Requests Per Interval

Controls how many requests are sent within the configured interval.

```text
Requests per interval:
```

### Interval

Defines the interval duration in milliseconds.

```text
Interval (ms):
```

These values are used to calculate a delay between requests.

### Debug Mode

The program can optionally display request details:

```text
Show request details? (y/n):
```

When enabled, it can display:

* Request URL
* Headers
* POST body
* Request errors

Avoid using debug mode when working with sensitive credentials, tokens, cookies, or other private information.

## Detection Method

The tool measures the time required for each HTTP request.

It searches the request for a `sleep()` expression and uses the detected value as the response-time threshold.

For example:

```text
sleep(3)
```

results in a default threshold of approximately:

```text
3000 ms
```

If no `sleep()` expression is found, the default threshold is:

```text
3000 ms
```

A response reaching or exceeding the threshold is reported as a potential match.

## Output

During execution, the tool displays the tested values and measured response times.

Example:

```text
[+] Sleep threshold: 3000 ms

[+] Attack started...

[-] XXX=1 CHAR='a' => 142ms
[-] XXX=1 CHAR='b' => 137ms
[+] XXX=1 CHAR='c' => 3012ms (HIT)
```

At the end, the tool displays:

```text
[+] Total requests: 123

[+] Extracted string: ...

[+] Detailed mapping:
  1 -> c
  2 -> ...
  3 -> ...
```

## Project Structure

```text
time-based-sqli-tool/
├── README.md
├── sqli_tool.py
├── requirements.txt
└── .gitignore
```

## Security Notes

This project is designed for controlled and authorized environments.

Use it only against:

* Your own applications
* Systems where you have explicit authorization
* CTF challenges
* Local security labs
* Intentionally vulnerable applications

Do not use this tool to access, extract, or manipulate data from systems without authorization.

## Known Limitations

The current implementation intentionally keeps request parsing and response detection simple.

Some limitations include:

* Raw HTTP parsing is basic and may not support every HTTP request format.
* The tool relies primarily on response time for detection.
* Network latency can affect results.
* HTTPS certificate verification is disabled in the current implementation.
* Only a predefined character set is tested.
* Some applications may require additional request handling or authentication logic.

## Future Improvements

Possible improvements include:

* Better HTTP request parsing
* Configurable character sets
* More reliable timing analysis
* Connection/session reuse
* Proxy support
* Improved error handling
* Command-line arguments
* Result export
* More detailed logging

## License

MIT License

---

**For educational and authorized security testing only.**
