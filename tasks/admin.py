from django.contrib import admin

from .models import ExportRun, ExportTask

class ExportRunAdmin(admin.ModelAdmin):
    pass


class ExportTaskAdmin(admin.ModelAdmin):
    pass

# register the new admin models
admin.site.register(ExportRun, ExportRunAdmin)
admin.site.register(ExportTask, ExportTaskAdmin)
