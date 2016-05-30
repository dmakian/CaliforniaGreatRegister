#!/usr/bin/env bash

# create and own the directories to store results locally
save_dir='saved_model/'
data_dir='.'
cp $data_dir'/train.txt' $save_dir'/data/chat.in'
cp $data_dir'/dev.txt' $save_dir'/data/chat_test.in'
