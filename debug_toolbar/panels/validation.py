import django
from django.template.loader import render_to_string

from debug_toolbar.panels import DebugPanel


class ValidationPanel(DebugPanel):
    """
    Panel that validates the output using lxml.
    """
    name = 'Validation'
    has_content = True

    def title(self):
        warnings = [err for err in self.tidydoc.errors if err.severity == 'W']
        errors = [err for err in self.tidydoc.errors if err.severity == 'E']
        return "%s errors/%s warnings" % (len(errors), len(warnings))

    def url(self):
        return ''

    def content(self):
        warnings = [err for err in self.tidydoc.errors if err.severity == 'W']
        errors = [err for err in self.tidydoc.errors if err.severity == 'E']
        context = {"warnings": warnings, "errors": errors}
        return render_to_string('debug_toolbar/panels/validation.html', context)

    def process_response(self, request, response):
        import tidy
        self.tidydoc = tidy.parseString(response.content)
