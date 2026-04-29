from setuptools import setup, find_packages
with open ('requirements.txt') as f:
   requirements = f.read().splitlines()
setup(
   name= "MLOps-Project1" ,
   version= "0.1" ,
   author= "Rajendra Kandel" ,
   description= "A sample MLOps project" ,
   packages= find_packages() ,
   install_requires= requirements ,
)

# To install the package, run the following command in the terminal:
# pip install -e .