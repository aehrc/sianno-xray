from django.contrib import admin
# Register your models here.
from .models import Grading, GradingType, GradingValueSet, GradingField, Document, GlobalSettings, Rectangle

class DocumentAdmin(admin.ModelAdmin):
	#readonly_fields = ['random_id']
	fields = ["document", "status", "allocated_to", "random_id", "type", "purpose", "accession_no","view_position","anatomy","scale", "width", "height"]
	list_max_show_all = 2000


admin.site.register(Grading)
admin.site.register(GradingType)
admin.site.register(GradingValueSet)
admin.site.register(GradingField)
admin.site.register(Document, DocumentAdmin)

admin.site.register(GlobalSettings)
admin.site.register(Rectangle)
