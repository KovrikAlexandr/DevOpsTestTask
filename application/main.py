import sys
import logging

from server import clear_inventory_file
from server import add_group_to_inventory, create_pg_config_file, run_ansible
from server import get_server_loading

STANDARD_SSH_PORT = 22
STANDARD_USERNAME = "root"
STANDARD_KEY_FILENAME = "~/.ssh/keys/vm_key"

if __name__ == "__main__":
    # Set logging
    logging.basicConfig(
        level=logging.INFO,
        format = "%(asctime)s - %(levelname)s - %(message)s",
        handlers = [
            logging.StreamHandler()
        ]
    )

    # Get arguments
    hostnames = sys.argv[1].split(",")
    # if len(hostnames) > 2:
    #     logging.error("Error: expected only two hostnames")
    #     exit(1)

    # Get server loadings
    loadings = []
    for hostname in hostnames:
        loading = get_server_loading(
            hostname = hostname,
            port=STANDARD_SSH_PORT,
            username=STANDARD_USERNAME,
            key_filename=STANDARD_KEY_FILENAME)
        loadings.append(loading)

    # Get servers groups
    hostnames_sorted = [h for _, h in sorted(zip(loadings, hostnames))]
    base_server = hostnames_sorted[1]
    connected_servers = [hostnames_sorted[0]]
    logging.info(f"Base server: {base_server}")
    logging.info(f"Connected servers: {connected_servers}")

    # Set ansible inventory
    clear_inventory_file()
    add_group_to_inventory("base", [base_server])
    add_group_to_inventory("connected", connected_servers)

    # Locally create PG config file
    create_pg_config_file(connected_servers)

    # Run ansible script
    run_ansible()















