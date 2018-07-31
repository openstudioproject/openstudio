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
        <div>{this.props.intl.formatMessage({ id:"app.pos.checkin.revenue.loading" })}</div> :
                        <div className="row">
                            <div className="col-md-6">
                                <RevenueList data={this.props.revenue.data}
                                             intl={this.props.intl}
                                             currency_symbol={this.props.settings.currency_symbol} />
                            </div>
                            <div className="col-md-6">
                                <RevenueTotal data={this.props.revenue.data}
                                              intl={this.props.intl}
                                              currency_symbol={this.props.settings.currency_symbol} />
                            </div>
                        </div>
                }
            </PageTemplate>
        )
    }
}

export default Revenue
