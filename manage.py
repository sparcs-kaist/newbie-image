from pathlib import Path
from urllib.request import urlopen
import string
import random
import os

from settings import USERS, PASSLENGTH, MYSQLPASSWD, DOCKERPATH

DOCKERPATH = Path(DOCKERPATH)
users = []

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
        userComposePath.write_text(uc)
        users.append(userPath)

def stop():
    for user in USERS:
        ucPath = DOCKERPATH / user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker compose.yml not found for {user}")
        
        os.system(f"cd {str(ucPath.parent)} && docker-compose down")

def start():
    for user in USERS:
        ucPath = DOCKERPATH / user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker-compose.yml not found for {user}")
        
        os.system(f"cd {str(ucPath.parent)} && docker compose up -d --build")

def getpass():
    for user in USERS:
        ucPath = DOCKERPATH / user / "docker-compose.yaml"
        if not ucPath.exists():
            raise FileNotFoundError(f"docker compose.yml not found for {user}")
        passwd = ucPath.read_text().split("NEW_PASSWORD=")[1].split("\n")[0]
        print(f"{user}:{passwd}")

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