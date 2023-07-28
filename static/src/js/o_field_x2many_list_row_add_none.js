/** @odoo-module **/

import Dialog from 'web.Dialog';
import FormView from 'web.FormView';
import FormController from 'web.FormController';
import { bus, _t } from 'web.core';
import { device } from 'web.config';
import viewRegistry from 'web.view_registry';

const Many2manyNoAddDeleteFormController = FormController.extend({
    events: {
//        'mouseover': '_ono_list_view1',
//        'mousemove': '_ono_list_view1',
    },
    start: function(){
        const self = this;
        return this._super.apply(this, arguments).then(function () {
            const row_add = self.el.querySelector('.o_field_x2many_list_row_add')
            row_add != undefined ?  row_add.classList.add('d-none') : '';
            const record_remove = self.el.querySelectorAll('.o_list_record_remove')
            record_remove != undefined ?  record_remove.forEach(rec => rec.classList.add('d-none') ) : '';


        });
    },
    _applyChanges: function (dataPointID, changes, event) {
        const self = this;
//        console.log('before',dataPointID, changes, event)


        return this._super(...arguments).then(() => {
            setTimeout(function(){
                const row_add = self.el.querySelector('.o_field_x2many_list_row_add')
                row_add != undefined ?  row_add.classList.add('d-none') : '';
                const record_remove = self.el.querySelectorAll('.o_list_record_remove')
                record_remove != undefined ?  record_remove.forEach(rec => rec.classList.add('d-none') ) : '';
            },200);

            const row_add = self.el.querySelector('.o_field_x2many_list_row_add')
            row_add != undefined ?  row_add.classList.add('d-none') : '';
            const record_remove = self.el.querySelectorAll('.o_list_record_remove')
            record_remove != undefined ?  record_remove.forEach(rec => rec.classList.add('d-none') ) : '';
//            console.log('after',row_add)
        });
    },
    _ono_list_view: function(){
            const self = this;
//        console.log('_ono_list_view')
            const row_add = self.el.querySelector('.o_field_x2many_list_row_add')
            row_add != undefined ?  row_add.classList.add('d-none') : '';
            const record_remove = self.el.querySelectorAll('.o_list_record_remove')
            record_remove != undefined ?  record_remove.forEach(rec => rec.classList.add('d-none') ) : '';
//            console.log('after',row_add)
    },
    _onDomUpdated() {
                console.log('_onDomUpdated')

    },
});

export const Many2manyNoAddDeleteFormView = FormView.extend({
    config: Object.assign({}, FormView.prototype.config, {
        Controller: Many2manyNoAddDeleteFormController,
    }),
});


viewRegistry.add('many2many_no_add_delete', Many2manyNoAddDeleteFormView);
