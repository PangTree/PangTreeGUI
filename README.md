# PangtreeVis

## About
PangTreeGUI is a web-browser tool. It enables direct calling [PangtreeBuild](https://github.com/PangTree/PangTreeBuild) but also loading the JSON file which is the result of calling PangtreeBuild.

## Installation (linux)

1) First you need to clone this repository:
```bash
$ git clone git@gitlab.com:PangTree/PangTreeGUI.git
# or
$ git clone https://github.com/PangTree/PangTreeGUI.git
```

2) Create new virtualenv with python>=3.6:
```bash
$  virtualenv -p python3.6 your_venv_name
```

3) Run virtualenv:
```bash
$ source your_venv_name/bin/activate
```

4) Change directory:
```
$ cd PangTreeGUI
```

5) Install requirements:
```bash
$ pip install -r requirements.txt
```

6) Make sure [PangtreeBuild](https://github.com/PangTree/PangTreeBuild) package is installed.
```
$ pip install pangtreebuild
```

## Usage

To use PangTreeGUI you need to activate your virtualenv and be in the PangTreeGUI folder.

```
$ python run.py
```

Open in your web browser (tested in Chrome and Firefox): 127.0.0.1/8052

## Founding
This software is developed with support of [OPUS 11 scientific project of National Science Centre:  Incorporating genomic variation information
into DNA sequencing data analysis](https://www.mimuw.edu.pl/~dojer/rmg/)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
