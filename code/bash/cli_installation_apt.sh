sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://pkgs.galtea.ai/public.key \
  | sudo tee /etc/apt/keyrings/galtea.asc > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/galtea.asc] \
  https://pkgs.galtea.ai/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/galtea.list

sudo apt update
sudo apt install galtea
