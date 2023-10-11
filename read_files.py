import os
from django.core.files import File
from retina_grader.models import Document, GlobalSettings, GradingField, Grading

from django.conf import settings
import random
import string
from django.contrib.auth.models import User
location = "/home/ubuntu/toread/"
for file in os.listdir(location):
	try:
		if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg") or file.lower().endswith(".png") :
			f = open(location+file, "rb")
			djangofile = File(f, name=file)
			user = User.objects.get(username=GlobalSettings.objects.get(key="default_allocated_user").value)


			random_string = "%s_%04d" % (
					list(string.ascii_uppercase)[random.randint(0, 25)], random.randint(0, 2000))
			d = Document(document=djangofile, random_id= random_string, allocated_to=user)
			d.save()


			for gf in GradingField.objects.all():
				Grading(grading_field=gf, document=d).save()


	except Exception as e:
		print(str(e))

