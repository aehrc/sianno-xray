# Sianno Wrist Fracture Grader


## 1. Create Virtual Environment (VE)
<br>

* Ensure python (v.3 or above) is installed
* In a terminal or cmd prompt, navigate (cd) into the directory where you want the VE to be placed.  

> `cd ~\my_venvs`

* Run the command:

> `py -m venv venv <your_VE_name>`

* It may take a minute.
* To activate the environment, navigate into the VE's parent folder and run the following:

> `\<your_VE_name>\Scripts\activate`

* You can deactivate the VE at anytime by running the command:

> `deactivate` 

<br>

## 2. Install the Required Python Libraries

<br>

*   Navigate to the simple_grader directory (note - sianno-xray-main is the branch name and may differ).  

>`cd ~\<grader file path>\sianno-xray-main`  

*   Install required libraries using the following command, making sure that the VE is activated:
> `pip install -r requirements.txt`
* Any conflicts that arise from the release of new versions can rear themselves here - troublesome or conflicting versions can be updated appropriately in requirements.txt to resolve them.

<br>

## 3. Update Media Root

<br>

* Open the simple_grader in an IDE. The author is using Visual Studio Code.
* In `\simple_grader\simple_grader\` open the settings.py file.
* Change the MEDIA_ROOT variable to the path where you want to store the wrist-fracture images and their annotation .JSON files.

* Alternatively, create a new settings file (or use the template settings_user.py), import all from settings.py (`from .settings import *`) and override the MEDIA_ROOT:

>`1 from .settings import *`

>`2 MEDIA_ROOT = "/<media file path>/grader_images"` 

* For more information on Django settings, see the [settings page](https://docs.djangoproject.com/en/4.0/topics/settings/ "Django Tutorial") of the Django Documentation.

<br>

## 4. Run the Simple Grader

<br>

* The simple grader is run using the Python web framework Django.
* From the IDE terminal - with the VE activated - run the simple_grader server using the following command:
>`py manage.py runserver`
* The terminal will output the port that the server is running on.  If the 8000 port (the default port) is in use, or you want to elect a different starting port, add the desired port to the runserver command:

>`py manage.py runserver 8080`

* If a separate settings file is to be used, specify it like so; note that the command is in python sytax so the '.py' file extension will need to be ommitted from the settings filename:
 > `py manage.py runserver 8080 --settings=simple_grader.<settings filename>` 
* For more information see the [Django Tutorial](https://docs.djangoproject.com/en/4.0/topics/settings/ "Django Tutorial").

* Navigate to the Sianno homepage by following the IP:Port address, followed by '/sianno'; for example, 127.0.0.1:8080/sianno

<br>

## 5. Credentials

<br>

* Log in using the following credentials:
    *   Username: Superuser
    *   Password: Superuser    
* A new user account can be created via the admin page.  This can be accessed by navigating to the server address followed by '/admin'; for example, 127.0.0.1:8080/admin.

<br>

## 6. Using the Grader

The Sianno index page displays a draft list and a reviewed list.  All un-annotated images are listed under the Drafts heading; all annotated images are listed under the Reviewed section.  Images can be uploaded by accessing the Actions dropdown list in the top right corner.
<br>

Once an image has been uploaded it will appear in the Draft list.  Select it to be redirected to the annotation page (sianno/detail). Images can be annotated either using a Rectangular tool or a Polygon tool.  To change between the two, open `/retina_grader/views.py`.  Under the `def detail(request)` function, assign the `annotation` to either 'rect' or 'poly' (remember to ctrl-s).
<br>

Using the rectangle tool, click and drag to begin drawing.  Click again to set the rectangle.  The rectangle can be moved by clicking and dragging, and it can be resized by clicking and dragging on the circles on the top-left and bottom-right of the rectangle. Double-clicking on the rectangle will bring up a modal that allows bone number annotation.  
<br>
Using the polygon tool, click on the 'Draw Polygon' button to begin annotation. To close the polygon, hold shift and click.  To delete the polygon, select it (it will be highlighted when selected) and press the 'Delete Selected' button.  Double-click on the polygon to annotate the bone number from the modal menu.  


## 7. Using the Django Database

For information about querying the database, read the Django documentation [here](https://docs.djangoproject.com/en/4.0/topics/db/queries/ "Making Queries").


### 7.1 Delete documents 
All Polygon, Rectangle, Point, and Grading objects are linked by foreign key with a Document object (see `retina_grader/models.py`), and delete on cascade when the corresponding Document object is deleted.  To delete documents for a clean start, do the following:

* Start the python shell from the program terminal:  `py manage.py shell`
* Import models:   `from retina_grader.models import *`
* Select all documents: `Document.objects.all()`
* Delete all documents: `Document.objects.all().delete()`

It's a good idea to also manually delete documents and .json files from your media folder.

# FRCNN Integration Branch

Use this branch for development of the FRCNN integration. Work done so far:

* Added a new Purpose attribute to the Wrist Fracture Document object (found in models): Assessing.
* When 'Upload' is selected from the 'Actions' dropdown menu, the image 'Assessing' purpose can now be selected.
* The uploaded file will appear on the 'Drafts' list with purpose listed as 'Assessing'.  Normally when the file is clicking on in the drafts list the `def detail` view will save the image locally with `write_docs(doc)` and then redirect to the `sianno/detail/?d=...` page where it can be annotated. 
