import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"

import ButtonCustomerEdit from "../../../components/ui/ButtonCustomerEdit"


class CustomerDisplay extends Component {
    constructor(props) {
        super(props)
        console.log("Customer display props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        customerID: PropTypes.integer,
        customers: PropTypes.object,
        edit_in_progress: PropTypes.boolean,
        onClickEdit: PropTypes.function
    }


    // onClickStartCamera(e) {
    //     console.log('camera start clicked')
    // }

    render() {
        const customerID = this.props.customerID
        const customers = this.props.customers
        const edit_in_progress = this.props.edit_in_progress
        const onClickEdit = this.props.onClickEdit

        return (
            <div>
                { !(customerID) || (edit_in_progress) ? null :
                <div className="box box-solid"> 
                    <div className="box-header">
                        <h3 className="box-title">Customer</h3>
                    </div>
                    <div className="box-body">
                        <div className="col-md-6">
                            camera stream will go here... when it's working...
                        </div>
                        <div className="col-md-6">
                            {customers[customerID].display_name}
                            {customers[customerID].address}
                            <ButtonCustomerEdit onClick={onClickEdit}/>
                        </div>
                    </div>
                </div>
                }
            </div>
        )
    }
}

export default CustomerDisplay

