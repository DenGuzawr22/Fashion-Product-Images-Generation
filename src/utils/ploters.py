import numpy as np
import matplotlib.pyplot as plt
import math
from PIL import Image
import random

import utils.paths as paths


def plotRandomImg(df, num=15, path=paths.IMG_FOLDER):
  """ plot random 15 images from dataframe

  Args:
      df (dataframe): pandas dataframe
      num (int, optional): number of images. Defaults to 15.
      path (string, optional): path to the folder with images. Defaults to paths.IMG_FOLDER.
  """
  ids = df['id']
  selected_image_ids = random.sample(ids.tolist(), num)
  plotImagesById(selected_image_ids, path)

def plotImagesById(ids, folder=paths.IMG_FOLDER):
    """Plot images by their id

    Args:
        ids (list): is a list of image id, the number of id must be multiple of 5
    """
    rows = int(len(ids)/5)
    fig, axes = plt.subplots(rows, 5, figsize=(15, rows*3))

    for i, ax in enumerate(axes.flatten()):
        image_id = ids[i]
        image_path = paths.getImagePath(image_id, folder)  
        img = Image.open(image_path)
        ax.imshow(img, cmap='Greys_r')
        ax.set_title(image_id)
        ax.axis('off')

    plt.tight_layout()
    plt.show()

def plot_2d_latent_space(decoder, image_shape):
  n = 12 # number of images per row and column
  limit=3 # random values are sampled from the range [-limit,+limit]

  grid_x = np.linspace(-limit,limit, n) 
  grid_y = np.linspace(limit,-limit, n)

  generated_images=[]
  for i, yi in enumerate(grid_y):
    single_row_generated_images=[]
    for j, xi in enumerate(grid_x):
      random_sample = np.array([[ xi, yi]])
      decoded_x = decoder.predict(random_sample,verbose=0)
      single_row_generated_images.append(decoded_x[0])
    generated_images.append(single_row_generated_images)      

  plot_generated_images(generated_images,n,n,True)



# Contains functions that allow plot data 

def plot_2d_data(data_2d,y,titles=None,figsize=(7,7)):
  _,axs=plt.subplots(1,len(data_2d),figsize=figsize)

  for i in range(len(data_2d)):
    if (titles!=None):
      axs[i].set_title(titles[i])
    scatter=axs[i].scatter(data_2d[i][:,0],data_2d[i][:,1],s=1,c=y[i],cmap=plt.cm.Paired)
    axs[i].legend(*scatter.legend_elements())

def plot_history(history,metric=None):
  fig, ax1 = plt.subplots(figsize=(10, 8))

  epoch_count=len(history.history['loss'])

  line1,=ax1.plot(range(1,epoch_count+1),history.history['loss'],label='train_loss',color='orange')
  ax1.plot(range(1,epoch_count+1),history.history['val_loss'],label='val_loss',color = line1.get_color(), linestyle = '--')
  ax1.set_xlim([1,epoch_count])
  ax1.set_ylim([0, max(max(history.history['loss']),max(history.history['val_loss']))])
  ax1.set_ylabel('loss',color = line1.get_color())
  ax1.tick_params(axis='y', labelcolor=line1.get_color())
  ax1.set_xlabel('Epochs')
  _=ax1.legend(loc='lower left')

  if (metric!=None):
    ax2 = ax1.twinx()
    line2,=ax2.plot(range(1,epoch_count+1),history.history[metric],label='train_'+metric)
    ax2.plot(range(1,epoch_count+1),history.history['val_'+metric],label='val_'+metric,color = line2.get_color(), linestyle = '--')
    ax2.set_ylim([0, max(max(history.history[metric]),max(history.history['val_'+metric]))])
    ax2.set_ylabel(metric,color=line2.get_color())
    ax2.tick_params(axis='y', labelcolor=line2.get_color())
    _=ax2.legend(loc='upper right')

def show_confusion_matrix(conf_matrix,class_names,figsize=(10,10)):
  fig, ax = plt.subplots(figsize=figsize)
  img=ax.matshow(conf_matrix)
  tick_marks = np.arange(len(class_names))
  _=plt.xticks(tick_marks, class_names,rotation=45)
  _=plt.yticks(tick_marks, class_names)
  _=plt.ylabel('Real')
  _=plt.xlabel('Predicted')
  
  for i in range(len(class_names)):
    for j in range(len(class_names)):
        text = ax.text(j, i, '{0:.1%}'.format(conf_matrix[i, j]),
                       ha='center', va='center', color='w')
        

def plot_generated_images(generated_images, nrows, ncols,no_space_between_plots=False, figsize=(10, 10)):
  _, axs = plt.subplots(nrows, ncols,figsize=figsize,squeeze=False)

  for i in range(nrows):
    for j in range(ncols):
      axs[i,j].axis('off')
      axs[i,j].imshow(generated_images[i][j])

  if no_space_between_plots:
    plt.subplots_adjust(wspace=0,hspace=0)

  plt.show()

def plot_gan_losses(d_losses,g_losses):
  fig, ax1 = plt.subplots(figsize=(10, 8))

  epoch_count=len(d_losses)

  line1,=ax1.plot(range(1,epoch_count+1),d_losses,label='discriminator_loss',color='orange')
  ax1.set_ylim([0, max(d_losses)])
  ax1.tick_params(axis='y', labelcolor=line1.get_color())
  _=ax1.legend(loc='lower left')

  ax2 = ax1.twinx()
  line2,=ax2.plot(range(1,epoch_count+1),g_losses,label='generator_loss')
  ax2.set_xlim([1,epoch_count])
  ax2.set_ylim([0, max(g_losses)])
  ax2.set_xlabel('Epochs')
  ax2.tick_params(axis='y', labelcolor=line2.get_color())
  _=ax2.legend(loc='upper right')


def plot_model_input_and_output(generator, model, num=6):
   # Trasform 5 random images from validation set
   val_x, val_y = next(generator)
   if (len(val_x) < num):
      val_x, val_y = next(generator) # redo 

   # get first 5 dataset images
   real_imgs = val_x[:num] 
   labels = val_y[:num]
   plot_generated_images([real_imgs], 1, num)

   generated_imgs = model.predict([real_imgs,labels], verbose=0)
   plot_generated_images([generated_imgs], 1, num)


def plot_losses_from_array(training_losses, validation_losses):
  epochs = list(range(1, len(training_losses) + 1))

  plt.plot(epochs, training_losses, label='Training Loss',  linestyle='-')

  # Plot validation losses
  plt.plot(epochs, validation_losses, label='Validation Loss', linestyle='-')

  # Add labels and a legend
  plt.xlabel('Epochs')
  plt.ylabel('Loss')
  plt.title('Training and Validation Loss Over Epochs')
  plt.legend()