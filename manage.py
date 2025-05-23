#!/usr/bin/python3
from urllib.request import urlopen
from subprocess import Popen, PIPE
from pathlib import Path
import random
import string
import socket
import sys
import os

from settings import *

# check python version 3.9+
if sys.version_info < (3, 9):
    print("Python 3.6+ is required")
    sys.exit(1)

reserv_port = []

#if os.system("docker-compose --version") == 0:   dcommand = "docker-compose"
#elif os.system("docker compose --version") == 0: dcommand = "docker compose"
if Popen("docker compose --version", shell=True, stdout=PIPE, stderr=PIPE).wait() == 0: dcommand = "docker compose"
elif Popen("docker-compose --version", shell=True, stdout=PIPE, stderr=PIPE).wait() == 0:   dcommand = "docker-compose"
else: raise FileNotFoundError("docker-compose not found")

def nginx():
    if Path(NGINXPATH).exists():
        for file in Path(NGINXPATH).iterdir():
            if file.is_file():
                file.unlink()
    else:
        Path(NGINXPATH).mkdir(parents=True, exist_ok=True)
    
    # web: {username}.newbie.sparcs.me
    # api: {username}.api.newbie.sparcs.me
    users = load_info()
    for user, key in users.items():
        apiConf = NGINXCONF.format(domain=f"{user}.api.newbie.sparcs.me", port=key["port8000"])
        webConf = NGINXCONF.format(domain=f"{user}.newbie.sparcs.me", port=key["port3000"])
        apiConfPath = Path(NGINXPATH) / f"{user}.api.newbie.sparcs.me.conf"
        webConfPath = Path(NGINXPATH) / f"{user}.newbie.sparcs.me.conf"
        apiConfPath.write_text(apiConf)
        webConfPath.write_text(webConf)
    
    print("Nginx config created")


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
    

def create(manual_user: str = ""):
    Path(DOCKERPATH).mkdir(exist_ok=True)
    deployComposePath = Path("docker-compose.deploy.yaml")

    if deployComposePath.exists():
        deploy = deployComposePath.read_text()
    else:
        url = urlopen("https://raw.githubusercontent.com/sparcs-kaist/newbie-image/main/docker-compose.deploy.yaml")
        deploy = url.read().decode()
        deployComposePath.write_text(deploy)

    if manual_user:
        _add(manual_user)
    else:
        for user in USERS:
            _add(user)

def _add(name: str):
    userPath = Path(DOCKERPATH) / name
    userPath.mkdir(exist_ok=True)
    userComposePath = userPath / "docker-compose.yaml"
    upass = ''.join(random.choices(string.ascii_letters + string.digits, k=PASSLENGTH))
    uc = Path("docker-compose.deploy.yaml").read_text()
    uc = uc.replace("||NEW_PASSWORD||", upass)
    uc = uc.replace("||MYSQL_ROOT_PASSWORD||", MYSQLPASSWD)
    uc = uc.replace("||USER||", name)
    port1, port2, port3 = create_three_ports()
    uc = uc.replace("||PORT22||", str(port1))
    uc = uc.replace("||PORT3000||", str(port2))
    uc = uc.replace("||PORT8000||", str(port3))
    userComposePath.write_text(uc)

def stop():
    for user in Path(DOCKERPATH).iterdir():
        ucPath = user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker compose.yml not found for {user}")
        
        os.system(f"cd {str(ucPath.parent)} && {dcommand} down")

def start():
    for user in Path(DOCKERPATH).iterdir():
        ucPath = user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker-compose.yml not found for {user}")
        
        os.system(f"cd {str(ucPath.parent)} && {dcommand} up -d --build")

def load_info() -> dict[str, dict[str, str]]:
    """
    Load the user information from the docker-compose.yaml file.

    Returns:
        dict: A dictionary containing the user information.

    Example return:
    {
        "user1": {
            "password": "password1",
            "port22": 17000,
            "port3000": 17001,
            "port8000": 17002
        },
        ...
    }
    """
    user_info = {}
    for user in Path(DOCKERPATH).iterdir():
        ucPath = user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker compose.yml not found for {user}")
        passwd = ucPath.read_text().split("NEW_PASSWORD=")[1].split("\n")[0]
        portstr = ucPath.read_text().split("ports:")[1].split("volumes")[0].split("- \"")[1:]
        user_info[user.name] = {
            "password": passwd,
            "port22": int(portstr[0].split(":")[0]),
            "port3000": int(portstr[1].split(":")[0]),
            "port8000": int(portstr[2].split(":")[0])
        }
    return user_info

def getpass():
    for user, info in load_info().items():
        print(PRINTINFO.format(user=user, passwd=info["password"], port22=info["port22"], port3000=info["port3000"], port8000=info["port8000"]))

def create_menu():
    while True:
        print("1. Create based on settings.py")
        print("2. Create manually")
        print("3. Back")

        choice = input("Enter your choice: ")
        if choice == "1":
            create()
        elif choice == "2":
            name = input("Enter the name of the user: ")
            create(name)
        elif choice == "3":
            break
        else:
            print("Invalid choice")

def backup():
    COMMAND="""docker exec -it {user}-app su - sparcs -c "mysqldump -u root --password=tnfqkrtm -h db --all-databases > ~/backup.sql" """

    for user in Path(DOCKERPATH).iterdir():
        user = user.name
        print(f"Woring for {user} backup...")
        os.system(COMMAND.format(user=user))
    
    print("Backup done")

def main():
    while True:
        print("1. Create docker-compose files")
        print("2. Start docker-compose")
        print("3. Stop docker-compose")
        print("4. Get passwords")
        print("5. Backup")
        print("6. Create nginx config")
        print("7. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            create_menu()
        elif choice == "2":
            start()
        elif choice == "3":
            stop()
        elif choice == "4":
            getpass()
        elif choice == "5":
            backup()
        elif choice == "6":
            nginx()
        elif choice == "7":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()