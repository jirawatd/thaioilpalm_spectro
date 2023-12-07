import time
from configparser import ConfigParser
from specdal import Collection, Spectrum
from matplotlib import pyplot as plt
import numpy as np
import csv
import os
import re
import argparse
import pandas as pd
from Common.helper import format_two_point_time
import nippy
import glob
import shutil
import joblib


### Run ASD Processing ###

def process_asd_files(config_file):
    start = time.time()
    print("start processing asd files")

    # Read config.conf file
    config_object = ConfigParser()
    config_object.read(config_file)

    # Get the input
    asd_path = config_object["INPUT"]["asd_path"]
    sample_mapping_file = config_object["INPUT"]["sample_mapping_file"]
    no_of_asd_per_sample = int(config_object["INPUT"]["no_of_asd_per_sample"])

    print("asd_path is {}".format(asd_path))
    print("sample_mapping_file is {}".format(sample_mapping_file))
    print("no_of_asd_per_sample is {}".format(no_of_asd_per_sample))

    # Read sample_mapping_file
    graph_min = float(config_object["PROCESSING"]["graph_min"])
    graph_max = float(config_object["PROCESSING"]["graph_max"])
    output_csv = bool(config_object["OUTPUT"]["output_csv"] == "true")
    output_graph = bool(config_object["OUTPUT"]["output_graph"] == "true")

    output_path = config_object["OUTPUT"]["output_path"]
    output_path_csv = os.path.join(output_path, 'csv')
    output_path_graph = os.path.join(output_path, 'graph')

    if not os.path.exists(output_path_csv):
        os.makedirs(output_path_csv)
    if not os.path.exists(output_path_graph):
        os.makedirs(output_path_graph)

    with open(sample_mapping_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'HEADER: {", ".join(row)}')
                line_count += 1
            else:
                plot_sample_name = re.sub('[\\\\/:*?"<>|,]', '_', (row[0] + "-" + row[1] + "-L" + row[2] + "-" + row[3]))
                print(f'Plot-Sample: {plot_sample_name}')

                c = Collection(name=plot_sample_name)
                for x in range(4, no_of_asd_per_sample + 4):
                    asd_file = row[x] + ".asd"
                    spectrum = Spectrum(filepath=os.path.join(asd_path, asd_file))
                    c.append(spectrum)

                c.data.head()
                if output_graph:
                    c.plot(title=plot_sample_name,legend=False, ylim=(graph_min, graph_max),ylabel='reflectance',figsize=(12,8))
                    # plt.show()
                    plt.axvspan(440, 510, facecolor='b', alpha=0.1)
                    plt.axvspan(520, 590, facecolor='g', alpha=0.1)
                    plt.axvspan(630, 685, facecolor='r', alpha=0.1)
                    plt.axvspan(690, 730, facecolor='darkred', alpha=0.2)
                    plt.axvspan(760, 850, facecolor='gray', alpha=0.1)
                    plt.savefig(os.path.join(output_path_graph, plot_sample_name)+"_all.png")
                    plt.clf()
                    data_max = c.max()
                    data_mean = c.mean()
                    data_min = c.min()
                    data_max.plot(title=plot_sample_name,legend=True, ylim=(graph_min, graph_max),ylabel='reflectance',color='r',label='Max',figsize=(12,8))
                    data_mean.plot(title=plot_sample_name,legend=True, ylim=(graph_min, graph_max),ylabel='reflectance',color='g',label='Avg',figsize=(12,8))
                    data_min.plot(title=plot_sample_name,legend=True, ylim=(graph_min, graph_max),ylabel='reflectance',color='b',label='Min',figsize=(12,8))
                    plt.axvspan(440, 510, facecolor='b', alpha=0.1)
                    plt.axvspan(520, 590, facecolor='g', alpha=0.1)
                    plt.axvspan(630, 685, facecolor='r', alpha=0.1)
                    plt.axvspan(690, 730, facecolor='darkred', alpha=0.2)
                    plt.axvspan(760, 850, facecolor='gray', alpha=0.1)
                    plt.savefig(os.path.join(output_path_graph, plot_sample_name)+"_min_max_avg.png")


                if output_csv:
                    output_file_name = os.path.join(output_path_csv, plot_sample_name)+".csv"
                    print('export_to_csv: {}'.format(output_file_name))
                    if os.path.exists(output_file_name):
                        os.remove(output_file_name)
                    
                    data_t = c.data.transpose()
                    data_t.insert(0, 'SAMPLE_CODE', plot_sample_name)
                    data_t.index.name = 'ASD_FILE'
                    data_t.to_csv(output_file_name, sep=',', encoding='utf-8')


                line_count += 1

        print(f'Processed {line_count} lines.')
        print('Overall time elapsed: {} seconds'.format(format_two_point_time(start, time.time())))


### Run ASD Processing ###

def preprocess_nir_data(config_file):
    
    # Read config.conf file
    config_object = ConfigParser()
    config_object.read(config_file)
    
    # Get the input
    output_path = config_object["OUTPUT"]["output_path"]
    tmp_path = config_object["TEMP"]["tmp_path"]
    print("output_path is {}".format(output_path))
    
    # Load configuration
    pipelines = nippy.read_configuration('method_pretreatment.ini')

    # Load data
    files = glob.glob('%s/csv/*.csv'%output_path)
    
    for file in files:
        filename = os.path.basename(file)
        #print(filename)
        # Read data and perform preprocessing
        data = np.genfromtxt('%s/csv/%s' % (output_path, filename), delimiter=',')
        data = np.delete(data, np.s_[0:2], axis=1)

        wavelength = data[0, :]
        spectra = data[1:, :].T

        # Dataset through all pipelines
        datasets = nippy.nippy(wavelength, spectra, pipelines)

        # Export the preprocessed data
        nippy.export_pipelines_to_csv('%s/%s' % (tmp_path,filename),
                                      datasets, pipelines, mkdir=True)

        # Read file, transpose, and add file name in SAMPLE_NO column
        df = pd.read_csv('%s//%s//1.csv'% (tmp_path,filename))
        df = df.T
        df.columns = df.iloc[0]
        df.insert(750, 'SAMPLE_NO', filename)
        df = df.iloc[1:]
        df.to_csv('%s//%s//2.csv' % (tmp_path,filename))

        # Move the file
        shutil.move(
            '%s//%s//2.csv' % (tmp_path,filename),
            "%s//emsc_%s" % (output_path,filename))
        
        # Delete all files in tmp
        dir = tmp_path
        for files in os.listdir(dir):
            path = os.path.join(dir, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)

### Run Edit Header ###

def replace_first_row(config_file):
    
    # Read config.conf file
    config_object = ConfigParser()
    config_object.read(config_file)
    
    # Get the input
    head_template = config_object["INPUT"]["head_template"]
    output_path = config_object["OUTPUT"]["output_path"]
    
    
    # Read the content of the source CSV file
    with open(head_template, 'r') as source_file:
        source_reader = csv.reader(source_file)
        source_data = list(source_reader)

    # Iterate over all files in the folder
    for filename in os.listdir(output_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(output_path, filename)

            # Read the content of the destination CSV file
            with open(file_path, 'r') as destination_file:
                destination_reader = csv.reader(destination_file)
                destination_data = list(destination_reader)

            # Replace the first row of the destination CSV file
            destination_data[0] = source_data[0]

            # Write back to the destination CSV file
            with open(file_path, 'w', newline='') as destination_file:
                destination_writer = csv.writer(destination_file)
                destination_writer.writerows(destination_data)
                
### Run Average 24 spectra ###
def average_spectra(config_file):
    
    # Read config.conf file
    config_object = ConfigParser()
    config_object.read(config_file)
    
    # Get the input
    output_path = config_object["OUTPUT"]["output_path"]               
    for filename in os.listdir(output_path):
        if filename.endswith('.csv'):
            # Construct the full file paths for df1 and output
            input_csv = os.path.join(output_path, filename)
            df=pd.read_csv(input_csv)
            grouped = df.groupby('SAMPLE_NO')
            averages = grouped.mean().iloc[:, :752]
            averages.to_csv('%s/%s'%(output_path,filename))
            
### Run Remove WL ###

def remove_common_columns_and_save(config_file):
    
    # Read config.conf file
    config_object = ConfigParser()
    config_object.read(config_file)
    
    # Get the input
    output_path = config_object["OUTPUT"]["output_path"]
    wl_remove = config_object["REMOVE"]["wl_remove"]
    
    common_columns = None
    # Load the second CSV file (df2)
    
    for filename in os.listdir(output_path):
        if filename.endswith('.csv'):
            # Construct the full file paths for df1 and output
            input_csv_path_df1 = os.path.join(output_path, filename)
            output_csv_path = os.path.join(output_path, f'remove_{filename}')

            # Load the CSV file
            df1 = pd.read_csv(input_csv_path_df1)
            df2 = pd.read_csv(wl_remove)
            # Identify common columns (using the first CSV file as a reference)
            if common_columns is None:
                common_columns = df1.columns.intersection(df2.columns)

            # Remove common columns from the df1 DataFrame
            df1 = df1.drop(columns=common_columns)

            # Save the modified DataFrame to a new CSV file
            df1.to_csv(output_csv_path, index=False)


def make_predictions_and_print(config_file):
    
    # Read config.conf file
    config_object = ConfigParser()
    config_object.read(config_file)
    
    # Get the input
    model_path = config_object["MODEL"]["model_path"]
    output_path = config_object["OUTPUT"]["output_path"]
    
    csv_file_path = glob.glob('%s//*.csv'%output_path)
            
    for file in csv_file_path:
        filename = os.path.basename(file)
        print (filename)

    # Load the model from the .sav file
    model = joblib.load(model_path)

    # Load new data from a CSV file
    new_data = pd.read_csv('%s/%s'%(output_path,filename))
    # Make predictions on the new data
    predictions = model.predict(new_data)

    # Print or use the predictions as needed
    print(predictions)




# Parse command-line arguments
parser = argparse.ArgumentParser(description='Argument indicating the configuration file')
parser.add_argument("-c", "--config", help="add a configuration file you would like to process the asd data"
                                              " \n ex. py run_asd_processing.py -c spectro_config.conf",
                       action="store", default='spectro_config.conf')
args = parser.parse_args()
config_file = args.config
print('config file: ' + config_file)

# Call the function with the provided configuration file
process_asd_files(config_file)
preprocess_nir_data(config_file)
replace_first_row(config_file)
average_spectra(config_file)
remove_common_columns_and_save(config_file)
make_predictions_and_print(config_file)
