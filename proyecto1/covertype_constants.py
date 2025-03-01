
# Features with string data types that will be converted to indices
CATEGORICAL_FEATURE_KEYS = ['Soil_Type' , 'Wilderness_Area']

# features númericas que escalados de 0 a 1
NUMERIC_TO_SCALE = ["Hillshade_9am","Hillshade_Noon"]

# features númericas que seran transformadas con z_score
NUMERIC_TO_Z = ["Elevation","Horizontal_Distance_To_Fire_Points","Horizontal_Distance_To_Hydrology","Horizontal_Distance_To_Roadways"]


# Feature that can be grouped into buckets
BUCKET_FEATURE_KEYS = ['Slope']

# Number of buckets used by tf.transform for encoding each bucket feature.
FEATURE_BUCKET_COUNT = {'Slope': 5}

# Feature that the model will predict
Cover_Type_KEY = 'Cover_Type'

# Utility function for renaming the feature
def transformed_name(key):
    return key + '_xf'
