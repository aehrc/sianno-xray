import re
from django.shortcuts import render
from .models import Document, Grading, GradingField, GlobalSettings, Rectangle
from django.shortcuts import HttpResponseRedirect, Http404, HttpResponse
from django.http.response import JsonResponse

from django.contrib.auth.decorators import login_required

from django.db.models.signals import  post_init, post_save, pre_save
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings
import random
import string
import csv
import json

import os
from .utils_run_ai import *


from .utils import save_polygon_info, save_rect_info, save_foot_rect_info, write_docs, read_dcm_file, write_polygon_docs, create_new_documents_for_osteomyelitis
# if settings.DIABETIC_FOOT_AI_ENABLED : 
# 	from .utils_diabetic_foot_ai import *



	
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
#import django async task library for post processing upon saving

# from django_q.tasks import async_task

from .utils import run_osteomyelitis_detection


#Receivers
#receives notification from a signal dispatcher that some action has taken place
@receiver(post_save, sender=Document)
def document_post_save(sender, instance, *args, **kwargs):
	print("Document POST Save" , str(instance))

	# async_task("retina_grader.tasks.get_image_from_dicom_and_run_dfai", instance.id)


	if instance.grading_set.count() == 0:

		for gf in GradingField.objects.all():
			grading = Grading(grading_field=gf, document=instance)
			grading.value = grading.grading_field.default_value
			grading.save()

	

@receiver(pre_save, sender=Document)
def document_pre_save(sender, instance, *args, **kwargs):
	#Set document type based on image name
	if instance.type == None:
		try:
			img_path, img_name = os.path.split(instance.document.path)
			instance_name, instance_extension = img_name.split(".")
			print("THE IMAGE NAME IS: ------------------------------")
			print(instance_name)
			doc_types  = {"OP": "PANAROMIC","BW":"BITEWING"}
			instance.type = doc_types[instance_name[:2]]
		except Exception as ex:
			print(str(ex))
			instance.type = "UNKNOWN"


	if settings.USE_RANDOM_ID == True and instance.random_id == "UNASSIGNED":
		instance.random_id = "%s_%04d" % (
		list(string.ascii_uppercase)[random.randint(0, 25)], random.randint(0, 2000))
		user = User.objects.get(username = GlobalSettings.objects.get(key="default_allocated_user").value)

		instance.allocated_to = user
 
	#save the document's scale from the beginning
	if instance.width > 1000:
		instance.scale = instance.width / 1000
		



#Views
@login_required
@csrf_exempt
def detail(request):
	annotation = "rect-foot" #use "poly" or "rect" to load the respective annotation tool
	#view used for rectangle annotation
	if annotation == "rect":
		try:
			document_id = request.GET["d"]
			doc = Document.objects.get(id=document_id)
			write_docs(doc)
			total_count = Document.objects.filter(allocated_to = request.user).count()
			completed_count = Document.objects.filter(status="Reviewed", allocated_to=request.user).count()

			if request.method == "GET":
				print("GET Request: ", request.GET)
				if doc == None:
					return HttpResponse("Record Cannot be opened or you are not authorised")
				return render(request, "detail.html", {
					"doc": doc,
					"completed_count" : completed_count,
					"total_count" : total_count,
					"annotation" : annotation})
			elif request.method == "POST":
				print("Post request: ", request.POST)
				if "foot_xray" in request.POST:
					print("updating foot xray info")
					foot_xray_rects = json.loads(request.POST['foot_xray_rects'])
					scale = json.loads(request.POST['scale'])
					print("--------------------")
					print(foot_xray_rects)
					print("---------SCALE IS-----------")
					print(scale)
					print("--------------------")
					save_foot_rect_info(doc, foot_xray_rects, scale)
					return JsonResponse({"result" : "OK"})

				if "save_next_wrist_xray" in request.POST:
					#get exclude value from the form.
					print("Save next wrist xray")
					#if exclude is true then we get all records with the same accession number and set the status 
					if "exclude_accession_number" in request.POST and request.POST["exclude_accession_number"] == "on":
						docs = Document.objects.filter(accession_no = doc.accession_no)
						docs.update(status="EXCLUDED")

						#get the next document in draft
						d = Document.objects.filter(status="Draft", allocated_to=request.user).first()
						if d == None:
							return HttpResponseRedirect("/sianno/" )
						return HttpResponseRedirect("/sianno/detail/?d="+str(d.id)+"")
					#as "EXCLUDE" and save the record and then load the next record.


					
				for p in request.POST:
					if p.startswith("grading_"):
						g = Grading.objects.get(id = p.split("grading_")[1])
						g.value = request.POST[p]
						g.save()
						#get the next record..
				doc.status = "Reviewed"
				doc.save()
				#get the next document in draft
				d = Document.objects.filter(status="Draft", allocated_to=request.user).first()
				if d == None:
					return HttpResponseRedirect("/sianno/" )
				return HttpResponseRedirect("/sianno/detail/?d="+str(d.id)+"")
		except Exception as ex:
			return HttpResponse(str(ex))
	elif annotation == "rect-foot":
		try:
			document_id = request.GET["d"]
			doc = Document.objects.get(id=document_id)
			# if settings.DIABETIC_FOOT_AI_ENABLED : 
				# get_image_from_dicom_and_run_dfai(document_id)
				# get_image_from_dicom_and_run_dfai(document_id)
			write_docs(doc)
			total_count = Document.objects.filter(allocated_to = request.user).count()
			completed_count = Document.objects.filter(status="Reviewed", allocated_to=request.user).count()
			
			if request.method == "GET":
				print("GET Request: ", request.GET)
				if doc == None:
					return HttpResponse("Record Cannot be opened or you are not authorised")
				#run the AI inference from here. 
				
				return render(request, "detail.html", {
					"doc": doc,
					"completed_count" : completed_count,
					"total_count" : total_count,
					"annotation" : annotation})
			elif request.method == "POST":

				#if the foot_xray_run_osteomylitis_detection is selected, then run the Osteo detection and return OK if all ran successfully. 
				if "foot_xray_run_osteomylitis_detection" in request.POST:
					print("running osteo detection")
					if run_osteomyelitis_detection(doc) : 
						return JsonResponse({"result" : "OK"})	
					else:
						return JsonResponse({"result": "NOT OK"})
					
				if "wrist_xray" in request.POST:
					print("updating wrist xray info")
					wrist_xray_rects = json.loads(request.POST['wrist_xray_rects'])
					scale = json.loads(request.POST['scale'])
					print("--------------------")
					print(wrist_xray_rects)
					print("---------SCALE IS-----------")
					print(scale)
					print("--------------------")
					save_rect_info(doc, wrist_xray_rects, scale)
					return JsonResponse({"result" : "OK"})
				
				if "foot_xray" in request.POST:
					print("updating foot xray info")
					foot_xray_rects = json.loads(request.POST['foot_xray_rects'])
					scale = json.loads(request.POST['scale'])
					print("--------------------")
					print(foot_xray_rects)
					print("---------SCALE IS-----------")
					print(scale)
					print("--------------------")
					save_foot_rect_info(doc, foot_xray_rects, scale)
					return JsonResponse({"result" : "OK"})
				if "save_next_foot_xray" in request.POST:
					#get exclude value from the form.
					print("JUST CHECKING THE POST HERE_______________________")
					print(request.POST)
					print("Save next foot xray")
					#if exclude is true then we get all records with the same accession number and set the status 
					if "exclude_accession_number" in request.POST and request.POST["exclude_accession_number"] == "on":
						docs = Document.objects.filter(accession_no = doc.accession_no)
						docs.update(status="EXCLUDED")

						#get the next document in draft
						d = Document.objects.filter(status="Draft", allocated_to=request.user).first()
						if d == None:
							return HttpResponseRedirect("/sianno/" )
						return HttpResponseRedirect("/sianno/detail/?d="+str(d.id)+"")
					#as "EXCLUDE" and save the record and then load the next record.
				if "save_next_wrist_xray" in request.POST:
					#get exclude value from the form.
					print("JUST CHECKING THE POST HERE_______________________")
					print(request.POST)
					print("Save next wrist xray")
					#if exclude is true then we get all records with the same accession number and set the status 
					if "exclude_accession_number" in request.POST and request.POST["exclude_accession_number"] == "on":
						docs = Document.objects.filter(accession_no = doc.accession_no)
						docs.update(status="EXCLUDED")

						#get the next document in draft
						d = Document.objects.filter(status="Draft", allocated_to=request.user).first()
						if d == None:
							return HttpResponseRedirect("/sianno/" )
						return HttpResponseRedirect("/sianno/detail/?d="+str(d.id)+"")
					#as "EXCLUDE" and save the record and then load the next record.
				for p in request.POST:
					
					if p.startswith("grading_"):
						g = Grading.objects.get(id = p.split("grading_")[1])
						g.value = request.POST[p]
						g.save()
						#get the next record..
				doc.status = "Reviewed"
				doc.save()
				#get the next document in draft
				
				STATUS_TEXT = "Draft"

				if settings.DIABETIC_FOOT_AI_ENABLED == True:
					#for bone labler, we return the next draft bone detected document
					if doc.allocated_to.username == "bone_labeler1":
						STATUS_TEXT = "Draft_Bone_Detected"
					elif doc.allocated_to.username == "osteo_labeler1":
						STATUS_TEXT = "Draft_Osteo_Detected"


				d = Document.objects.filter(status=STATUS_TEXT, allocated_to=request.user).first()
				if d == None:
					return HttpResponseRedirect("/sianno/" )
				return HttpResponseRedirect("/sianno/detail/?d="+str(d.id)+"")
		except Exception as ex:
			return HttpResponse(str(ex))

	#polygon annotation and saving methods		
	elif annotation == "poly":
		print("annotation type: ", annotation)
		try:		
			document_id = request.GET["d"]
			doc = Document.objects.get(id=document_id)			
			write_polygon_docs(doc)
			total_count = Document.objects.filter(allocated_to = request.user).count()			
			completed_count = Document.objects.filter(status="Reviewed", allocated_to=request.user).count()			
			if request.method == "GET":
				if doc == None:
					return HttpResponse("Record cannot be opened or you are not authorised")
				return render(request, "detail.html", {
					"doc": doc,
					"completed_count": completed_count,
					"total_count": total_count,
					"annotation" : annotation
				})				
			elif request.method == "POST":
				try:					
					print("post request: ", request.POST)
					polygons = json.loads(request.POST['polygons'])					
					save_polygon_info(doc, polygons)
					doc.status = "Reviewed"
					try:
						doc.save()
					except Exception as e:
						print("problem saving: ", str(e))
					redirect_url = "/sianno/"
					#get the next document in draft
					d = Document.objects.filter(status="Draft", allocated_to=request.user).first()
					if d == None:
						redirect_url = "/sianno/"
					else:
						redirect_url = "/sianno/detail/?d="+str(d.id)
					return JsonResponse({"result":"OK", "redirect_url":redirect_url})
				except Exception as ex:
					return JsonResponse({"result" : str(ex)})		
		except Exception as ex:
			print(str(ex))
			return HttpResponse(str(ex))
			
	#end if


@login_required
def index(request):
	if request.user.groups.filter(name__in=["coordinator"]).exists() : 
		document_list = Document.objects.filter(allocated_to = request.user).order_by("status")
		total_count = Document.objects.all().count()
		completed_count = Document.objects.filter(status = "Reviewed").count()
	else:
		document_list = Document.objects.filter(allocated_to = request.user).order_by("status")
		total_count = Document.objects.filter(allocated_to = request.user).count()
		completed_count = Document.objects.filter(allocated_to = request.user, status = "Reviewed").count()
	# next_doc = Document.objects.filter(status="Draft").first()
	

	return render(request, "index.html", {"document_list" : document_list,
										#   "next_doc" : next_doc,
										  "completed_count" : completed_count,
										  "total_count" : total_count})

#get the list of documents that belong to the user
@login_required
def index_json(request):
	if request.user.groups.filter(name__in=["coordinator"]).exists() : 
		document_list = Document.objects.filter(allocated_to = request.user, status = request.GET["status"]).order_by("accession_no")
		# total_count = Document.objects.all().count()
		# completed_count = Document.objects.filter(status = "Reviewed").count()
	else:
		document_list = Document.objects.filter(allocated_to = request.user, status = request.GET["status"]).order_by("accession_no")
		# total_count = Document.objects.filter(allocated_to = request.user).count()
		# completed_count = Document.objects.filter(allocated_to = request.user, status = "Reviewed").count()
	
	document_json = []
	for doc in document_list:
		document_json.append({
"id":str(doc.id),
"status":doc.status,
"user": doc.allocated_to.username,
"purpose":doc.purpose,
"type": doc.type,
"accession_no" : doc.accession_no,
"view_position": doc.view_position,
"anatomy": doc.anatomy,
"date_modified" : doc.date_modified.strftime("%d/%m/%y %H:%M %z")

		})
	return JsonResponse(document_json, safe=False)


# Export data as a csv file via the 'Actions' dropdown list
@login_required
def data_export(request):
	try:
		docs = Document.objects.all()
		data = []

		for d in docs:
			gx_quality,gx_orientation, gx_caries, rectangles = "N/A", "N/A","N/A", "[]"
			try:
				gx_quality = Grading.objects.filter(document = d, grading_field__grading_type__text = "Quality").first().value
			except:
				pass
			try:
				gx_orientation = Grading.objects.filter(document=d, grading_field__grading_type__text="Orientation").first().value
			except:
				pass
			try:
				gx_caries = Grading.objects.filter(document=d, grading_field__grading_type__text="Presence of Caries").first().value
			except:
				pass

			try:
				rectangles = []
				rects = Rectangle.objects.filter(document = d)
				for rect in rects:
					rectangles.append({"x": rect.x,
					 "y": rect.y,
					  "width": rect.width,
					   "height": rect.height,
					    # "bone_number": rect.bone_number,
					    #   "fracture_on_current_view": rect.fracture_on_current_view, 
					    #   "fracture_on_other_view": rect.fracture_on_other_view, 
						  "annotation_type" : rect.annotation_type,
						  "toe_number" : rect.toe_number,
						  })
			except:
				pass	

			data.append({
					"System ID" : str(d.id),
					"file_name" : d.document.name,
						"allocated_to": d.allocated_to.username,
						#  "type" : d.type,
						# "purpose" : d.purpose,
						 "status" : d.status,
						#  "Quality of images" : gx_quality,
						#  "Orientation" : gx_orientation,
						#  "Presence of Caries" : gx_caries,
						"view_type" : d.view_position,
						"accession_no" : d.accession_no,
						"anatomy": d.anatomy,

						 "Rectangles" : rectangles,
						 "scale": d.scale
						 })

		with open('export.csv', mode='w') as csv_file:
			field_names = ["System ID","file_name","allocated_to",
			# "type",
			# "purpose",
			"status",
			#"Quality of images","Orientation","Presence of Caries",
			"view_type","accession_no","anatomy",
			"Rectangles", "scale"]
			csvw = csv.DictWriter(csv_file, field_names)
			csvw.writeheader()
			csvw.writerows(data)
		res = HttpResponse(open("export.csv", "rb"), content_type='application/csv')
		res['Content-Disposition'] = 'attachment; filename="sianno_export.csv"'
		return res

	except Exception as ex:
		return HttpResponse(str(ex))

@login_required
def new_files(request):
	
	if request.user.groups.filter(name__in=["coordinator"]).exists() : 
		if request.method == "GET":
			users = User.objects.all()
			purposes = ["GRADING"] #"SCREENING",
			image_types = [
				# "WRIST-XRAY", 
				"FOOT-XRAY"
				] #"BITEWING", "PANAROMIC", "RETINA", "OTHER",

			return render(request,"modals/new_files_modal.html", {"users": users, "purposes": purposes, "image_types": image_types})
		elif request.method == "POST":
			try:
				print("Got the post request")
				print(request.POST)

				selected_user = User.objects.get(username=request.POST["username"])
				purpose = request.POST["purpose"]
				image_type = request.POST['image_type']
				for file in request.FILES.getlist('files'):
					#if the file is a dicom image then load the DICOM tags and convert into an image
					if file.name.endswith(".dcm"):
						try:
							# print(str(file))
							path = default_storage.save('tmp/' + file.name ,ContentFile(file.read()))
							temp_file = os.path.join(settings.MEDIA_ROOT,path)
							djangofile,accesstion_number,study_date, view_position,anatomy, height, width = read_dcm_file(temp_file,file.name)
							# #store the dicom file as DICOM file in the document and igore the file read by the read_dcm_file. TODO decide whether we need to render DICOM on demand
							djangofile = File(file)
							
							new_document = Document(allocated_to = selected_user,
							type=image_type,purpose= purpose, document=djangofile,
							 accession_no = accesstion_number, view_position = view_position, anatomy = anatomy, 
							 height = height, width = width)
							new_document.save()
							os.remove(temp_file)
						except Exception as ex:
							print(str(ex))
					else:

						djangofile = File(file)
 
						new_document = Document(allocated_to = selected_user,type=image_type,purpose= purpose, document=djangofile)
						new_document.save()
				return HttpResponseRedirect("/sianno/" )
			except Exception as ex_file:
				return HttpResponse("Error: " + str(ex_file))			 	
		return 
	else:
		return HttpResponse("Sorry, Not authorized")

from pydicom import dcmread
import io
import numpy as np
from PIL import Image


@login_required
def get_image(request):
	# http://localhost:8001/sianno/get_image/?document_id=10314
	#returns the image. 
	if request.method == "GET" :
		try:

			document_id = request.GET["document_id"]
			doc = Document.objects.get(id=document_id)
			if doc.document.name.endswith(".dcm"):
				#read the file as memory file and return as image. 
				ds = dcmread (settings.MEDIA_ROOT+ "/" + str(doc.document))
				image_2d = ds.pixel_array.astype(float)
				image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0
				image_2d_scaled = np.uint8(image_2d_scaled)
				response = HttpResponse()
				# response["Content-Type"] = "image/jpeg"
				response["Content-Type"] = "image/png"
				# format = "jpeg"
				format = "PNG"
				# image_byte = io.BytesIO()
				im = Image.fromarray(image_2d_scaled).convert("L").save(response, format=format)
				return response
				# with open(settings.MEDIA_ROOT+str(doc.document), "rb") as f:
		# 	return HttpResponse(f.read())
				# pass
			else:


				urlstring = "/media/"+str(doc.document)
				response = HttpResponseRedirect(urlstring)
				return response
		

		except Exception as e:
			print (e)
			response = HttpResponse("file error")
			return response
#when detect function is called, run bone detector for all the draft records		
@login_required()
def detect_bones(request):
	try:
		run_small_big_bone_detection()

		print("Detection algorithm was run successfully")
		return JsonResponse({"result":"OK"})
	except Exception as ex:

		return JsonResponse({"result": f"error: {ex}"})

#when detect function is called, run osteo detector for all the Completed records from the user "labler_bone"		
@login_required()
def detect_osteo(request):
	try:
		
		
		if create_new_documents_for_osteomyelitis() == True:


			print("Detection algorithm was run successfully")
			return JsonResponse({"result":"OK"})
		else:
			return JsonResponse({"result": "Program issue"})
	except Exception as ex:

		return JsonResponse({"result": f"error: {ex}"})

