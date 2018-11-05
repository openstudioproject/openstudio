import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import PageTemplate from "../../../components/PageTemplate"
import Box from "../../../components/ui/Box"
import BoxBody from "../../../components/ui/BoxBody"
import BoxHeader from "../../../components/ui/BoxHeader"

class Payment extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.shop.payment.page_title' })
        )
    }
    
    render() {

        return (
            <PageTemplate app_state={this.props.app}>
                <div className="row">
                    <div className="col-md-12">
                        Cancel & validate
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-4">
                        <Box>
                            <BoxHeader title="Payment methods" />
                            <BoxBody>
                                Payment methods content
                            </BoxBody>
                        </Box>
                    </div>
                    <div className="col-md-8">
                        <Box>
                            <BoxHeader title="Enter payment" />
                            <BoxBody>
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
