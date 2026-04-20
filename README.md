python3 -m venv iha_venv
source iha_venv/bin/activate
sudo apt-get install python3-dev python3-opencv python3-wxgtk4.0 python3-pip python3-matplotlib python3-lxml python3-pygame
python3 -m pip install PyYAML mavproxy
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc


sim_vehicle.py -w -v ArduPlane --console --map
