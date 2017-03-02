# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class BOQ(Document):
	pass



@frappe.whitelist()
def check_active_boq(project):
    if project:
        boq = frappe.get_all("BOQ", filters={"project": project, "is_active": 1})
        if len(boq) >= 1:
            frappe.throw(_("Currently BOQ {0} is active. can't create new BOQ".format(boq[0].name)))
