import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation
from keras.optimizers import RMSprop
import math

DROPOUT_RATE = 0.2
LEARNING_RATE = 0.00005

def getLeastPower2(n:int):
    l = math.ceil(math.log2(n))
    return 1 << l

def LSTM_model(output_class, feed_length, feed_dim, lr=LEARNING_RATE):
    # e.g. 26 -> 32
    model = Sequential()
    model.add(LSTM(64, name='lstm1', input_shape=(feed_length, feed_dim), return_sequences=True, 
        dropout=DROPOUT_RATE, recurrent_dropout=DROPOUT_RATE))
    model.add(LSTM(32, name='lstm2', dropout=DROPOUT_RATE, recurrent_dropout=DROPOUT_RATE))
    model.add(Dense(output_class, name='dense', kernel_initializer='uniform'))
    model.add(Activation('softmax', name='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=lr),
        metrics=['categorical_accuracy'])
    return model
