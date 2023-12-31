import numpy as np
from tensorflow import keras
from keras import layers
from keras import backend as K
import matplotlib.pyplot as plt
import random
import time
from sklearn.model_selection import train_test_split
from tensorflow import keras
from utils.gan_utils import chunks as chk
import utils.ploters as ploters
import utils.gan_utils as gu1


class Gan:
  def build_gan(self,input_noise_dim,neuron_count_per_hidden_layer,image_shape,n_pixel,hidden_activation,generator_output_activation):
    #Generator
    generator = keras.Sequential(name='generator')
    generator.add(layers.Input(shape=input_noise_dim, name='generator_input'))
    for neuron_count in neuron_count_per_hidden_layer:
      generator.add(layers.Dense(neuron_count, activation=hidden_activation))
    
    generator.add(layers.Dense(n_pixel, activation=generator_output_activation,name='generator_output'))
    generator.add(layers.Reshape(image_shape))
    
    #Discriminator
    discriminator = keras.Sequential(name='discriminator')
    discriminator.add(layers.Input(shape=image_shape,name='discriminator_input'))
    discriminator.add(layers.Reshape((n_pixel,)))
    for neuron_count in reversed(neuron_count_per_hidden_layer):
      discriminator.add(layers.Dense(neuron_count, activation=hidden_activation))
    
    discriminator.add(layers.Dense(1, activation='sigmoid',name='discriminator_output'))

    #GAN
    gan = keras.Model(generator.input, discriminator(generator.output),name='gan')
    return gan,generator,discriminator
  
  def train_gan(self,gan,generator,discriminator,train_generator,train_data_count,input_noise_dim,epoch_count, batch_size,
              get_random_input_func,get_real_batch_func,get_fake_batch_func,concatenate_batches_func,condition_count=-1,
              use_one_sided_labels=False,plt_frq=None,plt_example_count=10,image_shape=(28,28)):
    #iteration_count = int(train_data_count / batch_size)
    iteration_count = len(train_generator)
    print('Epochs: ', epoch_count)
    print('Batch size: ', batch_size)
    print('Iterations: ', iteration_count)
    train_data_count = batch_size * iteration_count
    print('Num images: ', train_data_count)
    print('')
    
    #Plot generated images
    if plt_frq!=None:
      print('Before training:')
      noise_to_plot = get_random_input_func(plt_example_count, input_noise_dim,condition_count)
      generated_output = generator.predict(noise_to_plot,verbose=0)
      generated_output = (generated_output * 255).astype(np.uint8)
      #generated_images = generated_output.reshape(plt_example_count, example_shape[0], example_shape[1])
      generated_images = generated_output
      ploters.plot_generated_images([generated_images],1,plt_example_count,figsize=(15, 5))
      
    d_epoch_losses=[]
    g_epoch_losses=[]
    for e in range(1, epoch_count+1):
        start_time = time.time()
        avg_d_loss=0
        avg_g_loss=0

        # Training indices are shuffled and grouped into batches

        for i in range(iteration_count):

            # 1. create a batch with real images from the training set
            real_batch_x,real_batch_y=get_real_batch_func(train_generator,0.9 if use_one_sided_labels else 1)
            #real_batch_x=get_real_batch_func(train_generator,batch_indices[i],0.9 if use_one_sided_labels else 1)

            current_batch_size=len(real_batch_x)
            # 2. create noise vectors for the generator and generate the images from the noise
            generator_input=get_random_input_func(current_batch_size, input_noise_dim,condition_count)
            fake_batch_x,fake_batch_y=get_fake_batch_func(generator,current_batch_size,generator_input)

            # 3. concatenate real and fake batches into a single batch
            discriminator_batch_x = concatenate_batches_func(real_batch_x, fake_batch_x)
            discriminator_batch_y= np.concatenate((real_batch_y, fake_batch_y))

            # 4. train discriminator
            d_loss = discriminator.train_on_batch(discriminator_batch_x, discriminator_batch_y)
            
            i = 0
            g_loss_sum = 0
            while i<10: 
              # 5. create noise vectors for the generator
              gan_batch_x = get_random_input_func(current_batch_size, input_noise_dim,condition_count)
              gan_batch_y = np.ones(current_batch_size)    #Flipped labels

              # 6. train generator
              g_loss = gan.train_on_batch(gan_batch_x, gan_batch_y)
              #print('g_loss while: {0:.3f}'.format(g_loss))
              i = i + 1
              g_loss_sum += g_loss
              if (g_loss<2.0):
                  break
            g_loss = g_loss_sum / i
            #print('i while:', i)
            # 7. avg losses
            avg_d_loss+=d_loss*current_batch_size
            avg_g_loss+=g_loss*current_batch_size
            
        avg_d_loss/=train_data_count
        avg_g_loss/=train_data_count

        d_epoch_losses.append(avg_d_loss)
        g_epoch_losses.append(avg_g_loss)

        end_time = time.time()

        print('Epoch: {0} exec_time={1:.1f}s d_loss={2:.3f} g_loss={3:.3f}'.format(e,end_time - start_time,avg_d_loss,avg_g_loss))

        # Update the plots
        if plt_frq!=None and e%plt_frq == 0:
            generated_output = generator.predict(noise_to_plot,verbose=0)
            generated_output = (generated_output * 255).astype(np.uint8)
            generated_images = generated_output.reshape(plt_example_count, image_shape[0], image_shape[1], image_shape[2])
            ploters.plot_generated_images([generated_images],1,plt_example_count,figsize=(15, 5))
    
    return d_epoch_losses,g_epoch_losses
  
  