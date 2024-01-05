import socket
import sys
import ssl
import os
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from colorama import init, Fore
import threading
import time
from bs4 import BeautifulSoup
import configparser

website = 'https://debugs.hashnode.dev/'
github = 'https://github.com/bibo318/Cloudflare-IP'

VERSION = '1.0.0'

R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'  # white
Y = '\033[33m'  # yellow

banner = r'''
______________            _____________________                         _______________ 
__  ____/__  /_________  _______  /__  __/__  /_____ ____________       ____  _/__  __ \
_  /    __  /_  __ \  / / /  __  /__  /_ __  /_  __ `/_  ___/  _ \_________  / __  /_/ /
/ /___  _  / / /_/ / /_/ // /_/ / _  __/ _  / / /_/ /_  /   /  __//_____/_/ /  _  ____/ 
\____/  /_/  \____/\__,_/ \__,_/  /_/    /_/  \__,_/ /_/    \___/       /___/  /_/ 
Khám phá địa chỉ IP thực sự của các trang web được bảo vệ bởi Cloudflare và khác.
'''

init()

def print_banners():
    """
    prints the program banners
    """
    print(f'{R}{banner}{W}\n')
    print(f'{G}[+] {Y}Version      : {W}{VERSION}')
    print(f'{G}[+] {Y}Created By   : {W}Bibo318')
    print(f'{G} \u2514\u27A4 {Y}Website      : {W}{website}')
    print(f'{G} \u2514\u27A4 {Y}Github       : {W}{github}\n')

def is_using_cloudflare(domain):
    try:
        response = requests.head(f"https://{domain}", timeout=5)
        headers = response.headers
        if "server" in headers and "cloudflare" in headers["server"].lower():
            return True
        if "cf-ray" in headers:
            return True
        if "cloudflare" in headers:
            return True
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
        pass

    return False

def detect_web_server(domain):
    try:
        response = requests.head(f"http://{domain}", timeout=5)
        server_header = response.headers.get("Server")
        if server_header:
            return server_header.strip()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
        pass

    return "UNKNOWN"

def get_ssl_certificate_info(host):
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=host) as sock:
            sock.connect((host, 443))
            certificate_der = sock.getpeercert(True)

        certificate = x509.load_der_x509_certificate(certificate_der, default_backend())

        # Trích xuất thông tin liên quan từ chứng chỉ
        common_name = certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        issuer = certificate.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        validity_start = certificate.not_valid_before
        validity_end = certificate.not_valid_after

        return {
            "Common Name": common_name,
            "Issuer": issuer,
            "Validity Start": validity_start,
            "Validity End": validity_end,
        }
    except Exception as e:
        print(f"{Fore.RED}Lỗi trích xuất thông tin chứng chỉ SSL: {e}{Fore.RESET}")
        return None

def find_subdomains_with_ssl_analysis(domain, filename, timeout=20):
    #nếu không thì is_using_cloudflare(domain):
        #print(f"{C}Trang web không sử dụng Cloudflare. Không cần quét tên miền phụ.{W}")
        #return

    subdomains_found = []
    subdomains_lock = threading.Lock()

    # quét tên miền phụ...

    def check_subdomain(subdomain):
        subdomain_url = f"https://{subdomain}.{domain}"

        try:
            response = requests.get(subdomain_url, timeout=timeout)
            if response.status_code == 200:
                with subdomains_lock:
                    subdomains_found.append(subdomain_url)
                    print(f"{Fore.GREEN}Đã tìm thấy tên miền phụ \u2514\u27A4: {subdomain_url}{Fore.RESET}")
        except requests.exceptions.RequestException as e:
            if "Đã vượt quá số lần thử lại tối đa với url" in str(e):
                pass

    with open(filename, "r") as file:
        subdomains = [line.strip() for line in file.readlines()]

    print(f"\n{Fore.YELLOW}Chủ đề bắt đầu...")
    start_time = time.time()

    threads = []
    for subdomain in subdomains:
        thread = threading.Thread(target=check_subdomain, args=(subdomain,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n{G} \u2514\u27A4 {C}Tổng số tên miền phụ được quét:{W} {len(subdomains)}")
    print(f"{G} \u2514\u27A4 {C}Tổng số tên miền phụ được tìm thấy:{W} {len(subdomains_found)}")
    print(f"{G} \u2514\u27A4 {C}Mất thời gian:{W} {elapsed_time:.2f} seconds")

    real_ips = []

    for subdomain in subdomains_found:
        subdomain_parts = subdomain.split('//')
        if len(subdomain_parts) > 1:
            host = subdomain_parts[1]
            real_ip = get_real_ip(host)
            if real_ip:
                real_ips.append((host, real_ip))
                print(f"\n{Fore.YELLOW}[+] {Fore.CYAN}Địa chỉ IP thực của {Fore.GREEN}{host}:{Fore.RED} {real_ip}")

                # Thực hiện phân tích chứng chỉ SSL
                ssl_info = get_ssl_certificate_info(host)
                if ssl_info:
                    print(f"{Fore.RED}   [+] {Fore.CYAN}Thông tin chứng chỉ SSL:")
                    for key, value in ssl_info.items():
                        print(f"{Fore.RED}      \u2514\u27A4 {Fore.CYAN}{key}:{W} {value}")

    if not real_ips:
        print(f"{R}Không tìm thấy địa chỉ IP thực cho tên miền phụ.")
    else:
        print("\nHoàn thành nhiệm vụ!!\n")
        # cho liên kết trong subdomains_found:
        # print(link)

def get_real_ip(host):
    try:
        real_ip = socket.gethostbyname(host)
        return real_ip
    except socket.gaierror:
        return None

#Đọc file cấu hình
def read_config():
    config = configparser.ConfigParser()
    #kiểm tra xem tập tin cấu hình có tồn tại không
    if not os.path.exists('config.ini'):
        #tạo tập tin cấu hình
        # Tạo phần [DEFAULT] và đặt tùy chọn securitytrails_api_key
        config["DEFAULT"] = {
        "securitytrails_api_key": "your_api_key"}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print(f"\n[!] {Fore.RED}Vui lòng thêm {C}SecurityTrails{Fore.RED} khóa API vào file config.ini {Fore.RESET}")
    else:
        config.read('config.ini')
        APIKEY = config['DEFAULT']['securitytrails_api_key']
        return APIKEY

def securitytrails_historical_ip_address(domain):
    if read_config() :
        url = f"https://api.securitytrails.com/v1/history/{domain}/dns/a"
        headers = {
        "accept": "application/json",
        "APIKEY": read_config()}
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            print(f"\n{Fore.GREEN}[+] {Fore.YELLOW}Thông tin địa chỉ IP lịch sử từ {C}SecurityTrails{Y} của {Fore.GREEN}{domain}:{W}")
            for record in data['records']:
                ip = record["values"][0]["ip"]
                first_seen = record["first_seen"]
                last_seen = record["last_seen"]
                organizations = record["organizations"][0]
                print(f"\n{R} [+] {C}IP Address: {R}{ip}{W}")
                print(f"{Y}  \u2514\u27A4 {C}First Seen: {G}{first_seen}{W}")
                print(f"{Y}  \u2514\u27A4 {C}Last Seen: {G}{last_seen}{W}")
                print(f"{Y}  \u2514\u27A4 {C}Organizations: {G}{organizations}{W}")
        except:
            print(f"{Fore.RED}Lỗi trích xuất thông tin Địa chỉ IP lịch sử từ SecurityTrails{Fore.RESET}")
            None
    else:
        print(f"{Fore.RED}Vui lòng thêm {C}SecurityTrails{Fore.RED} Khóa API của bạn vào file config.ini {Fore.RESET}")
        None

def get_domain_historical_ip_address(domain):
    try:
        url = f"https://viewdns.info/iphistory/?domain={domain}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    
        }
        response = requests.get(url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'border': '1'})

        if table:
            rows = table.find_all('tr')[2:]
            print(f"\n{Fore.GREEN}[+] {Fore.YELLOW}Thông tin địa chỉ IP lịch sử từ {C}Viewdns{Y} for {Fore.GREEN}{domain}:{W}")
            for row in rows:
                columns = row.find_all('td')
                ip_address = columns[0].text.strip()
                location = columns[1].text.strip()
                owner = columns[2].text.strip()
                last_seen = columns[3].text.strip()
                print(f"\n{R} [+] {C}IP Address: {R}{ip_address}{W}")
                print(f"{Y}  \u2514\u27A4 {C}Location: {G}{location}{W}")
                print(f"{Y}  \u2514\u27A4 {C}Owner: {G}{owner}{W}")
                print(f"{Y}  \u2514\u27A4 {C}Last Seen: {G}{last_seen}{W}")
        else:
            None
    except:
        None


if __name__ == "__main__":
    domain = sys.argv[1]  # chuyển miền trong đối số dòng lệnh, ví dụ: python3 cloakquest3r.py top.gg
    filename = "wordlist2.txt"
    print_banners()
    CloudFlare_IP = get_real_ip(domain)

    print(f"\n{Fore.GREEN}[!] {C}Kiểm tra xem trang web có sử dụng Cloudflare không{Fore.RESET}\n")

    if is_using_cloudflare(domain):

        print(f"\n{R}Trang web mục tiêu: {W}{domain}")
        print(f"{R}Địa chỉ IP hiển thị: {W}{CloudFlare_IP}\n")
        get_domain_historical_ip_address(domain)
        securitytrails_historical_ip_address(domain)
        print(f"\n{Fore.GREEN}[+] {Fore.YELLOW}Đang quét tên miền phụ.{Fore.RESET}")
        find_subdomains_with_ssl_analysis(domain, filename)

    else:
        print(f"{Fore.RED}- Trang web không sử dụng Cloudflare.")
        
        # Xác định công nghệ nó đang sử dụng
        technology = detect_web_server(domain)
        print(f"\n{Fore.GREEN}[+] {C}Trang web đang sử dụng: {Fore.GREEN} {technology}")

        # Hỏi người dùng xem họ có muốn tiếp tục không
        proceed = input(f"\n{Fore.YELLOW}> Bạn có muốn tiếp tục? {Fore.GREEN}(Có/không): ").lower()

        if proceed == "có":
            # Thêm chức năng cho công nghệ cụ thể tại đây
            print(f"\n{R}Trang web mục tiêu: {W}{domain}")
            print(f"{R}Địa chỉ IP hiển thị: {W}{CloudFlare_IP}\n")
            get_domain_historical_ip_address(domain)
            securitytrails_historical_ip_address(domain)

            print(f"{Fore.GREEN}[+] {Fore.YELLOW}Đang quét tên miền phụ.{Fore.RESET}")
            find_subdomains_with_ssl_analysis(domain, filename)
        else:
            print(f"{R}Hoạt động bị hủy bỏ. Đang thoát...{W}")

