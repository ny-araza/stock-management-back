# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class PollsArticle(models.Model):
    id = models.BigAutoField(primary_key=True)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()

    class Meta:
        managed = False
        db_table = 'polls_article'


class TAcces(models.Model):
    acc_id = models.AutoField(db_column='acc_Id', primary_key=True)  # Field name made lowercase.
    acc_code = models.CharField(unique=True, max_length=25, blank=True, null=True)
    acc_desc = models.CharField(max_length=100, blank=True, null=True)
    acc_enabled = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_acces'


class TArticle(models.Model):
    art_id = models.AutoField(db_column='art_Id', primary_key=True)  # Field name made lowercase.
    art_code = models.CharField(db_column='art_Code', max_length=25)  # Field name made lowercase.
    art_nom = models.CharField(db_column='art_Nom', max_length=155, blank=True, null=True)  # Field name made lowercase.
    art_datecre = models.DateTimeField(db_column='art_DateCre', blank=True, null=True)  # Field name made lowercase.
    art_datemdf = models.DateTimeField(db_column='art_DateMdf', blank=True, null=True)  # Field name made lowercase.
    art_usercre = models.CharField(db_column='art_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    art_usermdf = models.CharField(db_column='art_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    art_poids = models.DecimalField(db_column='art_Poids', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    art_taille = models.DecimalField(db_column='art_Taille', max_digits=10, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    art_stockmini = models.IntegerField(db_column='art_StockMini', blank=True, null=True)  # Field name made lowercase.
    art_enabled = models.IntegerField(blank=True, null=True)
    art_fam_id = models.IntegerField(db_column='art_fam_Id', blank=True, null=True)  # Field name made lowercase.
    art_sof_id = models.IntegerField(db_column='art_sof_Id', blank=True, null=True)  # Field name made lowercase.
    art_codebarre = models.CharField(db_column='art_CodeBarre', max_length=100, blank=True, null=True)  # Field name made lowercase.
    art_lot_id = models.IntegerField(db_column='art_lot_Id', blank=True, null=True)  # Field name made lowercase.
    art_stockable = models.IntegerField(db_column='art_Stockable', blank=True, null=True)  # Field name made lowercase.
    art_marque = models.CharField(db_column='art_Marque', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_article'


class TAutorisation(models.Model):
    aut_id = models.AutoField(db_column='aut_Id', primary_key=True)  # Field name made lowercase.
    aut_acc_code = models.CharField(max_length=25, blank=True, null=True)
    aut_men_code = models.IntegerField(blank=True, null=True)
    aut_usermdf = models.CharField(db_column='aut_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    aut_datemdf = models.DateTimeField(db_column='aut_DateMdf', blank=True, null=True)  # Field name made lowercase.
    aut_acces = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_autorisation'


class TBillet(models.Model):
    bil_id = models.AutoField(db_column='bil_Id', primary_key=True)  # Field name made lowercase.
    bil_codecaisse = models.CharField(db_column='bil_codeCaisse', max_length=25, blank=True, null=True)  # Field name made lowercase.
    bil_billet = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    bil_nombre = models.IntegerField(blank=True, null=True)
    bil_somme = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    bil_ttnb = models.DecimalField(db_column='bil_ttNb', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    bil_ttsum = models.DecimalField(db_column='bil_ttSum', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    bil_date = models.DateField(blank=True, null=True)
    bil_datecre = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_billet'


class TCaisse(models.Model):
    cas_id = models.AutoField(db_column='cas_Id', primary_key=True)  # Field name made lowercase.
    cas_code = models.CharField(db_column='cas_Code', max_length=25)  # Field name made lowercase.
    cas_datecre = models.DateTimeField(db_column='cas_DateCre', blank=True, null=True)  # Field name made lowercase.
    cas_datemdf = models.DateTimeField(db_column='cas_DateMdf', blank=True, null=True)  # Field name made lowercase.
    cas_usercre = models.CharField(db_column='cas_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cas_usermdf = models.CharField(db_column='cas_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cas_date = models.DateField(db_column='cas_Date', blank=True, null=True)  # Field name made lowercase.
    cas_datedeb = models.DateTimeField(db_column='cas_Datedeb', blank=True, null=True)  # Field name made lowercase.
    cas_datefin = models.DateTimeField(db_column='cas_Datefin', blank=True, null=True)  # Field name made lowercase.
    cas_valide = models.IntegerField(blank=True, null=True)
    cas_recette = models.DecimalField(db_column='cas_Recette', max_digits=18, decimal_places=2)  # Field name made lowercase.
    cas_depense = models.DecimalField(db_column='cas_Depense', max_digits=18, decimal_places=2)  # Field name made lowercase.
    cas_solde = models.DecimalField(db_column='cas_Solde', max_digits=18, decimal_places=2)  # Field name made lowercase.
    cas_fond = models.DecimalField(max_digits=18, decimal_places=2)
    cas_lettre = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_caisse'


class TClient(models.Model):
    cli_id = models.AutoField(db_column='cli_Id', primary_key=True)  # Field name made lowercase.
    cli_code = models.CharField(db_column='cli_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    cli_nom = models.CharField(db_column='cli_Nom', max_length=155, blank=True, null=True)  # Field name made lowercase.
    cli_datecre = models.DateTimeField(db_column='cli_DateCre', blank=True, null=True)  # Field name made lowercase.
    cli_datemdf = models.DateTimeField(db_column='cli_DateMdf', blank=True, null=True)  # Field name made lowercase.
    cli_usercre = models.CharField(db_column='cli_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cli_usermdf = models.CharField(db_column='cli_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cli_tel1 = models.CharField(db_column='cli_Tel1', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cli_tel2 = models.CharField(db_column='cli_Tel2', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cli_adresse = models.CharField(db_column='cli_Adresse', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cli_enabled = models.IntegerField(blank=True, null=True)
    cli_email = models.CharField(db_column='cli_Email', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cli_modepay = models.CharField(db_column='cli_ModePay', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cli_nif = models.CharField(max_length=50, blank=True, null=True)
    cli_stat = models.CharField(max_length=50, blank=True, null=True)
    cli_rcs = models.CharField(max_length=45, blank=True, null=True)
    cli_type = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_client'


class TCmdFournis(models.Model):
    cmf_id = models.AutoField(db_column='cmf_Id', primary_key=True)  # Field name made lowercase.
    cmf_code = models.CharField(db_column='cmf_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    cmf_datecre = models.DateTimeField(db_column='cmf_DateCre', blank=True, null=True)  # Field name made lowercase.
    cmf_datemdf = models.DateTimeField(db_column='cmf_DateMdf', blank=True, null=True)  # Field name made lowercase.
    cmf_usercre = models.CharField(db_column='cmf_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cmf_usermdf = models.CharField(db_column='cmf_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cmf_date = models.DateField(db_column='cmf_Date')  # Field name made lowercase.
    cmf_modecmd = models.CharField(db_column='cmf_ModeCmd', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cmf_dateliv = models.DateField(db_column='cmf_DateLiv', blank=True, null=True)  # Field name made lowercase.
    cmf_enabled = models.IntegerField(blank=True, null=True)
    cmf_montant_ht = models.DecimalField(db_column='cmf_Montant_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    cmf_montant_ttc = models.DecimalField(db_column='cmf_Montant_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    cmf_islivre = models.IntegerField(db_column='cmf_isLivre', blank=True, null=True)  # Field name made lowercase.
    cmf_fou_code = models.CharField(db_column='cmf_fou_Code', max_length=25)  # Field name made lowercase.
    cmf_lettre = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_cmd_fournis'


class TCode(models.Model):
    cod_id = models.AutoField(db_column='cod_Id', primary_key=True)  # Field name made lowercase.
    cod_table = models.CharField(db_column='cod_Table', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cod_num = models.CharField(db_column='cod_Num', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cod_annee = models.IntegerField(db_column='cod_Annee', blank=True, null=True)  # Field name made lowercase.
    cod_mois = models.IntegerField(db_column='cod_Mois', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_code'


class TCritere(models.Model):
    cri_id = models.AutoField(db_column='cri_Id', primary_key=True)  # Field name made lowercase.
    cri_code = models.CharField(db_column='cri_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    cri_desc = models.CharField(db_column='cri_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_critere'


class TDepense(models.Model):
    dep_id = models.AutoField(db_column='dep_Id', primary_key=True)  # Field name made lowercase.
    dep_date = models.DateField(blank=True, null=True)
    dep_desc = models.CharField(max_length=255, blank=True, null=True)
    dep_datecre = models.DateTimeField(db_column='dep_DateCre', blank=True, null=True)  # Field name made lowercase.
    dep_datemdf = models.DateTimeField(db_column='dep_DateMdf', blank=True, null=True)  # Field name made lowercase.
    dep_usercre = models.CharField(db_column='dep_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    dep_usermdf = models.CharField(db_column='dep_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    dep_montant = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    dep_type = models.CharField(max_length=100, blank=True, null=True)
    dep_mode = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_depense'


class TEntree(models.Model):
    ent_id = models.AutoField(db_column='ent_Id', primary_key=True)  # Field name made lowercase.
    ent_code = models.CharField(db_column='ent_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    ent_datecre = models.DateTimeField(db_column='ent_DateCre', blank=True, null=True)  # Field name made lowercase.
    ent_datemdf = models.DateTimeField(db_column='ent_DateMdf', blank=True, null=True)  # Field name made lowercase.
    ent_usercre = models.CharField(db_column='ent_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    ent_usermdf = models.CharField(db_column='ent_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    ent_fou_code = models.CharField(db_column='ent_fou_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ent_date = models.DateField(db_column='ent_Date')  # Field name made lowercase.
    ent_facture = models.CharField(db_column='ent_Facture', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ent_datepay = models.DateField(db_column='ent_DatePay', blank=True, null=True)  # Field name made lowercase.
    ent_modepaye = models.CharField(db_column='ent_ModePaye', max_length=20)  # Field name made lowercase.
    ent_dateecheance = models.DateField(db_column='ent_DateEcheance', blank=True, null=True)  # Field name made lowercase.
    ent_montant_ht = models.DecimalField(db_column='ent_Montant_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    ent_montant_ttc = models.DecimalField(db_column='ent_Montant_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    ent_cmf_code = models.CharField(db_column='ent_cmf_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_entree'


class TEntreprise(models.Model):
    etp_id = models.AutoField(db_column='etp_Id', primary_key=True)  # Field name made lowercase.
    etp_nom = models.CharField(max_length=50)
    etp_adresse = models.CharField(max_length=50, blank=True, null=True)
    etp_ville = models.CharField(max_length=50, blank=True, null=True)
    etp_quartier = models.CharField(max_length=50, blank=True, null=True)
    etp_codepostal = models.IntegerField(db_column='etp_codePostal', blank=True, null=True)  # Field name made lowercase.
    etp_mobile = models.CharField(max_length=25, blank=True, null=True)
    etp_fixe = models.CharField(max_length=25, blank=True, null=True)
    etp_fax = models.CharField(max_length=25, blank=True, null=True)
    etp_nif = models.CharField(db_column='etp_Nif', max_length=50, blank=True, null=True)  # Field name made lowercase.
    etp_stat = models.CharField(max_length=50, blank=True, null=True)
    etp_activite = models.CharField(max_length=50, blank=True, null=True)
    etp_siteweb = models.CharField(db_column='etp_siteWeb', max_length=50, blank=True, null=True)  # Field name made lowercase.
    etp_codebanque = models.CharField(db_column='etp_codeBanque', max_length=100, blank=True, null=True)  # Field name made lowercase.
    etp_logo = models.TextField(blank=True, null=True)
    etp_mail = models.CharField(db_column='etp_Mail', max_length=50, blank=True, null=True)  # Field name made lowercase.
    etp_banque = models.CharField(max_length=20, blank=True, null=True)
    etp_isdateperimp = models.IntegerField(db_column='etp_isDatePerImp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_entreprise'


class TEnumeration(models.Model):
    enu_id = models.AutoField(db_column='enu_Id', primary_key=True)  # Field name made lowercase.
    enu_code = models.CharField(db_column='enu_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    enu_nom = models.CharField(db_column='enu_Nom', max_length=155, blank=True, null=True)  # Field name made lowercase.
    enu_datecre = models.DateTimeField(db_column='enu_DateCre', blank=True, null=True)  # Field name made lowercase.
    enu_datemdf = models.DateTimeField(db_column='enu_DateMdf', blank=True, null=True)  # Field name made lowercase.
    enu_usercre = models.CharField(db_column='enu_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    enu_usermdf = models.CharField(db_column='enu_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    enu_decription = models.CharField(db_column='enu_Decription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    enu_order = models.IntegerField(db_column='enu_Order')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_enumeration'


class TFamille(models.Model):
    fam_id = models.AutoField(db_column='fam_Id', primary_key=True)  # Field name made lowercase.
    fam_code = models.CharField(db_column='fam_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    fam_nom = models.CharField(db_column='fam_Nom', max_length=155, blank=True, null=True)  # Field name made lowercase.
    fam_datecre = models.DateTimeField(db_column='fam_DateCre', blank=True, null=True)  # Field name made lowercase.
    fam_datemdf = models.CharField(db_column='fam_DateMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    fam_usercre = models.CharField(db_column='fam_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    fam_usermdf = models.CharField(db_column='fam_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    fam_enabled = models.IntegerField(db_column='fam_Enabled', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_famille'


class TFournis(models.Model):
    fou_id = models.AutoField(db_column='fou_Id', primary_key=True)  # Field name made lowercase.
    fou_code = models.CharField(db_column='fou_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    fou_nom = models.CharField(db_column='fou_Nom', max_length=155, blank=True, null=True)  # Field name made lowercase.
    fou_datecre = models.DateTimeField(db_column='fou_DateCre', blank=True, null=True)  # Field name made lowercase.
    fou_datemdf = models.DateTimeField(db_column='fou_DateMdf', blank=True, null=True)  # Field name made lowercase.
    fou_usercre = models.CharField(db_column='fou_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    fou_usermdf = models.CharField(db_column='fou_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    fou_tel1 = models.CharField(db_column='fou_Tel1', max_length=25, blank=True, null=True)  # Field name made lowercase.
    fou_tel2 = models.CharField(db_column='fou_Tel2', max_length=25, blank=True, null=True)  # Field name made lowercase.
    fou_adresse = models.CharField(db_column='fou_Adresse', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fou_mail = models.CharField(max_length=50, blank=True, null=True)
    fou_enabled = models.IntegerField(blank=True, null=True)
    fou_modepay = models.CharField(db_column='fou_ModePay', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fou_commercial = models.CharField(db_column='fou_Commercial', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_fournis'


class TInStock(models.Model):
    in_id = models.AutoField(db_column='in_Id', primary_key=True)  # Field name made lowercase.
    in_datecre = models.DateTimeField(db_column='in_DateCre', blank=True, null=True)  # Field name made lowercase.
    in_usercre = models.CharField(db_column='in_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    in_quantite = models.IntegerField(db_column='in_Quantite', blank=True, null=True)  # Field name made lowercase.
    in_pri_id = models.IntegerField(db_column='in_pri_Id', blank=True, null=True)  # Field name made lowercase.
    in_art_code = models.CharField(db_column='in_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    in_lot_code = models.CharField(db_column='in_lot_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    in_motif = models.CharField(max_length=50, blank=True, null=True)
    in_lot_id = models.IntegerField(db_column='in_lot_Id', blank=True, null=True)  # Field name made lowercase.
    in_date = models.DateField(blank=True, null=True)
    in_code = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_in_stock'


class TInventaire(models.Model):
    inv_id = models.AutoField(db_column='inv_Id', primary_key=True)  # Field name made lowercase.
    inv_code = models.CharField(db_column='inv_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    inv_datecre = models.DateTimeField(db_column='inv_DateCre', blank=True, null=True)  # Field name made lowercase.
    inv_datemdf = models.DateTimeField(db_column='inv_DateMdf', blank=True, null=True)  # Field name made lowercase.
    inv_usercre = models.CharField(db_column='inv_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    inv_usermdf = models.CharField(db_column='inv_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    inv_nbligne = models.IntegerField(db_column='inv_nbLigne', blank=True, null=True)  # Field name made lowercase.
    inv_date = models.DateField(db_column='inv_Date')  # Field name made lowercase.
    inv_etat = models.CharField(max_length=25, blank=True, null=True)
    inv_nbecart = models.IntegerField(db_column='inv_nbEcart', blank=True, null=True)  # Field name made lowercase.
    inv_nbverifie = models.IntegerField(db_column='inv_nbVerifie', blank=True, null=True)  # Field name made lowercase.
    inv_nbart = models.IntegerField(db_column='inv_nbArt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_inventaire'


class TLien(models.Model):
    lie_id = models.AutoField(db_column='lie_Id', primary_key=True)  # Field name made lowercase.
    lie_table = models.CharField(db_column='lie_Table', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lie_abs = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_lien'


class TLigneCaisse(models.Model):
    cail_id = models.AutoField(db_column='cail_Id', primary_key=True)  # Field name made lowercase.
    cail_datecre = models.DateTimeField(db_column='cail_DateCre', blank=True, null=True)  # Field name made lowercase.
    cail_datemdf = models.DateTimeField(db_column='cail_DateMdf', blank=True, null=True)  # Field name made lowercase.
    cail_usercre = models.CharField(db_column='cail_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cail_usermdf = models.CharField(db_column='cail_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cail_modepays = models.CharField(db_column='cail_ModePays', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cail_mobile = models.CharField(db_column='cail_Mobile', max_length=25)  # Field name made lowercase.
    cail_montant = models.DecimalField(db_column='cail_Montant', max_digits=18, decimal_places=2)  # Field name made lowercase.
    cail_solde = models.DecimalField(db_column='cail_Solde', max_digits=18, decimal_places=2)  # Field name made lowercase.
    cail_cai_code = models.CharField(max_length=25, blank=True, null=True)
    cail_etat = models.IntegerField(db_column='cail_Etat', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_ligne_caisse'


class TLigneCmdFournis(models.Model):
    cmfl_id = models.AutoField(db_column='cmfl_Id', primary_key=True)  # Field name made lowercase.
    cmfl_datecre = models.DateTimeField(db_column='cmfl_DateCre', blank=True, null=True)  # Field name made lowercase.
    cmfl_datemdf = models.DateTimeField(db_column='cmfl_DateMdf', blank=True, null=True)  # Field name made lowercase.
    cmfl_usercre = models.CharField(db_column='cmfl_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cmfl_usermdf = models.CharField(db_column='cmfl_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cmfl_quantite = models.IntegerField(db_column='cmfl_Quantite', blank=True, null=True)  # Field name made lowercase.
    cmfl_pri_id = models.IntegerField(db_column='cmfl_pri_Id', blank=True, null=True)  # Field name made lowercase.
    cmfl_cmf_code = models.CharField(db_column='cmfl_cmf_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cmfl_prixachat = models.DecimalField(db_column='cmfl_PrixAchat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cmfl_tva = models.DecimalField(db_column='cmfl_Tva', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cmfl_totalht = models.DecimalField(db_column='cmfl_TotalHT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cmfl_art_code = models.CharField(db_column='cmfl_Art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cmfl_fou_code = models.CharField(db_column='cmfl_fou_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cmfl_totalttc = models.DecimalField(db_column='cmfl_TotalTTC', max_digits=10, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_ligne_cmd_fournis'


class TLigneEntree(models.Model):
    entl_id = models.AutoField(db_column='entl_Id', primary_key=True)  # Field name made lowercase.
    entl_datecre = models.DateTimeField(db_column='entl_DateCre', blank=True, null=True)  # Field name made lowercase.
    entl_datemdf = models.DateTimeField(db_column='entl_DateMdf', blank=True, null=True)  # Field name made lowercase.
    entl_usercre = models.CharField(db_column='entl_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    entl_usermdf = models.CharField(db_column='entl_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    entl_quantite = models.IntegerField(db_column='entl_Quantite', blank=True, null=True)  # Field name made lowercase.
    entl_prixunit = models.DecimalField(db_column='entl_PrixUnit', max_digits=18, decimal_places=2)  # Field name made lowercase.
    entl_ttc = models.DecimalField(db_column='entl_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    entl_art_code = models.CharField(db_column='entl_art_Code', max_length=25)  # Field name made lowercase.
    entl_pri_id = models.IntegerField(db_column='entl_pri_Id')  # Field name made lowercase.
    entl_tva = models.DecimalField(db_column='entl_TVA', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    entl_ent_code = models.CharField(db_column='entl_ent_Code', max_length=25)  # Field name made lowercase.
    entl_ht = models.DecimalField(db_column='entl_HT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    entl_fou_code = models.CharField(db_column='entl_fou_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    entl_lot = models.CharField(db_column='entl_Lot', max_length=50, blank=True, null=True)  # Field name made lowercase.
    entl_dateper = models.DateField(db_column='entl_DatePer', blank=True, null=True)  # Field name made lowercase.
    entl_prix = models.DecimalField(db_column='entl_Prix', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    entl_remise = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_ligne_entree'


class TLigneInventaire(models.Model):
    invl_id = models.AutoField(db_column='invl_Id', primary_key=True)  # Field name made lowercase.
    invl_datecre = models.DateTimeField(db_column='invl_DateCre', blank=True, null=True)  # Field name made lowercase.
    invl_usercre = models.CharField(db_column='invl_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    invl_datemdf = models.DateTimeField(db_column='invl_DateMdf', blank=True, null=True)  # Field name made lowercase.
    invl_usermdf = models.CharField(db_column='invl_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    invl_qtetheo = models.IntegerField(db_column='invl_QteTheo', blank=True, null=True)  # Field name made lowercase.
    invl_art_code = models.CharField(db_column='invl_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    invl_lot_code = models.CharField(db_column='invl_lot_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    invl_lot_id = models.IntegerField(db_column='invl_lot_Id', blank=True, null=True)  # Field name made lowercase.
    invl_qtephys = models.IntegerField(db_column='invl_QtePhys', blank=True, null=True)  # Field name made lowercase.
    invl_ecart = models.IntegerField(db_column='invl_Ecart', blank=True, null=True)  # Field name made lowercase.
    invl_inv_code = models.CharField(max_length=25, blank=True, null=True)
    invl_etat = models.IntegerField(db_column='invl_Etat', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_ligne_inventaire'


class TLigneProforma(models.Model):
    prol_id = models.AutoField(db_column='prol_Id', primary_key=True)  # Field name made lowercase.
    prol_datecre = models.DateTimeField(db_column='prol_DateCre', blank=True, null=True)  # Field name made lowercase.
    prol_datemdf = models.DateTimeField(db_column='prol_DateMdf', blank=True, null=True)  # Field name made lowercase.
    prol_usercre = models.CharField(db_column='prol_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    prol_usermdf = models.CharField(db_column='prol_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    prol_quantite = models.IntegerField(db_column='prol_Quantite', blank=True, null=True)  # Field name made lowercase.
    prol_pri_id = models.IntegerField(db_column='prol_pri_Id', blank=True, null=True)  # Field name made lowercase.
    prol_pro_code = models.CharField(db_column='prol_pro_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    prol_prixunit = models.DecimalField(db_column='prol_PrixUnit', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    prol_tva = models.DecimalField(db_column='prol_Tva', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    prol_totalht = models.DecimalField(db_column='prol_TotalHT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    prol_art_code = models.CharField(db_column='prol_Art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    prol_cli_code = models.CharField(db_column='prol_cli_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    prol_remise = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    prol_totalttc = models.DecimalField(db_column='prol_TotalTTC', max_digits=10, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    prol_lot_id = models.IntegerField(db_column='prol_lot_Id', blank=True, null=True)  # Field name made lowercase.
    prol_lot_code = models.CharField(db_column='prol_lot_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    prol_lot_dateper = models.DateField(db_column='prol_lot_DatePer', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_ligne_proforma'


class TLigneRtc(models.Model):
    rtcl_id = models.AutoField(db_column='rtcl_Id', primary_key=True)  # Field name made lowercase.
    rtcl_datecre = models.DateTimeField(db_column='rtcl_DateCre', blank=True, null=True)  # Field name made lowercase.
    rtcl_datemdf = models.DateTimeField(db_column='rtcl_DateMdf', blank=True, null=True)  # Field name made lowercase.
    rtcl_usercre = models.CharField(db_column='rtcl_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtcl_usermdf = models.CharField(db_column='rtcl_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtcl_quantite = models.IntegerField(db_column='rtcl_Quantite', blank=True, null=True)  # Field name made lowercase.
    rtcl_prixunit = models.DecimalField(db_column='rtcl_PrixUnit', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtcl_ttc = models.DecimalField(db_column='rtcl_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtcl_ht = models.DecimalField(db_column='rtcl_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtcl_tva = models.DecimalField(db_column='rtcl_TVA', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rtcl_pri_id = models.IntegerField(db_column='rtcl_pri_Id', blank=True, null=True)  # Field name made lowercase.
    rtcl_lot_id = models.IntegerField(db_column='rtcl_lot_Id', blank=True, null=True)  # Field name made lowercase.
    rtcl_lot_code = models.CharField(db_column='rtcl_lot_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rtcl_lot_dateper = models.DateField(db_column='rtcl_lot_DatePer', blank=True, null=True)  # Field name made lowercase.
    rtcl_art_code = models.CharField(db_column='rtcl_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtcl_cli_code = models.CharField(db_column='rtcl_cli_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtcl_rtc_code = models.CharField(db_column='rtcl_rtc_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtcl_vte_code = models.CharField(db_column='rtcl_vte_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtcl_vtel_id = models.IntegerField(db_column='rtcl_vtel_Id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_ligne_rtc'


class TLigneRtf(models.Model):
    rtfl_id = models.AutoField(db_column='rtfl_Id', primary_key=True)  # Field name made lowercase.
    rtfl_datecre = models.DateTimeField(db_column='rtfl_DateCre', blank=True, null=True)  # Field name made lowercase.
    rtfl_datemdf = models.DateTimeField(db_column='rtfl_DateMdf', blank=True, null=True)  # Field name made lowercase.
    rtfl_usercre = models.CharField(db_column='rtfl_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtfl_usermdf = models.CharField(db_column='rtfl_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtfl_quantite = models.IntegerField(db_column='rtfl_Quantite', blank=True, null=True)  # Field name made lowercase.
    rtfl_prixunit = models.DecimalField(db_column='rtfl_PrixUnit', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtfl_ttc = models.DecimalField(db_column='rtfl_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtfl_ht = models.DecimalField(db_column='rtfl_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtfl_tva = models.DecimalField(db_column='rtfl_TVA', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rtfl_pri_id = models.IntegerField(db_column='rtfl_pri_Id', blank=True, null=True)  # Field name made lowercase.
    rtfl_lot_id = models.IntegerField(db_column='rtfl_lot_Id', blank=True, null=True)  # Field name made lowercase.
    rtfl_lot_code = models.CharField(db_column='rtfl_lot_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rtfl_lot_dateper = models.DateField(db_column='rtfl_lot_DatePer', blank=True, null=True)  # Field name made lowercase.
    rtfl_art_code = models.CharField(db_column='rtfl_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtfl_fou_code = models.CharField(db_column='rtfl_fou_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtfl_rtf_code = models.CharField(db_column='rtfl_rtf_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtfl_ent_code = models.CharField(db_column='rtfl_ent_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtfl_entl_id = models.IntegerField(db_column='rtfl_entl_Id', blank=True, null=True)  # Field name made lowercase.
    rtfl_remise = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rtft_puapremise = models.DecimalField(db_column='rtft_PuApRemise', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_ligne_rtf'


class TLigneVente(models.Model):
    vtel_id = models.AutoField(db_column='vtel_Id', primary_key=True)  # Field name made lowercase.
    vtel_datecre = models.DateTimeField(db_column='vtel_DateCre', blank=True, null=True)  # Field name made lowercase.
    vtel_datemdf = models.DateTimeField(db_column='vtel_DateMdf', blank=True, null=True)  # Field name made lowercase.
    vtel_usercre = models.CharField(db_column='vtel_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vtel_usermdf = models.CharField(db_column='vtel_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vtel_quantite = models.IntegerField(db_column='vtel_Quantite', blank=True, null=True)  # Field name made lowercase.
    vtel_prixunit = models.DecimalField(db_column='vtel_PrixUnit', max_digits=18, decimal_places=2)  # Field name made lowercase.
    vtel_ttc = models.DecimalField(db_column='vtel_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    vtel_ht = models.DecimalField(db_column='vtel_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    vtel_tva = models.DecimalField(db_column='vtel_TVA', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    vtel_pri_id = models.IntegerField(db_column='vtel_pri_Id', blank=True, null=True)  # Field name made lowercase.
    vtel_lot_id = models.IntegerField(db_column='vtel_lot_Id', blank=True, null=True)  # Field name made lowercase.
    vtel_lot_code = models.CharField(db_column='vtel_lot_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    vtel_lot_dateper = models.DateField(db_column='vtel_lot_DatePer', blank=True, null=True)  # Field name made lowercase.
    vtel_art_code = models.CharField(db_column='vtel_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vtel_valide = models.IntegerField(db_column='vtel_Valide', blank=True, null=True)  # Field name made lowercase.
    vtel_cli_code = models.CharField(db_column='vtel_cli_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vtel_vte_code = models.CharField(db_column='vtel_vte_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vtel_remise = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_ligne_vente'


class TListMenu(models.Model):
    men_id = models.AutoField(db_column='men_Id', primary_key=True)  # Field name made lowercase.
    men_code = models.IntegerField(unique=True, blank=True, null=True)
    men_desc = models.CharField(max_length=100, blank=True, null=True)
    men_enabled = models.IntegerField(blank=True, null=True)
    men_vbox = models.CharField(db_column='men_Vbox', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_list_menu'


class TLot(models.Model):
    lot_id = models.AutoField(db_column='lot_Id', primary_key=True)  # Field name made lowercase.
    lot_datecre = models.DateTimeField(db_column='lot_DateCre', blank=True, null=True)  # Field name made lowercase.
    lot_datemdf = models.DateTimeField(db_column='lot_DateMdf', blank=True, null=True)  # Field name made lowercase.
    lot_usercre = models.CharField(db_column='lot_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    lot_usermdf = models.CharField(db_column='lot_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    lot_enabled = models.IntegerField(db_column='lot_Enabled', blank=True, null=True)  # Field name made lowercase.
    lot_code = models.CharField(db_column='lot_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lot_dateper = models.DateField(db_column='lot_DatePer', blank=True, null=True)  # Field name made lowercase.
    lot_datefin = models.DateTimeField(db_column='lot_DateFin', blank=True, null=True)  # Field name made lowercase.
    lot_datedeb = models.DateTimeField(db_column='lot_DateDeb', blank=True, null=True)  # Field name made lowercase.
    lot_art_code = models.CharField(db_column='lot_Art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_lot'
        unique_together = (('lot_code', 'lot_art_code'),)


class TMvt(models.Model):
    mv_id = models.AutoField(db_column='mv_Id', primary_key=True)  # Field name made lowercase.
    mv_table = models.CharField(max_length=25, blank=True, null=True)
    mv_desc = models.CharField(max_length=50, blank=True, null=True)
    mv_etat = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_mvt'


class TMvtStock(models.Model):
    mvt_id = models.AutoField(db_column='mvt_Id', primary_key=True)  # Field name made lowercase.
    mvt_action = models.CharField(db_column='mvt_Action', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mvt_origine = models.CharField(db_column='mvt_Origine', max_length=25, blank=True, null=True)  # Field name made lowercase.
    mvt_datecre = models.DateTimeField(db_column='mvt_DateCre', blank=True, null=True)  # Field name made lowercase.
    mvt_datemdf = models.DateTimeField(db_column='mvt_DateMdf', blank=True, null=True)  # Field name made lowercase.
    mvt_usercre = models.CharField(db_column='mvt_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    mvt_usermdf = models.CharField(db_column='mvt_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    mvt_code_org = models.CharField(db_column='mvt_Code_Org', max_length=20)  # Field name made lowercase.
    mvt_qte = models.IntegerField(db_column='mvt_Qte')  # Field name made lowercase.
    mvt_date = models.DateField(db_column='mvt_Date')  # Field name made lowercase.
    mvt_art_code = models.CharField(db_column='mvt_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    mvt_pri_id = models.IntegerField(db_column='mvt_pri_Id')  # Field name made lowercase.
    mvt_lot_code = models.CharField(db_column='mvt_lot_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_mvt_stock'


class TOutStock(models.Model):
    out_id = models.AutoField(db_column='out_Id', primary_key=True)  # Field name made lowercase.
    out_datecre = models.DateTimeField(db_column='out_DateCre', blank=True, null=True)  # Field name made lowercase.
    out_usercre = models.CharField(db_column='out_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    out_quantite = models.IntegerField(db_column='out_Quantite', blank=True, null=True)  # Field name made lowercase.
    out_pri_id = models.IntegerField(db_column='out_pri_Id', blank=True, null=True)  # Field name made lowercase.
    out_art_code = models.CharField(db_column='out_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    out_lot_code = models.CharField(db_column='out_lot_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    out_motif = models.CharField(max_length=50, blank=True, null=True)
    out_lot_id = models.IntegerField(db_column='out_lot_Id', blank=True, null=True)  # Field name made lowercase.
    out_date = models.DateField(blank=True, null=True)
    out_code = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_out_stock'


class TPrix(models.Model):
    pri_id = models.AutoField(db_column='pri_Id', primary_key=True)  # Field name made lowercase.
    pri_datecre = models.DateTimeField(db_column='pri_DateCre', blank=True, null=True)  # Field name made lowercase.
    pri_datemdf = models.CharField(db_column='pri_DateMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    pri_usercre = models.CharField(db_column='pri_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    pri_usermdf = models.CharField(db_column='pri_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    pri_enabled = models.IntegerField(db_column='pri_Enabled', blank=True, null=True)  # Field name made lowercase.
    pri_datedeb = models.DateTimeField(db_column='pri_DateDeb', blank=True, null=True)  # Field name made lowercase.
    pri_datefin = models.DateTimeField(db_column='pri_DateFin', blank=True, null=True)  # Field name made lowercase.
    pri_vte = models.DecimalField(db_column='pri_Vte', max_digits=18, decimal_places=2)  # Field name made lowercase.
    pri_achat = models.DecimalField(db_column='pri_Achat', max_digits=18, decimal_places=2)  # Field name made lowercase.
    pri_art_code = models.CharField(db_column='pri_art_Code', max_length=25)  # Field name made lowercase.
    pri_marge = models.DecimalField(db_column='pri_Marge', max_digits=8, decimal_places=2)  # Field name made lowercase.
    pri_tauxmarge = models.DecimalField(db_column='pri_TauxMarge', max_digits=8, decimal_places=2)  # Field name made lowercase.
    pri_tva = models.DecimalField(db_column='pri_TVA', max_digits=8, decimal_places=2)  # Field name made lowercase.
    pri_unitevente = models.CharField(db_column='pri_UniteVente', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pri_nbcolis = models.IntegerField(db_column='pri_NbColis')  # Field name made lowercase.
    pri_chgprevu = models.IntegerField(db_column='pri_chgPrevu', blank=True, null=True)  # Field name made lowercase.
    pri_txremise = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_prix'


class TProforma(models.Model):
    pro_id = models.AutoField(db_column='pro_Id', primary_key=True)  # Field name made lowercase.
    pro_code = models.CharField(db_column='pro_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    pro_datecre = models.DateTimeField(db_column='pro_DateCre', blank=True, null=True)  # Field name made lowercase.
    pro_datemdf = models.DateTimeField(db_column='pro_DateMdf', blank=True, null=True)  # Field name made lowercase.
    pro_usercre = models.CharField(db_column='pro_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    pro_usermdf = models.CharField(db_column='pro_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    pro_date = models.DateField(db_column='pro_Date')  # Field name made lowercase.
    pro_modecmd = models.CharField(db_column='pro_ModeCmd', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pro_dateliv = models.DateField(db_column='pro_DateLiv', blank=True, null=True)  # Field name made lowercase.
    pro_enabled = models.IntegerField(blank=True, null=True)
    pro_montant_ht = models.DecimalField(db_column='pro_Montant_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    pro_montant_ttc = models.DecimalField(db_column='pro_Montant_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    pro_islivre = models.IntegerField(db_column='pro_isLivre', blank=True, null=True)  # Field name made lowercase.
    pro_cli_code = models.CharField(db_column='pro_cli_Code', max_length=25)  # Field name made lowercase.
    pro_lettre = models.CharField(max_length=255, blank=True, null=True)
    pro_tva = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    pro_remise = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_proforma'


class TRetourClient(models.Model):
    rtc_id = models.AutoField(db_column='rtc_Id', primary_key=True)  # Field name made lowercase.
    rtc_code = models.CharField(db_column='rtc_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    rtc_datecre = models.DateTimeField(db_column='rtc_DateCre', blank=True, null=True)  # Field name made lowercase.
    rtc_datemdf = models.DateTimeField(db_column='rtc_DateMdf', blank=True, null=True)  # Field name made lowercase.
    rtc_usercre = models.CharField(db_column='rtc_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtc_usermdf = models.CharField(db_column='rtc__UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    rtc_date = models.DateField(db_column='rtc_Date')  # Field name made lowercase.
    rtc_vte_code = models.CharField(db_column='rtc_vte_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rtc_montant_ht = models.DecimalField(db_column='rtc_Montant_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtc_montant_ttc = models.DecimalField(db_column='rtc_Montant_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtc_tva = models.DecimalField(db_column='rtc_TVA', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rtc_cli_code = models.CharField(db_column='rtc_cli_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rtc_cli_nom = models.CharField(db_column='rtc_cli_Nom', max_length=100, blank=True, null=True)  # Field name made lowercase.
    rtc_motif = models.CharField(max_length=50, blank=True, null=True)
    rtc_observation = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_retour_client'


class TRetourFournis(models.Model):
    rtf_id = models.AutoField(db_column='rtf_Id', primary_key=True)  # Field name made lowercase.
    rtf_code = models.CharField(db_column='rtf_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    rtf_datecre = models.DateTimeField(db_column='rtf_DateCre', blank=True, null=True)  # Field name made lowercase.
    rtf_datemdf = models.DateTimeField(db_column='rtf_DateMdf', blank=True, null=True)  # Field name made lowercase.
    rtf_usercre = models.CharField(db_column='rtf_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtf_usermdf = models.CharField(db_column='rtf_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    rtf_date = models.DateField(db_column='rtf_Date')  # Field name made lowercase.
    rtf_ent_code = models.CharField(db_column='rtf_ent_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rtf_cmf_code = models.CharField(db_column='rtf_cmf_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rtf_facture = models.CharField(max_length=20, blank=True, null=True)
    rtf_montant_ht = models.DecimalField(db_column='rtf_Montant_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtf_montant_ttc = models.DecimalField(db_column='rtf_Montant_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    rtf_fou_code = models.CharField(db_column='rtf_fou_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rtf_fou_nom = models.CharField(db_column='rtf_fou_Nom', max_length=100, blank=True, null=True)  # Field name made lowercase.
    rtf_motif = models.CharField(max_length=50, blank=True, null=True)
    rtf_observation = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_retour_fournis'


class TSousFamille(models.Model):
    sof_id = models.AutoField(db_column='sof_Id', primary_key=True)  # Field name made lowercase.
    sof_code = models.CharField(db_column='sof_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    sof_nom = models.CharField(db_column='sof_Nom', max_length=155, blank=True, null=True)  # Field name made lowercase.
    sof_datecre = models.DateTimeField(db_column='sof_DateCre', blank=True, null=True)  # Field name made lowercase.
    sof_datemdf = models.DateTimeField(db_column='sof_DateMdf', blank=True, null=True)  # Field name made lowercase.
    sof_usercre = models.CharField(db_column='sof_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    sof_usermdf = models.CharField(db_column='sof_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    sof_fam_id = models.IntegerField(db_column='sof_fam_Id', blank=True, null=True)  # Field name made lowercase.
    sof_fabricant = models.CharField(max_length=50, blank=True, null=True)
    sof_paysorg = models.CharField(db_column='sof_PaysOrg', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sof_enabled = models.IntegerField(db_column='sof_Enabled', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_sous_famille'


class TStock(models.Model):
    stk_id = models.AutoField(db_column='stk_Id', primary_key=True)  # Field name made lowercase.
    stk_datecre = models.DateTimeField(db_column='stk_DateCre', blank=True, null=True)  # Field name made lowercase.
    stk_datemdf = models.DateTimeField(db_column='stk_DateMdf', blank=True, null=True)  # Field name made lowercase.
    stk_usercre = models.CharField(db_column='stk_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    stk_usermdf = models.CharField(db_column='stk_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    stk_quantite = models.IntegerField(db_column='stk_Quantite', blank=True, null=True)  # Field name made lowercase.
    stk_pri_id = models.IntegerField(db_column='stk_pri_Id', blank=True, null=True)  # Field name made lowercase.
    stk_art_code = models.CharField(db_column='stk_art_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.
    stk_lot_code = models.CharField(db_column='stk_lot_Code', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_stock'


class TUsers(models.Model):
    use_id = models.AutoField(
        db_column='use_Id', primary_key=True)
    use_login = models.CharField(
        db_column='use_Login', max_length=25, blank=True, null=True)
    use_pwd = models.CharField(
        max_length=512, blank=True, null=True)
    use_acc_code = models.CharField(
        max_length=25, blank=True, null=True)
    use_enabled = models.IntegerField(
        blank=True, null=True)
    use_datecre = models.DateTimeField(
        db_column='use_DateCre', blank=True, null=True)
    use_datemdf = models.DateTimeField(
        db_column='use_DateMdf', blank=True, null=True)
    use_usercre = models.CharField(
        db_column='use_UserCre', max_length=25, blank=True, null=True)
    use_usermdf = models.CharField(
        db_column='use_UserMdf', max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_users'


class TVente(models.Model):
    vte_id = models.AutoField(db_column='vte_Id', primary_key=True)  # Field name made lowercase.
    vte_code = models.CharField(db_column='vte_Code', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    vte_datecre = models.DateTimeField(db_column='vte_DateCre', blank=True, null=True)  # Field name made lowercase.
    vte_datemdf = models.DateTimeField(db_column='vte_DateMdf', blank=True, null=True)  # Field name made lowercase.
    vte_usercre = models.CharField(db_column='vte_UserCre', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vte_usermdf = models.CharField(db_column='vte_UserMdf', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vte_date = models.DateField(db_column='vte_Date')  # Field name made lowercase.
    vte_modepaye = models.CharField(db_column='vte_ModePaye', max_length=50, blank=True, null=True)  # Field name made lowercase.
    vte_montant_ht = models.DecimalField(db_column='vte_Montant_HT', max_digits=18, decimal_places=2)  # Field name made lowercase.
    vte_montant_ttc = models.DecimalField(db_column='vte_Montant_TTC', max_digits=18, decimal_places=2)  # Field name made lowercase.
    vte_tva = models.DecimalField(db_column='vte_TVA', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    vte_cli_code = models.CharField(db_column='vte_cli_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    vte_cli_nom = models.CharField(db_column='vte_cli_Nom', max_length=100, blank=True, null=True)  # Field name made lowercase.
    vte_cli_contact = models.CharField(db_column='vte_cli_Contact', max_length=50, blank=True, null=True)  # Field name made lowercase.
    vte_payeclient = models.CharField(db_column='vte_PayeClient', max_length=50, blank=True, null=True)  # Field name made lowercase.
    vte_datepay = models.DateTimeField(db_column='vte_DatePay', blank=True, null=True)  # Field name made lowercase.
    vte_telmoney = models.CharField(db_column='vte_TelMoney', max_length=25, blank=True, null=True)  # Field name made lowercase.
    vte_valide = models.IntegerField(db_column='vte_Valide', blank=True, null=True)  # Field name made lowercase.
    vte_paye = models.IntegerField(db_column='vte_Paye', blank=True, null=True)  # Field name made lowercase.
    vte_datevalide = models.DateTimeField(db_column='vte_DateValide', blank=True, null=True)  # Field name made lowercase.
    vte_livreur = models.CharField(max_length=50, blank=True, null=True)
    vet_operateur = models.CharField(max_length=25, blank=True, null=True)
    vte_lettremontant = models.CharField(db_column='vte_lettreMontant', max_length=555, blank=True, null=True)  # Field name made lowercase.
    ve_dateecheance = models.DateField(db_column='ve_dateEcheance', blank=True, null=True)  # Field name made lowercase.
    ve_code_bl = models.CharField(max_length=45, blank=True, null=True)
    ve_adresse_liv = models.CharField(max_length=455, blank=True, null=True)
    ve_remise = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    ve_proforma = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_vente'
