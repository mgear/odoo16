# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import urllib.parse

from odoo import _, exceptions, http, tools
from odoo.http import request, Response
from odoo.tools import consteq
from lxml import etree
from werkzeug.exceptions import BadRequest, NotFound


class MassMailController(http.Controller):

    def _valid_unsubscribe_token(self, mailing_id, res_id, email, token):
        if not (mailing_id and res_id and email and token):
            return False
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        return consteq(mailing._unsubscribe_token(res_id, email), token)

    def _log_blacklist_action(self, blacklist_entry, mailing_id, description):
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        model_display = mailing.mailing_model_id.display_name
        blacklist_entry._message_log(body=description + " ({})".format(model_display))

    # ------------------------------------------------------------
    # SUBSCRIPTION MANAGEMENT
    # ------------------------------------------------------------

    # csrf is disabled here because it will be called by the MUA with unpredictable session at that time
    @http.route(['/mail/mailing/<int:mailing_id>/unsubscribe_oneclick'], type='http', website=True, auth='public',
                methods=["POST"], csrf=False)
    def mailing_unsubscribe_oneclick(self, mailing_id, email=None, res_id=None, token="", **post):
        self.mailing(mailing_id, email=email, res_id=res_id, token=token, **post)
        return Response(status=200)

    @http.route('/mailing/<int:mailing_id>/confirm_unsubscribe', type='http', website=True, auth='public')
    def mailing_confirm_unsubscribe(self, mailing_id, email=None, res_id=None, token="", **post):
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        # Check access (note that this will also raise AccessDenied if the mailing does not exist)
        if not self._valid_unsubscribe_token(mailing_id, res_id, email, str(token)):
            raise exceptions.AccessDenied()

        unsubscribed_str = _("Are you sure you want to unsubscribe from our mailing list?")
        # Display list name if list is public
        if mailing.mailing_model_real == 'mailing.contact':
            unsubscribed_lists = ', '.join(mailing_list.name for mailing_list in mailing.contact_list_ids if mailing_list.is_public)
            if unsubscribed_lists:
                unsubscribed_str = _(
                    'Are you sure you want to unsubscribe from the mailing list "%(unsubscribed_lists)s"?',
                    unsubscribed_lists=unsubscribed_lists
                )
        unsubscribe_btn = _("Unsubscribe")

        template = etree.fromstring("""
            <t t-call="mass_mailing.layout">
                <div class="container o_unsubscribe_form">
                    <form action="/mailing/confirm_unsubscribe" method="POST" class="col-lg-6 offset-lg-3 mt-4">
                        <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
                        <input type="hidden" name="email" t-att-value="email"/>
                        <input type="hidden" name="mailing_id" t-att-value="mailing_id"/>
                        <input type="hidden" name="res_id" t-att-value="res_id"/>
                        <input type="hidden" name="token" t-att-value="token"/>
                        <div id="info_state"  class="alert alert-success">
                            <div class="text-center">
                                <p t-out="unsubscribed_str"/>
                                <button type="submit" class="btn btn-primary" t-out="unsubscribe_btn"/>
                            </div>
                        </div>
                    </form>
                </div>
            </t>
        """)
        return request.env['ir.qweb']._render(template, {
            'main_object': mailing,
            'token': token,
            'email': email,
            'mailing_id': mailing_id,
            'unsubscribed_str': unsubscribed_str,
            'res_id': res_id,
            'unsubscribe_btn': unsubscribe_btn,
        })

    # kept for backwards compatibility, must eventually be merged with mailing/<mailing_id>/unsubscribe
    @http.route('/mailing/confirm_unsubscribe', type='http', website=True, auth='public', methods=['POST'])
    def mailing_confirm_unsubscribe_post(self, mailing_id, email=None, res_id=None, token="", **post):
        url_params = urllib.parse.urlencode({'email': email, 'res_id': res_id, 'token': token})
        url = f'/mail/mailing/{int(mailing_id)}/unsubscribe?{url_params}'
        return request.redirect(url)

    # todo: merge this route with /mail/mailing/confirm_unsubscribe on next minor version
    @http.route(['/mail/mailing/<int:mailing_id>/unsubscribe'], type='http', website=True, auth='public')
    def mailing(self, mailing_id, email=None, res_id=None, token="", **post):
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        if mailing.exists():
            res_id = res_id and int(res_id)
            if not self._valid_unsubscribe_token(mailing_id, res_id, email, str(token)):
                raise exceptions.AccessDenied()

            if mailing.mailing_model_real == 'mailing.contact':
                # Unsubscribe directly + Let the user choose their subscriptions
                mailing.update_opt_out(email, mailing.contact_list_ids.ids, True)

                contacts = request.env['mailing.contact'].sudo().search([('email_normalized', '=', tools.email_normalize(email))])
                subscription_list_ids = contacts.mapped('subscription_list_ids')
                # In many user are found : if user is opt_out on the list with contact_id 1 but not with contact_id 2,
                # assume that the user is not opt_out on both
                # TODO DBE Fixme : Optimise the following to get real opt_out and opt_in
                opt_out_list_ids = subscription_list_ids.filtered(lambda rel: rel.opt_out).mapped('list_id')
                opt_in_list_ids = subscription_list_ids.filtered(lambda rel: not rel.opt_out).mapped('list_id')
                opt_out_list_ids = set([list.id for list in opt_out_list_ids if list not in opt_in_list_ids])

                unique_list_ids = set([list.list_id.id for list in subscription_list_ids])
                list_ids = request.env['mailing.list'].sudo().browse(unique_list_ids).filtered('active')
                unsubscribed_list = ', '.join(str(list.name) for list in mailing.contact_list_ids if list.is_public)
                return request.render('mass_mailing.page_unsubscribe', {
                    'contacts': contacts,
                    'list_ids': list_ids,
                    'opt_out_list_ids': opt_out_list_ids,
                    'unsubscribed_list': unsubscribed_list,
                    'email': email,
                    'mailing_id': mailing_id,
                    'res_id': res_id,
                    'show_blacklist_button': request.env['ir.config_parameter'].sudo().get_param('mass_mailing.show_blacklist_buttons'),
                })
            else:
                opt_in_lists = request.env['mailing.contact.subscription'].sudo().search([
                    ('contact_id.email_normalized', '=', email),
                    ('opt_out', '=', False)
                ]).mapped('list_id').filtered('active')
                blacklist_rec = request.env['mail.blacklist'].sudo()._add(email)
                self._log_blacklist_action(
                    blacklist_rec, mailing_id,
                    _("""Requested blacklisting via unsubscribe link."""))
                return request.render('mass_mailing.page_unsubscribed', {
                    'email': email,
                    'mailing_id': mailing_id,
                    'res_id': res_id,
                    'list_ids': opt_in_lists,
                    'show_blacklist_button': request.env['ir.config_parameter'].sudo().get_param(
                        'mass_mailing.show_blacklist_buttons'),
                })
        return request.redirect('/web')

    @http.route('/mail/mailing/unsubscribe', type='json', auth='public')
    def unsubscribe(self, mailing_id, opt_in_ids, opt_out_ids, email, res_id, token):
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        if mailing.exists():
            if not self._valid_unsubscribe_token(mailing_id, res_id, email, token):
                return 'unauthorized'
            mailing.update_opt_out(email, opt_in_ids, False)
            mailing.update_opt_out(email, opt_out_ids, True)
            return True
        return 'error'

    @http.route('/mailing/feedback', type='json', auth='public')
    def send_feedback(self, mailing_id, res_id, email, feedback, token):
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        if mailing.exists() and email:
            if not self._valid_unsubscribe_token(mailing_id, res_id, email, token):
                return 'unauthorized'
            model = request.env[mailing.mailing_model_real]
            records = model.sudo().search([('email_normalized', '=', tools.email_normalize(email))])
            for record in records:
                record.sudo().message_post(body=_("Feedback from %(email)s: %(feedback)s", email=email, feedback=feedback))
            return bool(records)
        return 'error'

    @http.route(['/unsubscribe_from_list'], type='http', website=True, multilang=False, auth='public', sitemap=False)
    def unsubscribe_placeholder_link(self, **post):
        """Dummy route so placeholder is not prefixed by language, MUST have multilang=False"""
        raise NotFound()

    # ------------------------------------------------------------
    # TRACKING
    # ------------------------------------------------------------

    @http.route('/mail/track/<int:mail_id>/<string:token>/blank.gif', type='http', auth='public')
    def track_mail_open(self, mail_id, token, **post):
        """ Email tracking. """
        if not consteq(token, tools.hmac(request.env(su=True), 'mass_mailing-mail_mail-open', mail_id)):
            raise BadRequest()

        request.env['mailing.trace'].sudo().set_opened(domain=[('mail_mail_id_int', 'in', [mail_id])])
        response = Response()
        response.mimetype = 'image/gif'
        response.data = base64.b64decode(b'R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')

        return response

    @http.route('/r/<string:code>/m/<int:mailing_trace_id>', type='http', auth="public")
    def full_url_redirect(self, code, mailing_trace_id, **post):
        # don't assume geoip is set, it is part of the website module
        # which mass_mailing doesn't depend on
        country_code = request.geoip.get('country_code')

        request.env['link.tracker.click'].sudo().add_click(
            code,
            ip=request.httprequest.remote_addr,
            country_code=country_code,
            mailing_trace_id=mailing_trace_id
        )
        redirect_url = request.env['link.tracker'].get_url_from_code(code)
        if not redirect_url:
            raise NotFound()
        return request.redirect(redirect_url, code=301, local=False)

    # ------------------------------------------------------------
    # MAILING MANAGEMENT
    # ------------------------------------------------------------

    @http.route('/mailing/report/unsubscribe', type='http', website=True, auth='public')
    def turn_off_mailing_reports(self, token, user_id):
        if not token or not user_id:
            raise NotFound()
        user_id = int(user_id)
        correct_token = consteq(token, request.env['mailing.mailing']._get_unsubscribe_token(user_id))
        user = request.env['res.users'].sudo().browse(user_id)
        if correct_token and user.has_group('mass_mailing.group_mass_mailing_user'):
            request.env['ir.config_parameter'].sudo().set_param('mass_mailing.mass_mailing_reports', False)
            if user.has_group('base.group_system'):
                menu_id = request.env.ref('mass_mailing.menu_mass_mailing_global_settings').id
                return request.render('mass_mailing.mailing_report_deactivated', {'menu_id': menu_id})
            return request.render('mass_mailing.mailing_report_deactivated')
        raise NotFound()

    @http.route(['/mailing/<int:mailing_id>/view'], type='http', website=True, auth='public')
    def view(self, mailing_id, email=None, res_id=None, token=""):
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        if mailing.exists():
            res_id = int(res_id) if res_id else False
            if not self._valid_unsubscribe_token(mailing_id, res_id, email, str(token)) and not request.env.user.has_group('mass_mailing.group_mass_mailing_user'):
                raise exceptions.AccessDenied()

            html_markupsafe = mailing._render_field('body_html', [res_id])[res_id]
            # Update generic URLs (without parameters) to final ones
            html_markupsafe = html_markupsafe.replace('/unsubscribe_from_list',
                                                      mailing._get_unsubscribe_url(email, res_id))

            return request.render('mass_mailing.view', {
                    'body': html_markupsafe,
                })

        return request.redirect('/web')

    # ------------------------------------------------------------
    # BLACKLIST
    # ------------------------------------------------------------

    @http.route('/mailing/blacklist/check', type='json', auth='public')
    def blacklist_check(self, mailing_id, res_id, email, token):
        if not self._valid_unsubscribe_token(mailing_id, res_id, email, token):
            return 'unauthorized'
        if email:
            record = request.env['mail.blacklist'].sudo().with_context(active_test=False).search([('email', '=', tools.email_normalize(email))])
            if record['active']:
                return True
            return False
        return 'error'

    @http.route('/mailing/blacklist/add', type='json', auth='public')
    def blacklist_add(self, mailing_id, res_id, email, token):
        if not self._valid_unsubscribe_token(mailing_id, res_id, email, token):
            return 'unauthorized'
        if email:
            blacklist_rec = request.env['mail.blacklist'].sudo()._add(email)
            self._log_blacklist_action(
                blacklist_rec, mailing_id,
                _("""Requested blacklisting via unsubscription page."""))
            return True
        return 'error'

    @http.route('/mailing/blacklist/remove', type='json', auth='public')
    def blacklist_remove(self, mailing_id, res_id, email, token):
        if not self._valid_unsubscribe_token(mailing_id, res_id, email, token):
            return 'unauthorized'
        if email:
            blacklist_rec = request.env['mail.blacklist'].sudo()._remove(email)
            self._log_blacklist_action(
                blacklist_rec, mailing_id,
                _("""Requested de-blacklisting via unsubscription page."""))
            return True
        return 'error'

    # ------------------------------------------------------------
    # MISCELLANEOUS
    # ------------------------------------------------------------

    @http.route('/mailing/get_preview_assets', type='json', auth='user')
    def get_mobile_preview_styling(self):
        """ This route allows a rpc call to get the styling needed for email template conversion.
        We do this to avoid duplicating the template."""
        if not request.env.user.has_group('mass_mailing.group_mass_mailing_user'):
            raise NotFound
        return request.env['ir.qweb']._render('mass_mailing.iframe_css_assets_edit')
