from django.forms.renderers import TemplatesSetting


class VanillaFormRenderer(TemplatesSetting):
    form_template_name = 'core/forms/form.html'
