sudo apt update
apt list -a galtea                 # list the versions

sudo apt install galtea=5.4.0      # also downgrades a newer installed CLI
sudo apt-mark hold galtea          # keep 5.4.0 on `apt upgrade`
