import os
import shutil
from PIL import Image, ImageOps, ImageFilter
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import cv2

class FixData():

    def __init__(self, filepath):
        self.filepath = filepath
        self.train_path = self.filepath + "/train"
        self.train_label_path = self.filepath + "/train_label"
        self.test_path, self.test_label_path = self.rename_folders()
        self.val_path = None
        self.val_label_path = None

    def rename_folders(self):
        try:
            os.rename(os.path.join(self.filepath, "val"), os.path.join(self.filepath, "test"))
            os.rename(os.path.join(self.filepath, "val_label"), os.path.join(self.filepath, "test_label"))
            print("Directory names have successfully been changed.")
        except FileNotFoundError:
            print("Folder does not exist. Either cell has already ran or folder does not exist.")
        except OSError:
            pass
        return self.filepath + "/test", self.filepath + "/test_label"

    def move_folders(self):
        os.makedirs(os.path.join(self.filepath, "train_2"))
        os.makedirs(os.path.join(self.filepath, "train_label_2"))
        shutil.move(self.train_path, os.path.join(self.filepath, "train_2"))
        shutil.move(self.train_label_path, os.path.join(self.filepath, "train_label_2"))
        os.rename(os.path.join(self.filepath, "train_label_2"), os.path.join(self.filepath, "train_label"))
        os.rename(os.path.join(self.filepath, "train_2"), os.path.join(self.filepath, "train"))
        self.new_names()        

    def add_zeros(self, num):
        return str(num.zfill(4))
    
    def new_names(self):
        self.new_train_path = self.train_path + "/train"
        self.new_train_label_path = self.train_label_path + "/train_label"

    def rename_sort_data(self):
        for filename in os.listdir(self.new_train_path):
            updated_filename = filename[44:]
            updated_filename = os.path.join(self.new_train_path, self.add_zeros(updated_filename[:-4])+".png")
            os.rename(os.path.join(self.new_train_path, filename), updated_filename)

        for filename in os.listdir(self.new_train_label_path):
            updated_filename = self.add_zeros(filename[44:-10])
            updated_filename = os.path.join(self.new_train_label_path, updated_filename+".png")
            os.rename(os.path.join(self.new_train_label_path, filename), updated_filename)

        for filename in os.listdir(self.test_path):
            updated_filename = self.add_zeros(filename[44:-19])
            updated_filename = os.path.join(self.test_path, updated_filename+".png")
            os.rename(os.path.join(self.test_path, filename), updated_filename)

        for filename in os.listdir(self.test_label_path):
            updated_filename = self.add_zeros(filename[44:-25])
            updated_filename = os.path.join(self.test_label_path, updated_filename+".png")
            os.rename(os.path.join(self.test_label_path, filename), updated_filename)

    def create_val_set(self, pct):
        if len(os.listdir(self.new_train_path)) == len(os.listdir(self.new_train_label_path)):
            num_val_img = int(len(os.listdir(self.new_train_path))//(pct*100))
            os.makedirs(os.path.join(self.filepath, "val"))
            os.makedirs(os.path.join(self.filepath, "val_label"))
            val_path = self.filepath + "/val"
            val_label_path = self.filepath + "/val_label"
            for img in os.listdir(self.new_train_path)[-num_val_img:]:
               shutil.move(os.path.join(self.new_train_path, img), val_path + "/" + img)

            for img in os.listdir(self.new_train_label_path)[-num_val_img:]:
                shutil.move(os.path.join(self.new_train_label_path, img), val_label_path + "/" + img) 

            if len(os.listdir(val_path)) > 0 and len(os.listdir(val_label_path)) > 0:
                print("Validation directories created.")
        else:
            return "Files in train and train_label are not the length. Please double check this."
            
class SplitData(FixData):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.X_train = []
        self.X_val = []
        self.X_test = []
        self.y_train = []
        self.y_val = []
        self.y_test = []

        self.val_path = self.filepath + "/val"
        self.val_label_path = self.filepath + "/val_label"
        self.new_train_path = self.train_path + "/train"
        self.new_train_label_path = self.train_label_path + "/train_label"

    def resize_img(self, img_size):
        for img in os.listdir(self.new_train_path):
            open_img = Image.open(os.path.join(self.new_train_path, img)).resize((img_size, img_size))
            open_img = ImageOps.grayscale(open_img)
            open_img = np.array(open_img)
            open_img[open_img<200] = 0
            open_img = Image.fromarray(open_img)
            self.X_train.append(np.array(open_img)/np.max(open_img))
            for i in range(5,25,5):
                rot_img = open_img.rotate(i)
                self.X_train.append(np.array(rot_img)/np.max(rot_img))

        for img in os.listdir(self.val_path):
            open_img = Image.open(os.path.join(self.val_path, img)).resize((img_size, img_size))
            open_img = ImageOps.grayscale(open_img)
            open_img = np.array(open_img)
            open_img[open_img<200] = 0
            open_img = Image.fromarray(open_img)
            self.X_val.append(np.array(open_img)/np.max(open_img))
            for i in range(5,25,5):
                rot_img = open_img.rotate(i)
                self.X_val.append(np.array(rot_img)/np.max(rot_img))

        for img in os.listdir(self.test_path):
            open_img = Image.open(os.path.join(self.test_path, img)).resize((img_size, img_size))
            open_img = ImageOps.grayscale(open_img)
            open_img = np.array(open_img)
            open_img[open_img<200] = 0
            open_img = Image.fromarray(open_img)
            self.X_test.append(np.array(open_img)/np.max(open_img))
            for i in range(5,25,5):
                rot_img = open_img.rotate(i)
                self.X_test.append(np.array(rot_img)/np.max(rot_img))

        for img in os.listdir(self.new_train_label_path):
            open_img = Image.open(os.path.join(self.new_train_label_path, img)).resize((img_size, img_size))
            open_img = ImageOps.grayscale(open_img)
            open_img = np.array(open_img)
            open_img[open_img>0] = 1
            open_img = Image.fromarray(open_img)
            self.y_train.append(np.array(open_img))
            for i in range(5,25,5):
                rot_img = open_img.rotate(i)
                self.y_train.append(np.array(rot_img))

        for img in os.listdir(self.val_label_path):
            open_img = Image.open(os.path.join(self.val_label_path, img)).resize((img_size, img_size))
            open_img = ImageOps.grayscale(open_img)
            open_img = np.array(open_img)
            open_img[open_img>0] = 1
            open_img = Image.fromarray(open_img)
            self.y_val.append(np.array(open_img))
            for i in range(5,25,5):
                rot_img = open_img.rotate(i)
                self.y_val.append(np.array(rot_img))

        for img in os.listdir(self.test_label_path):
            open_img = Image.open(os.path.join(self.test_label_path, img)).resize((img_size, img_size))
            open_img = ImageOps.grayscale(open_img)
            open_img = np.array(open_img)
            open_img[open_img>0] = 1
            open_img = Image.fromarray(open_img)
            self.y_test.append(np.array(open_img))
            for i in range(5,25,5):
                rot_img = open_img.rotate(i)
                self.y_test.append(np.array(rot_img))
            

    def print_img_pair(self, num):
        fig = plt.figure(figsize=(10,10))
        plt.subplot(2, 2, 1)
        plt.imshow(np.array(self.X_train[num]), cmap="gray")
        plt.subplot(2, 2, 2)
        plt.imshow(np.array(self.y_train[num]), cmap="gray")

    def get_shapes(self):
        return f"X_train: {np.array(self.X_train).shape}, X_val: {np.array(self.X_val).shape}, X_test: {np.array(self.X_test).shape}, y_train: {np.array(self.y_train).shape}, y_val: {np.array(self.y_val).shape}, y_test: {np.array(self.y_test).shape}"

    def data(self):
        updated_X_train = np.array(self.X_train).reshape(14610,128,128,1).astype('float64')
        updated_y_train = np.array(self.y_train).reshape(14610,128,128,1).astype('float64')
        updated_X_val = np.array(self.X_val).reshape(765,128,128,1).astype('float64')
        updated_y_val = np.array(self.y_val).reshape(765,128,128,1).astype('float64')
        updated_X_test = np.array(self.X_test).reshape(645,128,128,1).astype('float64')
        updated_y_test = np.array(self.y_test).reshape(645,128,128,1).astype('float64')
        return updated_X_train, updated_y_train, updated_X_val, updated_y_val, updated_X_test, updated_y_test
'''
        y_train_stacked = np.dstack((updated_y_train, cv2.bitwise_not(updated_y_train)))
        y_val_stacked = np.dstack((updated_y_val, cv2.bitwise_not(updated_y_val)))
        y_test_stacked = np.dstack((updated_y_test, cv2.bitwise_not(updated_y_test)))

        y_train_stacked = y_train_stacked.reshape(14610,128,128,2)
        y_val_stacked = y_val_stacked.reshape(765,128,128,2)
        y_test_stacked = y_test_stacked.reshape(645,128,128,2)
'''
        

        


    
