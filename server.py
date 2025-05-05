import os
import csv
import re
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
from urllib.parse import parse_qs, urlparse

# Global CSV file path
DEFAULT_CSV_FILE = 'available_domains.csv'

def clean_number(value):
    """Extract numeric values from strings, handling commas and other formats."""
    if isinstance(value, str):
        # Remove commas and other non-numeric characters except decimal points
        clean = re.sub(r'[^\d.]', '', value)
        try:
            return float(clean) if clean else 0
        except ValueError:
            return 0
    return 0

def read_csv_data(csv_file=DEFAULT_CSV_FILE):
    """Read CSV data and return headers and rows."""
    if not os.path.exists(csv_file):
        return [], []
    
    headers = []
    data = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, [])  # Get headers
        for row in reader:
            data.append(row)
    
    return headers, data

def find_highest_backlinks(headers, data):
    """Find the highest backlinks value in the data."""
    # Find backlinks column
    backlinks_idx = -1
    for i, header in enumerate(headers):
        if "backlinks" in header.lower():
            backlinks_idx = i
            break
    
    if backlinks_idx == -1 or not data:
        return 0
    
    highest = 0
    for row in data:
        if len(row) > backlinks_idx:
            value = clean_number(row[backlinks_idx])
            highest = max(highest, value)
    
    return highest

class DomainViewerHandler(SimpleHTTPRequestHandler):
    """Custom request handler for serving the domain viewer."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Serve the template.html file
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open('html/template.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Get CSV data
            headers, data = read_csv_data()
            highest_backlinks = find_highest_backlinks(headers, data)
            
            # Create JavaScript to inject
            js_data = f"""
            // Fill in the data
            const tableHeaders = {json.dumps(headers)};
            const tableData = {json.dumps(data)};
            const highestBacklinks = {highest_backlinks};
            """
            
            # Replace placeholder with actual data
            html_content = html_content.replace('const tableData = [];', f'const tableData = {json.dumps(data)};')
            html_content = html_content.replace('const tableHeaders = [];', f'const tableHeaders = {json.dumps(headers)};')
            html_content = html_content.replace('let highestBacklinks = 0;', f'let highestBacklinks = {highest_backlinks};')
            
            self.wfile.write(html_content.encode('utf-8'))
            return
        
        # Serve data.json for AJAX requests
        elif path == '/data.json':
            headers, data = read_csv_data()
            highest_backlinks = find_highest_backlinks(headers, data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {
                'headers': headers,
                'data': data,
                'highestBacklinks': highest_backlinks
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return
            
        # For other files, use the default handler
        return SimpleHTTPRequestHandler.do_GET(self)

def run_server(port=8000):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DomainViewerHandler)
    print(f"Starting server at http://localhost:{port}")
    
    # Open browser
    webbrowser.open(f'http://localhost:{port}')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server() 