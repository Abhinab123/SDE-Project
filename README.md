# SDE-Project
This the Github Repo For The SDE final Project on E-Commerce Recommendation System using Big Data Analytics

# Steps to Install Docker and Docker Compose

## **1. Update System Packages**
```bash
sudo apt-get update
```

## **2. Uninstall Old Versions (if any)**
```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

## **3. Install Required Dependencies**
```bash
sudo apt-get install ca-certificates curl gnupg lsb-release
```

## **4. Add Docker’s Official GPG Key**
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

## **5. Add Docker Repository**
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

## **6. Install Docker Engine**
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## **7. Verify Docker Installation**
```bash
docker --version
```

## **8. Run Docker Without Sudo (Optional)**
```bash
sudo usermod -aG docker $USER
```
> Log out and log back in for the changes to take effect.

---

#  Install Docker Compose

> **Note:** Newer versions of Docker already include Docker Compose as a plugin.  
> If it’s not available, follow the steps below.

## **1. Download Latest Docker Compose Binary**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

## **2. Apply Executable Permissions**
```bash
sudo chmod +x /usr/local/bin/docker-compose
```

## **3. Verify Docker Compose Installation**
```bash
docker compose version
```
> If the above command doesn’t work, try:
```bash
docker-compose --version
```

---

# Test the Installation

Run the following command to confirm everything is working correctly:
```bash
docker run hello-world
```

If message **“Hello from Docker!”**, is displayed. Docker and Docker Compose have been successfully installed.
