from datetime import datetime

end_time = datetime(2024, 2, 21,11)

sites_to_block = ['facebook.com', 'www.facebook.com', 'youtube.com', 'www.youtube']

hosts_path = "/etc/hosts"

redirect = "127.0.0.1"

def block_sites():
    if datetime.now() < end_time:
        print("Websites have been blocked, time to focus!")
        with open(hosts_path, 'r+') as hostsfile:
            hosts_content = hostsfile.read()
            for site in sites_to_block:
                if site not in hosts_content:
                    hostsfile.write(redirect + " " + site + "\n")
    else:
        print("Websites have been unblocked!")
        with open(hosts_path, 'r+') as hostsfile:
            lines = hostsfile.readlines()
            hostsfile.seek(0)
            for line in lines:
                if not any(site in line for site in sites_to_block):
                    hostsfile.write(line)
            hostsfile.truncate()

if __name__ == "__main__":
    block_sites()