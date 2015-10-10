from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session 
from werkzeug import secure_filename
import os
#import pyodbc
import pandas as pd
import pandas.io.sql as sql
import json
from sklearn.metrics import pairwise_distances
import numpy as np
from sklearn.manifold import TSNE
import itertools
from sklearn.cluster import DBSCAN

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from StringIO import StringIO
import cStringIO
from PIL import Image
import cPickle as pickle

class MyServer(Flask):
    def __init__(self, *args, **kwargs):
            super(MyServer, self).__init__(*args, **kwargs)

            #instanciate your variables here
            self.df = []

            
app = MyServer(__name__)


@app.route("/")
def index():
    #global global_df
    #global_df = pd.DataFrame()
    print "Rendering index.html"
    return render_template("index.html")

    
from os import listdir, rename
from os.path import isfile, join
import skimage.io as io

@app.route('/get_images', methods=['POST'])
def get_images():
    
    print 'in get_images'
    try:
        print request
        print 'path'
        path = request.json['img_path']
        print 'exageration'
        exageration = int(request.json['exageration'])
        print 'perplexity'
        perplexity = int(request.json['perplexity'])
        print 'learning rate'
        learning_rate = int(request.json['learning_rate'])
        print 'metric'
        metric = request.json['metric']

        bucket = path.split('/')[0]
        folder = '/'.join(path.split('/')[1:])
        new_data_folder = 'tsnetooldata/' + folder

        

        con_s3 = S3Connection()
        tsnetooldata_bucket = con_s3.get_bucket('tsnetooldata')

        selectedBucket = con_s3.get_bucket(bucket)
        filesInBucket = selectedBucket.list(folder)

        if tsnetooldata_bucket.get_key(folder + '/img_data.pkl') is None:

            img_data = dict()
            i = 0
            for f in filesInBucket:
                print f
                #Load in the file
                file = StringIO()
                f.get_file(file)
                file.seek(0)
                pil_image = Image.open(file)
                
                #Resize
                pil_image_small = pil_image.resize((50, 50), Image.NEAREST) 
                
                #Save 
                out_pil_image_small = cStringIO.StringIO()
                pil_image_small.save(out_pil_image_small, 'PNG')
                 
                k = Key(tsnetooldata_bucket)
                k.key = f.key
                k.set_contents_from_string(out_pil_image_small.getvalue())

                #Get Flattened Data
                img_url = k.generate_url(expires_in=0, query_auth=False)
                img_flat = np.array(pil_image_small).ravel() 

                #Make Dict
                img_data[img_url] = img_flat
                
                if i%100 == 0:
                    print i
                i += 1

                
            k = Key(tsnetooldata_bucket)
            k.key = folder + '/img_data.pkl'
            k.set_contents_from_string(pickle.dumps(img_data))

      
        tsne_json = runTSNE(path, folder, metric, perplexity, exageration, learning_rate)
        print 'complete'
        return tsne_json
    except Exception, e:
        print e
        return ('', 204)


#@app.route('/uploads/')
def runTSNE(path, folder, metric, perplexity, exageration, learning_rate):


    similarities_pickle_file = folder + '/img_similarities_' + metric + '.pkl'
    t_sne_df_pickle_file = folder + '/tsne_fit_' + metric + '_' + str(perplexity) + '_' + str(exageration) + '_' +  str(learning_rate) + '.pkl'

    con_s3 = S3Connection()
    tsnetooldata_bucket = con_s3.get_bucket('tsnetooldata')

    img_data_pkl = tsnetooldata_bucket.get_key(folder + '/img_data.pkl')
    img_data = pickle.loads(img_data_pkl.get_contents_as_string())
 
   
    if tsnetooldata_bucket.get_key(t_sne_df_pickle_file) is None:
        if tsnetooldata_bucket.get_key(similarities_pickle_file) is None:
            print 'No Similarities Pickle'
            print 'Computing Pairwise Distance'
            img_similarities = pairwise_distances(np.array(img_data.values()), metric = metric, n_jobs=-2)
            img_similarities = np.nan_to_num(img_similarities)
            print "Pairwise Distance Complete"

            print 'Saving Image Similarities Pickle'
            k = Key(tsnetooldata_bucket)
            k.key = similarities_pickle_file
            k.set_contents_from_string(pickle.dumps(img_similarities))
        else:
            print 'Loading Image Similarities Pickle'
            img_similarities_pkl = tsnetooldata_bucket.get_key(similarities_pickle_file)
            img_similarities = pickle.loads(img_similarities_pkl.get_contents_as_string())

        print 'No TSNE Pickle'
        print "Running T-SNE"
        tsne_model = TSNE(n_components=2, random_state=0, perplexity = perplexity, early_exaggeration  = exageration ,learning_rate = learning_rate, verbose = 2) #metric = 'precomputed', )
        tsne_fit = tsne_model.fit_transform(img_similarities)
        print 'T-SNE Complete'

        t_sne_df = pd.DataFrame(tsne_fit)
        t_sne_df.columns = ['x', 'y']
        t_sne_df['path'] =  img_data.keys()

        print 'Saving T-SNE Pickle'
        k = Key(tsnetooldata_bucket)    
        k.key = t_sne_df_pickle_file
        k.set_contents_from_string(pickle.dumps(t_sne_df))
    else:
        print 'Loading T-SNE Pickle'
        t_sne_df_pickle = tsnetooldata_bucket.get_key(t_sne_df_pickle_file)
        t_sne_df = pickle.loads(t_sne_df_pickle.get_contents_as_string())


    return t_sne_df[:500].to_json(orient ='records')
    
    
    
if __name__ == "__main__":
	app.run(host='0.0.0.0',port=5000,debug=True)
    
