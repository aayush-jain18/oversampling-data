# Synthetic Data Generation

A solution for using Machine Learning towards synthetic data generation by 
carrying out exploratory data analysis of existing production database and 
deriving statistical characteristics from the prod DB and then generating 
synthetic data that encapsulates similar statistical properties and maintains 
same referential integrity and correlation co-coefficients.

## Main Features
Here are just a few of the things that Synthetic Data Generation tool does well:

  - Easy handling of Input data, supports multiple input formats such as
    delimited separated files, database connections, excels.
  - Oversamples the Input Data using SMOTENC.
  - Generates and draws a statistics relation for input data and output data.
    for comparison of synthetic data vs input data

## Getting Started

These instructions will get you a copy of the project up and running on your 
local machine for development and testing purposes.

### Prerequisites

Requires Python >= 3.6.2, all dependent python frameworks requirements are 
stated in [requirements.txt](requirements.txt)

### Build and Run

  - Clone or download to your desired location
  ```
  git clone https://github.com/aayush-jain18/synthetic-data-generation.git
  ```
  - cd to the installation directory synthetic-data-master and create a 
    virtualenv to isolate project requirements
  ```
  virtualenv testenv
  ```
  - Activate the virtualenv
  ```
  testenv\Scripts\activate
  ``` 
  - Install all the frameworks requirements in your virtualenv
  ```
  pip install -r requirements.txt
  ```
  - Change the input and output path for results as required in config.yaml
  - Run the framework from parent directory using below command
  ```
  python synthetic-data-generation\main.py
  ```
  - Deactivate the virtualenv once test is completed.
  ```
  deactivate
  ```

### Configuring Input

All the Input and output parameters for the tools can be configured via 
config.yaml, [config.yaml](https://github.com/aayush-jain18/synthetic-data-generation.git)
can be passed to the process from main.py

```python
if __name__ == '__main__':
    START = datetime.now()
    # TODO: Update below config path to load the desired the test config
    CONFIG = load_objects_file(path.abspath('.\\tests\\config.yaml'))
```

**Please use [config.yaml](https://github.com/aayush-jain18/synthetic-data-generation.git) 
as template for creating new configs

### Reports 

All the results are stored to reports, locations that is relative to 
input_path provided via ```config.yaml```. Following files are 
generated as output.

1. log.out (process details and events log)
2. db_metadata.xlsx (if input source is database, generated database metadata)
3. Input data source stats and clusters representation
   1. cluster.png
   2. heatmap.png
   3. pair_plot.png
   4. summary.xlsx
4. Synthetic output results, stats and clusters representation
   1. synth_cluster.png
   2. synth_heatmap.png
   3. synth_pair_plot.png
   4. synth_summary.xlsx
   5. synth_results.xlsx

<b>Input data cluster representation</b>

![alt text](https://github.com/aayush-jain18/synthetic-data-generation.git)

<b>Synthetic Data Generated output cluster representation</b>

![Synthetic cluster](https://github.com/aayush-jain18/synthetic-data-generation.git)

## Built With

* [Pandas](https://pandas.pydata.org/) - Data structures and Data analysis tools for the Python
* [NumPy](https://www.numpy.org/) - Data structures and Data analysis tools for the Python
* [scikit-learn](https://scikit-learn.org/stable/) - Data mining and data analysis
* [imbalanced-learn](https://pypi.org/project/imbalanced-learn/) - re-sampling tools for datasets showing strong between-class imbalance.
* [matplotlib](https://matplotlib.org/) - 2D plotting tools
* [seaborn](https://seaborn.pydata.org/) - statistical data visualization

## Authors

* **Aayush Jain** - *Author* - 

## License

This project is licensed under the **_______** License - see the 
[LICENSE.md](LICENSE.md) file for details
