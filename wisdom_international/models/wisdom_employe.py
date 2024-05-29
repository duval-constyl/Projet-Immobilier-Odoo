# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WisdomEmploye(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.employe'
    _description = 'info.employe'

    reference = fields.Char(string='Reference', readonly=True, required=True, copy=False,
                            default=lambda self: _('Nouveau'))
    name = fields.Char(string='Nom', required=True, tracking=True)
    surnames = fields.Char(string='Prénom', tracking=True)
    mail = fields.Char(string='Mail', tracking=True)
    country = fields.Many2one('res.country', string='Nationalité', ondelete='restrict', tracking=True)
    telephones = fields.Char('Téléphone', tracking=True)
    adresse = fields.Char(string='Adresse', tracking=True)
    fonction = fields.Char(string='Poste', tracking=True)
    num_cni = fields.Char(string='Numero CNI', tracking=True)
    ufile = fields.Binary(tracking=True)
    password = fields.Char(string='Mot de Passe', tracking=True)
    confirm_password = fields.Char(string='Confirmation MDP', tracking=True)
    state = fields.Selection([('fonction', 'En Fonction'), ('annuler', 'Annuler'), ('repos', 'En Repos')],
                             default="repos", string='States')
    achat_ids = fields.One2many('wisdom.achat', 'employe_ids', string='Achat', ondelete='restrict')

    # incrementation sequencial d'identifiant client
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('wisdom.employe') or _('Nouveau')
        res = super(WisdomEmploye, self).create(vals)
        return res

    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, field.reference))
        return res

        # contrainte mail
    _sql_constraints = [
        ('email_uniq', 'UNIQUE (mail)', 'adresse mail deja utiliser')
    ]


    def action_fonction(self):
        self.state = 'fonction'

    def action_repos(self):
        self.state = 'repos'

    def action_annuler(self):
        self.state = 'annuler'


class WisdomEmployeplan(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.employeplan'

    name = fields.Char(string='Nom', required=True, tracking=True)
    surnames = fields.Char(string='Prénom', tracking=True)
    telephones = fields.Char('Téléphone', tracking=True)
    employe_id =fields.Many2one('wisdom.employe', string='Employé')
    planficationemp_id = fields.Many2one('wisdom.planificationemp')

    @api.onchange('employe_id')
    def _onchange_employe_id(self):
        if not self.employe_id:
            self.update(
                {
                    'name': False,
                    'surnames': False,
                    'telephones': False,
                }
            )
        else:
            self.update(
                {
                    "name": self.employe_id.name,
                    "surnames": self.employe_id.surnames,
                    "telephones": self.employe_id.telephones,
                }
            )

