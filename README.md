# LandSlide, BengBengBeng!
This is a three-in-one platform designed for the `NASA 2017 Space App Challenge, Taipei`. 

# For Developers

We use python [Flask](http://flask.pocoo.org) framework to setup the frontpage webservice and use [Node](https://nodejs.org/) and [React](https://facebook.github.io/react/) to take care of the upload service and wager service (in submodule `static/landslide_victory` and `landslide_bid` respectively). Backend is implemented with [Ruby on Rails](rubyonrails.org/).

## Getting Started

### Installation

Develop on your own environment

First, clone the project

```bash
$ git clone --recursive -j8 https://github.com/Kai-FengChen/LandSlide_BengBengBeng.git
```
or
```bash
$ git clone https://github.com/Kai-FengChen/LandSlide_BengBengBeng.git
$ cd LandSlide_BengBengBeng
$ git submodule init
$ git submodule update
```

Please note that you have to setup an SSH key for your github in order to clone the submodule successfully. See [here](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/) for help.

Then, install all the prerequisites listed in `requirements.txt` by:

```bash
$ pip install -r requirements.txt
```

Also, for reference, the project is developed with python 3. We recommend to use pyenv-virtualenv to create a clean python environment before installing all the packages. See [here](https://github.com/yyuu/pyenv) and  [here](https://github.com/yyuu/pyenv-virtualenv)

Then, you have to install requirements for each submodule.

```bash
$ cd static/landslide_victory
$ npm install
$ cd ../../landslide_bid
$ npm install
$ cd ../landslide_backend
$ 
```

### Start The Service 

Mainpage:
```bash
$ python hello.py
```
Upload Page:
```bash
$ cd static/landslide_victory
$ npm start
```
Wager Page:
```bash
$ cd landslide_bid
$ npm start
```
Backend and Database:
```bash
$ cd landslide_backend
$ bundle
$ rails db:migrate
$ rails s
```

## Project Structure

```python
LandSlide_BengBengBeng
├── README.md #This File
├── hello.py # MainPage 
├── requirements.txt # Python dependencies
├── landslide_bid # Submodule for Wager Page
├── landslide_backend # Submodule for Backend and Database 
└── static
    ├── CSS
    ├── JS
    ├── data # All the open-data
    └──  landslide_victory # Submodule for Upload Page
└── templates
	└──  sample.html # frontpage
```
