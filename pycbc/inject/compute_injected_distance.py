import argparse
import random
import numpy as np
import pycbc.version as ver
from pycbc.io.hdf import HFile
# from lal import cached_detector_by_name
# from pycbc.detector import Detector

parser = argparse.ArgumentParser()
parser.add_argument("--verbose")
parser.add_argument("--input-file", metavar="INFILE", required=True,
                    help="path of input hdf5 file")
parser.add_argument("-v", "--version", action="version",
                    version=ver.git_verbose_msg)
parser.add_argument("--d-distr", default="gaussian",
                     choices=["gaussian", "lognormal"],
                     help="The distribution from which to draw the random "
                          "jittered ditance")
parser.add_argument("--phase-error", type=float, default=0,
                     help="Phase calibration uncertainty (degrees)")
parser.add_argument("--amplitude-error", type=float, default=0,
                     help="Amplitude calibration uncertainty (percent)")
parser.add_argument("--output-file", metavar="OUTFILE", required=True,
                    help="path of output hdf5 file")
args = parser.parse_args()

cached_detector = cached_detector_by_name
site_location_list = [('h','H1'),('l','L1'),('v','V1')]

siminsp_fname = args.input_file
siminsp_doc=HFile(siminsp_fname,'r')
if args.phase_error != 0 or args.amplitude_error != 0:
    with HFile(args.output_file,'w') as out: 
        for at in siminsp_doc.attrs:
           out.attrs[at]= at
        for sim in siminsp_doc.keys():
            print(sim)
            if sim != 'distance':
                out.create_dataset(sim,data=siminsp_doc[sim][:]) 
            else:
                mu = siminsp_doc['distance'] * (1 + 0.5 * np.deg2rad(args.phase_error)**2)
                sigma = (args.amplitude_error / 100.) * siminsp_doc['distance'][:]
                if args.d_distr == "gaussian":
                    new_dist_gauss=random.gauss(mu, sigma)
                    out.create_dataset('distance', data=new_dist_gauss)
                elif args.d_distr == "lognormal":
                    new_dist_log=np.log(random.lognormvariate(mu, sigma))
                    out.create_dataset('distance', data=new_dist_log)
                    with siminsp_doc as f:
                        for site, ifo in site_location_list:
                            out.attrs['eff_dist_'+site] = detector.Detector(ifo).effective_distance(f['distance'][:],f['ra'][:],f['dec'][:],np.ones(len(f['distance'][:]))*f.attrs['polarization'],f['tc'][:],f['inclination'][:])
                else:
                    raise ValueError("Can provide only 'gaussian' or 'lognormal'")            
else:
    shutil.copyfile(siminsp_doc, args.output_file)
siminsp_doc.close()                                     

