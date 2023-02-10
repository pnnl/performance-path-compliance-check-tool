from pathlib import Path
import os
import multiprocessing as mp
import subprocess
EPLUS_DIR = "C:\\EnergyPlusV22-2-0\\"


def run(eplus_wea:str, eplus_file: str, output_prefix:str):
	path = Path(eplus_file)
	parent_dir = path.parent.absolute()
	os.chdir(parent_dir)

	subprocess.run([EPLUS_DIR+"energyplus", "-w", eplus_wea, "-r", "-p", output_prefix, "-s", "C", eplus_file], shell=True)


def run_in_parallel(models:list, wea_dir: str):
	process = [mp.Process(target=run, args=(wea_dir, x)) for x in models]
	procs = []
	for p in process:
		procs.append(p)
		p.start()

	for proc in procs:
		proc.join()
