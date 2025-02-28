from odoo import fields, models


class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    project_id = fields.Many2one("project.project")
    project_code = fields.Char(related="project_id.project_code")

    def action_budget_confirm(self):
        super(CrossoveredBudget, self).action_budget_confirm()
        code = self.env["ir.sequence"].next_by_code("project.project")
        self.project_id.project_code = code

class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    project_line_id = fields.Many2one("project.line")