#!env zsh

if ! command -v python3 &>/dev/null
then
    echo "Python is not installed. Please install it and try again."
    exit 1
fi

if ! command -v pip3 &>/dev/null
then
    echo "pip is not installed. Please install it and try again."
    exit 1
fi


pip3 install -r requirements.txt > /dev/null

chmod +x odpd.py
sudo cp "odpd.py" /usr/local/bin

echo -e "[+] Install Complete: odpd.py"