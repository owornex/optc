# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import pluck, compose

from optic_store.doc_events.sales_order import get_parts


def execute():
    settings = frappe.get_single("Optical Store Settings")
    frames = map(lambda x: x.item_group, settings.frames)
    lenses = map(lambda x: x.item_group, settings.lens)

    for doctype in ["Sales Order", "Sales Invoice"]:
        for doc in _get_docs(doctype):
            if doc.orx_type == "Spectacles":
                frame, lens_right, lens_left = get_parts(doc.items)
                for item in doc.items:
                    if not item.os_spec_part:
                        if not frame and item.item_group in frames:
                            frappe.db.set_value(
                                item.doctype, item.name, "os_spec_part", "Frame"
                            )
                            frame = item
                        elif not lens_right and item.item_group in lenses:
                            frappe.db.set_value(
                                item.doctype, item.name, "os_spec_part", "Lens Right"
                            )
                            lens_right = item
                        elif not lens_left and item.item_group in lenses:
                            frappe.db.set_value(
                                item.doctype, item.name, "os_spec_part", "Lens Left"
                            )
                            lens_left = item


def _get_docs(doctype):
    return compose(
        partial(map, lambda x: frappe.get_doc(doctype, x)),
        partial(pluck, "name"),
        partial(frappe.get_all, doctype),
    )()
