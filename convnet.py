import os
import numpy as np
import pandas as pd
from skimage.io import imread 
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.utils import np_utils
from keras.datasets import mnist

NUM_IMG = 50

def get_training_data(train_path, labels_path):
	train_images = []
	train_files = []  # gather names of files to train
	for filename in os.listdir(train_path):
		if filename.endswith(".png"):
			train_files.append(train_path + filename)

	features = []  # load images as arrays
	for i, train_file in enumerate(train_files):
		if i >= NUM_IMG: break
		train_image = imread(train_file, True)  # loads image from file
		feature_set = np.asarray(train_image)
		features.append(feature_set)

	labels_df = pd.read_csv(labels_path)  # retrieve labels of images
	labels_df = labels_df["Finding Labels"]
	labels = np.zeros(NUM_IMG)  # labels column vector (0 for no finding, 1 for finding)

	# adjust labels column vector
	for i in range(NUM_IMG):
		if (labels_df[i] == 'No Finding'):
			labels[i] = 0
		else:
			labels[i] = 1
	images = np.expand_dims(np.array(features), axis=3).astype('float32') / 255  # adding single channel
	return images, labels


if __name__ == "__main__":
	x_train, y_train = get_training_data("data/train/", "data/train-labels.csv")
	x_test, y_test = get_training_data("data/test/", "data/test-labels.csv")

	f = open("log.txt","w")
	f.write("--------- Images ----------\n")
	f.write(str(x_train) + "\n")
	f.write("--------- Labels ----------\n")
	f.write(str(y_train) + "\n")
	f.close()

	# linear stack of layers
	model = Sequential()

	# Layer 1
	# rectifier linear unit [f(x) = max(0,x)]
	model.add(Conv2D(4, (3, 3), strides=(2,2), activation='relu', input_shape=(1024, 1024, 1), data_format='channels_last'))

	# Layer 2
	# max pooling
	model.add(MaxPooling2D(pool_size=(2,2)))

	# Layer 3
	model.add(Conv2D(4, (3, 3), strides=(2,2), activation='relu'))

	# Layer 4
	# randomly drops 25% of input to prevent overfitting
	model.add(Dropout(0.25))

	# Layer 5
	# flattens the output shape of the input
	model.add(Flatten())

	# Layer 6
	# dense layers will perform classification on features extracted from convolution and maxPooling
	model.add(Dense(1024, activation='relu'))

	# Layer 7
	# dimensionality of output space is one
	model.add(Dense(1, activation='sigmoid'))

	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy']) 
	model.fit(x_train, y_train, batch_size=4, nb_epoch=10, verbose=1)
	score = model.evaluate(x_test, y_test, verbose=0)