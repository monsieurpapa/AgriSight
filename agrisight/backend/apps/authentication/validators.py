import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """
    Enforce minimum complexity: upper, lower, number.
    """

    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password or ""):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code="password_no_upper",
            )
        if not re.search(r"[a-z]", password or ""):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code="password_no_lower",
            )
        if not re.search(r"[0-9]", password or ""):
            raise ValidationError(
                _("Password must contain at least one number."),
                code="password_no_number",
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter, one lowercase letter, and one number.")
