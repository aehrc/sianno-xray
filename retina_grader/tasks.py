
from time import sleep
from retina_grader.models import Document
from django.conf import settings


# Need to run this as a task within a view when document is saved......


def get_image_from_dicom_and_run_dfai(document_id):


	#first gets the image from the DICOM format from the document model and run the AI model using opencv image
	print("Document ID is ",str(document_id))

	doc = Document.objects.get(id=document_id)

	
	if doc.document.name.endswith(".dcm"):
		#read the file as memory file and return as image. 
		file_path = settings.MEDIA_ROOT+ "/" + str(doc.document)
		#run the external program. 
		print(f"Groing to sleep! with file path {file_path}" )

		sleep(30)
	
		print("Task ran!")
		#TODO  - Run the AI program and save the object in the model

		