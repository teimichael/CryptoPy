sudo apt-get update
sudo apt-get install build-essential libssl-dev libffi-dev python3-pip python3-dev
pip3 install --upgrade pip
pip3 install pyopenssl ndg-httpsclient pyasn1
tar -zxvf ta-lib-0.4.0-src.tar.gz
( cd ta-lib/ ; ./configure --prefix=/usr && make && sudo make install )
( cd ../ ; pip3 install -r requirements.txt )