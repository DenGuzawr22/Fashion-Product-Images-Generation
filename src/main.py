# %%
import math
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd
from tensorflow import keras
from keras import layers
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

from PIL import Image

import importlib

import control_panel as cp
import analysis as an
import utils.paths as paths
import utils.ploters as ploters 
import filters
import utils.bw_converter as bw
import models.vae as v1
import utils.image_generator as im_gen

# %%
importlib.reload(cp)
importlib.reload(an)
importlib.reload(paths)
importlib.reload(ploters)
importlib.reload(filters)
importlib.reload(bw)
importlib.reload(v1)
importlib.reload(im_gen)
importlib.reload(im_gen)


df = pd.read_csv(paths.getDataSetPath('styles.csv'))


# %%
an.showDatasetDetails(df)


# %%
importlib.reload(ploters)
ids = df['id']
selected_image_ids = random.sample(ids.tolist(),10)
ploters.plotImagesById(selected_image_ids)

# %%
importlib.reload(filters)
watches_df = filters.getWatches(df)
ploters.plotRandomImg(watches_df)


# %%
importlib.reload(ploters)
importlib.reload(bw)
bw.convert_to_bw(watches_df['id'])
ploters.plotRandomImg(watches_df, path=paths.BW_IMG_FOLDER_INNER)


# %%
import pathlib
data_dir = pathlib.Path(paths.BW_IMG_FOLDER_INNER).with_suffix('')
image_count = len(list(data_dir.glob('*.jpg')))
print(image_count)

l = list(data_dir.glob('*'))
print(l[0])

Image.open(str(l[0]))

# %% Generator
importlib.reload(im_gen)
generator = im_gen.createImageGenerator(paths.BW_IMG_FOLDER)
im_gen.plotGeneratedImages(generator)


# %% VAE
importlib.reload(v1)
import models.flatVAE as v2
importlib.reload(v2)
vae, vae_encoder, vae_decoder = v2.FlatVAE().getVAE(4800)
v1.plotVAE(vae)

# %%
kl_coefficient=1

#Information needed to compute the loss function
vae_input=vae.input
vae_output=vae.output
mu=vae.get_layer('mu').output
log_var=vae.get_layer('log_var').output

vae.add_loss(v1.vae_loss(vae_input,vae_output,mu,log_var,kl_coefficient,4800))
vae.compile(optimizer='adam')

# %%
epoch_count = 100
# batch_size=100
patience=5

early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=patience, restore_best_weights=True)

history = vae.fit(generator,epochs=epoch_count,callbacks=[early_stop])

# %%
batch_x = next(generator)
wathes = batch_x[0]
print(wathes.shape)
wathes = np.reshape(wathes, (len(wathes),4800))
print(wathes.shape)


# %%
epochs = 1
batch_size = 16

history_train_metrics=[]
for epoch in range(epochs):
    print(f"Epoch {epoch+1}/{epochs}"),
    batch_x = next(generator)  # Assuming the generator yields (batch_x, batch_y)
    

    wathes = batch_x[0]
    wathes = np.reshape(wathes, (len(wathes),4800))
    history = vae.fit(wathes, wathes, batch_size=batch_size, verbose=0)
    history_train_metrics.append(history)
    train_metrics = vae.evaluate(wathes, wathes, verbose = 0)
    print(train_metrics)
    # print('\tTRAIN', end = '')
    # for i in range(len(vae.metrics_names)):
    #   print(' {}={:.4f}'.format(vae.metrics_names[i],train_metrics[i]), end = '')
    # print()
print("end")



batch_x = next(generator)
wathes = batch_x[0][:5]
print(wathes.shape)
ploters.plot_generated_images(wathes, 1, 5)
wathes = np.reshape(wathes, (len(wathes),4800))
print(wathes.shape)
result = vae.predict(wathes)
print(result.shape)
result = np.reshape(result, (len(result), 80, 60, 1))
print(result.shape)
ploters.plot_generated_images(result, 1, 5)


# %%
ploters.plot_history(history_train_metrics, metric='accuracy')

# %%
encoder_input_size = vae_decoder.layers[0].input_shape[0][1]
arr = []
for img in range(10):
    randoms = []
    for i in range(encoder_input_size):
        randoms.append(random.normalvariate(0,1))
    arr.append(randoms)
random_sample = np.array(arr)
print(random_sample.shape)
# print('Random sample: ',random_sample)
decoded_x = vae_decoder.predict(random_sample,verbose=0)
generated = decoded_x.reshape(len(decoded_x), 80, 60, 1)
ploters.plot_generated_images(generated, 1, 5)

# %%
num_images = 20
images_in_cols = 5
rows = math.ceil(num_images/images_in_cols)

generated_images=[]
for row in range(rows):
    single_row_generated_images=[]
    for col in range(images_in_cols):
        random_sample = []
        for i in range(encoder_input_size):
            random_sample.append(random.normalvariate(0,1))
        single_row_generated_images.append(random_sample)
    single_row_generated_images = np.array(single_row_generated_images)
    decoded_x = vae_decoder.predict(single_row_generated_images,verbose=0)
    generated = decoded_x.reshape(len(decoded_x), 80, 60, 1)
    generated_images.append(generated)      

ploters.plot_generated_images(generated_images,rows,images_in_cols)

# %%
