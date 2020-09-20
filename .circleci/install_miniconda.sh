#!/usr/bin/env bash
if [ ! -d ${HOME}/miniconda ]; then
  curl -s https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh
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

conda update --all -y -q

conda install -y -q --file conda-requirements.txt
