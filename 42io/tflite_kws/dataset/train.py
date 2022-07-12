import numpy as np
from tensorflow import keras
import tensorflow as tf
DATASET_FILE = 'kws.npz' # 0-9up.npz
dset = np.load(DATASET_FILE)
print(dset['x_train'].shape)
#(1095480, 637)
x_train, x_test, x_valid = (
    dset[i].reshape(-1, 49, 13)[:,1:-1]
    for i in ['x_train', 'x_test', 'x_valid'])
y_train = dset['y_train']
y_test  = dset['y_test']
y_valid = dset['y_valid']

print(x_train.shape, x_test.shape, x_valid.shape)

def spectrogram_masking(spectrogram, dim=1, masks_number=2, mask_max_size=5):
  """Spectrogram masking on frequency or time dimension.
  Args:
    spectrogram: Input spectrum [batch, time, frequency]
    dim: dimension on which masking will be applied: 1 - time; 2 - frequency
    masks_number: number of masks
    mask_max_size: mask max size
  Returns:
    masked spectrogram
  """
  if dim not in (1, 2):
    raise ValueError('Wrong dim value: %d' % dim)
  input_shape = spectrogram.shape
  time_size, frequency_size = input_shape[1:3]
  dim_size = input_shape[dim]  # size of dimension on which mask is applied
  stripe_shape = [1, time_size, frequency_size]
  for _ in range(masks_number):
    mask_end = tf.random.uniform([], 0, mask_max_size, tf.int32)
    mask_start = tf.random.uniform([], 0, dim_size - mask_end, tf.int32)

    # initialize stripes with stripe_shape
    stripe_ones_left = list(stripe_shape)
    stripe_zeros_center = list(stripe_shape)
    stripe_ones_right = list(stripe_shape)

    # update stripes dim
    stripe_ones_left[dim] = dim_size - mask_start - mask_end
    stripe_zeros_center[dim] = mask_end
    stripe_ones_right[dim] = mask_start

    # generate mask
    mask = tf.concat((
        tf.ones(stripe_ones_left, spectrogram.dtype),
        tf.zeros(stripe_zeros_center, spectrogram.dtype),
        tf.ones(stripe_ones_right, spectrogram.dtype),
    ), dim)
    spectrogram = spectrogram * mask
  return spectrogram

train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_dataset = train_dataset.shuffle(len(x_train))
train_dataset = train_dataset.batch(128)
train_dataset = train_dataset.map(lambda x, y: (spectrogram_masking(x, 1, 3, 3), y))
train_dataset = train_dataset.map(lambda x, y: (spectrogram_masking(x, 2, 2, 2), y))

def streaming_input_output(streaming, t, inputs, otputs, x):
  if streaming:
    otputs.append(x)
    x = keras.Input(shape=[t] + x.shape[2:])
    inputs.append(x)
  return x

def build_model(streaming=False):

  # resetting the layer name generation counter
  keras.backend.clear_session()

  inputs  = []
  outputs = []

  x = x_in = keras.Input(shape=(1 if streaming else 47, 13))

  x = keras.layers.Conv1D(128, 1, use_bias=False)(x)
  x = keras.layers.BatchNormalization()(x)
  x = keras.layers.ReLU()(x)
  x = keras.layers.SpatialDropout1D(0.2)(x)

  for i in range(4):
    x = streaming_input_output(streaming, 1 + 2**i, inputs, outputs, x)
    x = keras.layers.SeparableConv1D(128, 2, dilation_rate=2**i, use_bias=False)(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.ReLU()(x)
    x = keras.layers.SpatialDropout1D(0.2)(x)

  x = streaming_input_output(streaming, 32, inputs, outputs, x)
  x = keras.layers.AveragePooling1D(x.shape[1])(x)
  x = keras.layers.Flatten()(x)

  x = keras.layers.Dense(128, use_bias=False)(x)
  x = keras.layers.BatchNormalization()(x)
  x = keras.layers.ReLU()(x)
  x = keras.layers.Dropout(0.2)(x)

  x = keras.layers.Dense(12)(x)
  x = keras.layers.Softmax()(x)

  model = keras.Model(inputs=[x_in] + inputs, outputs=[x] + outputs)

  model.summary()

  return model
  
model = build_model()

model.compile(loss=keras.losses.sparse_categorical_crossentropy,
              optimizer=keras.optimizers.Adam(),
              metrics=['accuracy'])
              
early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        mode='min',
        verbose=1,
        patience=100,
        restore_best_weights=True)

history = model.fit(train_dataset,
                    validation_data=(x_valid, y_valid),
                    callbacks=[early_stopping],
                    verbose=2,
                    epochs=100500)


results = model.evaluate(x_train, y_train, verbose=0)
print('train loss, train acc:', results)

results = model.evaluate(x_test, y_test, verbose=0)
print('test loss, test acc:', results)

results = model.evaluate(x_valid, y_valid, verbose=0)
print('valid loss, valid acc:', results)

stream_model = build_model(True)

# copy weights from old model to new one
for layer in stream_model.layers:
    if layer.get_weights():
      print("Transfer weights for layer {}".format(layer.name))
      layer.set_weights(model.get_layer(name=layer.name).get_weights())
      
converter = tf.lite.TFLiteConverter.from_keras_model(stream_model)
converter.experimental_new_converter = False
tflite_model = converter.convert()
with open("dcnn.tflite", "wb") as f:
  f.write(tflite_model)
