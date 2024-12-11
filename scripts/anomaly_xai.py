import shap
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from scripts.anomaly_detection import AnomalyDetector

def shap_predict_function(input_array):
    # Create an instance of the AnomalyDetector
    anomaly_detector = AnomalyDetector()
    
    # Initialize an empty list to store predictions
    predictions = []
    
    # Iterate through each row in the input array
    for row in input_array:
        # Convert row to DataFrame to match the prepare_data method
        input_df = pd.DataFrame([row], columns=[
            'SOG_mean', 'COG_mean', 'LAT_mean', 'LON_mean', 
            'Heading_mean_heading', 'Status_mode', 'TimeOfDay_mode'
        ])
        
        # Prepare the data
        prepared_input = anomaly_detector.prepare_data(input_df)
        
        # Make prediction
        prediction = anomaly_detector.predict(prepared_input)
        
        # Append the scalar prediction directly
        predictions.append(prediction)
    
    return np.array(predictions)

def generate_base64_plot(plot_function):
    # Create a new figure
    plt.figure(figsize=(10, 6))
    
    try:
        # Call the plot generation function
        plot_function()
        
        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        
        # Encode the bytes as base64
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return image_base64
    
    except Exception as e:
        print(f"Error generating plot: {e}")
        return None
    
    finally:
        # Always close the plot to free up memory
        plt.close()

def plot_instance_shap_values(shap_predict_function, df, input_df):
    # Prepare background data (use a subset of the dataset)
    background_data = df.values[:50]
    
    # Feature names
    feature_names = df.columns.tolist()
    
    # Create SHAP explainer
    explainer = shap.KernelExplainer(shap_predict_function, background_data)
    
    # Convert input DataFrame to numpy array
    input_data = input_df.values
    
    # Ensure input_data is a 2D array
    if input_data.ndim == 1:
        input_data = input_data.reshape(1, -1)
    
    # Calculate SHAP values for the instance
    shap_values = explainer.shap_values(input_data, nsamples=500)
    
    explanation = shap.Explanation(values=shap_values[0], 
                                base_values=explainer.expected_value, 
                                data=input_data[0], 
                                feature_names=feature_names)

    # Ensure shap_values is 2D
    if shap_values.ndim == 1:
        shap_values = shap_values.reshape(1, -1)
    
    # Dictionary to store plot images
    plot_images = {}
    
    # 1. Force Plot
    plot_images['force_plot'] = generate_base64_plot(
        lambda: shap.force_plot(
            explainer.expected_value, 
            shap_values[0], 
            input_data[0], 
            feature_names=feature_names, 
            matplotlib=True, 
            show=False
        )
    )

    # 2. Waterfall Plot
    plot_images['waterfall_plot'] = generate_base64_plot(
        lambda: shap.waterfall_plot(explanation, show=False)
    )
    
    # 3. Feature Contribution Plot
    plot_images['feature_contribution_plot'] = generate_base64_plot(
        lambda: plot_feature_contribution(shap_values[0], feature_names)
    )
    
    return {
        # 'force_plot':plot_images['force_plot'], 
        'waterfall_plot':plot_images['waterfall_plot']
        # 'feature_contribution_plot':plot_images['feature_contribution_plot']

    }

def plot_feature_contribution(shap_values, feature_names):

    # Sort features by absolute SHAP values
    sorted_idx = np.argsort(np.abs(shap_values))
    sorted_features = [feature_names[i] for i in sorted_idx]
    sorted_shap_values = shap_values[sorted_idx]
    
    plt.barh(sorted_features, sorted_shap_values)
    plt.title("Sorted Feature Contributions")
    plt.xlabel("SHAP Value")

def explain_prediction(input_df):
    # Load the dataset
    df = pd.read_csv("data/april_2015_anomaly_final.csv", on_bad_lines='skip')
    df.drop(['MMSI','TimeWindow','TimeOfDay','anomaly','VesselType_mode','Cargo_mode'], axis=1, inplace=True)
    
    # Verify input_df is a DataFrame
    if not isinstance(input_df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    # Verify input_df has the correct columns
    expected_columns = df.columns.tolist()
    if not all(col in input_df.columns for col in expected_columns):
        raise ValueError(f"Input DataFrame must have columns: {expected_columns}")
    
    # Select only the expected columns
    input_df = input_df[expected_columns]
    
    # Perform SHAP explanation
    result = plot_instance_shap_values(shap_predict_function, df, input_df)
    
    return result