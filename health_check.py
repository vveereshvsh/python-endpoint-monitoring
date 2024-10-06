import time
import requests
import yaml
import argparse


class HealthCheck:
    def __init__(self, config_file):
        self.endpoints = self.load_config(config_file)
        self.domain_stats = {}  # Store stats for each domain
        self.test_cycles = 0  # Track number of test cycles

    def load_config(self, file_path):
        """Load and parse the YAML configuration file."""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

    def check_endpoint(self, endpoint):
        """Send an HTTP request to the endpoint and return if it's UP or DOWN."""
        # Extract required fields
        url = endpoint['url']
        name = endpoint['name']  # Name is required, but not used in this implementation

        # Extract optional fields with default values
        method = endpoint.get('method', 'GET').upper()
        headers = endpoint.get('headers', {})  # Default is no custom headers
        body = endpoint.get('body', None)  # Default is no body (for POST requests)

        try:
            start_time = time.time()

            # Handle different methods with or without body
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=5)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=body, timeout=5)
            else:
                # Support additional methods like PUT, DELETE, etc. if needed
                response = requests.request(method, url, headers=headers, data=body, timeout=5)

            latency = (time.time() - start_time) * 1000  # Convert to ms
            if 200 <= response.status_code < 300 and latency < 500:
                return True, latency
            else:
                return False, latency
        except requests.exceptions.RequestException:
            return False, 0

    def update_stats(self, domain, status):
        """Update the domain availability stats based on the test result."""
        if domain not in self.domain_stats:
            self.domain_stats[domain] = {'total': 0, 'up': 0}

        self.domain_stats[domain]['total'] += 1
        if status == 'UP':
            self.domain_stats[domain]['up'] += 1

    def log_availability(self):
        """Log the availability of each domain to the console."""
        for domain, stats in self.domain_stats.items():
            availability = 100 * (stats['up'] / stats['total'])
            print(f"{domain} has {round(availability)}% availability")

    def run_health_checks(self):
        """Run the health checks continuously every 15 seconds."""
        while True:
            self.test_cycles += 1
            print(f"Starting test cycle #{self.test_cycles}")

            for endpoint in self.endpoints:
                domain = endpoint['url'].split("//")[-1].split("/")[0]  # Extract domain
                is_up, _ = self.check_endpoint(endpoint)
                status = 'UP' if is_up else 'DOWN'
                self.update_stats(domain, status)

            self.log_availability()
            time.sleep(15)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP Endpoint Health Checker")
    parser.add_argument('config', type=str, help="Path to YAML config file")
    args = parser.parse_args()

    health_check = HealthCheck(args.config)
    health_check.run_health_checks()
