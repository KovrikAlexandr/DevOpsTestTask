import paramiko
import math
import os
import logging
import subprocess

# Параметры нормализации
K_LOADAVG = 6
T_LOADAVG = 1

K_RAM = -2
T_RAM = 2

K_MEM = -0.2
T_MEM = 10

# Пути до файлов
SERVER_LOAD_SCRIPT_FILENAME = "../sh-scripts/get-server-load.bash"
SERVER_LOAD_SCRIPT_REMOTE = "/tmp/script"
INVENTORY_FILENAME = "../ansible/generated/inventory.ini"
PLAYBOOK_FILENAME = "../ansible/pb.yaml"
DB_VARS_FILENAME = "../ansible/generated/vars.yaml"
PG_CONFIG_FILENAME = "../ansible/files/pg_hba.conf"
SSH_KEYFILENAME = "~/.ssh/keys/vm_key"

def normalize(x, k, t):
    g = 100
    p = -k * (x - t)
    if p > 700:

        return 0
    elif p < -700:

        return g

    return g / (1 + math.exp(p))


def get_server_loading(hostname, port, username, key_filename):
    logging.info(f"Hostname is {hostname}, Port is {port}, Username is {username}, Key filename is {key_filename}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        username=username,
        port=port,
        key_filename=os.path.expanduser(key_filename)
    )

    logging.info("Connected successfully")

    sftp = client.open_sftp()
    sftp.put(SERVER_LOAD_SCRIPT_FILENAME, SERVER_LOAD_SCRIPT_REMOTE)
    sftp.close()

    logging.info("Script put successfully")

    stdin, stdout, stderr = client.exec_command(f"bash {SERVER_LOAD_SCRIPT_REMOTE}")
    output = stdout.read().decode()
    client.exec_command(f"rm {SERVER_LOAD_SCRIPT_REMOTE}")
    client.close()

    values = map(float, output.strip().splitlines())
    loadavg, ram, mem = values

    logging.info(f"Hostname: {hostname} - LA: {loadavg}, RAM: {ram}, MEM: {mem}")

    loadavg_normalized = normalize(loadavg, K_LOADAVG, T_LOADAVG)
    ram_normalized = normalize(ram / 1024, K_RAM, T_RAM)
    mem_normalized = normalize(mem / 1024, K_MEM, T_MEM)

    return (loadavg_normalized + ram_normalized + mem_normalized) / 3


def add_group_to_inventory(group_name, hostnames):
    lines = [f"[{group_name}]"]
    for hostname in hostnames:
        lines.append(f"{hostname} ansible_user=root ansible_port=22 ansible_ssh_private_key_file={SSH_KEYFILENAME}")
    content = "\n".join(lines) + "\n"
    with open(INVENTORY_FILENAME, "a") as f:
        f.write(content)


def clear_inventory_file():
    with open(INVENTORY_FILENAME, "w") as f:
        f.write("")

def create_db_vars(hostname, port, db_name, username, password):
    lines = [
        f"hostname: {hostname}",
        f"port: {port}",
        f"name: {db_name}",
        f"username: {username}",
        f"password: {password}"
    ]
    content = "\n".join(lines) + "\n"
    with open(DB_VARS_FILENAME, "a") as f:
        f.write(content)


def create_pg_config_file(hostnames):
    with open(PG_CONFIG_FILENAME, "w") as config:
        for hostname in hostnames:
            line = f"host    all    student    {hostname}/32    md5\n"
            config.write(line)


def run_ansible():
    result = subprocess.run(
        ["ansible-playbook", "-i", INVENTORY_FILENAME, PLAYBOOK_FILENAME]
    )
    if result.returncode != 0:
        logging.error("Error: error in ansible script")
        logging.info(result.stderr)


