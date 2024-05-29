# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class WisdomAchat(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'wisdom.achat'
    _description = 'info.achat'

    reference = fields.Char(string='Reference', readonly=True, required=True, copy=False,
                            default=lambda self: _('Nouveau'))
    # user_id = fields.Many2one('res.users', 'Users', required=True, index=True, ondelete='cascade')
    active = fields.Boolean(string="Active", default=True, tracking=True)
    info_terrain = fields.Text(string="Info du terrain", tracking=True)

    client_ids = fields.Many2one('wisdom.client', string='Client', copy=False, tracking=True, ondelete='restrict')
    name = fields.Char(string='Nom', required=True, tracking=True)
    surname = fields.Char(string='Prénom', tracking=True)
    num_cni = fields.Char(string='Numero CNI', tracking=True)
    mail = fields.Char(string='Mail', tracking=True)
    telephone = fields.Char('Téléphone', tracking=True)


    localite = fields.Char('Localité', tracking=True)
    recommandation = fields.Char(string='Recommandation', tracking=True)
    condition = fields.Text(string='Condition', tracking=True)
    date = fields.Datetime(string='Date Enregistrement', tracking=True, readonly=True, required=True, index=True,
                       default=datetime.today())

    employe_ids = fields.Many2one('wisdom.employe', string="Employé auteur")
    surnames = fields.Char(string='Prénom', tracking=True)
    telephones = fields.Char('Téléphone', tracking=True)

    doc_name =fields.Char()
    doc_names = fields.Char()
    donnee_tec= fields.Binary(string="Dossier Technique")
    date_tec = fields.Datetime(string="Date d'envoie", tracking=True)
    donnee_foncier = fields.Binary(string="Titre Foncier")
    date_foncier = fields.Datetime(string="Date d'envoie", tracking=True)

    state = fields.Selection([('annuler', 'Annuler'), ('brouillon', 'Brouillon'), ('verifier', 'Verifier'), ('mail', 'Envoyer par mail')
                              , ('telephone', 'Envoyer pars SMS'), ('avance', 'Montant Avancé'), ('payer', 'Payer Content')],default="brouillon", string='States')


    ouverture_dossier= fields.Monetary("Ouverture dossier", tracking=True)
    superficie = fields.Integer('Superficie(m²)', tracking=True, default=0)
    rabais = fields.Selection([('1', '0%'), ('5', '5%'), ('6', '6%'), ('7', '7%'), ('8', '8%'), ('9', '9%'),
                               ('10', '10%'), ('11', '11%'), ('12', '12%'), ('13', '13%'), ('14', '14%'), ('15', '15%')],default="1", string="Rabais sur l'achat du terrain" )
    frais_commision = fields.Integer('Frais commision agence(%)', default=5, readonly=True)
    frais_dossier= fields.Monetary("Frais d'etablissement Dossier Technique")

    superficie_unit= fields.Monetary('Prix Unité superficie')
    superficie_prix = fields.Monetary('Prix superficie', compute='_compute_superficie_prix')
    superficie_prix_total= fields.Monetary('Prix superficie aprés rabais', compute='_compute_superficie_prix_total')
    rabais_total= fields.Monetary('Prix rabais', compute='_compute_rabais_total')
    frais_commision_total= fields.Monetary('Prix commission', compute='_compute_frais_commision_total')
    # product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure',domain="[('category_id', '=', product_uom_category_id)]")
    # product_uom_category_id = fields.Many2one(related='product_uom_id.category_id', readonly=True)
    total = fields.Monetary("Somme Total", tracking=True, compute='_compute_total')
    montant_payer =fields.Monetary("Montant payer", tracking=True)
    reste_payer = fields.Monetary('Reste à payer', tracking=True, compute='_compute_reste_payer')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'XAF')]).id,readonly=True, string='Currency', tracking=True)
    # achat_count = fields.Integer(compute="_achat_count", string="# d'achat", store=True)

    color = fields.Integer()
    progress = fields.Integer(string="Progress", compute='_compute_progress')

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'brouillon':
                progress = 25
            elif rec.state == 'verifier':
                progress = 50
            elif rec.state == 'avance':
                progress = 75
            elif rec.state == 'payer':
                progress = 100
            else:
                progress = 0
            rec.progress = progress

    # def _achat_count(self):
    #     for rec in self:
    #         rec.achat_count = rec.env['wisdom.achat'].search_count([('reference', '=', rec.id)])

    # calcule reste à payer
    @api.depends('total', 'montant_payer')
    def _compute_reste_payer(self):
        for r in self:
            if not r.total:
                r.reste_payer = 0
            else:
                r.reste_payer = r.total - r.montant_payer

    # contrainte pour les quantité demander est egal à 0
    @api.constrains('montant_payer','total')
    def _check_montant_payer(self):
        for record in self:
            if record.montant_payer >= record.total:
                raise ValidationError(" Vous ne pouvez pas exceler le plafond du total {}".format(record.total))

    # calcule somme total
    @api.depends('frais_commision_total', 'superficie_prix_total', 'frais_dossier')
    def _compute_total(self):
        for r in self:
            if not r.superficie_prix_total:
                r.total = 0
            else:
                r.total = r.frais_commision_total + r.superficie_prix_total + r.frais_dossier

    # calcule superficie_prix
    @api.depends('superficie_unit', 'superficie')
    def _compute_superficie_prix(self):
        for r in self:
            if not r.superficie:
                r.superficie_prix = 0
            else:
                r.superficie_prix = r.superficie * r.superficie_unit

    # calcule superficie_prix apres rabais
    @api.depends('rabais_total', 'superficie_prix')
    def _compute_superficie_prix_total(self):
        for r in self:
            if not r.superficie_prix:
                r.superficie_prix_total = 0
            else:
                r.superficie_prix_total = r.superficie_prix - r.rabais_total


     # calcule frais commission
    @api.depends('superficie_prix','frais_commision')
    def _compute_frais_commision_total(self):
        for r in self:
            if not r.superficie_prix:
                r.frais_commision_total = 0
            else:
                r.frais_commision_total = r.superficie_prix * (r.frais_commision /100)

    # calcule rabais du terrain
    @api.depends('superficie_prix')
    def _compute_rabais_total(self):
        for rec in self:
            if rec.rabais == '1':
              rec.rabais_total = 0
            elif rec.rabais == '5':
              rec.rabais_total = rec.superficie_prix * (5 / 100)
            elif rec.rabais == '6':
              rec.rabais_total = rec.superficie_prix * (6 / 100)
            elif rec.rabais == '7':
              rec.rabais_total = rec.superficie_prix  * (7 / 100)
            elif rec.rabais == '8':
                rec.rabais_total = rec.superficie_prix * (8 / 100)
            elif rec.rabais == '9':
                rec.rabais_total = rec.superficie_prix * (9 / 100)
            elif rec.rabais == '10':
                rec.rabais_total = rec.superficie_prix * (10 / 100)
            elif rec.rabais == '11':
                rec.rabais_total = rec.superficie_prix * (11 / 100)
            elif rec.rabais == '12':
                rec.rabais_total = rec.superficie_prix * (12 / 100)
            elif rec.rabais == '13':
                rec.rabais_total = rec.superficie_prix * (13 / 100)
            elif rec.rabais == '14':
                rec.rabais_total = rec.superficie_prix * (14 / 100)
            elif rec.rabais == '15':
                rec.rabais_total = rec.superficie_prix * (15 / 100)
            else:
                rec.rabais_total = 0

    def action_payer(self):
        for rec in self:
            rec.state = 'payer'

    def action_avance(self):
        for rec in self:
            rec.state = 'avance'

    def action_telephone(self):
        for rec in self:
            if not rec.client_ids.telephone:
                raise ValidationError(_("Veuillez inserer un vrai numero whatsapp"))
            msg = 'Bonjour %s voici votre facture %s' % (rec.client_ids.name, rec.reference)
            whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (rec.client_ids.telephone, msg)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }


    def action_mail(self):
        for rec in self:
             rec.state = 'mail'
        # template_id = self.env.ref('wisdom_international.email_template_achat').id
        # template = self.env['mail.template'].browse(template_id)
        # template.send_mail(self.id, force_send=True)

    def action_verifier(self):
        for rec in self:
            rec.state = 'verifier'

    def action_brouillon(self):
        for rec in self:
            rec.state = 'brouillon'

    def action_annuler(self):
        for rec in self:
            rec.state = 'annuler'

    @api.onchange("employe_ids")
    def _onchange_employe_ids(self):

        if not self.employe_ids:
            self.update(
                {
                    "surnames": False,
                    "telephones": False,
                }
            )
        else:
            self.update(
                {
                    "surnames": self.employe_ids.surnames,
                    "telephones": self.employe_ids.telephones,
                }
            )

    # incrementation sequencial d'identifiant client
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('wisdom.achat') or _('Nouveau')
        res = super(WisdomAchat, self).create(vals)
        return res

    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, field.reference))
        return res

    @api.onchange("client_ids")
    def _onchange_client_ids(self):

        if not self.client_ids:
            self.update(
                {
                    "name": False,
                    "surname": False,
                    "telephone": False,
                    "mail": False,
                    "num_cni": False,
                }
            )
        else:
            self.update(
                {
                    "name": self.client_ids.name,
                    "surname": self.client_ids.surname,
                    "telephone": self.client_ids.telephone,
                    "mail": self.client_ids.mail,
                    "num_cni": self.client_ids.num_cni,
                }
            )