# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WisdomPlanificationEmp(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.planificationemp'
    _description = 'info.planfication'

    reference = fields.Char(string='Reference', readonly=True, required=True, copy=False,
                            default=lambda self: _('Nouveau'))
    active = fields.Boolean(string="Active", default=True, tracking=True)
    frais_transport = fields.Monetary("Frais Transport", tracking=True)
    prix_unitaire = fields.Monetary("Prix unitaire", tracking=True)
    total_rafrechissement = fields.Monetary("Total_rafraichissement", tracking=True, compute="_compute_rafraichissement_prix")
    location_voiture = fields.Monetary("Location voiture", tracking=True)
    palette_deau = fields.Integer("Rafraichissement qty_palette", tracking=True)
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'XAF')]).id,
                                  readonly=True, string='Currency', tracking=True)

    heure_depart = fields.Datetime('Heure de départ', tracking=True)
    lieu = fields.Char('Lieu de regroupement', tracking=True)
    remarque = fields.Text('Remarque', tracking=True)

    # vehicule = fields.Selection([('oui', 'Oui'), ('non', 'Non')], "Vehicule", required=True, tracking=True,
    #                             default="oui")
    localite = fields.Char('Localité', tracking=True)
    total = fields.Monetary("Total", tracking=True, compute='_compute_prix_total')

    planficationemp_ids = fields.One2many('wisdom.employeplan','planficationemp_id', string='Employé(e)')
    clientplan_ids = fields.One2many('wisdom.clientplan', 'planificationempl_id', string='Clients planifier')
    employe_id = fields.Many2one('wisdom.employe', string='Employé')

    state = fields.Selection([('annuler', 'Annuler'), ('brouillon', 'Brouillon'), ('verifier', 'Verifier'),
                              ('encour', 'Sur le terrain')
                                 , ('realiser', 'Réaliser')], default="brouillon", string='States')

    color = fields.Integer()

    def action_encour(self):
        self.state = 'encour'

    def action_realiser(self):
        self.state = 'realiser'

    def action_verifier(self):
        self.state = 'verifier'

    def action_brouillon(self):
        self.state = 'brouillon'

    def action_annuler(self):
        self.state = 'annuler'

        # calcule le total rafrachissement
    @api.depends('prix_unitaire', 'palette_deau')
    def _compute_rafraichissement_prix(self):
        for r in self:
            if not r.prix_unitaire:
                 r.total_rafrechissement = 0
            else:
                r.total_rafrechissement = r.prix_unitaire * r.palette_deau

    # calcule le total
    @api.depends('total_rafrechissement', 'frais_transport', 'location_voiture')
    def _compute_prix_total(self):
        for r in self:
            if not r.location_voiture:
                 r.total = 0
            else:
                r.total = r.total_rafrechissement + r.frais_transport + r.location_voiture

    # incrementation sequencial d'identifiant client
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('wisdom.planificationemp') or _('Nouveau')
        res = super(WisdomPlanificationEmp, self).create(vals)
        return res

    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, field.reference))
        return res


