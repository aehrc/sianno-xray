# Process steps
# Run the big bone detection algorithm on all "Draft" DICOM images
# This algorithm will create a folder of images in a specified location along with detected big bones in a text file
# For each of the text file, open the file and the DICOM image, resize the image and save it seperately
# Run the second algorithm on the resized image
# Read the output and combine it with the previous rectangle






#Runs the AI as a batch process
from retina_grader.models import Document, Rectangle, Grading, GradingField
import uuid
import os
from django.conf import settings
from pydicom import dcmread
from PIL import Image
import numpy as np
from pathlib import Path
import shutil
import subprocess
import csv
import cv2

#get the list of images from the database
docs = Document.objects.filter(status="Draft").all()
Document.objects.filter(status="Draft_Bone_Detected").delete()


#create a unique JOB ID for this run. 
job_id = uuid.uuid4()
# os.mkdir("./ai_run_jobs")
YOLO_PYTHON_PATH = "/Users/vig00a/code/sianno-xray-github/Yolov7_deployment/yolov7/venv_yolo7/bin/python"
if os.getenv('YOLO_PYTHON_PATH'):
    YOLO_PYTHON_PATH = os.environ.get('YOLO_PYTHON_PATH')


YOLO_PROJECT_PATH = "/Users/vig00a/code/sianno-xray-github/Yolov7_deployment/yolov7"
if os.getenv('YOLO_PROJECT_PATH'):
    YOLO_PROJECT_PATH = os.environ.get('YOLO_PROJECT_PATH')



input_image_folder_root = "/Users/vig00a/code/sianno-xray-github/ai_run_jobs/"
if os.getenv('input_image_folder_root'):
    input_image_folder_root = os.environ.get('input_image_folder_root')

input_images_folder = f"{input_image_folder_root}job_id_{job_id}/images/"


input_resized_images_folder = f"{input_image_folder_root}job_id_{job_id}/images_resized/"

Path(input_images_folder).mkdir(parents=True,exist_ok=True)
Path(input_resized_images_folder).mkdir(parents=True,exist_ok=True)

input_labels_folder = f"{input_image_folder_root}job_id_{job_id}/images/labels"
Path(input_labels_folder).mkdir(parents=True,exist_ok=True)

input_resized_labels_folder = f"{input_image_folder_root}job_id_{job_id}/images_resized/labels"
Path(input_resized_labels_folder).mkdir(parents=True,exist_ok=True)


#Confidence cut off for bone detection

CONFIDENCE_THRESHOLD = 0.0
if os.getenv('BONE_DETECTION_CONFIDENCE_THRESHOLD'):
    CONFIDENCE_THRESHOLD = float(os.environ.get('BONE_DETECTION_CONFIDENCE_THRESHOLD'))

# The following function crops and resizes the images based on the navicular bone

# Crop and resize the image for small bone detection
## Y_max is the y_max coordinate of Navicular bone


#the labels to use 
LABELS_STEP1 =  [
	'1_Hlx', 
	'4_Dist',
	'1_Prox',
	'4_Mid',
  '2_Prox',
  '4_Prox',
  '1_Met',
  '2_Met',
  '3_Met',
  '4_Met',
  '5_Met',
  'Med_Cune',
  'Lat_Cune',
  'Cuboid',
  'Int_Cune',
  'Navicular',
  'Calcaneus',
  'Talus',
  '5_Dist',
  '3_Dis',
  '2_Dist',
  '5_Mid',
  '3_Mid',
  '2_Mid',
  '3_Prox',
  '5_Prox'
  
  ]

LABELS_TO_FILTER_IN_STEP1 = ['Med_Cune',
  'Lat_Cune',
  'Cuboid',
  'Int_Cune',
  'Navicular',
  'Calcaneus',
  'Talus']

LABELS_STEP2 =  [
	'1_Hlx', 
	'4_Dist',
	'1_Prox',
	'4_Mid',
  '2_Prox',
  '4_Prox',
  '1_Met',
  '2_Met',
  '3_Met',
  '4_Met',
  '5_Met',
  '5_Dist',
  '3_Dis',
  '2_Dist',
  '5_Mid',
  '3_Mid',
  '2_Mid',
  '3_Prox',
  '5_Prox'
  
  ]



def crop_resize_image(path_to_image, dcm_name,  y_max):
	import cv2
	## This image is 460 * 460 pixels
	image = cv2.imread(path_to_image + dcm_name)
	height_original, width_original, channels_original = image.shape

	image_cropped = image[:int(y_max * height_original),:]
	print(f"YMAX {y_max}")
	print(f"Image Shape {image.shape}")
	print(f"Image Cropped Shape {image_cropped.shape}")

	cv2.imwrite( input_resized_images_folder + dcm_name, image_cropped)

	## Perhaps you might need to save this size, so you know how to scale back the coordinates to this size
	height, width, channels = image_cropped.shape

	image_cropped_resized = cv2.resize(image_cropped, (460,460), interpolation = cv2.INTER_AREA)

	return image_cropped_resized

#runs the full small and big bone detection 
def run_small_big_bone_detection():



	############# # Download the image to a temp file ####################################



	for doc in docs:
		doc_path = doc.document.path
		
		if doc.document.name.endswith(".dcm"):
			#read the file as memory file and return as image. 
			ds = dcmread (settings.MEDIA_ROOT+ "/" + str(doc.document))
			image_2d = ds.pixel_array.astype(float)
			image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0
			image_2d_scaled = np.uint8(image_2d_scaled)
			format = "PNG"
			# image_byte = io.BytesIO()
			file_name = f"{input_images_folder}{doc.id}.{format}"

			im = Image.fromarray(image_2d_scaled).convert("L").save(file_name, format=format)
			
	
		else:

			file_name = f"{input_images_folder}{doc.id}.{format}"
			shutil.copy( "/media/"+str(doc.document), file_name)

		

	#########################     #############################################
	#run the registration program
	#TODO for now
	#read the output of the registration program


	########################## #run the large bone detector ############################


	subprocess.run([YOLO_PYTHON_PATH, "detect.py",
					"--weights",
					"./runs/train/exp8/weights/best.pt",
					"--source",
					f"{input_images_folder}",
					], 
					cwd=f"{YOLO_PROJECT_PATH}") 

	#read the output of the AI registration program
	#TODO
	#read the outputs from the labels AI programs output files 



	#Run the resize algorithm on each document 

	for doc in docs:
		results_txt_file = os.path.join(input_labels_folder,f"{doc.id}.txt")
		# print(results_txt_file)
		if os.path.exists(results_txt_file):
			print(f"file exists for document: {doc.id}")
			bones = []

			with open(results_txt_file) as resultsfile:
				reader1 = csv.reader(resultsfile, delimiter=" ")
				for row in reader1:
					toe_number = int(row[0])
					x = float(row[1])
					y = float(row[2])
					width = float(row[3])
					height = float(row[4])
					confidence = float(row[5])
					bones.append({
						"toe": LABELS_STEP1[toe_number],
						"x": x - width/2,
						"y": y - height/2,
						"width": width,
						"height": height,
						"confidence" : confidence
								})
				#print(f"BONES: {bones}")

				#get the Navicular bone YMax
				nav_bone_exists = False

				for bone in bones:

					if bone["toe"] == "Navicular":
						nav_y_max = bone["y"]
						nav_bone_exists = True
				#if Navicular bone exists, then proceed with calling the cropping algorithm and calling the small bone detection algorithm
				if nav_bone_exists : 
					crop_resize_image(input_images_folder, f"{doc.id}.PNG", nav_y_max )


	################################################################## RUN SMALL BONE DETECTION ALGORITHM  ##################################################################
	# Now that we have run resize program, we run the STEP 2 (Small bone detection algorithm)
	subprocess.run([YOLO_PYTHON_PATH, "detect.py",
					"--weights",
					"./runs/train/exp8/weights/best-small-bone-detection.pt",
					"--source",
					f"{input_resized_images_folder}",
					], 
					cwd=f"{YOLO_PROJECT_PATH}") 



	######################################################################### READ THE RESULTS FROM THE SMALL BONE #############################################################################

	for doc in docs:
		results_txt_file = os.path.join(input_labels_folder,f"{doc.id}.txt")
		results_resized_txt_file = os.path.join(input_resized_labels_folder,f"{doc.id}.txt")

		# print(results_txt_file)
		bones = []

		if os.path.exists(results_txt_file):
			print(f"file exists for document: {doc.id}")

			with open(results_txt_file) as resultsfile:
				reader1 = csv.reader(resultsfile, delimiter=" ")
				for row in reader1:
					toe_number = int(row[0])
					x = float(row[1])
					y = float(row[2])
					width = float(row[3])
					height = float(row[4])
					confidence = float(row[5])
					# Only use the big bones from Step 1. 
					if LABELS_STEP1[toe_number] in LABELS_TO_FILTER_IN_STEP1 :

						bones.append({
							"toe": LABELS_STEP1[toe_number],
							"x": x - width/2,
							"y": y - height/2,
							"width": width,
							"height": height,
							"confidence" : confidence
									})
				#print(f"BONES: {bones}")
		

			#Check if Resized rectangles are saved, if yes then load the bones detected from the algorithm
			if os.path.exists(results_resized_txt_file):

				with open(results_resized_txt_file) as resultsfile:
					reader1 = csv.reader(resultsfile, delimiter=" ")
					for row in reader1:
						toe_number = int(row[0])
						x = float(row[1])
						y = float(row[2])
						width = float(row[3])
						height = float(row[4])
						confidence = float(row[5])
						bones.append({
							"toe": LABELS_STEP2[toe_number],
							"x": x - width/2,
							"y": y - height/2,
							"width": width,
							"height": height,
							"confidence" : confidence
									})
					#print(f"BONES_RESIZED: {bones}")
		

	###########################################################################################################################################################################



	#Save the document into new document and rectangles


	for doc in docs:
		results_txt_file = os.path.join(input_labels_folder,f"{doc.id}.txt")
		results_resized_txt_file = os.path.join(input_resized_labels_folder,f"{doc.id}.txt")
		
		bones = []

		# print(results_txt_file)
		#first check the big bones detection files

		if os.path.exists(results_txt_file):
			print(f"file exists for larger bone document: {doc.id}")

			with open(results_txt_file) as resultsfile:
				reader1 = csv.reader(resultsfile, delimiter=" ")
				for row in reader1:
					toe_number = int(row[0])
					x = float(row[1])
					y = float(row[2])
					width = float(row[3])
					height = float(row[4])
					confidence = float(row[5])
					# Only use the big bones from Step 1. 

					if confidence > CONFIDENCE_THRESHOLD and LABELS_STEP1[toe_number] in LABELS_TO_FILTER_IN_STEP1 :

						bones.append({
							"toe": LABELS_STEP1[toe_number],
							"x": x - width/2,
							"y": y - height/2,
							"width": width,
							"height": height,
							"confidence" : confidence
									})
						# pass
					
		# check for small bone detection files
		if os.path.exists(results_resized_txt_file):
				print(f"file exists for smaller bone document: {doc.id}")

				with open(results_resized_txt_file) as resultsfile:
					reader1 = csv.reader(resultsfile, delimiter=" ")
					for row in reader1:
						toe_number = int(row[0])
						x = float(row[1])
						y = float(row[2])
						width = float(row[3])
						height = float(row[4])
						confidence = float(row[5])
						if confidence > CONFIDENCE_THRESHOLD:
							bones.append({
								"toe": LABELS_STEP2[toe_number],
								"x": x - width/2,
								"y": y - height/2,
								"width": width,
								"height": height,
								"confidence" : confidence
										})
							# pass
				#print(f"BONES: {bones}")

		
		print(f"Final Bone: {bones}")


		#create a new document with the same ID
		old_doc_id = doc.id #used to read the original image height in the STEP 2 small bone detector

		#set the draft document status to processed
		doc.status = "Removed_From_Draft"
		doc.save()

		doc.id = None
		doc.status = "Draft_Bone_Detected"
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
			scale = float(doc.scale)
			# If the bone is the small bone detector, then get the height of the small bone image and 
			#use it in  the new bone.
			if bone["toe"] in LABELS_STEP2:
				print("Bone in STEP 2")
				resized_image_path = os.path.join(input_resized_images_folder,f"{old_doc_id}.PNG")
				im = Image.open(resized_image_path)
				resized_height = im.height
				print(f"Resized height{resized_height}, Original Height {doc.height}, Bone Height {bone['height']}, Bone Y {bone['y']}")
				rect = Rectangle(document = doc,
								x= int(bone["x"] * doc.width / scale ) , 
								#the Y from the results text is for the cropped image. we need to first get the height with respect to that and then add the cropped height to get the actual Y

								y = int(
									
									((bone["y"] * resized_height) ) / scale
									
									), 
								width = int(bone["width"] * doc.width / scale), 
								#the height from the results text is for the cropped image. we need to first get the height with respect to that and then add the cropped height to get the actual height

								height = int(
									((bone["height"] * resized_height) ) / scale)
									,
								annotation_type = "Osteomyelitis",
								toe_number  = bone["toe"]

								)
			
				rect.save()			
			else:

				rect = Rectangle(
					document = doc,
									x= int(bone["x"] * doc.width / scale ) , 
									y = int(bone["y"] * doc.height / scale), 
									width = int(bone["width"] * doc.width / scale), 
									height = int(bone["height"] * doc.height / scale),
									annotation_type = "Osteomyelitis",
									toe_number  = bone["toe"]

									)
				
				rect.save()
			print(f"Rect Saved {rect.id}")


					
