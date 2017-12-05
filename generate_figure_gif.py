#!/usr/bin/python

import os
import string
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

plt.ioff()

#### general parameters

num_of_variables = 2 # number of variables in data
num_of_clusters = np.random.randint(1, 4) # number of clusters in data
data_points_per_variable = 100 # number of data points per cluster
states_in_movie = 4 # the number of different randomly generated positions for the clusters
steps_between_states = 10 # the resolution of steps between each position
palette = sns.diverging_palette(255, 133, l=60, n=num_of_clusters, center="dark") # the color palette used
names = ['Cats','Dogs','Tentacles','Eyes','Elder Gods'] # A custom list of names for the vars and clusters

### randomly choosing names for variables
var_names = np.random.choice(names, num_of_variables, replace=False)
for name in var_names:
  names.remove(name)

### randomly choosing names for clusters
cluster_names = np.random.choice(names, num_of_clusters, replace=False)
for name in cluster_names:
  names.remove(name)

### This function generates a pandas DataFrame with num_of_variables + 1 columns (one for each variable, and another for
### the cluster name value).
def generate_data(num_of_variables, num_of_clusters, data_points_per_variable, var_names, cluster_names):
  data = np.zeros(shape=(num_of_variables, data_points_per_variable * num_of_clusters))
  ### create several clusters
  for cluster in range(num_of_clusters):
    means = np.random.rand(num_of_variables) # means of cluster for each variable
    stds = np.random.rand(num_of_variables) # std of cluster for each variable
    ### create covariance matrix between variables
    cov = np.random.rand(num_of_variables, num_of_variables) 
    for row in range(cov.shape[0]):
      for col in range(cov.shape[1]):
        cov[row, col] = cov[col, row]
    ### create correlated new data
    new_data = np.random.multivariate_normal(means, cov, data_points_per_variable).T
    ### shift cluster across the axes
    for var in range(num_of_variables):
      new_data[var, :] += np.random.randint(-num_of_clusters, num_of_clusters)
    ### add new data to data set
    data[:, (data_points_per_variable * cluster) : (data_points_per_variable * (cluster + 1))] = new_data
  data += np.abs(np.min(data))
  columns = var_names
  cluster_column = []
  for cluster in range(num_of_clusters):
    cluster_column += [cluster_names[cluster]] * data_points_per_variable
  data = pd.DataFrame(data.T, columns= columns)
  data['cluster'] = cluster_column
  return data

### This function creates a new figure using seaborn
def create_frame(frame_ind, data, palette):
  print 'plotting frame {}'.format(frame_ind)
  fig = plt.figure(figsize=(10,10))
  frame = sns.PairGrid(data = data, hue='cluster', palette=palette); 
  frame = frame.map_upper(plt.scatter)
  frame = frame.map_diag(sns.kdeplot, legend=False, shade=True)
  frame = frame.map_lower(sns.kdeplot, cmap='hot_r')
  frame.set(yticks=[])
  frame.set(xticks=[])
  fig.set_size_inches(5,5)
  plt.savefig('temp_{}/frame_{}.jpg'.format(start_time, str(frame_ind).zfill(4)), transperant=False, format='jpg',bbox_inches='tight', dpi=200)
  plt.close('all')

### This function creates a series of figures transitioning between one cluster position to another
def create_state(first_data, last_data, var_names, steps_between_states, palette, frame_ind):
  # We will fill this list with new data for each step, gradually coming closer to the new cluster
  data_between_steps = []
  data_between_steps.append(first_data)
  for step in range(1, steps_between_states):
    new_data = data_between_steps[step - 1].copy()
    new_data[var_names] += (last_data[var_names] - first_data[var_names]) / steps_between_states
    data_between_steps.append(new_data)

  # For each step between the last state and the new, we generate a new frame
  for step in range(0, steps_between_states - 1):
    create_frame(frame_ind, data_between_steps[step], palette)
    frame_ind += 1  
  # return the last data, to be the beginning of the new state
  return data_between_steps[-1], frame_ind

### Make a temporary folder to keep the frames before the gif
start_time = time.strftime("%Y_%m_%d_%H_%M", time.localtime())
if not os.path.isdir('temp_{}'.format(start_time)):
  os.mkdir('temp_{}'.format(start_time))


### This generates the first position of the clusters
original_data = generate_data(num_of_variables, num_of_clusters, data_points_per_variable, var_names, cluster_names)
first_data = original_data.copy()

### This loop creates a new position for each state, and creates new data for the position of the clusters
### transitioning between the previous state and the new one (with a step resolution of steps_between_states)
frame_ind = 0
for state in range(states_in_movie):
  # First we set the position at the end of the state, to which the clusters with transition
  last_data = generate_data(num_of_variables, num_of_clusters, data_points_per_variable, var_names, cluster_names)
  first_data, frame_ind = create_state(first_data, last_data, var_names, steps_between_states, palette, frame_ind)

### finally, we will return to the original state, creating a loop
last_data = original_data.copy()
_, frame_ind = create_state(first_data, last_data, var_names, steps_between_states, palette, frame_ind)

### If we want, we can add glitches to some of the figures
glitch_frequency = 0.1 # the frequency of glitches in the gif
num_of_glitches = int(frame_ind * glitch_frequency)
for glitch in range(num_of_glitches):
  glitch_ind = np.random.randint(0, frame_ind)
  os.system('jpglitch temp_{}/frame_{}.jpg --jpg'.format(start_time, str(glitch_ind).zfill(4)))

### generate a gif from all the frames
os.system('convert temp_{}/frame_*.jpg -set delay 10 -loop 0  -resize 300x300  small_animation.gif'.format(start_time))
os.system('convert temp_{}/frame_*.jpg -set delay 10 -loop 0   big_animation.gif'.format(start_time))
print 'combined gif'

### finally, remvoe the temporary folder
os.system('rm -rf temp_{}'.format(start_time))

