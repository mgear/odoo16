# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.l10n_ch.models.res_bank import _is_l10n_ch_postal
from odoo.tools.misc import str2bool


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    def _find_or_create_bank_account(self):
        if self.company_id.account_fiscal_country_id.code in ('CH', 'LI') and _is_l10n_ch_postal(self.account_number):
            bank_account = self.env['res.partner.bank'].search(
                [('company_id', '=', self.company_id.id),
                 ('sanitized_acc_number', 'like', self.account_number + '%'),
                 ('partner_id', '=', self.partner_id.id)])
            if not bank_account and not str2bool(
                    self.env['ir.config_parameter'].sudo().get_param("account.skip_create_bank_account_on_reconcile")
            ):
                bank_account = self.env['res.partner.bank'].create({
                    'company_id': self.company_id.id,
                    'acc_number': self.account_number + " " + self.partner_id.name,
                    'partner_id': self.partner_id.id
                })
            return bank_account
        else:
            return super()._find_or_create_bank_account()
