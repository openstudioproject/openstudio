import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../../components/PageTemplate"

import RevenueList from "./RevenueList"
import RevenueTotal from "./RevenueTotal"

class Revenue extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchRevenue: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        attendance: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )

        this.props.fetchRevenue(this.props.match.params.clsID)
    }
    
    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.revenue.loaded) ? 
                        <div>Loading revenue, please wait...</div> :
                        <div className="row">
                            <div class="col-md-6">
                                <RevenueList data={this.props.revenue.data}
                                            currency_symbol={this.props.settings.currency_symbol} />
                            </div>
                            <div class="col-md-6">
                                <RevenueTotal data={this.props.revenue.data}
                                              currency_symbol={this.props.settings.currency_symbol} />
                            </div>
                        </div>
                }
            </PageTemplate>
        )
    }
}

export default Revenue
