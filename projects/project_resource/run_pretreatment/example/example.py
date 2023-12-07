import nippy
import numpy as np


if __name__ == '__main__':
    # 1. Load configuration
    pipelines = nippy.read_configuration('C:\\Users\\jirawatd\\Code_Project\\thaioilpalm_spectro\\example.py')

    # 2. Load data
    data = np.genfromtxt('C:\\Users\\jirawatd\\Code_Project\\thaioilpalm_spectro\\example.py', delimiter=',')
    wavelength = data[0, :]
    spectra = data[1:, :].T  # Rows = wavelength, Columns = samples

    # 3. Dataset through all pipelines
    datasets = nippy.nippy(wavelength, spectra, pipelines)

    # 4. Export the preprocessed data (showcasing three variants)
    nippy.export_pipelines_to_csv('C:\\Users\\jirawatd\\Code_Project\\thaioilpalm_spectro\\example\\output', datasets, pipelines, mkdir=True)

