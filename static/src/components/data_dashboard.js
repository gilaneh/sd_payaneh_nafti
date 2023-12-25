/** @odoo-module */
    import { registry } from "@web/core/registry"
    const { Component, useRef, onMounted, useState } = owl
    const { useEnv, onWillStart } = owl.hooks;

    import { useService } from "@web/core/utils/hooks"
    import { DataCards } from "./data_cards/data_cards"
    const { DateTime, Settings } = luxon;

    const SERVER_DATE_FORMAT = "yyyy-MM-dd";

export class DataDashboard extends Component {
    setup(){
//        console.log('company:', this.env.services)

        this.state = useState({
            spgr: {
                value: 0.7722,
                status: "1402/10/01",
            },
            contracts: {
                value: 0,
                status: "",
            },
            open_requests: {
                value: 0,
                status: "",
            },
            this_day_requests_count: {
                value: 110,
                status: "",
            },
            this_day_requests_amount: {
                value: 110,
                status: "",
            },
            delivered_month_amount: {
                value: 2110,
                status: "",
            },
        })

        this.orm = useService("orm")
        this.actionService = useService("action")

        onWillStart(async ()=>{
            await this.getSpgr()
            await this.getContracts()
            await this.getRequests()
        })
    }
    async getSpgr(){
        const spgr = await this.orm.searchRead("sd_payaneh_nafti.spgr", [['active', '=', 'True']],['spgr', 'spgr_date'])
//        console.log('spgr:', spgr, spgr[0].spgr, spgr[0].spgr_date)
        this.state.spgr.status = moment(spgr[0].spgr_date).format("jYYYY/jMM/jDD");
        this.state.spgr.value = spgr[0].spgr;
    }
    async getContracts(){
        let contracts = await this.orm.call("sd_payaneh_nafti.contract_registration", "get_contracts", [],{})
        contracts = JSON.parse(contracts)
//        console.log('contracts:', contracts, typeof contracts, )
//        this.state.spgr.status = moment(spgr[0].spgr_date).format("jYYYY/jMM/jDD");
        this.state.contracts.value = contracts.open_contracts;
    }
    async getRequests(){
        let requests = await this.orm.call("sd_payaneh_nafti.input_info", "get_requests", [],{})
        requests = JSON.parse(requests)
//        console.log('requests:', requests,  )
//        this.state.spgr.status = moment(spgr[0].spgr_date).format("jYYYY/jMM/jDD");
        this.state.open_requests.value = requests.open_requests;
        this.state.this_day_requests_count.value = requests.this_day_requests_count;
        this.state.this_day_requests_amount.value = requests.this_day_requests_amount;
    }
    viewContracts(){
        this.actionService = useService("action")
        let today = moment().locale('en').format('YYYY/MM/DD')
        console.log('today:',  today, moment.locale())
        let domain = ['|','|',['end_date', '>', today],
        ['first_extend_end_date', '>', today],
        ['second_extend_end_date', '>', today],
        ]
//        this.orm = useService("orm")
//        this.orm.call("sd_payaneh_nafti.contract_registration", "dash_get_inputs", [],{})
//        console.log('viewContracts', this.orm, this.actionService, )
//          this.actionService.doAction("sd_payaneh_nafti.action_window_contract_registration")
        this.actionService.doAction({
            name: "Ongoing Contracts",
            res_model: "sd_payaneh_nafti.contract_registration",
//            res_id: this.actionId,
            views: [[false, "list"], [false, "form"]],
            type: "ir.actions.act_window",
            view_mode: "list",
            domain: domain,
            target: "current",
        });
    }
    viewThisDayRequests(){
        this.actionService = useService("action")
        let today = moment().locale('en').format('YYYY/MM/DD')
        let domain = [['request_date', '=', today]]
        this.actionService.doAction({
            name: "This day Requests",
            res_model: "sd_payaneh_nafti.input_info",
//            res_id: this.actionId,
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            view_mode: "list",
            domain: domain,
            target: "current",
        });
    }

    viewSpgr(){
        console.log('DateTime:', DateTime.fr)
    }
}

DataDashboard.template = "data_dashboard"
DataDashboard.components = { DataCards }
registry.category("actions").add("data_dashboard", DataDashboard)
