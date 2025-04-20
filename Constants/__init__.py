# from os.path import dirname, join
from pathlib import Path

# paths for parent directory
# PARENT_DIR = dirname(dirname(__file__))
PARENT_DIR = Path(__file__).resolve().parent.parent

# paths for datasets
DATASET_PATH = PARENT_DIR / 'Datasets'
TRUE_DATASET = DATASET_PATH,'Dataset.csv'
SEVERITY_DATASET = DATASET_PATH / 'Symptom_severity.csv'
DESCRIPTION_DATASET = DATASET_PATH / 'symptom_Description.csv'
PRECAUTION_DATASET = DATASET_PATH / 'symptom_precaution.csv'

# paths for model and encoder
STORAGE_PATH = PARENT_DIR / 'Storage'
SAVED_MODEL_PATH = STORAGE_PATH / 'SavedModels'
SAVED_ENCODER_PATH = STORAGE_PATH / 'SavedEncoders'
KNNMODEL_PATH = SAVED_MODEL_PATH / "KNN_model.pkl"
LENCODER_PATH = SAVED_ENCODER_PATH / "encoder.pkl"

# templates
TEMPLATES_PATH = PARENT_DIR / 'templates'