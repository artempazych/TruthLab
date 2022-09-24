from keras.preprocessing.text import Tokenizer
from keras import models
from keras import layers
from numpy import zeros
from random import shuffle
from random import seed
from matplotlib import pyplot

def vectorize_sequences(sequences, dimension=4000):
    results = zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.
    return results


def vectorize_labels(labels):
    results = zeros(len(labels))
    for i, label in enumerate(labels):
        if (label.lower() == 'spam'):
            results[i] = 1
    return results

def test_predict(model, testtext, expected_label):
    testtext_list = []
    testtext_list.append(testtext)
    testtext_sequence = tokenizer.texts_to_sequences(testtext_list)
    x_testtext = vectorize_sequences(testtext_sequence)
    prediction = model.predict(x_testtext)[0][0]

    if prediction > 0.5:
        if expected_label == 'Spam':
            return True
    else:
        if expected_label == 'No spam':
            return True

    return False

tokenizer = Tokenizer()
tokenizer.fit_on_texts(train_data_raw)
train_data_seq = tokenizer.texts_to_sequences(train_data_raw)

x_train = vectorize_sequences(train_data_seq, 4000)
y_train = vectorize_labels(train_labels_raw)

model = models.Sequential()
model.add(layers.Dense(8, activation='relu', input_shape=(4000,)))
model.add(layers.Dense(8, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))
model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
history = model.fit(x_train, y_train, epochs=8, batch_size=100, validation_split=0.5)
epochs = range(1, 9)
history_dict = history.history

acc_values = history_dict['acc']
val_acc_values = history_dict['val_acc']
loss_values = history_dict['loss']