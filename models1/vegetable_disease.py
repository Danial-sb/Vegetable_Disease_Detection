# -*- coding: utf-8 -*-
"""Vegetable_disease.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PZ56pH5gfosHgHTlYOXHotk12JAI4kLK
"""

from google.colab import drive
drive.mount("/content/drive")

"""**Importing The Dependencies**"""

import tensorflow as tf
from tensorflow.keras import models, layers
import matplotlib.pyplot as plt
import numpy as np
from keras.utils.vis_utils import plot_model
from tensorflow.keras.callbacks import EarlyStopping
import visualkeras

BATCH_SIZE = 32
IMAGE_SIZE = 256
CHANNELS=3
EPOCHS=50

dataset = tf.keras.preprocessing.image_dataset_from_directory(
    '/content/drive/MyDrive/PlantVillage',
    shuffle = True,
    image_size = (IMAGE_SIZE,IMAGE_SIZE),
    batch_size = BATCH_SIZE
)

class_names = dataset.class_names
class_names

"""**Visualizing The Images**"""

plt.figure(figsize = (9,9))
for image_batch, label_batch in dataset.take(1):
  for i in range(12):
    ax = plt.subplot(3,4, i+1)
    plt.imshow(image_batch[i].numpy().astype('uint8'))
    plt.axis('off')
    plt.title(class_names[label_batch[i].numpy()])

"""**Spliting the data into training, validation, and test partitions.**"""

def get_dataset_partitions(ds, train_split = 0.8, val_split = 0.1, test_split = 0.1, shuffle=True, shuffle_size = 10000):

  if shuffle:
    ds = ds.shuffle(shuffle_size, seed = 12)

  train_size = int(train_split* len(ds))
  val_size = int(val_split* len(ds))

  train_ds = ds.take(train_size)
  val_ds = ds.skip(train_size).take(val_size)
  test_ds = ds.skip(train_size).skip(val_size)

  return train_ds, test_ds, val_ds

train_ds, test_ds, val_ds = get_dataset_partitions(dataset)

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
test_ds = test_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)

#Resizing
resize_and_rescale = tf.keras.Sequential([
  layers.experimental.preprocessing.Resizing(IMAGE_SIZE, IMAGE_SIZE),
  layers.experimental.preprocessing.Rescaling(1./255),
])

#data augmentation
data_augmentation = tf.keras.Sequential([
  layers.experimental.preprocessing.RandomFlip("horizontal_and_vertical"),
  layers.experimental.preprocessing.RandomRotation(0.2),
])

"""**Implementing the model**"""

def model_implementation(train_data, validation_data, batch_size = BATCH_SIZE, image_size = IMAGE_SIZE, epochs = EPOCHS, channels = CHANNELS):

    input_shape = (batch_size, image_size, image_size, channels)
    n_classes = 3
    callback = tf.keras.callbacks.EarlyStopping(min_delta = 0.001, patience = 20, restore_best_weights = True)
    model = models.Sequential([
                  resize_and_rescale,
                  data_augmentation,
                  layers.Conv2D(32, (3,3), activation='relu', input_shape= input_shape),
                  layers.MaxPooling2D((2,2)),
                  layers.Conv2D(64,  kernel_size = (3,3), activation='relu'),
                  layers.MaxPooling2D((2, 2)),
                  layers.Conv2D(64,  kernel_size = (3,3), activation='relu'),
                  layers.MaxPooling2D((2, 2)),
                  layers.Conv2D(64, (3, 3), activation='relu'),
                  layers.MaxPooling2D((2, 2)),
                  layers.Conv2D(64, (3, 3), activation='relu'),
                  layers.MaxPooling2D((2, 2)),
                  layers.Conv2D(64, (3, 3), activation='relu'),
                  layers.MaxPooling2D((2, 2)),
                  layers.Flatten(),
                  layers.Dense(64, activation='relu'),
                  layers.Dense(n_classes, activation='softmax'),

    ])
    model.build(input_shape = input_shape)
    model.compile( optimizer = 'adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False), metrics=['accuracy'])
    history = model.fit(train_data, batch_size = batch_size, validation_data = validation_data, verbose = 1, epochs = epochs, callbacks = [callback])

    return model, history

model, history = model_implementation(train_ds, val_ds)

model.summary()

visualkeras.layered_view(model, legend =True, max_xy = 100)

"""**Evaluation**"""

model.evaluate(test_ds)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(range(EPOCHS), acc, label='Training Accuracy')
plt.plot(range(EPOCHS), val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(range(EPOCHS), loss, label='Training Loss')
plt.plot(range(EPOCHS), val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

for image_batch, label_batch in test_ds.take(1):
  plt.imshow(image_batch[31].numpy().astype('uint8'))
  plt.title(class_names[label_batch[31].numpy()])
  plt.axis('off')

  prediction = model.predict(image_batch)
  print(class_names[np.argmax(prediction[31])])

"""**Saving the model for using in the application**"""

model.save('/content/model/1.h5')