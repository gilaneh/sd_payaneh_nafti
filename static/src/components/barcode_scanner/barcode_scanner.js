/** @odoo-module **/
const { Component } = owl
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { DataDashboard } from "../data_dashboard";

export class DataDashboardBarcode extends DataDashboard{
    setup(){
    super.setup();
        console.log('DataDashboardBarcode', this)
    }
}