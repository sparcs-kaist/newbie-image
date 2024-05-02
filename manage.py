from urllib.request import urlopen
from subprocess import Popen, PIPE
from pathlib import Path
import random
import string
import socket
import sys
import os

from settings import *

# check python version 3.6+
if sys.version_info < (3, 6):
    print("Python 3.6+ is required")
    sys.exit(1)


DOCKERPATH = Path(DOCKERPATH)
reserv_port = []
users = []

#if os.system("docker-compose --version") == 0:   dcommand = "docker-compose"
#elif os.system("docker compose --version") == 0: dcommand = "docker compose"
if Popen("docker-compose --version", shell=True, stdout=PIPE, stderr=PIPE).wait() == 0:   dcommand = "docker-compose"
elif Popen("docker compose --version", shell=True, stdout=PIPE, stderr=PIPE).wait() == 0: dcommand = "docker compose"
else: raise FileNotFoundError("docker-compose not found")


def port_usage(port: int):
    #if os.system("netstat --version") == 0:
    #    return os.system(f"netstat -tuln | grep {port}")
    #elif os.system("lsof -h") == 0:
    #    return os.system(f"lsof -i :{port}")
    if Popen("netstat --version", shell=True, stdout=PIPE, stderr=PIPE).wait() == 0:
        return Popen(f"netstat -tuln | grep {port}", shell=True, stdout=PIPE, stderr=PIPE).wait()
    elif Popen("lsof -h", shell=True, stdout=PIPE, stderr=PIPE).wait() == 0:
        return Popen(f"lsof -i :{port}", shell=True, stdout=PIPE, stderr=PIPE).wait()
    else:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("0.0.0.0", port))
            sock.close()
            return 0
        except OSError:
            return 1

def get_port():
    while True:
        port = random.randint(*PORTRANGE)
        if port not in reserv_port and port_usage(port) != 0:
            reserv_port.append(port)
            return port

def create_three_ports():
    while True:
        port1 = get_port()
        port2 = get_port()
        port3 = get_port()
        if port1 != port2 and port2 != port3 and port1 != port3:
            reserv_port.append(port1)
            reserv_port.append(port2)
            reserv_port.append(port3)
            return port1, port2, port3
    

def create():
    DOCKERPATH.mkdir(exist_ok=True)
    deployComposePath = Path("docker-compose.deploy.yaml")

    if deployComposePath.exists():
        deploy = deployComposePath.read_text()
    else:
        url = urlopen("https://raw.githubusercontent.com/sparcs-kaist/newbie-image/main/docker-compose.deploy.yaml")
        deploy = url.read().decode()

    for user in USERS:
        userPath = DOCKERPATH / user
        userPath.mkdir(exist_ok=True)
        userComposePath = userPath / "docker-compose.yaml"
        
        upass = ''.join(random.choices(string.ascii_letters + string.digits, k=PASSLENGTH))
        uc = deploy.replace("||NEW_PASSWORD||", upass)
        uc = uc.replace("||MYSQL_ROOT_PASSWORD||", MYSQLPASSWD)
        uc = uc.replace("||USER||", user)
        port1, port2, port3 = create_three_ports()
        uc = uc.replace("||PORT22||", str(port1))
        uc = uc.replace("||PORT3000||", str(port2))
        uc = uc.replace("||PORT8000||", str(port3))
        userComposePath.write_text(uc)
        users.append(userPath)

def stop():
    for user in USERS:
        ucPath = DOCKERPATH / user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker compose.yml not found for {user}")
        
        os.system(f"cd {str(ucPath.parent)} && {dcommand} down")

def start():
    for user in USERS:
        ucPath = DOCKERPATH / user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker-compose.yml not found for {user}")
        
        os.system(f"cd {str(ucPath.parent)} && {dcommand} up -d --build")

def getpass():
    for user in USERS:
        ucPath = DOCKERPATH / user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker compose.yml not found for {user}")
        passwd = ucPath.read_text().split("NEW_PASSWORD=")[1].split("\n")[0]
        portstr = ucPath.read_text().split("ports:")[1].split("volumes")[0].split("- \"")[1:]
        port1 = portstr[0].split(":")[0]
        port2 = portstr[1].split(":")[0]
        port3 = portstr[2].split(":")[0]
        print(PRINTINFO.format(user=user, passwd=passwd, port22=port1, port3000=port2, port8000=port3))

def main():
    while True:
        print("1. Create docker-compose files")
        print("2. Start docker-compose")
        print("3. Stop docker-compose")
        print("4. Get passwords")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            create()
        elif choice == "2":
            start()
        elif choice == "3":
            stop()
        elif choice == "4":
            getpass()
        elif choice == "5":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()