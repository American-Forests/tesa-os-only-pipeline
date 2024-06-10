# tesa-os-only-pipeline

Repo of OS-only GIS tools for tesa processing (aka 'the pipeline'). Below is how to setup the conda environment used for these tools.

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

### Using `requirements.txt`

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Create the Conda Environment**

   Create a new Conda environment and install dependencies from `requirements.txt`:

   ```sh
   conda create --name myenv --file requirements.txt
   ```

3. **Activate the Conda Environment**

   Activate the environment you just created:

   ```sh
   conda activate myenv
   ```

4. **Verify the Installation**

   Ensure all the packages are installed correctly by listing the installed packages:

   ```sh
   conda list
   ```

### Using `environment.yml`

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Create the Conda Environment**

   Create a new Conda environment from the `environment.yml` file:

   ```sh
   conda env create -f environment.yml
   ```

3. **Activate the Conda Environment**

   Activate the environment you just created:

   ```sh
   conda activate myenv
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
conda env remove -n myenv
```

## Usage

Provide instructions and examples for using your project. Here’s an example:

```sh
python script.py
```

## License

This project is licensed under the MIT License.
