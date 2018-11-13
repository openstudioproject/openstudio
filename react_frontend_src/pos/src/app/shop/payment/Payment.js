import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import PageTemplate from "../../../components/PageTemplate"
import Box from "../../../components/ui/Box"
import BoxBody from "../../../components/ui/BoxBody"
import BoxHeader from "../../../components/ui/BoxHeader"
import ButtonBack from "../../../components/ui/ButtonBack"

import PaymentMethods from "./PaymentMethods"
import PaymentTotal from "./PaymentTotal"
import CustomerButton from "../components/CustomerButtonContainer"
import ButtonValidate from "./ButtonValidate"

class Payment extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        state: PropTypes.object,
        total: PropTypes.int,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.shop.payment.page_title' })
        )
    }

    onClickPaymentMethod(id) {
        console.log(id)
        this.props.setSelectedPaymentMethod(id)
    }

    onClickValidate() {
        console.log('validate clicked')
        this.props.submitCart(this.props.state)
        this.props.history.push('/shop/validation')
    }
    
    render() {
        const history = this.props.history
        const total = this.props.total
        const selected_method = this.props.selected_method

        return (
            <PageTemplate app_state={this.props.app}>
                <div className="row">
                    <div className="col-md-12">
                        <ButtonValidate selectedID={selected_method}
                                        total={total}
                                        onClick={this.onClickValidate.bind(this)} />
                        <ButtonBack onClick={() => history.push('/shop/products')}>
                            Cancel
                        </ButtonBack>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-4">
                        <Box>
                            {/* <BoxHeader title="Payment methods" /> */}
                            <BoxBody>
                                <PaymentMethods methods={this.props.app.payment_methods}
                                                selected_method={selected_method}
                                                onClick={this.onClickPaymentMethod.bind(this)} />
                            </BoxBody>
                        </Box>
                    </div>
                    <div className="col-md-8">
                        <Box>
                            {/* <BoxHeader title="Enter payment" /> */}
                            <BoxBody>
                                <div className="row">
                                    <div className="col-md-12">
                                        <PaymentTotal methods={this.props.app.payment_methods}
                                                      total={total}
                                                      selected_method={selected_method} />
                                    </div>
                                </div>

                                <div className="row">
                                    <div className="col-md-3">
                                        <CustomerButton />
                                    </div>
                                </div>
                            </BoxBody>
                        </Box>
                    </div>
                </div>
            </PageTemplate>
        )
    }
}

export default Payment
