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



