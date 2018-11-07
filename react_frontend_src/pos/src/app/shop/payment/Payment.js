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

class Payment extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        total: PropTypes.int,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.shop.payment.page_title' })
        )
    }

    onClickPaymentMethod(id) {
        console.log(id)
    }
    
    render() {
        const history = this.props.history
        const total = this.props.total

        return (
            <PageTemplate app_state={this.props.app}>
                <div className="row">
                    <div className="col-md-12">
                        <ButtonBack onClick={() => history.push('/shop/products')}>
                            Cancel
                        </ButtonBack>
                        Cancel & validate
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-4">
                        <Box>
                            <BoxHeader title="Payment methods" />
                            <BoxBody>
                                <PaymentMethods methods={this.props.app.payment_methods}
                                                onClick={this.onClickPaymentMethod.bind(this)} />
                            </BoxBody>
                        </Box>
                    </div>
                    <div className="col-md-8">
                        <Box>
                            <BoxHeader title="Enter payment" />
                            <BoxBody>
                                <PaymentTotal total={total} />
                                Payment, numpad & customer display
                            </BoxBody>
                        </Box>
                    </div>
                </div>
            </PageTemplate>
        )
    }
}

export default Payment
