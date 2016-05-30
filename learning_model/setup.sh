#!/usr/bin/env bash

# create and own the directories to store results locally
save_dir='saved_model/'
sudo mkdir -p $save_dir'/data/'
sudo mkdir -p $save_dir'/nn_models/'
sudo mkdir -p $save_dir'/results/'

# copy train and test data with proper naming
data_dir='tf_seq2seq_chatbot/data/train'
cp $data_dir'/train_x.txt' $save_dir'/data/train/x.in'
cp $data_dir'/train_y.txt' $save_dir'/data/train/y.in'

cp $data_dir'/dev_x.txt' $save_dir'/data/dev/x.in'
cp $data_dir'/dev_y.txt' $save_dir'/data/dev/y.in'
