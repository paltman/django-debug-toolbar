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
        return "%s errors/%s warnings" % (len(self.errors), len(self.warnings))

    def url(self):
        return ''

    def content(self):
        context = {"warnings": self.warnings, "errors": self.errors}
        return render_to_string('debug_toolbar/panels/validation.html', context)

    @property
    def warnings(self):
        if not hasattr(self, "_warnings"):
            self._warnings = [err for err in self.tidydoc.errors
                              if err.severity == 'W']
        return self._warnings

    @property
    def errors(self):
        if not hasattr(self, "_errors"):
            self._errors = [err for err in self.tidydoc.errors
                              if err.severity == 'E']
        return self._errors

    def process_response(self, request, response):
        import tidy
        self.tidydoc = tidy.parseString(response.content)

    def to_data(self):
        return {"errors": self.errors,
                "warnings": self.warnings}
