# tesa-os-only-pipeline

Repo of OS-only GIS tools for tesa processing (aka 'the pipeline'). Below is how to setup the conda environment used for (most) of these tools (some of the deep learning stuff - like 'are-you-square' is the exception - which will have its own conda instructions in the README).

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Using requirements.txt](#using-requirementstxt)
  - [Using environment.yml](#using-environmentyml)
- [Usage](#usage)
- [License](#license)

## Installation

Follow these steps to set up the project on your local machine.

### Prerequisites

- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) should be installed on your system.
- Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (maybe)

### Using `environment.yml`

1. **Clone the Repository**

   ```sh
   git clone https://github.com/American-Forests/tesa-os-only-pipeline.git
   cd tesa-os-only-pipeline
   ```

2. **Create the Conda Environment**

   Create a new Conda environment from the `environment.yml` file:

   ```sh
   conda env create -f environment.yml
   ```

3. **Activate the Conda Environment**

   Activate the environment you just created:

   ```sh
   conda activate OS-only-GIS
   ```

4. **Verify the Installation**

   Ensure all the packages are installed correctly by listing the installed packages:

   ```sh
   conda list
   ```

### Updating the Environment

If you make changes to the `environment.yml` file and need to update the environment, you can use the following command:

```sh
conda env update --file environment.yml --prune
```

The `--prune` flag removes dependencies that are no longer required.

### Deactivating and Removing the Environment

To deactivate the current environment, use:

```sh
conda deactivate
```

To remove the environment completely, use:

```sh
conda env remove -n OS-only-GIS
```

## Usage

For any of the scripts in this repo, please provide instructions and examples for using your project. Here’s an example:

```sh
python script.py
```

## License

This project is licensed under the MIT License.
