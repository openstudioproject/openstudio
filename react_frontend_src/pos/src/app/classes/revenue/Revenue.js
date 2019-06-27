import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../../components/PageTemplate"
import ButtonBack from "../../../components/ui/ButtonBack"

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
        data: PropTypes.object
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.classes.page_title' })
        )

        this.props.fetchRevenueAndTeacherPayment(this.props.match.params.clsID)
    }

    onClickBtnCancel() {
        console.log('button cancel clicked')
        const clsID = this.props.match.params.clsID
        const history = this.props.history

        history.push(`/classes/attendance/${clsID}`)
    }
    
    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.data.revenue_loaded || !this.props.data.teacher_payment_loaded) ? 
                        <div>{this.props.intl.formatMessage({ id:"app.pos.classes.revenue.loading" })}</div> :
                        <div>
                            <div className="row header-tools">
                                <div className="col-md-12">
                                    <ButtonBack onClick={this.onClickBtnCancel.bind(this)}>
                                        Back
                                    </ButtonBack>    
                                </div>
                            </div>
                            <div className="row">
                                <div className="col-md-8">
                                    <RevenueList revenue={this.props.data.revenue}
                                                intl={this.props.intl}
                                                currency_symbol={this.props.settings.currency_symbol} />
                                </div>
                                <div className="col-md-4">
                                    <RevenueTotal revenue={this.props.data.revenue}
                                                teacher_payment={this.props.data.teacher_payment}
                                                teacher_payment_verifying={this.props.data.teacher_payment_verifying}
                                                intl={this.props.intl}
                                                currency_symbol={this.props.settings.currency_symbol}
                                                onVerify={() => this.props.verifyTeacherPayment(this.props.data.teacher_payment.data.id)} />
                                </div>
                            </div>
                        </div>
                }
            </PageTemplate>
        )
    }
}

export default Revenue
