
import tensorflow as tf
import tensorflow_transform as tft

import covertype_constants

# Unpack the contents of the constants module

_CATEGORICAL_FEATURE_KEYS=covertype_constants.CATEGORICAL_FEATURE_KEYS
_NUMERIC_TO_SCALE=covertype_constants.NUMERIC_TO_SCALE
_NUMERIC_TO_Z=covertype_constants.NUMERIC_TO_Z
_BUCKET_FEATURE_KEYS=covertype_constants.BUCKET_FEATURE_KEYS
_FEATURE_BUCKET_COUNT=covertype_constants.FEATURE_BUCKET_COUNT
_Cover_Type_KEY=covertype_constants.Cover_Type_KEY
_transformed_name=covertype_constants.transformed_name

# Define the transformations
def preprocessing_fn(inputs):
    """tf.transform's callback function for preprocessing inputs.
    Args:
        inputs: map from feature keys to raw not-yet-transformed features.
    Returns:
        Map from string feature key to transformed feature operations.
    """
    outputs = {}

    # Scale these features to the range [0,1]
    for key in _NUMERIC_TO_SCALE:
        outputs[_transformed_name(key)] = tft.scale_to_0_1(
            inputs[key])

    # Returns a standardized column with mean 0 and variance 1
    for key in _NUMERIC_TO_Z:
        outputs[_transformed_name(key)] = tft.scale_to_z_score(
            inputs[key])
    
    # Bucketize these features
    for key in _BUCKET_FEATURE_KEYS:
        outputs[_transformed_name(key)] = tft.bucketize(
            inputs[key], _FEATURE_BUCKET_COUNT[key])

    # Convert strings to indices in a vocabulary
    for key in _CATEGORICAL_FEATURE_KEYS:
        outputs[_transformed_name(key)] = tft.compute_and_apply_vocabulary(inputs[key])

    # Convert the label strings to an index
    outputs[_transformed_name(_Cover_Type_KEY)] = tft.compute_and_apply_vocabulary(inputs[_Cover_Type_KEY])
    
    return outputs
