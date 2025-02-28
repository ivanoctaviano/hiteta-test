from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    line_ids = fields.One2many("project.line", "project_id", copy=False)
    budget_post_id = fields.Many2one("account.budget.post", string="Budgetary Position")
    budget_id = fields.Many2one("crossovered.budget")
    project_code = fields.Char()
    invisible_stage_id = fields.Many2one(
        comodel_name="project.project.stage",
        compute="_compute_invisible_stage",
        help="Technical field to get the domain invisible stage",
    )
    invisible_confirm = fields.Boolean(
        compute="_compute_invisible_button",
        help="Technical field to invisible button confirm",
    )
    invisible_approve_reject_tier_1 = fields.Boolean(
        compute="_compute_invisible_button",
        help="Technical field to invisible button approve and reject tier 1",
    )
    invisible_approve_reject_tier_2 = fields.Boolean(
        compute="_compute_invisible_button",
        help="Technical field to invisible button approve and reject tier 2",
    )

    @api.depends("stage_id")
    def _compute_invisible_stage(self):
        for project in self:
            project.invisible_stage_id = project.env.ref("project.project_project_stage_3")

    @api.depends("stage_id")
    def _compute_invisible_button(self):
        to_do = self.env.ref("project.project_project_stage_0").id
        in_progress = self.env.ref("project.project_project_stage_1").id
        in_review = self.env.ref("central_group_project.project_project_stage_in_review").id
        done = self.env.ref("project.project_project_stage_2").id
        for project in self:
            project.invisible_confirm = True
            project.invisible_approve_reject_tier_1 = True
            project.invisible_approve_reject_tier_2 = True
            if project.stage_id.id == to_do:
                project.invisible_confirm = False
            elif project.stage_id.id == in_progress:
                project.invisible_approve_reject_tier_1 = False
            elif project.stage_id.id == in_review:
                project.invisible_approve_reject_tier_2 = False

    def button_confirm(self):
        if not self.line_ids.filtered(lambda line: line.display_type not in ("line_section", "line_note")):
            raise UserError(_("You need to add a RAB line before confirm."))
        self.stage_id = self.env.ref("project.project_project_stage_1")

    def button_approve_tier_1(self):
        self.stage_id = self.env.ref("central_group_project.project_project_stage_in_review")

    def button_reject_tier_1(self):
        self.stage_id = self.env.ref("project.project_project_stage_3")

    def button_approve_tier_2(self):
        self.stage_id = self.env.ref("project.project_project_stage_2")
        budget_id = self.env["crossovered.budget"].create({
            "name": self.name,
            "date_from": self.date_start,
            "date_to": self.date,
            "project_id": self.id,
            "crossovered_budget_line_ids": [(0, 0, {
                "general_budget_id": self.budget_post_id.id,
                "analytic_account_id": self.analytic_account_id.id,
                "planned_amount": line.price_subtotal,
                "date_from": self.date_start,
                "date_to": self.date,
                "project_line_id": line.id,
            }) for line in self.line_ids.filtered(lambda line: line.display_type not in ("line_section", "line_note"))]
        })
        self.budget_id = budget_id

    def button_reject_tier_2(self):
        self.stage_id = self.env.ref("project.project_project_stage_3")

class ProjectLine(models.Model):
    _name = "project.line"
    _description = "Rencana Anggaran Biaya Project"

    project_id = fields.Many2one("project.project")
    sequence = fields.Integer(string="Sequence", default=10)
    display_type = fields.Selection(
        selection=[
            ("line_section", "Section"),
            ("line_note", "Note"),
        ],
        default=False)
    name = fields.Char("Jenis Pekerjaan")
    quantity = fields.Integer()
    product_uom = fields.Many2one("uom.uom")
    price_unit = fields.Float()
    currency_id = fields.Many2one("res.currency", "Currency", required=True, default=lambda self: self.env.company.currency_id.id)
    price_subtotal = fields.Monetary(compute="compute_subtotal", string="Subtotal", store=True)

    @api.depends("quantity", "price_unit")
    def compute_subtotal(self):
        """
        compute prf subtotal
        """
        for record in self:
            record.price_subtotal = record.quantity * record.price_unit