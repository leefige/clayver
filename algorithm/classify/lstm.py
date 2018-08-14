import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation
from keras.utils import to_categorical
import math

DROPOUT_RATE = 0.2

def getLeastPower2(n:int):
    l = math.ceil(math.log2(n))
    return 1 << l

def lstm(output_class, feed_length, feed_dim):
    # e.g. 26 -> 32
    powerClass = getLeastPower2(output_class)

    model = Sequential()
    model.add(LSTM(powerClass, input_dim=feed_dim, input_length=feed_length, 
        dropout=DROPOUT_RATE, recurrent_dropout=DROPOUT_RATE))
    model.add(Dense(output_class, kernel_initializer='uniform'))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop',
        metrics=['accuracy', 'categorical_accuracy'])
    return model
