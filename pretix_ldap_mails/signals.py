import ldap
from collections import OrderedDict
from django import forms
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from ldap.filter import escape_filter_chars
from pretix.base.services.orders import OrderError
from pretix.base.signals import register_global_settings, validate_order


@receiver(validate_order, dispatch_uid="ldap_mails_email_validator")
def validate_order(sender, **kwargs):
    email = escape_filter_chars(kwargs["email"])
    ldap_connection = ldap.initialize(
        sender.organizer.settings.get("ldap_mails_ldap_server")
    )
    ldap_connection.simple_bind_s(
        sender.organizer.settings.get("ldap_mails_ldap_user"),
        sender.organizer.settings.get("ldap_mails_ldap_password"),
    )
    # Search for user by email
    result = ldap_connection.search_s(
        sender.organizer.settings.get("ldap_mails_ldap_base"),
        ldap.SCOPE_SUBTREE,
        "(mail={})".format(email),
    )
    if len(result) == 0:
        raise OrderError(_("Email {} is not allowed to order.").format(email))


@receiver(register_global_settings, dispatch_uid="ldap_mails_settings")
def register_global_settings(sender, **kwargs):
    return OrderedDict(
        [
            (
                "ldap_mails_ldap_server",
                forms.CharField(
                    label=_("LDAP server for mail verification"),
                    required=False,
                ),
            ),
            (
                "ldap_mails_ldap_user",
                forms.CharField(
                    label=_("LDAP dn for query user for mail verification"),
                    required=False,
                ),
            ),
            (
                "ldap_mails_ldap_password",
                forms.CharField(
                    label=_("LDAP password for query user for mail verification"),
                    required=False,
                ),
            ),
            (
                "ldap_mails_ldap_base",
                forms.CharField(
                    label=_("LDAP base containing users for mail verification"),
                    required=False,
                ),
            ),
        ]
    )
