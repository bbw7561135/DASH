from dash.training_parameters import create_training_params_file
from dash.create_training_set import create_training_set_files
from dash.create_template_set import create_template_set_file
from dash.deep_learning_multilayer import train_model
import zipfile
import os
import shutil
import time

if __name__ == '__main__':
    dataDirName = 'data_files_AgnosticZ_noHost/'
    dataFilenames = []
    if not os.path.exists(dataDirName):
        os.makedirs(dataDirName)

    # CREATE PARAMETERS PICKLE FILE
    t1 = time.time()
    trainingParamsFilename = 'data_files_AgnosticZ_noHost/training_params.pickle'  # create_training_params_file(dataDirName)
    dataFilenames.append(trainingParamsFilename)
    t2 = time.time()
    print("time spent: {0:.2f}".format(t2 - t1))

    # CREATE TRAINING SET FILES
    trainingSetFilename = 'data_files_AgnosticZ_noHost/training_set.zip'  # create_training_set_files(dataDirName, minZ=0, maxZ=0.8, redshiftPrecision=0.02, trainWithHost=False, classifyHost=False)
    dataFilenames.append(trainingSetFilename)
    t3 = time.time()
    print("time spent: {0:.2f}".format(t3 - t2))

    # CREATE TEMPLATE SET FILE
    templateSetFilename = 'data_files_AgnosticZ_noHost/templates.npz'  # create_template_set_file(dataDirName)
    dataFilenames.append(templateSetFilename)
    t4 = time.time()
    print("time spent: {0:.2f}".format(t4 - t3))

    # TRAIN TENSORFLOW MODEL
    modelFilenames = train_model(dataDirName)
    dataFilenames.extend(modelFilenames)
    t5 = time.time()
    print("time spent: {0:.2f}".format(t5 - t4))

    # MAKE INFO TEXT FILE ABOUT MODEL
    modelInfoFilename = dataDirName + "model_info.txt"
    with open(modelInfoFilename, "w") as f:
        f.write("Date Time: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        f.write("Directory: %s\n" % dataDirName)
        f.write("Add Host: True\n")
        f.write("SN-Host fractions: [0.01, 0.02, 0.05, 0.07, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]\n")
        f.write("Classify Host: False\n")
        f.write("Redshift: Agnostic\n")
        f.write("Redshift Range: 0 to 0.8\n")
        f.write("Redshift Precision: 0.02\n")
        f.write("Training Amount: 50 x 200000\n")
        dataFilenames.append(modelInfoFilename)

    # SAVE ALL FILES TO ZIP FILE
    dataFilesZip = 'data_files_agnosticZ_noHost_v01.zip'
    with zipfile.ZipFile(dataFilesZip, 'w') as myzip:
        for f in dataFilenames:
            myzip.write(f)

    modelZip = 'model_agnosticZ_noHost_v01.zip'
    with zipfile.ZipFile(modelZip, 'w') as myzip:
        for f in [dataFilenames[0]] + dataFilenames[2:]:
            myzip.write(f)

    # Delete data_files folder since they are now in the zip files
    # for filename in filenames:
    #     os.remove(filename)