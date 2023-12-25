/** @odoo-module */
    import { registry } from "@web/core/registry"
    const { Component, useRef, onMounted, useState } = owl
    const { useEnv, onWillStart } = owl.hooks;

    import { useService } from "@web/core/utils/hooks"
    import { DataCards } from "./data_cards/data_cards"


export class DataDashboard extends Component {
    setup(){
        this.state = useState({
            spgr: {
                value: 0.7722,
                status: "1402/10/01",
            },
            contracts: {
                value: 0,
                status: "",
            }
        })
        this.orm = useService("orm")
        onWillStart(async ()=>{
            await this.getSpgr()
            await this.getContracts()
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
        console.log('spgr:', contracts, typeof contracts, )
//        this.state.spgr.status = moment(spgr[0].spgr_date).format("jYYYY/jMM/jDD");
        this.state.contracts.value = contracts.open_contracts;
    }
}
DataDashboard.template = "data_dashboard"
DataDashboard.components = { DataCards }
registry.category("actions").add("data_dashboard", DataDashboard)
