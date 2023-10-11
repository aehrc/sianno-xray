#Runs the AI as a batch process
from retina_grader.models import Document, Rectangle
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
#get the list of images from the database
docs = Document.objects.all()
#create a unique JOB ID for this run. 
job_id = uuid.uuid4()
# os.mkdir("./ai_run_jobs")

input_images_folder = f"/Users/vig00a/code/sianno-xray-github/ai_run_jobs/job_id_{job_id}/images/"
Path(input_images_folder).mkdir(parents=True,exist_ok=True)

input_labels_folder = f"/Users/vig00a/code/sianno-xray-github/ai_run_jobs/job_id_{job_id}/images/labels"

YOLO_PYTHON_PATH = "/Users/vig00a/code/sianno-xray-github/Yolov7_deployment/yolov7/venv_yolo7/bin/python"
#Download the image to a temp file
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

	


#run the registration program
#TODO for now
#read the output of the registration program

#run the AI to number detection

subprocess.run([YOLO_PYTHON_PATH, "detect.py",
                "--weights",
                "./runs/train/exp8/weights/best.pt",
                "--source",
                f"{input_images_folder}",
                 ], 
                 cwd="/Users/vig00a/code/sianno-xray-github/Yolov7_deployment/yolov7") 

#read the output of the AI registration program
#TODO
#read the outputs from the labels AI programs output files 
#the labels to use 
labels =  ['1_Hlx', '4_Dist','1_Prox','4_Mid',
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
  '5_Prox']


for doc in docs:
    results_txt_file = os.path.join(input_labels_folder,f"{doc.id}.txt")
    print(results_txt_file)
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
                    "toe": labels[toe_number],
                    "x": x - width/2,
                    "y": y - height/2,
                    "width": width,
                    "height": height,
                    "confidence" : confidence
                              })
            print(f"BONES: {bones}")

            #create a new document with the same ID 
            doc.id = None
            doc.status = "Draft_AI_Generated"
            doc.save()
            print(f"Document Saved {doc.id}")
            for bone in bones:
                scale = float(doc.scale)
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


                




#save rectangles in the local database

