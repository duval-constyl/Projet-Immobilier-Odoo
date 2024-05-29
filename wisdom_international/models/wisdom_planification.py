# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WisdomPlanification(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.planification'
    _description = 'info.planfication'

    reference = fields.Char(string='Reference', readonly=True, required=True, copy=False,
                            default=lambda self: _('Nouveau'))
    frais_transport = fields.Monetary("Frais Transport", tracking=True)
    prix_unitaire = fields.Monetary("Prix unitaire", tracking=True)
    total_rafrechissement = fields.Monetary("Total_rafraichissement", tracking=True)
    location_voiture = fields.Monetary("Location voiture", tracking=True)
    palette_deau = fields.Integer("Rafraichissement qty", tracking=True)
    currency_id = fields.Many2one('res.currency',default=lambda self: self.env['res.currency'].search([('name', '=', 'XAF')]).id,readonly=True, string='Currency', tracking=True)

    vehicule = fields.Selection([('oui', 'Oui'), ('non', 'Non')], "Vehicule",required=True, tracking=True, default="oui")
    localite = fields.Char('Localité', tracking=True)
    total = fields.Monetary("Total", tracking=True, compute='_compute_price_total')
    somme_activation = fields.Monetary("Ouverture dossier", tracking=True)
    superficie = fields.Char('Superficie', tracking=True)

    heure_depart = fields.Datetime('Heure de départ', tracking=True)
    lieu = fields.Char('Lieu de regroupement', tracking=True)
    remarque = fields.Text('Remarque', tracking=True)

    client_id = fields.Many2one('wisdom.client', string='Client', copy=False, tracking=True,ondelete='restrict')
    surname = fields.Char(string='Prénom', tracking=True)
    telephone = fields.Char('Téléphone', tracking=True)
    mail = fields.Char(string='Mail', tracking=True)

    state = fields.Selection([('annuler', 'Annuler'), ('brouillon', 'Brouillon'), ('verifier', 'Verifier'), ('encour', 'Pas encore planifier')
            , ('planifier', 'Planifier'), ('mail', 'Envoyer par mail'), ('telephone', 'Envoyer pars SMS')],default="brouillon", string='States')
    
    active = fields.Boolean(string="Active", default=True, tracking=True)
    color = fields.Integer()

    def action_telephone(self):
        self.state = 'telephone'

    def action_mail(self):
        self.state = 'mail'

    def action_encour(self):
        self.state = 'encour'

    def action_planifier(self):
        self.state = 'planifier'

    def action_verifier(self):
        self.state = 'verifier'

    def action_brouillon(self):
        self.state = 'brouillon'

    def action_annuler(self):
        self.state = 'annuler'

    @api.depends('somme_activation', 'location_voiture')
    def _compute_price_total(self):
        for r in self:
            if r.vehicule == 'oui':
                r.total = r.somme_activation
            else:
                r.total = r.somme_activation + r.location_voiture


    # incrementation sequencial d'identifiant client
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('wisdom.planification') or _('Nouveau')
        res = super(WisdomPlanification, self).create(vals)
        return res

    @api.onchange("client_id")
    def _onchange_client_id(self):

        if not self.client_id:
            self.update(
                {
                    "surname": False,
                    "telephone": False,
                    "mail": False,
                }
            )
        else:
            self.update(
                {
                    "surname": self.client_id.surname,
                    "telephone": self.client_id.telephone,
                    "mail": self.client_id.mail,
                }
            )

class WisdomClientPlan(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.clientplan'

    client_id = fields.Many2one('wisdom.client', string='Client', copy=False, tracking=True, ondelete='restrict')
    surname = fields.Char(string='Prénom', tracking=True)
    telephone = fields.Char('Téléphone', tracking=True)
    vehicule = fields.Selection([('oui', 'Oui'), ('non', 'Non')], "Vehicule", required=True, tracking=True,
                                default="oui")
    planification_id = fields.Many2one('wisdom.planification', string='Planification', tracking=True)
    planificationempl_id = fields.Many2one('wisdom.planificationemp', string='Planification Entreprise', tracking=True)

    @api.onchange("planification_id")
    def _onchange_planification_id(self):

        if not self.planification_id:
            self.update(
                {
                    "client_id": False,
                    "telephone": False,
                    "vehicule": False,
                    "surname": False,
                }
            )
        else:
            self.update(
                {
                    "client_id": self.planification_id.client_id.client_id,
                    "telephone": self.planification_id.client_id.telephone,
                    "vehicule": self.planification_id.vehicule,
                    "surname": self.planification_id.client_id.surname,
                }
            )