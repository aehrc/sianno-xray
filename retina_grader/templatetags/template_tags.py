
"""
@author : Janardhan Vignarajan

@copyright: www.aehrc.com

@organization: AEHRC.COM

@summary: custom filter tag to check if permission exists




"""



from django import template
from django.contrib.auth.models import Group
from django.utils.html import mark_safe
register = template.Library()

import datetime



@register.filter(name='is_enabled')
def is_enabled(value, arg):
    """

    :param value: the variable which would be tested
    :param arg: is the actual permission object
    :return:returns true or false if the value is found in the permission table passed
    """

    """checks the permission variable model and see if it can access the data"""

    for p in arg:
        if ( value== str(p.allowed_view)+":"+str(p.allowed_view_action)):
            return True

    return False

@register.filter(name='is_in_group')
def is_in_group(value, arg):
    """

   :param value: the variable which would be tested
   :param arg: is the actual permission object
   :return: true or false if the user is in group
   """

    try:
       group = Group.objects.get(name=arg)
       if group in value.groups.all():
           return True
       else:
           return False
    except:
        return False



@register.filter(name="get_yes_no")
def get_yes_no(value):


    try:
        if value:
            return mark_safe("<span class='glyphicon glyphicon-ok'></span>")
    except:
        pass
    return mark_safe("<span class='glyphicon glyphicon-remove'></span>")


@register.filter(name="get_yes_no_consent")
def get_yes_no_consent(value):


    try:
        if value:
            return "Yes"
    except:
        pass
    return "No"



@register.filter(name="subtract")
def subtract(value,arg):

    try:
        return int(value) - int(arg)
    except Exception as ex:
        #print(ex)
        return 0

@register.filter(name="dictKeyLookup")
def dictKeyLookup(the_dict, key):
   # Try to fetch from the dict, and if it's not found return an empty string.
   return the_dict.get(key, '')



@register.filter(name="joinArray")
def joinArray(array, arg):
    return arg.join(str(i) for i in array)


@register.filter(name="addCSS")
def addCSS(field,css):
    return field.as_widget(attrs={"class":css})

from urllib.parse import unquote
@register.filter(name="unquote_string")

def unquote_string(value):
    return unquote(value)


@register.filter(name="get_yes_no_2")
def get_yes_no_2(value):


    try:
        if value in ["1","true"] :
            return "Yes"
        else:
            return "No"
    except:
        pass
    return "Not Available"
#processes the ack message from HIH and returns true if it has ACK, if not returns false
@register.filter(name="process_hih_ack")
def process_hih_ack(value):
    if value == None or value == "":
        return "red"
    try:

        if str(value).replace("HIH Return:", "").split("|")[8] == "ACK^T02":
            return "green"


    except :
        return "red"
    return "red"

# processes the ack message from MPS and returns true if it has HTTP 201, if not returns false
@register.filter(name="process_mps_ack")
def process_mps_ack(value):
    if value == None or value == "":
        return "red"
    try:

        if str(value).replace("MPS Return:", "").split(";")[0] == "HTTP201":
            return "green"


    except:
        return "red"
    return "red"

@register.filter(name="get_voided_class")
def get_voided_class(value):
    if value.voided == True:
        return 'void-page-overlay'
    else:
        return ''


        # Consent
    # Form: HIH
    # Return:MSH | ^ ~\ & | EnsembleHL7 | ISC | MICE ^ ^ L | 0106 ^ HdwaMedicalFacility
    # .0106 ^ L | 202001230752 | | ACK ^ T02 | MICE
    # .0106.CF
    # .5
    # SotJPURQE6a50zMH2RxPg | D ^ T | 2.6
    # MSA | CA | MICE
    # .0106.CF
    # .5
    # SotJPURQE6a50zMH2RxPg  Visit
    # Report: Images: MPS
    # Return:HTTP201;
    # Response
    # Text:{"id": 88, "username": "wabaapi", "reference": "L5900476", "created_at": 1579737125, "stage": "PENDING",
    #       "status": null, "status_text": nu
