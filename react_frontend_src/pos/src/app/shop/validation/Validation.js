import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import PageTemplate from "../../../components/PageTemplate"
import Box from "../../../components/ui/Box"
import BoxBody from "../../../components/ui/BoxBody"
import BoxHeader from "../../../components/ui/BoxHeader"

import ButtonNextOrder from "./ButtonNextOrder"
import ValidationList from "./ValidationList"


class Validation extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        state: PropTypes.object,
        app: PropTypes.object,
        items: PropTypes.array,
        total: PropTypes.int,
        selected_method: PropTypes.int,
        clearSelectedPaymentMethod: PropTypes.function,
        clearCartItems: PropTypes.function,
        clearSelectedCustomer: PropTypes.function
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.shop.validation.page_title' })
        )
        this.props.validateCart(this.props.state)
    }


    onClickNextOrder() {
        console.log('next order clicked')
        this.props.clearSelectedPaymentMethod()
        this.props.clearCartItems()
        this.props.clearSelectedCustomer()
        //TODO: Add clear functions for cart error & error message, if any.
        this.props.history.push('/shop/products')

    }
    
    render() {
        const app = this.props.app
        console.log('app')
        console.log(app)
        const history = this.props.history
        const items = this.props.items
        const total = this.props.total
        const selected_method = this.props.selected_method

        return (
            <PageTemplate app_state={app}>
                {(app.cart_validating) ?
                    <div className="row">
                        <div className="col-md-4 col-md-offset-4">
                            <Box>
                                <BoxBody>
                                    <div className='text-muted'>
                                        <i className="fa fa-spinner fa-pulse fa-5x fa-fw"></i>
                                    </div>
                                    Please wait... <br />
                                    Validating cart...
                                </BoxBody>
                            </Box>
                        </div>
                    </div>
                    : (app.cart_validation_error) ?
                        <div>
                            <div className="row">
                                <div className="col-md-12">
                                    <ButtonNextOrder onClick={this.onClickNextOrder.bind(this)} />
                                </div>
                            </div>
                            <div className="row">
                                <div className="col-md-4 col-md-offset-4">
                                    <Box>
                                        <BoxBody>
                                            <div className="text-orange">
                                                <i className="fa fa-exclamation-triangle fa-5x"></i>
                                            </div>
                                            Hmm... I seem to have found something that needs your attention while validating this shopping cart. <br /><br />
                                            <div className="text-orange bold">
                                                {app.cart_validation_data.message}
                                            </div>
                                        </BoxBody>
                                    </Box>
                                </div>
                            </div>
                        </div> :
                        // Everything ok
                        <div>
                            <div className="row">
                                <div className="col-md-12">
                                    <ButtonNextOrder onClick={this.onClickNextOrder.bind(this)} />
                                </div>
                            </div>
                            <div className="row">
                                <div className="col-md-4 col-md-offset-4">
                                    <Box>
                                        <BoxBody>
                                            <div className='text-green'>
                                                <i className="fa fa-check fa-5x"></i>
                                            </div>
                                            Success!<br />
                                            <span className="text-green">
                                                <i className="fa fa-leaf"></i> Please consider the environment before printing!
                                            </span><br /><br />
                                            <a href={app.cart_validation_data.receipt_link} 
                                               target="_blank"
                                               className="btn btn-default">
                                                <i className="fa fa-print"></i> Print receipt
                                            </a>
                                        </BoxBody>
                                    </Box>
                                </div>
                            </div>
                        </div>
                }
            </PageTemplate>
        )
    }
}

export default Validation
