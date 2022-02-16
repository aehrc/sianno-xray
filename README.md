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

*   Navigate to the simple_grader directory.  

>`cd ~\<grader file path>\simple_grader`  

*   Install required libraries using the following command, making sure that the VE is activated:
> `pip install -r requirements.txt`
* Any conflicts that arise from the release of new versions will rear themselves here - update the versions appropriately in requirements.txt to resolve them.

<br>

## 3. Update Media Root

<br>

* Open the simple_grader in an IDE. The author is using Visual Studio Code.
* In `\simple_grader\simple_grader\` open the settings.py file.
* Change the MEDIA_ROOT variable to the path where you want to store the wrist-fracture images and their annotation .JSON files.

* Alternatively, create a new settings file, import all from settings.py (`from .settings import *`) and override the MEDIA_ROOT:

>`1 from .settings import *`

>`2 MEDIA_ROOT = "/<media file path>/grader_images"`

 * Then, select the settings file required using the following command - being sure to omit the `.py` file extension from the settings filename.
 > `py manage.py runserver 8080 --settings simple_grader.<settings file name>` 

* For more information on Django settings, see the [settings page](https://docs.djangoproject.com/en/4.0/topics/settings/ "Django Tutorial") of the Django Documentation.

<br>

## 4. Run the Simple Grader

<br>

* The simple grader is run using the Python web framework Django.
* From the terminal, with the VE activated, run the simple_grader server using the following command:
>`py manage.py runserver`
* The terminal will output the port that the server is running on.  If the 8000 port (the default port) is in use, or you want to elect a different starting port, add the desired port to the runserver command:

>`py manage.py runserver 8080`
* For more information see the [Django Tutorial](https://docs.djangoproject.com/en/4.0/intro/tutorial01/ "Django Tutorial").

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

Images can be annotated either using a Rectangular tool or a Polygon tool.  To change between the two, open `/simple_grader/retina_grader/views.py`.  Under the `def detail(request)` function, assign the `annotation` to either 'rect' or 'poly'.
<br>

A couple of notes on the annotation tools:
* Double-clicking on a rectangle or polygon will allow the user to add/change the text annotation. 
* When drawing using the polygon annotation tool, hold shift and click to close the polygon. 
* Click a polygon (or rectangle PENDING) to select it (it will be highlighted), and use the 'Delete Selected' button to remove it.

## 7. Using the Django Database

For information about querying the database, read the Django documentation [here](https://docs.djangoproject.com/en/4.0/topics/db/queries/ "Making Queries").


### 7.1 Delete documents 
All Polygon, Rectangle, Point, and Grading objects are linked by foreign key with a Document object (see `retina_grader/models.py`), and delete on cascade when the corresponding Document object is deleted.  To delete documents for a clean start, do the following:

* Start the python shell from the program terminal:  `py manage.py shell`
* Import models:   `from retina_grader.models import *`
* Select all documents: `Documents.objects.all()`
* Delete all documents: `Documents.objects.all().delete()`

It's a good idea to also manually delete documents and .json files from your media folder.

 
