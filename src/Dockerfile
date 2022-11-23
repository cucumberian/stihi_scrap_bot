from python:3.10-slim

run apt-get update
run apt-get install texlive-fonts-recommended -y
run apt-get install texlive-lang-cyrillic -y
run apt-get install texlive-latex-extra -y
run apt clean && rm -rf /var/lib/apt/lists/*

run mkdir -p /usr/src/app/
workdir /usr/src/app/

copy app.py requirements.txt /usr/src/app/

run python3 -m pip install --upgrade pip
run pip3 install --no-cache-dir -r requirements.txt

cmd ["python3", "app.py"]
