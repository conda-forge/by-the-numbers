#!/usr/bin/env bash
if [ ! -d ${HOME}/miniconda ]; then
  curl -sL https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh -o miniconda.sh
  bash miniconda.sh -b -p ${HOME}/miniconda
  rm -f miniconda.sh

  export PATH=${HOME}/miniconda/bin:$PATH

  conda config --set always_yes yes --set changeps1 no
  conda config --add channels defaults
  conda config --add channels conda-forge
  conda update -q conda
fi

export PATH=${HOME}/miniconda/bin:$PATH

conda config --set always_yes yes --set changeps1 no
conda config --add channels defaults
conda config --add channels conda-forge
conda update -q conda

source activate base

mamba update --all -y -q

mamba install -y -q --file conda-requirements.txt
