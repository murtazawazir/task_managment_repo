from odoo import models, api

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.depends('composition_mode', 'model', 'res_domain', 'res_ids', 'template_id')
    def _compute_attachment_ids(self):
        """
        Inherit the attachment_ids computation logic
        :return:
        """
        for composer in self:
            super(MailComposer, composer)._compute_attachment_ids()
            # Check if the model is sale.order, if so, get the excel attachment and add it
            # to the mail attachments
            if composer.model == 'sale.order':
                for id in eval(composer.res_ids):
                    so = self.env[composer.model].browse(id)
                    if so:
                        xl_att_id = so.create_get_quotation_excel_id()
                        if xl_att_id not in composer.attachment_ids.ids:
                            att_ids = composer.attachment_ids.ids
                            att_ids.append(xl_att_id)
                            composer.attachment_ids = att_ids
