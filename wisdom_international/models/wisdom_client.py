# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WisdomClient(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.client'
    _description = 'info.client'


    reference = fields.Char(string='Reference', readonly=True, required=True, copy=False,
                            default=lambda self: _('Nouveau'))
    name = fields.Char(string='Nom', required=True, tracking=True)
    surname = fields.Char(string='Prénom', tracking=True)
    mail = fields.Char(string='Mail', tracking=True)
    country = fields.Many2one('res.country', string='Nationalité', ondelete='restrict', tracking=True)
    telephone = fields.Char('Téléphone', tracking=True)
    adresse = fields.Char(string='Adresse', tracking=True)
    date_naissance = fields.Date(string='Date_Naissance', tracking=True)
    lieu_naissance = fields.Char(string='Lieu_Naissance', tracking=True)
    recommandation = fields.Char(string='Recommandation', tracking=True)
    num_cni = fields.Char(string='Numero CNI', tracking=True)
    date_enregistrement = fields.Datetime(string='Date_Enregistrement', tracking=True,readonly=True, required=True, index=True, default=lambda self: fields.Datetime.now())
    planification_ids = fields.One2many('wisdom.planification', 'client_id', string='Planification', ondelete='restrict')
    achat_ids = fields.One2many('wisdom.achat', 'client_ids', string='Achat',ondelete='restrict')

    color = fields.Integer()
    state = fields.Selection([('valider', 'Valider'), ('encour', 'Pas encore planifier'), ('planifier', 'Planifier'), ('telephone', 'Ecrire au client')],
                             default="encour", string='States')

    somme_activation = fields.Monetary("Ouverture dossier", tracking=True)
    superficie = fields.Char('Superficie(m²)', tracking=True)
    vehicule = fields.Selection([('oui', 'Oui'), ('non', 'Non')], "Vehicule", required=True, tracking=True,default="oui")
    localite = fields.Char('Localité', tracking=True)
    lieu = fields.Char('Lieu de regroupement', tracking=True)
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'XAF')]).id,
                                  readonly=True, string='Currency', tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)

    def action_valider(self):
        for rec in self:
            rec.state = 'valider'

    def action_encour(self):
        for rec in self:
            rec.state = 'encour'

    def action_planifier(self):
        for rec in self:
            rec.state = 'planifier'

    def action_telephone(self):
        for rec in self:
            if not rec.telephone:
                raise ValidationError(_("Veuillez inserer un vrai numero whatsapp"))
            msg = 'Bonjour M/Mlle %s ' % rec.name
            whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (rec.telephone, msg)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    # incrementation sequencial d'identifiant client
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('wisdom.client') or _('Nouveau')
        res = super(WisdomClient, self).create(vals)
        return res

        # contrainte mail
    _sql_constraints = [
         ('email_uniq', 'UNIQUE (mail)', 'adresse mail deja utiliser')
    ]

    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, field.reference))
        return res



class WisdomClientPlan(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.clientplan'

    client_id = fields.Many2one('wisdom.client', string='Client', copy=False, tracking=True)
    name = fields.Char(string='Nom', tracking=True)
    surname = fields.Char(string='Prénom', tracking=True)
    telephone = fields.Char('Téléphone', tracking=True)
    num_cni = fields.Char(string='Numero CNI', tracking=True)
    vehicule = fields.Selection([('oui', 'Oui'), ('non', 'Non')], "Vehicule", required=True, tracking=True,
                                default="oui")
    state = fields.Selection([('valider', 'Valider'), ('encour', 'Pas encore planifier'), ('planifier', 'Planifier')],
                             default="encour", string='States')

    planificationempl_id = fields.Many2one('wisdom.planificationemp', string='Planification Entreprise', tracking=True)

    @api.onchange("client_id")
    def _onchange_client_id(self):
        if not self.client_id:
            self.update(
                {
                    "name": False,
                    "telephone": False,
                    "vehicule": False,
                    "surname": False,
                    "num_cni": False,
                    "state": False,
                }
            )
        else:
            self.update(
                {
                    "name": self.client_id.name,
                    "telephone": self.client_id.telephone,
                    "vehicule": self.client_id.vehicule,
                    "surname": self.client_id.surname,
                    "num_cni": self.client_id.num_cni,
                    "state": self.client_id.state,
                }
            )
        return {'domain': {'client_id': [('state', '=', ['planifier', 'valider'])]}}

