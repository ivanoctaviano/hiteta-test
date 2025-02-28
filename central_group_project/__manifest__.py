# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Central Group Project",
    "version" : "1.0",
    "author": "Ivan Octaviano",
    "description": """
        Manage Project
    """,
    "depends" : ["base", "project", "account_budget_oca"],
    "data": [
        "security/ir.model.access.csv",
        "security/group.xml",
        "data/project_data.xml",
        "views/account_budget.xml",
        "views/project_project.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}