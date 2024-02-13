from .models import Document, Grading, GradingField, Point, Polygon, Rectangle
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


#Utils contains functions that don't belong in views, ie: don't return a HTTP Response

def save_rect_info(doc, rect_info, scale):
	print("---------")
	print(doc.random_id)
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

def save_foot_rect_info(doc, rect_info, scale):
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
		created_rect = Rectangle.objects.create(document = doc, x = item["x"], y = item["y"], width = item["width"], height = item["height"],
			annotation_type = item["annotation_type"],
			toe_number = item["toe_number"],

			# fracture_on_current_view= item["fracture_on_current_view"], 
			# fracture_on_other_view= item["fracture_on_other_view"], 
			# view_type = item["view_type"]
			)

		# toe_numbers = item["toe_number"].split(",")
		print("=============================")
		print(item["toe_number"])
		print("=============================")
		
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
		#  "bone_number" : item.bone_number,
		#  "fracture_on_current_view": item.fracture_on_current_view,
		#  "fracture_on_other_view" : item.fracture_on_other_view,
		#  "view_type" : item.view_type,
		 "annotation_type": item.annotation_type,
		 "toe_number": item.toe_number,
		 "osteomyelitis_present_score": round(item.osteomyelitis_present_score * 100)
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

def write_docs_foot(doc):
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
	view_position = "Not Available"
	anatomy = "Not Available"

	# view_position = ds.ViewPosition
	if ((0x0018, 0x1030) in ds): 
		view_position = ds[0x0018, 0x1030].value
	if ((0x0040, 0x0254) in ds): 
		anatomy = ds[0x0040, 0x0254].value
		
	#(0018, 1030) # View posion for foot
	#(0040, 0254) #anatomy for foot

	print("after reading meta data")
	image_2d = ds.pixel_array.astype(float)
	print("read the pixel array")
	image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0
	image_2d_scaled = np.uint8(image_2d_scaled)
	image_byte = io.BytesIO()
	
	# Image.fromarray(image_2d_scaled).save("/Users/vig00a/Downloads/test.jpg")	
	im = Image.fromarray(image_2d_scaled).convert("L")
	im.save(image_byte, format="JPEG")
	memory_file = InMemoryUploadedFile(image_byte,None, file_name.replace(".dcm",".jpg"), 'image/jpeg',image_byte.seek(0,os.SEEK_END), None) 
	return (File(memory_file),accession_number,study_date, view_position, anatomy, im.height,im.width)



# Run the Osteomyelities Detection for a given document ID

import uuid
from pathlib import Path
import cv2
import subprocess


def run_osteomyelitis_detection(document):
	job_id = uuid.uuid4()

	OSTEO_WORKING_PATH = "/Users/vig00a/code/sianno-xray-github/ai_run_jobs/osteo/"
	OSTEO_PYTHON_PATH = "/Users/vig00a/code/sianno-xray-github/df_osteo_detection_program/venv-df-osteo/bin/python"

	if os.getenv('OSTEO_WORKING_PATH'):
		OSTEO_WORKING_PATH = os.environ.get('OSTEO_WORKING_PATH')

	if os.getenv('OSTEO_PYTHON_PATH'):
		OSTEO_PYTHON_PATH = os.environ.get('OSTEO_PYTHON_PATH')

	CONFIDENCE_THRESHOLD = 0.5
	if os.getenv('OSTEO_DETECTION_CONFIDENCE_THRESHOLD'):
		CONFIDENCE_THRESHOLD = float(os.environ.get('OSTEO_DETECTION_CONFIDENCE_THRESHOLD'))

	input_images_osteomyelitis = f"{OSTEO_WORKING_PATH}job_id_{job_id}/"
	cropped_rect_osteomyelitis_images = f"{OSTEO_WORKING_PATH}job_id_{job_id}/cropped_images/"
	results_rect_osteomyelitis_images = f"{OSTEO_WORKING_PATH}job_id_{job_id}/cropped_images/results"

	Path(input_images_osteomyelitis).mkdir(parents=True,exist_ok=True)
	Path(cropped_rect_osteomyelitis_images).mkdir(parents=True,exist_ok=True)
	Path(results_rect_osteomyelitis_images).mkdir(parents=True,exist_ok=True)

	#First get the document's PNG
	doc_path = document.document.path



	im = None

	if document.document.name.endswith(".dcm"):
		#read the file as memory file and return as image. 
		ds = dcmread (settings.MEDIA_ROOT+ "/" + str(document.document))
		image_2d = ds.pixel_array.astype(float)
		image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0
		image_2d_scaled = np.uint8(image_2d_scaled)
		format = "PNG"
		# image_byte = io.BytesIO()
		file_name = f"{input_images_osteomyelitis}{document.id}.{format}"

		im = Image.fromarray(image_2d_scaled).convert("L").save(file_name, format=format)
		im = Image.open(file_name)


	rectangles = Rectangle.objects.filter(document = document)
	scale = float(document.scale)

	for rect in rectangles:
		try:
			
			print(f"rect x,y {rect.x},{rect.y}, W, H { rect.width}, {rect.height} Scale: {document.scale}")
			rect_left = rect.x * scale
			rect_top = rect.y * scale
			rect_right = (rect.x + rect.width) * scale
			rect_bottom = (rect.y + rect.height) * scale



			
			# im1 = im.crop((rect_left,rect_top, rect_right, rect_bottom))

			# im1.save(f'{cropped_rect_osteomyelitis_images}{rect.id}.png', format="PNG")


			#Crop 224x224 image 
			#get the center x and y 
			rect_center_x = (rect.x +  (rect.width)/2)* scale
			rect_center_y = (rect.y +  (rect.height)/2)* scale
			#now get the 224x224 rect coordinates
			cropped_rect_left = round(rect_center_x - (224/2))
			cropped_rect_top = round(rect_center_y - (224/2))
			cropped_rect_right = round(rect_center_x + (224/2))
			cropped_rect_bottom = round(rect_center_y + (224/2))
			im1 = im.crop((cropped_rect_left,cropped_rect_top, cropped_rect_right, cropped_rect_bottom))
			im1.save(f'{cropped_rect_osteomyelitis_images}{rect.id}.png', format="PNG")
			print(f"saved cropped rectangle left, top, right, bottom {cropped_rect_left}, {cropped_rect_top}, {cropped_rect_right}, {cropped_rect_bottom}")


			#if the width and height is greater than 224, then resize
			#left off here


		except Exception as ex:
			print(str(ex))



	#  Run the Osteo Detection on the input folder.#################

	DJANO_WORKING_DIRECTORY = "/Users/vig00a/code/sianno-xray-github/retina_grader"
	if os.getenv('DJANO_WORKING_DIRECTORY'):
		DJANO_WORKING_DIRECTORY = os.environ.get('DJANO_WORKING_DIRECTORY')

	subprocess.run([OSTEO_PYTHON_PATH, "run_osteo.py",
				"--source",
				f"{cropped_rect_osteomyelitis_images}",
					"--output_folder",
				f"{results_rect_osteomyelitis_images}",
				 ], 
				 cwd=DJANO_WORKING_DIRECTORY) 

	print("Ran the Osteo Detection ")


	############## once the process has run successfully. read the results text from the file and load the rectangles

	results_file_name = f'{results_rect_osteomyelitis_images}/results.txt'
	print(f"results file name: {results_file_name}")
	results = json.loads(open(results_file_name).read())
	print(f"results : {results}")

	#we assume that the results is stored in the following format: 
	for result in results:
		if result["osteomyelitis_present_score"] >= CONFIDENCE_THRESHOLD:
			rect_id = result["rect_id"]
			osteomyelitis_present_score = result["osteomyelitis_present_score"]
			rect = Rectangle.objects.get(id = rect_id)
			print("got the rect to be saved, updating scores")
			rect.osteomyelitis_present_score = osteomyelitis_present_score
			rect.save()
			print(f"rectangle updated with score RectID { rect_id}, Score {osteomyelitis_present_score}")	




	return True

def create_new_documents_for_osteomyelitis():
	try:

		#get the new allocated to user
		user1 = User.objects.get(username="bone_labeler1")
		user2 = User.objects.get(username="osteo_labeler1")
		#get the documents where the labeler1 has finished the bone labelling

		docs = Document.objects.filter(status="Reviewed", 
									allocated_to = user1 
									)

		for doc in docs:
			bones = Rectangle.objects.filter(document = doc)
			doc.id = None
			doc.status = "Draft_Osteo_Detected"
			doc.allocated_to = user2
			#Adjust the Scale if not set appropriately
			if doc.width > 1000:
				doc.scale = doc.width / 1000

			doc.save()
			print(f"Document Saved {doc.id}")

			#Create new Grading 
			if doc.grading_set.count() == 0:

				for gf in GradingField.objects.all():
					grading = Grading(grading_field=gf, document=doc)
					grading.value = grading.grading_field.default_value
					grading.save()
			#for each bones, remove any duplicates and keep only the ones with the highest confidence
			



			#For each bones, create a new rectangle and save it in the database
			for bone in bones:
				bone.id = None
				bone.document = doc
				bone.save()


		#now for each document for user2 in draft, run the osteo detection algorithm
		docs = Document.objects.filter(status="Draft_Osteo_Detected", 
									allocated_to = user2 
									)
		
		for doc in docs:
			run_osteomyelitis_detection(doc)
		
		return True
	except Exception as ex:
		print(f"Error in osteo detection {str(ex)}")
		return False