'''
Imports
'''

import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import  Pool
import numpy as np
from tqdm import tqdm

from .otherUtils import convertRowToDictionary
from .fileAndDirUtils import copyImageFromAToB, calcMeanAndStdOfImage, resizeImage

def calculateMeansAndStdMultiprocessing(df, pathToImages):
    imagePathList = generateFileListForMeanAndStds(df, pathToImages)
    print(len(imagePathList))
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(tqdm(executor.map(workerMeanStds, (imagePathList)), total=len(imagePathList)))
    
    sorted(meansStds, key=lambda x: x[0])
    means = [x[1] for x in meansStds]
    stds = [x[2] for x in meansStds]
    
    return(means, stds)


def generateFileList(dataframe, path_to_all_images, pathToDest, IMG_SIZES):
    imageList = []
    for tupleRaw in dataframe.itertuples(index=True, name=None):
        row = convertRowToDictionary(tupleRaw, dataframe.columns)
        index = tupleRaw[0]
        fileName = row['fileName']
        label = row['label']
        pathToSource = os.path.join(path_to_all_images, fileName)
        pathToDestination = os.path.join(pathToDest, fileName)
        imageList.append((pathToSource, pathToDestination, IMG_SIZES[0], IMG_SIZES[1]))
        
        if index % 100 == 1:
            print(f'Processed {index} lines.', end='\r')
    return imageList

def generateFileListForCopy(dataframe, sourceDir, destDir):
    imageTupleList = []
    for tupleRaw in dataframe.itertuples(index=True, name=None):
        row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)
        index = tupleRaw[0]
        imageID = row_dict['id']
        imageName = str(imageID) + '.jpg'    
        pathToImageOriginal = os.path.join(sourceDir, imageName)
        pathToImageTargetDir = os.path.join(destDir, imageName)
        imageTupleList.append((pathToImageOriginal, pathToImageTargetDir))
    return imageTupleList

def generateFileListForMeanAndStds(df, pathToImageDir):
    imagePathList = []
    for tupleRaw in df.itertuples(index=True, name=None):
        row = convertRowToDictionary(tupleRaw, df.columns, True)
        index = row['index']
        image_id = row['id']
        imageName = str(image_id) + '.jpg'
        imagePathList.append((tupleRaw[0], os.path.join(pathToImageDir, imageName)))

        if tupleRaw[0] % 10000 == 1:
            print(f'Processed {tupleRaw[0]} lines.', end='\r')
    return imagePathList


def parallelize_dataframe(df, func, n_cores=16):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df

def parallelize_dataframe_comments(df, func, n_cores=16):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


def resizeImagesMultiprocessing(imageListTuple):
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(tqdm(executor.map(workerResizeImage, imageListTuple), total=len(imageListTuple)))

        
def resizeNormalizeImagesMultiprocessing(imageListTuple):
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(tqdm(executor.map(workerResizeImageAndNormalize, imageListTuple), total=len(imageListTuple)))        

def workerCopyAToB(data):
    if not (os.path.exists(data[1])):
        copyImageFromAToB(data[0], data[1])


meansStds = []
def workerMeanStds(d):
    i = d[0]
    m, s = calcMeanAndStdOfImage(d[1])
    meansStds.append((i,m,s))
    
def workerResizeImage(data):
    if not (os.path.exists(data[1])):
#         print(sourceDirFilePath)
        resizeImage(data[0], data[1], data[2], data[3]) # ACHTUNG IN CONFIG AUSLAGERN
  
    