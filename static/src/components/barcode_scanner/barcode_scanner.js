/** @odoo-module **/
const { Component } = owl
const { onMounted } = owl.hooks
import core from 'web.core';
import { useBus } from "@web/core/utils/hooks";

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { DataDashboard } from "../data_dashboard";

patch(DataDashboard.prototype, 'data_dashboard',{
    setup(){
        this._super()
        Component.env.bus.on('barcode_scanned', this, this._onBarcodeScanned);

    },
    _onBarcodeScanned(barcode){
        Component.env.bus.off('barcode_scanned', this, this._onBarcodeScanned);
        this._viewInputInfo(barcode)
//        console.log('_onBarcodeScanned',barcode)
        Component.env.bus.on('barcode_scanned', this, this._onBarcodeScanned);

    },
    async _viewInputInfo(document_no){
        const res_id = await this.orm.searchRead("sd_payaneh_nafti.input_info", [['document_no', '=', document_no]],['id'])
        console.log('_viewInputInfo', document_no, res_id)

        let today = moment().locale('en').format('YYYY/MM/DD')
        let domain = [['document_no', '=', document_no]]
        this.actionService.doAction({
            name: "This day Requests",
            res_model: "sd_payaneh_nafti.input_info",
            res_id: res_id[0].id,
            views: [ [false, "form"]],
            type: "ir.actions.act_window",
            view_mode: "form",
            domain: domain,
//            context: {'search_default_meter_no_group': 1},
            target: "new",
        });
    },

})