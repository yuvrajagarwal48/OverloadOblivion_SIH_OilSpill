import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import numpy as np

def convert_numpy_to_native(obj):
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_native(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    return obj

def store_data_in_firebase(ais_dict, anomaly_result, sar_prediction, logger):
    # Path to your Firebase service account JSON file
    cred_path = 'scripts/spill-sentinel-firebase-adminsdk-tdawx-df80652d13.json'

    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(cred_path)
    
    # Check if the app is already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    try:
        # Get Firestore client
        db = firestore.client()

        # Get the current timestamp for storing the data
        timestamp = datetime.datetime.now().isoformat()

        # Convert NumPy types to native Python types
        converted_ais_dict = convert_numpy_to_native(ais_dict)
        converted_anomaly_result = convert_numpy_to_native(anomaly_result)
        converted_sar_prediction = convert_numpy_to_native(sar_prediction)

        # Extract MMSI from the converted AIS dictionary
        mmsi = converted_ais_dict.get("MMSI", None)
        if not mmsi:
            raise ValueError("MMSI is missing from AIS data")

        # Combine the dictionaries into a single dictionary for the report
        report_data = {
            "ais_data": converted_ais_dict,
            "MMSI": mmsi,  # Add MMSI as a singular top-level field
            "anomaly_result": converted_anomaly_result,
            "sar_prediction": converted_sar_prediction,
            "timestamp": timestamp
        }

        # Storing the combined report in Firestore under the "reports" collection
        reports_ref = db.collection('reports').document()  # Automatically generate a unique document ID
        reports_ref.set(report_data)
        
        print("Reports saved successfully")
        if logger:
            logger.info("Report stored successfully in Firebase.")
    
    except Exception as e:
        print(f"Error in storing report in Firebase: {e}")
        if logger:
            logger.error("Error storing report in Firebase.",exc_info=True)