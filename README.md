S3toTSNE
=============

A small D3.js, Flask and Scikit Learn app that lets you visualise images in an S3 bucket using T-SNE.

Note
===============
This application is configured to replicate images in a s3 bucket **/tsnetooldata**. If you don't want images loaded to this bucket, you can change all references to **tsnetooldata** in **app.py**.

It can be configured to use the local file system, but this isn't currently implemented.

To Run
===============

1. Clone the repo.
2. Navigate to **/S3toTSNE/**
3. Ensure your AWS Access Key environment variables are set (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
4. From the command line run `python app.py`
5. Navigate to [http://localhost:5000](http://localhost:5000)

Summary
=============

[T-SNE (T-Stochastic Neighbor Embedding)](https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding) is a dimensionality reduction algorithm that is notably useful for reducing high dimensional data sets such as images, to lower dimensions (normally 2 or 3). 

When in 2 dimensions, images can be visualised using the lower dimension embeddings as x and y coordinates. t-SNE aims to preserve local structure, so similar images appear close to each other - often times obvious clusters will appear.

This tool will take the raw images, conver them to 2d arrays of pixels, run the t-SNE algorithm and visualise in an interactive UI that can be zoomed in and investigated.

A web page will open in the browser with an input box for an S3 folder location, and some setting for t-SNE Parameters. Ensure your S3 bucket is accessable from your local machine.

<img src = "https://github.com/GerHarte/S3toTSNE/blob/master/static/img/Screenshot1.png"/>

Enter your S3 bucket location holding your images. They will get loaded to the application (this could take a while, progress will be printed to the command line). Once the images are converted and loaded into the application, they will be cached so changing parameters and re-running t-SNE will be much faster.

Images will then appear in the UI for you to explore.

<img src = "https://github.com/GerHarte/S3toTSNE/blob/master/static/img/Screenshot2.png"/>

If the embedding does not generate a good visual representation, try different parameters and click Refresh until you are happy with the image map.

<img src = "https://github.com/GerHarte/S3toTSNE/blob/master/static/img/Screenshot5.png"/>

Here you can start to see the structure evolving - the 0's out to the left and the 1's in the lower part. Also within the 1's you can see the more local similarities of slanted 1's closer to the centre and the more vertical 1's on the outside.

You can zoom and pan round the images to inspect the clusters.

<img src = "https://github.com/GerHarte/S3toTSNE/blob/master/static/img/Screenshot6.png"/>

<img src = "https://github.com/GerHarte/S3toTSNE/blob/master/static/img/Screenshot7.png"/>


t-SNE can take some time to tune, there should be 