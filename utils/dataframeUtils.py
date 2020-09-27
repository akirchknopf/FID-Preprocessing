'''
imports
'''

import os
import pandas as pd



from .otherUtils import addFullPath, chunkify, convertRowToDictionary, isBlank, parseStringAsNpArray, processComment

from .multiprocessingUtils import parallelize_dataframe


def addComments(data):
    dataframe = data[0]
    df_all_comments = data[1]
    try:
        dataframe.insert(loc=dataframe.shape[1], column='comments', value=[list for i in range(dataframe.shape[0])])
        dataframe.insert(loc=dataframe.shape[1], column='up_vote_comments', value=[list for i in range(dataframe.shape[0])])
    except ValueError:
        print('Found columns, ignoring inserting')
    df_comments = pd.merge(dataframe, df_all_comments, left_on='id', right_on='submission_id', how='inner',suffixes=('_left','_right'))
    for row in dataframe.itertuples(index=True, name=None):
        row_dict = convertRowToDictionary(row, dataframe.columns, True)        
        currentCommentsSelector = df_comments['submission_id'] == row_dict['id']

        # Selecting all related comments and cleaning unnamed stuff
        selectedComments = df_comments[currentCommentsSelector]
        selectedComments = selectedComments.loc[:, ~selectedComments.columns.str.contains('^Unnamed')]

        clean_comments = []
        clean_up_vote = []

        if not selectedComments.empty:
            if (len(selectedComments)) is not int(row_dict['num_comments']):
                print(f'Checked comments and num_comments -> mismatch! len of comments found: {len(selectedComments)}, but should be {int(row_dict["num_comments"])} at id {row_dict["id"]}')
                dataframe.at[row[0], 'num_comments'] = len(selectedComments)
        else:
            dataframe.at[row[0], 'num_comments'] = 0

            # Iterating over all found comments, cleaning them 
            for row_comment in selectedComments.itertuples(index=True, name=None):
                row_dict_comments = convertRowToDictionary(row_comment, selectedComments.columns, True)
                clean_comments.append(processComment(row_dict_comments['body']))
                clean_up_vote.append(row_dict_comments['ups'])

        # Inserting at correct position
        dataframe.at[row[0], 'comments'] = clean_comments
        dataframe.at[row[0], 'up_vote_comments'] = clean_up_vote

    return dataframe

def checkIfTrainCSVIsValid(path_to_cleaned_csv_file, df_taken_train):
    try:
        df_to_check = pd.read_csv(path_to_cleaned_csv_file, header=0, sep='\t')
        
        if (len(df_to_check))  == len(df_taken_train):
            print('Len of csv and calculated train set is equal')
        # Len is equal, but is mean also set?
        if 'means' in df_to_check and 'stds' and 'author_enc' in df_to_check:
            print('Columns Mean and Stds and author_enc exists, checking if all values are present:')
            # Columns exists, now check if there are all values set
            for tupleRaw in df_to_check.itertuples(index=True, name=None):
                row_dict = convertRowToDictionary(tupleRaw, df_to_check.columns, True)
                means = parseStringAsNpArray(row_dict['means']);
                stds = parseStringAsNpArray(row_dict['stds']) 
                
                if len(means) == 0  or len(stds) == 0 or not isinstance(row_dict['author_enc'], int):                    
                     return False

            return True
            print('CSV is valid, skipping recalculating of means and stds')
        else:
            print('Column Mean and/or Stds and/or author_enc does not exist recalculating')
            return False

    except FileNotFoundError:
        return False

def cleanDataFrameFromNansandnans(df):
    df['title'] = df['title'].astype(str)
    df['clean_title'] = df['clean_title'].astype(str)
#     df['upvote_ratio'] = df['upvote_ratio'].astype(str)
    df = df[~df['title'].str.contains('NaN')]    
    df = df[~df['clean_title'].str.contains('NaN')]
#     df = df[~df['upvote_ratio'].str.contains('NaN')]
    df = df[~df['title'].str.contains('nan')]
    df = df[~df['clean_title'].str.contains('nan')]
#     df = df[~df['upvote_ratio'].str.contains('nan')]
    return df

def countFakeNoFake(dataframe):
    count_fake = 0
    count_not_fake = 0
    for tupleRaw in dataframe.itertuples():
        row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)
        currentLabel = row_dict['2_way_label']# Get 2-way label (fake, no fake)
        if (currentLabel) == 1:
            count_fake += 1
        else:
            count_not_fake +=1

    print("We have " + str(count_not_fake) + " not fakes!")
    print("We have " + str(count_fake) + " fakes!")
    return(count_fake, count_not_fake)

def createIDLabelFile(dataframe, pathToDirectory, fileName, isTrain=False):

    image_label_list = []
    for tupleRaw in dataframe.itertuples(index=True, name=None):
        row = convertRowToDictionary(tupleRaw, dataframe.columns, True)
#         print(row)
        if isTrain:
            imageID = row['id']
            label = row['2_way_label']
#             print('label')
        else:
            imageID = row['id']
            label = row['2_way_label']
#             print(tupleRaw)
#             print(label)
#             break
        
        imageName = str(imageID) + ".jpg"
#         print(imageName)
        image_label_list.append([imageName, label])
#         print(image_label_list)

    df = pd.DataFrame(image_label_list, columns = ['imageName', 'label'])
    df = df.show_pandas_n_last_columns(2)
    df.columns = ['fileName', 'label']
    
    if not os.path.exists(pathToDirectory):
        print("no outdir found, creating it instead!")
        os.makedirs(pathToDirectory)
    
    path_to_cleaned_csv = os.path.join(pathToDirectory, fileName)
    df.to_csv(path_to_cleaned_csv, sep='\t', encoding='utf-8')
    return df

def createIDTitleCommentsTextLabelFile(dataframe, pathToDirectory, fileName, isTrain = False): 
    path_to_cleaned_csv = os.path.join(pathToDirectory, fileName)
    if isTrain:
        df = dataframe[['clean_title', 'id', 'comments', '2_way_label', 'means', 'stds']]
        for tupleRaw in dataframe.itertuples(index=True, name=None):
            row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)
            df.at[tupleRaw[0], 'id'] = addFullPath(row_dict['id'], pathToDirectory)
    else:
        for tupleRaw in dataframe.itertuples(index=True, name=None):
            row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)
            df = dataframe[['clean_title', 'id', 'comments', '2_way_label']]
            df.at[tupleRaw[0], 'id'] = addFullPath(row_dict['id'], pathToDirectory)

    df.to_csv(path_to_cleaned_csv, sep='\t', encoding='utf-8', index=False)
    return df

def createMetaDataLabelFile(dataframe, pathToDirectory, fileName):
    path_to_cleaned_csv = os.path.join(pathToDirectory, fileName)
    df = dataframe[['author_enc','id', 'score', 'hasNanScore', 'upvote_ratio', 'hasNanUpvote', 'num_comments', '2_way_label']]
#     for tupleRaw in dataframe.itertuples(index=True, name=None):
#         row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)
#         df.at[tupleRaw[0], 'id'] = addFullPath(row_dict['id'], pathToDirectory)
    df.to_csv(path_to_cleaned_csv, sep='\t', encoding='utf-8', index=False)
    return df

def createIDTitleCommentsTextMetaDataLabelFile(dataframe, pathToDirectory, pathToImages, fileName, isTrain = False): 
    path_to_cleaned_csv = os.path.join(pathToDirectory, fileName)
    dataframe = dataframe.reindex(columns=['author_enc', 'clean_title', 'id', 'imagePath', 'comments', 'num_comments', 'up_vote_comments', 'score', 'hasNanScore', 'upvote_ratio', 'hasNanUpvote', '2_way_label'])
    dataframe['imagePath'] = dataframe['imagePath'].astype(str)
    if isTrain:
#         df = dataframe[['author_enc', 'clean_title', 'id', 'imagePath', 'score', 'hasNanScore', 'upvote_ratio', 'hasNanUpvote', 'comments', 'num_comments', 'up_vote_comments', 'means', 'stds', '2_way_label']]
        for tupleRaw in dataframe.itertuples(index=True, name=None):
            row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)
            path = addFullPath(row_dict['id'], pathToImages)
            dataframe.at[tupleRaw[0], "imagePath"] = path
    else:
        for tupleRaw in dataframe.itertuples(index=True, name=None):
            row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)
#             df = dataframe[['author_enc', 'clean_title', 'id', 'imagePath', 'comments', 'num_comments', 'up_vote_comments', 'score', 'hasNanScore', 'upvote_ratio', 'hasNanUpvote', '2_way_label']]
            path = addFullPath(row_dict['id'], pathToImages)
            dataframe.at[tupleRaw[0], "imagePath"] = path
    dataframe.to_csv(path_to_cleaned_csv, sep='\t', encoding='utf-8', index=False)
    return dataframe

def createIDTitleFile(dataframe, pathToDirectory, fileName):
    text_label_list = []
    for tupleRaw in dataframe.itertuples(index=True, name=None):
    #     print(tupleRaw)
        title = (tupleRaw[1])
        if isBlank (str(title)):
            print("detected empty string")
            break
        label = (tupleRaw[12])
        text_label_list.append([title, label])

    df = pd.DataFrame(text_label_list, columns = [title, label])
    df = df.show_pandas_n_last_columns(2)
    df.columns = ['title', 'label']

    if not os.path.exists(pathToDirectory):
        print("no outdir found, creating it instead!")
        os.makedirs(pathToDirectory)

    path_to_cleaned_csv = os.path.join(pathToDirectory, fileName)
    df.to_csv(path_to_cleaned_csv, sep='\t', encoding='utf-8')

def createIDTitleTextLabelFile(dataframe, pathToDirectory, fileName):
    id_text_image_label_list = []
    for tupleRaw in dataframe.itertuples(index=True, name=None):
#         print(tupleRaw)
        rowID = (tupleRaw[6])
        imageID = (tupleRaw[6])
        imageName = str(imageID) + ".jpg"
        title = (tupleRaw[12])
        if isBlank (str(title)):
            print("detected empty string")
            break
        label = (tupleRaw[14])
        
        if (len([rowID, imageName, title, label]) is not 4):
            print([rowID, imageID, title, label])
            print('error, length mismatch')
            break
        
        id_text_image_label_list.append([rowID, imageName, title, label])

    df = pd.DataFrame(id_text_image_label_list, columns = ['rowID', 'imageName', 'title', 'label'])
    df = df.show_pandas_n_last_columns(4)
    df.columns = ['rowID','image', 'title', 'label']

    if not os.path.exists(pathToDirectory):
        print("no outdir found, creating it instead!")
        os.makedirs(pathToDirectory)

    path_to_cleaned_csv = os.path.join(pathToDirectory, fileName)
    df.to_csv(path_to_cleaned_csv, sep='\t', encoding='utf-8')
    
dict = {}    
def encodeAuthors(df, all_authors):
    try:
        df.insert(loc=df.columns.get_loc('author') + 1, column='author_enc', value=df['author'])
    except Exception:
        print('already added columns author_enc')

    df['author'] = df['author'].replace('nan' ,'no_author')
    df["author"].fillna("no_author", inplace = True)

#     dict = {}


    for i, a in enumerate(all_authors):
        dict[a] = i

    count_chunks = 8
    chunks = chunkify(df, count_chunks)

    newChunks = None

    for chunk in chunks:
    #     start = time.time()
        dft = chunk
        newChunk = parallelize_dataframe(dft, replace, 16)
        newChunks = pd.concat([newChunks, newChunk], ignore_index=True, sort=False)
    #     end = time.time()
    #     print(f'It took {(end - start) / 60} minutes to process this chunk' )
    df = newChunks
    if (len(df) != len(newChunks)):
        raise ValueError('Lenmismatch, aborting')
    return df    


def replace(df):
    df.author_enc = df.author.replace(dict)
    return df  

def replaceNanInScoreAndUpvote(dataframe):
    dataframe['score'].fillna(-1, inplace=True)
    dataframe['upvote_ratio'].fillna(-1, inplace=True)
    try:
        dataframe.insert(loc=dataframe.columns.get_loc('upvote_ratio') + 1, column='hasNanUpvote', value=0)
        dataframe.insert(loc=dataframe.columns.get_loc('score') + 1, column='hasNanScore', value=0)
    except Exception:
        print('already added columns hasNan')
    
    for tupleRaw in dataframe.itertuples(index=True, name=None):
        row_dict = convertRowToDictionary(tupleRaw, dataframe.columns, True)

        if  row_dict['score'] == -1:
            dataframe.at[tupleRaw[0], 'hasNanScore'] = 1
        if  row_dict['upvote_ratio'] == -1:
            dataframe.at[tupleRaw[0], 'hasNanUpvote'] = 1
    return dataframe

def show_pandas_n_front_columns(self, n):
    return self.iloc[:, :n]


def show_pandas_n_last_columns(self, n):
    return self.iloc[:, -n:]

def writeAuthorListToCSV(all_authors, pathToFile):
    df = pd.DataFrame(all_authors, columns=["trainAuthorList"])
    df.to_csv(pathToFile, sep=';', encoding='utf-8', index=False)

def writeOutCleanedDataFrameToCSV(dataframe, pathToDirectory, fileName):
    print("writing cleaned dataframe -> ")
    
    if not os.path.exists(pathToDirectory):
        print("no outdir found, creating it instead!")
        os.makedirs(pathToDirectory)
   
    path_to_cleaned_csv = os.path.join(pathToDirectory, fileName)
    dataframe.to_csv(path_to_cleaned_csv, sep='\t', encoding='utf-8')
    print("finished writing cleaned dataframe!")
    return dataframe

