import numpy as np
import json
from keras.models import load_model
from keras.losses import MeanSquaredError




class Prediction:

    MODEL_PATH = 'emc_test_automation_api/src/services/trained_lstm_model.h5'
    def __init__():
        pass

    # Define and register the custom mse function
    def custom_mse(y_true, y_pred):
        mse = MeanSquaredError()
        return mse(y_true, y_pred)

    @staticmethod
    def predict_results(inputs):
        try:
            print("\n\n\n\n\n\n\n here \n\n\n\n")
            model = load_model(Prediction.MODEL_PATH, custom_objects={'mse': Prediction.custom_mse})
        except:
            print("\n\n\n\n\n\n\n failed to load model \n\n\n\n\n\n\n ")

        # print(inputs)
        
        # inputs format [0, 1.0, 1.28e-03, -6.39e-07]
        inputs = [float(inputs[0]),float(inputs[1]),float(inputs[2]),float(inputs[3])]
        test_case = np.array(inputs).reshape(1, 1, 4)

        print(test_case)

        try:
            predictions = model.predict(test_case)
            print("\n\n\n\n\n\n\n", predictions[0].tolist(), "\n\n\n\n\n\n\n")

            # Format the response in JSON
            return {  
                "status": 'success',
                "predictions": predictions[0].tolist()
            }
        except :
            print("\n\n\n\n\n\n\n", "failed to predict", "\n\n\n\n\n\n\n")

            return {
                "status" : "fail",
                "predictions": []
            }


