import os


def run_gpg_agent(gnupg_home):
    print("#####################################")
    os.system(f"/opt/bin/gpg-agent -v --homedir '{gnupg_home}' --daemon")
    print("#####################################")

