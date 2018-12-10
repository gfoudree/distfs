FROM fedora:latest

RUN dnf update -y 

RUN dnf install python3 procps net-tools python3-pip -y

RUN pip3 install kademlia asyncio
RUN mkdir /app

WORKDIR /app

COPY . .


CMD ["python3", "main.py"]
