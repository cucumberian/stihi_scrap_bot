from python:3.12-slim

run apt-get update
run apt-get install texlive-fonts-recommended -y
run apt-get install texlive-lang-cyrillic -y
run apt-get install texlive-latex-extra -y
run apt clean && rm -rf /var/lib/apt/lists/*

ENV APP_HOME=/usr/src/app

RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .

cmd ["python3", "app.py"]
