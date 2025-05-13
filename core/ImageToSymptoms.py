import base64
import numpy as np
import tensorflow as tf

from io import BytesIO
from PIL import Image
from pathlib import Path
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image as kerasimg
from pathlib import Path

from ..Constants.path import IMAGE_DATASET_FOLDER, IMAGE_MODEL,VALIDATION_DATAFI, TRAINING_DATAFI, IMAGE_MODEL, CLASSINDICES

class ImageToSymptoms:
    def __init__(self):
        self.__model__ = models.load_model(IMAGE_MODEL) if IMAGE_MODEL.exists() else self.__create_model__()
        self.__history__ = None
        self.__IMG_SIZE__ = (128, 128)
        self.__BATCH_SIZE__ = 32
        self.__val_data__ = self.__loadTVData__(VALIDATION_DATAFI, mode='V') if (VALIDATION_DATAFI.exists()) else None
        self.__train_data__ = self.__loadTVData__(TRAINING_DATAFI, mode='T') if (TRAINING_DATAFI.exists()) else None
        self.__class_labels__ = np.load(CLASSINDICES, allow_pickle=True).item() if (CLASSINDICES.exists()) else None
        self.__class_indices__ = {v: k for k, v in self.__class_labels__.items()} if (self.__class_labels__ != None) else None


    def __create_model__(self) -> bool:
        """
        used to create a model
        """
        datagen = kerasimg.ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2,
            horizontal_flip=True,
            zoom_range=0.2
        )

        self.__train_data__ = datagen.flow_from_directory(
            IMAGE_DATASET_FOLDER,
            target_size=self.__IMG_SIZE__,
            batch_size=self.__BATCH_SIZE__,
            class_mode='categorical',
            subset='training'
        )

        self.__val_data__ = datagen.flow_from_directory(
            IMAGE_DATASET_FOLDER,
            target_size=self.__IMG_SIZE__,
            batch_size=self.__BATCH_SIZE__,
            class_mode='categorical',
            subset='validation'
        )

        self.__model__ = models.Sequential([
            layers.InputLayer(input_shape=(128, 128, 3)),

            layers.Conv2D(32, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),

            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),

            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),

            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(self.__train_data__.num_classes, activation='softmax')
        ])

        self.__model__.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        self.__model__.summary()
        self.__history__ = self.__model__.fit(
            self.__train_data__,
            validation_data=self.__val_data__,
            epochs=50
        )

        # Save class_indices from training data
        self.__class_labels__ = self.__train_data__.class_indices
        self.__class_indices__ = {v: k for k, v in self.__class_labels__.items()}
        np.save(CLASSINDICES, self.__train_data__.class_indices)

        x , y = self.__savedTVdata__(self.__train_data__)
        self.__saveTVData__(TRAINING_DATAFI, x, y)
        x, y = self.__savedTVdata__(self.__val_data__)
        self.__saveTVData__(VALIDATION_DATAFI, x, y)
        return True


    def __loadTVData__(self, path:Path, mode:str):
        """
        """
        if mode.lower() == 'v':
            valdata = np.load(path)
            x = valdata['X']
            y = valdata['y']
            valdata = tf.data.Dataset.from_tensor_slices((x, y))
            valdata = valdata.batch(self.__BATCH_SIZE__).prefetch(tf.data.AUTOTUNE)
            return valdata
        
        elif mode.lower() == 't':
            traindata = np.load(path)
            x = traindata['X']
            y = traindata['y']
            traindata = tf.data.Dataset.from_tensor_slices((x, y))
            traindata = traindata.batch(self.__BATCH_SIZE__).prefetch(tf.data.AUTOTUNE)
            return traindata

        else:
            print("Invalid Mode")
    
    def __saveTVData__(self, path, a:np.array, b:np.array) -> bool:
        """
        """
        np.savez(path,X=a, y=b)  # used to save the data
    
    def __savedTVdata__(self, tv: kerasimg.DirectoryIterator) -> np.array:
        """
        """
        print(f"tv : {tv}")
        X, Y = [], []
        for i in range(len(tv)):
            x, y = tv[i]
            X.append(x)
            Y.append(y)

        X = np.concatenate(X)
        Y = np.concatenate(Y)
        print(f"{X},{Y}")
        return X, Y

    def __lengthOfData__(self) -> True:
        """
        Calculating the minimum image that each folder contain and their avg
        """
        dic = {}
        for folder in IMAGE_DATASET_FOLDER.iterdir():
            # for items in folder.iterdir():
            total_images = [items for items in folder.iterdir()]
            dic[folder.name] = len(total_images)

        sum = 0
        count = 0
        for _, j in dic.items():
            sum+=j
            count+=1
        print(f"sum: {sum}, count:{count}")
        avg = sum/count
        print(f"avg: ({avg})")
        lst = [i for i,j in dic.items() if j<31]
        print("Folder contain more images than 31: ",len(lst))
        print("dic: ",dic)
        return True

    def __eval_model__(self) -> bool:
        print(f"self.__train_data__: {self.__train_data__}")
        self.__model__.evaluate(self.__val_data__)
        return True
    
    def __saveModel__(self)-> bool:
        self.__eval_model__()
        self.__model__.save(IMAGE_MODEL)
        return True

    def Predict(self, image:str)->str:
          # Decode base64 string to image
        image_data = base64.b64decode(image.split(",")[-1])
        img = Image.open(BytesIO(image_data)).convert("RGB")
        img = img.resize(self.__IMG_SIZE__)

        # Convert to array and preprocess
        img_array = kerasimg.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict
        prediction = self.__model__.predict(img_array)
        predicted_index = np.argmax(prediction)
        predicted_label = self.__class_indices__[predicted_index]
        return " ".join(predicted_label.split('_'))

# code for testing the image class 

# a = ImageToSymptoms()
# print(f'class : {a.__class_indices__}')
# print(f'class : {a.__class_labels__}')

# # first image Path
# imageForTesting = Path(IMAGE_DATASET_FOLDER / 'blackheads' / '000001.jpg')
# with open(imageForTesting, "rb") as image_file:
#     encoded_bytes = base64.b64encode(image_file.read())
#     base64_str = encoded_bytes.decode('utf-8')

# print(a.Predict(base64_str))