
# 'Are You Square?' - a ROW refinement script

This script is designed to classify parcels based on their geometric properties using a machine learning approach. It combines feature engineering (extracting meaningful metrics from geometries) with a deep learning model for classification. The goal is to distinguish between actual parcels and rights-of-way (ROW) by assigning integer values from 0 to 10 based on the shape characteristics of the polygons.


## Authors

asimmons-steffen

## Deployment

### Prerequisites

Make sure you have the following installed on your machine:
•	Python 3.6 or later
•	Conda (Anaconda or Miniconda)


### Script Structure

The script consists of the following main parts:
1.	Feature Engineering: Extracts geometric features from polygons and multi-polygons.
2.	Labelling Shapes: Labels shapes based on predefined rules applied to the geometric features.
3.	Model Training: Trains a deep learning model on the labelled data.
4.	Classification: Uses the trained model to classify new shapefiles based on their geometric properties.


### Setting Up the environment

* Create a Conda Environment
Open your terminal or command prompt and create a new conda environment:
conda create --name parcel-labeling python=3.8
* Activate the Environment
Activate the newly created environment:
conda activate parcel-labeling
* Install Required Packages
Make sure you have the following Python libraries installed:
```
•	geopandas
•	numpy
•	pandas
•	tensorflow
•	shapely
•	sklearn
•	argparse
•	joblib
•	pyyaml
```

You can install them using the following command:
`pip install geopandas numpy pandas tensorflow shapely scikit-learn joblib pyyaml`


### Folder Structure

Ensure your project directory has the following structure:
```
your_project_directory/
│
├── parcel_classifier.py
├── config_train.yaml
├── config_classify.yaml
├── training_data.shp
├── SanBenito_Training.shp
├── Ludlow.shp
```

## Script Explanation

Feature Engineering

This section calculates various geometric metrics for each polygon in the shapefiles. Key geometric metrics include:
```
•	Width and Height: Dimensions of the bounding box.
•	Diagonal: Length of the diagonal of the bounding box.
•	Aspect Ratio (ar): Ratio of width to height.
•	Compactness Ratio (cr): How circular the polygon is.
•	Shape Factor (sf): Another measure of compactness.
•	Elongation (er): Ratio of the longer side to the shorter side of the bounding box.
•	Perimeter: Length of the boundary of the polygon.
•	Area: Area enclosed by the polygon.
•	Convex Hull Ratio: Ratio of the polygon’s area to the area of its convex hull.
•	Bounding Box Aspect Ratio (bounding_box_ar): Aspect ratio of the bounding box.
•	Perimeter to Area Ratio (perimeter_area_ratio): Ratio of perimeter to area.
```

Loading Data
The `load_data` function reads the shapefiles and calculates geometric features for each polygon.

Labeling Shapes
The `label_shapes` function assigns class labels based on predefined rules applied to the geometric metrics.

Building and Training the Model
The `train_model` function creates a neural network model with batch normalization and dropout layers to prevent overfitting and trains the deep learning model on the labelled training data.

Classifying Shapefiles
The `classify_shapefile` function uses the trained model to classify new shapefiles based on their geometric properties.

Main Function
The `main` function parses the configuration file and executes either training or classification based on the provided configuration.


## YAML Configuration Files

config_train.yaml
This configuration file specifies the mode as train and provides the paths to the input shapefiles, model output file, and scaler output file

save_modelV05.h5 is the file that stores the trained deep learning model used to classify parcels based on their geometric properties.
scaler.pkl is the file that stores the StandardScaler object used to normalize the feature data. Scaling the features ensures that they have a mean of 0 and a standard deviation of 1, which helps the neural network to converge more quickly during training and make more accurate predictions.
Model Accuracy Metric
The accuracy metric is one of the most common metrics used to evaluate the performance of a classification model. It is a measure of how often the model correctly predicts the class label compared to the actual labels in the dataset.
Definition
Accuracy is defined as the ratio of the number of correct predictions to the total number of predictions made. Mathematically, it can be expressed as:
 
Calculation
For a classification model, the accuracy is calculated by comparing the predicted labels to the true labels. Here's how it works:
1.	Correct Predictions: These are instances where the predicted label matches the actual label.
2.	Total Predictions: This is the total number of instances in the dataset.

The accuracy is then the fraction of correct predictions out of the total predictions.

For example:
•	IF the training accuracy is 0.99, it means 95% of the training data was correctly classified by the model.
•	IF the testing accuracy is 0.85, it means 85% of the test data was correctly classified by the model.
•	NOTE: The classification report provides a detailed breakdown of the model's performance for each class in the test data.

config_classify.yaml
This configuration file specifies the mode as classify and provides the paths to the input shapefile, model file, scaler file, and output shapefile.



## Steps to Run Script

1.	Activate Your Environment: Ensure you're in the correct conda environment.
`conda activate parcel-labeling`

2.	Install Required Packages: Make sure you have all required packages installed.
`pip install geopandas numpy pandas tensorflow shapely scikit-learn joblib pyyaml`

3.	Train the Model: Run the training script with the training configuration file.
`python parcel_classifier.py config_train.yaml`

4.	Classify New Data: Run the classification script with the classification configuration file.
`python parcel_classifier.py config_classify.yaml`



