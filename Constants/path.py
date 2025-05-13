# from os.path import dirname, join
from pathlib import Path

# paths for parent directory
PARENT_DIR = Path(__file__).resolve().parent.parent

# paths for datasets
DATASET_PATH = PARENT_DIR / 'Datasets'
TRUE_DATASET = DATASET_PATH / 'Dataset.csv'
IMAGE_DATASET_FOLDER = DATASET_PATH / 'imagedataset'
TEMPIMAGEFOLDER = DATASET_PATH / 'TempImageFolder'
SEVERITY_DATASET = DATASET_PATH / 'Symptom_severity.csv'
DESCRIPTION_DATASET = DATASET_PATH / 'symptom_Description.csv'
PRECAUTION_DATASET = DATASET_PATH / 'symptom_precaution.csv'
CLEANSYM_DATASET = DATASET_PATH / 'cleanDataset.pkl'

# paths for model and encoder
STORAGE_PATH = PARENT_DIR / 'Storage'
SAVED_MODEL_PATH = STORAGE_PATH / 'SavedModels'
SAVED_ENCODER_PATH = STORAGE_PATH / 'SavedEncoders'
SAVEDDATA = STORAGE_PATH / 'SavedData'
USERSDATASAVED = STORAGE_PATH / 'UserData'

# models and files
KNNMODEL_PATH = SAVED_MODEL_PATH / "KNN_model.pkl"
LENCODER_PATH = SAVED_ENCODER_PATH / "encoder.pkl"
IMAGE_MODEL = SAVED_MODEL_PATH / 'imageModel.keras'
TRAINING_DATAFI = SAVEDDATA / 'train_data.npz'
VALIDATION_DATAFI = SAVEDDATA / 'val_data.npz' 
CLASSINDICES = SAVEDDATA / 'class_indices.npy'
USERDATAFILE = USERSDATASAVED / 'userData.pkl' # User Data Save

# log folder
LOGFOLDER = PARENT_DIR / 'logs'
LOGFILE = LOGFOLDER / 'log.txt'

# templates
TEMPLATES_PATH = PARENT_DIR / 'templates'

# function for making all the folder that's is not present in the root directory (not file)
def ensure_dirs():
    for path in [DATASET_PATH, STORAGE_PATH, SAVED_MODEL_PATH, SAVED_ENCODER_PATH, LOGFOLDER, SAVEDDATA, USERSDATASAVED]:
        path.mkdir(parents=True, exist_ok=True)

    LOGFILE.touch()