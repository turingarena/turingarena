# Install Turingarena on Ubuntu 18.04 LTS

The task of this guide is to let you install Turingarena from scratch on a new machine with Ubuntu 18.04 LTS as OS

For the installation we recommend you to have at least 20 GB of free space on your hard disk

## Step 1 - Install requirements

```bash
sudo apt update
sudo apt upgrade
sudo apt install git
sudo apt install build-essential
wget -q -O- https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo apt install tmux
```

## Step 2 - Download the repo

```bash
git clone https://github.com/turingarena/turingarena.git
```

## Step 3 - Install  task-maker-rust

```bash
wget https://github.com/edomora97/task-maker-rust/releases/download/v0.4.0/task-maker-rust_0.4.0_amd64.deb
sudo dpkg -i task-maker-rust_0.4.0_amd64.deb
```

## Step 4 - Install Turingarena

From the folder `turingarena` execute:

```bash
cd server
sudo npm ci
cd ../web
sudo npm ci
```

## Step 5 - Increase the inotify watch limit

```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
```

