FROM ubuntu:24.04

# Install dependencies
RUN sed -i 's/archive.ubuntu.com/ftp.kaist.ac.kr/g' /etc/apt/sources.list.d/ubuntu.sources && \
    sed -i 's/security.ubuntu.com/ftp.kaist.ac.kr/g' /etc/apt/sources.list.d/ubuntu.sources

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    git \
    vim \
    curl \
    wget \
    unzip \
    openssh-server \
    sudo

RUN userdel -r ubuntu && \
    useradd -m -s /bin/bash sparcs && \
    chown -R sparcs:sparcs /home/sparcs && \
    adduser sparcs sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo 'Banner /etc/banner' >> /etc/ssh/sshd_config
RUN su - sparcs -c 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash'
RUN tar czf /sparcs-home.tar.gz /home/sparcs

ADD docker-entrypoint.sh /docker-entrypoint.sh
ADD banner /etc/banner
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]