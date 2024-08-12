import geopandas as gpd
import numpy as np
import pandas as pd
import tensorflow as tf
from shapely.geometry import MultiPolygon
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import argparse
import joblib
import yaml

def calculate_features(geometry):
    try:
        if isinstance(geometry, MultiPolygon):
            features = [calculate_polygon_features(polygon) for polygon in geometry.geoms]
            width = np.max([f[0] for f in features])
            height = np.max([f[1] for f in features])
            diagonal_1 = np.mean([f[2] for f in features])
            ar = np.mean([f[3] for f in features])
            cr = np.mean([f[4] for f in features])
            sf = np.mean([f[5] for f in features])
            er = np.mean([f[6] for f in features])
            perimeter = np.sum([f[7] for f in features])
            area = np.sum([f[8] for f in features])
            convex_hull_ratio = np.mean([f[9] for f in features])
            bounding_box_ar = width / height if height != 0 else float('inf')
            perimeter_area_ratio = perimeter / area if area != 0 else float('inf')
            elongation = np.mean([f[10] for f in features])
            return [width, height, diagonal_1, ar, cr, sf, er, perimeter, area, convex_hull_ratio, bounding_box_ar, perimeter_area_ratio, elongation, True]
        else:
            return calculate_polygon_features(geometry) + [False]
    except Exception as e:
        print(f"Error calculating features: {e}")
        return [0] * 14

def calculate_polygon_features(polygon):
    try:
        bounds = polygon.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        diagonal_1 = np.sqrt((width)**2 + (height)**2)
        ar = width / height if height != 0 else float('inf')
        cr = 4 * np.pi * polygon.area / (polygon.length ** 2)
        sf = polygon.area / (polygon.length ** 2)
        er = max(width, height) / min(width, height) if min(width, height) != 0 else float('inf')
        perimeter = polygon.length
        area = polygon.area
        convex_hull_area = polygon.convex_hull.area
        convex_hull_ratio = area / convex_hull_area if convex_hull_area != 0 else 0
        bounding_box_ar = width / height if height != 0 else float('inf')
        perimeter_area_ratio = perimeter / area if area != 0 else float('inf')
        elongation = max(width, height) / min(width, height) if min(width, height) != 0 else float('inf')
        return [width, height, diagonal_1, ar, cr, sf, er, perimeter, area, convex_hull_ratio, bounding_box_ar, perimeter_area_ratio, elongation]
    except Exception as e:
        print(f"Error calculating polygon features: {e}")
        return [0] * 13

def load_data(shapefile_paths):
    combined_df = pd.DataFrame()
    for shapefile_path in shapefile_paths:
        try:
            gdf = gpd.read_file(shapefile_path)
            features = gdf['geometry'].apply(calculate_features)
            feature_df = pd.DataFrame(features.tolist(), columns=[
                'width', 'height', 'diagonal_1', 'ar', 'cr', 'sf', 'er', 
                'perimeter', 'area', 'convex_hull_ratio', 'bounding_box_ar', 'perimeter_area_ratio', 'elongation', 'is_multipolygon'
            ])
            if 'rw_prb_idx' in gdf.columns:
                feature_df['rw_prb_idx'] = gdf['rw_prb_idx']
            combined_df = pd.concat([combined_df, feature_df], ignore_index=True)
        except Exception as e:
            print(f"Error loading data from {shapefile_path}: {e}")
    return combined_df

def label_shapes(df):
    labels = []
    for idx, row in df.iterrows():
        try:
            ar = row['ar']
            cr = row['cr']
            elongation = row['elongation']
            is_multipolygon = row['is_multipolygon']

            if 0.99 <= ar <= 1.01 and cr > 0.85:
                labels.append(0)  # Exact squares
            elif 0.90 <= ar <= 1.10 and cr > 0.70:
                labels.append(1)  # Near squares
            elif 0.85 <= ar <= 1.15 and cr > 0.60:
                labels.append(2)  # Near squares
            elif 0.80 <= ar <= 1.20 and cr > 0.55:
                labels.append(3)  # Near squares
            elif 0.75 <= ar <= 1.25 and cr > 0.50:
                labels.append(4)  # Less square
            elif 0.70 <= ar <= 1.30 and cr > 0.45:
                labels.append(5)  # Less square
            elif 0.65 <= ar <= 1.35 and cr > 0.40:
                labels.append(6)  # Barely square
            elif elongation > 3 and elongation <= 5:
                labels.append(7)  # Long skinny
            elif elongation > 5 and elongation <= 7:
                labels.append(8)  # Very long skinny
            elif elongation > 7 and elongation <= 9:
                labels.append(9)  # Extremely long skinny
            elif elongation > 9 or is_multipolygon:
                labels.append(10)  # Extremely long and extremely skinny or multipolygon
            else:
                labels.append(4)  # Default to less square if none of the above
        except Exception as e:
            print(f"Error labeling shape at index {idx}: {e}")
            labels.append(-1)  # Assign an invalid label for error cases
    return labels

def train_model(training_data_paths, model_output_path, scaler_output_path):
    try:
        data = load_data(training_data_paths)
        X = data.drop(columns=['rw_prb_idx'], errors='ignore')
        y = np.array(label_shapes(X))
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # Save the scaler
        joblib.dump(scaler, scaler_output_path)
        
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(256, activation='relu', input_shape=(X_train.shape[1],)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='softmax')
        ])
        
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        
        # Training the model
        model.fit(X_train, y_train, epochs=3000, validation_data=(X_test, y_test))
        
        y_pred = np.argmax(model.predict(X_test), axis=1)
        print(classification_report(y_test, y_pred))
        print("Training accuracy:", accuracy_score(y_train, np.argmax(model.predict(X_train), axis=1)))
        print("Testing accuracy:", accuracy_score(y_test, y_pred))
        
        model.save(model_output_path)
        print(f"Model saved to {model_output_path}")
    except Exception as e:
        print(f"Error training model: {e}")

def classify_shapefile(model_path, scaler_path, shapefile_path, output_path):
    try:
        model = tf.keras.models.load_model(model_path)
        scaler = joblib.load(scaler_path)
        data = load_data([shapefile_path])
        X = data.drop(columns=['rw_prb_idx'], errors='ignore')
        
        X = scaler.transform(X)
        
        data['rw_prb_idx'] = np.argmax(model.predict(X), axis=1)
        
        gdf = gpd.read_file(shapefile_path)
        gdf['rw_prb_idx'] = data['rw_prb_idx']
        gdf.to_file(output_path)
        print(f"Classified shapefile saved to {output_path}")
    except Exception as e:
        print(f"Error classifying shapefile: {e}")

def main():
    parser = argparse.ArgumentParser(description="Train and classify parcels and ROW using shapefiles")
    parser.add_argument('config', help="Path to the configuration file")
    
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return
    
    try:
        mode = config['mode']
        inputs = config['inputs']
        model_path = config['model']
        scaler_path = config['scaler']
        output_path = config.get('output')
        
        if mode == 'train':
            train_model(inputs, model_path, scaler_path)
        elif mode == 'classify':
            if not output_path:
                raise ValueError("Output path is required for classify mode")
            classify_shapefile(model_path, scaler_path, inputs[0], output_path)
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
