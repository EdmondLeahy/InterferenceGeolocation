import os
import sys
import subprocess
from shutil import copyfile

LOG_LIST = ['BESTPOS', 'SPRINKLERDATA', 'SPRINKLERDATAH', 'VERSION']

def rename_dat(dat_file):
    pass

def run_nconvert(gps_file):
    os.mkdir('OBS')
    os.chdir('OBS')
    nc_call = f'nc --split -c{LOG_LIST} {gps_file}'
    subprocess.run(nc_call)
    os.chdir('..')


def main():

    for folder in os.walk(os.getcwd()):
        os.chdir(folder)
        cwd = os.getcwd()
        dat_list = [os.path.join(cwd, f) for f in os.listdir() if f.endswith('.DAT')]

        for dat in dat_list:
            # rename_dat(dat)
            run_nconvert(dat)


if __name__ == '__main__':
    sys.exit(main())
