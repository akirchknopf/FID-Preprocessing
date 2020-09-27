'''
imports
'''
from numpy import asarray
import os
from PIL import Image

def addFullPath(fileName, pathToImages):
    fileName = (str(fileName) + '.jpg')
    return os.path.join(pathToImages, fileName)


def calcMeanAndStdOfImage(path):
    if (os.path.isfile(path)):
        try:
            im = Image.open(path).convert("RGB") # For the case its a CMYK
            pixels = asarray(im)
            pixels = pixels.astype('float32')
            means = pixels.mean(axis=(0,1), dtype='float32')
            stds = pixels.std(axis=(0,1), dtype='float32')
            return means, stds
        except OSError:
            print(OSError)
            return [], []
    else:
        return [], [] 

def checkIfDirExistsAndCreate(path):
    if not os.path.exists(path):
        print(f'Dir not found, creating {path} instead')
        os.makedirs(path)
    
def checkIfImageIsAvaliable(image_id, pathToImageFolder):
    path = os.path.join(pathToImageFolder , str(image_id) + ".jpg")
    if (os.path.isfile(path)):
        try:
            im = Image.open(path)
            return True
        except OSError:
            return False
    else:
        return False
    
def checkIfImagesAreAvailableAndValid(dataFrameToCheck, pathToImageDir):
    meansDataset = []
    temp_drop_indices = []
    temp_keep_indices = []
    count_true = 0
    count_false = 0
    # Check if all images are available, if not prepare for dropping, also for entries without images!
    dirList = listdir_fullpath(pathToImageDir)
    print("Starting check directory, need to check: " + str(len(dirList)) + " files... but have " + str(dataFrameToCheck.shape[0]) + " entries in dataframe")
    
    for index, row in dataFrameToCheck.iterrows():
        if (row["hasImage"]):
            image_id = row['id']
            state = checkIfImageIsAvaliable(image_id, pathToImageDir)
#             print(val)
            if state:
                count_true += 1
                temp_keep_indices.append(index)
            else:
                count_false += 1            
                temp_drop_indices.append(index);
            if index % 100 == 1:
                print(f'Processed {index} lines.', end='\r')
#                 print(index)
        else:
            temp_drop_indices.append(index);
    print(str(count_true) + " images found")
    print(str(count_false) + " images not found")
    print("Check total images within data set, which are not available = " + str((count_true + count_false) - len(dirList)))
    return (temp_keep_indices, temp_drop_indices);
    
def copyImageFromAToB(pathToImageOriginal, pathToImageTargetDir):
    if (os.path.isfile(pathToImageOriginal)):
                    if not (os.path.isfile(pathToImageTargetDir)):
                        try:
                            shutil.copyfile(pathToImageOriginal, pathToImageTargetDir)
                        except:
                            print('Error in copying file: ' + pathToImage)
    
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]  

def resizeImage(pathToImage, pathToDestImage, IMG_WIDTH, IMG_HEIGHT):
    size = (IMG_WIDTH, IMG_HEIGHT)
    img = Image.open(pathToImage)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img = img.resize(size, Image.ANTIALIAS)
    img.save(pathToDestImage)
    
def writeMeansToFile(data, pathToFile):
    with open (pathToFile, 'w') as file:
        print('Writing  file')
        file.write(str(data))