if [ -d "Clients/logs/" ]; then
    if [ "$(ls -A Clients/logs/)" ]; then
        rm Clients/logs/*
        echo ">>> Logs is cleared."
    else
        echo ">>> Logs is empty."
    fi
else
    mkdir "Clients/logs/"
    echo ">>> Logs is Created."
fi

for i in {1..10}
do
   python3 src/main.py -p1 "Clients/Python/main.py" -p2 "Clients/Python/main.py"
    echo ">>> server runned."
done


# chmod +x ../AICup2022-x86_64.AppImage
# ../AICup2022-x86_64.AppImage
