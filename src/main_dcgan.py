# %%
import matplotlib.pyplot as plt
import random
from scipy import linalg
from tensorflow import keras
import importlib

# import graphviz

import utils.paths as paths
import utils.ploters as ploters 

from utils.image_provider import labels_provider

import utils.image_provider as img_gen

import gan.gan as g
import gan.dcgan as dcg
import gan.cdcgan as cdcg
import utils.gan_utils as g_ut
from keras.utils import to_categorical
import utils.df_preprocessing as preprocess
import metrics.fid as fid

# %%
importlib.reload(img_gen)
importlib.reload(paths)
importlib.reload(ploters)
importlib.reload(g)
importlib.reload(g_ut)
importlib.reload(dcg)
importlib.reload(cdcg)

# %%
#### Possible classes:

# "Watches" #2542 !
# "Handbags" #1759 !
# "Sunglasses" #1073 !
# "Belts" #813 !
# "Backpacks" #724
# "Sarees" #475
# "Deodorant" #347
# "Nail Polish" #329
# "Ties" #263

# "Sports Shoes" #2036
# "Flip Flops" #916 !
# "Formal Shoes" #637

CLASSES = ["Sunglasses", "Ties"]

# %% DF Generator
importlib.reload(img_gen)
importlib.reload(preprocess)

#parameters
BATCH_SIZE = 64
image_heigh = 64
image_weigh = 64
num_color_dimensions = 3 # 1 for greyscale or 3 for RGB
with_color_label = True # class label inlude article color

# Computed parameters
image_size = (image_heigh, image_weigh)
image_shape = (image_heigh, image_weigh, num_color_dimensions)
num_pixels = image_heigh * image_weigh * num_color_dimensions
rgb_on = (num_color_dimensions==3)
is_fid_active = image_heigh == image_weigh and image_weigh > 75 and rgb_on
if(with_color_label and (not rgb_on)): # error check
   raise Exception("Illegal state: color label can be used only with RGB images")

class_mode = "multi_output" if(with_color_label) else "categorical"
train_provider, _  = img_gen.create_data_provider_df(
    paths.IMG_FOLDER,
    CLASSES,
    class_mode=class_mode,
    image_size=image_size,
    batch_size=BATCH_SIZE,
    rgb=rgb_on,
    validation_split=0.001,
    tanh_rescale=True
)
one_hot_label_len = train_provider.num_classes if(with_color_label) else len(train_provider.class_indices)
if(type(train_provider) is img_gen.MultiLabelImageDataGenerator):
    all_one_hot_labels = train_provider.labels
else:
    all_one_hot_labels = to_categorical(train_provider.labels)

ploters.plot_provided_images(train_provider)


# %% DCGAN
importlib.reload(dcg)
importlib.reload(g)
importlib.reload(g_ut)

#input_noise_dim=100
input_noise_dim=100

dcgan,dcgan_generator,dcgan_discriminator=dcg.dcGan().build_dcgan(input_noise_dim, image_shape)
#dcgan.summary()
dcgan_generator.summary()
dcgan_discriminator.summary()
g_ut.plotdcGAN(dcgan)
# %%
optimizer_gen = keras.optimizers.Adam(learning_rate=0.000005)
optimizer_dis = keras.optimizers.Adam(learning_rate=0.000005)

#optimizer_gen = keras.optimizers.SGD(learning_rate=0.0001)
#optimizer_dis = keras.optimizers.SGD(learning_rate=0.0001) 


#optimizer_a = keras.optimizers.legacy.RMSprop()
dcgan_discriminator.compile(loss='binary_crossentropy', optimizer=optimizer_dis)

dcgan_discriminator.trainable = False
dcgan.compile(loss='binary_crossentropy', optimizer=optimizer_gen)

# %%

epoch_count=50

d_epoch_losses,g_epoch_losses=g.Gan().train_gan(dcgan,
                                        dcgan_generator,
                                        dcgan_discriminator,
                                        train_provider,
                                        2000,
                                        input_noise_dim,
                                        epoch_count,
                                        BATCH_SIZE,
                                        g_ut.get_gan_random_input,
                                        g_ut.get_gan_real_batch,
                                        g_ut.get_gan_fake_batch,
                                        g_ut.concatenate_gan_batches,
                                        use_one_sided_labels=True,
                                        plt_frq=2,
                                        plt_example_count=15,
                                        image_shape=image_shape)

ploters.plot_gan_losses(d_epoch_losses,g_epoch_losses)
# %% CDCGAN
importlib.reload(cdcg)
importlib.reload(g)
importlib.reload(g_ut)

input_noise_dim=100
use_one_sided_labels=True

cdcgan,cdcgan_generator,cdcgan_discriminator=cdcg.cdcGan().build_cdcgan(input_noise_dim, one_hot_label_len, image_shape, num_pixels)
#cdcgan.summary()
cdcgan_generator.summary()
cdcgan_discriminator.summary()
g_ut.plotcdcGAN(cdcgan)

# %%
optimizer_gen = keras.optimizers.Adam(learning_rate=0.01)
optimizer_dis = keras.optimizers.Adam(learning_rate=0.01)

#optimizer_gen = keras.optimizers.SGD(learning_rate=0.0001)
#optimizer_dis = keras.optimizers.SGD(learning_rate=0.0001) 


#optimizer_a = keras.optimizers.legacy.RMSprop()
cdcgan_discriminator.compile(loss='binary_crossentropy', optimizer=optimizer_dis)

cdcgan_discriminator.trainable = False
cdcgan.compile(loss='binary_crossentropy', optimizer=optimizer_gen)

# %%
True
epoch_count=10

d_epoch_losses,g_epoch_losses=g.Gan().train_gan(cdcgan,
                                        cdcgan_generator,
                                        cdcgan_discriminator,
                                        train_provider,
                                        2000,
                                        input_noise_dim,
                                        epoch_count,
                                        BATCH_SIZE,
                                        g_ut.get_cgan_random_input,
                                        g_ut.get_cgan_real_batch,
                                        g_ut.get_cgan_fake_batch,
                                        g_ut.concatenate_cgan_batches,
                                        condition_count=one_hot_label_len,
                                        use_one_sided_labels=use_one_sided_labels,
                                        plt_frq=2,
                                        plt_example_count=10,
                                        image_shape=image_shape)
ploters.plot_gan_losses(d_epoch_losses,g_epoch_losses)
# %%True
importlib.reload(ploters)
importlib.reload(img_gen)
if(with_color_label):
   ploters.plot_model_generated_colorfull_article_types(
      cdcgan_generator, 
      len(CLASSES), 
      one_hot_label_len, 
      rows=1,
      imgProducer=img_gen.ConditionalGANImageGenerator)
else:
   ploters.plot_model_generated_article_types(
      cdcgan_generator, 
      one_hot_label_len, 
      rows=1, 
      cols=10,
      imgProducer=img_gen.ConditionalGANImageGenerator)
# %%
image_generator = img_gen.ConditionalGANImageGenerator(cdcgan_generator, labels_provider(all_one_hot_labels, BATCH_SIZE))
fid.compute_fid(train_provider, image_generator, image_shape)
# %%
