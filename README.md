# Predicting Neighbourhood Change with Machine Learning

## About this Repository

This repo is intended to support replication and exploration of the analysis undertaken for our [Urban Studies](http://journals.sagepub.com/home/usj) article "Understanding urban gentrification through Machine Learning: Predicting neighbourhood change in London". Although we are not in a position to provide individualised support for installation or configuration of the iPython environment, we _have_ attempted to make it as painless as possible for you to get up and running _without_ hosing your existing Python environment. Please note that final visualisation of the results was undertaken in QGIS, available for free for Mac, PC, and Linux.

## Installation & Start-Up

You will need to install the free Anaconda Python environment in order to run the setup script -- it should not matter if you install the full version or mini-conda so long as you have the conda toolset available to you. For some people the changes to the .bashrc/.bash_profile file made by Anacdona will cause problems elsewhere, so you are advised to see what effect the addition of the `export PATH` line has.

Installation instructions are also contained in the head of the YAML script, but are reproduced here for clarity:
```
conda-env create -f setup.yml
source activate mlgent
python -m ipykernel install --name mlgent --display-name "ML Gentrification"
jupyter lab
```
Obviously, if you see warning or error messages at any point you should stop and attempt to debug rather than mindlessly proceeding.

At this point you should have a new 'kernel' available in Jupyter called 'ML Gentrification' (or just mlgent if you skipped the naming command about). The notebooks have all been set up to expect a kernel with this name and will prompt you to select a different kernel if you've opted to skip the environment creation step above. 

## Replication

### Running the Notebooks

The notebooks have been named in such a way as to make it easy to work out the sequence of 'scripts' that need to be run: start with 01.. and finish with 08. You'll notice that there are two versions of 08 (Neighbourhood Prediction); this is because I had timeout issues running 08 as a notebook and although the analysis would often complete at some point I had no way of knowing when, or if errors had arisen after the timeout occurred. Consequently, you might wish to run the 08 Python _script_ instead as it will provide output directly to the terminal instead of indirectly via the server.

### Geo-Convert

There are also several scripts to support testing of the class created to automate interaction with the MIMAS's Geo-Convert tool. This is essential for mapping between 2001 and 2011 because of boundary changes between the two Censuses. If you are not working with UK Census data then this tool is not relevant (though boundary changes may still impact your results... you have been warned!). I should note that although it is possible, in principle, to update this class to perform any and all of the actions associated with the Geo-Convert web service I have _only_ implemented the 2001 -> 2011 conversion of LSOAs as that is all that I needed.

From time to time the MIMAS may also update Geo-Convert and break the `geoconvert` class; up to a point I will attempt to correct this quickly, but if the changes are substantial enough then this may not be something I'm able to address immediately.

### Downloading Data

Where possible I have attempted to either automate the download of the required data, or to make it available directly from the repo _as downloaded_ from the source web site. In theory the NOMIS API should enable the automated selection and downloading of the data used by notebooks 2 and 3, but at the time that I was doing my work the API was broken and the documentation rather poor. Thus, the data in the `data` folder.

### Random Seeds

Many of the algorithms used in this analysis rely on `randomness` -- I have attempted to set the same seed everywhere that randomness might be used by Python and so your results _should_ match mine. Be aware, however, that minor platform differences or other changes to the code _could_ significaintly alter the results (though we obviously hope not!).

## To Dos

* Adjust GeoConvert Class Testing to be fully self-contained and download a 'random' 2001 data set from the London Data Store for conversion."
* Add links to README
