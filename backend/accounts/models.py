"""
Modèles de l'app accounts.

[Note pédagogique] On garde le modèle User standard de Django (simple et
robuste), et on lui ajoute un Profil 1-pour-1 pour les infos métier qui ne sont
pas dans User — ici `email_verified` (l'utilisateur a-t-il cliqué le lien de
confirmation envoyé par email ?).

Choix d'architecture « email = identifiant » : à l'inscription, on met
username = email (voir SignupSerializer). Le login se fait donc par email, sans
backend d'authentification custom. C'est le compromis le plus simple pour un
kit pédagogique (un vrai produit utiliserait souvent un User personnalisé avec
USERNAME_FIELD = 'email').
"""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Informations complémentaires attachées à un utilisateur."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    # Validation "soft" : le compte fonctionne même si l'email n'est pas vérifié,
    # mais un bandeau invite l'utilisateur à cliquer le lien de confirmation.
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile<{self.user.email or self.user.username}>"


def get_or_create_profile(user) -> Profile:
    """Récupère (ou crée) le profil d'un utilisateur.

    Pratique pour les comptes créés AVANT l'ajout du modèle Profile (ils n'ont
    pas encore de profil) : on le crée à la volée plutôt que de planter.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


class DataRequest(models.Model):
    """Journal des demandes d'exercice de droits RGPD — audit trail SAR (J3-bis).

    [Note pédagogique] Le RGPD impose la *redevabilité* (accountability, art. 5.2) :
    on doit pouvoir prouver qu'on a traité les demandes des personnes (droit
    d'accès art. 15, droit à la portabilité art. 20). On journalise donc chaque
    demande d'export ici. On utilise on_delete=SET_NULL + un snapshot de l'email :
    la trace d'audit SURVIT à la suppression du compte, avec un minimum de données.
    """

    class RequestType(models.TextChoices):
        EXPORT = "export", "Export des données (accès / portabilité)"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="data_requests",
    )
    user_email = models.EmailField(
        blank=True,
        help_text="Snapshot de l'email au moment de la demande (conservé même après suppression).",
    )
    request_type = models.CharField(
        max_length=20, choices=RequestType.choices, default=RequestType.EXPORT
    )
    export_format = models.CharField(max_length=8, default="json", help_text="json ou csv")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Demande RGPD (SAR)"
        verbose_name_plural = "Demandes RGPD (SAR)"

    def __str__(self) -> str:
        return f"{self.get_request_type_display()} — {self.user_email} — {self.created_at:%Y-%m-%d}"
