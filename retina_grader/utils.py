import sys

from pandas import ExcelWriter
from .models import Document, Grading, GradingField, GradingType, Point, Polygon, Rectangle
import json
from django.conf import settings
from django.contrib.auth.models import User
import os
from PIL import Image
import numpy as np
from pydicom import dcmread
import io
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
import shutil
import time
import subprocess as sp #for boilerplate code
import datetime

#boilerplate code to get the image tested and return the result
def get_frcnn_annotation(doc):
	
	print(doc.document.name) #returns 'document_tray/Superuser/filename
	path_to_save = settings.MEDIA_ROOT + "/test_image"
	#create temp dir if required
	if not os.path.exists(path_to_save):
		os.makedirs(path_to_save)
	#copy file from document.path to test image folder using shutil
	shutil.copy(doc.document.path, path_to_save)
	
	
	# event loop should run until the bat file has completed
	run_bat("./", "test.bat")	
	
	
	#return False


def run_bat(filepath, filename):
	p = sp.Popen(filename, cwd=filepath, shell=True)
	out, err = p.communicate()
	
	


#runs the deep learning inferring module on a specific image. 
#Author for this function: Maryam.Mehdizadeh@csiro.au 

if settings.DENTAL_AI_INFER_MODULE_ENABLED : 
# loading the model and weights
	from keras.applications.inception_v3 import InceptionV3
	from keras.applications.inception_v3 import preprocess_input
	from keras.models import Model
	from keras.layers import Dense, GlobalAveragePooling2D
	from keras.layers import Dropout
	from PIL import Image
	import numpy as np
	import tensorflow as tf

	base_model = InceptionV3(weights='imagenet',include_top=False)
	x = base_model.output
	x = GlobalAveragePooling2D()(x)
	x = Dense(1024, activation='relu')(x)
	x = Dropout(0.5)(x)
	predictions = Dense(1, activation='sigmoid')(x) 
	model = Model(input=base_model.input, output=predictions)
	model.compile(optimizer='rmsprop',loss='binary_crossentropy',metrics=['accuracy'])
	model.load_weights(settings.DENTAL_AI_INFER_MODULE_WEIGHTS_FOLDER + '/weights00000100.h5') # load the weights of your best trained model
	keys = ["image_name", "prediction", "outcome"]
	graph = tf.get_default_graph()#Change required to allow django dev server to run the code

def dental_ai_infer_module_process_image(image_file_name_with_path):
	
	global graph#Change required to allow django dev server to run the code
	with graph.as_default():#Change required to allow django dev server to run the code

		print("Opening the image for dental AI infer")
		image = Image.open(image_file_name_with_path)
		image = image.resize((128,128)) # resize the image as per your trained model
		im = np.asarray(image)
		im=np.expand_dims(im,axis=0)
		im = im.astype('float')
		print("About to preprocess")
		im=preprocess_input(im)
		print("About to predict")

		prdct=model.predict(im)
		print("Prediction finished")

		return prdct[0,0] # <0.5 is caries otherwise healthy

def dental_ai_infer_module_crop_image(image_path, x1,x2,y1,y2):
	try:
		img_orginal = Image.open(image_path)
		img_cropped = img_orginal.crop((x1,y1,x2,y2))
		filename = settings.DENTAL_AI_INFER_MODULE_SAVED_IMAGE_FOLDER + datetime.datetime.now().strftime("/cropped-%d-%m-%y-%H-%M-%S.jpg")
		img_cropped.save(filename)
		return filename
	except Exception as ex:
		raise ex



	

#Utils contains functions that don't belong in views, ie: don't return a HTTP Response



def save_rect_info(doc, rect_info, scale):
	print("---------")
	print(doc.random_id)
	print("----------")
	print(rect_info)
	doc.scale = scale
	print(doc.save())
	Rectangle.objects.filter(document = doc).delete()
	for idx, item in enumerate(rect_info):
		print(item["y"])
		print(item["x"], item["width"], item["height"])
		Rectangle.objects.create(document = doc, x = item["x"], y = item["y"], width = item["width"], height = item["height"],
			bone_number= item["bone_number"], 
			fracture_on_current_view= item["fracture_on_current_view"], 
			fracture_on_other_view= item["fracture_on_other_view"], 
			view_type = item["view_type"]
			)
	return 

#Save polygon and associated point information to database
def save_polygon_info(doc, polygons):
	print("save_polygon_info")
	
	Polygon.objects.filter(document = doc).delete()
	for idx, poly in enumerate(polygons):
		print("polygon: ", poly)
		polygon_obj = Polygon.objects.create(document = doc, idx = idx,
			bone_number= poly["bone_number"], 
			fracture_on_current_view= poly["fracture_on_current_view"], 
			fracture_on_other_view= poly["fracture_on_other_view"], 
			view_type = poly["view_type"]
		)	
		print(polygon_obj)
		for idx, item in enumerate(poly["polygon_point_list"]):
			print("item: ", item)
			Point.objects.create(polygon = polygon_obj, x = item['x'], y = item['y'], idx = idx)
	print("save complete")
	return
	

def get_rect_info(doc):
	rects = []
	for item in doc.rectangle_set.all():
		rects.append({"x": str(item.x), "y": str(item.y), "width": str(item.width), "height": str(item.height),		 
		 "bone_number" : item.bone_number,
		 "fracture_on_current_view": item.fracture_on_current_view,
		 "fracture_on_other_view" : item.fracture_on_other_view,
		 "view_type" : item.view_type
		 })
	return rects

# get polygon info from document and return info as two arrays
# called from write_polygon_docs
def get_polygon_info(doc):
	#print("get_polygon_info")
	circle_points = []
	polygon_points = []
	fracture_info = []
	#print("doc polygons: ", doc.polygon_set.all())	
	for polygon in doc.polygon_set.all():
		circle_points_poly = []
		polygon_points_poly = []
		#print("polygon: ", polygon)
		for point in polygon.point_set.all():
			#print("point: ", point)
			circle_points_poly.append({"x":str(point.x), "y":str(point.y), "idx":str(point.idx)})
			polygon_points_poly.append([str(point.x), str(point.y)])
		circle_points.append(circle_points_poly)
		polygon_points.append(polygon_points_poly)
		fracture_info.append({
			"bone_number" : polygon.bone_number,
			"fracture_on_current_view": polygon.fracture_on_current_view,
			"fracture_on_other_view" : polygon.fracture_on_other_view,
			"view_type" : polygon.view_type
		})

	return circle_points, polygon_points, fracture_info


def write_docs(doc):
	path_to_save = settings.MEDIA_ROOT + "/" + str(doc.id) + "/"
	json_name = path_to_save + "rect.json"
	rects = get_rect_info(doc)

	if not os.path.exists(path_to_save):
		os.makedirs(path_to_save)

	with open(json_name, "w") as f:
		json.dump(rects, f, ensure_ascii=False)

	return 

#save polygon data as JSON file in <MEDIA_ROOT>/<doc id>/polygon_new.json
def write_polygon_docs(doc):
	#print("write polygons doc")
	path_to_save = settings.MEDIA_ROOT + "/" + str(doc.id) + "/"
	json_filename = path_to_save + "polygon_new.json"
	#print("trying to get polygon info")
	circle_points, polygon_points, fracture_info = get_polygon_info(doc)
	polygon_json = {"circle" : circle_points, "polygon" : polygon_points, "fracture_info" : fracture_info}
	print("write polygon docs - json result: ", polygon_json)
	#create directory if not already there
	if not os.path.exists(path_to_save):
		os.makedirs(path_to_save)
	#write json file to directory
	with open(json_filename, "w") as f:
		json.dump(polygon_json, f, ensure_ascii=False)
	return

def read_dcm_file(file,file_name):
	print("Before reading the file")
	ds = dcmread(file)
	print("After reading the file")
	accession_number = ds.AccessionNumber
	study_date = ds.StudyDate
	view_position = ds.ViewPosition
	print("after reading meta data")
	image_2d = ds.pixel_array.astype(float)
	print("read the pixel array")
	image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0
	image_2d_scaled = np.uint8(image_2d_scaled)
	image_byte = io.BytesIO()
	
	# Image.fromarray(image_2d_scaled).save("/Users/vig00a/Downloads/test.jpg")	
	Image.fromarray(image_2d_scaled).convert("L").save(image_byte, format="JPEG")
	memory_file = InMemoryUploadedFile(image_byte,None, file_name.replace(".dcm",".jpg"), 'image/jpeg',image_byte.seek(0,os.SEEK_END), None) 
	return (File(memory_file),accession_number,study_date, view_position)