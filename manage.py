from pathlib import Path
from urllib.request import urlopen
import string
import random
import os

USERS = ["Alice", "Bob", "Charlie"]
DOCKERPATH = Path("./newbie")
MYSQLPASSWD = ''
PASSLENGTH = 32

users = []
deployComposePath = Path("docker-compose.deploy.yml")

def create():
    DOCKERPATH.mkdir(exist_ok=True)
    if deployComposePath.exists():
        deploy = deployComposePath.read_text()
    else:
        url = urlopen("https://raw.githubusercontent.com/sparcs-kaist/newbie-image/main/docker-compose.deploy.yml")
        deployComposePath.write_text(url.read().decode())

    for user in USERS:
        userPath = DOCKERPATH / user
        userPath.mkdir(exist_ok=True)
        userComposePath = userPath / "docker-compose.yml"

        upass = ''.join(random.choices(string.ascii_letters + string.digits, k=PASSLENGTH))
        uc = deploy.replace("||NEW_PASSWORD||", upass)
        uc = uc.replace("||MYSQL_ROOT_PASSWORD||", MYSQLPASSWD)
        userComposePath.write_text(uc)
        users.append(userPath)

def stop():
    for user in users:
        if not (user / "docker-compose.yml").exists():
            raise FileNotFoundError(f"docker-compose.yml not found for {user}")
        
        os.system(f"cd {user} && docker-compose down")

def start():
    for user in users:
        if not (user / "docker-compose.yml").exists():
            raise FileNotFoundError(f"docker-compose.yml not found for {user}")
        
        os.system(f"cd {user} && docker-compose up -d --build")

def getpass():
    for user in users:
        if not (user / "docker-compose.yml").exists():
            raise FileNotFoundError(f"docker-compose.yml not found for {user}")
        passwd = (user / "docker-compose.yml").read_text().split("MYSQL_PASSWORD=")[1].split("\n")[0]
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