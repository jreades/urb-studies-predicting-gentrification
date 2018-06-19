# Predicting Neighbourhood Change with Machine Learning

## About this Repository

This repo is intended to support replication and exploration of the analysis undertaken for our Urban Studies article "Understanding urban gentrification through Machine Learning: Predicting neighbourhood change in London". Although we are not in a position to provide individualised support for installation or configuration of the iPython environment, we _have_ attempted to make it as painless as possible for you to get up and running _without_ hosing your existing Python environment. Please note that final visualisation of the results was undertaken in QGIS, available for free for Mac, PC, and Linux.

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

## Replication


