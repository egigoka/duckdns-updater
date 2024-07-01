import requests
import time
from secrets import DUCKDNS_TOKEN, DUCKDNS_DOMAIN


def print_safe(*args, **kwargs):
    args = list(args)

    secrets = {
        DUCKDNS_TOKEN: "<token>"
    }

    for secret, replace in secrets.items():
        for cnt, arg in enumerate(args):
            args[cnt] = arg.replace(secret, replace)

        for key in kwargs.keys():
            kwargs[key] = kwargs[key].replace(secret, replace)

    print(*args, **kwargs)


def get_public_ip():
    """Get the current public IP address."""
    for i in range(10):
        try:
            response = requests.get("http://ipinfo.io/ip")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(60)
            print(f"connection error, retrying in 60 seconds... retry {i+1}")
    return response.text.strip()


def update_dns(token, domain, ip):
    """Update the DNS record."""
    response = requests.get(f"https://www.duckdns.org/update?domains={domain}&token={token}&ip={ip}")
    return response.text


def main():
    current_ip = get_public_ip()

    try:
        with open('last_ip.txt', 'r') as file:
            last_ip = file.read().strip()
    except FileNotFoundError:
        last_ip = None

    if current_ip == last_ip:
        return

    print_safe(f"Updating {DUCKDNS_DOMAIN}.duckdns.org to {current_ip}")

    status = update_dns(DUCKDNS_TOKEN, DUCKDNS_DOMAIN, current_ip)

    success = True if status == "OK" else False

    if success:
        with open('last_ip.txt', 'w') as file:
            file.write(current_ip)
    else:
        print_safe("Failed to update DNS records. Status: {status}")


if __name__ == "__main__":
    main()
