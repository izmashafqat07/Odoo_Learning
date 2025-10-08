# models/res_users.py
from odoo import models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def unlink(self):
        # jin users ko delete kar rahe hain unke partner collect kar lo
        partners_to_check = self.env['res.partner']
        for user in self:
            if user.partner_id:
                partners_to_check |= user.partner_id

        # pehle user delete karo (super call)
        res = super().unlink()

        # ab un partners ko nikaalo jo ab kisi user se linked nahi rahe (orphan)
        orphan_partners = partners_to_check.filtered(lambda p: not p.user_ids)

        # HARD DELETE with SAFE FALLBACK to archive
        for partner in orphan_partners:
            try:
                # kuch extra safety: companies ya parents ko chhor do (optional)
                if partner.is_company or partner.child_ids:
                    # company ya parent/contact tree ho to archive better
                    partner.active = False
                    continue

                partner.unlink()  # try hard delete
            except Exception:
                # agar dependencies ki wajah se delete na ho, to archive kar do
                partner.active = False

        return res
