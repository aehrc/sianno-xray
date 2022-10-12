from re import X
import uuid

from django.forms.widgets import DateInput
from django.db import models
from django.contrib.auth.models import User

from django.core.files.storage import FileSystemStorage
from django.conf import settings


GRADING_STATUS_CHOICES = (
('Inactive','Inactive'),
('Active','Active'),

)
#I am adding a line of comment

#DOCUMENT TYPES
DOCUMENT_TYPES = (('BITEWING','BITEWING'),
				 ('PANAROMIC','PANAROMIC'),
				
					)


#PURPOSE TYPES
PURPOSE_TYPES = (('SCREENING','SCREENING'),
				 ('GRADING','GRADING'),
				
					)
#UI types
UI_CONTROL_TYPES = (('Label','Label'),
				 ('Radio','Radio'),
				 ('CheckBox','CheckBox'),
				 ('Text','Text'),
				 ('Select','Select'),
				 ('Date','Date'),
					('number','number'),
					('TextArea', 'TextArea'),

					)

VALUE_SET_CHOICES = (
	('Yes','Yes'),
	('No','No'),
	('Type I','Type I'),
	('Type II','Type II'),
	('Gestational','Gestational'),
	('Other','Other'),
	('Smoker','Smoker'),
	('Ex Smoker','Ex Smoker'),
	('Non Smoker','Non Smoker'),
	('Diabetic Laser','Diabetic Laser'),
	('Other Ocular Laser','Other Ocular Laser'),
	('No Laser', 'No Laser'),

	('6/60','6/60'),
	('6/36','6/36'),
	('6/24','6/24'),
	('6/18','6/18'),
	('6/9','6/9'),
	('6/6','6/6'),
	('6/5','6/5'),
	('CF','CF'),
	('HM','HM'),
	('LP','LP'),
	('NLP','NLP'),

	('Mild NPDR','Mild NPDR'),#DR
	('Moderate NPDR','Moderate NPDR'),#DR
	('Severe NPDR','Severe NPDR'),#DR
	('PDR','PDR'),#DR
	('No DR','No DR'),#DR
	('Unable to grade','Unable to grade'),#DR
	('Present','Present'), #DMO
	('None','None'), #DMO

	('Repeat photos in 24 months','Repeat photos in 2 years'),#Recommendation
	('Repeat photos in 1 year','Repeat photos in 1 year'),#Recommendation
	('Repeat photos in 6 months','Repeat photos in 6 months'),#Recommendation

	('Review in clinic','Review in clinic'),#Recommendation

	('Not Applicable','Not Applicable'),#Not applicable for other items

	('1 Week','1 Week'),
	('1 Month','1 Month'),
	('3 Months','3 Months'),
	('1 Year','1 Year'),

	('Not Recorded','Not Recorded'),
	('Left','Left'),
	('Right', 'Right'),

	('Good', 'Good'),
	('Poor', 'Poor'),
	('Moderate', 'Moderate'),

	('Correct', 'Correct'),
	('Incorrect', 'Incorrect'),	

)

#store the image under user's name
def get_file_location_path(instance, filename):
	print("FILE LOCATION: " + 'document_tray/{0}/{1}'.format(instance.allocated_to.username, filename))	
	return 'document_tray/{0}/{1}'.format(instance.allocated_to.username, filename)


# Create your models here.
class GradingType(models.Model):
	"""
	Model to hold grading history types. These are collection of predefined grading fields set by the administrator
	Each of these types can be of different user interface control types : eg: L/R is a is a drop down.
	"""

	#id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	text = models.CharField(max_length=200)
	ui_control_type = models.CharField( max_length = 20,  default = "Text", choices = UI_CONTROL_TYPES)
	ui_order = models.IntegerField(default=0) #ordering field which manages the user interface order

	#options = models.CharField( max_length = 300, default = "")#Semicolon seperated values based


	def __str__(self):
		return "%s" % (self.text)



class GradingField(models.Model):
	"""
	Model to hold grading field. Eg  a grading field which is of a gradig type and with

	"""
	#id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	grading_type = models.ForeignKey(GradingType, on_delete = models.CASCADE)
	comments =  models.CharField(max_length = 100, default="admin comment")
	is_monitorred = models.BooleanField(default= False)
	default_value = models.CharField(max_length = 100, default="admin comment")
	def __str__(self):
		return "%s" % (self.grading_type)

class Document(models.Model):
	"""Model to hold the actual document.
	"""
	# document = models.FileField(upload_to="document_tray/")
	type = models.CharField(max_length = 20, blank=True, null=True, choices=DOCUMENT_TYPES)
	width = models.PositiveIntegerField(blank=True, null=True)
	height = models.PositiveIntegerField(blank=True, null=True)

	scale = models.DecimalField(max_digits=16, decimal_places=12, default=1.0)
	document = models.ImageField(blank=True, null=True,
		height_field='height',
		width_field='width',
		storage=FileSystemStorage(location=settings.MEDIA_ROOT),
		upload_to=get_file_location_path)

	status =  models.CharField(max_length = 20, default="Draft")
	allocated_to = models.ForeignKey(User, on_delete = models.CASCADE, null=True )
	random_id =  models.CharField(max_length = 20, default="UNASSIGNED")
	purpose =  models.CharField(max_length = 20, blank=True, null=True, choices=PURPOSE_TYPES)
	date_added = models.DateTimeField(null=True, auto_now_add=True)
	date_modified = models.DateTimeField(null=True, auto_now=True)

	#Additional information regarding patient
	patient_id = models.CharField(max_length = 20, default="UNASSIGNED")#patient ID
	accession_no = models.CharField(max_length = 100, default="UNASSIGNED")#accession number
	view_position =  models.CharField(max_length = 100, default="UNASSIGNED")#accession number

	class Meta:
		if settings.USE_RANDOM_ID : 
			ordering = ['random_id']

		else:
			ordering = ['document']

	def __str__(self):
		if settings.USE_RANDOM_ID : 
			return "ID: %s | Allocated To: %s | Status: %s" % (self.random_id, self.allocated_to, self.status)
		else:
			return "ID: %s | Allocated To: %s | Status: %s" % (self.document.name, self.allocated_to, self.status)

class Rectangle(models.Model):
	document = models.ForeignKey(Document, on_delete = models.CASCADE)
	r_id = models.PositiveIntegerField(null=True, blank=True)
	x = models.FloatField(null=True, blank=True)
	y = models.FloatField(null=True, blank=True)
	width = models.FloatField(null=True, blank=True)
	height = models.FloatField(null=True, blank=True)
	'''
	tooth = models.TextField(null=True, blank=True, default = "unknown")
	site = models.CharField(max_length = 200, verbose_name = "Site of Caries", default = "Occlusal", blank = True, null=True)
	depth = models.CharField(max_length = 200, verbose_name = "Depth of Caries", default = "Enamel up to DEJ", blank = True, null=True)
	eruption = models.CharField(max_length = 200, verbose_name = "Eruption Status", default = "Erupted", blank = True, null=True)
	Supernumerary = models.CharField(max_length = 200, verbose_name = "Supernumerary Tooth", default = "None", blank = True, null=True)'''

	#fields for wrist xray
	bone_number = models.CharField(max_length=50,null=True, blank=True, default = "unknown")
	fracture_on_current_view = models.CharField(max_length=20,null=True, blank=True, default = "No")
	fracture_on_other_view = models.CharField(max_length=20,null=True, blank=True, default = "No")
	view_type = models.CharField(max_length=20,null=True, blank=True, default = "unknown")

# a polygon attached to a document object via ForeignKey.  In case of multiple polygons, the point coordinates are
# stored in seperate class, Point
class Polygon(models.Model):
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	idx = models.IntegerField(null=True,blank=True)

	#fields for wrist xray
	bone_number = models.CharField(max_length=50,null=True, blank=True, default = "unknown")
	fracture_on_current_view = models.CharField(max_length=20,null=True, blank=True, default = "No")
	fracture_on_other_view = models.CharField(max_length=20,null=True, blank=True, default = "No")
	view_type = models.CharField(max_length=20,null=True, blank=True, default = "unknown")
	
# polygon point - with Polygon FK
class Point(models.Model):
	polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE)
	x = models.FloatField(null=True, blank=True)
	y = models.FloatField(null=True, blank=True)
	idx = models.IntegerField(null=True, blank=True)

class Grading(models.Model):
	"""
	Model to hold the actual Grading. This binds the grading to the document and other details. This field and will hold values.

	"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


	grading_field = models.ForeignKey(GradingField, on_delete = models.CASCADE)
	document = models.ForeignKey(Document, on_delete = models.CASCADE)
	date = models.DateField(verbose_name="Date of onset", blank=True, null=True)#start date of the onset
	value = models.CharField(max_length=200 ,verbose_name="Observed values (if any)", blank=True, null= True, default = "Not Recorded")

	class Meta:
		ordering = ['-grading_field__grading_type__ui_order']#set the ordering field to this


class GradingValueSet(models.Model):
	"""

	Model to hold values for each grading for the grading type.
	Each medical history type can have possible values. Eg: Diabetic Type should have Type1, TypeII as values


	"""
	#id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	grading_type = models.ForeignKey(GradingType, on_delete = models.CASCADE)
	value = models.CharField(max_length=200, choices = VALUE_SET_CHOICES)



class GlobalSettings(models.Model):
	key =  models.CharField(max_length = 100)
	value = models.CharField(max_length=500)
