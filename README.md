
# FID-Preprocessing of Data

## Description

This is the repository for the master thesis 'Automated Identification of Information Disorder in Social Media from Multimodal Data'. With the help of [NetIdee](www.netidee.at) successfully implemented. 

This is the first repository of the master thesis. Its main purpose is the preprocessing part. The other repositories are:
 
 - [Model Calculations and Experiments](https://github.com/akirchknopf/FID-Model-Handling)
 - [Model Evaluation](https://github.com/akirchknopf/FID-Evaluation) 


## License


* This project is licensed under the GNU General Public License version 3 (GPL v3) - see the [GPL.txt](gpl.txt) file for details.
* This document is distributed under CC-BY-Sharelike-3.0 AT

## Installation Instructions

### Virtual Environment
```
python3 -m venv ./venv

source venv/bin/activate

pip install --upgrade pip

pip3 install jupyter

pip3 install pandas

pip3 install Pillow==2.2.2

pip3 install tqdm


```
## Directory Structure
Please prepare following directory structure for all three repositories:

- FID-Dataset
- FID-Preprocessing
- FID-Model-Handling
- FID-Evaluation

Within the FID-Preprocessing clone this repository, so it should look like:
```
.
├── preprocessing_and_statistics_dataset_with_comments-meta_test.ipynb
├── README.md
├── utils
│   ├── dataframeUtils.py
│   ├── fileAndDirUtils.py
│   ├── multiprocessingUtils.py
│   ├── otherUtils.py
├── venv
```


# Before running

## Download Fakeddit Dataset

Please download the whole dataset from the dataset authors repository, which you can find here: [Link to dataset authors](https://github.com/entitize/Fakeddit). Please download also the gdrive images from the section Installation.

## Prepare directory structure



Please prepare following directory structure within FID-Dataset directory:
```
.
├── 001_fakeddit_from_website 
│   ├── 000_archive # Copy of the original data
│   ├── 001_website_data # all original *.tsv files
│   ├── 002_download_tool_repo # copy of the image downloader if necessary
│   └── 003_gdrive_images # all images prepared by the dataset authors
```

## Running the preprocessing

When you start running the preprocessing notebook please change the pathes accordingly to your folder structure. Afterwards all the necessary data and following dorectories should be generated. When you try to run this notebook the first time, it will take around 3-4 hours, depending on your hardware, to process all the data.
